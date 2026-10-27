from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.response import Response

from analytics.recommendation import DIMENSIONS, Profile, aggregate, gaps, recommend, vector, weights
from .models import Invitation, RecommendationProfile, RecommendationRequirement, Team, TeamMember, User
from .serializers import UserSerializer


class ProfileDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationProfile
        fields = ["abilities", "skills", "availability", "goal", "experience", "bio"]

    def validate(self, attrs):
        # Validate the merged state for PATCH, preserving unchanged coordinates.
        data = {k: getattr(self.instance, k) for k in self.Meta.fields} if self.instance else {}
        data.update(attrs)
        try:
            abilities = attrs["abilities"] if "abilities" in attrs else (data.get("abilities") or None)
            Profile.parse(dict(id=1, abilities=abilities,
                               skills=data.get("skills", []), availability=data.get("availability", []),
                               goal=data.get("goal", ""), experience=[data["experience"]] if data.get("experience") else []))
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        return attrs


class RequirementSerializer(ProfileDataSerializer):
    class Meta:
        model = RecommendationRequirement
        fields = ["abilities", "skills", "availability", "goal", "experience", "weights"]

    def validate_weights(self, value):
        if not isinstance(value, dict):
            raise ValidationError("权重必须是对象")
        try:
            return weights(value)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc


def profile_for(user):
    try:
        data = ProfileDataSerializer(user.recommendation_profile).data
    except RecommendationProfile.DoesNotExist:
        data = {}
    return Profile.parse(dict(id=user.id, display_name=user.display_name or user.username,
                              **{k: v for k, v in data.items() if k not in {"bio", "experience", "abilities"}},
                              abilities=data.get("abilities") or None,
                              experience=[data["experience"]] if data.get("experience") else []))


def team_for(request, pk):
    team = get_object_or_404(Team.objects.select_related("project", "leader"), pk=pk)
    if not (request.user.is_staff or request.user.role == User.Role.ADMIN or team.leader_id == request.user.id
            or TeamMember.objects.filter(team=team, user=request.user).exists()):
        raise PermissionDenied("仅团队成员或管理员可查看")
    return team


def member_profiles(team):
    return [profile_for(m.user) for m in team.members.select_related("user", "user__recommendation_profile")]


def requirement_for(team):
    try:
        data = RequirementSerializer(team.recommendation_requirement).data
    except RecommendationRequirement.DoesNotExist:
        raise ValidationError("请队长先配置推荐需求") from None
    data["abilities"] = data["abilities"] or [0] * 5
    return data


class RecommendationProfileView(GenericAPIView):
    serializer_class = ProfileDataSerializer

    def payload(self, user):
        try:
            profile = dict(ProfileDataSerializer(user.recommendation_profile).data)
            profile["abilities"] = profile["abilities"] or [0] * 5
            profile["display_name"] = user.display_name
        except RecommendationProfile.DoesNotExist:
            profile = None
        data = dict(UserSerializer(user).data)
        data["team_id"] = user.team_memberships.order_by("team_id").values_list("team_id", flat=True).first()
        return {"user": data, "profile": profile}

    def get(self, request):
        return Response(self.payload(request.user))

    @transaction.atomic
    def patch(self, request):
        profile, _ = RecommendationProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if "display_name" in request.data:
            user_serializer = UserSerializer(request.user, data={"display_name": request.data["display_name"]}, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        return Response(self.payload(request.user))


class TeamRequirementView(GenericAPIView):
    serializer_class = RequirementSerializer

    def patch(self, request, pk):
        team = team_for(request, pk)
        if team.leader_id != request.user.id and not (request.user.is_staff or request.user.role == User.Role.ADMIN):
            raise PermissionDenied("仅队长或管理员可配置需求")
        with transaction.atomic():
            obj, _ = RecommendationRequirement.objects.get_or_create(team=team)
            serializer = self.get_serializer(obj, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)


class TeamMatrixView(GenericAPIView):
    def get(self, request, pk):
        team = team_for(request, pk)
        members = member_profiles(team)
        return Response(dict(team_name=team.project.title, dimensions=DIMENSIONS,
                             current=[v * 100 for v in aggregate(members)],
                             required=requirement_for(team)["abilities"],
                             members=[dict(id=p.id, display_name=p.display_name,
                                           abilities=[v * 100 for v in p.abilities]) for p in members]))


class TeamGapsView(GenericAPIView):
    def get(self, request, pk):
        team = team_for(request, pk)
        missing = gaps(aggregate(member_profiles(team)), vector(requirement_for(team)["abilities"]))
        return Response(dict(results=[dict(dimension=name, gap=round(g * 100, 10),
                                           explanation=f"尚缺 {g * 100:.2f} 分能力")
                                      for name, g in zip(DIMENSIONS, missing, strict=True) if g > 0]))


class TeamRecommendationsView(GenericAPIView):
    def get(self, request, pk):
        team = team_for(request, pk)
        try:
            raw_k = request.query_params.get("top_k", "5")
            if not raw_k.isascii() or not raw_k.isdecimal():
                raise ValueError("top_k 必须为非负整数")
            k = int(raw_k)
            if k > 1000:
                raise ValueError("top_k 最大为 1000")
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        spec = requirement_for(team)
        members = member_profiles(team)
        invited = Invitation.objects.filter(team=team, status="pending").values_list("invitee_id", flat=True)
        users = User.objects.filter(is_active=True, role=User.Role.STUDENT).exclude(
            team_memberships__team=team).select_related("recommendation_profile")
        people = [profile_for(u) for u in users]
        result = recommend(members, spec["abilities"], people, required_skills=spec["skills"],
                           availability=spec["availability"], goal=spec["goal"],
                           experience=[spec["experience"]] if spec["experience"] else [], top_k=k,
                           custom_weights=spec["weights"] or None)
        invited_ids = set(invited)
        for row in result["results"]:
            row["invited"] = row["id"] in invited_ids
        result.update(project_id=team.project_id, applied=False)
        return Response(result)
