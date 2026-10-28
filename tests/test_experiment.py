import unittest

from analytics.experiment import cosine, run


class ExperimentTests(unittest.TestCase):
    def stable_results(self, report):
        return [{k: v for k, v in row.items() if k not in {"median_ms", "max_ms"}}
                for row in report["reports"]]

    def test_fixed_seed_reproduces_candidates_and_metrics(self):
        first, second = run(42), run(42)
        self.assertEqual(self.stable_results(first), self.stable_results(second))
        self.assertEqual([r["candidates"] for r in first["reports"]], [100, 500, 1000])

    def test_seed_changes_the_dataset(self):
        self.assertNotEqual(self.stable_results(run(1)), self.stable_results(run(2)))

    def test_quality_metric_and_unique_selection(self):
        for row in run()["reports"]:
            quality = row["mean_gap_coverage_at_5"]
            for ids in row["selected_ids"].values():
                self.assertEqual(len(set(ids)), 5)
            for value in quality.values():
                self.assertGreaterEqual(value, 0)
                self.assertLessEqual(value, 1)
            # Complement directly optimizes this metric; this is not evidence of user preference.
            self.assertGreaterEqual(quality["complement"], quality["similar"])
            self.assertGreaterEqual(quality["complement"], quality["random"])

    def test_cosine_zero_identical_and_orthogonal(self):
        self.assertEqual(cosine((0, 0), (1, 2)), 0)
        self.assertAlmostEqual(cosine((1, 2), (1, 2)), 1)
        self.assertEqual(cosine((1, 0), (0, 1)), 0)
