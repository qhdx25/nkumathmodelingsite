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
          <svg viewBox="0 0 32 32" width="30" height="30">
            <circle cx="16" cy="16" r="15" fill="#710a53" />
            <circle cx="16" cy="16" r="12" fill="none" stroke="#ffffff" stroke-width="0.8" opacity="0.55" />
            <text
              x="16"
              y="20.5"
              text-anchor="middle"
              font-family="Arial, Helvetica, sans-serif"
              font-size="9.5"
              font-weight="700"
              fill="#ffffff"
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
