# CampusTeam 满分协作执行方案

## 满分控制线

课程最低线不是满分线。本项目按以下目标执行：

| 个人证据 | 课程下限 | CampusTeam 目标 |
|---|---:|---:|
| 已关闭且由本人认领的 Issue | 4 | ≥6，全部由 PR 自动关闭 |
| 有效合并 Commit | 8 | 12-20，均匀分布，拒绝刷量 |
| 合并 PR | 4 | 6，描述完整率 100% |
| 有效 Review | 6 条 / 3 个 PR | ≥10 条 / ≥4 个 PR，48 小时内响应 |
| 测试或缺陷 | 5 用例或 2 个 bugfix PR | ≥8 用例且 ≥1 个 bugfix/CI 贡献 |
| 文档或讨论 | 3 次 docs 或 5 条讨论 | ≥3 次 docs 且 ≥5 条实质讨论 |

## 小组 70 分执行门禁

| 项 | 满分做法 | 仓库证据 |
|---|---|---|
| A1 需求与规划 8 | 28 个预规划 Issue，全部具备 AC、负责人、标签、里程碑、依赖 | Issues、Projects、Milestones |
| A2 设计与架构 6 | 架构图、ER 图、API、ADR；关键变更继续补 ADR | `docs/architecture.md`、`docs/api.md`、`docs/adr/` |
| A3 功能质量 16 | P0 100%、P1 ≥70%、一键启动、边界与权限处理、无密钥 | README、Release、测试记录 |
| A4 工程规范 10 | main 保护、PR 门禁、合规分支和提交、禁 force push/delete | Ruleset/Branches 截图、Git 历史 |
| A5 PR 与评审 12 | 全部 main 变更经 PR；真实 Request changes 往返 | PR 时间线、Review、Checks |
| A6 测试与 CI 10 | lint + test + build + coverage；门禁状态检查 | Actions、覆盖率报告 |
| A7 文档治理 4 | README、LICENSE、CONTRIBUTING、CHANGELOG、模板齐全 | 仓库文件 |
| A8 发布答辩 4 | v0.1.0、v0.2.0、v1.0.0；Notes 与演示链路齐全 | Releases、Tags、答辩材料 |

## 四人分工与交叉要求

- A：后端与治理主责，但不得代建其他成员 PR；至少评审 B 与 D 的核心 PR。
- B：前端主责，同时承担 API Mock、组件测试和一份前端 ADR。
- C：推荐算法主责，同时提供接口适配、算法测试、基线实验与解释文档。
- D：团队分析/QA 主责，同时完成可运行的核心模块，不得只写测试或文档。
- 所有人：每个迭代至少 2 个 Issue、2 个 PR、一次 Review 轮值、一次文档或会议贡献。

## 迭代与发布

### v0.1.0 Alpha

完成项目骨架、数据模型、登录/权限、画像基础、前端壳、推荐基线接口、CI 与至少 2 次会议记录。

### v0.2.0 Beta

完成 P0 业务闭环、能力矩阵、缺口识别、Top-K 推荐与解释、覆盖率报告和对比实验初版。

### v1.0.0

完成 P0 100%、P1 ≥70%，交付健康度/风险或数据看板，补齐三版本 CHANGELOG、个人贡献说明书与答辩证据链。

## GitHub 配置清单

- 仓库建议为课程组织内的私有仓库；若课程明确要求公开，再调整可见性。
- 默认分支改为 `main`，启用自动删除 head branch。
- 创建标签：`feature`、`bug`、`docs`、`test`、`backend`、`frontend`、`algorithm`、`analytics`、`P0`、`P1`、`P2`、`P3`、`blocked`。
- 创建 Milestone：`v0.1.0 Alpha`、`v0.2.0 Beta`、`v1.0.0`。
- main 规则：必须 PR、批准数 ≥1、新提交取消旧批准、状态检查通过、对话解决、禁止 force push、禁止删除。
- Required checks：先选择 `repository-governance`；应用骨架建立后再加入 backend test、frontend test/build、coverage。

## 真实性与学术诚信

不代替成员创建提交、PR、Review 或贡献说明书；不补录、不刷量、不伪造往返。自动化只建立真实工作所需的规范与任务，成员必须使用自己的实名 GitHub 账号完成实现、评审和答辩。
