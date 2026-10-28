<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from "vue";
import * as echarts from "echarts/core";
import { RadarChart } from "echarts/charts";
import {
  RadarComponent,
  LegendComponent,
  TooltipComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
echarts.use([
  RadarChart,
  RadarComponent,
  LegendComponent,
  TooltipComponent,
  CanvasRenderer,
]);
import { radarOption } from "../domain/capabilities.js";
const props = defineProps({ matrix: { type: Object, required: true } });
const container = ref(null);
let chart, observer;
onMounted(() => {
  chart = echarts.init(container.value);
  chart.setOption(radarOption(props.matrix));
  observer = new ResizeObserver(() => chart.resize());
  observer.observe(container.value);
});
watch(
  () => props.matrix,
  (value) => chart?.setOption(radarOption(value), true),
  { deep: true },
);
onBeforeUnmount(() => {
  observer?.disconnect();
  chart?.dispose();
});
</script>
<template>
  <div
    ref="container"
    class="radar"
    role="img"
    aria-label="团队当前能力与项目需求雷达图，详细数值见下方表格"
  />
</template>
