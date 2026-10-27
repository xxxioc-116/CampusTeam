import unittest

from analytics.recommendation import Profile, aggregate, complement, recommend, slots, vector, weights


class RecommendationTests(unittest.TestCase):
    def profile(self, id=1, abilities=None, **kwargs):
        return Profile.parse(dict(id=id, abilities=abilities, **kwargs))

    def test_normalization_missing_min_max(self):
        self.assertEqual(vector(), (0,) * 5)
        self.assertEqual(vector([None, 0, 100, 50, 25]), (0, 0, 1, .5, .25))

    def test_invalid_vectors(self):
        for value in ([0], "12345", [True] * 5, [-1] * 5, [101] * 5,
                      [float("nan")] * 5, [float("inf")] * 5, ["50"] * 5, [10**1000] * 5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                vector(value)

    def test_weights(self):
        self.assertAlmostEqual(sum(weights().values()), 1)
        for value in ({}, dict(complement=1), {k: .1 for k in weights()},
                      {**weights(), "time": True}, {**weights(), "goal": -1}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                weights(value)

    def test_aggregate_and_manual_complement(self):
        members = [self.profile(1, [80, 20, 0, 0, 0]), self.profile(2, [50, 40, 0, 0, 0])]
        current = aggregate(members)
        self.assertEqual(current, (.8, .4, 0, 0, 0))
        score, filled = complement(current, vector([100, 80, 0, 0, 0]), vector([80, 60, 0, 0, 0]))
        self.assertAlmostEqual(score, 1 / 3)
        self.assertAlmostEqual(filled[1], .2)
        self.assertEqual(complement(current, vector([100, 80, 0, 0, 0]), current)[0], 0)
        self.assertEqual(complement(current, current, vector([100] * 5))[0], 0)
        self.assertEqual(aggregate([]), (0,) * 5)

    def test_time_union_and_validation(self):
        item = dict(day=1, start="18:00", end="20:00")
        self.assertEqual(len(slots([item, item, dict(day=1, start="19:00", end="21:00")])), 180)
        for item in (dict(day=True, start="18:00", end="20:00"),
                     dict(day=8, start="18:00", end="20:00"),
                     dict(day=1, start="24:00", end="25:00"),
                     dict(day=1, start="20:00", end="18:00"),
                     dict(day=1, start="oops!", end="20:00"),
                     dict(day=1, start="+1:00", end="20:00"),
                     dict(day=1, start="１８:００", end="20:00"), {}):
            with self.subTest(item=item), self.assertRaises(ValueError):
                slots([item])

    def test_full_score_and_explanation_consistency(self):
        time = [dict(day=1, start="18:00", end="20:00")]
        p = self.profile(2, [100] * 5, skills=["Python", "python"], availability=time,
                         goal="学习", experience=["课程"])
        r = recommend([], [100] * 5, [p], required_skills=["Python"], availability=time,
                      goal="学习", experience=["课程"])["results"][0]
        self.assertAlmostEqual(r["score"], 100)
        self.assertAlmostEqual(sum(r["contributions"].values()), r["score"])
        self.assertEqual(len(r["reasons"]), 9)
        self.assertEqual(r["risks"], [])

    def test_configurable_weights_change_ranking_and_are_traceable(self):
        complement = self.profile(1, [100] * 5)
        skill = self.profile(2, [20] * 5, skills=["Python"])
        kwargs = dict(required_skills=["Python"])
        baseline = recommend([], [100] * 5, [skill, complement], **kwargs)
        self.assertEqual(baseline["results"][0]["id"], 1)
        config = dict(complement=.1, skill=.9, time=0, goal=0, experience=0)
        changed = recommend([], [100] * 5, [skill, complement], custom_weights=config, **kwargs)
        self.assertEqual(changed["results"][0]["id"], 2)
        self.assertNotEqual(baseline["weight_version"], changed["weight_version"])
        reordered = recommend([], [100] * 5, [complement, skill], custom_weights=dict(reversed(list(config.items()))), **kwargs)
        self.assertEqual(changed["weight_version"], reordered["weight_version"])
        self.assertIn("技能命中 1/1 项，贡献 90.00 分", changed["results"][0]["reasons"])

    def test_sort_k_and_members_exclusion(self):
        candidates = [self.profile(i) for i in (3, 2, 1)]
        for k, expected in ((0, []), (1, [2]), (999, [2, 3])):
            r = recommend([candidates[2]], [100] * 5, candidates, top_k=k)
            self.assertEqual([p["id"] for p in r["results"]], expected)
        for k in (-1, 1001, True, 1.5):
            with self.assertRaises(ValueError):
                recommend([], [0] * 5, [], top_k=k)
        with self.assertRaises(ValueError):
            recommend([], [0] * 5, [candidates[0], candidates[0]])

    def test_missing_data_does_not_create_matches(self):
        r = recommend([], [0] * 5, [self.profile()])["results"][0]
        self.assertEqual(r["score"], 0)
        self.assertIn("技能信息缺失", r["risks"])
        self.assertEqual(r["reasons"], [])

    def test_profile_validation(self):
        for data in ({}, dict(id=True), dict(id=0), dict(id=1, skills="Python"),
                     dict(id=1, goal=None), dict(id=1, experience=[""])):
            with self.subTest(data=data), self.assertRaises(ValueError):
                Profile.parse(data)


if __name__ == "__main__":
    unittest.main()
