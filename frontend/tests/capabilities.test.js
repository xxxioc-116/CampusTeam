import { describe, it, expect } from "vitest";
import {
  bounded,
  radarOption,
  validateProfile,
} from "../src/domain/capabilities.js";
const profile = () => ({
  display_name: "林同学",
  bio: "",
  abilities: [0, 100, 50, 60, 70],
  availability: [],
});
describe("画像 #9", () => {
  it("允许空时间与能力边界", () => expect(validateProfile(profile())).toBe(""));
  it("拒绝空姓名", () =>
    expect(validateProfile({ ...profile(), display_name: " " })).toContain(
      "姓名",
    ));
  it("拒绝越界或缺失能力", () => {
    expect(
      validateProfile({ ...profile(), abilities: [101, 2, 3, 4, 5] }),
    ).toContain("0–100");
    expect(validateProfile({ ...profile(), abilities: [] })).toContain("五维");
  });
  it("跨日时间提示拆分", () =>
    expect(
      validateProfile({
        ...profile(),
        availability: [{ day: 1, start: "23:00", end: "01:00" }],
      }),
    ).toContain("跨日"));
  it("拒绝同日重叠时间，允许相邻时间", () => {
    const availability = [
      { day: 1, start: "18:00", end: "20:00" },
      { day: 1, start: "19:00", end: "21:00" },
    ];
    expect(validateProfile({ ...profile(), availability })).toContain("重叠");
    availability[1].start = "20:00";
    expect(validateProfile({ ...profile(), availability })).toBe("");
  });
});
describe("雷达图映射 #11", () => {
  it("夹紧极值并将缺失值显示为零", () => {
    const option = radarOption({
      dimensions: ["A", "B", "C"],
      current: [-1, 200],
      required: [NaN, 0, 100],
    });
    expect(option.series[0].data[0].value).toEqual([0, 100, 0]);
    expect(option.series[0].data[1].value).toEqual([0, 0, 100]);
    expect(option.radar.indicator.every((x) => x.max === 100)).toBe(true);
  });
  it("空维度不制造虚假数据", () =>
    expect(radarOption({}).radar.indicator).toEqual([]));
  it("非数值归零", () => expect(bounded("bad")).toBe(0));
});
