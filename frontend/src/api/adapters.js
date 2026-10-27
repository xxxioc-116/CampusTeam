import { ApiError } from "./client.js";

/**
 * 后端适配层：把 Django（codex/backend-owner-tasks 分支）的真实响应
 * 转换成页面期望的结构。演示模式下本文件不生效。
 *
 * 为什么要这一层：后端字段目前与 docs/frontend-api-contract.md 有差异，
 * 直接改页面会导致后端一升级字段就要重写 UI。适配层集中处理差异，
 * 后端补齐后只需删掉对应映射。
 */

const TYPE_LABEL = {
  course: "课程项目",
  competition: "学科竞赛",
  innovation: "创新创业",
};
const TYPE_CODE = Object.fromEntries(
  Object.entries(TYPE_LABEL).map(([code, label]) => [label, code]),
);
export const STATUS_LABEL = {
  recruiting: "招募中",
  active: "进行中",
  closed: "已结束",
};

// 后端尚未提供的接口（见 docs/frontend-backend-alignment.md）
const UNSUPPORTED = [
  /^\/teams\/[^/]+\/capability-matrix$/,
  /^\/teams\/[^/]+\/gaps$/,
  /^\/teams\/[^/]+\/recommendations/,
];

export function splitPath(path) {
  const [pathname, search = ""] = path.split("?");
  return { pathname, params: new URLSearchParams(search) };
}

export function emptyProfile() {
  return {
    display_name: "",
    bio: "",
    skills: [],
    abilities: [0, 0, 0, 0, 0],
    goal: "学习提升",
    experience: "",
    availability: [],
  };
}

function normalizeUser(user = {}) {
  return {
    id: user.id,
    username: user.username,
    display_name: user.display_name || user.username || "",
    role: user.role,
    team_id: user.team_id ?? null,
  };
}

function normalizeProject(project) {
  return {
    id: project.id,
    title: project.title,
    description: project.description,
    category: TYPE_LABEL[project.project_type] || project.project_type || "",
    skills: (project.skills || []).map((s) =>
      typeof s === "string" ? s : s.name,
    ),
    member_count: project.member_count ?? null,
    capacity: project.max_members ?? project.capacity ?? 0,
    status: project.status,
    team_id: project.team_id ?? null,
    can_view_team: Boolean(project.can_view_team),
    applied: Boolean(project.applied),
    owner: project.owner ? normalizeUser(project.owner) : null,
  };
}

/** 请求侧：路径与参数名映射 */
export function adaptRequest(path, options = {}) {
  const { pathname, params } = splitPath(path);
  let nextPath = path;
  let { body } = options;

  // 项目检索：search→keyword、category→type、skill 后端未实现
  if (pathname === "/projects") {
    const mapped = new URLSearchParams();
    const keys = { search: "keyword", category: "type", status: "status" };
    params.forEach((value, key) => {
      if (!value) return;
      if (key === "page" || key === "page_size") {
        mapped.set(key, value);
        return;
      }
      const target = keys[key];
      if (!target) return; // skill 等后端未支持的筛选直接丢弃
      mapped.set(
        target,
        key === "category" ? TYPE_CODE[value] || value : value,
      );
    });
    const search = mapped.toString();
    nextPath = search ? `/projects?${search}` : "/projects";
  }

  // 邀请：前端用 candidate_id，后端字段是 invitee_id
  if (/^\/teams\/[^/]+\/invitations$/.test(pathname) && body) {
    body = {
      invitee_id: body.candidate_id ?? body.invitee_id,
      message: body.message || "",
    };
  }

  // 画像：后端 UserSerializer 只接受 display_name
  if (pathname === "/profiles/me" && options.method === "PATCH" && body) {
    body = { display_name: body.display_name };
  }

  return { path: nextPath, options: { ...options, body } };
}

/** 响应侧：后端结构 → 页面结构 */
export function adaptResponse(path, data, options = {}) {
  const { pathname } = splitPath(path);

  if (pathname === "/auth/login" || pathname === "/auth/register") {
    return {
      access_token: data.access_token || data.token,
      user: normalizeUser(data.user),
    };
  }

  if (pathname === "/profiles/me") {
    const user = normalizeUser(data.user || data);
    if (options.method === "PATCH") {
      return {
        user,
        profile: {
          ...emptyProfile(),
          ...options.body,
          display_name: user.display_name,
          backend_partial: true,
        },
      };
    }
    return {
      user,
      profile: {
        ...emptyProfile(),
        display_name: user.display_name,
        backend_partial: true,
      },
    };
  }

  if (pathname === "/projects") {
    const results = Array.isArray(data) ? data : data.results || [];
    return {
      count: Array.isArray(data)
        ? results.length
        : (data.count ?? results.length),
      results: results.map(normalizeProject),
    };
  }

  return data;
}

/** 错误侧：把“后端还没有这个接口”翻译成可读文案 */
export function adaptError(path, error) {
  const { pathname } = splitPath(path);
  if (error.status === 404 && UNSUPPORTED.some((re) => re.test(pathname)))
    return new ApiError(
      "该接口后端尚未实现（团队能力矩阵/缺口/推荐依赖 #5、#13–#18），当前请在演示模式下查看",
      501,
    );
  return error;
}
