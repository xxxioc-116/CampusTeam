# 前端联调契约 v0.1（待后端确认）

依据 API 草案扩展字段，保持 `/api/v1` 和原路径。无真实后端可验证，本文件是建议契约。能力和所有分项分数均为 0–100，权重为 0–1。正式算法若返回 0–1 归一化分数，必须在接口适配层统一换算，不能混用。

## 通用规则

- 路径不带末尾斜杠，JSON 请求/响应；令牌 `Authorization: Bearer <access_token>`。
- 错误 HTTP 400/401/403/404/409/5xx：`{"code":"...","message":"可展示错误","details":{}}`。
- 后端提供可信角色 `student` / `captain` / `admin`，注册只能生成 student。
- 前端不实现令牌刷新；过期 401 退出，网络失败保留会话。
- 本人、团队、候选人 ID 可为数字或不含斜杠的安全字符串。时间段 day 1–7，HH:mm、当日，跨日拆分。

## 登录注册与画像 #7–9

`POST /auth/login` 请求 `{"username":"student","password":"…"}`；`POST /auth/register` 额外 `display_name`。

成功响应（登录/注册相同结构，注册后直接登录）：

```json
{"access_token":"opaque-token","user":{"id":1,"username":"student","display_name":"林同学","role":"student","team_id":1}}
```

没有团队时 `team_id: null`。用户名当前校验为 3–30 位字母、数字、下划线；密码至少 8 位。更严格策略以双方协商结果为准。

`GET /profiles/me` 返回：

```json
{
 "user":{"id":1,"username":"student","display_name":"林同学","role":"student","team_id":1},
 "profile":{"display_name":"林同学","bio":"","skills":["Vue"],"abilities":[80,45,70,85,60],"goal":"学习提升","experience":"课程项目","availability":[{"day":1,"start":"18:00","end":"20:00"}]}
}
```

`PATCH /profiles/me` 请求 profile 的完整可编辑字段，成功返回同上，保存以响应 profile 回显。无画像允许 `profile: null`；数组返回空数组，字符串为空字符串，不向客户端返回可修改角色。abilities 顺序固定：编程开发、数据分析、产品设计、沟通协作、项目管理。

## 项目大厅 #10

`GET /projects?search=校园&category=课程项目&skill=Vue&page=1&page_size=6`。page 从 1 开始；空参数省略；多个筛选条件按 AND 组合。

```json
{"count":1,"results":[{"id":1,"title":"校园低碳出行地图","description":"项目简介","category":"课程项目","skills":["Vue"],"member_count":2,"capacity":5,"status":"recruiting","team_id":1,"can_view_team":true,"applied":false}]}
```

status 取 `recruiting` / `closed`；`can_view_team` 依据当前用户授权返回，所有团队相关接口仍须后端校验。筛选总数为 count。无数据为 `{"count":0,"results":[]}`。

`POST /projects/{id}/applications` 请求 `{"message":"希望加入项目"}`，成功 201 `{"id":1,"status":"pending"}`；已申请/成员/关闭招募按业务规则拒绝且返回可展示信息。后端必须有唯一约束/幂等规则，重复返回 409。提交不自动加入团队。

## 团队矩阵与缺口 #11

`GET /teams/{id}/capability-matrix`：

```json
{"team_name":"低碳校园实验室","dimensions":["编程开发","数据分析","产品设计","沟通协作","项目管理"],"current":[80,45,70,85,60],"required":[85,80,75,80,75],"members":[{"id":1,"display_name":"林同学","abilities":[80,30,70,65,45]}]}
```

current / required / members.abilities 按 dimensions 同序；缺值显示 0，越界值在显示层裁剪。空团队 members `[]`，所有当前维度为 0；未配置维度时 dimensions `[]`，页面显示暂无数据。聚合口径由算法成员确认，演示样例 current 采用逐维最大值，不在前端计算聚合。

`GET /teams/{id}/gaps`：

```json
{"results":[{"dimension":"数据分析","gap":35,"explanation":"当前 45 / 需求 80，优先补齐。"}]}
```

gap 使用非负 0–100 缺口。空数组代表无缺口。两个接口均仅允许本团队成员或获授权管理员访问。

## 推荐解释与动作 #12

`GET /teams/{id}/recommendations?top_k=5`，可选 3/5/10。返回：

```json
{
 "project_id":1,"weight_version":"baseline-v1","applied":false,
 "weights":{"complement":0.35,"skill":0.25,"time":0.2,"goal":0.1,"experience":0.1},
 "results":[{"id":101,"display_name":"许同学","skills":["Python"],"score":89.75,"scores":{"complement":95,"skill":90,"time":85,"goal":90,"experience":80},"reasons":["可补齐数据分析能力"],"risks":[],"invited":false}]
}
```

后端排序并生成理由和风险，前端只显示，不实现正式推荐算法。贡献 = 分项分数 × 权重，总分由后端给出；推荐算法要保证其一致性，权重版本必须可追溯。没有候选人 results `[]`。演示分数是固定样例，仅用于 UI 测试。

`POST /teams/{id}/invitations` 请求 `{"candidate_id":101,"message":"邀请加入团队"}`；仅队长/授权管理员允许；201 `{"status":"pending"}`，重复 409。邀请待审批期间不加入团队。

学生可见项目申请按钮，负责人可向候选人发邀请；真实后端须禁止已是成员重复申请、越权邀请等，演示环境为便于展示动作不完整覆盖所有业务状态。审批、加入后重新计算能力属于 #5/#18/#27 的联合工作。
