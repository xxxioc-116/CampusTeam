import json
import random
import statistics
from time import perf_counter

from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from core.models import Project, RecommendationProfile, RecommendationRequirement, Team, TeamMember, User


class RecommendationPerformanceTests(TestCase):
    def test_api_scales_without_n_plus_one_queries(self):
        rng = random.Random(20261027)
        owner = User.objects.create_user(username="perf-owner", role="leader")
        project = Project.objects.create(owner=owner, title="Performance", project_type="course")
        team = Team.objects.create(project=project, leader=owner)
        TeamMember.objects.create(team=team, user=owner)
        RecommendationRequirement.objects.create(team=team, abilities=[90] * 5)
        client = APIClient()
        token = Token.objects.create(user=owner)
        client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        previous = 0
        reports = []
        expected_scores = {}
        for size in (100, 500, 1000):
            users = User.objects.bulk_create([User(username=f"candidate-{i}") for i in range(previous, size)])
            RecommendationProfile.objects.bulk_create([
                RecommendationProfile(user=u, abilities=[rng.randrange(101) for _ in range(5)]) for u in users])
            # Independent hand formula for this fixture: current=0, required=90;
            # only complement contributes, at weight .35. Check actual identities too.
            for profile in RecommendationProfile.objects.filter(user__in=users):
                expected_scores[profile.user_id] = sum(min(v, 90) for v in profile.abilities) / 450 * 35
            expected_ids = sorted(expected_scores, key=lambda uid: (-expected_scores[uid], uid))[:5]
            elapsed = []
            for _ in range(5):
                start = perf_counter()
                with self.assertNumQueries(6):  # Includes real Token authentication.
                    response = client.get(f"/api/v1/teams/{team.id}/recommendations?top_k=5")
                elapsed.append((perf_counter() - start) * 1000)
                self.assertEqual(response.status_code, 200)
                rows = response.data["results"]
                self.assertEqual(len(rows), 5)
                self.assertEqual(len({r["id"] for r in rows}), 5)
                self.assertEqual([r["id"] for r in rows], expected_ids)
                self.assertEqual([r["score"] for r in rows], sorted([r["score"] for r in rows], reverse=True))
                for row in rows:
                    self.assertAlmostEqual(row["score"], expected_scores[row["id"]])
                    self.assertAlmostEqual(row["score"], sum(row["contributions"].values()))
            reports.append(dict(candidates=size, median_ms=round(statistics.median(elapsed), 3),
                                max_ms=round(max(elapsed), 3), queries=6))
            previous = size
        print("API_BENCHMARK=" + json.dumps(reports))
