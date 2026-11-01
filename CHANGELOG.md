# Changelog

## 1.0.1 - Unreleased

### Added

- Add an authenticated invitation inbox with accept/reject actions, processed-state protection, team refresh, empty/error states and frontend/backend regression coverage (#45).

## 1.0.0 - 2026-10-31

### Added

- Add team health, risk warnings and admin analytics APIs (#19-#23).
- Add backend coverage artifacts and independent core module gates (#22).
- Add real-browser defense-chain E2E, scale regression and reproducible performance reports (#24).
- Add complete release notes, defense script, contribution links and automated release-evidence validation (#28).

### Fixed

- Restrict benchmark report output to plain file names under `artifacts/` and cover traversal attempts (#24).
- Restore profile edits from the latest server snapshot when cancellation is requested (#9).
- Align all administrator authorization checks with the business `User.Role.ADMIN` role (#18).

### Known limitations

- Health dashboard and admin analytics UI remain API-driven in the demonstration.
- The course delivery targets a single-node environment; production availability and capacity work remain out of scope.

## 0.2.0 - 2026-10-30

### Added

- Add the Vue project, profile, team, gap and recommendation flows (#7-#12).
- Add explainable weighted recommendations, experiments and authenticated APIs (#13-#18).
- Add real Token integration and CI quality aggregation (#26-#27).

## 0.1.0 - 2026-10-27

### Added

- Establish repository governance, architecture, API contracts and protected delivery workflow.
- Add authentication, projects, teams, applications, invitations, auditing and repeatable demo data (#1-#6).

## Unreleased — Recommendation

- Add the defense-chain end-to-end scenario (register, search, profile, matrix, recommendation, invite/accept, recompute, health) and an API performance regression report with environment, scale and conclusions (#24).

- Add GET /admin/analytics with popular projects, scarce skills and team formation metrics, including inline metric definitions and admin-only access (#23).
- Add per-module coverage gate (core service/API ≥60%) and downloadable coverage artifacts (coverage.xml + htmlcov) in CI, with 13 transition-branch tests raised core/services.py to 100% (#22).
- Add five-dimension team health scoring, common-time/goal alignment and four-type risk warnings via GET /teams/{id}/health, with fixed documented thresholds and no new database models (#19, #20, #21).
- Verify real profile persistence and invitation acceptance recompute team capabilities (#27).
- Add backend/frontend/integration quality gates with coverage and locked dependency installs (#26).
- Run the locked local Playwright CLI and clean only the generated temporary test database on exit.

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

- Add profile edit cancellation that restores the latest loaded or saved server snapshot, with component regression coverage (#9).

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
