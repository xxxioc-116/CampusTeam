"""Scale regression: query counts must not grow with the candidate pool (#24).

Timing assertions are flaky on shared CI runners, so this test guards the
structural property instead: the same endpoint issues the same number of SQL
queries at 50 and 200 candidates. A regression that introduces an N+1 shows up
as a query-count difference and fails deterministically.
"""

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from core.models import (Project, ProjectSkillRequirement, RecommendationProfile, RecommendationRequirement, Skill, Team,
                         TeamMember, User, UserSkill)

SIZES = (50, 200)


def query_count(call):
    with CaptureQueriesContext(connection) as captured:
        response = call()
    assert response.status_code == 200, response.content[:200]
    return len(captured)


class ApiScaleRegressionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        owner = User.objects.create_user(username="scale-owner", role=User.Role.LEADER)
        project = Project.objects.create(owner=owner, title="Scale", project_type="course", max_members=4)
        cls.team = Team.objects.create(project=project, leader=owner)
        TeamMember.objects.create(team=cls.team, user=owner)
        RecommendationProfile.objects.create(user=owner, abilities=[90, 80, 70, 0, 0], skills=["Python"],
                                             availability=[{"day": 1, "start": "18:00", "end": "21:00"}],
                                             goal="竞赛获奖")
        RecommendationRequirement.objects.create(team=cls.team, abilities=[100, 90, 80, 60, 40],
                                                 skills=["Python", "Figma"],
                                                 availability=[{"day": 1, "start": "18:00", "end": "21:00"}],
                                                 goal="竞赛获奖", weights={})
        python_skill = Skill.objects.create(name="Python")
        ProjectSkillRequirement.objects.create(project=project, skill=python_skill, required_level=3)
        cls.admin = User.objects.create_user(username="scale-admin", role=User.Role.ADMIN)
        cls.created = 0

    def setUp(self):
        self.member = APIClient()
        self.member.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=self.team.leader).key}")
        self.admin = APIClient()
        self.admin.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=self.admin_user()).key}")

    def admin_user(self):
        return User.objects.get(username="scale-admin")

    def grow_to(self, target):
        while self.created < target:
            batch = [User(username=f"scale-cand-{i}") for i in range(self.created, target)]
            users = User.objects.bulk_create(batch)
            RecommendationProfile.objects.bulk_create([
                RecommendationProfile(user=user, abilities=[(i * 13) % 101 for _ in range(5)], skills=["Python"])
                for i, user in enumerate(users, start=self.created)])
            if users:
                UserSkill.objects.bulk_create([UserSkill(user=user, skill=Skill.objects.first(), level=3)
                                               for user in users])
            self.created = target

    def counts(self):
        return dict(
            matrix=query_count(lambda: self.member.get(f"/api/v1/teams/{self.team.id}/capability-matrix")),
            gaps=query_count(lambda: self.member.get(f"/api/v1/teams/{self.team.id}/gaps")),
            health=query_count(lambda: self.member.get(f"/api/v1/teams/{self.team.id}/health")),
            recommendations=query_count(lambda: self.member.get(f"/api/v1/teams/{self.team.id}/recommendations")),
            analytics=query_count(lambda: self.admin.get("/api/v1/admin/analytics")),
        )

    def test_query_counts_do_not_grow_with_candidate_pool(self):
        measured = {}
        for size in SIZES:
            self.grow_to(size)
            measured[size] = self.counts()
        self.assertEqual(measured[SIZES[0]], measured[SIZES[-1]],
                         f"query counts changed with the candidate pool: {measured}")
