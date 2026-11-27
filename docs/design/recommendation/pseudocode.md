# 推荐算法伪代码集（素材）

> 对应报告 6.11–6.14、6.18 节。实现基准为 `analytics/recommendation.py`。

## 1 Top-K 稳定排序

```text
算法 TopKSort(candidates, top_k, weights):
输入：candidates 为已算出分项的候选列表；top_k 为整数；weights 为五项权重
输出：稳定排序后的前 top_k 名

 1  if top_k 不是整数 or top_k < 0 or top_k > 1000:
 2      raise ValueError(0–1000 的整数)
 3  if 候选 id 去重后的数量 ≠ candidates 长度: raise ValueError(id 不得重复)
 4  for p ∈ candidates:
 5      for k ∈ 五项:
 6          p.contributions[k] ← 100 × p.scores[k] × weights[k]
 7      p.score ← Σ p.contributions[k]
 8  sort candidates by key = (−p.score, p.id)      // 降序，同分按 id 升序
 9  return candidates[0 : min(top_k, len(candidates))]
```

说明：第 8 行用复合键保证同分场景结果确定；排序前不取整，避免舍入造成并列。第 9 行天然覆盖 top_k = 0 与 top_k > n 两种边界。

## 2 推荐理由生成

```text
算法 BuildReasons(p, filled, scores, contributions, context):
 1  reasons ← []
 2  for j = 1 to 5:
 3      if filled[j] > 0:
 4          reasons.append(可补齐 + DIMENSIONS[j] + fmt(filled[j]×100, 2) + 分)
 5  if contributions.skill > 0:
 6      reasons.append(技能命中 hit/total 项，贡献 fmt(contributions.skill,2) 分)
 7  if contributions.time > 0:
 8      reasons.append(协作时间覆盖 fmt(scores.time×100,2)%，贡献 fmt(contributions.time,2) 分)
 9  if contributions.goal > 0:
10      reasons.append(合作目标一致，贡献 fmt(contributions.goal,2) 分)
11  if contributions.experience > 0:
12      reasons.append(经历类别匹配，贡献 fmt(contributions.experience,2) 分)
13  return reasons
```

说明：理由与分项贡献一一对应，避免出现总分高但没有理由，或理由与得分不一致的情况。

## 3 风险提示生成

```text
算法 BuildRisks(p, filled, project):
 1  risks ← []
 2  if 所有 filled[j] 均为 0: risks.append(未补齐当前能力缺口)
 3  if project.availability 为空 or p.availability 为空:
 4      risks.append(时间信息不足)
 5  else if |project.availability ∩ p.availability| = 0:
 6      risks.append(可用时间无交集)
 7  if p.skills 为空: risks.append(技能信息缺失)
 8  return risks
```

## 4 缺失值与异常输入处理

```text
算法 NormalizeInput(v, maximum=100):
 1  if v 是布尔值 or v 不是实数类型: raise ValueError(能力值必须是有限数字)
 2  if v < 0 or v > maximum or v 非有限: raise ValueError(数值越界)
 3  return float(v) / maximum

算法 AbilityVector(values):
 1  if values is None: return (0, 0, 0, 0, 0)
 2  if values 不是 list/tuple or 长度 ≠ 5: raise ValueError(必须包含五个维度)
 3  return tuple(0.0 if v is None else NormalizeInput(v) for v in values)

算法 Weights(values):
 1  w ← values if values 非空 else WEIGHTS
 2  if keys(w) ≠ 五项权重: raise ValueError(必须提供全部五项)
 3  for k ∈ w: w[k] ← NormalizeInput(w[k], maximum=1)
 4  if |Σ w[k] − 1| > 1e-9: raise ValueError(权重之和必须为 1)
 5  return w

算法 TimeSlots(values):
 1  if values 不是 list/tuple: raise ValueError(可用时间必须为数组)
 2  result ← 空集
 3  for item ∈ values:
 4      if item 不是 dict or keys(item) ≠ {day, start, end}: raise ValueError(字段错误)
 5      if type(day) ≠ int or day ∉ [1,7]: raise ValueError(day 必须介于 1 和 7)
 6      if start/end 不符合 HH:mm 或时分非法: raise ValueError(时间格式错误)
 7      if start ≥ end: raise ValueError(结束时间必须晚于开始时间，跨日请拆分)
 8      result ∪= { (day−1)×1440 + t | t ∈ [start, end) }
 9  return result
```

边界口径：缺失的向量或单维 null 记为 0，但不表示已测得零能力，采集端应提示补全画像；字符串、布尔、NaN、无穷、越界一律拒绝；候选 id 重复拒绝；已有团队成员在评分前排除。
