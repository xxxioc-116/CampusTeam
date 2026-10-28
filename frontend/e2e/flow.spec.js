import { test, expect } from "@playwright/test";
async function login(page, name = "captain") {
  await page.goto("/login");
  await page.getByLabel("用户名").fill(name);
  const password = await page.getByTestId("demo-password").textContent();
  await page.getByLabel("密码", { exact: true }).fill(password);
  await page.getByRole("button", { name: "登录", exact: true }).click();
  await expect(page).toHaveURL(/projects/);
}
test("未登录拦截、登录错误、退出", async ({ page }) => {
  await page.goto("/profile");
  await expect(page).toHaveURL(/login.*redirect/);
  await page.getByLabel("用户名").fill("student");
  await page.getByLabel("密码", { exact: true }).fill("wrong123");
  await page.getByRole("button", { name: "登录", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("用户名或密码错误");
  const password = await page.getByTestId("demo-password").textContent();
  await page.getByLabel("密码", { exact: true }).fill(password);
  await page.getByRole("button", { name: "登录", exact: true }).click();
  await expect(page).toHaveURL(/profile/);
  await page.getByRole("button", { name: "退出" }).click();
  await expect(page).toHaveURL(/login/);
});
test("画像保存与刷新回显", async ({ page }) => {
  await login(page);
  await page.getByRole("link", { name: "能力画像", exact: true }).click();
  await page.getByLabel("姓名", { exact: true }).fill("测试同学");
  await page.getByLabel("个人简介").fill("希望加入数据分析项目");
  await page.getByLabel("技能标签").fill("Vue, Python");
  await page.getByRole("button", { name: "保存画像" }).click();
  await expect(page.getByText("画像已保存")).toBeVisible();
  await page.reload();
  await expect(page.getByLabel("姓名", { exact: true })).toHaveValue(
    "测试同学",
  );
  await expect(page.getByLabel("个人简介")).toHaveValue("希望加入数据分析项目");
  await page.screenshot({
    path: "../docs/images/profile-accessibility.png",
    fullPage: true,
  });
});

test("刷新后演示口令更新，旧口令不能登录", async ({ page }) => {
  await page.goto("/login");
  const previous = await page.getByTestId("demo-password").textContent();
  await page.reload();
  const current = await page.getByTestId("demo-password").textContent();
  expect(current).not.toBe(previous);
  await page.getByLabel("用户名").fill("captain");
  await page.getByLabel("密码", { exact: true }).fill(previous);
  await page.getByRole("button", { name: "登录", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("用户名或密码错误");
  await page.getByLabel("密码", { exact: true }).fill(current);
  await page.getByRole("button", { name: "登录", exact: true }).click();
  await expect(page).toHaveURL(/projects/);
});
test("筛选、空态、分页与申请", async ({ page }) => {
  await login(page);
  await expect(page.locator(".project-card")).toHaveCount(6);
  await page.getByRole("button", { name: "下一页" }).click();
  await expect(page.locator(".project-card").first()).toContainText(
    "校园心理关怀工具",
  );
  await page.getByLabel("搜索项目").fill("不存在的名称");
  await page.getByRole("button", { name: "筛选", exact: true }).click();
  await expect(page.getByText("暂无数据")).toBeVisible();
  await page.getByLabel("搜索项目").fill("低碳");
  await page.getByRole("button", { name: "筛选", exact: true }).click();
  await expect(page.locator(".project-card")).toHaveCount(1);
  await page.getByRole("button", { name: "申请加入", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "已申请", exact: true }),
  ).toBeDisabled();
});
test("团队雷达、推荐解释与邀请", async ({ page }) => {
  await login(page);
  await page.getByRole("link", { name: "我的团队" }).click();
  await expect(page.getByRole("img", { name: /雷达图/ })).toBeVisible();
  await expect(page.getByText("缺口 35", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "查看互补队友推荐 →" }).click();
  await expect(page.locator(".recommendation")).toHaveCount(5);
  await expect(page.locator(".recommendation").first()).toContainText(
    "能力互补度",
  );
  await expect(page.locator(".recommendation").first()).toContainText(
    "数据分析能力可补齐项目当前缺口",
  );
  await page
    .getByRole("button", { name: "邀请加入团队", exact: true })
    .first()
    .click();
  await expect(
    page.getByRole("button", { name: "已邀请", exact: true }),
  ).toBeDisabled();
  await page.getByLabel("推荐人数").selectOption("3");
  await expect(page.locator(".recommendation")).toHaveCount(3);
});
test("学生拦截管理员路由与团队资源越权", async ({ page }) => {
  await login(page, "student");
  await page.goto("/admin");
  await expect(page).toHaveURL(/forbidden/);
  await page.goto("/teams/2");
  await expect(page.getByRole("alert")).toContainText("只有本团队成员可以查看");
});
