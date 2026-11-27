# 推荐算法公式集（素材）

> 对应报告 6.4–6.11 节。能力值内部归一化到 [0,1]，公开输出乘以 100 映射到 [0,100]。实现基准为 `analytics/recommendation.py`（VERSION = baseline-v1）。公式在正式报告中转为 Word 公式对象。

## 1 符号约定

| 符号 | 含义 |
|---|---|
| D | 五个固定能力维度：编程开发、数据分析、产品设计、沟通协作、项目管理，共 5 维 |
| x(u,j) | 用户 u 在维度 j 的能力，输入 0–100 有限数字，内部 a(u,j) = x(u,j) / 100 |
| M / P | 当前团队成员集合 / 候选用户集合，评分前由 P 排除 M |
| C(j) | 团队在维度 j 的现有能力 |
| R(j) | 项目在维度 j 的需求能力 |
| G(j) | 团队在维度 j 的能力缺口 |
| F(p,j) | 候选人 p 在维度 j 的实际有效补量 |
| w(k) | 第 k 项评分权重，k 取 complement、skill、time、goal、experience |
| s(p,k) | 候选人 p 的第 k 项得分，内部取值 [0,1] |
| S(p) | 候选人 p 的加权总分，公开取值 [0,100] |

## 2 能力聚合公式（6.5）

团队能力取成员逐维最大值，表示「团队是否有人具备该能力」，不累加人数或工时：

    C(j) = max { a(u,j) | u ∈ M },  j = 1..5

当 M 为空时 C(j) = 0。成员加入或退出后重新计算，不设聚合缓存。

## 3 能力缺口公式（6.6）

    G(j) = max(R(j) − C(j), 0),  j = 1..5

缺失画像或单维缺失按 0 处理；G(j) = 0 表示该维无缺口。

## 4 有效补量公式（6.7）

    F(p,j) = min( G(j), max(a(p,j) − C(j), 0) ),  j = 1..5

该式同时防止两种误判：候选人能力低于团队现状时不产生负补量；候选人能力远超需求时只计到缺口上限，避免重复能力被当作互补。候选人互补度为：

    complement(p) = ΣF(p,j) / ΣG(j)   （当 ΣG(j) > 0）
    complement(p) = 0                 （当 ΣG(j) = 0）

算例：C = [0.80, 0.40, 0, 0, 0]，R = [1.00, 0.80, 0, 0, 0]，A = [0.80, 0.60, 0, 0, 0]。
G = [0.20, 0.40, 0, 0, 0]，F = [0, 0.20, 0, 0, 0]，complement = 0.20 / 0.60 = 1/3。

## 5 五维评分公式（6.8）

| 分项 k | 公式 | 分母为 0 时 |
|---|---|---|
| complement | complement(p)，见第 4 节 | 0 |
| skill | s(skill) = |S(proj) ∩ S(p)| / |S(proj)| | 0 |
| time | s(time) = |T(proj) ∩ T(p)| / |T(proj)| | 0 |
| goal | s(goal) = 1（g(proj) 非空且忽略大小写后与 g(p) 相同），否则为 0 | 0 |
| experience | s(experience) = |E(proj) ∩ E(p)| / |E(proj)| | 0 |

S 为技能标签集（去首尾空格、忽略大小写、去重）；T 为可用分钟集合，按星期 1–7 与当日 HH:mm 左闭右开区间展开，重叠自动去重、跨日拆分；E 为已确认的经历类别标签，不从自由文本猜测。

## 6 权重设计（6.9）

| 分项 | complement | skill | time | goal | experience | 合计 |
|---|---|---|---|---|---|---|
| 默认权重 w(k) | 0.35 | 0.25 | 0.20 | 0.10 | 0.10 | 1.00 |

配置必须包含全部五项、每一项非负且和为 1（容差 1e-9）。默认版本记为 baseline-v1；自定义权重记为 custom- 加上按 key 排序 JSON 的 SHA-256 前 12 位，字段顺序变化不改变版本。

## 7 加权总分公式（6.10）

    c(p,k) = 100 × s(p,k) × w(k)
    S(p)   = Σ c(p,k)

分项公开值 100 × s(p,k)、贡献值 c(p,k) 均不提前舍入，UI 层可显示两位小数。

## 8 Top-K 稳定排序（6.11）

    sort candidates by key = (−S(p), id(p))
    TopK = 排序结果的前 min(k, n) 项

k 为整数且 0 ≤ k ≤ 1000；k = 0 返回空列表，k > n 返回全部。候选人 id 必须为正整数且互不重复。

## 9 推荐输入与输出表（6.2）

| 方向 | 字段 | 类型 | 约束 |
|---|---|---|---|
| 输入 | members[].abilities | number[5] | 0–100 有限数字；null 或整组缺失记为 0 |
| 输入 | required | number[5] | 同上 |
| 输入 | required_skills / experience | string[] | 非空字符串，忽略大小写与首尾空格 |
| 输入 | availability | object[] | day 为 1–7，start/end 为 HH:mm，end > start |
| 输入 | goal | string | 可为空 |
| 输入 | top_k | int | 0–1000 |
| 输入 | custom_weights | object | 五项齐全、非负、和为 1 |
| 输出 | weight_version | string | baseline-v1 或 custom- 加哈希前 12 位 |
| 输出 | results[].score | number | 未舍入总分 |
| 输出 | results[].scores / contributions | object | 分项分与分项贡献 |
| 输出 | results[].reasons / risks | string[] | 可解释理由与风险提示 |
| 输出 | results[].filled | number[5] | 逐维有效补量（0–100） |
