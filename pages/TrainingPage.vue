<script setup>
import PlaceholderBlock from '../components/PlaceholderBlock.vue'
import { notices, owner, resources, tracks } from '../data/training'
</script>

<template>
  <main class="page">
    <section class="page-head">
      <div class="container">
        <p class="kicker">校队培训</p>
        <h1>系统训练，备战竞赛</h1>
        <p class="page-lead">
          从入门到上场：培训资料、训练体系与代表队培训通知集中在这里。
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <p class="owner-note">
          <span class="owner-tag">待建设</span>
          {{ owner.note }}{{ owner.contact }}
        </p>

        <div class="section-head">
          <div>
            <p class="kicker">资料链接</p>
            <h2>培训资料</h2>
          </div>
        </div>

        <ul class="link-list">
          <li v-for="item in resources" :key="item.label">
            <a v-if="item.href" :href="item.href" target="_blank" rel="noreferrer">
              <span class="link-title">{{ item.label }}</span>
              <span class="link-note">{{ item.desc }}</span>
              <span class="link-open" aria-hidden="true">↗</span>
            </a>
            <div v-else class="link-row is-pending">
              <span class="link-title">{{ item.label }}</span>
              <span class="link-note">{{ item.desc }}</span>
              <span class="badge badge-pending">待补充</span>
            </div>
          </li>
        </ul>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <div>
            <p class="kicker">训练体系</p>
            <h2>四个阶段，从零到上场</h2>
          </div>
          <span class="head-note">内容待各专题负责人填充</span>
        </div>

        <div class="track-grid">
          <article v-for="t in tracks" :key="t.title" class="track-card">
            <h3>{{ t.title }}</h3>
            <p class="track-desc">{{ t.desc }}</p>
            <ul>
              <li v-for="item in t.items" :key="item">{{ item }}</li>
            </ul>
          </article>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <div>
            <p class="kicker">培训通知</p>
            <h2>代表队培训通知</h2>
          </div>
          <span class="badge badge-pending">暂无通知</span>
        </div>

        <ul v-if="notices.length" class="notice-plain">
          <li v-for="n in notices" :key="n.title">
            <time>{{ n.date }}</time>
            <span>{{ n.title }}</span>
          </li>
        </ul>

        <PlaceholderBlock
          v-else
          title="培训通知位"
          desc="按时间倒序列出代表队培训的时间、地点、主讲与参训对象，支持跳转原文。"
          requirement="负责人提供通知条目（日期 / 标题 / 链接）后填入 data/training.js 的 notices 数组即可。"
          ratio="16 / 4"
          compact
        />
      </div>
    </section>
  </main>
</template>
