# Changelog

## Unreleased — Recommendation

- Remove Django staff bypasses from recommendation team reads and requirement writes; enforce business ADMIN, leadership and membership rules with four regression tests (#18).

- Lock CI dependencies with wheel SHA-256 verification, disable npm install scripts, and run installed Playwright directly (SonarCloud supply-chain findings).

- Persist recommendation profiles and validated team weights; expose authenticated recommendation APIs and real-Token performance tests (#18).

- Add stable weight identifiers, contribution explanations and fixed-seed reproducibility tests.

- Add validated five-dimensional normalization, maximum team aggregation and actual-gap complement scoring (#13, #14).
- Add configurable five-factor stable Top-K and score-consistent explanations (#15, #16).
- Add reproducible random/similar/complement experiments and recommendation CI (#17, #26).

本项目遵循 Semantic Versioning 与 Keep a Changelog。

## Unreleased

### Added

- Add the Vue 3 frontend for issues #7-#12, including authentication, profile editing, project discovery, team capability visualization, and explainable recommendations.
- Add frontend unit and end-to-end tests, API alignment documentation, and a dedicated lint/format/test/build CI workflow.
- Document that profile, team matrix, gap analysis, and recommendation flows still require real-backend integration before issues #9, #11, and #12 can close.

- 建立项目治理、评分对照、Issue/PR 模板、CI 治理检查和文档骨架。

## 0.1.0 - Planned

### Added

- 需求与架构基线。
- 用户认证、能力画像、项目与团队数据模型骨架。
- 前后端项目骨架和基础 CI。

### Known limitations

- Alpha 版本不包含完整推荐闭环与管理员数据看板。