<script setup>
import { ref } from 'vue'
import { boards, planned, samplePosts } from '../data/team'

const active = ref('all')
</script>

<template>
  <main class="page">
    <section class="page-head">
      <div class="container">
        <h1>寻找队友，加入队伍</h1>
        <p class="page-lead">
          面向全校的数模组队与交流板块：发布招募、寻找队友、分享经验。
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <p class="owner-note">
          <span class="owner-tag">待建设</span>
          本页面由组队平台负责人建设，当前为版式骨架，帖子与发帖功能尚未接入。
        </p>

        <div class="board-bar">
          <div class="board-tabs" role="group" aria-label="板块筛选">
            <button
              v-for="b in boards"
              :key="b.id"
              type="button"
              class="chip"
              :class="{ 'is-active': active === b.id }"
              :aria-pressed="active === b.id"
              @click="active = b.id"
            >
              {{ b.label }}
            </button>
          </div>
          <button class="btn btn-solid" type="button" disabled>发帖</button>
        </div>

        <ul class="post-list">
          <li v-for="(p, i) in samplePosts" :key="i" class="post-row is-placeholder">
            <span class="post-board">{{ p.board }}</span>
            <div class="post-main">
              <p class="post-title">{{ p.title }}</p>
              <p class="post-meta">{{ p.author }} · {{ p.meta }}</p>
            </div>
            <span class="post-replies">{{ p.replies }} 回复</span>
          </li>
        </ul>

        <p class="section-foot">
          以上三行为版式示意，不是真实帖子。接入数据后按「板块 · 标题 · 发帖人 · 时间 · 回复数」渲染。
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>需要实现的功能</h2>
          <span class="head-note">待接入后端</span>
        </div>

        <ul class="plan-list">
          <li v-for="(p, i) in planned" :key="i">
            <span class="plan-index">{{ String(i + 1).padStart(2, '0') }}</span>
            <span>{{ p }}</span>
          </li>
        </ul>
      </div>
    </section>
  </main>
</template>
