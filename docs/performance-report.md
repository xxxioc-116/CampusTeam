# API 性能回归报告（#24）

本报告由 `python scripts/benchmark_api.py` 自动生成，数据来自隔离的临时 SQLite 数据库；
结论仅用于回归对比，不代表生产容量承诺。

## 运行环境

| 项目 | 值 |
|---|---|
| platform | Windows 11 (AMD64) |
| cpu | Intel64 Family 6 Model 154 Stepping 4, GenuineIntel |
| cpu_count | 12 |
| python | 3.13.14 |
| sqlite | 3.53.1 |
| database | django.db.backends.sqlite3 |

## 数据规模与结果

候选人数量：100, 500, 1000；固定 1 个项目、1 个团队、1 名成员；每个规模重复 5 次，记录中位数、P95 与 SQL 查询数。

| 接口 | 100 人 中位/P95 (ms) | 查询 | 500 人 中位/P95 (ms) | 查询 | 1000 人 中位/P95 (ms) | 查询 |
|---|---:|---:|---:|---:|---:|---:|
| `GET /projects?page=1` | 7.19 / 8.78 | 4 | 7.09 / 8.49 | 4 | 4.93 / 6.99 | 4 |
| `GET /teams/{id}/capability-matrix` | 10.09 / 10.84 | 4 | 7.98 / 10.55 | 4 | 5.08 / 8.21 | 4 |
| `GET /teams/{id}/gaps` | 8.2 / 11.52 | 4 | 9.42 / 11.05 | 4 | 5.61 / 7.09 | 4 |
| `GET /teams/{id}/recommendations?top_k=5` | 70.89 / 74.66 | 6 | 207.45 / 264.0 | 6 | 359.44 / 407.26 | 6 |
| `GET /teams/{id}/health` | 10.71 / 10.92 | 4 | 10.51 / 14.74 | 4 | 5.94 / 8.23 | 4 |
| `GET /admin/analytics` | 15.68 / 18.81 | 11 | 11.01 / 13.43 | 11 | 11.48 / 15.44 | 11 |

## 结论

- `GET /projects?page=1`：SQL 查询数恒为 4，三种规模下无 N+1；耗时基本不随候选人数变化（7.19 → 4.93 ms）。
- `GET /teams/{id}/capability-matrix`：SQL 查询数恒为 4，三种规模下无 N+1；耗时基本不随候选人数变化（10.09 → 5.08 ms）。
- `GET /teams/{id}/gaps`：SQL 查询数恒为 4，三种规模下无 N+1；耗时基本不随候选人数变化（8.2 → 5.61 ms）。
- `GET /teams/{id}/recommendations?top_k=5`：SQL 查询数恒为 6，三种规模下无 N+1；耗时随候选人数近似线性增长（70.89 → 359.44 ms）。
- `GET /teams/{id}/health`：SQL 查询数恒为 4，三种规模下无 N+1；耗时基本不随候选人数变化（10.71 → 5.94 ms）。
- `GET /admin/analytics`：SQL 查询数恒为 11，三种规模下无 N+1；耗时基本不随候选人数变化（15.68 → 11.48 ms）。

## 复现方式

```powershell
python scripts/benchmark_api.py
python scripts/benchmark_api.py --out docs/performance-report.md
```

