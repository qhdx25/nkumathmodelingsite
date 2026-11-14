<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import SiteHeader from './components/SiteHeader.vue'
import SiteFooter from './components/SiteFooter.vue'

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
</script>

<template>
  <div class="site-shell">
    <SiteHeader :overlay="overlay" :stuck="stuck" :lang="lang" />
    <RouterView />
    <SiteFooter :lang="lang" />
  </div>
</template>
