# 前端与后端真实接口的差异记录

对照对象：`codex/backend-owner-tasks` 分支（`core/views.py`、`core/serializers.py`、`campusteam/settings.py`）。
原契约 `docs/frontend-api-contract.md` 是前端单方面提出、尚未被后端确认的建议稿；以下差异均已在
`frontend/src/api/adapters.js` 中处理，页面组件不需要改。

## 已适配（前端改代码解决）

| # | 项目 | 后端实际 | 前端原假设 | 处理方式 |
|---|---|---|---|---|
| 1 | 认证头 | `Authorization: Token <key>` | `Bearer <access_token>` | `client.js` 支持 `authScheme`，默认 `Token`，可用 `VITE_AUTH_SCHEME` 覆盖 |
| 2 | 登录响应字段 | `{"token": "...", "user": {...}}` | `{"access_token": "..."}` | `auth.js#setSession` 同时接受两种；适配层统一成 `access_token` |
| 3 | 注册行为 | 只创建用户，返回 201，**不发令牌** | 注册即登录 | `api/index.js` 注册成功后自动调用 `/auth/login` 换令牌 |
| 4 | 队长角色名 | `leader` | `captain` | `auth.js#canManageTeam` 同时接受 `leader`/`captain`/`admin` |
| 5 | 项目检索参数 | `keyword` / `type` / `status` | `search` / `category` / `skill` | 适配层做参数名与类型编码转换（中文类型 → `course`/`competition`/`innovation`） |
| 6 | 项目字段 | `project_type`、`max_members`、`owner`，无 `skills`/`member_count`/`team_id`/`can_view_team`/`applied` | 契约里的完整字段 | 适配层映射：`category=project_type`、`capacity=max_members`，缺失字段给安全默认值 |
| 7 | 邀请请求体 | `invitee_id` | `candidate_id` | 适配层字段改名 |
| 8 | 画像接口 | `GET/PATCH /profiles/me` 返回 **User**（id/username/display_name/role） | 返回 `{user, profile{abilities, availability...}}` | 适配层包装成 `{user, profile}` 并标记 `backend_partial`；页面顶部显示提示，PATCH 只发送 `display_name` |

## 后端尚未提供（前端已降级，不能算验收通过）

| 能力 | 缺失接口 | 影响 |
|---|---|---|
| 五维能力、技能、空闲时间 | `/profiles/me` 无对应字段与序列化器（模型有 `UserSkill`） | #9 只能保存姓名/简介，其余字段刷新后丢失 |
| 团队能力矩阵 | `GET /teams/{id}/capability-matrix` | #11 雷达图与能力表在真实模式无法取数 |
| 能力缺口 | `GET /teams/{id}/gaps` | 缺口条与说明无法取数 |
| 推荐与解释 | `GET /teams/{id}/recommendations` | #12 整页无法取数 |
| 当前用户所属团队 | 用户序列化器无 `team_id` | 顶部“我的团队”入口在真实模式隐藏 |
| 我的团队/成员列表 | 无 `GET /teams/mine`、`GET /teams/{id}/members` | 无法展示成员管理、申请审批 |

上述接口在真实模式下会返回清晰的“后端尚未实现”提示（`adaptError`，HTTP 501 语义），
不会伪装成通用网络错误。

## 建议后端在 #3、#5 后续迭代补齐

1. 用户序列化器增加 `team_id`（`TeamMember` 反查）与画像字段；
2. `/projects` 增加 `skills`、`member_count`、`can_view_team`、`applied`（聚合或注解查询）；
3. 补齐 `capability-matrix`、`gaps`、`recommendations`（#11/#12 的验收前置）；
4. 若坚持 `Bearer` 方案，需要在前端 `.env` 设 `VITE_AUTH_SCHEME=Bearer`，两边约定一处即可。

## 联调步骤

```powershell
# 后端（codex/backend-owner-tasks 分支）
python manage.py runserver          # http://127.0.0.1:8000
# 前端
# .env: VITE_USE_MOCK=false
npm run dev                         # http://127.0.0.1:5173
```

验收顺序：健康检查 → 登录 → 项目大厅列表/筛选/申请 → 画像（仅姓名）→ 团队页（预期提示接口未实现）。
