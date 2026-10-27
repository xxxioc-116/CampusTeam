# w44504143-png 任务交付

日期：2026-10-27。任务 #13–#18，协作任务 #26、#27。

| 交付分支 | 内容 | PR 基线 |
|---|---|---|
| feature/13-recommendation-delivery | #13–#17：向量、缺口、五项权重、解释、实验 | main |
| feature/18-recommendation-delivery | #18：持久化、Token API、权限、性能；依赖算法及 #29 | codex/backend-owner-tasks |
| feature/27-integration-delivery | #27 联调、#26 CI；依赖 API 及 #30 | feature/27-integration-dependencies |

依赖组合分支只保留已有后端、算法和前端的历史及内容，用于缩小 PR 差异；不单独合并。
待 #29、#30 和算法/API PR 合并后，将后续 PR 更新到最新 main 并重新运行 CI。
基础后端属于 #29 作者，原始前端属于 #30 作者，本次不把队友代码计作个人原创。
未代替非作者审批，也未合并或关闭 Issues。

## 复现检查

```powershell
$env:DJANGO_DEBUG='true'
.\.venv\Scripts\python -m ruff check analytics tests core campusteam manage.py
.\.venv\Scripts\python manage.py check
.\.venv\Scripts\python manage.py makemigrations --check --dry-run
.\.venv\Scripts\python -m coverage run --source=analytics,core --omit='*/tests/*,*/migrations/*,*/management/*,analytics/experiment.py' manage.py test core tests
.\.venv\Scripts\python -m coverage report --fail-under=80
.\.venv\Scripts\python -m build
.\.venv\Scripts\python -m analytics.experiment
Set-Location frontend
npm ci
npm run lint
npm run format:check
npm test -- --coverage
npm run build
npx playwright install chromium
Set-Location ..
.\scripts\test-real.ps1
```

先安装 requirements.txt、ruff==0.14.2、build==1.3.0，并在 frontend 执行 npm ci。
真实测试创建独立 SQLite 和随机口令，使用端口 8001/5174，不使用 Mock。
测试通过浏览器发邀请，以候选人真实 Token 调用接受接口，再确认页面重算；没有宣称已实现邀请收件箱。
结果和性能边界见 recommendation-validation.md。

## 手动体验与讲解

可运行 scripts/start-demo.ps1，结束运行 scripts/stop-demo.ps1。
或设置 DJANGO_DEBUG=true、独立 DB_NAME、至少 12 字符的 CAMPUS_DEMO_PASSWORD，
迁移并运行 seed_recommendation_demo，再启动 Django 与 VITE_USE_MOCK=false 的前端。
不得将口令或 Token 提交到代码、文档或聊天。

需要理解：能力归一化、逐维最大值、实际缺口增量、五项权重和为 1、稳定排序、
分项贡献与解释一致、审批后读取最新成员关系，以及合成实验不能代表真实满意度。
经历目前为类别精确匹配，未做自由文本语义推断；技能等级也未被擅自映射成能力维度。

## GitHub 权限与待验收事项

GitHub 插件可以读取仓库，但创建分支返回 403 Resource not accessible by integration。
本次使用现有 Git 凭据核验账号 w44504143-png，再通过 Git/CLI 交付；不输出或保存凭据。
远端结果以实际 PR、Actions 为准，不用本地测试替代远端运行。
#26 的 main 强制门禁仍需管理员按 ci-gate.md 配置；配置前保持该验收项未完成。
非作者批准及依赖合并仍需团队完成；AI 辅助实现和测试已如实披露，不能代用户声明已理解。
