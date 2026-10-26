<script setup>
import { onMounted, onBeforeUnmount, ref } from "vue";
import { useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import { auth, canManageTeam } from "../auth.js";
import { api } from "../api/index.js";
import { bounded, scoreLabels } from "../domain/capabilities.js";
import AsyncState from "../components/AsyncState.vue";
const route = useRoute(),
  data = ref(null),
  loading = ref(true),
  error = ref(""),
  topK = ref(5),
  busy = ref(new Set());
let controller,
  sequence = 0;
async function load() {
  const id = ++sequence;
  controller?.abort();
  controller = new AbortController();
  loading.value = true;
  error.value = "";
  try {
    const response = await api(
      `/teams/${route.params.id}/recommendations?top_k=${topK.value}`,
      { signal: controller.signal },
    );
    if (id === sequence) data.value = response;
  } catch (e) {
    if (id === sequence && e.name !== "AbortError") error.value = e.message;
  } finally {
    if (id === sequence) loading.value = false;
  }
}
onBeforeUnmount(() => {
  sequence++;
  controller?.abort();
});
async function invite(candidate) {
  if (busy.value.has(candidate.id) || candidate.invited) return;
  busy.value.add(candidate.id);
  try {
    await api(`/teams/${route.params.id}/invitations`, {
      method: "POST",
      body: {
        candidate_id: candidate.id,
        message: "邀请你加入团队，一起补齐能力拼图。",
      },
    });
    candidate.invited = true;
    ElMessage.success("邀请已发送");
  } catch (e) {
    ElMessage.error(e.message);
  } finally {
    busy.value.delete(candidate.id);
  }
}
async function apply() {
  if (busy.value.has("apply") || data.value.applied) return;
  busy.value.add("apply");
  try {
    await api(`/projects/${data.value.project_id}/applications`, {
      method: "POST",
      body: { message: "希望加入团队" },
    });
    data.value.applied = true;
    ElMessage.success("申请已提交");
  } catch (e) {
    ElMessage.error(e.message);
  } finally {
    busy.value.delete("apply");
  }
}
onMounted(load);
</script>
<template>
  <div class="page-heading">
    <p class="eyebrow">EXPLAINABLE MATCHING</p>
    <h1>找到团队的下一块拼图</h1>
    <p>了解每一项得分的来源，再决定与谁同行。</p>
    <router-link :to="`/teams/${route.params.id}`">← 返回团队分析</router-link>
  </div>
  <div class="panel result-heading">
    <label
      >推荐人数<select v-model.number="topK" @change="load">
        <option :value="3">Top 3</option>
        <option :value="5">Top 5</option>
        <option :value="10">Top 10</option>
      </select></label
    ><span class="muted">分数越高越匹配，仍需线下沟通确认</span>
  </div>
  <AsyncState
    :loading="loading"
    :error="error"
    :empty="!data?.results?.length"
    @retry="load"
    ><p class="muted">
      权重版本：{{ data.weight_version }} · 各项得分 0–100，贡献 = 分数 × 权重
    </p>
    <article
      v-for="(candidate, i) in data.results"
      :key="candidate.id"
      class="panel recommendation"
    >
      <div class="candidate-head">
        <div class="avatar">{{ candidate.display_name.slice(0, 1) }}</div>
        <div>
          <span class="eyebrow"
            >MATCH {{ String(i + 1).padStart(2, "0") }}</span
          >
          <h2>{{ candidate.display_name }}</h2>
          <div class="tags">
            <el-tag v-for="skill in candidate.skills" :key="skill">{{
              skill
            }}</el-tag>
          </div>
        </div>
        <div class="score">
          <strong>{{ bounded(candidate.score).toFixed(1) }}</strong
          ><span>综合匹配分</span>
        </div>
      </div>
      <div class="recommendation-body">
        <div>
          <h3>五维分项与贡献</h3>
          <div class="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>评分维度</th>
                  <th>分数</th>
                  <th>权重</th>
                  <th>贡献</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(label, key) in scoreLabels" :key="key">
                  <td>{{ label }}</td>
                  <td>{{ bounded(candidate.scores[key]) }}</td>
                  <td>
                    {{ (bounded(data.weights[key], 1) * 100).toFixed(0) }}%
                  </td>
                  <td>
                    {{
                      (
                        bounded(candidate.scores[key]) *
                        bounded(data.weights[key], 1)
                      ).toFixed(1)
                    }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div>
          <h3>为什么推荐 TA</h3>
          <ul>
            <li v-for="reason in candidate.reasons" :key="reason">
              {{ reason }}
            </li>
          </ul>
          <h3>需要沟通的风险</h3>
          <p v-if="!candidate.risks.length" class="muted">
            暂无已识别风险；建议确认时间与合作目标。
          </p>
          <p v-for="risk in candidate.risks" :key="risk" class="risk">
            {{ risk }}
          </p>
          <el-button
            v-if="canManageTeam(auth.user?.role)"
            type="primary"
            :disabled="candidate.invited"
            :loading="busy.has(candidate.id)"
            @click="invite(candidate)"
            >{{ candidate.invited ? "已邀请" : "邀请加入团队" }}</el-button
          >
          <p v-else class="muted">邀请由团队负责人发送。</p>
        </div>
      </div>
    </article>
    <section class="panel">
      <h2>希望加入这个项目？</h2>
      <p>提交申请后等待负责人审核，提交不会立即改变团队能力。</p>
      <el-button
        :disabled="data.applied"
        :loading="busy.has('apply')"
        @click="apply"
        >{{ data.applied ? "已提交申请" : "申请加入项目" }}</el-button
      >
    </section></AsyncState
  >
</template>
