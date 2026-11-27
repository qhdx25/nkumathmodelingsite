import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { getToken } from '@/api'
import { useUserStore } from '@/stores/user'

/**
 * 路由表与导航守卫。
 * meta.requiresAuth：需要登录
 * meta.requiresAdmin：需要管理员角色
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true, title: '登录' },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { public: true, title: '注册' },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('@/views/HomeView.vue'),
        meta: { title: '首页' },
      },
      {
        path: 'profile',
        name: 'profile',
        component: () => import('@/views/ProfileView.vue'),
        meta: { requiresAuth: true, title: '个人中心' },
      },
      {
        path: 'teams',
        name: 'teams',
        component: () => import('@/views/TeamsView.vue'),
        meta: { requiresAuth: true, participantOnly: true, title: '我的团队' },
      },
      {
        path: 'teams/:id',
        name: 'team-detail',
        component: () => import('@/views/TeamDetailView.vue'),
        meta: { requiresAuth: true, participantOnly: true, title: '团队详情' },
      },
      {
        path: 'recruitments',
        name: 'recruitments',
        component: () => import('@/views/RecruitmentsView.vue'),
        meta: { title: '招募广场' },
      },
      {
        path: 'applications',
        name: 'applications',
        component: () => import('@/views/ApplicationsView.vue'),
        meta: { requiresAuth: true, participantOnly: true, title: '申请管理' },
      },
      {
        path: 'recommendations',
        name: 'recommendations',
        component: () => import('@/views/RecommendationsView.vue'),
        meta: { requiresAuth: true, participantOnly: true, title: '智能推荐' },
      },
      {
        path: 'chat',
        name: 'chat',
        component: () => import('@/views/ChatView.vue'),
        meta: { requiresAuth: true, participantOnly: true, title: '团队交流' },
      },
      {
        path: 'admin',
        name: 'admin',
        component: () => import('@/views/AdminView.vue'),
        meta: { requiresAuth: true, requiresAdmin: true, title: '后台管理' },
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 全局前置守卫：每次跳转前检查登录与角色
router.beforeEach(async (to) => {
  const store = useUserStore()
  const needsAuth = to.meta.requiresAuth === true

  if (needsAuth && !getToken()) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  // 有 token 但还没拉过用户资料（例如刚刷新页面）
  if (getToken() && !store.user) {
    try {
      await store.fetchMe()
    } catch {
      store.logout()
      if (needsAuth) return { name: 'login' }
    }
  }
  if (to.meta.requiresAdmin && !store.isAdmin) {
    return { name: 'home' }
  }
  return true
})

router.afterEach((to) => {
  document.title = `${(to.meta.title as string) || 'MathTeam'} · MathTeam`
})

export default router
