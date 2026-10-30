from django.db.models import Count, Q
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from analytics.statistics import formation, scarcity, transitions
from .models import Application, Invitation, Project, ProjectSkillRequirement, RequestStatus, TeamMember, User, UserSkill
from .permissions import IsAdminRole

DEFAULT_TOP_N = 5
MAX_TOP_N = 50


def top_n_from(request):
    raw = request.query_params.get("top_n", str(DEFAULT_TOP_N))
    if not raw.isascii() or not raw.isdecimal():
        raise ValidationError("top_n 必须为正整数")
    value = int(raw)
    if not 1 <= value <= MAX_TOP_N:
        raise ValidationError(f"top_n 必须介于 1 和 {MAX_TOP_N}")
    return value


def demand_by_skill():
    rows = (ProjectSkillRequirement.objects.values("skill__name", "skill__category")
            .annotate(projects=Count("project", distinct=True)).order_by())
    return {row["skill__name"]: {"category": row["skill__category"] or "", "projects": row["projects"]} for row in rows}


def supply_by_skill():
    rows = (UserSkill.objects.filter(user__is_active=True, user__role=User.Role.STUDENT)
            .values("skill__name").annotate(students=Count("user", distinct=True)).order_by())
    return {row["skill__name"]: row["students"] for row in rows}


def popular_projects(limit):
    # ``applications`` is already the reverse accessor on Project, so the
    # aggregate needs a distinct annotation name.
    rows = (Project.objects.annotate(application_count=Count("applications", distinct=True),
                                     team_size=Count("team__members", distinct=True))
            .order_by("-application_count", "id")[:limit])
    return [dict(project_id=p.id, title=p.title, project_type=p.project_type, status=p.status,
                 applications=p.application_count, team_size=p.team_size) for p in rows]


class AdminAnalyticsView(GenericAPIView):
    """GET /api/v1/admin/analytics —平台统计，仅业务管理员可读。

    Metric definitions live in docs/admin-analytics.md; formulas come from
    analytics.statistics so they can be unit-tested without the database.
    """

    permission_classes = [IsAdminRole]

    def get(self, request):
        limit = top_n_from(request)
        projects = Project.objects.count()
        formed = Project.objects.annotate(size=Count("team__members")).filter(size__gte=2).count()
        applications = Application.objects.aggregate(
            total=Count("id"),
            accepted=Count("id", filter=Q(status=RequestStatus.ACCEPTED)))
        invitations = Invitation.objects.aggregate(
            total=Count("id"),
            accepted=Count("id", filter=Q(status=RequestStatus.ACCEPTED)))
        return Response(dict(
            top_n=limit,
            overview=dict(
                students=User.objects.filter(is_active=True, role=User.Role.STUDENT).count(),
                projects=projects,
                teams=TeamMember.objects.values("team").distinct().count(),
                recruiting_projects=Project.objects.filter(status=Project.Status.RECRUITING).count(),
                applications=transitions(applications["total"], applications["accepted"]),
                invitations=transitions(invitations["total"], invitations["accepted"]),
            ),
            popular_projects=popular_projects(limit),
            scarce_skills=scarcity(demand_by_skill(), supply_by_skill(), top_n=limit),
            team_formation=formation(formed, projects),
            definitions=dict(
                popular_projects="按申请总数降序，并列按项目 id 升序",
                scarce_skills="gap = 需求该技能的项目数 − 拥有该技能的活跃学生数；按 gap 降序",
                team_formation="团队人数 ≥2 的项目数 / 项目总数",
                acceptance_rate="已接受数 / 请求总数（含待处理）",
                students="is_active 且业务角色为 student 的用户数",
            ),
        ))
