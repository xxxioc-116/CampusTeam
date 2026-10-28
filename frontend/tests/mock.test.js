import { beforeEach, describe, it, expect } from "vitest";
import { createClient } from "../src/api/client.js";
import { demoPassword, mockTransport } from "../src/api/mock.js";
let token, api;
beforeEach(() => {
  localStorage.clear();
  token = "";
  api = createClient({ transport: mockTransport, token: () => token });
});
async function login(username = "captain") {
  const data = await api("/auth/login", {
    method: "POST",
    body: { username, password: demoPassword },
  });
  token = data.access_token;
  return data;
}
describe("演示接口流程 #8–12（不代表真实后端验收）", () => {
  it("内置演示账号使用本页随机口令，拒绝其他口令", async () => {
    expect(demoPassword).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i,
    );
    await expect(
      api("/auth/login", {
        method: "POST",
        body: { username: "captain", password: crypto.randomUUID() },
      }),
    ).rejects.toMatchObject({ status: 401 });
    expect((await login()).user.username).toBe("captain");
  });
  it("拒绝无认证查询", async () =>
    await expect(api("/projects")).rejects.toMatchObject({ status: 401 }));
  it("注册默认学生、忽略提交的管理员角色", async () => {
    const data = await api("/auth/register", {
      method: "POST",
      body: {
        username: "new_user",
        password: crypto.randomUUID(),
        display_name: "新同学",
        role: "admin",
      },
    });
    expect(data.user.role).toBe("student");
    token = data.access_token;
    expect((await api("/profiles/me")).profile.abilities).toEqual([
      0, 0, 0, 0, 0,
    ]);
  });
  it("画像保存后回显", async () => {
    await login();
    const profile = (await api("/profiles/me")).profile;
    profile.bio = "做过 Vue 项目";
    profile.abilities = [100, 80, 60, 40, 20];
    await api("/profiles/me", { method: "PATCH", body: profile });
    expect((await api("/profiles/me")).profile).toMatchObject({
      bio: "做过 Vue 项目",
      abilities: [100, 80, 60, 40, 20],
    });
  });
  it("分页无重复且可筛选", async () => {
    await login();
    const a = await api("/projects?page=1&page_size=6"),
      b = await api("/projects?page=2&page_size=6");
    expect(a.count).toBe(17);
    expect(a.results).toHaveLength(6);
    expect(a.results.some((p) => b.results.some((q) => p.id === q.id))).toBe(
      false,
    );
    const filtered = await api("/projects?category=学科竞赛&skill=Python");
    expect(filtered.results.length).toBeGreaterThan(0);
    expect(
      filtered.results.every(
        (p) => p.category === "学科竞赛" && p.skills.includes("Python"),
      ),
    ).toBe(true);
  });
  it("空搜索结果", async () => {
    await login();
    expect((await api("/projects?search=不存在的名称")).results).toEqual([]);
  });
  it("拒绝非法页码", async () => {
    await login();
    await expect(api("/projects?page=0")).rejects.toMatchObject({
      status: 400,
    });
  });
  it("申请后防重复", async () => {
    await login();
    await api("/projects/1/applications", { method: "POST", body: {} });
    await expect(
      api("/projects/1/applications", { method: "POST", body: {} }),
    ).rejects.toMatchObject({ status: 409 });
    expect((await api("/projects")).results[0].applied).toBe(true);
  });
  it("不能申请已关闭项目", async () => {
    await login();
    await expect(
      api("/projects/17/applications", { method: "POST", body: {} }),
    ).rejects.toMatchObject({ status: 409 });
  });
  it("成员不能读取其他团队", async () => {
    await login("student");
    await expect(api("/teams/2/gaps")).rejects.toMatchObject({ status: 403 });
  });
  it("矩阵与缺口一致", async () => {
    await login();
    const matrix = await api("/teams/1/capability-matrix"),
      gaps = await api("/teams/1/gaps");
    const i = matrix.dimensions.indexOf("数据分析");
    expect(gaps.results[0].gap).toBe(matrix.required[i] - matrix.current[i]);
  });
  it("五维贡献等于总分，Top-K 有效", async () => {
    await login();
    const data = await api("/teams/1/recommendations?top_k=3");
    expect(data.results).toHaveLength(3);
    for (const item of data.results) {
      expect(item.score).toBeCloseTo(
        Object.keys(data.weights).reduce(
          (sum, k) => sum + data.weights[k] * item.scores[k],
          0,
        ),
      );
      expect(item.reasons.length).toBeGreaterThan(0);
    }
    expect(data.results[0].score).toBeGreaterThan(data.results[1].score);
  });
  it("学生不能邀请，队长可以且防重复", async () => {
    await login("student");
    await expect(
      api("/teams/1/invitations", {
        method: "POST",
        body: { candidate_id: 101 },
      }),
    ).rejects.toMatchObject({ status: 403 });
    await login();
    await api("/teams/1/invitations", {
      method: "POST",
      body: { candidate_id: 101 },
    });
    await expect(
      api("/teams/1/invitations", {
        method: "POST",
        body: { candidate_id: 101 },
      }),
    ).rejects.toMatchObject({ status: 409 });
    expect((await api("/teams/1/recommendations")).results[0].invited).toBe(
      true,
    );
  });
});
