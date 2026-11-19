<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormRules } from 'element-plus'
import { authApi } from '@/api'

const router = useRouter()
const loading = ref(false)
const form = reactive({
  username: '', email: '', password: '', confirm: '', real_name: '', school: '',
})

const rules: FormRules = {
  username: [{ required: true, min: 3, max: 50, message: '用户名至少 3 个字符', trigger: 'blur' }],
  email: [{ required: true, type: 'email', message: '请输入合法邮箱', trigger: 'blur' }],
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
}

async function submit() {
  try {
    loading.value = true
    // 注册接口不接受 confirm 字段，提交前剔除
    await authApi.register({
      username: form.username,
      email: form.email,
      password: form.password,
      real_name: form.real_name || undefined,
      school: form.school || undefined,
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
          <el-input v-model="form.email" placeholder="name@example.com" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="至少 8 位" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm">
          <el-input v-model="form.confirm" type="password" show-password />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.real_name" placeholder="选填" />
        </el-form-item>
        <el-form-item label="学校">
          <el-input v-model="form.school" placeholder="选填，管理员按学校限定管理范围" />
        </el-form-item>
        <el-button type="primary" class="submit" :loading="loading" @click="submit">注册</el-button>
      </el-form>
      <div class="footer">已有账号？<el-button link type="primary" @click="router.push('/login')">去登录</el-button></div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #eef2ff 0%, #fdf2f8 100%);
}
.auth-card {
  width: 460px; padding: 36px 40px; background: #fff; border-radius: 16px;
  box-shadow: 0 20px 50px rgba(79,70,229,.12);
}
.brand { text-align: center; margin: 0; font-size: 28px; font-weight: 800; }
.subtitle { text-align: center; color: #6b7280; margin: 8px 0 24px; font-size: 14px; }
.submit { width: 100%; }
.footer { text-align: center; margin-top: 12px; font-size: 14px; color: #6b7280; }
</style>
