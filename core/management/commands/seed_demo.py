from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Project, Skill, Team, TeamMember, User, UserSkill


class Command(BaseCommand):
    help = "创建可重复执行的 CampusTeam 演示数据"

    def add_arguments(self, parser):
        parser.add_argument("--leader-password", required=True, help="本地演示队长密码")
        parser.add_argument("--student-password", required=True, help="本地演示学生密码")

    @transaction.atomic
    def handle(self, *args, **options):
        leader, leader_created = User.objects.get_or_create(username="demo_leader", defaults={"display_name": "演示队长", "role": User.Role.LEADER})
        if leader_created:
            leader.set_password(options["leader_password"])
            leader.save(update_fields=["password"])
        student, student_created = User.objects.get_or_create(username="demo_student", defaults={"display_name": "演示学生"})
        if student_created:
            student.set_password(options["student_password"])
            student.save(update_fields=["password"])
        python, _ = Skill.objects.get_or_create(name="Python", defaults={"category": "backend"})
        UserSkill.objects.update_or_create(user=student, skill=python, defaults={"level": 4})
        project, _ = Project.objects.get_or_create(
            owner=leader,
            title="CampusTeam 智能组队平台",
            defaults={"description": "面向高校课程与竞赛的智能组队平台", "project_type": Project.Type.COURSE},
        )
        team, _ = Team.objects.get_or_create(project=project, defaults={"leader": leader})
        TeamMember.objects.get_or_create(team=team, user=leader)
        self.stdout.write(self.style.SUCCESS("演示数据已就绪"))

