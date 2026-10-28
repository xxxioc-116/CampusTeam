import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Project, RecommendationProfile, RecommendationRequirement, Team, TeamMember, User


class Command(BaseCommand):
    help = "Seed isolated recommendation demo users; requires CAMPUS_DEMO_PASSWORD."

    @transaction.atomic
    def handle(self, *args, **options):
        password = os.environ.get("CAMPUS_DEMO_PASSWORD")
        if not password or len(password) < 12:
            raise CommandError("Set CAMPUS_DEMO_PASSWORD (at least 12 characters); use a demo database.")
        users = []
        for username, role, abilities in (
            ("rec_leader", "leader", [80, 20, 40, 70, 60]),
            ("rec_candidate", "student", [70, 95, 80, 70, 60]),
        ):
            user, _ = User.objects.get_or_create(username=username, defaults={"role": role, "display_name": username})
            user.set_password(password)
            user.save(update_fields=["password"])
            RecommendationProfile.objects.update_or_create(user=user, defaults={"abilities": abilities, "skills": ["Python"]})
            users.append(user)
        project, _ = Project.objects.get_or_create(owner=users[0], title="推荐联调演示", defaults={"project_type": "course"})
        team, _ = Team.objects.get_or_create(project=project, defaults={"leader": users[0]})
        TeamMember.objects.get_or_create(team=team, user=users[0])
        RecommendationRequirement.objects.update_or_create(team=team, defaults={"abilities": [80, 80, 70, 70, 60], "skills": ["Python"]})
        self.stdout.write(f"team_id={team.id}; users=rec_leader,rec_candidate; no real student data used")
