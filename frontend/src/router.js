import { createRouter, createWebHistory } from "vue-router";
import { auth, clearSession, permissionDecision } from "./auth.js";
import { api } from "./api/index.js";
const Login = () => import("./views/Login.vue");
const Profile = () => import("./views/Profile.vue");
const Projects = () => import("./views/Projects.vue");
const Team = () => import("./views/Team.vue");
const Recommendations = () => import("./views/Recommendations.vue");
const Invitations = () => import("./views/Invitations.vue");
const Status = () => import("./views/Status.vue");
export function makeRouter(history = createWebHistory()) {
  const router = createRouter({
    history,
    routes: [
      { path: "/", redirect: "/projects" },
      { path: "/login", component: Login, meta: { public: true } },
      { path: "/register", component: Login, meta: { public: true } },
      { path: "/profile", component: Profile },
      { path: "/projects", component: Projects },
      { path: "/invitations", component: Invitations },
      { path: "/teams/:id", component: Team },
      { path: "/teams/:id/recommendations", component: Recommendations },
      {
        path: "/forbidden",
        component: Status,
        props: {
          title: "403 · 无权访问",
          text: "请联系团队负责人确认成员权限。",
        },
        meta: { public: true },
      },
      {
        path: "/unavailable",
        component: Status,
        props: {
          title: "暂时无法恢复登录状态",
          text: "请检查网络及后端服务，然后点击返回项目大厅重试。",
        },
        meta: { public: true },
      },
      {
        path: "/admin",
        component: Status,
        props: { title: "管理员入口", text: "统计看板由后续任务实现。" },
        meta: { roles: ["admin"] },
      },
      {
        path: "/:pathMatch(.*)*",
        component: Status,
        props: {
          title: "404 · 页面不存在",
          text: "请检查网址或返回项目大厅。",
        },
        meta: { public: true },
      },
    ],
  });
  router.beforeEach(async (to) => {
    if (!to.meta.public && auth.token && !auth.user) {
      try {
        auth.user = (await api("/profiles/me")).user;
      } catch (error) {
        if (error.status === 401) clearSession();
        else return error.status === 403 ? "/forbidden" : "/unavailable";
      }
    }
    return permissionDecision(to, auth);
  });
  return router;
}
export const router = makeRouter();
