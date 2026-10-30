from django.test import TestCase
from rest_framework.exceptions import PermissionDenied, ValidationError

from core.models import Application, AuditLog, Invitation, Project, RequestStatus, Team, TeamMember, User
from core.services import transition_request


class TransitionServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username="owner", role=User.Role.LEADER)
        cls.applicant = User.objects.create_user(username="applicant")
        cls.other = User.objects.create_user(username="other")

    def setUp(self):
        self.project = Project.objects.create(owner=self.owner, title="Service", project_type="course", max_members=2)
        self.team = Team.objects.create(project=self.project, leader=self.owner)
        TeamMember.objects.create(team=self.team, user=self.owner)

    def application(self, **kwargs):
        return Application.objects.create(project=self.project, applicant=self.applicant, **kwargs)

    def invitation(self, **kwargs):
        return Invitation.objects.create(team=self.team, inviter=self.owner, invitee=self.applicant, **kwargs)

    def test_already_processed_is_rejected(self):
        application = self.application(status=RequestStatus.ACCEPTED)
        with self.assertRaisesMessage(ValidationError, "该记录已处理"):
            transition_request(application, "accept", self.owner)

    def test_application_withdraw_requires_applicant(self):
        application = self.application()
        with self.assertRaisesMessage(PermissionDenied, "仅申请人可以撤回"):
            transition_request(application, "withdraw", self.other)

    def test_application_withdraw_by_applicant_succeeds(self):
        application = self.application()
        transition_request(application, "withdraw", self.applicant)
        application.refresh_from_db()
        self.assertEqual(application.status, RequestStatus.WITHDRAWN)
        self.assertTrue(AuditLog.objects.filter(action="application.withdraw").exists())

    def test_application_accept_requires_owner(self):
        application = self.application()
        with self.assertRaisesMessage(PermissionDenied, "仅项目负责人可以处理申请"):
            transition_request(application, "accept", self.applicant)

    def test_application_accept_rejects_when_team_is_full(self):
        TeamMember.objects.create(team=self.team, user=self.other)  # max_members = 2 reached
        application = self.application()
        with self.assertRaisesMessage(ValidationError, "团队人数已满"):
            transition_request(application, "accept", self.owner)
        application.refresh_from_db()
        self.assertEqual(application.status, RequestStatus.PENDING)

    def test_application_accept_adds_member(self):
        application = self.application()
        transition_request(application, "accept", self.owner)
        application.refresh_from_db()
        self.assertEqual(application.status, RequestStatus.ACCEPTED)
        self.assertTrue(TeamMember.objects.filter(team=self.team, user=self.applicant).exists())

    def test_application_reject_is_terminal(self):
        application = self.application()
        transition_request(application, "reject", self.owner)
        application.refresh_from_db()
        self.assertEqual(application.status, RequestStatus.REJECTED)
        self.assertFalse(TeamMember.objects.filter(team=self.team, user=self.applicant).exists())

    def test_application_unknown_action_is_rejected(self):
        application = self.application()
        with self.assertRaisesMessage(ValidationError, "不支持的操作"):
            transition_request(application, "approve", self.owner)

    def test_invitation_withdraw_requires_inviter(self):
        invitation = self.invitation()
        with self.assertRaisesMessage(PermissionDenied, "仅邀请人可以撤回"):
            transition_request(invitation, "withdraw", self.applicant)

    def test_invitation_withdraw_by_inviter_succeeds(self):
        invitation = self.invitation()
        transition_request(invitation, "withdraw", self.owner)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, RequestStatus.WITHDRAWN)
        self.assertTrue(AuditLog.objects.filter(action="invitation.withdraw").exists())

    def test_invitation_accept_requires_invitee(self):
        invitation = self.invitation()
        with self.assertRaisesMessage(PermissionDenied, "仅被邀请人可以处理邀请"):
            transition_request(invitation, "accept", self.owner)

    def test_invitation_accept_rejects_when_team_is_full(self):
        TeamMember.objects.create(team=self.team, user=self.other)
        invitation = self.invitation()
        with self.assertRaisesMessage(ValidationError, "团队人数已满"):
            transition_request(invitation, "accept", self.applicant)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, RequestStatus.PENDING)

    def test_invitation_accept_adds_member(self):
        invitation = self.invitation()
        transition_request(invitation, "accept", self.applicant)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, RequestStatus.ACCEPTED)
        self.assertTrue(TeamMember.objects.filter(team=self.team, user=self.applicant).exists())

    def test_invitation_unknown_action_is_rejected(self):
        invitation = self.invitation()
        with self.assertRaisesMessage(ValidationError, "不支持的操作"):
            transition_request(invitation, "approve", self.applicant)
