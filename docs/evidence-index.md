# 答辩证据索引

| 证据 | 位置 | 状态 |
|---|---|---|
| 需求规格说明书 | `docs/CampusTeam_软件需求规格说明书_初版.docx` | 已入库 |
| 架构、ER 与 ADR | `docs/architecture.md`、`docs/adr/` | 已完成 |
| API 契约 | `docs/api.md`、`docs/frontend-api-contract.md` | 已完成 |
| 自动化测试与覆盖率 | `core/tests/`、`tests/`、`docs/coverage.md` | CI 门禁通过 |
| E2E 答辩链路 | `frontend/e2e-real/defense-chain.spec.js`、`docs/e2e-defense-chain.md` | CI 通过 |
| 性能回归 | `core/tests/test_api_scale_regression.py`、`docs/performance-report.md` | 已完成 |
| 演示数据 | `python manage.py seed_recommendation_demo` | 可重复、无固定密码 |
| 演示脚本 | `docs/demo-script.md` | v1.0.0 已更新 |
| Release Notes | `docs/releases/v0.1.0.md`、`v0.2.0.md`、`v1.0.0.md` | 三版齐全 |
| GitHub Issues | https://github.com/xxxioc-116/CampusTeam/issues | 28 项可追溯 |
| Pull Requests | https://github.com/xxxioc-116/CampusTeam/pulls?q=is%3Apr | #29-#39 可追溯 |
| Actions | https://github.com/xxxioc-116/CampusTeam/actions | 构建、测试、集成和质量门禁 |
| 四人贡献索引 | `docs/contributions/README.md` | 客观链接已整理 |

## 关键闭环

| 范围 | Issue | PR | 验收结果 |
|---|---|---|---|
| 后端核心 | #1-#6 | #29 | 合并，权限修复后批准 |
| 前端主流程 | #7-#12 | #30、#36 | 合并，安全与回归检查通过 |
| 推荐算法与联调 | #13-#18、#27 | #31-#33 | 合并，算法、权限和真实联调通过 |
| 设计与治理 | #25-#26 | #34、保护规则 | 设计复审与强制门禁完成 |
| 健康度与统计 | #19-#23 | #37-#38 | 合并，覆盖率和统计接口通过 |
| E2E 与性能 | #24 | #39 | 安全修复、双人复审后合并 |
| 发布与答辩 | #28 | 本发布 PR | 三版说明、演示与证据链 |

