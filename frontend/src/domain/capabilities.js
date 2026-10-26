export const dimensions = [
  "编程开发",
  "数据分析",
  "产品设计",
  "沟通协作",
  "项目管理",
];
export function bounded(value, max = 100) {
  const n = Number(value);
  return Number.isFinite(n) ? Math.max(0, Math.min(max, n)) : 0;
}
export function radarOption(matrix) {
  const labels = matrix.dimensions || [];
  return {
    tooltip: {},
    legend: { bottom: 0, data: ["团队当前", "项目需求"] },
    radar: {
      indicator: labels.map((name) => ({ name, max: 100 })),
      radius: "62%",
    },
    series: [
      {
        type: "radar",
        data: [
          {
            name: "团队当前",
            value: labels.map((_, i) => bounded(matrix.current?.[i])),
            areaStyle: { opacity: 0.15 },
          },
          {
            name: "项目需求",
            value: labels.map((_, i) => bounded(matrix.required?.[i])),
          },
        ],
      },
    ],
  };
}
export function validateProfile(p) {
  if (!p.display_name?.trim()) return "请填写姓名";
  if (p.display_name.length > 40) return "姓名不能超过 40 字";
  if (p.bio.length > 500) return "个人简介不能超过 500 字";
  if (
    p.abilities.length !== 5 ||
    p.abilities.some(
      (v) => !Number.isFinite(Number(v)) || Number(v) < 0 || Number(v) > 100,
    )
  )
    return "五维能力必须在 0–100 之间";
  if (p.availability.some((s) => !s.start || !s.end || s.start >= s.end))
    return "空闲时间的结束时间必须晚于开始时间；跨日请拆成两段";
  for (let i = 0; i < p.availability.length; i++)
    for (let j = i + 1; j < p.availability.length; j++) {
      const a = p.availability[i],
        b = p.availability[j];
      if (a.day === b.day && a.start < b.end && b.start < a.end)
        return "同一天的空闲时间不能重叠";
    }
  return "";
}
export const scoreLabels = {
  complement: "能力互补度",
  skill: "技能匹配度",
  time: "时间匹配度",
  goal: "目标一致性",
  experience: "经历匹配度",
};
