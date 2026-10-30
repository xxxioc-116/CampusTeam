# 后端覆盖率报告（#22）

## 目标与口径

| 口径 | 阈值 | 说明 |
|---|---:|---|
| 全局 | 80% | `coverage report --fail-under=80`，防止整体回退 |
| 核心 Service / API | 60% | 对 `core/services.py`、`core/views.py`、`core/serializers.py`、`core/recommendation_api.py`、`core/team_health_api.py`、`core/analytics_api.py` 单独计算 |

Issue #22 的验收下限为 40%、目标 60%；本仓库两条门禁都高于验收下限，
核心模块门禁取 60%，避免某个热点模块回退被全局高分掩盖。

## 统计范围

`--source=analytics,core`，排除 `*/tests/*`、`*/migrations/*`、`*/management/*`、
`analytics/experiment.py`（离线实验脚本，不属于运行时逻辑）。

## 本地运行

```powershell
$env:DJANGO_DEBUG="true"; $env:DJANGO_SECRET_KEY="local-only"
python -m coverage run --source=analytics,core --omit='*/tests/*,*/migrations/*,*/management/*,analytics/experiment.py' manage.py test core tests
python -m coverage report            # 终端汇总
python -m coverage report --include='core/services.py,core/views.py' --fail-under=60
python -m coverage html              # 生成 htmlcov/index.html
python -m coverage xml               # 生成 coverage.xml（CI/工具消费）
```

`htmlcov/` 与 `coverage.xml` 均在 `.gitignore` 中，不入库。

## 在 CI 获取报告

`Quality` 工作流的 `backend` job 在上传覆盖率后执行：

1. `coverage report`（终端输出，含 Missing 行号）
2. `coverage report --include=... --fail-under=60`（核心模块门禁）
3. `coverage xml` + `coverage html`
4. `actions/upload-artifact` 上传 **`backend-coverage`**（保留 14 天）

获取方式：GitHub → **Actions** → 选择对应 run → 页面底部 **Artifacts** →
下载 `backend-coverage` → 解压后打开 `htmlcov/index.html`。

## 当前基线（本地 2026-10-29）

| 模块 | 覆盖率 |
|---|---:|
| `analytics/recommendation.py` | 96% |
| `analytics/team_health.py` | 100% |
| `analytics/statistics.py` | 100% |
| `core/services.py` | 100% |
| `core/views.py` | 91% 以上 |
| `core/recommendation_api.py` | 98% |
| `core/team_health_api.py` | 100% |
| `core/analytics_api.py` | 100% |
| **全局** | **95%** |

`core/services.py` 的补齐来自 `core/tests/test_services.py`：状态机 13 个分支
（重复处理、越权撤回/处理、团队满员、未知动作、接受后入队与审计日志）。

## 维护约定

- 新增 Service/API 时同步补充正常、边界与异常路径用例；仅在无法测试的分支
  （如依赖外部服务）使用 `# pragma: no cover` 并在 PR 中说明原因。
- 覆盖率下降不是唯一信号：门禁只保证下限，评审仍需检查断言是否有效。
