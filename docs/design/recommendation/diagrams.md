# 推荐算法设计图（Mermaid 源）

> GitHub 可直接渲染。报告阶段导出为 PNG 后放入 `docs/design/assets/recommendation/`，按 X-Y 编号，图题置于图下方，五号宋体加粗。

## 推荐模块类图

```mermaid
classDiagram
    class Profile {
        +int id
        +tuple abilities
        +frozenset skills
        +frozenset availability
        +str goal
        +frozenset experience
        +parse(data) Profile
    }
    class TeamState {
        +tuple current
        +set member_ids
        +aggregate(members) tuple
    }
    class Requirement {
        +tuple required
        +frozenset skills
        +frozenset availability
        +str goal
        +frozenset experience
    }
    class GapCalculator {
        +gaps(current, required) tuple
        +complement(current, required, candidate) tuple
    }
    class ScoringService {
        +dict weights
        +score(candidate, context) Result
        +rank(results, top_k) list
    }
    class RecommendationResult {
        +int id
        +float score
        +dict scores
        +dict contributions
        +list reasons
        +list risks
        +list filled
    }
    Profile --> TeamState : 逐维聚合
    TeamState --> GapCalculator : 团队能力 C
    Requirement --> GapCalculator : 需求 R
    GapCalculator --> ScoringService : 互补度分项
    Requirement --> ScoringService : 技能时间目标经历
    ScoringService --> RecommendationResult : 生成
```

## 能力矩阵结构图

```mermaid
flowchart LR
    U1[成员 A 能力向量] --> M[团队能力矩阵 C 逐维最大值]
    U2[成员 B 能力向量] --> M
    U3[成员 C 能力向量] --> M
    M --> D1[编程开发]
    M --> D2[数据分析]
    M --> D3[产品设计]
    M --> D4[沟通协作]
    M --> D5[项目管理]
    R[项目需求向量 R] --> G[缺口向量 G]
    D1 --> G
    D2 --> G
    D3 --> G
    D4 --> G
    D5 --> G
    G --> A[候选人有效补量 F]
```

## 能力缺口计算流程图

```mermaid
flowchart TD
    A[输入 C R A] --> B[G(j) = max R(j) 减 C(j) 与 0 的较大值]
    B --> Q{缺口总和大于 0}
    Q -- 否 --> D[complement 记为 0]
    Q -- 是 --> E[F(p,j) = min G(j) 与 max A(p,j) 减 C(j)]
    E --> H[complement = 所有 F 之和 除以 所有 G 之和]
    D --> I[输出补量 F 与互补度]
    H --> I
```

## 推荐活动图

```mermaid
flowchart TD
    S([推荐请求]) --> V[参数校验: top_k 能力 时间 标签]
    V -->|非法| E([返回 400 统一错误])
    V -->|合法| P[读取画像与团队成员]
    P --> A[聚合团队能力 C]
    A --> G[计算缺口 G]
    G --> F[排除现有成员]
    F --> SC[五维评分与加权总分]
    SC --> R[稳定排序 按总分降序 id 升序]
    R --> T[截取 Top-K]
    T --> O[生成理由与风险]
    O --> Z([返回推荐结果])
```

## 推荐查询时序图

```mermaid
sequenceDiagram
    participant U as 前端页面
    participant API as 推荐 API
    participant S as ScoringService
    participant DB as 画像与团队仓储
    U->>API: GET /api/recommendations?top_k=5
    API->>API: 校验 Token 与 top_k
    API->>DB: 查询画像与团队成员
    DB-->>API: members 与 profile
    API->>S: recommend(members, required, candidates, weights)
    S->>S: 聚合 C 到 缺口 G 到 五维评分 到 稳定排序
    S-->>API: weight_version 与 results
    API-->>U: 200 与推荐结果
```
