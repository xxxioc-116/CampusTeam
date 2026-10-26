import { beforeEach, describe, it, expect, vi } from "vitest";
import { createMemoryHistory } from "vue-router";
const { api } = vi.hoisted(() => ({ api: vi.fn() }));
vi.mock("../src/api/index.js", () => ({ api, isDemo: true, query: () => "" }));
import { makeRouter } from "../src/router.js";
import { auth, clearSession } from "../src/auth.js";
beforeEach(() => {
  clearSession();
  api.mockReset();
});
describe("真实路由守卫与刷新恢复 #7", () => {
  it("未登录无法直接打开画像", async () => {
    const router = makeRouter(createMemoryHistory());
    await router.push("/profile");
    expect(router.currentRoute.value.path).toBe("/login");
    expect(router.currentRoute.value.query.redirect).toBe("/profile");
    expect(api).not.toHaveBeenCalled();
  });
  it("刷新后从接口恢复角色再判断权限", async () => {
    auth.token = "valid";
    api.mockResolvedValue({ user: { role: "student" } });
    const router = makeRouter(createMemoryHistory());
    await router.push("/admin");
    expect(router.currentRoute.value.path).toBe("/forbidden");
    expect(auth.user.role).toBe("student");
    expect(api).toHaveBeenCalledOnce();
  });
  it("过期会话清除并回到登录", async () => {
    auth.token = "expired";
    api.mockRejectedValue({ status: 401 });
    const router = makeRouter(createMemoryHistory());
    await router.push("/profile");
    expect(auth.token).toBe("");
    expect(router.currentRoute.value.path).toBe("/login");
  });
  it("恢复会话时网络异常不误报为权限错误，可重试", async () => {
    auth.token = "valid";
    api
      .mockRejectedValueOnce(new Error("network"))
      .mockResolvedValueOnce({ user: { role: "student" } });
    const router = makeRouter(createMemoryHistory());
    await router.push("/profile");
    expect(router.currentRoute.value.path).toBe("/unavailable");
    expect(auth.token).toBe("valid");
    await router.push("/projects");
    expect(router.currentRoute.value.path).toBe("/projects");
    expect(api).toHaveBeenCalledTimes(2);
  });
});
