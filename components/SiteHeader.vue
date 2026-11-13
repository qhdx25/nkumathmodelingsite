<script setup>
import { RouterLink, useRoute } from 'vue-router'
import { nav, topLinks } from '../data/site'

defineProps({
  // 首页：叠在大图上，文字反白
  overlay: { type: Boolean, default: false },
})

const route = useRoute()
const isActive = (to) => (to === '/' ? route.path === '/' : route.path.startsWith(to.split('#')[0]))
</script>

<template>
  <header class="site-head" :class="{ 'is-overlay': overlay }">
    <div class="topbar">
      <div class="container topbar-inner">
        <p class="topbar-note">数学科学学院 · 学生社团</p>
        <ul class="top-links">
          <li v-for="item in topLinks" :key="item.label">
            <RouterLink v-if="item.to !== '/'" :to="item.to">{{ item.label }}</RouterLink>
            <span v-else class="is-soon" :title="item.note">{{ item.label }}</span>
          </li>
        </ul>
      </div>
    </div>

    <div class="container masthead">
      <RouterLink to="/" class="brand">
        <img class="brand-mark" src="/img/nku-mark.png" alt="南开大学校徽" />
        <span class="brand-copy">
          <strong>南开大学数学建模协会</strong>
          <em>Nankai University Mathematical Modeling Association</em>
        </span>
      </RouterLink>

      <nav class="main-nav" aria-label="主导航">
        <RouterLink
          v-for="item in nav"
          :key="item.to"
          :to="item.to"
          :class="{ 'is-active': isActive(item.to) }"
        >{{ item.label }}</RouterLink>
      </nav>
    </div>
  </header>
</template>
