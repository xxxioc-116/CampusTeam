# CampusTeam 演示脚本

## 准备

1. 按 README 创建环境、迁移数据库并运行 `python manage.py seed_demo --leader-password '<本地密码>' --student-password '<本地密码>'`。
2. 执行 `python manage.py runserver`。
3. 打开 `/api/v1/health` 验证服务状态。

本地演示用户名为 `demo_leader` 与 `demo_student`，密码由运行命令的人现场传入，不写入仓库。演示账号不得部署到生产环境。

## 主演示链路

1. 注册学生账号并登录，展示 Token 与统一用户信息。
2. 使用队长账号创建课程项目，系统自动建立团队并把创建人加入团队。
3. 在项目列表使用关键词、类型和分页检索。
4. 学生申请加入项目；重复申请被拒绝并返回 `duplicate_application`。
5. 队长接受申请，成员自动加入团队；重复处理被拒绝。
6. 队长向另一学生发出邀请；学生接受邀请。
7. 管理员查看审计日志，展示注册、登录、创建项目、申请、邀请和状态变化记录。
8. 展示越权测试：普通学生修改他人项目或邀请成员均返回 403。

## 证据

- 自动化测试：`python -m coverage run manage.py test`
- 覆盖率：`python -m coverage report -m`
- 数据迁移一致性：`python manage.py makemigrations --check --dry-run`
- 系统检查：`python manage.py check`

