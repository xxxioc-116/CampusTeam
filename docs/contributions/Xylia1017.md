# 个人工程贡献说明书 - Xylia1017

- 学号：202426204019
- GitHub：[@Xylia1017](https://github.com/Xylia1017)
- 小组：CampusTeam
- 承担角色：后端分析与测试（健康度 / 管理员统计 / 覆盖率 / E2E / 性能回归）
- 统计截止：2026-11-02

## 一、任务完成情况

| Issue | 标题 | 状态 | 主要 PR | 完成时间 |
|---|---|---|---|---|
| [#19](https://github.com/xxxioc-116/CampusTeam/issues/19) | 定义团队健康度指标与阈值 | Closed | [#37](https://github.com/xxxioc-116/CampusTeam/pull/37) | 2026-10-28 |
| [#20](https://github.com/xxxioc-116/CampusTeam/issues/20) | 实现时间重合度与目标一致性算法 | Closed | [#37](https://github.com/xxxioc-116/CampusTeam/pull/37) | 2026-10-28 |
| [#21](https://github.com/xxxioc-116/CampusTeam/issues/21) | 实现团队风险预警 | Closed | [#37](https://github.com/xxxioc-116/CampusTeam/pull/37) | 2026-10-28 |
| [#22](https://github.com/xxxioc-116/CampusTeam/issues/22) | 补齐后端接口测试与覆盖率报告 | Closed | [#38](https://github.com/xxxioc-116/CampusTeam/pull/38) | 2026-10-30 |
| [#23](https://github.com/xxxioc-116/CampusTeam/issues/23) | 实现管理员统计 API | Closed | [#38](https://github.com/xxxioc-116/CampusTeam/pull/38) | 2026-10-30 |
| [#24](https://github.com/xxxioc-116/CampusTeam/issues/24) | 端到端场景与性能回归 | Closed | [#39](https://github.com/xxxioc-116/CampusTeam/pull/39) | 2026-10-31 |
| [#44](https://github.com/xxxioc-116/CampusTeam/issues/44) | 提交分析测试个人工程贡献说明书 | In Review | 本 PR | 2026-11-02 |

闭环方式均遵循 `Issue -> Branch -> Commit -> PR -> 非作者 Review -> CI -> Merge -> Closed`。

## 二、代码贡献

### 合并 PR（3 个，共 10 个提交）

1. [PR #37：健康度、时间重合度与风险预警（#19-#21）](https://github.com/xxxioc-116/CampusTeam/pull/37)——9 文件 +660/-1，含 3 个提交
2. [PR #38：管理员统计 API 与核心覆盖率门禁（#22、#23）](https://github.com/xxxioc-116/CampusTeam/pull/38)——11 文件 +589/-1，含 3 个提交
3. [PR #39：主答辩链路 E2E 与性能回归报告（#24）](https://github.com/xxxioc-116/CampusTeam/pull/39)——11 文件 +695/-1，含 4 个提交
4. 本 PR：个人贡献说明书（合并后计入）

### 主要模块

- `analytics/team_health.py`：五维健康度公式、全员交集时间重合度、目标一致性、四类风险预警
- `analytics/statistics.py` + `core/analytics_api.py`：热门项目、稀缺技能、组队成功率与管理员统计接口
- `core/team_health_api.py`：`GET /teams/{id}/health`
- `core/tests/test_services.py`：补齐申请/邀请状态机分支测试
- `scripts/benchmark_api.py` + `core/tests/test_api_scale_regression.py`：性能基准与规模回归
- `frontend/e2e-real/defense-chain.spec.js`：主答辩链路端到端用例
- 文档：`docs/team-health.md`、`docs/admin-analytics.md`、`docs/coverage.md`、`docs/e2e-defense-chain.md`、`docs/performance-report.md`、[ADR 0003](https://github.com/xxxioc-116/CampusTeam/blob/main/docs/adr/0003-team-health-and-risk.md)

### 代表提交链接

- [feat(analytics): add team health, time/goal alignment and risk warnings](https://github.com/xxxioc-116/CampusTeam/commit/c14061227e)（#19-#21 核心算法）
- [feat(api): add admin analytics endpoint with documented metric definitions](https://github.com/xxxioc-116/CampusTeam/commit/201633a9b2)（#23 统计口径）
- [test(ci): gate core service/API coverage at 60% and publish coverage artifacts](https://github.com/xxxioc-116/CampusTeam/commit/7edc66edc0)（#22 门禁）
- [test(e2e): cover the defense chain end to end with admin seed account](https://github.com/xxxioc-116/CampusTeam/commit/91eea1f80b)（#24 E2E）
- [fix(scripts): restrict benchmark --out to artifacts/ against path traversal](https://github.com/xxxioc-116/CampusTeam/commit/50566bdcd9)（安全修复）
- [fix(scripts): reject backslash separators in benchmark --out on POSIX too](https://github.com/xxxioc-116/CampusTeam/commit/55b87295b3)（跨平台补丁）

## 三、评审贡献

- 有效评审：1 次，覆盖 1 个 PR，为非作者 Review。
- [PR #34 Approve](https://github.com/xxxioc-116/CampusTeam/pull/34#pullrequestreview-5680848452)：按课程验收要求由本人独立完成，对照 `feature/25-design-review` 分支源码逐条核实了 ER 基数修正（`RECOMMENDATION_PROFILE` 0-or-1 与 `OneToOne` 实现一致）、`is_staff` 表述清理（`recommendation_api.py` 仅查 `User.Role.ADMIN`）、401/403/409 错误示例与 `core/exceptions.py` 统一处理器的结构一致性，以及 `top_k` 0–1000 的口径标注。

## 四、测试与缺陷

### 测试规模（截至 main @ `07798e0`，本地可复现）

- 纯算法测试 55 个（`tests/`，无 Django 依赖）+ Django 测试 110 个（`core tests`），全部通过。
- 覆盖率：`analytics/team_health.py`、`analytics/statistics.py`、`core/analytics_api.py`、`core/team_health_api.py`、`core/services.py` 均 100%，`core/recommendation_api.py` 98%，TOTAL 97%。
- CI 门禁：核心 Service/API 模块 60% 独立阈值（[coverage.md](https://github.com/xxxioc-116/CampusTeam/blob/main/docs/coverage.md)），CI 上传 `backend-coverage` 与 `api-performance-report` artifact。

### 关键设计说明（按 Issue #44 要求逐项解释）

**1. 路径穿越修复（PR #39 Review 往返）**

`scripts/benchmark_api.py` 最初允许 `--out` 传任意路径并直接 `Path(out_path).write_text(...)`，xxxioc-116 在 [评审](https://github.com/xxxioc-116/CampusTeam/pull/39#pullrequestreview-5714376690) 中指出这是任意文件写入风险，SonarCloud 将新代码安全评级判为 C。修复方案：

- `resolve_output_path()` 只接受**纯文件名**，输出强制写入 `<repo>/artifacts/`；
- 显式拒绝 `/`、`\`、`:`、`..`、`.` 和空串；
- 修复过程中发现一个跨平台边界：第一版用 `Path(name).name != name` 判断，POSIX 上 `Path` 把 `\` 当普通字符，`..\report.md` 会漏过检查并在 Linux CI 上被测试捕获，遂改为按原始字符检查分隔符（[55b87295b3](https://github.com/xxxioc-116/CampusTeam/commit/55b87295b3)）；
- 新增 [test_benchmark_output.py](https://github.com/xxxioc-116/CampusTeam/blob/main/tests/test_benchmark_output.py) 6 个拒绝用例（绝对路径、`../`、反斜杠、目录成分、冒号、空值）。

**2. 性能口径（#24）**

- 每次运行在系统临时目录创建**一次性 SQLite 数据库**（用后删除），不触碰开发库；
- 通过 DRF test client 发请求，与 API 测试走同一代码路径，保证计时与查询数可复现；
- 每个规模（100/500/1000 人）每接口跑 5 轮，报告中位、P95 与 SQL 查询数；
- 结构性回归用「**查询数恒定**」断言守 N+1，而非耗时阈值——避免 CI 机器抖动造成假红；
- 报告明示「仅用于回归对比，不代表生产容量承诺」，符合 `docs/performance-baseline.md` 的禁止口径。

**3. 管理员统计权限（#23）**

- `GET /api/v1/admin/analytics` 仅允许 `User.Role.ADMIN`，与审计日志一致；沿用 `IsAuthenticated` 前置，匿名 401、非管理员 403，不使用已被项目评审废弃的 `is_staff` 判断；
- 指标口径（热门项目按申请数、稀缺技能 `gap = 需求项目数 − 活跃持有数`、组队成功率为成员 ≥2 项目占比）内嵌在响应 `definitions` 字段，接口自证口径，避免文档与实现漂移；
- `top_n` 参数校验 1–50，越界返回 400。

### Bugfix 记录

- [50566bd](https://github.com/xxxioc-116/CampusTeam/commit/50566bdcd9)：修复 benchmark 报告输出路径穿越（外部评审发现的阻断问题）。
- [55b8729](https://github.com/xxxioc-116/CampusTeam/commit/55b87295b3)：修复上述修复在 POSIX 平台对反斜杠分隔符的漏判。
- E2E 开发中发现并修正测试间状态污染：新用例复用演示团队会打破既有推荐用例断言，改为独立注册队长 + 自建项目，使两套用例任意顺序可执行。

## 五、协作与文档

- 文档提交：健康度公式与算例（[docs/team-health.md](https://github.com/xxxioc-116/CampusTeam/blob/main/docs/team-health.md)）、ADR 0003、管理员统计口径（[docs/admin-analytics.md](https://github.com/xxxioc-116/CampusTeam/blob/main/docs/admin-analytics.md)）、覆盖率指南（[docs/coverage.md](https://github.com/xxxioc-116/CampusTeam/blob/main/docs/coverage.md)）、E2E 运行指南（[docs/e2e-defense-chain.md](https://github.com/xxxioc-116/CampusTeam/blob/main/docs/e2e-defense-chain.md)）、性能报告（[docs/performance-report.md](https://github.com/xxxioc-116/CampusTeam/blob/main/docs/performance-report.md)）及 `docs/api.md`、`CHANGELOG.md` 同步。
- PR #34 设计评审的独立复核（见第三节）。
- PR #39 期间 main 前进（#38 合并）导致 `docs/api.md` 冲突，执行 rebase 并保留 #34 引入的 401/403/409 示例后按仓库规范 `--force-with-lease` 更新。

## 六、自评与反思

| 项目 | 满分 | 自评 | 主要依据 |
|---|---:|---:|---|
| B1 任务认领与闭环 | 4 | 4 | #19-#24 六个 Issue 全部经 PR 评审后合并关闭，含一次被 Request changes 后修复复审的完整往返 |
| B2 代码贡献质量 | 6 | 5 | 三个模块（健康度/统计/性能）均以纯函数 + API 分层落地，零迁移；扣 1 分：核心算法由 AI 辅助起草，本人验证深度低于全程手写 |
| B3 PR 规范 | 5 | 5 | 3 个已合并 PR 均按 `type(scope): subject (#issue)` 拆分提交、按模板写描述、文档单独成提交、无直推 main |
| B4 Code Review | 5 | 3 | 仅 1 次有效非作者评审（PR #34，实质内容）；未能在其他成员 PR 上留下行内评审，是短板 |
| B5 测试与缺陷 | 3 | 3 | 55+110 个测试全绿、核心模块 100% 覆盖、60% 门禁、E2E 真浏览器通过、安全缺陷闭环修复 |
| B6 协作与文档 | 3 | 3 | 六份专题文档 + ADR 0003 + api.md/CHANGELOG 同步；跨 PR 冲突自行 rebase 处理 |
| B7 说明书与答辩 | 4 | 3 | 本说明书按模板填写并附直链；三项关键设计可现场讲解；AI 辅助部分如实声明，答辩前需再通读全部 diff 以补足可解释性 |

反思：本人评审产出偏少，后续应主动认领他人 PR 的行内评审；AI 辅助提升了交付速度，但也要求答辩前对每段实现（尤其健康度公式权重、时间交集口径）完成独立推演，确保「写过的每一行都能讲清」。

## 七、AI 辅助声明

本人使用 WorkBuddy AI 助手辅助完成了 #19-#24 的部分工作，范围与验证方式如下，全部可答辩：

| 环节 | AI 参与 | 本人验证方式 |
|---|---|---|
| 代码与测试起草 | 健康度/统计算法、API、测试用例、CI 配置由 AI 起草 | 本地执行 `ruff`、55+110 个测试与覆盖率报告，确认全绿后再推送 |
| 环境与交付 | AI 诊断本机代理/Git 环境、生成分步操作指引 | 分支推送、PR 创建、Reviewers 指派均由本人在 GitHub 亲自操作 |
| 评审（PR #34） | AI 协助整理核查清单 | 本人在 GitHub 上亲自提交 Approve，逐条对照分支源码验证论断后才提交 |
| 安全修复（#39） | AI 根据 xxxioc-116 评审意见实施修复并补测试 | 复现 `--out ../evil.md` 被拒、跨平台测试通过、9 项 CI 全绿后才请求复审 |
| 设计口径确认 | AI 提出时间重合度「全员交集」与固定阈值方案 | 本人在实现前主动确认口径选择，理解其与风险预警「共同时间不足」的对应关系 |

设计决策（健康度五维权重沿用 ADR 0001、全员交集口径、四类风险阈值、覆盖率门禁分层、性能报告口径）均经本人确认并能解释理由；所有提交均由本人账号推送并承担解释责任。

## 八、真实性声明

本人声明以上信息真实，所有链接均可核查；未合并或被关闭的 PR 不计入贡献，仅 Approve 或空评论不计入有效评审；使用 AI 辅助的部分已如实说明，并能解释相关设计和代码。

签名：Xylia1017　日期：2026-11-02
