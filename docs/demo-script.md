# CampusTeam v1.0.0 答辩演示脚本

## 准备

1. 按 README 创建环境并安装前后端依赖。
2. 设置仅用于本地演示的 `CAMPUS_DEMO_PASSWORD`，执行迁移和 `python manage.py seed_recommendation_demo`。
3. 分别启动 Django 与 Vue，打开 `/api/v1/health` 验证后端状态。
4. 不使用真实学生数据；演示完成后删除临时数据库和本地环境变量。

本地推荐演示用户名为 `rec_leader`、`rec_candidate` 与 `rec_admin`，密码由运行者通过环境变量现场传入，不写入仓库。演示账号不得部署到生产环境。

## 主演示链路

1. 注册并登录新用户，进入项目大厅。
2. 创建课程项目，系统自动建立团队并把创建人加入团队。
3. 在项目大厅按关键词检索，验证写后读一致性。
4. 保存个人能力画像，刷新后验证真实持久化。
5. 进入团队页，展示能力矩阵和五维能力缺口。
6. 打开互补推荐，展示 Top-K 排序、分项得分和推荐理由。
7. 邀请 `rec_candidate`；候选人通过真实 Token 接受邀请。
8. 返回团队页，验证成员加入、能力重算和缺口收敛。
9. 调用团队健康度接口，展示五维评分、状态和风险列表。
10. 使用 `rec_admin` 调用管理员统计接口，展示项目、组队率、接受率和稀缺技能。
11. 重复邀请同一成员，验证返回 409；普通学生越权操作验证返回 403。

## 证据

- 完整自动化：`powershell -File scripts/test-real.ps1`
- 后端覆盖率：`python -m coverage run --source=analytics,core manage.py test core tests`
- 覆盖率报告：`python -m coverage report -m`
- 性能报告：`python scripts/benchmark_api.py --out performance-report.md`
- 数据迁移一致性：`python manage.py makemigrations --check --dry-run`
- 系统检查：`python manage.py check`
- 发布证据检查：`python scripts/verify_release_evidence.py`

所有自动化产生的报告写入忽略目录，不把数据库、口令、Token 或生成物提交入库。

