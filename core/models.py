from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .recommendation_models import RecommendationProfile, RecommendationRequirement  # noqa: F401


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "学生"
        LEADER = "leader", "队长"
        ADMIN = "admin", "管理员"

    role = models.CharField(max_length=16, choices=Role.choices, default=Role.STUDENT, db_index=True)
    display_name = models.CharField(max_length=64, blank=True)


class Skill(models.Model):
    name = models.CharField(max_length=64, unique=True)
    category = models.CharField(max_length=64, blank=True, db_index=True)

    def __str__(self):
        return self.name


class UserSkill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="user_skills")
    level = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "skill"], name="unique_user_skill")]
        indexes = [models.Index(fields=["user", "level"])]


class Project(models.Model):
    class Type(models.TextChoices):
        COURSE = "course", "课程项目"
        COMPETITION = "competition", "竞赛项目"
        INNOVATION = "innovation", "创新创业"

    class Status(models.TextChoices):
        RECRUITING = "recruiting", "招募中"
        ACTIVE = "active", "进行中"
        CLOSED = "closed", "已结束"

    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="owned_projects")
    title = models.CharField(max_length=120, db_index=True)
    description = models.TextField()
    project_type = models.CharField(max_length=20, choices=Type.choices, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECRUITING, db_index=True)
    max_members = models.PositiveSmallIntegerField(default=4, validators=[MinValueValidator(2), MaxValueValidator(20)])
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["project_type", "status", "-created_at"])]


class ProjectSkillRequirement(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="skill_requirements")
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT, related_name="project_requirements")
    required_level = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    weight = models.DecimalField(max_digits=4, decimal_places=3, default=1)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["project", "skill"], name="unique_project_skill")]


class Team(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="team")
    leader = models.ForeignKey(User, on_delete=models.PROTECT, related_name="led_teams")
    created_at = models.DateTimeField(auto_now_add=True)


class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="team_memberships")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["team", "user"], name="unique_team_member")]


class RequestStatus(models.TextChoices):
    PENDING = "pending", "待处理"
    ACCEPTED = "accepted", "已同意"
    REJECTED = "rejected", "已拒绝"
    WITHDRAWN = "withdrawn", "已撤回"


class Application(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    message = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=16, choices=RequestStatus.choices, default=RequestStatus.PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["project", "applicant"], condition=models.Q(status=RequestStatus.PENDING), name="unique_pending_application")
        ]


class Invitation(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="invitations")
    inviter = models.ForeignKey(User, on_delete=models.PROTECT, related_name="sent_invitations")
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_invitations")
    message = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=16, choices=RequestStatus.choices, default=RequestStatus.PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["team", "invitee"], condition=models.Q(status=RequestStatus.PENDING), name="unique_pending_invitation")
        ]


class AuditLog(models.Model):
    actor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_logs")
    action = models.CharField(max_length=64, db_index=True)
    target_type = models.CharField(max_length=64)
    target_id = models.CharField(max_length=64, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["actor", "-created_at"]), models.Index(fields=["action", "-created_at"])]

