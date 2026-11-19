import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { authApi, clearToken, getToken, setToken } from '@/api'
import type { UserOut } from '@/types'

/**
 * Pinia 用户仓库：保存当前登录用户与 token。
 * 用 setup 语法（组合式）定义，和 Vue 3 的 ref/computed 写法一致。
 */
export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(getToken())
  const user = ref<UserOut | null>(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() =>
    ['school_admin', 'platform_admin'].includes(user.value?.role || ''),
  )
  const isPlatformAdmin = computed(() => user.value?.role === 'platform_admin')

  /** 登录：成功后把 token 写入 localStorage 并拉取用户资料 */
  async function login(username: string, password: string) {
    loading.value = true
    try {
      const res = await authApi.login(username, password)
      token.value = res.access_token
      setToken(res.access_token)
      await fetchMe()
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    if (!token.value) return null
    user.value = await authApi.me()
    return user.value
  }

  function logout() {
    token.value = null
    user.value = null
    clearToken()
  }

  return { token, user, loading, isLoggedIn, isAdmin, isPlatformAdmin, login, fetchMe, logout }
})
