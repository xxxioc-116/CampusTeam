import { describe, it, expect } from "vitest";
import { permissionDecision, safeRedirect } from "../src/auth.js";
const to = { fullPath: "/profile", meta: {} };
describe("路由权限 #7", () => {
  it("未登录保留原路径", () =>
    expect(permissionDecision(to, { token: "" })).toEqual({
      path: "/login",
      query: { redirect: "/profile" },
    }));
  it("登录学生可访问普通路由", () =>
    expect(
      permissionDecision(to, { token: "x", user: { role: "student" } }),
    ).toBe(true));
  it("学生不可进入管理员页", () =>
    expect(
      permissionDecision(
        { ...to, meta: { roles: ["admin"] } },
        { token: "x", user: { role: "student" } },
      ),
    ).toBe("/forbidden"));
  it("管理员可进入管理路由", () =>
    expect(
      permissionDecision(
        { ...to, meta: { roles: ["admin"] } },
        { token: "x", user: { role: "admin" } },
      ),
    ).toBe(true));
  it("公开页面不要求令牌", () =>
    expect(
      permissionDecision({ ...to, meta: { public: true } }, { token: "" }),
    ).toBe(true));
  it.each([
    "https://evil.test",
    "//evil.test",
    "/login",
    "/register?redirect=/profile",
    undefined,
  ])("拒绝不安全的回跳 %s", (value) =>
    expect(safeRedirect(value)).toBe("/projects"),
  );
  it("保留内部回跳", () => expect(safeRedirect("/teams/1")).toBe("/teams/1"));
});
