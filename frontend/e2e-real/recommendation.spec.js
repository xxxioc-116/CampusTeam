import { test, expect } from "@playwright/test";

test("真实画像、推荐、邀请接受与团队能力重算 #27", async ({
  page,
  request,
}) => {
  const password = process.env.CAMPUS_DEMO_PASSWORD;
  expect(password).toBeTruthy();
  await page.goto("/login");
  await page.getByLabel("用户名").fill("rec_leader");
  await page.getByLabel("密码", { exact: true }).fill(password);
  await page.getByRole("button", { name: "登录", exact: true }).click();
  await expect(page).toHaveURL(/projects/);
  await page.getByRole("link", { name: "能力画像", exact: true }).click();
  await page.getByLabel("个人简介").fill("真实后端持久化联调");
  await page.getByRole("button", { name: "保存画像" }).click();
  await expect(page.getByText("画像已保存")).toBeVisible();
  await page.reload();
  await expect(page.getByLabel("个人简介")).toHaveValue("真实后端持久化联调");
  await page.getByRole("link", { name: "我的团队" }).click();
  await expect(page).toHaveURL(/teams\/\d+$/);
  const teamId = /teams\/(\d+)/.exec(page.url())[1];
  await expect(page.getByText("缺口 60", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "查看互补队友推荐 →" }).click();
  await expect(page.locator(".recommendation").first()).toContainText(
    "rec_candidate",
  );
  const invitationResponse = page.waitForResponse(
    (response) =>
      response.url().endsWith(`/teams/${teamId}/invitations`) &&
      response.request().method() === "POST",
  );
  await page
    .getByRole("button", { name: "邀请加入团队", exact: true })
    .first()
    .click();
  const invitation = await (await invitationResponse).json();
  await expect(
    page.getByRole("button", { name: "已邀请", exact: true }).first(),
  ).toBeDisabled();
  const login = await request.post("http://127.0.0.1:8001/api/v1/auth/login", {
    data: { username: "rec_candidate", password },
  });
  expect(login.ok()).toBeTruthy();
  const candidate = await login.json();
  // The current UI has no invitation inbox; accept through the real API using the candidate's token.
  const accepted = await request.post(
    `http://127.0.0.1:8001/api/v1/invitations/${invitation.id}/transition`,
    {
      headers: { Authorization: `Token ${candidate.token}` },
      data: { action: "accept" },
    },
  );
  expect(accepted.ok()).toBeTruthy();
  await page.goto(`/teams/${teamId}`);
  await expect(page.getByText("目前没有能力缺口")).toBeVisible();
  await expect(page.getByText("rec_candidate", { exact: true })).toBeVisible();
});
