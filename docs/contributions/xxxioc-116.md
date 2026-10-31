# 个人工程贡献说明书 - xxxioc-116

- 学号：待本人确认后填写
- GitHub：[@xxxioc-116](https://github.com/xxxioc-116)
- 小组：CampusTeam
- 承担角色：Maintainer / Backend Developer / Release Manager / Reviewer
- 统计截止：2026-10-31

## 一、任务完成情况

| Issue | 标题 | 状态 | 主要 PR | 完成时间 |
|---|---|---|---|---|
| [#1](https://github.com/xxxioc-116/CampusTeam/issues/1) | 建立 Django DRF 项目骨架与环境配置 | Closed | [#29](https://github.com/xxxioc-116/CampusTeam/pull/29) | 2026-10-27 |
| [#2](https://github.com/xxxioc-116/CampusTeam/issues/2) | 实现用户注册登录与角色权限 | Closed | [#29](https://github.com/xxxioc-116/CampusTeam/pull/29) | 2026-10-27 |
| [#3](https://github.com/xxxioc-116/CampusTeam/issues/3) | 建立项目与技能核心数据模型 | Closed | [#29](https://github.com/xxxioc-116/CampusTeam/pull/29) | 2026-10-27 |
| [#4](https://github.com/xxxioc-116/CampusTeam/issues/4) | 实现项目发布检索 REST API | Closed | [#29](https://github.com/xxxioc-116/CampusTeam/pull/29) | 2026-10-27 |
| [#5](https://github.com/xxxioc-116/CampusTeam/issues/5) | 实现团队申请邀请业务闭环 | Closed | [#29](https://github.com/xxxioc-116/CampusTeam/pull/29) | 2026-10-27 |
| [#6](https://github.com/xxxioc-116/CampusTeam/issues/6) | 完成审计日志与 API 性能优化 | Closed | [#29](https://github.com/xxxioc-116/CampusTeam/pull/29) | 2026-10-27 |
| [#25](https://github.com/xxxioc-116/CampusTeam/issues/25) | 完成需求、架构、ER 与 API 设计评审 | Closed | [#34](https://github.com/xxxioc-116/CampusTeam/pull/34) | 2026-10-28 |
| [#28](https://github.com/xxxioc-116/CampusTeam/issues/28) | 完成发布演示数据与答辩证据链 | Closed | [#40](https://github.com/xxxioc-116/CampusTeam/pull/40) | 2026-10-31 |
| [#41](https://github.com/xxxioc-116/CampusTeam/issues/41) | 提交组长个人工程贡献说明书与发布复盘 | In Review | 本 PR | 2026-10-31 |

闭环方式均遵循 `Issue -> Branch -> Commit -> PR -> 非作者 Review -> CI -> Merge -> Closed`。未将关闭但未合并的 [PR #35](https://github.com/xxxioc-116/CampusTeam/pull/35) 计入合并 PR。

## 二、代码贡献

### 合并 PR

1. [PR #29：后端核心任务](https://github.com/xxxioc-116/CampusTeam/pull/29)
2. [PR #34：需求、架构与 API 设计评审](https://github.com/xxxioc-116/CampusTeam/pull/34)
3. [PR #40：v1.0.0 发布与答辩证据](https://github.com/xxxioc-116/CampusTeam/pull/40)
4. 本 PR：个人贡献说明书与发布复盘（合并后计入）

### 主要模块与代表提交

- 仓库治理与工作流：[chore(repo): establish project governance baseline](https://github.com/xxxioc-116/CampusTeam/commit/d5742890e7d936ca14ca497c93d1301ec5c43532)
- 后端业务闭环：[feat(backend): deliver owner workstream for issues 1-6](https://github.com/xxxioc-116/CampusTeam/commit/2ec59442e4285ddd1cfd3fa40154dfec128c6f79)
- 权限回归修复：[fix(auth): align invitation admin role check](https://github.com/xxxioc-116/CampusTeam/commit/f1f4058309498359b3794c4e322f74387df6a255)
- 设计评审初稿：[docs(design): draft requirements architecture and API review](https://github.com/xxxioc-116/CampusTeam/commit/4fc29b50dc62180f8cdc17e5a8981bfae8210b1f)
- 设计门禁复核：[docs(design): finalize gate and main status review](https://github.com/xxxioc-116/CampusTeam/commit/f930a272c77be04ad05dbd1ed783b9629f8cadd7)
- 发布与答辩证据：[docs(release): complete defense evidence and release notes](https://github.com/xxxioc-116/CampusTeam/commit/a4e43f6711b888b530874dc2844d5f47a27f8193)

本人实现或维护的核心范围包括 Django/DRF 工程骨架、自定义用户与角色权限、项目/技能/团队数据模型、项目 REST API、申请邀请状态机、审计日志、仓库治理、架构/API 设计评审和三版本发布。

## 三、评审贡献

本人对他人 PR 的评审覆盖正确性、权限、安全、测试、CI、贡献归属和文档一致性，不将仅 Approve 或空评论计为有效评审。代表记录如下：

| PR | 评审结论与技术内容 | 证据 |
|---|---|---|
| #30 | 阻断 Sonar 安全评级、错误 CI 触发分支和存在 XSS 漏洞的依赖；修复后复审 | [Request changes](https://github.com/xxxioc-116/CampusTeam/pull/30#pullrequestreview-5677521045) / [Approve](https://github.com/xxxioc-116/CampusTeam/pull/30#pullrequestreview-5677794113) |
| #31 | 核对五维归一化、稳定 Top-K、解释一致性和固定种子实验 | [Approve](https://github.com/xxxioc-116/CampusTeam/pull/31#pullrequestreview-5669491618) |
| #32 | 阻断两处 `is_staff` 权限旁路并要求四项回归测试；修复后复审 | [Request changes](https://github.com/xxxioc-116/CampusTeam/pull/32#pullrequestreview-5677242877) / [Approve](https://github.com/xxxioc-116/CampusTeam/pull/32#pullrequestreview-5677385399) |
| #33 | 阻止联调 PR 代合他人前端代码，要求同步 main、缩小差异并保持贡献归属 | [Request changes](https://github.com/xxxioc-116/CampusTeam/pull/33#pullrequestreview-5677745822) / [Approve](https://github.com/xxxioc-116/CampusTeam/pull/33#pullrequestreview-5677924207) |
| #36 | 核对画像取消恢复、保存后基线和回归测试 | [Approve](https://github.com/xxxioc-116/CampusTeam/pull/36#pullrequestreview-5678816225) |
| #37 | 核对健康度五维公式、四类风险、权限矩阵和23项算法测试 | [Approve](https://github.com/xxxioc-116/CampusTeam/pull/37#pullrequestreview-5684624022) |
| #38 | 核对管理员权限、统计口径、边界校验和覆盖率门禁 | [Approve](https://github.com/xxxioc-116/CampusTeam/pull/38#pullrequestreview-5714327667) |
| #39 | 发现 benchmark 任意路径写入问题，要求限制输出目录并补安全测试；修复后复审 | [Request changes](https://github.com/xxxioc-116/CampusTeam/pull/39#pullrequestreview-5714376690) / [Approve](https://github.com/xxxioc-116/CampusTeam/pull/39#pullrequestreview-5721724710) |

## 四、测试与缺陷贡献

- 后端主链路测试覆盖认证、项目、团队、申请、邀请、审计、权限和重复状态迁移。
- 修复业务管理员因 `is_staff` 判断无法邀请成员的问题，并补角色回归测试，证据见 [PR #29 Review 往返](https://github.com/xxxioc-116/CampusTeam/pull/29)。
- 在评审中发现并推动修复前端依赖安全、推荐权限旁路、CI 分支错误和 benchmark 路径穿越问题。
- 建立并维护 Required Review、Required Checks、禁止直推和禁止强推的 main 门禁；最终发布的后端、前端、集成、推荐、治理和 SonarCloud 检查均通过。

## 五、协作与文档贡献

- 维护 Issue、Labels、Milestones、Projects、分支保护和三版本 Release。
- 参与或撰写 README、CONTRIBUTING、CHANGELOG、架构、API、ADR、演示脚本、发布说明和答辩证据索引。
- 将口头分工落到 Issue、Assignee、PR、Review 和 Milestone，保留可核查过程证据。
- 对大型或混合 PR 主动要求拆清贡献边界，避免一人代劳或他人工作被错误归属。

## 六、自评与反思

| 项目 | 满分 | 自评 | 主要依据 |
|---|---:|---:|---|
| B1 任务认领与闭环 | 4 | 4 | 8个已关闭Issue，均有PR或发布证据 |
| B2 代码贡献质量 | 6 | 5 | 承担后端核心与权限；早期提交粒度偏大，未自评满分 |
| B3 PR 规范 | 5 | 4 | 4个合并PR目标达成；PR #35关闭未合并，不计贡献 |
| B4 Code Review | 5 | 5 | 覆盖8个他人PR，多次形成阻断、修复、复审往返 |
| B5 测试与缺陷 | 3 | 3 | 后端测试、权限修复、CI与安全缺陷审查 |
| B6 协作与文档 | 3 | 3 | 仓库治理、设计、发布和里程碑维护 |
| B7 说明书与答辩 | 4 | 4 | 本说明书附完整链接；答辩分仍以现场表现为准 |
| **合计** | **30** | **28** | 不含教师可能评定的组长附加分 |

### 不足与改进

- 早期将 #1-#6 合并在一个后端 PR 中，虽然功能相关，但不利于人均 PR 指标和逐任务验收；后续改为独立 Issue、分支和Review门禁。
- 初期过度依赖组长集中审核，组员有效 Review 分布不足；v1.0.1 阶段采用交叉评审矩阵补足真实评审能力。
- 发布工作较晚才形成自动校验；后续项目应在 Alpha 阶段就把 Release Notes、证据索引和贡献说明纳入 CI。

### 收获

通过本项目掌握了从需求拆分、架构决策、分支保护、CI门禁、实质Code Review到语义化发布的完整工程链路，并认识到“可追溯过程”与最终功能同等重要。

## 七、AI 使用与真实性声明

本项目使用 AI 辅助生成初稿、检查代码差异、整理测试与文档。所有进入仓库的内容均经过本人核对，并通过自动化测试、CI、非作者Review或人工复审；本人能够解释所认领的后端、治理、评审和发布内容。未将其他成员的代码成果认领为本人独立贡献。

本人声明以上信息真实，所有链接均可核查。如有不实，愿接受课程考核方案处理。

签名：________　日期：2026-10-31
