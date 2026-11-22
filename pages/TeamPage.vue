<script setup>
const configured = import.meta.env.VITE_TEAM_PLATFORM_URL || ''
let platformUrl = ''
try {
  const url = new URL(configured)
  if (['https:', 'http:'].includes(url.protocol)) platformUrl = url.href
} catch {}
</script>

<template>
  <main class="page">
    <section class="page-head"><div class="container">
      <h1>协会组队平台</h1>
      <p class="page-lead">寻找队友，加入队伍，一起完成数学建模竞赛。</p>
    </div></section>
    <section class="section"><div class="container">
      <div class="section-head"><h2>寻找适合你的队伍</h2></div>
      <p>在组队平台完善能力画像、浏览招募信息、提交组队申请，并与队友交流。</p>
      <p style="margin-top: 24px" v-if="platformUrl">
        <a class="btn btn-solid" :href="platformUrl">进入组队平台</a>
      </p>
      <p class="owner-note" v-else>组队平台正在接入，开放后可从这里进入。</p>
      <p class="section-foot">平台使用独立账号。浏览招募信息无需登录，申请组队与团队交流需注册登录。</p>
    </div></section>
  </main>
</template>
