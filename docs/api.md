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

## 推荐模块契约（#13–#18、#27，已合并 main，验收记录见 PR #31–#33）

所有路径仍加 `/api/v1`，不带尾斜杠，使用 `Authorization: Token <token>`。

### 本人画像

`GET /profiles/me` 返回 `{user, profile}`；user 包含只读 team_id（多团队时选 id 最小的团队）。
画像尚未建立时 profile 为 null。`PATCH /profiles/me` 保存下列可编辑字段并返回服务器持久化结果：

```json
{
  "display_name":"测试同学", "bio":"希望参与数据项目",
  "abilities":[80,40,60,70,50], "skills":["Python","Vue"],
  "availability":[{"day":1,"start":"18:00","end":"20:00"}],
  "goal":"学习提升", "experience":"课程项目"
}
```

abilities 顺序固定为编程开发、数据分析、产品设计、沟通协作、项目管理；0–100 有限数字，
单维 null 按 0 计算，非法数值/布尔值/错误长度拒绝。时间必须为 ASCII HH:mm、星期 1–7、当日结束晚于开始。
skills 为字符串数组；experience 当前按完整字符串作为一个类别精确匹配，不做语义推断。
角色、team_id、id 不可由此修改。profile 字段与原 Alpha 扁平响应不同，已在本地前端适配层同步处理。

### 团队推荐需求

`PATCH /teams/{id}/recommendation-requirements`：仅本团队队长或 `User.Role.ADMIN` 可配置（`is_staff` 判断已在 #32 评审中移除，见 `core/recommendation_api.py`）。
字段包括 abilities、skills、availability、goal、experience 和可选 weights；不接受 bio/display_name。
首次未配置需求时，团队分析接口返回 400，请队长先配置；不虚构默认需求。

```json
{
  "abilities":[80,80,70,70,60], "skills":["Python"],
  "weights":{"complement":0.35,"skill":0.25,"time":0.2,"goal":0.1,"experience":0.1}
}
```

五项权重必须齐全、非负、有限且合计为 1。省略 weights 时保留现有配置，新建需求默认使用 ADR 0001 基线。
显式传空对象、数组、非法权重返回 400，事务回滚，不覆盖原配置。

### 矩阵、缺口与推荐

- `GET /teams/{id}/capability-matrix`：`{team_name, dimensions, current, required, members}`。
  current 为成员能力逐维最大值；members 包含 id、display_name、abilities，所有公共能力值为 0–100。
- `GET /teams/{id}/gaps`：`{results:[{dimension,gap,explanation}]}`，只输出正缺口；gap 消除浮点显示尾差。
- `GET /teams/{id}/recommendations?top_k=5`：top_k 为 0–1000 整数，0 返回空结果，超过候选人数返回全部。

```json
{
  "project_id":1, "weight_version":"baseline-v1", "applied":false,
  "weights":{"complement":0.35,"skill":0.25,"time":0.2,"goal":0.1,"experience":0.1},
  "results":[{
    "id":2,"display_name":"候选人","skills":["python"],"score":60,
    "scores":{"complement":100,"skill":100,"time":0,"goal":0,"experience":0},
    "contributions":{"complement":35,"skill":25,"time":0,"goal":0,"experience":0},
    "reasons":["可补齐数据分析 60.00 分","技能命中 1/1 项，贡献 25.00 分"],
    "risks":["时间信息不足"],"filled":[0,60,0,0,0],"invited":false
  }]
}
```

上述三个 GET 接口只允许本团队成员、队长或 `User.Role.ADMIN`，匿名 401，越权 403，不存在的团队 404。
候选池为已启用的 student 角色，排除本团队成员；其他团队的学生当前允许推荐。
invited 表示已有待处理邀请；邀请待处理不增加成员，接受邀请/申请后重新读取矩阵会立即重算。
applied 为兼容原页面的占位字段，不应用来表示本团队成员能再次申请本团队。
默认权重为 baseline-v1；自定义权重使用可复现摘要标识，响应同时携带完整配置。
总分按未舍入贡献之和计算、降序排列，并列按用户 id 升序。

### 团队健康度与风险预警（#19–#21）

`GET /teams/{id}/health`：本团队成员、队长或 `User.Role.ADMIN` 可读；匿名 401，
越权 403，不存在的团队 404，需求未配置 400。返回五维健康度（capability/
skill/time/goal/experience，权重与推荐模块一致）、0–100 总分、healthy/watch/
at_risk 分档与四类风险（critical_gap、capability_duplication、
common_time_insufficient、goal_inconsistency）。时间重合度取全员交集；
指标公式、固定阈值与算例见 docs/team-health.md，设计决策见 ADR 0003。

### 错误与限制

校验错误返回 400、code=validation_error；权限错误 permission_denied，认证错误 not_authenticated。
错误格式由 core.exceptions 统一生成。推荐结果请求时计算，不保存历史画像快照；响应配置标识不能替代完整历史重放。
健康度与四类风险预警已随 #19–#21 交付（见上节）；风险看板页与管理员统计仍由 #23 等任务完成。

### 错误响应示例（401 / 403 / 409）

未携带或携带失效令牌访问受保护接口 —— HTTP 401：

```json
{"code":"not_authenticated","message":"身份认证信息未提供或已失效","details":{}}
```

非本团队成员访问团队能力矩阵 —— HTTP 403：

```json
{"code":"permission_denied","message":"您不是该团队的成员，无法查看能力矩阵","details":{}}
```

重复提交同一项目的申请 —— HTTP 409：

```json
{"code":"duplicate_application","message":"已有待处理申请","details":{}}
```

> 口径说明：错误凭据登录返回 400（`validation_error`），而非 401；401 仅用于
> 已登录会话的令牌缺失或失效。这与 `core/exceptions.py` 及前端 `client.js`
> 的处理一致（前端仅对 401 清除会话）。
