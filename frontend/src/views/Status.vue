<script setup>
defineProps({ title: String, text: String });
</script>
<template>
  <section class="panel state">
    <h1>{{ title }}</h1>
    <p>{{ text }}</p>
    <router-link to="/projects">返回项目大厅</router-link>
  </section>
</template>
