import { describe, expect, it } from "vitest";
import {
  adaptError,
  adaptRequest,
  adaptResponse,
  emptyProfile,
  splitPath,
} from "../src/api/adapters.js";
import { ApiError } from "../src/api/client.js";
import { canManageTeam, setSession, auth } from "../src/auth.js";

describe("后端适配 #7–#12", () => {
  it("拆分路径与查询参数", () => {
    const { pathname, params } = splitPath("/projects?search=校园&page=2");
    expect(pathname).toBe("/projects");
    expect(params.get("search")).toBe("校园");
    expect(params.get("page")).toBe("2");
  });

  it("项目检索参数映射为后端的 keyword/type，并丢弃未支持的 skill", () => {
    const { path } = adaptRequest(
      "/projects?search=低碳&category=课程项目&skill=Vue&page=1&page_size=6",
    );
    const params = new URLSearchParams(path.split("?")[1]);
    expect(params.get("keyword")).toBe("低碳");
    expect(params.get("type")).toBe("course");
    expect(params.get("page")).toBe("1");
    expect(params.has("skill")).toBe(false);
  });

  it("邀请请求体从 candidate_id 改为 invitee_id", () => {
    const { options } = adaptRequest("/teams/1/invitations", {
      method: "POST",
      body: { candidate_id: 101, message: "邀请" },
    });
    expect(options.body).toEqual({ invitee_id: 101, message: "邀请" });
  });

  it("画像 PATCH 保留真实后端支持的完整画像", () => {
    const { options } = adaptRequest("/profiles/me", {
      method: "PATCH",
      body: { display_name: "林同学", bio: "简介", abilities: [1, 2, 3, 4, 5] },
    });
    expect(options.body).toEqual({
      display_name: "林同学",
      bio: "简介",
      abilities: [1, 2, 3, 4, 5],
    });
  });

  it("真实画像响应直接回显服务器保存的数据", () => {
    const profile = {
      display_name: "真实画像",
      abilities: [80, 40, 60, 70, 50],
      skills: ["Python"],
    };
    const data = adaptResponse("/profiles/me", {
      user: { id: 1, team_id: 3 },
      profile,
    });
    expect(data.profile).toEqual(profile);
    expect(data.profile.backend_partial).toBeUndefined();
    expect(data.user.team_id).toBe(3);
  });

  it("项目响应映射为页面字段，缺失值给安全默认", () => {
    const data = adaptResponse("/projects", {
      count: 1,
      results: [
        {
          id: 3,
          title: "校园低碳出行地图",
          description: "简介",
          project_type: "course",
          status: "recruiting",
          max_members: 5,
          owner: {
            id: 9,
            username: "owner",
            display_name: "负责人",
            role: "leader",
          },
        },
      ],
    });
    expect(data.count).toBe(1);
    expect(data.results[0]).toMatchObject({
      id: 3,
      category: "课程项目",
      capacity: 5,
      member_count: null,
      skills: [],
      team_id: null,
      can_view_team: false,
      applied: false,
    });
  });

  it("兼容后端未分页的数组响应", () => {
    const data = adaptResponse("/projects", [
      { id: 1, title: "A", description: "", project_type: "competition" },
    ]);
    expect(data.count).toBe(1);
    expect(data.results[0].category).toBe("学科竞赛");
  });

  it("登录响应把 token 统一成 access_token", () => {
    const data = adaptResponse("/auth/login", {
      token: "abc",
      user: {
        id: 1,
        username: "student",
        display_name: "林同学",
        role: "student",
      },
    });
    expect(data.access_token).toBe("abc");
    expect(data.user.team_id).toBeNull();
  });

  it("画像响应包装成 user/profile，并标记字段不完整", () => {
    const data = adaptResponse("/profiles/me", {
      id: 1,
      username: "student",
      display_name: "林同学",
      role: "student",
    });
    expect(data.profile.display_name).toBe("林同学");
    expect(data.profile.abilities).toEqual(emptyProfile().abilities);
    expect(data.profile.backend_partial).toBe(true);
  });

  it("已实现的团队接口保留真实 404 错误", () => {
    const friendly = adaptError(
      "/teams/1/capability-matrix",
      new ApiError("内容不存在", 404),
    );
    expect(friendly.status).toBe(404);
    expect(friendly.message).toContain("内容不存在");
    const passthrough = adaptError(
      "/projects",
      new ApiError("内容不存在", 404),
    );
    expect(passthrough.status).toBe(404);
  });
});

describe("角色与登录态兼容", () => {
  it("队长角色同时接受 leader 与 captain", () => {
    expect(canManageTeam("leader")).toBe(true);
    expect(canManageTeam("captain")).toBe(true);
    expect(canManageTeam("admin")).toBe(true);
    expect(canManageTeam("student")).toBe(false);
  });

  it("setSession 接受后端 token 字段", () => {
    setSession({ token: "t1", user: { id: 1, role: "leader" } });
    expect(auth.token).toBe("t1");
    expect(auth.user.role).toBe("leader");
  });

  it("缺少令牌时报错", () => {
    expect(() => setSession({ user: { id: 1 } })).toThrow("令牌");
  });
});
