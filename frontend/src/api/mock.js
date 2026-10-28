// 本文件仅供演示，不能替代后端认证、权限与推荐服务。
import { dimensions, validateProfile } from "../domain/capabilities.js";
export const demoPassword = crypto.randomUUID();
const accounts = new Map(
  ["student", "captain", "admin"].map((name, i) => [
    name,
    {
      password: demoPassword,
      user: {
        id: i + 1,
        username: name,
        display_name: ["林同学", "陈队长", "管理员"][i],
        role: name === "student" ? "student" : name,
        team_id: 1,
      },
    },
  ]),
);
const key = "ct-demo-v1";
function initial() {
  return { profiles: {}, applications: [], invitations: [], sessions: {} };
}
function read() {
  try {
    return JSON.parse(localStorage.getItem(key)) || initial();
  } catch {
    return initial();
  }
}
function write(state) {
  localStorage.setItem(key, JSON.stringify(state));
}
const categories = ["课程项目", "学科竞赛", "科研训练", "创新创业"];
const titles = [
  "校园低碳出行地图",
  "智能学习计划助手",
  "非遗数字展览",
  "校园二手物品平台",
  "图书馆座位分析",
  "机器人视觉挑战",
  "校园心理关怀工具",
  "社区志愿服务平台",
  "科研文献知识图谱",
  "智慧食堂排队预测",
  "校园活动推荐",
  "无障碍校园导航",
  "可持续包装设计",
  "课堂互动小助手",
  "大学生创新工作坊",
  "开源社团主页",
  "多模态笔记工具",
];
export const projects = titles.map((title, i) => ({
  id: i + 1,
  title,
  category: categories[i % 4],
  description:
    "面向校园真实场景，寻找愿意共同调研、设计与开发的伙伴。用一个学期把想法做成可展示的作品。",
  skills: i % 2 ? ["Python", "数据分析"] : ["Vue", "产品设计"],
  capacity: 5,
  member_count: 2 + (i % 3),
  status: i === 16 ? "closed" : "recruiting",
  team_id: i + 1,
}));
const weights = {
  complement: 0.35,
  skill: 0.25,
  time: 0.2,
  goal: 0.1,
  experience: 0.1,
};
function recommendations() {
  return Array.from({ length: 8 }, (_, i) => {
    const scores = {
      complement: 95 - i * 5,
      skill: 90 - i * 4,
      time: 85 - i * 3,
      goal: 90 - i * 2,
      experience: 80 - i * 4,
    };
    return {
      id: 101 + i,
      display_name: [
        "许同学",
        "王同学",
        "李同学",
        "赵同学",
        "周同学",
        "吴同学",
        "郑同学",
        "孙同学",
      ][i],
      skills: ["数据分析", "Python"],
      scores,
      score: Object.keys(weights).reduce(
        (s, k) => s + scores[k] * weights[k],
        0,
      ),
      reasons: [
        "数据分析能力可补齐项目当前缺口",
        "目标与团队的作品落地方向一致",
      ],
      risks: i % 2 ? ["周末时间重合较少，建议先确认协作安排"] : [],
    };
  });
}
function reply(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
function fail(message, status = 400, details = {}) {
  return reply({ code: "DEMO_ERROR", message, details }, status);
}
function defaultProfile(user) {
  return {
    display_name: user.display_name,
    bio: "",
    skills: [],
    abilities: [0, 0, 0, 0, 0],
    goal: "学习提升",
    experience: "",
    availability: [],
  };
}
export async function mockTransport(url, options = {}) {
  await new Promise((resolve, reject) => {
    if (options.signal?.aborted) {
      reject(new DOMException("请求已取消", "AbortError"));
      return;
    }
    const abort = () => {
      clearTimeout(timer);
      reject(new DOMException("请求已取消", "AbortError"));
    };
    const timer = setTimeout(() => {
      options.signal?.removeEventListener("abort", abort);
      resolve();
    }, 100);
    options.signal?.addEventListener("abort", abort, { once: true });
  });
  const parsed = new URL(url, "https://demo.local"),
    path = parsed.pathname.replace(/^.*\/api\/v1/, "").replace(/\/$/, ""),
    method = options.method || "GET";
  const state = read(),
    body = options.body ? JSON.parse(options.body) : {};
  if (path === "/auth/login" || path === "/auth/register") {
    if (method !== "POST") return fail("不支持的方法", 405);
    let account = accounts.get(body.username);
    if (path.endsWith("register")) {
      if (account) return fail("用户名已存在", 409);
      if (
        !/^[a-zA-Z0-9_]{3,30}$/.test(body.username) ||
        typeof body.password !== "string" ||
        body.password.length < 8 ||
        !body.display_name?.trim()
      )
        return fail("注册信息不合法");
      account = {
        password: body.password,
        user: {
          id: crypto.randomUUID(),
          username: body.username,
          display_name: body.display_name,
          role: "student",
          team_id: null,
        },
      };
      accounts.set(body.username, account);
    } else if (!account || account.password !== body.password)
      return fail("用户名或密码错误", 401);
    const token = crypto.randomUUID();
    state.sessions[token] = account.user;
    write(state);
    return reply({ access_token: token, user: account.user });
  }
  // 兼容 Token / Bearer 两种认证前缀（后端用 Token）
  const token = options.headers?.Authorization?.replace(/^(Token|Bearer) /, ""),
    user = state.sessions[token];
  if (!user) return fail("登录已失效，请重新登录", 401);
  if (path === "/profiles/me") {
    if (method === "PATCH") {
      const problem = validateProfile(body);
      if (problem) return fail(problem);
      state.profiles[user.id] = body;
      user.display_name = body.display_name;
      write(state);
    } else if (method !== "GET") return fail("不支持的方法", 405);
    return reply({
      user,
      profile: state.profiles[user.id] || defaultProfile(user),
    });
  }
  if (path === "/projects" && method === "GET") {
    const q = parsed.searchParams,
      page = Number(q.get("page") || 1),
      size = Number(q.get("page_size") || 6);
    if (
      !Number.isInteger(page) ||
      page < 1 ||
      !Number.isInteger(size) ||
      size < 1 ||
      size > 100
    )
      return fail("分页参数无效");
    const list = projects
      .filter(
        (p) =>
          (!q.get("category") || p.category === q.get("category")) &&
          (!q.get("skill") ||
            p.skills.some((s) =>
              s.toLowerCase().includes(q.get("skill").toLowerCase()),
            )) &&
          (!q.get("search") ||
            (p.title + p.description).includes(q.get("search"))),
      )
      .map((p) => ({
        ...p,
        applied: state.applications.includes(`${user.id}:${p.id}`),
        can_view_team: user.role === "admin" || user.team_id === p.team_id,
      }));
    return reply({
      count: list.length,
      results: list.slice((page - 1) * size, page * size),
    });
  }
  const application = path.match(/^\/projects\/(\d+)\/applications$/);
  if (application && method === "POST") {
    const project = projects.find((p) => p.id === Number(application[1]));
    if (!project) return fail("项目不存在", 404);
    if (project.status !== "recruiting") return fail("项目已结束招募", 409);
    const id = `${user.id}:${project.id}`;
    if (state.applications.includes(id))
      return fail("已申请，请勿重复提交", 409);
    state.applications.push(id);
    write(state);
    return reply({ id: state.applications.length, status: "pending" }, 201);
  }
  const team = path.match(
    /^\/teams\/(\d+)\/(capability-matrix|gaps|recommendations|invitations)$/,
  );
  if (team) {
    const id = Number(team[1]),
      action = team[2];
    if (!projects.some((p) => p.team_id === id)) return fail("团队不存在", 404);
    if (user.role !== "admin" && user.team_id !== id)
      return fail("只有本团队成员可以查看", 403);
    if (action === "invitations" && method === "POST") {
      if (!["captain", "admin"].includes(user.role))
        return fail("只有负责人可以邀请", 403);
      if (!recommendations().some((c) => c.id === body.candidate_id))
        return fail("候选人不存在", 404);
      const item = `${id}:${body.candidate_id}`;
      if (state.invitations.includes(item))
        return fail("已邀请，请勿重复提交", 409);
      state.invitations.push(item);
      write(state);
      return reply({ status: "pending" }, 201);
    }
    if (method !== "GET") return fail("不支持的方法", 405);
    if (action === "capability-matrix")
      return reply({
        team_name: "低碳校园实验室",
        dimensions,
        current: [80, 45, 70, 85, 60],
        required: [85, 80, 75, 80, 75],
        members: [
          { id: 1, display_name: "林同学", abilities: [80, 30, 70, 65, 45] },
          { id: 2, display_name: "陈队长", abilities: [65, 45, 55, 85, 60] },
        ],
      });
    if (action === "gaps")
      return reply({
        results: [
          {
            dimension: "数据分析",
            gap: 35,
            explanation: "当前 45 / 需求 80，优先寻找数据分析伙伴。",
          },
          {
            dimension: "项目管理",
            gap: 15,
            explanation: "当前 60 / 需求 75，建议补齐里程碑规划能力。",
          },
          { dimension: "编程开发", gap: 5, explanation: "当前 80 / 需求 85。" },
          { dimension: "产品设计", gap: 5, explanation: "当前 70 / 需求 75。" },
        ],
      });
    if (action === "recommendations") {
      const k = Number(parsed.searchParams.get("top_k") || 5);
      if (!Number.isInteger(k) || k < 1 || k > 50)
        return fail("top_k 必须为 1–50 的整数");
      return reply({
        project_id: id,
        weight_version: "demo-baseline-v1",
        weights,
        applied: state.applications.includes(`${user.id}:${id}`),
        results: recommendations()
          .slice(0, k)
          .map((c) => ({
            ...c,
            invited: state.invitations.includes(`${id}:${c.id}`),
          })),
      });
    }
  }
  return fail("演示接口不存在", 404);
}
