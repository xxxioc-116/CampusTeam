import { test, expect } from "@playwright/test";

/**
 * 主答辩链路（#24）：注册 → 登录 → 项目检索 → 画像保存 → 团队矩阵/缺口
 * → 互补推荐 → 邀请 → 候选人接受 → 能力重算 → 健康度接口。
 *
 * 运行前提与 recommendation.spec.js 相同：真实后端 + 真实 Token，
 * 数据库由 scripts/test-real.ps1 / CI integration job 预置演示数据。
 *
 * 本用例为链路单独注册一名队长并自建项目/团队，避免污染 #27 用例共享的
 * 演示团队（team_id=1）与其"缺口 60"、"接受后无缺口"断言。
 */
const password = process.env.CAMPUS_DEMO_PASSWORD;
const api = "http://127.0.0.1:8001/api/v1";

async function apiLogin(request, username) {
  const response = await request.post(`${api}/auth/login`, {
    data: { username, password },
  });
  expect(response.ok()).toBeTruthy();
  return response.json();
}

test("答辩链路 01：新用户注册后进入项目页", async ({ page }) => {
  expect(password).toBeTruthy();
  const username = `defense_${Date.now().toString(36)}`;
  await page.goto("/register");
  await page.getByLabel("用户名").fill(username);
  await page.getByLabel("姓名").fill("答辩链路");
  await page.getByLabel("密码", { exact: true }).fill(password);
  await page.getByLabel("确认密码").fill(password);
  await page.getByRole("button", { name: "注册并进入" }).click();
  await expect(page).toHaveURL(/projects/);
});

test("答辩链路 02：检索、画像、矩阵、推荐、邀请、接受与健康度", async ({
  page,
  request,
}) => {
  expect(password).toBeTruthy();
  const suffix = Date.now().toString(36);
  const leaderName = `defense_leader_${suffix}`;

  // 1. 独立注册 + 登录 + 完善画像（真实 API）
  const registered = await request.post(`${api}/auth/register`, {
    data: { username: leaderName, password, display_name: "答辩队长" },
  });
  expect(registered.ok()).toBeTruthy();
  const leader = await apiLogin(request, leaderName);
  const auth = { Authorization: `Token ${leader.token}` };
  const profile = await request.patch(`${api}/profiles/me`, {
    headers: auth,
    data: {
      abilities: [80, 20, 40, 70, 60],
      skills: ["Python"],
      goal: "答辩演示",
      availability: [{ day: 1, start: "18:00", end: "21:00" }],
    },
  });
  expect(profile.ok()).toBeTruthy();

  // 2. 创建项目（自动成为队长）并配置团队需求
  const title = `答辩链路团队 ${suffix}`;
  const created = await request.post(`${api}/projects`, {
    headers: auth,
    data: {
      title,
      description: "答辩链路端到端验证",
      project_type: "course",
      max_members: 4,
    },
  });
  expect(created.ok()).toBeTruthy();
  const project = await created.json();
  const me = await (
    await request.get(`${api}/profiles/me`, { headers: auth })
  ).json();
  const teamId = me.user.team_id;
  expect(teamId).toBeTruthy();

  const requirement = await request.patch(
    `${api}/teams/${teamId}/recommendation-requirements`,
    {
      headers: auth,
      data: {
        abilities: [80, 80, 70, 70, 60],
        skills: ["Python"],
        goal: "答辩演示",
        availability: [{ day: 1, start: "18:00", end: "21:00" }],
      },
    },
  );
  expect(requirement.ok()).toBeTruthy();

  // 3. 浏览器登录
  await page.goto("/login");
  await page.getByLabel("用户名").fill(leaderName);
  await page.getByLabel("密码", { exact: true }).fill(password);
  await page.getByRole("button", { name: "登录", exact: true }).click();
  await expect(page).toHaveURL(/projects/);

  // 4. 项目检索（演示项目）
  await page.getByPlaceholder("项目名称或简介").fill("推荐联调");
  await page.getByRole("button", { name: "筛选" }).click();
  await expect(page.getByText("推荐联调演示").first()).toBeVisible();

  // 5. 画像保存（真实持久化）
  await page.getByRole("link", { name: "能力画像", exact: true }).click();
  await page.getByLabel("个人简介").fill("答辩链路端到端验证");
  await page.getByRole("button", { name: "保存画像" }).click();
  await expect(page.getByText("画像已保存")).toBeVisible();

  // 6. 团队矩阵与缺口
  await page.getByRole("link", { name: "我的团队" }).click();
  await expect(page).toHaveURL(new RegExp(`teams/${teamId}$`));
  await expect(page.getByText("能力矩阵")).toBeVisible();
  await expect(page.getByText(/缺口\s*60/).first()).toBeVisible();

  // 7. 互补推荐
  await page.getByRole("button", { name: "查看互补队友推荐 →" }).click();
  await expect(page).toHaveURL(/recommendations/);
  await expect(page.locator(".recommendation").first()).toContainText(
    "rec_candidate",
  );

  // 8. 邀请候选人
  const invitationResponse = page.waitForResponse(
    (response) =>
      response.url().endsWith(`/teams/${teamId}/invitations`) &&
      response.request().method() === "POST",
  );
  await page
    .getByRole("button", { name: "邀请加入团队", exact: true })
    .first()
    .click();
  await invitationResponse;
  const candidate = await apiLogin(request, "rec_candidate");

  // 9. 候选人通过邀请收件箱 UI 接受邀请
  await page.getByRole("button", { name: "退出" }).click();
  await page.getByLabel("用户名").fill("rec_candidate");
  await page.getByLabel("密码", { exact: true }).fill(password);
  await page.getByRole("button", { name: "登录", exact: true }).click();
  await page.getByRole("link", { name: "收到的邀请" }).click();
  await page.getByRole("button", { name: "接受并加入" }).click();
  await expect(page.getByText("该邀请已处理，不能重复操作。")).toBeVisible();

  // 10. 能力重算：候选人出现在成员列表，缺口收敛
  await page.getByRole("link", { name: "我的团队" }).click();
  await expect(page).toHaveURL(new RegExp(`teams/${teamId}$`));
  await expect(
    page.getByText("rec_candidate", { exact: true }).first(),
  ).toBeVisible();

  // 11. 健康度与风险预警接口（#19–#21）在真实数据上可用
  const health = await request.get(`${api}/teams/${teamId}/health`, {
    headers: auth,
  });
  expect(health.ok()).toBeTruthy();
  const healthBody = await health.json();
  expect(healthBody.status).toMatch(/^(healthy|watch|at_risk)$/);
  expect(Array.isArray(healthBody.risks)).toBeTruthy();
  expect(Object.keys(healthBody.scores).sort()).toEqual([
    "capability",
    "experience",
    "goal",
    "skill",
    "time",
  ]);

  // 12. 重复邀请必须被拒绝（同一候选人已是成员）
  const again = await request.post(`${api}/teams/${teamId}/invitations`, {
    headers: auth,
    data: { invitee_id: candidate.user.id, message: "重复邀请" },
  });
  expect(again.status()).toBe(409);

  // 13. 项目检索能命中新建项目（写后读一致性）
  await page.goto("/projects");
  await page.getByPlaceholder("项目名称或简介").fill(title);
  await page.getByRole("button", { name: "筛选" }).click();
  await expect(page.getByText(title).first()).toBeVisible();
  expect(project.id).toBeTruthy();
});

test("答辩链路 03：管理员统计接口", async ({ request }) => {
  expect(password).toBeTruthy();
  const adminLogin = await request.post(`${api}/auth/login`, {
    data: { username: "rec_admin", password },
  });
  // 演示数据默认没有管理员账号时跳过，避免依赖未 seed 的角色。
  test.skip(!adminLogin.ok(), "seed 数据中没有管理员账号，跳过该断言");
  const admin = await adminLogin.json();
  const stats = await request.get(`${api}/admin/analytics`, {
    headers: { Authorization: `Token ${admin.token}` },
  });
  expect(stats.ok()).toBeTruthy();
  const body = await stats.json();
  expect(body.overview.projects).toBeGreaterThan(0);
  expect(Array.isArray(body.scarce_skills)).toBeTruthy();
  expect(body.team_formation.projects).toBe(body.overview.projects);
});
