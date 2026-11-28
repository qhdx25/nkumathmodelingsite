<script setup lang="ts">
import { reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { isAxiosError } from 'axios'
import ElMessage from 'element-plus/es/components/message/index.mjs'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const store = useUserStore()
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function submit() {
  try {
    await store.login(form.username, form.password)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect as string
    await router.push(redirect || '/')
  } catch (error) {
    // 登录页的 401 由拦截器静默处理，这里给出业务需要的明确提示。
    if (isAxiosError(error) && error.response?.status === 401) {
      ElMessage.error('账户或密码错误')
    }
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="brand">Math<span>Team</span></h1>
      <p class="subtitle">数学建模竞赛智能组队与协作平台</p>

      <el-form :model="form" :rules="rules" label-position="top" @submit.prevent="submit">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" size="large" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password size="large" placeholder="请输入密码" />
        </el-form-item>
        <el-button type="primary" size="large" class="submit" :loading="store.loading" @click="submit">
          登录
        </el-button>
      </el-form>

      <div class="auth-footer">
        还没有账号？
        <el-button
          class="auth-switch-button"
          link
          type="primary"
          @click="router.push('/register')"
        >
          立即注册
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden; padding: 28px;
  background:
    radial-gradient(circle at 18% 22%, rgba(141, 58, 116, .2), transparent 28%),
    radial-gradient(circle at 82% 76%, rgba(113, 10, 83, .16), transparent 30%),
    linear-gradient(145deg, #fdf9fb 0%, #f3e8ef 52%, #e9dce5 100%);
}
.auth-page::before {
  content: ''; position: absolute; inset: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(113, 10, 83, .055) 1px, transparent 1px),
    linear-gradient(90deg, rgba(113, 10, 83, .055) 1px, transparent 1px);
  background-size: 42px 42px;
  mask-image: linear-gradient(to bottom, #000, transparent 85%);
}
.auth-page::after {
  content: ''; position: absolute; width: 520px; height: 520px;
  right: -210px; top: -190px; border: 1px solid rgba(113, 10, 83, .16);
  border-radius: 50%; box-shadow: 0 0 0 64px rgba(113, 10, 83, .035),
    0 0 0 128px rgba(113, 10, 83, .025);
}
.auth-card {
  position: relative; z-index: 1; width: min(430px, 100%); padding: 42px;
  background: rgba(255, 255, 255, .7); border: 1px solid rgba(113, 10, 83, .16);
  border-radius: 24px; backdrop-filter: blur(22px) saturate(135%);
  box-shadow: 0 28px 80px rgba(64, 8, 47, .16), inset 0 1px rgba(255,255,255,.9);
}
.brand { text-align: center; margin: 0; font-size: 32px; font-weight: 800; }
.brand span { color: var(--mt-primary); }
.subtitle { text-align: center; color: #6b7280; margin: 8px 0 28px; font-size: 14px; }
.submit { width: 100%; }
</style>
