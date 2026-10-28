# 团队健康度与风险预警（#19–#21）

## 定位

健康度回答"现有团队对自身需求的覆盖程度"，风险预警回答"当前结构可能出什么问题"。
两者均为请求时计算，不落库、无历史快照；不需要新数据库模型。
数据来源与推荐模块相同：`RecommendationProfile` 与 `RecommendationRequirement`。

## 五维健康度公式（#19）

每个分项内部为 0–1，输出 ×100；健康总分 = Σ 分项 × 权重 × 100。

| 分项 | 权重 | 公式 | 缺失口径 |
|---|---|---|---|
| capability 能力达成 | 0.35 | Σ min(C,R) / Σ R，C 为成员逐维最大值聚合 | 需求全零记 0 |
| skill 技能覆盖 | 0.25 | (团队技能并集 ∩ 需求技能) / 需求技能数 | 需求为空记 0 |
| time 时间重合 | 0.20 | 全员可用时间交集 ∩ 需求协作时间 / 需求分钟数（#20） | 需求为空记 0 |
| goal 目标一致 | 0.10 | 目标非空且与团队目标一致的成员占比（#20） | 团队目标为空记 0 |
| experience 经验覆盖 | 0.10 | (团队经验并集 ∩ 需求经验) / 需求经验数 | 需求为空记 0 |

权重沿用推荐模块默认配置（ADR 0001）；团队配置了自定义权重时健康度使用
同一配置，五项非负且和为 1 的校验一致。没有需求或缺少信息的分项为 0，
不凭空赋满分。

### 典型算例

需求：abilities=[100,80,60,0,0]、skills=[Python,数据分析]、周一 18:00–21:00、
goal=竞赛获奖、experience=[竞赛]。成员甲：abilities=[100,80,60,0,0]、
skills=[Python,数据分析]、周一 18:00–21:00、goal=竞赛获奖、experience=[竞赛]；
成员乙：abilities=[60,0,0,0,0]、skills=[Python]、周一 18:00–19:00、
goal=竞赛获奖。

- capability = (100+80+60)/240 = 100 → 贡献 35
- skill = 2/2 = 100 → 贡献 25
- time = 全员交集 60 分钟 / 180 分钟 = 33.33% → 贡献 6.67
- goal = 2/2 = 100 → 贡献 10
- experience = 1/1 = 100 → 贡献 10
- 总分 = 86.67 → healthy

## 时间重合度与目标一致性（#20）

- 时间按星期 1–7、当日 HH:mm、左闭右开分钟区间处理；重叠自动去重，
  跨日必须拆分（延续推荐模块契约）。
- 重合度使用**全员交集**：一人不在场即共同时间为空，这与"团队协作要求
  人人到场"的产品语义一致。
- 任一成员未填写可用时间时交集为空，得分如实为 0，同时输出
  common_time_insufficient 风险并注明"信息可能未填写"，避免把未填写
  误读为已测得的零。
- 多个不相交的交集窗口按分钟并集累计；无交集得 0。
- 目标比对去首尾空格、忽略大小写；团队目标为空时不评估。

## 风险预警（#21，固定阈值）

| 类型 | 级别 | 触发条件 |
|---|---|---|
| critical_gap | high | 某维度缺口 ≥ 30 分 |
| capability_duplication | medium | ≥2 名成员可独立覆盖同一非零需求维度，且其他维度存在 ≥10 分缺口 |
| common_time_insufficient | medium | 全员共同时间覆盖 <20%，或成员时间信息缺失 |
| goal_inconsistency | medium | 存在成员目标非空但与团队目标不一致 |

阈值定义在 `analytics/team_health.py` 常量中；本期不做 API 可调参数
（ADR 0003），如需调整随版本发布。

### 健康分档

| 状态 | 总分 |
|---|---|
| healthy | ≥ 80 |
| watch | 60–79 |
| at_risk | < 60 |

## API

`GET /api/v1/teams/{id}/health`，权限与 matrix/gaps/recommendations 一致
（本团队成员、队长或业务 ADMIN；匿名 401、越权 403、团队不存在 404）；
需求未配置返回 400。响应示例：

```json
{
  "status": "healthy",
  "thresholds": {"healthy": 80, "watch": 60},
  "dimensions": ["编程开发", "数据分析", "产品设计", "沟通协作", "项目管理"],
  "scores": {"capability": 100, "skill": 100, "time": 33.33, "goal": 100, "experience": 100},
  "total": 86.67,
  "weights": {"complement": 0.35, "skill": 0.25, "time": 0.2, "goal": 0.1, "experience": 0.1},
  "risks": [{"type": "common_time_insufficient", "level": "medium", "ratio": 0.3333,
             "explanation": "全员共同可用时间仅覆盖需求 33.33%，低于 20% 阈值"}],
  "team_id": 1, "project_id": 1, "team_name": "Health"
}
```

> 注：上文 risks 示例为演示两个字段的形状；33.33% 实际不会触发 <20% 阈值，
> 以 API 实测输出为准。分项与总分不提前舍入，UI 可显示两位小数。

## 运行与验证

```powershell
python -m unittest discover -s tests -v
$env:DJANGO_DEBUG="true"; python manage.py test core tests
```

纯算法测试见 `tests/test_team_health.py`（22 个用例），API 测试见
`core/tests/test_team_health_api.py`（6 个用例）。设计决策见
ADR 0003。
