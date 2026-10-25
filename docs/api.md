# CampusTeam API 草案

统一前缀：`/api/v1`。错误响应使用 `{ "code": "...", "message": "...", "details": {} }`。

| 方法 | 路径 | 说明 | 主要权限 |
|---|---|---|---|
| POST | `/auth/register` | 注册 | 匿名 |
| POST | `/auth/login` | 登录 | 匿名 |
| GET/PATCH | `/profiles/me` | 查看或修改本人画像 | 已登录 |
| GET/POST | `/projects` | 检索或创建项目 | 已登录 |
| GET/PATCH | `/projects/{id}` | 查看或修改项目 | 成员 / 负责人 |
| POST | `/projects/{id}/applications` | 申请加入 | 已登录 |
| POST | `/teams/{id}/invitations` | 邀请候选人 | 队长 |
| GET | `/teams/{id}/capability-matrix` | 团队能力矩阵 | 团队成员 |
| GET | `/teams/{id}/gaps` | 能力缺口 | 团队成员 |
| GET | `/teams/{id}/recommendations` | Top-K 推荐与解释 | 团队成员 |
| GET | `/teams/{id}/health` | 健康度与风险 | 团队成员 |
| GET | `/admin/analytics` | 平台统计 | 管理员 |

每个端点在实现 Issue 中补充请求字段、响应字段、错误码、权限边界与示例，并以自动化 API 测试作为验收依据。
