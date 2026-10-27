import { reactive } from "vue";
// 令牌仅存当前标签页；刷新后通过 /profiles/me 从服务器恢复角色。
export const auth = reactive({
  token: sessionStorage.getItem("ct-token") || "",
  user: null,
});
// 后端真实角色为 student / leader / admin；captain 仅用于兼容演示数据
export const LEADER_ROLES = ["leader", "captain", "admin"];
export function canManageTeam(role) {
  return LEADER_ROLES.includes(role);
}
export function setSession(data) {
  // 后端返回 token，接口契约写作 access_token，两者都接受
  const token = data?.access_token || data?.token;
  if (!token || !data.user) throw new Error("登录响应缺少令牌或用户信息");
  auth.token = token;
  auth.user = data.user;
  sessionStorage.setItem("ct-token", auth.token);
}
export function clearSession() {
  auth.token = "";
  auth.user = null;
  sessionStorage.removeItem("ct-token");
}
export function permissionDecision(to, state) {
  if (to.meta.public) return true;
  if (!state.token) return { path: "/login", query: { redirect: to.fullPath } };
  if (to.meta.roles && !to.meta.roles.includes(state.user?.role))
    return "/forbidden";
  return true;
}
export function safeRedirect(value) {
  return typeof value === "string" &&
    value.startsWith("/") &&
    !value.startsWith("//") &&
    !/^\/(login|register)(?:[/?#]|$)/.test(value)
    ? value
    : "/projects";
}
