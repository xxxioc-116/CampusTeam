from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from core.models import Invitation, Project, Team, TeamMember, User


class InvitationInboxApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.leader = User.objects.create_user(username="leader", role=User.Role.LEADER)
        cls.invitee = User.objects.create_user(username="invitee")
        cls.outsider = User.objects.create_user(username="outsider")
        cls.project = Project.objects.create(
            owner=cls.leader,
            title="邀请收件箱项目",
            description="测试",
            project_type=Project.Type.COURSE,
        )
        cls.team = Team.objects.create(project=cls.project, leader=cls.leader)
        TeamMember.objects.create(team=cls.team, user=cls.leader)
        cls.invitation = Invitation.objects.create(
            team=cls.team,
            inviter=cls.leader,
            invitee=cls.invitee,
            message="欢迎加入",
        )

    def setUp(self):
        self.client = APIClient()

    def auth(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_list_requires_authentication(self):
        self.assertEqual(self.client.get("/api/v1/invitations").status_code, 401)

    def test_list_returns_only_received_invitations_with_display_fields(self):
        self.auth(self.invitee)
        response = self.client.get("/api/v1/invitations")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["team_name"], "邀请收件箱项目")
        self.assertEqual(response.data[0]["inviter"]["username"], "leader")
        self.assertEqual(response.data[0]["message"], "欢迎加入")

        self.auth(self.outsider)
        self.assertEqual(self.client.get("/api/v1/invitations").data, [])

    def test_invitee_accepts_and_repeat_returns_conflict(self):
        self.auth(self.invitee)
        path = f"/api/v1/invitations/{self.invitation.id}/transition"
        accepted = self.client.post(path, {"action": "accept"}, format="json")
        self.assertEqual(accepted.status_code, 200)
        self.assertTrue(TeamMember.objects.filter(team=self.team, user=self.invitee).exists())
        repeated = self.client.post(path, {"action": "accept"}, format="json")
        self.assertEqual(repeated.status_code, 409)
        self.assertEqual(repeated.data["code"], "invitation_already_processed")

    def test_unrelated_user_cannot_transition_invitation(self):
        self.auth(self.outsider)
        response = self.client.post(
            f"/api/v1/invitations/{self.invitation.id}/transition",
            {"action": "reject"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)
