"""Pure aggregation helpers for the admin statistics API (#23).

No Django imports: the view layer collects counts, this module defines the
metric semantics so the formulas stay reviewable and unit-testable.
Internal ratios are [0, 1]; the API layer decides display precision.
"""


def ratio(numerator, denominator):
    """Safe ratio; a zero denominator means "no data", reported as 0.0."""
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def scarcity(demand, supply, top_n=None):
    """Rank skills by unmet demand.

    ``demand`` maps skill name -> {"category": str, "projects": int} and counts
    how many projects list that skill as a requirement.
    ``supply`` maps skill name -> number of active students owning the skill.

    gap = max(projects − students, 0): each project needs at least one holder,
    so a skill whose holders are fewer than the projects requiring it is scarce.
    Skills nobody requires are excluded; a required skill nobody owns scores the
    largest gap and supply_per_project = 0.
    """
    rows = []
    for name, info in demand.items():
        required = info["projects"]
        holders = supply.get(name, 0)
        rows.append(dict(skill=name, category=info.get("category", ""),
                         demand_projects=required, supply_students=holders,
                         gap=max(required - holders, 0),
                         supply_per_project=ratio(holders, required)))
    rows.sort(key=lambda r: (-r["gap"], r["supply_per_project"], r["skill"]))
    return rows[:top_n] if top_n is not None else rows


def formation(formed, total):
    """Team formation success: projects whose team has at least two members."""
    return dict(projects=total, formed_projects=formed, success_rate=ratio(formed, total))


def transitions(total, accepted):
    """Acceptance statistics shared by applications and invitations."""
    return dict(total=total, accepted=accepted, acceptance_rate=ratio(accepted, total))
