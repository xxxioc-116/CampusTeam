<script setup>
import { onMounted, onBeforeUnmount, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { api, isDemo, query } from "../api/index.js";
import { STATUS_LABEL } from "../api/adapters.js";
import AsyncState from "../components/AsyncState.vue";
const filters = reactive({ search: "", category: "", skill: "" }),
  applied = ref({ search: "", category: "", skill: "" });
const projects = ref([]),
  count = ref(0),
  page = ref(1),
  loading = ref(false),
  error = ref(""),
  applying = ref(new Set());
let controller,
  sequence = 0;
async function load() {
  const id = ++sequence;
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = "";
  try {
    const data = await api(
      "/projects?" +
        query({ ...applied.value, page: page.value, page_size: 6 }),
      { signal: controller.signal },
    );
    if (id === sequence) {
      projects.value = data.results;
      count.value = data.count;
    }
  } catch (e) {
    if (id === sequence && e.name !== "AbortError") error.value = e.message;
  } finally {
    if (id === sequence) loading.value = false;
  }
}
function search() {
  applied.value = { ...filters };
  page.value = 1;
  load();
}
function changePage(value) {
  page.value = value;
  load();
}
async function apply(project) {
  if (applying.value.has(project.id) || project.applied) return;
  applying.value.add(project.id);
  try {
    await api(`/projects/${project.id}/applications`, {
      method: "POST",
      body: { message: "希望加入项目，共同完成目标。" },
    });
    project.applied = true;
    ElMessage.success("申请已提交，等待负责人审核");
  } catch (e) {
    ElMessage.error(e.message);
  } finally {
    applying.value.delete(project.id);
  }
}
onMounted(load);
onBeforeUnmount(() => {
  sequence++;
  controller?.abort();
});
</script>
<template>
  <div class="page-heading">
    <p class="eyebrow">FIND YOUR NEXT CHALLENGE</p>
    <h1>项目大厅</h1>
    <p>发现值得投入的想法，找到需要你的团队。</p>
  </div>
  <form class="panel filters" @submit.prevent="search">
    <label
      >搜索项目<input
        v-model.trim="filters.search"
        placeholder="项目名称或简介" /></label
    ><label
      >项目类型<select v-model="filters.category">
        <option value="">全部类型</option>
        <option>课程项目</option>
        <option>学科竞赛</option>
        <option>创新创业</option>
      </select></label
    ><label
      >技能<input
        v-model.trim="filters.skill"
        placeholder="例如 Vue"
        :disabled="!isDemo" /></label
    ><el-button native-type="submit" type="primary">筛选</el-button>
    <p v-if="!isDemo" class="muted">
      真实后端暂只支持关键词与项目类型筛选，技能筛选待 #4 补齐。
    </p>
  </form>
  <div class="result-heading">
    <span>共 {{ count }} 个项目</span
    ><span class="muted">寻找互补，一起成长</span>
  </div>
  <AsyncState
    :loading="loading"
    :error="error"
    :empty="!projects.length"
    @retry="load"
    ><div class="project-grid">
      <article
        v-for="project in projects"
        :key="project.id"
        class="panel project-card"
      >
        <div>
          <el-tag>{{ project.category }}</el-tag
          ><span class="project-id">#{{ project.id }}</span>
        </div>
        <h2>{{ project.title }}</h2>
        <p>{{ project.description }}</p>
        <div class="tags" v-if="project.skills.length">
          <el-tag v-for="skill in project.skills" :key="skill" type="info">{{
            skill
          }}</el-tag>
        </div>
        <p class="muted">
          {{ project.member_count ?? "—" }} / {{ project.capacity }} 人 ·
          {{ STATUS_LABEL[project.status] || project.status }}
        </p>
        <div class="card-actions">
          <el-button
            type="primary"
            :disabled="project.applied || project.status !== 'recruiting'"
            :loading="applying.has(project.id)"
            @click="apply(project)"
            >{{ project.applied ? "已申请" : "申请加入" }}</el-button
          ><router-link
            v-if="project.can_view_team"
            :to="`/teams/${project.team_id}`"
            >查看团队 →</router-link
          >
        </div>
      </article>
    </div></AsyncState
  ><el-pagination
    v-if="count > 6"
    :current-page="page"
    :page-size="6"
    :total="count"
    layout="prev, pager, next"
    @current-change="changePage"
  />
</template>
