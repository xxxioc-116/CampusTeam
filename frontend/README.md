# CampusTeam 前端：任务 #7–#12

基于上传快照 `d5742890e7d936ca14ca497c93d1301ec5c43532`。原仓库只有文档，本次新增 Vue 3、Vue Router、Element Plus、ECharts 应用及测试。未实现 Django 后端、真实推荐算法、审批闭环或 #27 加入后重算。

## 1. Windows 首次启动（演示模式，无需 Python / MySQL）

安装 Node.js 22.12 或更新的 LTS 版本。解压到普通文件夹，用 VS Code 打开 `CampusTeam-main`，选择“终端 → 新建终端”，执行：

```powershell
cd frontend
node --version
npm --version
npm ci
Copy-Item .env.example .env
npm run dev
```

打开终端提示的地址，通常为 http://127.0.0.1:5173 。保持终端运行；停止用 Ctrl+C。macOS / Linux 将复制命令改为 `cp .env.example .env`。若 PowerShell 提示禁止执行 npm.ps1，可使用 `npm.cmd ci` 和 `npm.cmd run dev`，或切换 VS Code 终端为 Command Prompt。

演示账号：`student`（学生）、`captain`（队长）、`admin`（管理员）；统一密码 `Campus123!`。学生与队长属于团队 1，管理员能查看其他团队。新注册账号默认学生且尚无团队。注册账号的密码仅在内存中，刷新后不能再次用该新账号登录，但现有登录会话保留；可重新注册或用内置演示账号。请勿输入真实密码、个人隐私信息。

演示数据保存在浏览器 localStorage，登录令牌放在 sessionStorage。演示认证与权限检查都在客户端，不能用于生产。重置方法：浏览器 F12 → Application / 应用 → Storage → 清除此站点数据，再刷新。多个标签页的演示状态不保证并发一致。

## 2. 一步步手动验收

| 任务 | 操作 | 预期 |
|---|---|---|
| #7 路由 | 未登录直接打开 `/profile` | 跳转登录；登录后回到画像 |
| #7 越权 | student 登录后访问 `/admin`；访问 `/teams/2` | 分别显示 403 页面、接口权限提示 |
| #8 登录/注册 | 输入错误密码；注册虚构账号；退出 | 显示错误；注册进入大厅；退出后不能访问保护页 |
| #9 画像 | 保存姓名、技能、五维能力、空闲时间后刷新 | 数据回显；空画像显示五维 0、时间空态 |
| #9 校验 | 两个同日时间段重叠；结束早于开始 | 阻止保存并提示原因；能力限制为 0–100 |
| #10 大厅 | 搜索“低碳”、筛选 Python、切换第二页 | 条件生效、总数更新、页面结果不同 |
| #10 空态 | 搜索“不存在的名称” | 显示“暂无数据” |
| #10 申请 | 点击“申请加入” | 成功提示、按钮变为“已申请”并禁用 |
| #11 矩阵 | captain → 我的团队 | 雷达、能力表、成员表、缺口显示；数据分析缺口 35 |
| #12 推荐 | 团队页 → 查看互补队友推荐 → Top 3 | 展示 3 人、五维分数/权重/贡献、理由、风险 |
| #12 邀请 | captain 点击推荐中的邀请 | 成功后按钮显示“已邀请”；student 不显示邀请按钮 |
| #45 邀请收件箱 | 顶部“收到的邀请” → 接受或拒绝 | 展示团队、邀请人、留言和状态；接受后“我的团队”刷新；已处理邀请无操作按钮 |

演示模式不访问网络，因此浏览器 Offline 不能模拟演示接口网络故障。真实网络失败、超时、401、403、非 JSON 等已在请求层测试中验证。要手动检查真实网络异常，切换正式 API 模式且关闭后端，应看到网络错误与重试按钮。

## 3. 自动化测试与构建

在 `frontend` 目录运行：

```powershell
npm run lint
npm test
npm run build
```

`npm test` 是无界面的单元/流程测试；`npm run build` 生成 `dist/`，成功后用 `npm run preview` 预览。不要双击 `dist/index.html`，必须由 HTTP 服务器提供。首次端到端测试还需下载浏览器：

```powershell
npx playwright install chromium
npm run test:e2e
```

Linux CI 用 `npx playwright install --with-deps chromium`。测试会自动启动本地演示站点，不需要手动另开服务。端到端覆盖路由、登录失败、画像保存回显、筛选分页、申请、图表、推荐邀请与越权。测试失败会在终端显示失败步骤，`test-results/` 为临时结果。

## 4. 接入队友的 Django 后端

1. 先由后端同学提供可运行的服务和测试账号。原 ZIP 中没有 `backend/`、MySQL 配置或 Docker Compose，不能执行根 README 中原先的后端示例。
2. 修改 `frontend/.env`：

```dotenv
VITE_USE_MOCK=false
VITE_API_BASE_URL=/api/v1
API_PROXY_TARGET=http://127.0.0.1:8000
```

3. 重新启动 `npm run dev`。Vite 将 `/api` 转发到 Django，浏览器仍访问 5173，开发时不需要额外跨域配置。
4. 按 `../docs/frontend-api-contract.md` 对齐字段、无尾斜杠路径、Bearer 令牌、权限和分页。这里的响应字段是本次建议的联调契约，原草案只定义了路径，尚未得到后端实现验证。
5. 正式部署时设置 `VITE_USE_MOCK=false` 后重新构建，并由同源反向代理提供 `/api`；`API_PROXY_TARGET` 只对开发服务器生效。History 路由需要服务器把非 `/api` 的前端路径回退到 `index.html`。

示例 Nginx 规则（按部署路径调整）：

```nginx
location /api/ { proxy_pass http://127.0.0.1:8000; }
location / { try_files $uri $uri/ /index.html; }
```

后端必须独立验证所有成员、角色与操作权限，不能信任前端隐藏按钮或客户端角色。当前契约未实现令牌刷新，过期 401 会清除会话并要求重登。生产认证、HTTPS、刷新/注销策略由后端团队确认。

## 5. 代码导读

- `src/router.js` / `src/auth.js`：公开路由、登录回跳、角色守卫；刷新后从本人接口恢复用户角色。
- `src/api/client.js`：统一 JSON 请求、超时、取消、错误与失效处理。
- `src/api/mock.js`：演示数据与模拟传输，不属于后端交付。
- `src/views/`：登录注册、画像、大厅、团队、推荐与邀请收件箱页面。
- `src/components/RadarChart.vue`：雷达映射、容器缩放和卸载销毁。
- `src/domain/capabilities.js`：五维能力、校验与可单测的图表数据转换。
- `tests/` / `e2e/`：单元、演示流程、页面验收测试。

项目大厅只在提交筛选或切页时请求；取消旧请求并使用序列号防止旧响应覆盖新结果。推荐 Top-K 同样防止竞态。申请/邀请按钮在提交期间禁用且成功后持久显示状态；最终防重复由真实后端提供唯一约束和 409。

## 6. 团队提交方式

不要覆盖队友后续提交。先在你自己的最新仓库创建分支，复制本包新增 `frontend/`、`docs/frontend-api-contract.md`、`docs/frontend-delivery.md`、`.github/workflows/frontend.yml`；按需合并根 README、CHANGELOG、`.gitignore` 与 `docs/api.md` 的文档变化。不要提交 node_modules、.env、dist。

```powershell
git switch main
git pull
git switch -c feature/7-12-frontend
# 将上述文件复制到你的工作目录后
git add frontend docs .github/workflows/frontend.yml README.md CHANGELOG.md .gitignore
git commit -m "feat(frontend): implement profile projects and team insights"
git push -u origin feature/7-12-frontend
```

提交前自己阅读并运行测试。按项目要求建议把 #7–#12 拆成较小 PR；若合为大 PR，应解释首次骨架与共享接口的原因。真实 Issue 编号确认后再写关联号，别仅凭截图关闭 Issue。请求队友 Review，不要自评自合。注明 AI 辅助生成、本人测试及后续联调范围。此次没有推送 GitHub、创建 PR、生成评审或宣称真实后端验收完成。
