<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <!-- 所有页面都渲染在这里，布局由各路由的 meta 决定 -->
  <RouterView />
</template>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
}
</style>
