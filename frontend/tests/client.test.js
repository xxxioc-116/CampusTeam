import { describe, it, expect, vi } from "vitest";
import { createClient } from "../src/api/client.js";
describe("请求与错误 #8", () => {
  it("携带令牌并发送 JSON", async () => {
    const transport = vi.fn().mockResolvedValue(new Response('{"ok":true}'));
    const api = createClient({ transport, token: () => "token" });
    expect(
      await api("/profiles/me", { method: "PATCH", body: { name: "同学" } }),
    ).toEqual({ ok: true });
    expect(transport.mock.calls[0][1]).toMatchObject({
      headers: {
        Authorization: "Token token",
        "Content-Type": "application/json",
      },
      body: '{"name":"同学"}',
    });
  });
  it("认证方案可配置为 Bearer", async () => {
    const transport = vi.fn().mockResolvedValue(new Response('{"ok":true}'));
    const api = createClient({
      transport,
      token: () => "abc",
      authScheme: "Bearer",
    });
    await api("/profiles/me");
    expect(transport.mock.calls[0][1].headers.Authorization).toBe("Bearer abc");
  });
  it("展示接口错误并保留字段详情", async () => {
    const api = createClient({
      transport: async () =>
        new Response(
          '{"message":"姓名错误","details":{"display_name":"不能为空"}}',
          { status: 400 },
        ),
    });
    await expect(api("/profiles/me")).rejects.toMatchObject({
      message: "姓名错误",
      status: 400,
      details: { display_name: "不能为空" },
    });
  });
  it("401 清除登录态", async () => {
    const clear = vi.fn();
    const api = createClient({
      transport: async () => new Response("{}", { status: 401 }),
      onUnauthorized: clear,
    });
    await expect(api("/projects")).rejects.toThrow("登录已失效");
    expect(clear).toHaveBeenCalledOnce();
  });
  it("登录密码错误不会触发全局退出", async () => {
    const clear = vi.fn();
    const api = createClient({
      transport: async () =>
        new Response('{"message":"密码错误"}', { status: 401 }),
      onUnauthorized: clear,
    });
    await expect(api("/auth/login")).rejects.toThrow("密码错误");
    expect(clear).not.toHaveBeenCalled();
  });
  it("非 JSON 的 500 错误也有提示", async () => {
    const api = createClient({
      transport: async () => new Response("oops", { status: 500 }),
    });
    await expect(api("/projects")).rejects.toThrow("服务暂时不可用");
  });
  it("网络异常转换为中文错误", async () => {
    const api = createClient({
      transport: async () => {
        throw new TypeError("fetch");
      },
    });
    await expect(api("/projects")).rejects.toThrow("网络连接失败");
  });
  it("成功但非 JSON 的响应提示契约错误", async () => {
    const api = createClient({ transport: async () => new Response("html") });
    await expect(api("/projects")).rejects.toThrow("接口响应格式");
  });
  it("主动取消不显示网络错误", async () => {
    const controller = new AbortController();
    controller.abort();
    const api = createClient({
      transport: async () => {
        throw new DOMException("abort", "AbortError");
      },
    });
    await expect(
      api("/projects", { signal: controller.signal }),
    ).rejects.toMatchObject({ name: "AbortError" });
  });
  it("超时提示", async () => {
    const api = createClient({
      timeout: 5,
      transport: (_url, options) =>
        new Promise((_resolve, reject) =>
          options.signal.addEventListener("abort", () =>
            reject(new DOMException("abort", "AbortError")),
          ),
        ),
    });
    await expect(api("/projects")).rejects.toThrow("请求超时");
  });
});
