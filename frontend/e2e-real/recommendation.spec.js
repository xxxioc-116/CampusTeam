import { test, expect } from "@playwright/test";

test("真实画像、推荐、邀请接受与团队能力重算 #27", async ({ page }) => {
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
  await invitationResponse;
  await expect(
    page.getByRole("button", { name: "已邀请", exact: true }).first(),
  ).toBeDisabled();
  await page.getByRole("button", { name: "退出" }).click();
  await page.getByLabel("用户名").fill("rec_candidate");
  await page.getByLabel("密码", { exact: true }).fill(password);
  await page.getByRole("button", { name: "登录", exact: true }).click();
  await page.getByRole("link", { name: "收到的邀请" }).click();
  await expect(page.getByText("推荐联调演示", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "接受并加入" }).click();
  await expect(page.getByText("该邀请已处理，不能重复操作。")).toBeVisible();
  await page.getByRole("link", { name: "我的团队" }).click();
  await expect(page).toHaveURL(new RegExp(`teams/${teamId}$`));
  await expect(page.getByText("目前没有能力缺口")).toBeVisible();
  await expect(
    page.getByRole("cell", { name: "rec_candidate", exact: true }),
  ).toBeVisible();
});
