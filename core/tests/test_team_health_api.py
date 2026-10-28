from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from core.models import Project, RecommendationProfile, RecommendationRequirement, Team, TeamMember, User

REQUIREMENT = dict(abilities=[100, 80, 60, 0, 0], skills=["Python", "数据分析"],
                   availability=[{"day": 1, "start": "18:00", "end": "21:00"}],
                   goal="竞赛获奖", experience="竞赛")


class TeamHealthApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.leader = User.objects.create_user(username="leader", role="leader")
        cls.member = User.objects.create_user(username="member")
        cls.outsider = User.objects.create_user(username="outsider")
        cls.business_admin = User.objects.create_user(username="admin", role=User.Role.ADMIN, is_staff=False)
        cls.project = Project.objects.create(owner=cls.leader, title="Health", project_type="course", max_members=4)
        cls.team = Team.objects.create(project=cls.project, leader=cls.leader)
        TeamMember.objects.create(team=cls.team, user=cls.leader)
        TeamMember.objects.create(team=cls.team, user=cls.member)
        RecommendationProfile.objects.create(
            user=cls.leader, abilities=[100, 80, 60, 0, 0], skills=["Python", "数据分析"],
            availability=[{"day": 1, "start": "18:00", "end": "21:00"}], goal="竞赛获奖", experience="竞赛")
        RecommendationProfile.objects.create(
            user=cls.member, abilities=[60, 0, 0, 0, 0], skills=["Python"],
            availability=[{"day": 1, "start": "18:00", "end": "19:00"}], goal="竞赛获奖", experience="")
        RecommendationRequirement.objects.create(team=cls.team, **REQUIREMENT)

    def setUp(self):
        self.client = APIClient()
        self.auth(self.leader)

    def auth(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def get(self):
        return self.client.get(f"/api/v1/teams/{self.team.id}/health")

    def test_permissions_match_other_team_endpoints(self):
        self.assertEqual(self.get().status_code, 200)  # leader
        self.auth(self.member)
        self.assertEqual(self.get().status_code, 200)  # member
        self.auth(self.business_admin)
        self.assertEqual(self.get().status_code, 200)  # business ADMIN
        self.auth(self.outsider)
        self.assertEqual(self.get().status_code, 403)
        self.client.credentials()
        self.assertEqual(self.get().status_code, 401)

    def test_unconfigured_requirement_returns_400(self):
        empty_team_project = Project.objects.create(owner=self.leader, title="Empty", project_type="course")
        empty_team = Team.objects.create(project=empty_team_project, leader=self.leader)
        TeamMember.objects.create(team=empty_team, user=self.leader)
        self.auth(self.leader)
        response = self.client.get(f"/api/v1/teams/{empty_team.id}/health")
        self.assertEqual(response.status_code, 400)
        # Matches the existing gaps endpoint behavior (DRF ValidationError
        # default code). docs/api.md currently claims validation_error; that
        # pre-existing docs/implementation mismatch is tracked separately.
        self.assertEqual(response.data["code"], "invalid")

    def test_response_shape_and_scores(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for key in ("status", "thresholds", "dimensions", "scores", "total", "weights", "risks"):
            self.assertIn(key, data)
        self.assertEqual(data["team_id"], self.team.id)
        self.assertEqual(data["dimensions"], ["编程开发", "数据分析", "产品设计", "沟通协作", "项目管理"])
        # Capability: min(C,R) sums 240 / 240 -> 100; skill 2/2 -> 100;
        # time: common 60 of 180 -> 1/3; goal 2/2 -> 100; experience 1/1 -> 100.
        self.assertEqual(data["scores"]["capability"], 100.0)
        self.assertEqual(data["scores"]["skill"], 100.0)
        self.assertAlmostEqual(data["scores"]["time"], 100 / 3)
        self.assertEqual(data["scores"]["goal"], 100.0)
        self.assertEqual(data["scores"]["experience"], 100.0)
        expected_total = 35 + 25 + 100 / 3 * 0.20 + 10 + 10
        self.assertAlmostEqual(data["total"], expected_total)
        self.assertEqual(data["status"], "healthy")

    def test_risks_are_included(self):
        # Shrink the member window so the common time ratio drops below 20%.
        RecommendationProfile.objects.filter(user=self.member).update(
            availability=[{"day": 1, "start": "18:00", "end": "18:15"}])
        data = self.get().json()
        time_risks = [r for r in data["risks"] if r["type"] == "common_time_insufficient"]
        self.assertEqual(len(time_risks), 1)
        self.assertAlmostEqual(time_risks[0]["ratio"], 15 / 180)

    def test_no_risks_for_fully_aligned_team(self):
        RecommendationProfile.objects.filter(user=self.member).update(
            abilities=[100, 80, 60, 0, 0], skills=["Python", "数据分析"],
            availability=[{"day": 1, "start": "18:00", "end": "21:00"}], goal="竞赛获奖", experience="竞赛")
        data = self.get().json()
        self.assertEqual(data["risks"], [])
        self.assertEqual(data["total"], 100.0)

    def test_custom_weights_are_honored(self):
        RecommendationRequirement.objects.filter(team=self.team).update(
            weights=dict(complement=0.5, skill=0.2, time=0.1, goal=0.1, experience=0.1))
        data = self.get().json()
        self.assertEqual(data["weights"]["complement"], 0.5)
        RecommendationRequirement.objects.filter(team=self.team).update(weights={})
