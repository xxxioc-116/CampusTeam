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

## Alpha 已实现契约

### 认证

- `POST /auth/register`：`username`、`password`（至少 8 位）、可选 `display_name`。
- `POST /auth/login`：返回 `token` 与用户角色；后续请求使用 `Authorization: Token <token>`。
- 注册接口仅创建学生角色；队长身份在创建项目时产生，管理员身份只能由后台管理。

### 项目检索

`GET /projects` 支持 `keyword`、`type`、`status`、`page`、`page_size`。`page_size` 上限为 100；非法枚举值返回 400。创建项目后自动创建团队并把创建者设为队长。

### 申请与邀请状态机

- `POST /projects/{id}/applications` 创建申请。
- `POST /applications/{id}/transition`，请求体 `action=accept|reject|withdraw`。
- `POST /teams/{id}/invitations`，请求体含 `invitee_id`。
- `POST /invitations/{id}/transition`，请求体 `action=accept|reject|withdraw`。
- 同一项目/团队只允许一条待处理记录；已处理记录不能重复操作；接受时校验团队容量。

### 统一错误

框架错误返回：

```json
{"code":"permission_denied","message":"仅项目负责人可以修改项目","details":{"detail":"..."}}
```

业务冲突使用 409，例如 `duplicate_application`、`duplicate_invitation` 和 `already_member`。
