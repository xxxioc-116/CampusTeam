# 主答辩链路端到端自动化（#24）

## 覆盖链路

`frontend/e2e-real/defense-chain.spec.js`（真实后端 + 真实 Token + 真实浏览器，非 Mock）：

| 步骤 | 断言点 | 方式 |
|---|---|---|
| 01 注册 | 新账号注册后进入 `/projects` | UI |
| 02-1 登录 | 进入 `/projects` | UI |
| 02-2 项目检索 | 关键词筛选命中演示项目 | UI |
| 02-3 画像保存 | 提示"画像已保存"，刷新后保持 | UI + 真实持久化 |
| 02-4 团队矩阵/缺口 | 矩阵渲染、缺口 60 可见 | UI |
| 02-5 互补推荐 | 推荐列表首位为 `rec_candidate` | UI |
| 02-6 邀请 | POST `/teams/{id}/invitations` 返回邀请对象 | UI 触发 + 响应断言 |
| 02-7 接受邀请 | 候选人 Token 调用 transition 成功 | API（UI 暂无邀请收件箱） |
| 02-8 能力重算 | 候选人出现在成员列表 | UI |
| 02-9 健康度 | `status` 属于 healthy/watch/at_risk，五维分项齐全 | API |
| 02-10 重复邀请 | 已为成员时返回 409 | API |
| 02-11 写后读 | 新建项目可被检索到 | UI |
| 03 管理员统计 | 项目数 >0、稀缺技能为数组、组队率分母一致 | API |

链路用**独立注册的队长 + 自建项目**运行，不触碰 #27 用例共享的演示团队
（`team_id=1`），两条用例可任意顺序执行。

## 运行方式

```powershell
# 仓库根目录；需要已安装 Python 与前端依赖
powershell -File scripts/test-real.ps1
```

脚本会创建临时数据库、迁移、写入演示数据（`rec_leader` / `rec_candidate` / `rec_admin`），
启动 Django 与 Vite，跑完自动清理临时数据库。

CI 中由 `Quality → integration` job 执行（同样的 Playwright real 配置）。

## 与其它测试的分工

| 层次 | 位置 | 关注点 |
|---|---|---|
| 纯算法 | `tests/` | 评分、健康度、统计公式，无数据库 |
| API/服务 | `core/tests/` | 权限矩阵、错误码、状态机、规模回归 |
| 端到端 | `frontend/e2e-real/` | 真实浏览器 + 真实 Token 的答辩链路 |

## 已知边界

- 接受邀请、健康度、管理员统计目前通过 API 断言：前端尚无邀请收件箱、
  健康度面板与统计页，UI 上线后应把这三步改为 UI 驱动。
- 演示数据仅用于本地与 CI；`CAMPUS_DEMO_PASSWORD` 由调用方注入，不入库。
