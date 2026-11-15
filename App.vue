<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import SiteHeader from './components/SiteHeader.vue'
import SiteFooter from './components/SiteFooter.vue'
import MathBackground from './components/MathBackground.vue'

const route = useRoute()
// 首页（中/英）头部叠在大图上，文字反白；其余页面为常规白底头部
const overlayPage = computed(() => route.name === 'home' || route.name === 'en-home')
const lang = computed(() => (route.meta?.lang === 'en' ? 'en' : 'zh'))

// 滚过大图后头部变白底吸顶
const stuck = ref(false)
const onScroll = () => {
  stuck.value = window.scrollY > 96
}
onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
})
onUnmounted(() => window.removeEventListener('scroll', onScroll))

const overlay = computed(() => overlayPage.value && !stuck.value)

// 按钮点击涟漪：全局事件委托，.btn / 新闻标签 / 系列专题箭头生效；
// prefers-reduced-motion 时不生成涟漪
let reducedMotion = false
const onPointerDown = (e) => {
  if (reducedMotion) return
  const host = e.target.closest(
    '.btn, .news-tabs button, .series-arrow, .chip, .notice-row, .news-archive li, .minutes-list li, .notice-callout, .contest-card.is-link',
  )
  if (!host) return
  const r = host.getBoundingClientRect()
  // 单层浅色圆：scale 0→4 缓缓扩散
  const d = Math.max(r.width, r.height) * 0.75
  const s = document.createElement('span')
  s.className = 'ripple'
  s.style.width = s.style.height = `${d}px`
  s.style.left = `${e.clientX - r.left - d / 2}px`
  s.style.top = `${e.clientY - r.top - d / 2}px`
  host.appendChild(s)
  s.addEventListener('animationend', () => s.remove(), { once: true })
}
onMounted(() => {
  reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  window.addEventListener('pointerdown', onPointerDown)
})
onUnmounted(() => window.removeEventListener('pointerdown', onPointerDown))
</script>

<template>
  <div class="site-shell">
    <MathBackground />
    <SiteHeader :overlay="overlay" :stuck="stuck" :lang="lang" />
    <RouterView />
    <SiteFooter :lang="lang" />
  </div>
</template>
