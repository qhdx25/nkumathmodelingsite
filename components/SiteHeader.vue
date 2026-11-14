<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { nav, topLinks } from '../data/site'
import { enHeader } from '../data/en'

const props = defineProps({
  // 首页：叠在大图上，文字反白
  overlay: { type: Boolean, default: false },
  // 滚动吸顶后：白底 + 阴影
  stuck: { type: Boolean, default: false },
  // zh | en —— 英文版换一整套导航文案
  lang: { type: String, default: 'zh' },
})

const route = useRoute()
const isEn = computed(() => props.lang === 'en')
const navItems = computed(() => (isEn.value ? enHeader.nav : nav))
const links = computed(() => (isEn.value ? enHeader.topLinks : topLinks))
const note = computed(() => (isEn.value ? enHeader.note : '数学科学学院 · 学生社团'))
const brand = computed(() => (isEn.value ? enHeader.brand : '南开大学数学建模协会'))
const brandSub = computed(() =>
  isEn.value ? enHeader.brandSub : 'Nankai University Mathematical Modeling Association',
)
const homeTo = computed(() => (isEn.value ? '/en' : '/'))
const isActive = (to) => {
  if (to.includes('#')) return false
  // 首页（中/英）做精确匹配，否则 /en 会把 /en/news 也算成选中
  if (to === '/' || to === '/en') return route.path === to
  return route.path.startsWith(to)
}
</script>

<template>
  <header class="site-head" :class="{ 'is-overlay': overlay, 'is-stuck': stuck, 'is-en': isEn }">
    <div class="topbar">
      <div class="container topbar-inner">
        <p class="topbar-note">{{ note }}</p>
        <ul class="top-links">
          <li v-for="item in links" :key="item.label">
            <RouterLink :to="item.to">{{ item.label }}</RouterLink>
          </li>
        </ul>
      </div>
    </div>

    <div class="container masthead">
      <RouterLink :to="homeTo" class="brand">
        <img class="brand-mark" src="/img/nku-mark.png" :alt="isEn ? enHeader.alt : '南开大学校徽'" />
        <span class="brand-copy">
          <strong>{{ brand }}</strong>
          <em>{{ brandSub }}</em>
        </span>
      </RouterLink>

      <nav class="main-nav" :aria-label="isEn ? 'Main navigation' : '主导航'">
        <RouterLink
          v-for="item in navItems"
          :key="item.label"
          :to="item.to"
          :class="{ 'is-active': isActive(item.to) }"
        >{{ item.label }}</RouterLink>
      </nav>
    </div>
  </header>
</template>
