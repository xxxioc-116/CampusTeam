# CampusTeam 贡献指南

## 唯一工作流

1. 先创建或认领包含验收标准的 Issue。
2. 从最新 `main` 创建短生命周期分支。
3. 以一个逻辑变更一个提交的粒度开发并测试。
4. 推送分支并创建 PR，正文必须包含 `Closes #<issue号>`。
5. 请求至少一名非作者成员 Review；CI 全绿、对话全部解决后方可合并。
6. 合并后删除分支，由 PR 自动关闭 Issue。

## 分支命名

- `feature/<issue号>-<英文短横线简述>`
- `bugfix/<issue号>-<英文短横线简述>`
- `hotfix/<issue号>-<英文短横线简述>`
- `chore/<英文短横线简述>`

示例：`feature/12-profile-api`、`bugfix/31-score-boundary`。

## Commit Message

格式：`<type>(<scope>): <subject>`

允许的类型：`feat`、`fix`、`docs`、`test`、`refactor`、`perf`、`style`、`chore`。

- subject 使用英文祈使句，首字母小写，结尾不加句号。
- 标题不超过 72 个字符。
- 一个提交只完成一个逻辑变更。
- 正文解释为什么这样改，不重复代码已经表达的内容。

示例：`feat(match): add explainable complement score`。

## PR 合并门禁

- 必须关联并关闭 Issue。
- 必须有至少一名非作者 Approve。
- 至少有一条实质性评审意见；指出位置、原因与可执行建议。
- CI 的 lint、test、build、governance 全部通过。
- 所有 Review 对话已解决。
- 新提交会使旧批准失效，需要重新审查。
- UI 变更附截图或 GIF；API 变更同步更新文档。
- 建议少于 400 行；超过 800 行必须说明并优先拆分。

## 评审轮值

采用交叉评审，避免固定两人互相盖章：A 评 B、B 评 C、C 评 D、D 评 A；第二轮反向轮换。每人至少在 3 个不同 PR 中留下 10 条高质量行内评论，并在 48 小时内响应。

## 测试要求

- 每项功能至少覆盖正常、边界、异常三类路径。
- 核心 Service/API 覆盖率不低于 40%，团队目标为 60%。
- 每名成员至少提交 5 个有效测试用例，并参与至少一个缺陷闭环。
- 禁止空断言、只验证 HTTP 200、不检查业务结果的测试。

## AI 辅助声明

允许使用 AI 辅助，但作者必须理解、测试并改造结果。大量使用 AI 的模块需在 PR 的“AI 辅助说明”中如实记录，答辩时能解释相关设计与代码。
