<script setup lang="ts">
import { reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
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
  } catch {
    // Axios 拦截器已经弹过错误提示，这里不重复
  }
}

function fillDemo(username: string) {
  form.username = username
  form.password = '123456'
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

      <div class="demo">
        <span class="muted">演示账号（密码 123456）：</span>
        <el-button link type="primary" @click="fillDemo('alice')">alice 学生</el-button>
        <el-button link type="primary" @click="fillDemo('bob')">bob 队长</el-button>
        <el-button link type="primary" @click="fillDemo('admin')">admin 管理员</el-button>
      </div>
      <div class="footer">还没有账号？<el-button link type="primary" @click="router.push('/register')">立即注册</el-button></div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #eef2ff 0%, #fdf2f8 100%);
}
.auth-card {
  width: 420px; padding: 40px; background: #fff; border-radius: 16px;
  box-shadow: 0 20px 50px rgba(79,70,229,.12);
}
.brand { text-align: center; margin: 0; font-size: 32px; font-weight: 800; }
.brand span { color: #4f46e5; }
.subtitle { text-align: center; color: #6b7280; margin: 8px 0 28px; font-size: 14px; }
.submit { width: 100%; }
.demo { margin-top: 20px; padding-top: 16px; border-top: 1px dashed #e5e7eb; }
.footer { text-align: center; margin-top: 12px; font-size: 14px; color: #6b7280; }
</style>
