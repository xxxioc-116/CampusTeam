<script setup>
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { auth } from "../auth.js";
import { api } from "../api/index.js";
import AsyncState from "../components/AsyncState.vue";

const invitations = ref([]),
  loading = ref(true),
  error = ref(""),
  acting = ref(new Set()),
  actionError = ref({});

const statusText = {
  pending: "待处理",
  accepted: "已接受",
  rejected: "已拒绝",
  withdrawn: "已撤回",
};

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const data = await api("/invitations");
    invitations.value = Array.isArray(data) ? data : data.results || [];
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

async function transition(invitation, action) {
  if (invitation.status !== "pending" || acting.value.has(invitation.id))
    return;
  acting.value = new Set(acting.value).add(invitation.id);
  actionError.value = { ...actionError.value, [invitation.id]: "" };
  try {
    const updated = await api(`/invitations/${invitation.id}/transition`, {
      method: "POST",
      body: { action },
    });
    Object.assign(invitation, updated);
    if (action === "accept") {
      const profile = await api("/profiles/me");
      auth.user = profile.user;
    }
    ElMessage.success(action === "accept" ? "已加入团队" : "已拒绝邀请");
  } catch (e) {
    actionError.value = {
      ...actionError.value,
      [invitation.id]: e.message,
    };
    if (e.status === 409) await load();
  } finally {
    const next = new Set(acting.value);
    next.delete(invitation.id);
    acting.value = next;
  }
}

onMounted(load);
</script>

<template>
  <div class="page-heading">
    <p class="eyebrow">INVITATION INBOX</p>
    <h1>收到的邀请</h1>
    <p>查看团队邀请，并完成接受或拒绝。</p>
  </div>
  <AsyncState :loading="loading" :error="error" @retry="load">
    <el-empty v-if="!invitations.length" description="暂时没有收到团队邀请" />
    <section v-else class="invitation-list" aria-label="收到的邀请列表">
      <article
        v-for="invitation in invitations"
        :key="invitation.id"
        class="panel invitation-card"
      >
        <div>
          <p class="eyebrow">{{ statusText[invitation.status] }}</p>
          <h2>{{ invitation.team_name || `团队 ${invitation.team}` }}</h2>
          <p>
            邀请人：{{
              invitation.inviter?.display_name ||
              invitation.inviter?.username ||
              "未知"
            }}
          </p>
          <p class="muted">{{ invitation.message || "对方未填写留言" }}</p>
          <p v-if="actionError[invitation.id]" role="alert" class="error">
            {{ actionError[invitation.id] }}
          </p>
        </div>
        <div v-if="invitation.status === 'pending'" class="invitation-actions">
          <el-button
            :loading="acting.has(invitation.id)"
            @click="transition(invitation, 'reject')"
            >拒绝</el-button
          >
          <el-button
            type="primary"
            :loading="acting.has(invitation.id)"
            @click="transition(invitation, 'accept')"
            >接受并加入</el-button
          >
        </div>
        <p v-else class="muted">该邀请已处理，不能重复操作。</p>
      </article>
    </section>
  </AsyncState>
</template>
