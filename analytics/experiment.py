"""Run with python -m analytics.experiment; stdout is reproducible JSON (except timing)."""

import json
import random
import statistics
from math import sqrt
from time import perf_counter

from .recommendation import Profile, aggregate, complement, recommend, vector


def run(seed=20261027):
    rng = random.Random(seed)
    members = [Profile.parse(dict(id=1, abilities=[90, 20, 80, 30, 70]))]
    required = [90] * 5
    current, target = aggregate(members), vector(required)
    reports = []
    for size in (100, 500, 1000):
        people = [Profile.parse(dict(id=i + 2, abilities=[rng.randrange(101) for _ in range(5)]))
                  for i in range(size)]
        elapsed = []
        for _ in range(7):
            start = perf_counter()
            result = recommend(members, required, people)
            elapsed.append((perf_counter() - start) * 1000)
        ids = [r["id"] for r in result["results"]]
        assert len(ids) == 5 and len(set(ids)) == 5
        assert result == recommend(members, required, list(reversed(people)))
        by_id = {p.id: p for p in people}
        selections = {
            "random": rng.sample(people, 5),
            "similar": sorted(people, key=lambda p: (-cosine(current, p.abilities), p.id))[:5],
            "complement": [by_id[i] for i in ids],
        }
        quality = {name: statistics.mean(complement(current, target, p.abilities)[0] for p in chosen)
                   for name, chosen in selections.items()}
        reports.append(dict(candidates=size, median_ms=statistics.median(elapsed),
                            max_ms=max(elapsed), mean_gap_coverage_at_5=quality,
                            selected_ids={k: [p.id for p in v] for k, v in selections.items()}))
    return dict(seed=seed, repeats=7, dataset="synthetic uniform integer abilities 0..100",
                note="Algorithm timing only; API and database latency measured separately. Synthetic results are not user satisfaction evidence.",
                reports=reports)


def cosine(a, b):
    denominator = sqrt(sum(v * v for v in a) * sum(v * v for v in b))
    return sum(x * y for x, y in zip(a, b, strict=True)) / denominator if denominator else 0


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
