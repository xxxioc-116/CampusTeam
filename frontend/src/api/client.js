import { auth, clearSession } from "../auth.js";
export class ApiError extends Error {
  constructor(message, status = 0, details = {}) {
    super(message);
    this.status = status;
    this.details = details;
  }
}
export function createClient({
  base = "/api/v1",
  transport = fetch,
  token = () => auth.token,
  onUnauthorized = clearSession,
  timeout = 12000,
  authScheme = "Token",
} = {}) {
  return async function request(path, { method = "GET", body, signal } = {}) {
    const controller = new AbortController();
    const abort = () => controller.abort();
    if (signal?.aborted) abort();
    signal?.addEventListener("abort", abort, { once: true });
    const timer = setTimeout(abort, timeout);
    try {
      const headers = { Accept: "application/json" };
      if (body !== undefined) headers["Content-Type"] = "application/json";
      if (token()) headers.Authorization = authScheme + " " + token();
      const response = await transport(base.replace(/\/$/, "") + path, {
        method,
        headers,
        signal: controller.signal,
        ...(body === undefined ? {} : { body: JSON.stringify(body) }),
      });
      const data =
        response.status === 204
          ? null
          : await response.json().catch(() => null);
      if (!response.ok) {
        if (response.status === 401 && !path.startsWith("/auth/"))
          onUnauthorized();
        throw new ApiError(
          data?.message ||
            {
              401: "登录已失效，请重新登录",
              403: "你没有操作权限",
              404: "内容不存在",
              409: "请勿重复操作",
            }[response.status] ||
            "服务暂时不可用，请重试",
          response.status,
          data?.details || {},
        );
      }
      if (response.status !== 204 && data === null)
        throw new ApiError("接口响应格式不正确", response.status);
      return data;
    } catch (error) {
      if (error instanceof ApiError) throw error;
      if (signal?.aborted) throw new DOMException("请求已取消", "AbortError");
      throw new ApiError(
        controller.signal.aborted
          ? "请求超时，请重试"
          : "网络连接失败，请检查网络或后端是否启动",
      );
    } finally {
      clearTimeout(timer);
      signal?.removeEventListener("abort", abort);
    }
  };
}
