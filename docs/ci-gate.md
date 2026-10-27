# CI 全链路与合并门禁（#26）

`quality.yml` 在 PR 和 main 推送时运行：

- backend：安装依赖、全部后端 Python lint、Django 检查、迁移漂移检查、测试、80% 业务覆盖率、sdist/wheel 构建。
- frontend：npm ci、ESLint、格式检查、Vitest 覆盖率、生产构建。
- integration：临时 SQLite、迁移和合成数据、非 Mock Chromium 真实接口测试。
- quality-gate：即使上游失败或跳过也执行；只有三个任务均成功才成功。

独立 `recommendation.yml` 另执行算法 90% 覆盖率门槛、包构建与固定种子实验，并上传实验 JSON。
`governance.yml` 检查必需文件、受禁生成物和 PR 标题。
前端覆盖率门槛覆盖 auth、adapters/client、domain；不代表全部 Vue 页面覆盖率。

## 管理员配置

工作流合并到 main 并至少运行一次后，由仓库管理员打开 Settings → Rules → Rulesets，
为 main 建立启用状态的分支规则：

1. 要求通过 Pull Request 合并，至少一名非作者批准。
2. 新提交使旧批准失效；要求解决全部评审对话。
3. 要求状态检查 `quality-gate`、`repository-governance`、`recommendation-checks` 成功，并要求分支与 main 保持最新。
4. 禁止强制推送和删除；不配置常规绕过主体。
5. 保存后用未通过 CI 的测试 PR 确认无法合并，再记录规则链接与验证结果。

该文档和工作流文件本身不会开启 GitHub 强制门禁。当前 GitHub 插件创建分支返回
403 Resource not accessible by integration，且插件不提供规则管理写操作。
在管理员真实配置并验证之前，#26 的“设为 main 合并门禁”验收项保持未完成。
