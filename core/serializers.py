from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers

from .models import Application, Invitation, Project, RequestStatus, Team, TeamMember, User


class UserSerializer(serializers.ModelSerializer):
    team_id = serializers.SerializerMethodField()

    def get_team_id(self, user):
        return user.team_memberships.order_by("team_id").values_list("team_id", flat=True).first()

    class Meta:
        model = User
        fields = ["id", "username", "display_name", "role", "team_id"]
        read_only_fields = ["id", "role"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "password", "display_name"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user or not user.is_active:
            raise serializers.ValidationError("用户名或密码错误")
        attrs["user"] = user
        return attrs


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ["id", "owner", "title", "description", "project_type", "status", "max_members", "created_at", "updated_at"]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    @transaction.atomic
    def create(self, validated_data):
        owner = self.context["request"].user
        project = Project.objects.create(owner=owner, **validated_data)
        team = Team.objects.create(project=project, leader=owner)
        TeamMember.objects.create(team=team, user=owner)
        if owner.role == User.Role.STUDENT:
            owner.role = User.Role.LEADER
            owner.save(update_fields=["role"])
        return project


class ApplicationSerializer(serializers.ModelSerializer):
    applicant = UserSerializer(read_only=True)

    class Meta:
        model = Application
        fields = ["id", "project", "applicant", "message", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "project", "applicant", "status", "created_at", "updated_at"]


class InvitationSerializer(serializers.ModelSerializer):
    inviter = UserSerializer(read_only=True)
    invitee = UserSerializer(read_only=True)
    invitee_id = serializers.PrimaryKeyRelatedField(source="invitee", queryset=User.objects.all(), write_only=True)

    class Meta:
        model = Invitation
        fields = ["id", "team", "inviter", "invitee", "invitee_id", "message", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "team", "inviter", "invitee", "status", "created_at", "updated_at"]


class StatusTransitionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["accept", "reject", "withdraw"])

    def validate(self, attrs):
        instance = self.context["instance"]
        if instance.status != RequestStatus.PENDING:
            raise serializers.ValidationError("仅待处理记录可以变更状态")
        return attrs

