import { createClient, ApiError } from "./client.js";
import { mockTransport } from "./mock.js";
import { adaptRequest, adaptResponse, adaptError } from "./adapters.js";

export const isDemo = import.meta.env.VITE_USE_MOCK !== "false";

const request = createClient({
  base: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  transport: isDemo ? mockTransport : fetch,
  // Django REST Framework TokenAuthentication 的默认关键字是 Token，不是 Bearer
  authScheme: import.meta.env.VITE_AUTH_SCHEME || "Token",
});

/** 页面统一调用入口：演示模式直通，真实模式经过适配层 */
export async function api(path, options = {}) {
  if (isDemo) return request(path, options);
  const { path: realPath, options: realOptions } = adaptRequest(path, options);
  try {
    // 后端注册接口不返回令牌，注册成功后自动登录换取令牌
    if (realPath === "/auth/register") {
      await request(realPath, realOptions);
      const logged = await request("/auth/login", {
        method: "POST",
        body: {
          username: realOptions.body?.username,
          password: realOptions.body?.password,
        },
      });
      return adaptResponse("/auth/login", logged);
    }
    return adaptResponse(
      path,
      await request(realPath, realOptions),
      realOptions,
    );
  } catch (error) {
    throw adaptError(path, error);
  }
}

export function query(params) {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== "" && v != null) q.set(k, v);
  });
  return q.toString();
}

export { ApiError };
