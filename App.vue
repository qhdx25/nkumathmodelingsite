<script setup>
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import SiteHeader from './components/SiteHeader.vue'
import SiteFooter from './components/SiteFooter.vue'

const route = useRoute()
// 首页头部叠在大图上，文字反白；其余页面为常规白底头部
const overlay = computed(() => route.name === 'home')
</script>

<template>
  <div class="site-shell">
    <SiteHeader :overlay="overlay" />
    <RouterView />
    <SiteFooter />
  </div>
</template>
