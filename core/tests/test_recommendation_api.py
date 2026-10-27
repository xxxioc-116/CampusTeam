from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from core.models import Project, RecommendationProfile, RecommendationRequirement, Team, TeamMember, User


class RecommendationApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username="owner", role="leader")
        cls.candidate = User.objects.create_user(username="candidate")
        cls.outsider = User.objects.create_user(username="outsider")
        cls.project = Project.objects.create(owner=cls.owner, title="Test", project_type="course", max_members=4)
        cls.team = Team.objects.create(project=cls.project, leader=cls.owner)
        TeamMember.objects.create(team=cls.team, user=cls.owner)
        RecommendationProfile.objects.create(user=cls.owner, abilities=[80, 20, 0, 0, 0])
        RecommendationProfile.objects.create(user=cls.candidate, abilities=[80, 100, 0, 0, 0], skills=["Python"])
        RecommendationRequirement.objects.create(team=cls.team, abilities=[80, 80, 0, 0, 0], skills=["Python"])

    def setUp(self):
        self.client = APIClient()
        self.auth(self.owner)

    def auth(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def get(self, endpoint):
        return self.client.get(f"/api/v1/teams/{self.team.id}/{endpoint}")

    def test_permissions(self):
        for endpoint in ("recommendations", "capability-matrix", "gaps"):
            self.auth(self.outsider)
            self.assertEqual(self.get(endpoint).status_code, 403)
            self.client.credentials()
            self.assertEqual(self.get(endpoint).status_code, 401)

    def test_profile_persistence_and_validation(self):
        self.auth(self.candidate)
        payload = dict(display_name="新名字", abilities=[50] * 5, skills=["Vue"], bio="hello",
                       goal="学习", experience="课程", availability=[dict(day=1, start="18:00", end="20:00")])
        response = self.client.patch("/api/v1/profiles/me", payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile"]["abilities"], [50] * 5)
        response = self.client.get("/api/v1/profiles/me")
        self.assertEqual(response.data["profile"]["skills"], ["Vue"])
        self.assertEqual(response.data["user"]["display_name"], "新名字")
        for values in ([True] * 5, [101] * 5, []):
            bad = self.client.patch("/api/v1/profiles/me", {"abilities": values}, format="json")
            self.assertEqual(bad.status_code, 400)
        self.candidate.refresh_from_db()
        self.assertEqual(self.candidate.recommendation_profile.abilities, [50] * 5)

    def test_scores_and_query_count(self):
        # Query count stays constant as candidate count grows (no N+1 profiles).
        with self.assertNumQueries(6):
            result = self.get("recommendations")
        self.assertEqual(result.status_code, 200)
        first = result.data["results"][0]
        self.assertEqual(first["id"], self.candidate.id)
        self.assertEqual(first["score"], 60)
        self.assertAlmostEqual(sum(first["contributions"].values()), first["score"])
        self.assertIn("可补齐数据分析 60.00 分", first["reasons"])

    def test_invitation_join_recalculates_without_cache(self):
        before = self.get("capability-matrix")
        self.assertEqual(before.data["current"][1], 20)
        self.assertEqual(self.get("gaps").data["results"][0]["gap"], 60)
        invitation = self.client.post(f"/api/v1/teams/{self.team.id}/invitations",
                                      {"invitee_id": self.candidate.id}, format="json")
        self.assertEqual(invitation.status_code, 201)
        self.assertTrue(self.get("recommendations").data["results"][0]["invited"])
        self.assertEqual(self.get("capability-matrix").data["current"][1], 20)
        self.auth(self.candidate)
        accepted = self.client.post(f"/api/v1/invitations/{invitation.data['id']}/transition",
                                    {"action": "accept"}, format="json")
        self.assertEqual(accepted.status_code, 200)
        after = self.get("capability-matrix")
        self.assertEqual(after.data["current"][1], 100)
        self.assertEqual(self.get("gaps").data["results"], [])
        self.assertNotIn(self.candidate.id, [r["id"] for r in self.get("recommendations").data["results"]])

    def test_requirement_permissions_and_missing_config(self):
        path = f"/api/v1/teams/{self.team.id}/recommendation-requirements"
        self.auth(self.candidate)
        self.assertEqual(self.client.patch(path, {"goal": "学习"}, format="json").status_code, 403)
        self.auth(self.owner)
        self.assertEqual(self.client.patch(path, {"abilities": [90] * 5}, format="json").status_code, 200)
        RecommendationRequirement.objects.all().delete()
        self.assertEqual(self.get("recommendations").status_code, 400)

    def test_application_approval_recalculates_capabilities(self):
        self.auth(self.candidate)
        created = self.client.post(f"/api/v1/projects/{self.project.id}/applications", {}, format="json")
        self.assertEqual(created.status_code, 201)
        self.auth(self.owner)
        self.assertEqual(self.get("capability-matrix").data["current"][1], 20)
        accepted = self.client.post(f"/api/v1/applications/{created.data['id']}/transition",
                                    {"action": "accept"}, format="json")
        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(self.get("capability-matrix").data["current"][1], 100)
        self.assertEqual(self.get("gaps").data["results"], [])

    def test_k_and_empty_candidates(self):
        for value in ("-1", "1.5", "true", "1001"):
            self.assertEqual(self.get(f"recommendations?top_k={value}").status_code, 400)
        self.assertEqual(self.get("recommendations?top_k=0").data["results"], [])
        User.objects.exclude(pk=self.owner.pk).update(is_active=False)
        self.assertEqual(self.get("recommendations").data["results"], [])

    def test_team_weights_are_validated_and_persisted(self):
        path = f"/api/v1/teams/{self.team.id}/recommendation-requirements"
        config = dict(complement=1, skill=0, time=0, goal=0, experience=0)
        response = self.client.patch(path, {"weights": config}, format="json")
        self.assertEqual(response.status_code, 200)
        result = self.get("recommendations").data
        self.assertEqual(result["weights"], config)
        self.assertTrue(result["weight_version"].startswith("custom-"))
        self.assertEqual(result["results"][0]["score"], 100)
        for value in ({}, [], {**config, "complement": .5}, {**config, "skill": True}):
            invalid = self.client.patch(path, {"weights": value}, format="json")
            self.assertEqual(invalid.status_code, 400)
        self.assertEqual(self.get("recommendations").data["weights"], config)
