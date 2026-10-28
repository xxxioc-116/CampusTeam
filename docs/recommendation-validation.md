# 推荐模块验证记录

日期：2026-10-27（Asia/Shanghai）；Windows、Python 3.13.16、Node 24.16.0、SQLite。
依赖基线：后端 PR #29 的 2ec59442；前端 PR #30 的 c2450f2e。

| 检查 | 结果 |
|---|---|
| Django check / makemigrations --check --dry-run | 通过，无迁移漂移 |
| Python 测试 | 31 项通过：原后端 8、算法 10、实验 4、推荐 API 8、性能 1 |
| 后端和算法业务覆盖率 | 629 条语句、36 未执行，94%；排除测试、迁移、管理命令和实验脚本 |
| 算法核心覆盖率 / 推荐 API 覆盖率 | 96% / 98% |
| Ruff | 全部 analytics、tests、core、campusteam、manage.py 通过 |
| 前端测试 | 62 项通过；包含真实画像响应完整字段回显回归 |
| 前端覆盖率 | 行 96.26%、分支 88.88%；范围 auth、adapters/client、domain，不含全部页面 |
| 前端 lint / 格式 / Vite 构建 | 通过；构建仍提示大包 |
| Python 隔离构建 | sdist 和 wheel 成功 |
| 真实 Chromium | 1 项通过，总耗时 4.4 秒；Django + SQLite + 非 Mock Vite |

## 真实闭环

浏览器登录队长 → 保存画像 → 刷新确认持久化 → 团队数据分析缺口 60 →
推荐首位 rec_candidate → 浏览器邀请 → 候选真实登录后通过 API 接受 →
浏览器显示新成员和缺口清空。邀请接受通过 API 完成，原前端没有邀请收件箱。
另有 API 测试覆盖申请加入、负责人审批、成员能力重算。
前端基础属于 PR #30 作者，后端基础属于 PR #29 作者；本次贡献是推荐、适配、测试和门禁。

## 真实 Token 性能基线（#18）

固定种子 20261027，每个规模请求 5 次，Top-5；启用 coverage。

| 候选人 | 中位耗时 ms | 最大耗时 ms | SQL 次数 |
|---|---:|---:|---:|
| 100 | 36.770 | 41.914 | 6 |
| 500 | 157.731 | 162.808 | 6 |
| 1000 | 321.122 | 354.041 | 6 |

使用 APIClient 和真实 Authorization: Token 请求头，包含认证查询；不含网络和浏览器渲染。
候选规模增长不增加查询数。每次请求核对唯一候选、排序、分项贡献和；
另以独立人工公式 sum(min(能力,90))/450*35 验证应选人员及其分数。
耗时受机器负载影响，不是生产 SLA，尚未验证 MySQL。

复现：设置 DJANGO_DEBUG=true，运行
`python manage.py test core.tests.test_recommendation_performance`。
算法实验：`python -m analytics.experiment`；种子和质量指标可复现，耗时不可固定。
算法/实验测试：`python -m unittest discover -s tests`（14 项）。
完整复跑命令见 local-handoff.md。

## 尚待完成

GitHub Actions 结果必须以实际远端运行为准；本地通过不等于远端通过。
非作者审批、依赖 PR 合并和管理员启用 main 强制门禁不能由本次自评代替。
#26 配置与管理员操作见 ci-gate.md；在启用前不关闭该 Issue。

## 2026-10-28 权限评审修复

推荐 API 两处权限判断已移除 is_staff，仅按业务 User.Role.ADMIN、队长和成员关系授权。
新增 4 项真实 Token 回归测试：staff 学生访问其他团队矩阵/缺口/推荐均为 403；
staff 学生成员修改需求为 403 且数据库保持原值；非 staff 业务 ADMIN 可读取并更新需求。
写入拒绝测试先加入团队，确保独立覆盖第二处写权限检查，而非提前被成员检查拦截。
本地完整 Python 测试 36 项通过，业务覆盖率 94%、推荐 API 98%。
SonarCloud 依赖安装修复保留。最新远端结果以 PR 当前提交的全部 check-runs 为准。

## main 基线的前端回归

将 #33 的 base 改为 main 后，尚未合并的 #30 前端代码也被纳入新增代码扫描。
修复固定演示口令、模拟 URL、能力滑块标签关联及前端安装脚本四项标注。
演示账号使用本页随机生成的 UUID 口令，登录页显示当前口令，刷新后更新；不影响真实后端认证。
新增单元和浏览器回归验证随机口令、错误口令及刷新后旧口令失效。
画像页的滑块容器改用 div 和具名控件，保留原布局；评审截图见 images/profile-accessibility.png。
独立 Chromium Mock 页面回归 6 项通过；真实后端联调仍由 quality.yml 的 integration 任务验证。
