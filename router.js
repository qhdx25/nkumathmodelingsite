import { createRouter, createWebHistory } from 'vue-router'

import CommitteePage from './pages/CommitteePage.vue'
import HomePage from './pages/HomePage.vue'
import MaterialsPage from './pages/MaterialsPage.vue'
import TrainingPage from './pages/TrainingPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomePage },
    { path: '/committee', name: 'committee', component: CommitteePage },
    { path: '/materials', name: 'materials', component: MaterialsPage },
    { path: '/training', name: 'training', component: TrainingPage },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }

    if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth',
      }
    }

    return { top: 0 }
  },
})

export default router
