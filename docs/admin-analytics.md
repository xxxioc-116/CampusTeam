# 管理员统计 API 与指标口径（#23）

## 定位

平台级聚合统计，供管理员在答辩演示与运营复核时使用。只读、请求时计算、不落库；
仅 `User.Role.ADMIN` 可访问（`IsAdminRole`，`is_staff` 不参与判定）。

## 接口

`GET /api/v1/admin/analytics?top_n=5`

- `top_n`：热门项目与稀缺技能的返回条数，1–50，默认 5；非整数或越界返回 400。
- 权限：匿名 401；学生/队长（即使 `is_staff=True`）403 `permission_denied`。

## 指标口径

### 1. 热门项目 `popular_projects`

按项目的申请总数降序，并列按项目 id 升序。

```
applications = COUNT(Application WHERE project = p)        # 全部状态
team_size    = COUNT(TeamMember WHERE team = p.team)
```

返回 `project_id`、`title`、`project_type`、`status`、`applications`、`team_size`。
口径只表达"热度"（收到多少申请），不表达转化质量。

### 2. 稀缺技能 `scarce_skills`

```
demand_projects = COUNT(DISTINCT ProjectSkillRequirement.project WHERE skill = s)
supply_students = COUNT(DISTINCT UserSkill.user WHERE skill = s
                        AND user.is_active AND user.role = student)
gap             = max(demand_projects - supply_students, 0)
supply_per_project = supply_students / demand_projects
```

排序：`gap` 降序 → `supply_per_project` 升序 → 技能名升序。
只统计被至少一个项目需求的技能；无人拥有时 `supply_students = 0`、`gap` 取满额。

> 口径边界：一个项目需要某技能记 1 次需求，不区分 `required_level` 与权重；
> 停用账号与非学生角色不计入供给。

### 3. 组队成功率 `team_formation`

```
formed_projects = COUNT(Project WHERE team 的成员数 >= 2)
success_rate    = formed_projects / 项目总数        # 无项目时为 0
```

"成功组队"定义为团队至少 2 人（项目创建时自动建立团队并含队长本人，
因此 1 人团队即"尚未成队"）。

### 4. 概览 `overview`

| 字段 | 口径 |
|---|---|
| `students` | `is_active` 且业务角色为 student 的用户数 |
| `projects` | 项目总数 |
| `teams` | 至少有一名成员的团队数 |
| `recruiting_projects` | `status = recruiting` 的项目数 |
| `applications` / `invitations` | 总数、已接受数、接受率 = 已接受 / 总数（分母含待处理） |

接受率分母包含待处理请求，因此它反映"当前转化进度"，不是最终通过率。

## 响应示例

```json
{
  "top_n": 5,
  "overview": {
    "students": 12, "projects": 4, "teams": 3, "recruiting_projects": 2,
    "applications": {"total": 8, "accepted": 3, "acceptance_rate": 0.375},
    "invitations": {"total": 2, "accepted": 1, "acceptance_rate": 0.5}
  },
  "popular_projects": [
    {"project_id": 3, "title": "校园二手平台", "project_type": "course",
     "status": "recruiting", "applications": 5, "team_size": 2}
  ],
  "scarce_skills": [
    {"skill": "Figma", "category": "设计", "demand_projects": 3,
     "supply_students": 1, "gap": 2, "supply_per_project": 0.3333}
  ],
  "team_formation": {"projects": 4, "formed_projects": 3, "success_rate": 0.75},
  "definitions": {"popular_projects": "按申请总数降序，并列按项目 id 升序", "...": "..."}
}
```

响应内嵌 `definitions`，使结果可自证口径、便于答辩时解释与复核。

## 复核方式

- 纯公式见 `analytics/statistics.py`（`ratio` / `scarcity` / `formation` / `transitions`），
  单元测试在 `tests/test_statistics.py`。
- 接口与权限见 `core/analytics_api.py`，测试在 `core/tests/test_analytics_api.py`
  （管理员/学生/队长/停用用户、`is_staff` 学生、`top_n` 越界）。

## 未包含的内容

健康度与风险预警见 `docs/team-health.md`（团队维度，成员可读）；本接口只做平台维度聚合，
不返回个人画像内容。
