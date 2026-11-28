<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import ElMessage from 'element-plus/es/components/message/index.mjs'
import type { FormRules } from 'element-plus'
import { authApi } from '@/api'

const router = useRouter()
const loading = ref(false)
const NANKAI_EMAIL_DOMAIN = 'mail.nankai.edu.cn'
const form = reactive({
  username: '', email: '', password: '', confirm: '', real_name: '', college: '',
})

const rules: FormRules = {
  username: [{ required: true, min: 3, max: 50, message: '用户名至少 3 个字符', trigger: 'blur' }],
  email: [
    { required: true, type: 'email', message: '请输入合法邮箱', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        const domain = value?.split('@').pop()?.toLowerCase()
        if (value && domain !== NANKAI_EMAIL_DOMAIN) {
          callback(new Error(`仅支持 @${NANKAI_EMAIL_DOMAIN} 邮箱注册`))
        } else {
          callback()
        }
      },
      trigger: ['blur', 'change'],
    },
  ],
  password: [{ required: true, min: 8, message: '密码至少 8 位', trigger: 'blur' }],
  confirm: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== form.password) callback(new Error('两次密码不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
  real_name: [
    { required: true, whitespace: true, message: '请输入姓名', trigger: 'blur' },
  ],
  college: [
    {
      required: true,
      whitespace: true,
      message: '请输入学院全称',
      trigger: 'blur',
    },
  ],
}

async function submit() {
  try {
    loading.value = true
    // 注册接口不接受 confirm 字段，提交前剔除
    await authApi.register({
      username: form.username,
      email: form.email,
      password: form.password,
      real_name: form.real_name.trim(),
      college: form.college.trim(),
    })
    ElMessage.success('注册成功，请登录')
    await router.push('/login')
  } catch {
    // 错误提示由拦截器统一处理
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="brand">创建账号</h1>
      <p class="subtitle">开始构建你的竞赛能力画像</p>
      <el-form :model="form" :rules="rules" label-position="top" @submit.prevent="submit">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="用于登录" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="name@mail.nankai.edu.cn" />
          <div class="email-hint">仅支持南开大学邮箱（@{{ NANKAI_EMAIL_DOMAIN }}）</div>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="至少 8 位" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm">
          <el-input v-model="form.confirm" type="password" show-password />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="学院（必须填写学院全称）" prop="college">
          <el-input v-model="form.college" placeholder="例如：数学科学学院" />
        </el-form-item>
        <el-button type="primary" class="submit" :loading="loading" @click="submit">注册</el-button>
      </el-form>
      <div class="auth-footer">
        已有账号？
        <el-button
          class="auth-switch-button"
          link
          type="primary"
          @click="router.push('/login')"
        >
          去登录
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
.auth-card {
  position: relative; z-index: 1; width: min(470px, 100%); padding: 38px 40px;
  background: rgba(255, 255, 255, .7); border: 1px solid rgba(113, 10, 83, .16);
  border-radius: 24px; backdrop-filter: blur(22px) saturate(135%);
  box-shadow: 0 28px 80px rgba(64, 8, 47, .16), inset 0 1px rgba(255,255,255,.9);
}
.brand { text-align: center; margin: 0; font-size: 28px; font-weight: 800; color: var(--mt-primary); }
.subtitle { text-align: center; color: #6b7280; margin: 8px 0 24px; font-size: 14px; }
.submit { width: 100%; }
.email-hint { width: 100%; margin-top: 6px; color: #6b7280; font-size: 12px; line-height: 1.4; }
</style>
