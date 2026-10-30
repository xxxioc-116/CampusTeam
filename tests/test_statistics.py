from unittest import TestCase

from analytics.statistics import formation, ratio, scarcity, transitions


class RatioTests(TestCase):
    def test_zero_denominator_is_zero_not_error(self):
        self.assertEqual(ratio(3, 0), 0.0)
        self.assertEqual(ratio(0, 0), 0.0)

    def test_normal_ratio(self):
        self.assertAlmostEqual(ratio(1, 4), 0.25)


class ScarcityTests(TestCase):
    def demand(self, *rows):
        return {name: {"category": category, "projects": projects} for name, category, projects in rows}

    def test_gap_and_ordering(self):
        demand = self.demand(("Python", "后端", 5), ("Figma", "设计", 3), ("Rust", "后端", 2))
        supply = {"Python": 2, "Rust": 4}
        rows = scarcity(demand, supply)
        # Python and Figma both miss 3 holders; the zero-supply skill ranks first.
        self.assertEqual([r["skill"] for r in rows], ["Figma", "Python", "Rust"])
        self.assertEqual(rows[0]["gap"], 3)
        self.assertEqual(rows[0]["supply_per_project"], 0.0)
        self.assertEqual(rows[1]["gap"], 3)
        self.assertEqual(rows[1]["supply_per_project"], 0.4)
        # Enough holders: gap floors at zero, never negative.
        self.assertEqual(rows[2]["gap"], 0)

    def test_top_n_limits_rows(self):
        demand = self.demand(("A", "", 3), ("B", "", 2), ("C", "", 1))
        self.assertEqual(len(scarcity(demand, {}, top_n=2)), 2)

    def test_empty_demand_returns_empty(self):
        self.assertEqual(scarcity({}, {"Python": 10}), [])


class FormationTests(TestCase):
    def test_rate_and_counts(self):
        self.assertEqual(formation(3, 4), dict(projects=4, formed_projects=3, success_rate=0.75))

    def test_no_projects(self):
        self.assertEqual(formation(0, 0)["success_rate"], 0.0)


class TransitionStatTests(TestCase):
    def test_acceptance_rate(self):
        self.assertEqual(transitions(4, 1), dict(total=4, accepted=1, acceptance_rate=0.25))

    def test_no_requests(self):
        self.assertEqual(transitions(0, 0)["acceptance_rate"], 0.0)
