from unittest import TestCase

from analytics.recommendation import Profile, slots
from analytics.team_health import (
    COMMON_TIME_THRESHOLD,
    CRITICAL_GAP_THRESHOLD,
    HEALTHY_THRESHOLD,
    WATCH_THRESHOLD,
    evaluate,
    goal_alignment_score,
    health,
    risks,
    time_overlap,
    time_overlap_score,
)

REQUIREMENT = dict(abilities=[100, 80, 60, 0, 0], skills=["python", "数据分析"],
                   availability=[dict(day=1, start="18:00", end="21:00")],
                   goal="竞赛获奖", experience=["竞赛"])


def profile(pid, *, abilities=(0, 0, 0, 0, 0), skills=(), availability=(), goal="", experience=(), name=""):
    return Profile.parse(dict(id=pid, display_name=name, abilities=list(abilities), skills=list(skills),
                              availability=list(availability), goal=goal, experience=list(experience)))


class TimeOverlapTests(TestCase):
    def test_full_intersection_scores_one(self):
        members = [profile(1, availability=[dict(day=1, start="18:00", end="21:00")]),
                   profile(2, availability=[dict(day=1, start="19:00", end="22:00")])]
        covered, required, missing = time_overlap([m.availability for m in members],
                                                  slots(REQUIREMENT["availability"]))
        self.assertEqual((covered, required, missing), (120.0, 180.0, False))
        self.assertAlmostEqual(time_overlap_score(members, REQUIREMENT["availability"]), 120 / 180)

    def test_no_intersection_scores_zero(self):
        members = [profile(1, availability=[dict(day=2, start="18:00", end="21:00")]),
                   profile(2, availability=[dict(day=1, start="18:00", end="21:00")])]
        self.assertEqual(time_overlap_score(members, REQUIREMENT["availability"]), 0.0)

    def test_multiple_intersection_windows_are_counted(self):
        members = [profile(1, availability=[dict(day=1, start="18:00", end="19:00"),
                                            dict(day=1, start="20:00", end="21:00")])]
        covered, required, _ = time_overlap([members[0].availability], slots(REQUIREMENT["availability"]))
        self.assertEqual(covered, 120.0)
        self.assertEqual(required, 180.0)

    def test_empty_member_availability_flags_missing_info_and_scores_zero(self):
        members = [profile(1, availability=[dict(day=1, start="18:00", end="21:00")]), profile(2)]
        covered, _, missing = time_overlap([m.availability for m in members],
                                           slots(REQUIREMENT["availability"]))
        self.assertEqual((covered, missing), (0.0, True))
        self.assertEqual(time_overlap_score(members, REQUIREMENT["availability"]), 0.0)

    def test_no_members_reports_missing_info(self):
        covered, required, missing = time_overlap([], slots(REQUIREMENT["availability"]))
        self.assertEqual((covered, required, missing), (0.0, 180.0, True))

    def test_cross_day_intervals_are_rejected_and_must_be_split(self):
        with self.assertRaises(ValueError):
            slots([dict(day=1, start="23:00", end="01:00")])

    def test_requirement_without_time_scores_zero_without_risk(self):
        members = [profile(1, availability=[dict(day=1, start="18:00", end="21:00")])]
        self.assertEqual(time_overlap_score(members, []), 0.0)
        self.assertEqual([r for r in risks(members, dict(abilities=[0] * 5, availability=[]))
                          if r["type"] == "common_time_insufficient"], [])


class GoalAlignmentTests(TestCase):
    def test_case_and_whitespace_insensitive_match(self):
        members = [profile(1, goal=" 竞赛获奖 "), profile(2, goal="竞赛获奖"), profile(3, goal="其他")]
        self.assertAlmostEqual(goal_alignment_score(members, "竞赛获奖"), 2 / 3)

    def test_empty_team_goal_scores_zero(self):
        self.assertEqual(goal_alignment_score([profile(1, goal="竞赛获奖")], ""), 0.0)

    def test_goal_conflict_is_reported(self):
        members = [profile(1, goal="竞赛获奖", name="甲"), profile(2, goal="创业实践", name="乙")]
        found = [r for r in risks(members, REQUIREMENT) if r["type"] == "goal_inconsistency"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["members"], ["乙"])


class HealthTests(TestCase):
    def test_documented_sample_calculation(self):
        # C=[100,80,60,0,0] meets the requirement exactly on the three set dimensions;
        # skill/time/goal/experience fully covered by the only member.
        members = [profile(1, abilities=(100, 80, 60, 0, 0), skills=["Python", "数据分析"],
                           availability=[dict(day=1, start="18:00", end="21:00")],
                           goal="竞赛获奖", experience=["竞赛"])]
        result = health(members, REQUIREMENT)
        self.assertEqual(result["scores"]["capability"], 100.0)
        self.assertEqual(result["scores"]["skill"], 100.0)
        self.assertEqual(result["scores"]["time"], 100.0)
        self.assertEqual(result["scores"]["goal"], 100.0)
        self.assertEqual(result["scores"]["experience"], 100.0)
        self.assertAlmostEqual(result["total"], 100.0)

    def test_partial_capability_uses_min_not_surplus(self):
        # Requirement 40 with member 100: min caps at 40, no bonus for surplus.
        members = [profile(1, abilities=(100, 0, 0, 0, 0))]
        result = health(members, dict(abilities=[40, 0, 0, 0, 0]))
        self.assertEqual(result["scores"]["capability"], 100.0)

    def test_default_weights_match_recommendation_module(self):
        members = [profile(1, abilities=(100, 80, 60, 0, 0), skills=["Python", "数据分析"],
                           availability=[dict(day=1, start="18:00", end="21:00")], goal="竞赛获奖")]
        result = health(members, REQUIREMENT)
        self.assertEqual(result["weights"], dict(complement=0.35, skill=0.25, time=0.20,
                                                 goal=0.10, experience=0.10))
        # 35 + 25 + 20 + 10 + 0 = 90 -> healthy band edge.
        self.assertAlmostEqual(result["total"], 90.0)
        self.assertEqual(evaluate(members, REQUIREMENT)["status"], "healthy")

    def test_status_bands(self):
        strong = [profile(1, abilities=(100, 80, 60, 0, 0), skills=["Python", "数据分析"],
                          availability=[dict(day=1, start="18:00", end="21:00")],
                          goal="竞赛获奖", experience=["竞赛"])]
        self.assertEqual(evaluate(strong, REQUIREMENT)["status"], "healthy")
        watch = [profile(1, abilities=(100, 80, 60, 0, 0), skills=["Python", "数据分析"])]
        result = evaluate(watch, REQUIREMENT)
        self.assertEqual(result["status"], "watch")
        self.assertTrue(WATCH_THRESHOLD <= result["total"] < HEALTHY_THRESHOLD)
        weak = [profile(1, abilities=(0, 0, 0, 0, 0))]
        self.assertEqual(evaluate(weak, REQUIREMENT)["status"], "at_risk")

    def test_empty_team_is_rejected(self):
        with self.assertRaises(ValueError):
            health([], REQUIREMENT)

    def test_custom_weights_are_validated(self):
        members = [profile(1, abilities=(100, 80, 60, 0, 0))]
        with self.assertRaises(ValueError):
            health(members, dict(abilities=[100, 0, 0, 0, 0]), dict(complement=2.0))


class RiskTests(TestCase):
    def test_critical_gap_reported_at_threshold(self):
        members = [profile(1, abilities=(65, 0, 0, 0, 0))]
        found = [r for r in risks(members, dict(abilities=[100, 0, 0, 0, 0])) if r["type"] == "critical_gap"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["dimension"], "编程开发")
        self.assertGreaterEqual(found[0]["gap"], CRITICAL_GAP_THRESHOLD)

    def test_small_gap_is_not_critical(self):
        members = [profile(1, abilities=(75, 0, 0, 0, 0))]
        self.assertEqual([r for r in risks(members, dict(abilities=[100, 0, 0, 0, 0]))
                          if r["type"] == "critical_gap"], [])

    def test_capability_duplication_needs_surplus_and_gap(self):
        # Requirement 40 in dimension 1 but the team reaches 100 (surplus 60)
        # while dimension 2 still lacks 80: duplication plus a critical gap.
        requirement = dict(abilities=[40, 80, 0, 0, 0])
        members = [profile(1, abilities=(100, 0, 0, 0, 0)), profile(2, abilities=(100, 0, 0, 0, 0))]
        found = [r for r in risks(members, requirement) if r["type"] == "capability_duplication"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["dimension"], "编程开发")
        # No gap anywhere: surplus alone is not duplication.
        complete = [profile(1, abilities=(100, 80, 60, 0, 0))]
        self.assertEqual([r for r in risks(complete, dict(abilities=[40, 80, 60, 0, 0]))
                          if r["type"] == "capability_duplication"], [])

    def test_common_time_below_threshold_is_flagged(self):
        # One member covers 60 of 180 required minutes: 33%? No: intersection of both members.
        members = [profile(1, availability=[dict(day=1, start="18:00", end="18:30")]),
                   profile(2, availability=[dict(day=1, start="18:00", end="21:00")])]
        found = [r for r in risks(members, REQUIREMENT) if r["type"] == "common_time_insufficient"]
        self.assertEqual(len(found), 1)
        self.assertLess(found[0]["ratio"], COMMON_TIME_THRESHOLD)

    def test_missing_member_time_is_flagged_as_insufficient(self):
        members = [profile(1, availability=[dict(day=1, start="18:00", end="21:00")]), profile(2)]
        found = [r for r in risks(members, REQUIREMENT) if r["type"] == "common_time_insufficient"]
        self.assertEqual(len(found), 1)
        self.assertIn("未填写", found[0]["explanation"])

    def test_four_categories_together(self):
        requirement = dict(abilities=[40, 80, 0, 0, 0], skills=[],
                           availability=[dict(day=1, start="18:00", end="21:00")],
                           goal="竞赛获奖", experience=[])
        members = [profile(1, abilities=(100, 0, 60, 0, 0), goal="创业实践", name="甲",
                           availability=[dict(day=1, start="18:00", end="19:00")]),
                   profile(2, abilities=(100, 0, 0, 0, 0), goal="竞赛获奖", name="乙")]
        types = sorted(r["type"] for r in risks(members, requirement))
        self.assertEqual(types, ["capability_duplication", "common_time_insufficient",
                                 "critical_gap", "goal_inconsistency"])

    def test_healthy_team_has_no_risks(self):
        members = [profile(1, abilities=(100, 80, 60, 0, 0), skills=["Python", "数据分析"],
                           availability=[dict(day=1, start="18:00", end="21:00")],
                           goal="竞赛获奖", experience=["竞赛"])]
        self.assertEqual(risks(members, REQUIREMENT), [])
