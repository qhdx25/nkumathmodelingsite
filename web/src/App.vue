<script setup lang="ts">
import { RouterView } from 'vue-router'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
</script>

<template>
  <el-config-provider :locale="zhCn">
    <!-- 所有页面都渲染在这里，布局由各路由的 meta 决定 -->
    <RouterView />
  </el-config-provider>
</template>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
}
</style>
