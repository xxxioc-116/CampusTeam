# 个人工程贡献说明书 yuuuu1693

- 学号：未在仓库中公开（答辩材料中由本人补充）
- GitHub：[@yuuuu1693](https://github.com/yuuuu1693)
- 小组：CampusTeam
- 承担角色：前端开发、前后端契约联调、设计评审与代码审查

## 一 任务完成情况

| Issue | 标题 | 状态 | PR | 完成时间 |
|---|---|---|---|---|
| [#7](https://github.com/xxxioc-116/CampusTeam/issues/7) | 建立 Vue 3 前端骨架与路由权限 | 已关闭 | [#30](https://github.com/xxxioc-116/CampusTeam/pull/30) | 2026-10-28 |
| [#8](https://github.com/xxxioc-116/CampusTeam/issues/8) | 实现登录注册与统一错误态 | 已关闭 | [#30](https://github.com/xxxioc-116/CampusTeam/pull/30) | 2026-10-28 |
| [#9](https://github.com/xxxioc-116/CampusTeam/issues/9) | 实现学生能力画像编辑页面 | 已关闭 | [#30](https://github.com/xxxioc-116/CampusTeam/pull/30)、[#36](https://github.com/xxxioc-116/CampusTeam/pull/36) | 2026-10-28 |
| [#10](https://github.com/xxxioc-116/CampusTeam/issues/10) | 实现项目大厅与筛选分页 | 已关闭 | [#30](https://github.com/xxxioc-116/CampusTeam/pull/30) | 2026-10-28 |
| [#11](https://github.com/xxxioc-116/CampusTeam/issues/11) | 实现团队能力矩阵雷达图与缺口展示 | 已关闭 | [#30](https://github.com/xxxioc-116/CampusTeam/pull/30) | 2026-10-28 |
| [#12](https://github.com/xxxioc-116/CampusTeam/issues/12) | 实现推荐结果与解释页面 | 已关闭 | [#30](https://github.com/xxxioc-116/CampusTeam/pull/30) | 2026-10-28 |
| [#25](https://github.com/xxxioc-116/CampusTeam/issues/25) | 需求、架构 ER 与 API 设计评审协作 | 已关闭 | [#34](https://github.com/xxxioc-116/CampusTeam/pull/34) | 2026-10-28 |

## 二 代码贡献

- 有效合并 Commit：PR #30 中 4 个前端提交、PR #36 中 1 个画像回归提交，以及 PR #34 中 2 个设计评审整改提交。
- 合并 PR：本人独立提交并合并 [PR #30](https://github.com/xxxioc-116/CampusTeam/pull/30) 与 [PR #36](https://github.com/xxxioc-116/CampusTeam/pull/36)；并在 [PR #34](https://github.com/xxxioc-116/CampusTeam/pull/34) 协作完成第二部分评审和整改。
- 主要模块：Vue 3/Element Plus 前端骨架、Token 登录与角色路由、学生画像、项目大厅、团队能力矩阵与缺口、推荐解释、API adapter、Mock/真实后端切换和前端测试。
- 代表提交链接：
  - [完成 #7–#12 前端流程](https://github.com/xxxioc-116/CampusTeam/commit/23edd4cd842c1114fc570f991bfda22bf38e7b8b)
  - [接入真实画像与团队 API](https://github.com/xxxioc-116/CampusTeam/commit/ef8dff302a80daf66bf934a68630b9d155dbee75)
  - [修复安全审查阻塞项](https://github.com/xxxioc-116/CampusTeam/commit/d3ba77e40f037a0de0d7ab39a57013fb109306d9)
  - [画像取消恢复与回归测试](https://github.com/xxxioc-116/CampusTeam/commit/5092ce59f1407b815aa35c020465ee9431b1cd4c)
  - [完成 ER/API 设计评审第二部分](https://github.com/xxxioc-116/CampusTeam/commit/58a68d7e8ac38e55d31035c0835746a5de7ea93c)

### 关键工程说明

1. **安全依赖修复。** 将存在公开 XSS 风险的 ECharts 5.6.0 升级到 6.1.0并更新 lockfile；CI 安装改为 `npm ci --ignore-scripts`；同时把前端 CI 的 push 分支从个人分支改为 `main`。修复提交见 [d3ba77e](https://github.com/xxxioc-116/CampusTeam/commit/d3ba77e40f037a0de0d7ab39a57013fb109306d9)。
2. **画像取消回归。** 取消按钮恢复最近一次成功加载/保存的完整快照，而非只清空当前输入；保存成功后以服务端最终响应更新快照。PR #36 增加两个回归场景，防止取消恢复到过期数据。
3. **真实后端协作。** PR #30 后期不再以 Mock 页面作为完成依据；根据后端真实响应调整 `adapters.js`、Token 登录、画像回显、团队矩阵/缺口/推荐接口，并保留 `VITE_USE_MOCK` 仅作演示与隔离测试开关。

## 三 评审贡献

- 有效评审数与覆盖 PR 数：至少 3 次正式 Review，覆盖 2 个他人 PR。
  - [PR #29 首轮 Request changes](https://github.com/xxxioc-116/CampusTeam/pull/29#pullrequestreview-5665877730)：发现 `is_staff` 与业务 `User.Role.ADMIN` 权限模型不一致，并要求补回归测试。
  - [PR #29 复审 Approve](https://github.com/xxxioc-116/CampusTeam/pull/29#pullrequestreview-5669357217)：核对权限修复、非 staff 管理员测试及 CI 后批准。
  - [PR #37 实质 Approve](https://github.com/xxxioc-116/CampusTeam/pull/37#pullrequestreview-5684610130)：核对五维健康度、时间交集、目标一致性、风险阈值、权限和边界测试。
- 代表性行内评论链接：PR #34 的评审协作与整改证据集中记录在 [设计评审文件变更](https://github.com/xxxioc-116/CampusTeam/pull/34/files)；正式 Review 证据以上述 #29、#37 链接为准。

## 四 测试与缺陷

- 有效测试用例：PR #30 合并时前端 Vitest 共 62 项通过；PR #36 新增 2 个画像快照回归场景后共 64 项通过。测试覆盖登录、路由权限、API adapter、错误态、项目筛选分页、画像、团队分析和推荐交互。
- Bugfix PR：[PR #36](https://github.com/xxxioc-116/CampusTeam/pull/36) 修复画像编辑取消无法恢复服务端基线的问题，并更新 CHANGELOG。
- CI 维护记录：[安全审查整改提交](https://github.com/xxxioc-116/CampusTeam/commit/d3ba77e40f037a0de0d7ab39a57013fb109306d9) 修正 Frontend CI push 分支并采用无脚本依赖安装；PR #30/#36 合并前均通过 ESLint、Prettier、Vitest、Vite build、Governance 与 SonarCloud。

## 五 协作与文档

- 文档提交：在 PR #30 补充前端 README、接口契约、测试说明和 CHANGELOG；在 [PR #34](https://github.com/xxxioc-116/CampusTeam/pull/34) 完成现状/规划 ER 分离、serializer/view/test 字段核对、401/403/409 示例和数据库边界说明。
- Issue/Discussion 实质讨论：围绕 #7–#12 与后端 PR #29/#31–#33 对齐真实接口；明确 #9 需独立修复取消恢复，#11/#12 以真实后端响应而非 Mock 演示验收。
- 会议与看板工作：按负责人安排更新 PR 描述、关联 Issue、测试证据与 UI 截图；在后端合并后同步分支并完成非 Mock 回归。

## 六 自评与反思

| 项目 | 满分 | 自评 | 证据链接 |
|---|---:|---:|---|
| B1 任务认领与闭环 | 4 | 4 | [#7–#12 闭环](https://github.com/xxxioc-116/CampusTeam/pull/30)；[#9 独立修复](https://github.com/xxxioc-116/CampusTeam/pull/36) |
| B2 代码贡献质量 | 6 | 5 | [真实 API 适配](https://github.com/xxxioc-116/CampusTeam/commit/ef8dff302a80daf66bf934a68630b9d155dbee75)；[安全整改](https://github.com/xxxioc-116/CampusTeam/commit/d3ba77e40f037a0de0d7ab39a57013fb109306d9) |
| B3 PR 规范 | 5 | 4 | [PR #30](https://github.com/xxxioc-116/CampusTeam/pull/30)；[PR #36](https://github.com/xxxioc-116/CampusTeam/pull/36) |
| B4 Code Review | 5 | 4 | [#29 Request changes](https://github.com/xxxioc-116/CampusTeam/pull/29#pullrequestreview-5665877730)；[#37 Approve](https://github.com/xxxioc-116/CampusTeam/pull/37#pullrequestreview-5684610130) |
| B5 测试与缺陷 | 3 | 3 | [画像快照回归测试](https://github.com/xxxioc-116/CampusTeam/commit/5092ce59f1407b815aa35c020465ee9431b1cd4c) |
| B6 协作与文档 | 3 | 3 | [PR #34 第二部分](https://github.com/xxxioc-116/CampusTeam/commit/58a68d7e8ac38e55d31035c0835746a5de7ea93c) |
| B7 说明书与答辩 | 4 | 3 | 本文及其独立 PR；最终分数由非作者 Review 和答辩确认 |

反思：首个前端 PR 规模过大，导致真实后端依赖、依赖安全和 CI 配置问题集中到后期暴露。后续应按“基础框架、单一用户流、真实契约、回归修复”拆分小 PR，并在开发开始时就让 Mock 与真实响应共享同一 contract test。当前仍需继续补齐邀请收件箱等用户闭环，不能用 API 可调用代替 UI 已交付。

## 七 AI 辅助与真实性声明

AI 用于代码结构建议、测试场景枚举、文档措辞和差异检查；本人负责确认需求、选择实现方案、逐项核对改动、运行 ESLint/Prettier/Vitest/Vite build、完成真实后端回归并根据 Review 整改。答辩时本人能够说明 Token/路由权限、API adapter、画像快照、Mock/真实切换及安全依赖修复的设计和验证过程。

本人声明以上信息真实，所有链接均可核查；没有将协作者的后端、推荐算法或团队分析成果冒充为本人独立贡献。

签名：yuuuu1693　日期：2026-10-31
