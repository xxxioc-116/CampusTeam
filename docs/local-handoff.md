# w44504143-png 联调交付

更新日期：2026-10-28。

#29（基础后端）、#30（前端）、#31（算法）、#32（推荐 API）均已合并。
#33 基于最新 main，只交付 #27 真实联调与 #26 CI；前端重复修复采用 #30 已审版本，保留 ECharts 6 升级。
原始前端和修复归属 yuuuu1693，基础后端归属 #29 作者；本次不代合或认领队友成果。
历史依赖组合分支不再参与合并。

## 安装与复现

先创建 .venv，再执行以下步骤：

1. Python 安装：python -m pip install --only-binary=:all: --require-hashes -r requirements-ci.txt。
2. 设置 DJANGO_DEBUG=true；执行 Django check、makemigrations --check --dry-run。
3. Ruff 检查 analytics、tests、core、campusteam、manage.py。
4. coverage run --source=analytics,core --omit='*/tests/*,*/migrations/*,*/management/*,analytics/experiment.py' manage.py test core tests；coverage report --fail-under=80。
5. python -m build --no-isolation。
6. frontend 目录执行 npm ci --ignore-scripts、npm run lint、npm run format:check、npm test -- --coverage、npm run build。
7. frontend 目录执行 node node_modules/@playwright/test/cli.js install chromium。
8. 仓库根目录执行 scripts/test-real.ps1。

真实测试创建独立 SQLite 和随机口令，使用端口 8001/5174，不使用 Mock。
脚本直接运行锁文件安装的 Playwright CLI，finally 恢复调用位置/环境变量并清理本次临时数据库及 sidecar。
浏览器发出邀请后，通过候选人真实 Token 接受，再确认页面重算；没有宣称已实现邀请收件箱。
申请审批重算另有 API 测试；验证边界见 recommendation-validation.md。

## 手动体验

可运行 scripts/start-demo.ps1，结束运行 scripts/stop-demo.ps1。
或设置 DJANGO_DEBUG=true、独立 DB_NAME 和至少 12 字符的 CAMPUS_DEMO_PASSWORD，迁移并运行 seed_recommendation_demo，
再启动 Django 与 VITE_USE_MOCK=false 的前端。不要把口令或 Token 提交到仓库。

## 待验收

#18 已关闭；#27 等待 #33 的非作者最终批准和合并。
#26 的工作流由本 PR 提供，main 强制门禁仍需管理员按 ci-gate.md 启用并验证。
当前账号无管理员权限，不能把已配置工作流等同于已启用门禁。
AI 辅助实现和测试已披露，作者仍需自行理解；未代非作者批准或合并。
