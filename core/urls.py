from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .recommendation_api import (
    RecommendationProfileView, TeamGapsView, TeamMatrixView,
    TeamRecommendationsView, TeamRequirementView,
)

from .team_health_api import TeamHealthView
from .views import (
    ApplicationTransitionView,
    AuditLogView,
    InvitationTransitionView,
    LoginView,
    ProjectViewSet,
    RegisterView,
    TeamInvitationView,
    health,
)

router = DefaultRouter(trailing_slash=False)
router.register("projects", ProjectViewSet, basename="project")

urlpatterns = [
    path("health", health),
    path("auth/register", RegisterView.as_view()),
    path("auth/login", LoginView.as_view()),
    path("profiles/me", RecommendationProfileView.as_view()),
    path("teams/<int:pk>/recommendation-requirements", TeamRequirementView.as_view()),
    path("teams/<int:pk>/capability-matrix", TeamMatrixView.as_view()),
    path("teams/<int:pk>/gaps", TeamGapsView.as_view()),
    path("teams/<int:pk>/recommendations", TeamRecommendationsView.as_view()),
    path("teams/<int:pk>/health", TeamHealthView.as_view()),
    path("applications/<int:pk>/transition", ApplicationTransitionView.as_view()),
    path("teams/<int:pk>/invitations", TeamInvitationView.as_view()),
    path("invitations/<int:pk>/transition", InvitationTransitionView.as_view()),
    path("admin/audit-logs", AuditLogView.as_view()),
    path("", include(router.urls)),
]

