<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { auth } from "../auth.js";
import { api } from "../api/index.js";
import { dimensions, validateProfile } from "../domain/capabilities.js";
import AsyncState from "../components/AsyncState.vue";
const loading = ref(true),
  error = ref(""),
  saving = ref(false),
  saveError = ref(""),
  partial = ref(false), // 后端是否只支持部分字段（当前仅姓名）
  skillsText = ref("");
const form = reactive({
  display_name: "",
  bio: "",
  skills: [],
  abilities: [0, 0, 0, 0, 0],
  goal: "学习提升",
  experience: "",
  availability: [],
});
function apply(profile) {
  Object.assign(
    form,
    {
      display_name: "",
      bio: "",
      skills: [],
      abilities: [0, 0, 0, 0, 0],
      goal: "学习提升",
      experience: "",
      availability: [],
    },
    profile || {},
  );
  skillsText.value = form.skills.join(", ");
  partial.value = Boolean(profile?.backend_partial);
}
async function load() {
  loading.value = true;
  error.value = "";
  try {
    apply((await api("/profiles/me")).profile);
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
async function save() {
  if (saving.value) return;
  saveError.value = validateProfile(form);
  if (saveError.value) return;
  saving.value = true;
  try {
    const payload = {
      ...form,
      display_name: form.display_name.trim(),
      skills: [
        ...new Set(
          skillsText.value
            .split(/[,，]/)
            .map((s) => s.trim())
            .filter(Boolean),
        ),
      ],
    };
    const saved = await api("/profiles/me", { method: "PATCH", body: payload });
    apply(saved.profile);
    if (saved.user) auth.user = saved.user;
    ElMessage.success("画像已保存");
  } catch (e) {
    saveError.value = e.message;
  } finally {
    saving.value = false;
  }
}
onMounted(load);
</script>
<template>
  <div class="page-heading">
    <p class="eyebrow">YOUR CAPABILITIES</p>
    <h1>我的能力画像</h1>
    <p>让团队了解你的优势与期待。能力评分范围为 0–100。</p>
  </div>
  <AsyncState :loading="loading" :error="error" @retry="load"
    ><el-alert
      v-if="partial"
      type="warning"
      :closable="false"
      show-icon
      title="当前后端只开放姓名与简介字段"
      description="五维能力、技能标签、空闲时间等字段的接口尚未实现（依赖 #3），此处填写的内容刷新后不会保留。"
      style="margin-bottom: 16px"
    />
    <form class="profile-grid" @submit.prevent="save">
      <section class="panel">
        <h2>基本信息</h2>
        <label
          >姓名<input
            v-model="form.display_name"
            maxlength="40"
            required /></label
        ><label
          >个人简介<textarea
            v-model="form.bio"
            maxlength="500"
            rows="3"
          /></label
        ><label
          >技能标签（用逗号分隔）<input
            v-model="skillsText"
            placeholder="Vue, Python, Figma" /></label
        ><label
          >合作目标<select v-model="form.goal">
            <option>学习提升</option>
            <option>竞赛获奖</option>
            <option>作品落地</option>
            <option>科研探索</option>
          </select></label
        ><label
          >项目与竞赛经历<textarea
            v-model="form.experience"
            maxlength="2000"
            rows="3"
          />
        </label>
      </section>
      <section class="panel">
        <h2>五维能力</h2>
        <div v-for="(name, i) in dimensions" :key="name" class="ability-field">
          <span>{{ name }}</span>
          <el-slider
            v-model="form.abilities[i]"
            :min="0"
            :max="100"
            show-input
            :aria-label="name"
          />
        </div>
        <h2>每周空闲时间</h2>
        <p v-if="!form.availability.length" class="muted">
          尚未添加时间段。跨日时间请拆分。
        </p>
        <div v-for="(slot, i) in form.availability" :key="i" class="time-row">
          <select v-model.number="slot.day" :aria-label="`星期 ${i + 1}`">
            <option
              v-for="(day, j) in ['一', '二', '三', '四', '五', '六', '日']"
              :key="day"
              :value="j + 1"
            >
              周{{ day }}
            </option></select
          ><input
            v-model="slot.start"
            type="time"
            aria-label="开始时间"
            required
          /><input
            v-model="slot.end"
            type="time"
            aria-label="结束时间"
            required
          /><el-button @click="form.availability.splice(i, 1)">删除</el-button>
        </div>
        <el-button
          @click="
            form.availability.push({ day: 1, start: '18:00', end: '20:00' })
          "
          >添加时间段</el-button
        >
      </section>
      <div class="save-bar">
        <p v-if="saveError" role="alert" class="error">{{ saveError }}</p>
        <el-button native-type="submit" type="primary" :loading="saving"
          >保存画像</el-button
        >
      </div>
    </form></AsyncState
  >
</template>
