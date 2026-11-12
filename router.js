import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('./pages/HomePage.vue') },
  { path: '/competition', name: 'competition', component: () => import('./pages/CompetitionPage.vue') },
  { path: '/materials', name: 'materials', component: () => import('./pages/MaterialsPage.vue') },
  { path: '/committee', name: 'committee', component: () => import('./pages/CommitteePage.vue') },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('./pages/NotFoundPage.vue') },
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

export default router
