import { createRouter, createWebHistory } from 'vue-router'

const SITE = '南开大学数学建模协会'

const routes = [
  { path: '/', name: 'home', component: () => import('./pages/HomePage.vue'), meta: { title: '首页' } },
  { path: '/competition', name: 'competition', component: () => import('./pages/CompetitionPage.vue'), meta: { title: '竞赛' } },
  { path: '/training', name: 'training', component: () => import('./pages/TrainingPage.vue'), meta: { title: '校队培训' } },
  { path: '/materials', name: 'materials', component: () => import('./pages/MaterialsPage.vue'), meta: { title: '建模资料' } },
  { path: '/team', name: 'team', component: () => import('./pages/TeamPage.vue'), meta: { title: '组队平台' } },
  { path: '/notice', name: 'notice', component: () => import('./pages/NoticePage.vue'), meta: { title: '信息公示' } },
  { path: '/notice/:slug', name: 'notice-detail', component: () => import('./pages/NoticeDetailPage.vue'), meta: { title: '信息公示' } },
  { path: '/committee', name: 'committee', component: () => import('./pages/CommitteePage.vue'), meta: { title: '委员会' } },
  { path: '/news', name: 'news', component: () => import('./pages/NewsPage.vue'), meta: { title: '最新动态' } },
  { path: '/search', name: 'search', component: () => import('./pages/SearchPage.vue'), meta: { title: '站内搜索' } },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('./pages/NotFoundPage.vue'), meta: { title: '页面不存在' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, behavior: 'smooth' }
    return { top: 0 }
  },
})

router.afterEach((to) => {
  const page = to.meta?.title
  document.title = !page || to.name === 'home' ? SITE : `${page} · ${SITE}`
})

export default router
