from django.db.models import Q
from rest_framework import generics, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Application, AuditLog, Invitation, Project, Team, TeamMember, User
from .permissions import IsAdminRole, IsProjectOwnerOrReadOnly
from .serializers import (
    ApplicationSerializer,
    InvitationSerializer,
    LoginSerializer,
    ProjectSerializer,
    RegisterSerializer,
    StatusTransitionSerializer,
    UserSerializer,
)
from .services import audit, transition_request


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok", "service": "CampusTeam API"})


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        audit(user, "auth.register", user)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        audit(user, "auth.login", user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        user = serializer.save()
        audit(self.request.user, "profile.update", user)


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectOwnerOrReadOnly]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        qs = Project.objects.select_related("owner").all()
        keyword = self.request.query_params.get("keyword", "").strip()
        project_type = self.request.query_params.get("type", "").strip()
        project_status = self.request.query_params.get("status", "").strip()
        if keyword:
            qs = qs.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword))
        if project_type:
            valid = {choice for choice, _ in Project.Type.choices}
            if project_type not in valid:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"type": "非法项目类型"})
            qs = qs.filter(project_type=project_type)
        if project_status:
            valid = {choice for choice, _ in Project.Status.choices}
            if project_status not in valid:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"status": "非法项目状态"})
            qs = qs.filter(status=project_status)
        return qs

    def perform_create(self, serializer):
        project = serializer.save()
        audit(self.request.user, "project.create", project)

    def perform_update(self, serializer):
        project = serializer.save()
        audit(self.request.user, "project.update", project)

    @action(detail=True, methods=["post"], url_path="applications")
    def applications(self, request, pk=None):
        project = self.get_object()
        if project.owner_id == request.user.id or TeamMember.objects.filter(team=project.team, user=request.user).exists():
            return Response({"code": "invalid_application", "message": "团队成员不能申请自己的团队", "details": {}}, status=400)
        serializer = ApplicationSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        if Application.objects.filter(project=project, applicant=request.user, status="pending").exists():
            return Response({"code": "duplicate_application", "message": "已有待处理申请", "details": {}}, status=409)
        application = serializer.save(project=project, applicant=request.user)
        audit(request.user, "application.create", application)
        return Response(ApplicationSerializer(application).data, status=status.HTTP_201_CREATED)


class ApplicationTransitionView(generics.GenericAPIView):
    serializer_class = StatusTransitionSerializer

    def post(self, request, pk):
        instance = generics.get_object_or_404(Application.objects.select_related("project", "applicant", "project__team"), pk=pk)
        serializer = self.get_serializer(data=request.data, context={"instance": instance})
        serializer.is_valid(raise_exception=True)
        transition_request(instance, serializer.validated_data["action"], request.user)
        return Response(ApplicationSerializer(instance).data)


class TeamInvitationView(generics.GenericAPIView):
    serializer_class = InvitationSerializer

    def post(self, request, pk):
        team = generics.get_object_or_404(Team.objects.select_related("project", "leader"), pk=pk)
        if team.leader_id != request.user.id and request.user.role != User.Role.ADMIN:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("仅队长可以邀请成员")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invitee = serializer.validated_data["invitee"]
        if TeamMember.objects.filter(team=team, user=invitee).exists():
            return Response({"code": "already_member", "message": "该用户已是团队成员", "details": {}}, status=409)
        if Invitation.objects.filter(team=team, invitee=invitee, status="pending").exists():
            return Response({"code": "duplicate_invitation", "message": "已有待处理邀请", "details": {}}, status=409)
        invitation = serializer.save(team=team, inviter=request.user)
        audit(request.user, "invitation.create", invitation)
        return Response(InvitationSerializer(invitation).data, status=201)


class InvitationTransitionView(generics.GenericAPIView):
    serializer_class = StatusTransitionSerializer

    def post(self, request, pk):
        instance = generics.get_object_or_404(Invitation.objects.select_related("team", "team__project", "invitee", "inviter"), pk=pk)
        serializer = self.get_serializer(data=request.data, context={"instance": instance})
        serializer.is_valid(raise_exception=True)
        transition_request(instance, serializer.validated_data["action"], request.user)
        return Response(InvitationSerializer(instance).data)


class AuditLogView(generics.ListAPIView):
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return AuditLog.objects.select_related("actor").all()

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        data = [{
            "id": item.id,
            "actor": item.actor.username if item.actor else None,
            "action": item.action,
            "target_type": item.target_type,
            "target_id": item.target_id,
            "details": item.details,
            "created_at": item.created_at,
        } for item in page]
        return self.get_paginated_response(data)

