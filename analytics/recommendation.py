"""Scores are normalized internally to [0, 1]; public output uses [0, 100]."""

from dataclasses import dataclass, field
from hashlib import sha256
from json import dumps
from math import isclose, isfinite
from numbers import Real

DIMENSIONS = ("编程开发", "数据分析", "产品设计", "沟通协作", "项目管理")
WEIGHTS = dict(complement=0.35, skill=0.25, time=0.20, goal=0.10, experience=0.10)
VERSION = "baseline-v1"


def number(value, maximum=100):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError("能力值必须是有限数字")
    if not 0 <= value <= maximum or not isfinite(value):
        raise ValueError(f"数值必须介于 0 和 {maximum}")
    return float(value) / maximum


def vector(values=None):
    """Missing vector or coordinates mean zero; invalid inputs are rejected."""
    if values is None:
        return (0.0,) * 5
    if not isinstance(values, (list, tuple)) or len(values) != 5:
        raise ValueError("能力向量必须包含五个维度")
    return tuple(0.0 if v is None else number(v) for v in values)


def weights(values=None):
    result = dict(WEIGHTS if values is None else values)
    if set(result) != set(WEIGHTS):
        raise ValueError("必须提供全部五项权重")
    result = {k: number(v, 1) for k, v in result.items()}
    if not isclose(sum(result.values()), 1, abs_tol=1e-9):
        raise ValueError("权重之和必须为 1")
    return result


def labels(values):
    if not isinstance(values, (list, tuple)) or any(not isinstance(v, str) or not v.strip() for v in values):
        raise ValueError("标签必须为非空字符串数组")
    return frozenset(v.strip().casefold() for v in values)


def slots(values):
    """Union overlapping intervals; never count repeated availability twice."""
    result = set()
    if not isinstance(values, (list, tuple)):
        raise ValueError("可用时间必须为数组")
    for item in values:
        if not isinstance(item, dict) or set(item) != {"day", "start", "end"}:
            raise ValueError("时间段需要 day/start/end")
        day = item["day"]
        if type(day) is not int or not 1 <= day <= 7:
            raise ValueError("day 必须介于 1 和 7")
        minutes = []
        for key in ("start", "end"):
            value = item[key]
            if (not isinstance(value, str) or len(value) != 5 or value[2] != ":"
                    or not value.isascii() or not (value[:2] + value[3:]).isdecimal()):
                raise ValueError("时间格式必须为 HH:mm")
            try:
                h, m = int(value[:2]), int(value[3:])
            except ValueError:
                raise ValueError("时间格式必须为 HH:mm") from None
            if not 0 <= h <= 23 or not 0 <= m <= 59:
                raise ValueError("非法时间")
            minutes.append(h * 60 + m)
        start, end = minutes
        if start >= end:
            raise ValueError("结束时间必须晚于开始时间，跨日请拆分")
        result.update((day - 1) * 1440 + t for t in range(start, end))
    return frozenset(result)


@dataclass(frozen=True)
class Profile:
    id: int
    abilities: tuple = (0, 0, 0, 0, 0)
    skills: frozenset = field(default_factory=frozenset)
    availability: frozenset = field(default_factory=frozenset)
    goal: str = ""
    experience: frozenset = field(default_factory=frozenset)
    display_name: str = ""

    @classmethod
    def parse(cls, data):
        if not isinstance(data, dict) or type(data.get("id")) is not int or data["id"] < 1:
            raise ValueError("id 必须为正整数")
        for key in ("goal", "display_name"):
            if not isinstance(data.get(key, ""), str):
                raise ValueError(f"{key} 必须为字符串")
        return cls(data["id"], vector(data.get("abilities")), labels(data.get("skills", [])),
                   slots(data.get("availability", [])), data.get("goal", "").strip(),
                   labels(data.get("experience", [])), data.get("display_name", ""))


def aggregate(members):
    return tuple(max((m.abilities[i] for m in members), default=0.0) for i in range(5))


def gaps(current, required):
    return tuple(max(r - c, 0.0) for c, r in zip(current, required, strict=True))


def complement(current, required, candidate):
    missing = gaps(current, required)
    filled = tuple(min(g, max(a - c, 0.0)) for g, a, c in zip(missing, candidate, current, strict=True))
    return (sum(filled) / sum(missing) if sum(missing) else 0.0), filled


def recommend(members, required, candidates, *, required_skills=(), availability=(),
              goal="", experience=(), top_k=5, custom_weights=None):
    if type(top_k) is not int or not 0 <= top_k <= 1000:
        raise ValueError("top_k 必须为 0–1000 的整数")
    w = weights(custom_weights)
    target = vector(required)
    wanted_skills, wanted_experience = labels(required_skills), labels(experience)
    wanted_time = slots(availability)
    if not isinstance(goal, str):
        raise ValueError("goal 必须为字符串")
    if len({p.id for p in candidates}) != len(candidates):
        raise ValueError("候选人 id 不得重复")
    current, member_ids = aggregate(members), {m.id for m in members}
    results = []
    for p in candidates:
        if p.id in member_ids:
            continue
        score, filled = complement(current, target, p.abilities)
        parts = dict(complement=score,
                     skill=len(wanted_skills & p.skills) / len(wanted_skills) if wanted_skills else 0.0,
                     time=len(wanted_time & p.availability) / len(wanted_time) if wanted_time else 0.0,
                     goal=float(bool(goal.strip()) and goal.strip().casefold() == p.goal.casefold()),
                     experience=len(wanted_experience & p.experience) / len(wanted_experience) if wanted_experience else 0.0)
        contributions = {k: v * w[k] * 100 for k, v in parts.items()}
        reasons = [f"可补齐{DIMENSIONS[i]} {v * 100:.2f} 分" for i, v in enumerate(filled) if v > 0]
        detail = dict(skill=f"技能命中 {len(wanted_skills & p.skills)}/{len(wanted_skills)} 项",
                      time=f"协作时间覆盖 {parts['time'] * 100:.2f}%",
                      goal="合作目标一致", experience="经历类别匹配")
        reasons.extend(f"{detail[k]}，贡献 {contributions[k]:.2f} 分"
                       for k in detail if contributions[k] > 0)
        risks = []
        if not any(filled):
            risks.append("未补齐当前能力缺口")
        if not wanted_time or not p.availability:
            risks.append("时间信息不足")
        elif not parts["time"]:
            risks.append("可用时间无交集")
        if not p.skills:
            risks.append("技能信息缺失")
        results.append(dict(id=p.id, display_name=p.display_name, skills=sorted(p.skills),
                            score=sum(contributions.values()), scores={k: v * 100 for k, v in parts.items()},
                            contributions=contributions, reasons=reasons, risks=risks,
                            filled=[v * 100 for v in filled]))
    results.sort(key=lambda r: (-r["score"], r["id"]))
    version = VERSION if w == WEIGHTS else "custom-" + sha256(dumps(w, sort_keys=True).encode()).hexdigest()[:12]
    return dict(weight_version=version, weights=w, results=results[:top_k])
