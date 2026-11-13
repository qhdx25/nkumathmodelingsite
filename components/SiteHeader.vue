<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { nav, subNav } from '../data/site'

const route = useRoute()

const isActive = (to) => (to === '/' ? route.path === '/' : route.path.startsWith(to))
const subActive = computed(() => subNav.some((item) => route.path.startsWith(item.to)))
</script>

<template>
  <header class="site-header">
    <div class="container header-inner">
      <RouterLink to="/" class="brand">
        <span class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 32 32" width="34" height="34">
            <circle cx="16" cy="16" r="16" fill="#ffffff" />
            <circle cx="16" cy="16" r="12.5" fill="none" stroke="#710a53" stroke-width="0.8" opacity="0.4" />
            <text
              x="16"
              y="20.6"
              text-anchor="middle"
              font-family="Arial, Helvetica, sans-serif"
              font-size="10"
              font-weight="700"
              fill="#710a53"
            >NKU</text>
          </svg>
        </span>
        <span class="brand-copy">
          <strong>南开大学数学建模协会</strong>
          <em>数学科学学院</em>
        </span>
      </RouterLink>

      <nav class="main-nav" aria-label="主导航">
        <RouterLink
          v-for="item in nav"
          :key="item.to"
          :to="item.to"
          :class="{ 'is-active': isActive(item.to) }"
        >{{ item.label }}</RouterLink>

        <div class="nav-item">
          <a href="#" :class="{ 'is-active': subActive }" @click.prevent>更多</a>
          <div class="sub-nav">
            <RouterLink
              v-for="item in subNav"
              :key="item.to"
              :to="item.to"
              :class="{ 'is-active': route.path.startsWith(item.to) }"
            >{{ item.label }}</RouterLink>
          </div>
        </div>
      </nav>
    </div>
  </header>
</template>
