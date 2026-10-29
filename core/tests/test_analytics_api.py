from django.test import TestCase
from rest_framework.test import APIClient

from core.models import (Application, Invitation, Project, ProjectSkillRequirement, RequestStatus, Skill, Team,
                         TeamMember, User, UserSkill)


class AdminAnalyticsApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(username="admin", role=User.Role.ADMIN, is_staff=False)
        cls.owner = User.objects.create_user(username="owner", role=User.Role.LEADER)
        cls.student = User.objects.create_user(username="student")
        cls.inactive = User.objects.create_user(username="inactive", is_active=False)

        cls.hot = Project.objects.create(owner=cls.owner, title="热门项目", project_type="competition", max_members=4)
        cls.cold = Project.objects.create(owner=cls.owner, title="冷门项目", project_type="course", max_members=3)
        hot_team = Team.objects.create(project=cls.hot, leader=cls.owner)
        TeamMember.objects.create(team=hot_team, user=cls.owner)
        TeamMember.objects.create(team=hot_team, user=cls.student)
        Team.objects.create(project=cls.cold, leader=cls.owner)  # 0 members -> not formed

        python = Skill.objects.create(name="Python", category="后端")
        figma = Skill.objects.create(name="Figma", category="设计")
        rust = Skill.objects.create(name="Rust", category="后端")
        ProjectSkillRequirement.objects.create(project=cls.hot, skill=python, required_level=3)
        ProjectSkillRequirement.objects.create(project=cls.hot, skill=figma, required_level=2)
        ProjectSkillRequirement.objects.create(project=cls.cold, skill=rust, required_level=4)
        UserSkill.objects.create(user=cls.student, skill=python, level=4)
        UserSkill.objects.create(user=cls.inactive, skill=figma, level=5)  # inactive user not counted

        Application.objects.create(project=cls.hot, applicant=cls.student, status=RequestStatus.ACCEPTED)
        Application.objects.create(project=cls.cold, applicant=cls.student, status=RequestStatus.PENDING)
        Invitation.objects.create(team=hot_team, inviter=cls.owner, invitee=cls.student,
                                 status=RequestStatus.REJECTED)

    def setUp(self):
        self.client = APIClient()
        self.auth(self.admin)

    def auth(self, user):
        from rest_framework.authtoken.models import Token
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def get(self, **params):
        return self.client.get("/api/v1/admin/analytics", params)

    def test_only_business_admin_can_read(self):
        self.assertEqual(self.get().status_code, 200)
        for user in (self.owner, self.student):
            self.auth(user)
            response = self.get()
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.data["code"], "permission_denied")
        self.client.credentials()
        self.assertEqual(self.get().status_code, 401)

    def test_overview_counts(self):
        data = self.get().json()["overview"]
        self.assertEqual(data["students"], 1)  # inactive user excluded
        self.assertEqual(data["projects"], 2)
        self.assertEqual(data["teams"], 1)  # only teams with members
        self.assertEqual(data["applications"], dict(total=2, accepted=1, acceptance_rate=0.5))
        self.assertEqual(data["invitations"], dict(total=1, accepted=0, acceptance_rate=0.0))

    def test_popular_projects_ordered_by_applications(self):
        rows = self.get().json()["popular_projects"]
        self.assertEqual([r["title"] for r in rows], ["热门项目", "冷门项目"])
        self.assertEqual(rows[0]["applications"], 1)
        self.assertEqual(rows[0]["team_size"], 2)

    def test_scarce_skills_ranked_by_unmet_demand(self):
        rows = self.get().json()["scarce_skills"]
        # Python: 1 project, 1 active holder -> gap 0; Figma: 1 project, 0 active
        # holders (inactive excluded) -> gap 1; Rust: 1 project, 0 holders -> gap 1.
        by_skill = {r["skill"]: r for r in rows}
        self.assertEqual(by_skill["Python"]["gap"], 0)
        self.assertEqual(by_skill["Figma"]["supply_students"], 0)
        self.assertEqual(by_skill["Figma"]["gap"], 1)
        self.assertEqual(rows[0]["gap"], 1)

    def test_team_formation_rate(self):
        data = self.get().json()["team_formation"]
        self.assertEqual(data, dict(projects=2, formed_projects=1, success_rate=0.5))

    def test_top_n_validation_and_effect(self):
        self.assertEqual(self.get(top_n=1).json()["top_n"], 1)
        self.assertEqual(len(self.get(top_n=1).json()["popular_projects"]), 1)
        for bad in ("0", "51", "abc", "-1", "1.5", ""):
            with self.subTest(top_n=bad):
                response = self.get(top_n=bad)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.data["code"], "invalid")

    def test_staff_student_is_rejected(self):
        staff_student = User.objects.create_user(username="staff-student", role=User.Role.STUDENT, is_staff=True)
        self.auth(staff_student)
        self.assertEqual(self.get().status_code, 403)

    def test_definitions_are_returned(self):
        self.assertIn("scarce_skills", self.get().json()["definitions"])
