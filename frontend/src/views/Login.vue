<script setup>
import { computed, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api, isDemo } from "../api/index.js";
import { setSession, safeRedirect } from "../auth.js";
const route = useRoute(),
  router = useRouter();
const registering = computed(() => route.path === "/register");
const form = reactive({
  username: "",
  password: "",
  display_name: "",
  confirm: "",
});
const busy = ref(false),
  error = ref("");
async function submit() {
  if (busy.value) return;
  error.value = "";
  if (!/^[a-zA-Z0-9_]{3,30}$/.test(form.username)) {
    error.value = "用户名需为 3–30 位字母、数字或下划线";
    return;
  }
  if (form.password.length < 8) {
    error.value = "密码至少 8 位";
    return;
  }
  if (
    registering.value &&
    (!form.display_name.trim() || form.password !== form.confirm)
  ) {
    error.value = "请填写姓名，并确认两次密码一致";
    return;
  }
  busy.value = true;
  try {
    const payload = { username: form.username, password: form.password };
    if (registering.value) payload.display_name = form.display_name.trim();
    setSession(
      await api(registering.value ? "/auth/register" : "/auth/login", {
        method: "POST",
        body: payload,
      }),
    );
    await router.replace(safeRedirect(route.query.redirect));
  } catch (e) {
    error.value = e.message;
  } finally {
    busy.value = false;
  }
}
</script>
<template>
  <section class="auth-layout">
    <div class="auth-story">
      <p class="eyebrow">BUILD SOMETHING TOGETHER</p>
      <h1>把你的能力，<br />放进合适的团队。</h1>
      <p>从学生画像到可解释推荐，找到与你互补的伙伴。</p>
      <div class="story-stat">
        01 认识自己　 /　02 发现项目　 /　03 开始协作
      </div>
    </div>
    <div class="panel auth-card">
      <h2>{{ registering ? "创建账号" : "欢迎回来" }}</h2>
      <p class="muted">
        {{ registering ? "注册后完善你的能力画像" : "登录你的校园协作空间" }}
      </p>
      <form @submit.prevent="submit">
        <label
          >用户名<input
            v-model.trim="form.username"
            autocomplete="username"
            required
            maxlength="30" /></label
        ><label v-if="registering"
          >姓名<input
            v-model.trim="form.display_name"
            maxlength="40"
            required
            autocomplete="name" /></label
        ><label
          >密码<input
            v-model="form.password"
            type="password"
            :autocomplete="registering ? 'new-password' : 'current-password'"
            required
            minlength="8" /></label
        ><label v-if="registering"
          >确认密码<input
            v-model="form.confirm"
            type="password"
            autocomplete="new-password"
            required
        /></label>
        <p v-if="error" role="alert" class="error">{{ error }}</p>
        <el-button
          native-type="submit"
          type="primary"
          :loading="busy"
          class="wide"
          >{{ registering ? "注册并进入" : "登录" }}</el-button
        >
      </form>
      <p>
        <router-link
          :to="{
            path: registering ? '/login' : '/register',
            query: route.query,
          }"
          >{{
            registering ? "已有账号？去登录" : "没有账号？立即注册"
          }}</router-link
        >
      </p>
      <p v-if="isDemo" class="hint">
        演示账号：student / captain / admin<br />统一密码：Campus123!<br />演示注册请使用虚构信息。
      </p>
      <p v-else class="hint">
        真实后端角色为 student / leader / admin；账号请联系团队负责人获取，请勿使用真实密码。
      </p>
    </div>
  </section>
</template>
