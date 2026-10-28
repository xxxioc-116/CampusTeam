from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from core.models import Application, AuditLog, Project, RequestStatus, Skill, TeamMember, User, UserSkill


class ApiTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="leader", password="StrongPass123", role=User.Role.LEADER)
        self.student = User.objects.create_user(username="student", password="StrongPass123")
        self.other = User.objects.create_user(username="other", password="StrongPass123")
        self.admin = User.objects.create_user(username="admin", password="StrongPass123", role=User.Role.ADMIN)
        self.client = APIClient()

    def auth(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def create_project(self):
        self.auth(self.owner)
        response = self.client.post("/api/v1/projects", {
            "title": "CampusTeam",
            "description": "智能组队平台",
            "project_type": "course",
            "max_members": 4,
        }, format="json")
        self.assertEqual(response.status_code, 201)
        return Project.objects.get(pk=response.data["id"])

    def test_health_and_auth_flow(self):
        self.client.credentials()
        self.assertEqual(self.client.get("/api/v1/health").status_code, 200)
        register = self.client.post("/api/v1/auth/register", {
            "username": "new-user", "password": "StrongPass123", "display_name": "新用户"
        }, format="json")
        self.assertEqual(register.status_code, 201)
        login = self.client.post("/api/v1/auth/login", {
            "username": "new-user", "password": "StrongPass123"
        }, format="json")
        self.assertEqual(login.status_code, 200)
        self.assertIn("token", login.data)

    def test_role_and_project_permissions(self):
        project = self.create_project()
        self.auth(self.student)
        denied = self.client.patch(f"/api/v1/projects/{project.id}", {"title": "越权修改"}, format="json")
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(denied.data["code"], "permission_denied")
        self.auth(self.owner)
        allowed = self.client.patch(f"/api/v1/projects/{project.id}", {"title": "合法修改"}, format="json")
        self.assertEqual(allowed.status_code, 200)

    def test_project_search_filter_pagination_and_invalid_params(self):
        self.auth(self.owner)
        for i in range(12):
            self.client.post("/api/v1/projects", {
                "title": f"Python 项目 {i}", "description": "课程实践", "project_type": "course"
            }, format="json")
        result = self.client.get("/api/v1/projects?keyword=Python&type=course&page_size=5")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.data["results"]), 5)
        invalid = self.client.get("/api/v1/projects?type=unknown")
        self.assertEqual(invalid.status_code, 400)

    def test_models_constraints_and_indexes(self):
        skill = Skill.objects.create(name="Python", category="backend")
        UserSkill.objects.create(user=self.student, skill=skill, level=3)
        with self.assertRaises(IntegrityError):
            with self.captureOnCommitCallbacks(execute=True):
                UserSkill.objects.create(user=self.student, skill=skill, level=4)
        self.assertTrue(any(index.fields == ["user", "level"] for index in UserSkill._meta.indexes))

    def test_application_full_lifecycle_and_duplicate(self):
        project = self.create_project()
        self.auth(self.student)
        first = self.client.post(f"/api/v1/projects/{project.id}/applications", {"message": "申请加入"}, format="json")
        self.assertEqual(first.status_code, 201)
        duplicate = self.client.post(f"/api/v1/projects/{project.id}/applications", {}, format="json")
        self.assertEqual(duplicate.status_code, 409)
        app_id = first.data["id"]
        self.auth(self.owner)
        accepted = self.client.post(f"/api/v1/applications/{app_id}/transition", {"action": "accept"}, format="json")
        self.assertEqual(accepted.status_code, 200)
        self.assertTrue(TeamMember.objects.filter(team=project.team, user=self.student).exists())
        repeat = self.client.post(f"/api/v1/applications/{app_id}/transition", {"action": "accept"}, format="json")
        self.assertEqual(repeat.status_code, 400)

    def test_application_reject_and_withdraw(self):
        project = self.create_project()
        for user, action, expected in [
            (self.student, "withdraw", RequestStatus.WITHDRAWN),
            (self.other, "reject", RequestStatus.REJECTED),
        ]:
            self.auth(user)
            created = self.client.post(f"/api/v1/projects/{project.id}/applications", {}, format="json")
            if action == "withdraw":
                response = self.client.post(f"/api/v1/applications/{created.data['id']}/transition", {"action": action}, format="json")
            else:
                self.auth(self.owner)
                response = self.client.post(f"/api/v1/applications/{created.data['id']}/transition", {"action": action}, format="json")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["status"], expected)

    def test_invitation_permissions_accept_and_audit(self):
        project = self.create_project()
        self.auth(self.student)
        denied = self.client.post(f"/api/v1/teams/{project.team.id}/invitations", {"invitee_id": self.other.id}, format="json")
        self.assertEqual(denied.status_code, 403)
        self.auth(self.owner)
        invited = self.client.post(f"/api/v1/teams/{project.team.id}/invitations", {"invitee_id": self.other.id}, format="json")
        self.assertEqual(invited.status_code, 201)
        self.auth(self.other)
        accepted = self.client.post(f"/api/v1/invitations/{invited.data['id']}/transition", {"action": "accept"}, format="json")
        self.assertEqual(accepted.status_code, 200)
        self.assertTrue(AuditLog.objects.filter(action="invitation.accept").exists())

    def test_role_admin_can_invite_without_django_staff_flag(self):
        project = self.create_project()
        self.assertFalse(self.admin.is_staff)

        self.auth(self.admin)
        response = self.client.post(
            f"/api/v1/teams/{project.team.id}/invitations",
            {"invitee_id": self.other.id},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["invitee"]["id"], self.other.id)
        self.assertTrue(
            AuditLog.objects.filter(actor=self.admin, action="invitation.create").exists()
        )

    def test_audit_log_is_admin_only_and_paginated(self):
        project = self.create_project()
        self.auth(self.student)
        self.assertEqual(self.client.get("/api/v1/admin/audit-logs").status_code, 403)
        self.auth(self.admin)
        response = self.client.get("/api/v1/admin/audit-logs?page_size=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

