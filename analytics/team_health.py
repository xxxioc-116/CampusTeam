"""Team health metrics, time/goal alignment and risk warnings (#19-#21).

Pure functions only: no Django imports, mirroring analytics/recommendation.py.
Internal scores are normalized to [0, 1]; public output uses [0, 100].

Health semantics: how well the current team covers its own requirement
(RecommendationRequirement). The five sub-scores map one-to-one onto the
requirement fields abilities/skills/availability/goal/experience, and reuse
the recommendation default weights (ADR 0001): capability 0.35, skill 0.25,
time 0.20, goal 0.10, experience 0.10.
"""

from analytics.recommendation import DIMENSIONS, aggregate, gaps, labels, slots, vector, weights

# Fixed risk thresholds (documented in docs/team-health.md; not API-tunable).
HEALTHY_THRESHOLD = 80.0
WATCH_THRESHOLD = 60.0
CRITICAL_GAP_THRESHOLD = 30.0  # points (0-100 scale) on a single dimension
DUPLICATION_GAP_THRESHOLD = 10.0  # other-dimension gap that makes redundant coverage wasteful
COMMON_TIME_THRESHOLD = 0.20  # fraction of required collaboration minutes

# Health dimension -> recommendation weight key (same default weight values).
WEIGHT_KEY_MAP = dict(capability="complement", skill="skill", time="time",
                      goal="goal", experience="experience")
HEALTH_DIMENSIONS = tuple(WEIGHT_KEY_MAP)


def time_overlap(member_slot_sets, required):
    """Return (covered, required_minutes, info_missing) in requirement minutes.

    Uses the intersection of ALL member availability: team collaboration
    requires everyone to be present at the same time. When any member provides
    no availability the intersection is empty and ``info_missing`` marks that
    the score may reflect an unfinished profile rather than a measured zero.
    """
    required_minutes = float(len(required))
    if not member_slot_sets:
        return 0.0, required_minutes, True
    info_missing = any(not s for s in member_slot_sets)
    if not required:
        return 0.0, required_minutes, info_missing
    common = frozenset.intersection(*member_slot_sets) if len(member_slot_sets) > 1 else member_slot_sets[0]
    return float(len(common & required)), required_minutes, info_missing


def time_overlap_score(members, requirement_availability):
    """Time overlap ratio in [0, 1].

    The intersection is a true intersection: one member with no availability
    makes the common time empty, scoring 0; the API layer reports the missing
    information as a risk so an unfilled profile is not read as a measured zero.
    """
    required = slots(requirement_availability)
    if not required or not members:
        return 0.0
    covered, required_minutes, _ = time_overlap([m.availability for m in members], required)
    return covered / required_minutes


def goal_alignment_score(members, team_goal):
    """Fraction of members whose goal matches the team goal (case-insensitive).

    An empty team goal cannot be evaluated and scores 0, consistent with the
    recommendation module's rule that missing requirements never score full.
    """
    target = team_goal.strip().casefold() if isinstance(team_goal, str) else ""
    if not target or not members:
        return 0.0
    aligned = sum(1 for m in members if m.goal.strip().casefold() == target)
    return aligned / len(members)


def as_label_list(value):
    """Normalize the requirement experience field (str or list) to a list."""
    if isinstance(value, str):
        return [value] if value.strip() else []
    return list(value) if isinstance(value, (list, tuple)) else []


def coverage_score(team_values, required_values):
    """Label-set coverage: team union hit count / required label count."""
    required = labels(as_label_list(required_values))
    if not required:
        return 0.0
    team_set = frozenset.union(*team_values) if team_values else frozenset()
    return len(team_set & required) / len(required)


def health(members, requirement, custom_weights=None):
    """Compute the five-dimension team health for one team.

    ``requirement`` uses the same field shape as RecommendationRequirement.
    Returns [0, 100] sub-scores, the weighted total, the effective weights and
    the fixed dimension order.
    """
    if not members:
        raise ValueError("团队至少需要一名成员")
    w = weights(custom_weights)
    target = vector(requirement.get("abilities"))
    team_abilities = aggregate(members)
    capability = (sum(min(c, r) for c, r in zip(team_abilities, target, strict=True)) / sum(target)
                  if sum(target) else 0.0)
    parts = dict(capability=capability,
                 skill=coverage_score([m.skills for m in members], requirement.get("skills") or []),
                 time=time_overlap_score(members, requirement.get("availability") or []),
                 goal=goal_alignment_score(members, requirement.get("goal", "")),
                 experience=coverage_score([m.experience for m in members], requirement.get("experience") or []))
    return dict(dimensions=DIMENSIONS,
                scores={k: parts[k] * 100 for k in HEALTH_DIMENSIONS},
                total=sum(parts[k] * w[WEIGHT_KEY_MAP[k]] for k in HEALTH_DIMENSIONS) * 100,
                weights={WEIGHT_KEY_MAP[k]: w[WEIGHT_KEY_MAP[k]] for k in HEALTH_DIMENSIONS})


def risks(members, requirement):
    """Evaluate the four risk categories from #21.

    Returns a list of dicts with stable ``type`` values: critical_gap,
    capability_duplication, common_time_insufficient, goal_inconsistency.
    """
    result = []
    target = vector(requirement.get("abilities"))
    team_abilities = aggregate(members)
    missing = gaps(team_abilities, target)
    # 1. Critical gaps.
    for i, gap_value in enumerate(missing):
        if gap_value * 100 >= CRITICAL_GAP_THRESHOLD:
            result.append(dict(type="critical_gap", level="high", dimension=DIMENSIONS[i],
                               gap=round(gap_value * 100, 10),
                               explanation=f"{DIMENSIONS[i]}缺口 {gap_value * 100:.2f} 分，达到关键阈值"))
    # 2. Capability duplication: at least two members individually cover the
    # same required dimension while other dimensions still lack coverage.
    if any(g * 100 >= DUPLICATION_GAP_THRESHOLD for g in missing):
        for i, required_level in enumerate(target):
            if required_level <= 0:
                continue
            covering = [m.display_name or str(m.id) for m in members if m.abilities[i] >= required_level]
            if len(covering) >= 2:
                result.append(dict(type="capability_duplication", level="medium", dimension=DIMENSIONS[i],
                                   members=covering,
                                   explanation=f"{len(covering)} 名成员均可独立覆盖{DIMENSIONS[i]}，"
                                               f"同时其他维度仍有缺口"))
    # 3. Insufficient common time.
    required = slots(requirement.get("availability") or [])
    covered, required_minutes, info_missing = time_overlap([m.availability for m in members], required)
    if required_minutes:
        if info_missing:
            result.append(dict(type="common_time_insufficient", level="medium", ratio=0.0,
                               explanation="部分成员未填写可用时间，无法评估全员共同协作时间"))
        else:
            ratio = covered / required_minutes
            if ratio < COMMON_TIME_THRESHOLD:
                result.append(dict(type="common_time_insufficient", level="medium", ratio=round(ratio, 10),
                                   explanation=f"全员共同可用时间仅覆盖需求 {ratio * 100:.2f}%，"
                                               f"低于 {COMMON_TIME_THRESHOLD * 100:.0f}% 阈值"))
    # 4. Goal inconsistency.
    team_goal = requirement.get("goal", "")
    target_goal = team_goal.strip().casefold() if isinstance(team_goal, str) else ""
    if target_goal:
        mismatched = [m.display_name or str(m.id) for m in members
                      if m.goal.strip() and m.goal.strip().casefold() != target_goal]
        if mismatched:
            result.append(dict(type="goal_inconsistency", level="medium", members=mismatched,
                               explanation="以下成员的个人目标与团队目标不一致：" + "、".join(mismatched)))
    return result


def evaluate(members, requirement, custom_weights=None):
    """One-call entry: health scores, status band and risks."""
    health_result = health(members, requirement, custom_weights)
    total = health_result["total"]
    if total >= HEALTHY_THRESHOLD:
        status = "healthy"
    elif total >= WATCH_THRESHOLD:
        status = "watch"
    else:
        status = "at_risk"
    return dict(status=status,
                thresholds=dict(healthy=HEALTHY_THRESHOLD, watch=WATCH_THRESHOLD),
                **health_result,
                risks=risks(members, requirement))
