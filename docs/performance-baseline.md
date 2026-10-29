# API 性能基线

当前 Alpha 基线以本地 SQLite 测试环境为准，不等同于生产容量结论。

| 接口 | 数据规模 | 基线要求 | 优化措施 |
|---|---:|---:|---|
| 项目列表 | 100 条 | 单页最多 100 条 | 复合索引、固定最大页长、owner `select_related` |
| 审计日志 | 1000 条 | 单页最多 100 条 | action/created_at 与 actor/created_at 索引 |
| 项目筛选 | 1000 条 | 使用类型、状态、时间索引 | 参数白名单，避免无界页长 |

性能数据必须在发布前使用目标数据库和统一硬件重新测量，记录数据量、执行次数、P50/P95 和查询数。禁止把本地单次耗时作为生产承诺。

## 回归测量（#24）

- 一键测量脚本：`python scripts/benchmark_api.py`（隔离临时 SQLite，自动删除；
  `--out docs/performance-report.md` 可生成报告）
- 最近一次测量结果、运行环境与结论见 [性能回归报告](performance-report.md)
- CI 在 `Quality → backend` job 每次运行后产出 `api-performance-report` artifact
- 结构性回归由 `core/tests/test_api_scale_regression.py` 守护：同一接口在 50 与
  200 名候选人下 SQL 查询数必须一致，出现 N+1 会确定性失败（不依赖计时）


