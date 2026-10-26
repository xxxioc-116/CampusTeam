<script setup>
defineProps({ loading: Boolean, error: String, empty: Boolean });
defineEmits(["retry"]);
</script>
<template>
  <div v-if="loading" class="state" role="status">正在加载，请稍候…</div>
  <div v-else-if="error" class="state error" role="alert">
    <p>{{ error }}</p>
    <el-button @click="$emit('retry')">重新加载</el-button>
  </div>
  <el-empty v-else-if="empty" description="暂无数据" />
  <slot v-else />
</template>
