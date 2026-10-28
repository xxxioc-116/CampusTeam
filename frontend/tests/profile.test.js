import { beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import Profile from "../src/views/Profile.vue";

const { api, info } = vi.hoisted(() => ({ api: vi.fn(), info: vi.fn() }));

vi.mock("../src/api/index.js", () => ({ api }));
vi.mock("element-plus", () => ({
  ElMessage: { success: vi.fn(), info },
}));

const profile = {
  display_name: "加载后的姓名",
  bio: "加载后的简介",
  skills: ["Vue", "Python"],
  abilities: [10, 20, 30, 40, 50],
  goal: "竞赛获奖",
  experience: "课程项目",
  availability: [{ day: 2, start: "18:00", end: "20:00" }],
};

const button = {
  template:
    '<button :type="nativeType || type" :disabled="disabled || loading" @click="$emit(\'click\')"><slot /></button>',
  props: ["nativeType", "type", "disabled", "loading"],
  emits: ["click"],
};

function screen() {
  return mount(Profile, {
    global: {
      stubs: {
        ElButton: button,
        ElAlert: { template: "<div />" },
        ElEmpty: { template: "<div />" },
        ElSlider: {
          template: '<input class="ability" :value="modelValue" />',
          props: ["modelValue"],
        },
      },
    },
  });
}

beforeEach(() => {
  api.mockReset();
  info.mockReset();
});

describe("能力画像取消编辑 #9", () => {
  it("恢复最近一次从服务器加载的完整快照", async () => {
    api.mockResolvedValue({ profile });
    const wrapper = screen();
    await flushPromises();

    const textInputs = wrapper.findAll(
      'input:not([type="time"]):not(.ability)',
    );
    await textInputs[0].setValue("未保存的新姓名");
    await textInputs[1].setValue("React");
    await wrapper.find("textarea").setValue("未保存的新简介");
    await wrapper.get('button[type="button"]').trigger("click");
    await flushPromises();

    expect(textInputs[0].element.value).toBe("加载后的姓名");
    expect(textInputs[1].element.value).toBe("Vue, Python");
    expect(wrapper.find("textarea").element.value).toBe("加载后的简介");
    expect(
      wrapper.findAll(".ability").map((item) => item.element.value),
    ).toEqual(["10", "20", "30", "40", "50"]);
    expect(wrapper.find('input[aria-label="开始时间"]').element.value).toBe(
      "18:00",
    );
    expect(info).toHaveBeenCalledWith("已恢复最近一次保存的画像");
  });

  it("保存成功后把服务器响应更新为新的取消快照", async () => {
    const saved = { ...profile, display_name: "服务器保存后的姓名" };
    api
      .mockResolvedValueOnce({ profile })
      .mockResolvedValueOnce({ profile: saved });
    const wrapper = screen();
    await flushPromises();

    const name = wrapper.find('input:not([type="time"]):not(.ability)');
    await name.setValue("准备保存的姓名");
    await wrapper.find("form").trigger("submit");
    await flushPromises();
    expect(api).toHaveBeenLastCalledWith(
      "/profiles/me",
      expect.objectContaining({ method: "PATCH" }),
    );
    expect(name.element.value).toBe("服务器保存后的姓名");

    await name.setValue("再次产生未保存修改");
    await wrapper.get('button[type="button"]').trigger("click");
    expect(name.element.value).toBe("服务器保存后的姓名");
  });
});
