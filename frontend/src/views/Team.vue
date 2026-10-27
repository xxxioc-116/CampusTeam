<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { api } from "../api/index.js";
import { bounded } from "../domain/capabilities.js";
import RadarChart from "../components/RadarChart.vue";
import AsyncState from "../components/AsyncState.vue";
const route = useRoute(),
  matrix = ref(null),
  gaps = ref([]),
  loading = ref(true),
  error = ref("");
async function load() {
  loading.value = true;
  error.value = "";
  try {
    const [m, g] = await Promise.all([
      api(`/teams/${route.params.id}/capability-matrix`),
      api(`/teams/${route.params.id}/gaps`),
    ]);
    matrix.value = m;
    gaps.value = g.results;
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
onMounted(load);
</script>
<template>
  <div class="page-heading">
    <p class="eyebrow">TEAM INSIGHTS</p>
    <h1>团队能力分析</h1>
    <p>结合当前能力与项目需求，识别下一位伙伴应补齐的方向。</p>
  </div>
  <AsyncState
    :loading="loading"
    :error="error"
    :empty="!matrix?.dimensions?.length"
    @retry="load"
    ><div class="analysis-grid">
      <section class="panel">
        <h2>{{ matrix.team_name }} · 能力雷达</h2>
        <RadarChart :matrix="matrix" />
        <div class="table-scroll">
          <table>
            <thead>
              <tr>
                <th>能力维度</th>
                <th>当前</th>
                <th>需求</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(name, i) in matrix.dimensions" :key="name">
                <td>{{ name }}</td>
                <td>{{ bounded(matrix.current[i]) }}</td>
                <td>{{ bounded(matrix.required[i]) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
      <section class="panel">
        <h2>优先补齐方向</h2>
        <p class="muted">
          能力统一使用 0–100 刻度；图表与表格均限制在该范围内。
        </p>
        <el-empty v-if="!gaps.length" description="目前没有能力缺口" />
        <div v-for="gap in gaps" :key="gap.dimension" class="gap">
          <div>
            <strong>{{ gap.dimension }}</strong
            ><span>缺口 {{ bounded(gap.gap) }}</span>
          </div>
          <el-progress
            :percentage="bounded(gap.gap)"
            :show-text="false"
            color="#df9756"
          />
          <p>{{ gap.explanation }}</p>
        </div>
        <router-link :to="`/teams/${route.params.id}/recommendations`"
          ><el-button type="primary">查看互补队友推荐 →</el-button></router-link
        >
      </section>
    </div>
    <section class="panel member-panel">
      <h2>成员能力矩阵</h2>
      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th>成员</th>
              <th v-for="name in matrix.dimensions" :key="name">{{ name }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="member in matrix.members" :key="member.id">
              <td>{{ member.display_name }}</td>
              <td v-for="(_, i) in matrix.dimensions" :key="i">
                {{ bounded(member.abilities[i]) }}
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="!matrix.members.length" class="muted">暂无成员</p>
      </div>
    </section></AsyncState
  >
</template>
