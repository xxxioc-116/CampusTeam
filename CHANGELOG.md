# Changelog

## Unreleased — Recommendation

- Remove Django staff bypasses from recommendation team reads and requirement writes; enforce business ADMIN, leadership and membership rules with four regression tests (#18).

- Lock CI dependencies with wheel SHA-256 verification, disable npm install scripts, and run installed Playwright directly (SonarCloud supply-chain findings).

- Persist validated team scoring weights with stable configuration identifiers and contribution-consistent explanations (#15, #16, #18).
- Test fixed-seed experiment reproducibility and real-Token API ranking at 100/500/1000 candidates (#17, #18).
- Extend quality-gate lint to all backend Python modules; remove unused imports and an unused test assignment (#26).

- Persist recommendation profiles and team requirements; expose authenticated matrix, gap and recommendation APIs (#18).
- Verify application/invitation approval recomputes capabilities; adapt frontend full-profile persistence (#27).
- Add real browser integration, bounded-query performance checks and aggregate CI gate (#26).

- Add validated five-dimensional normalization, maximum team aggregation and actual-gap complement scoring (#13, #14).
- Add configurable five-factor stable Top-K and score-consistent explanations (#15, #16).
- Add reproducible random/similar/complement experiments and recommendation CI (#17, #26).

本项目遵循 Semantic Versioning 与 Keep a Changelog。

## Unreleased

### Added

- Vue 3 frontend, UI tests and frontend CI from PR #30 (yuuuu1693); retained as dependency attribution.

- 建立项目治理、评分对照、Issue/PR 模板、CI 治理检查和文档骨架。
- 建立 Django 5.1 与 Django REST Framework 后端骨架、环境变量配置和健康检查。
- 增加注册、登录、个人资料、学生/队长/管理员角色权限。
- 增加项目、技能、团队、申请、邀请和审计日志数据模型及初始迁移。
- 增加项目关键词检索、类型/状态筛选、安全分页和对象级权限。
- 增加申请与邀请的同意、拒绝、撤回及防重复业务闭环。
- 增加可重复执行的演示数据命令和后端自动化测试，当前覆盖率 94%。

## 0.1.0 - Planned

### Added

- 需求与架构基线。
- 用户认证、能力画像、项目与团队数据模型骨架。
- 前后端项目骨架和基础 CI。

### Known limitations

- Alpha 版本不包含完整推荐闭环与管理员数据看板。
