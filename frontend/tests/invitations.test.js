import { beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import Invitations from "../src/views/Invitations.vue";
import { auth } from "../src/auth.js";

const { api, success } = vi.hoisted(() => ({
  api: vi.fn(),
  success: vi.fn(),
}));

vi.mock("../src/api/index.js", () => ({ api }));
vi.mock("element-plus", () => ({ ElMessage: { success } }));

const pending = {
  id: 9,
  team: 2,
  team_name: "智能学习计划助手",
  inviter: { username: "leader", display_name: "王队长" },
  message: "期待你加入前端开发",
  status: "pending",
};

const button = {
  template:
    '<button :disabled="loading || disabled" @click="$emit(\'click\')"><slot /></button>',
  props: ["loading", "disabled", "type"],
  emits: ["click"],
};

function screen() {
  return mount(Invitations, {
    global: {
      stubs: {
        ElButton: button,
        ElEmpty: {
          template: '<div class="empty">{{ description }}</div>',
          props: ["description"],
        },
      },
    },
  });
}

function click(wrapper, text) {
  return wrapper
    .findAll("button")
    .find((item) => item.text().includes(text))
    .trigger("click");
}

beforeEach(() => {
  api.mockReset();
  success.mockReset();
  auth.user = { id: 7, display_name: "林同学", team_id: null };
});

describe("邀请收件箱 #45", () => {
  it("展示团队、邀请人、留言与待处理状态", async () => {
    api.mockResolvedValue([pending]);
    const wrapper = screen();
    await flushPromises();
    expect(wrapper.text()).toContain("智能学习计划助手");
    expect(wrapper.text()).toContain("王队长");
    expect(wrapper.text()).toContain("期待你加入前端开发");
    expect(wrapper.text()).toContain("待处理");
  });

  it("接受后刷新本人团队信息并禁止重复操作", async () => {
    api
      .mockResolvedValueOnce([{ ...pending }])
      .mockResolvedValueOnce({ ...pending, status: "accepted" })
      .mockResolvedValueOnce({
        user: { id: 7, display_name: "林同学", team_id: 2 },
      });
    const wrapper = screen();
    await flushPromises();
    await click(wrapper, "接受并加入");
    await flushPromises();
    expect(api).toHaveBeenNthCalledWith(2, "/invitations/9/transition", {
      method: "POST",
      body: { action: "accept" },
    });
    expect(api).toHaveBeenNthCalledWith(3, "/profiles/me");
    expect(auth.user.team_id).toBe(2);
    expect(wrapper.text()).toContain("不能重复操作");
    expect(success).toHaveBeenCalledWith("已加入团队");
  });

  it("拒绝邀请后更新状态", async () => {
    api
      .mockResolvedValueOnce([{ ...pending }])
      .mockResolvedValueOnce({ ...pending, status: "rejected" });
    const wrapper = screen();
    await flushPromises();
    await click(wrapper, "拒绝");
    await flushPromises();
    expect(wrapper.text()).toContain("已拒绝");
    expect(success).toHaveBeenCalledWith("已拒绝邀请");
  });

  it("空列表显示明确空态", async () => {
    api.mockResolvedValue([]);
    const wrapper = screen();
    await flushPromises();
    expect(wrapper.get(".empty").text()).toContain("暂时没有收到团队邀请");
  });

  it.each([
    [403, "你没有操作权限"],
    [0, "网络连接失败，请检查网络或后端是否启动"],
  ])("加载失败时展示 %s 错误", async (status, message) => {
    api.mockRejectedValue(Object.assign(new Error(message), { status }));
    const wrapper = screen();
    await flushPromises();
    expect(wrapper.get('[role="alert"]').text()).toContain(message);
  });

  it("409 冲突后刷新服务端状态并隐藏操作按钮", async () => {
    api
      .mockResolvedValueOnce([{ ...pending }])
      .mockRejectedValueOnce(
        Object.assign(new Error("邀请已处理，请勿重复操作"), { status: 409 }),
      )
      .mockResolvedValueOnce([{ ...pending, status: "accepted" }]);
    const wrapper = screen();
    await flushPromises();
    await click(wrapper, "接受并加入");
    await flushPromises();
    expect(api).toHaveBeenLastCalledWith("/invitations");
    expect(wrapper.text()).toContain("已接受");
    expect(wrapper.text()).toContain("不能重复操作");
  });
});
