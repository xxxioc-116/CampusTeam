<script setup>
import { watch } from "vue";
import { useRouter } from "vue-router";
import { auth, clearSession } from "./auth.js";
import { isDemo } from "./api/index.js";
const router = useRouter();
function logout() {
  clearSession();
  router.push("/login");
}
watch(
  () => auth.token,
  (token, old) => {
    if (!token && old)
      router.replace({
        path: "/login",
        query: { redirect: router.currentRoute.value.fullPath },
      });
  },
);
</script>
<template>
  <div class="shell">
    <header>
      <router-link class="brand" to="/projects"
        ><b>CT</b> CampusTeam</router-link
      >
      <nav v-if="auth.token">
        <router-link to="/projects">项目大厅</router-link
        ><router-link to="/profile">能力画像</router-link
        ><router-link
          v-if="auth.user?.team_id"
          :to="`/teams/${auth.user.team_id}`"
          >我的团队</router-link
        >
      </nav>
      <div class="account" v-if="auth.token">
        <span>{{ auth.user?.display_name }}</span
        ><el-button text @click="logout">退出</el-button>
      </div>
    </header>
    <div v-if="isDemo" class="demo-banner">
      演示模式 · 数据仅保存在当前浏览器，不代表真实后端或真实推荐结果
    </div>
    <main><router-view :key="$route.path" /></main>
    <footer>CampusTeam · 发现彼此的能力，让协作发生</footer>
  </div>
</template>
