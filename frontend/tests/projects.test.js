import { beforeEach, describe, expect, it, vi } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import { nextTick } from "vue";
import Projects from "../src/views/Projects.vue";
const { api } = vi.hoisted(() => ({ api: vi.fn() }));
vi.mock("../src/api/index.js", () => ({
  api,
  isDemo: true,
  query: (params) => new URLSearchParams(params).toString(),
}));
vi.mock("element-plus", () => ({
  ElMessage: { success: vi.fn(), error: vi.fn() },
}));
function deferred() {
  let resolve, reject;
  const promise = new Promise((a, b) => {
    resolve = a;
    reject = b;
  });
  return { promise, resolve, reject };
}
const button = {
  template: '<button :disabled="disabled || loading"><slot /></button>',
  props: ["disabled", "loading"],
};
function screen() {
  return mount(Projects, {
    global: {
      stubs: {
        ElButton: button,
        ElTag: { template: "<span><slot /></span>" },
        ElEmpty: { template: "<div>暂无数据</div>" },
        ElPagination: {
          template:
            "<button @click=\"$emit('current-change',2)\">下一页</button>",
          emits: ["current-change"],
        },
        RouterLink: { template: "<a><slot /></a>" },
      },
    },
  });
}
const result = (title) => ({
  count: 12,
  results: [
    {
      id: 1,
      title,
      description: "介绍",
      category: "课程项目",
      skills: ["Vue"],
      member_count: 2,
      capacity: 5,
      status: "recruiting",
      applied: false,
    },
  ],
});
beforeEach(() => api.mockReset());
describe("大厅实际组件 #10", () => {
  it("只在筛选提交时请求，分页一次只发送一次请求", async () => {
    api.mockResolvedValue(result("第一页"));
    const wrapper = screen();
    await flushPromises();
    expect(api).toHaveBeenCalledTimes(1);
    await wrapper.find("input").setValue("校园");
    expect(api).toHaveBeenCalledTimes(1);
    await wrapper.find("form").trigger("submit");
    await flushPromises();
    expect(api).toHaveBeenCalledTimes(2);
    expect(api.mock.calls[1][0]).toContain("search=%E6%A0%A1%E5%9B%AD");
    await wrapper
      .findAll("button")
      .find((b) => b.text() === "下一页")
      .trigger("click");
    await flushPromises();
    expect(api).toHaveBeenCalledTimes(3);
    expect(api.mock.calls[2][0]).toContain("page=2");
    wrapper.unmount();
  });
  it("迟到的旧请求不能覆盖新结果", async () => {
    const first = deferred(),
      second = deferred();
    api.mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
    const wrapper = screen();
    await nextTick();
    await wrapper.find("input").setValue("新");
    await wrapper.find("form").trigger("submit");
    second.resolve(result("新结果"));
    await flushPromises();
    expect(wrapper.text()).toContain("新结果");
    first.resolve(result("旧结果"));
    await flushPromises();
    expect(wrapper.text()).toContain("新结果");
    expect(wrapper.text()).not.toContain("旧结果");
    wrapper.unmount();
  });
  it("错误提示后可重试", async () => {
    api
      .mockRejectedValueOnce(new Error("后端连接失败"))
      .mockResolvedValueOnce(result("恢复项目"));
    const wrapper = screen();
    await flushPromises();
    expect(wrapper.get('[role="alert"]').text()).toContain("后端连接失败");
    await wrapper
      .findAll("button")
      .find((b) => b.text() === "重新加载")
      .trigger("click");
    await flushPromises();
    expect(wrapper.text()).toContain("恢复项目");
    wrapper.unmount();
  });
  it("申请过程中锁定按钮，成功后保留已申请", async () => {
    const application = deferred();
    api
      .mockResolvedValueOnce(result("测试项目"))
      .mockReturnValueOnce(application.promise);
    const wrapper = screen();
    await flushPromises();
    const apply = wrapper
      .findAll("button")
      .find((b) => b.text() === "申请加入");
    await apply.trigger("click");
    expect(apply.element.disabled).toBe(true);
    expect(api).toHaveBeenCalledTimes(2);
    application.resolve({ status: "pending" });
    await flushPromises();
    expect(apply.text()).toBe("已申请");
    expect(apply.element.disabled).toBe(true);
    wrapper.unmount();
  });
});
