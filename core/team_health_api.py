from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from analytics.team_health import evaluate
from .recommendation_api import member_profiles, requirement_for, team_for


class TeamHealthView(GenericAPIView):
    """GET /api/v1/teams/{id}/health — five-dimension health plus #21 risks.

    Read permission matches the other team analytics endpoints (member,
    leader or business ADMIN); an unconfigured requirement returns 400 so the
    leader configures it first, mirroring the gaps endpoint.
    """

    def get(self, request, pk):
        team = team_for(request, pk)
        spec = requirement_for(team)
        members = member_profiles(team)
        result = evaluate(members, spec, custom_weights=spec.get("weights") or None)
        result.update(team_id=team.id, project_id=team.project_id, team_name=team.project.title)
        return Response(result)
