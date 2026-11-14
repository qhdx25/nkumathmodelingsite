<script setup>
import PaperLibrary from '../components/PaperLibrary.vue'
import { feishu, groups } from '../data/materials'
</script>

<template>
  <main class="page">
    <section class="page-head">
      <div class="container">
        <h1>资料共享，共同进步</h1>
        <p class="page-lead">
          历年真题、获奖论文与工具资料，按五类归档。真题与论文以外部链接为主，
          LaTeX / Python / MATLAB 三类正在整理。
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <a class="strip" :href="feishu.url" target="_blank" rel="noreferrer">
          <div>
            <p class="card-kicker">飞书知识库</p>
            <h2>{{ feishu.title }}</h2>
            <p>{{ feishu.desc }}</p>
          </div>
          <span class="btn btn-solid">打开资料库 ↗</span>
        </a>

        <nav class="anchor-bar" aria-label="资料分类">
          <a v-for="g in groups" :key="g.id" :href="`#${g.id}`">{{ g.title }}</a>
        </nav>
      </div>
    </section>

    <section v-for="g in groups" :id="g.id" :key="g.id" class="section material-section">
      <div class="container">
        <div class="section-head">
          <h2>{{ g.title }}</h2>
          <span v-if="g.placeholder" class="head-note">整理中</span>
        </div>

        <p class="section-intro">{{ g.desc }}</p>

        <!-- 历年真题：官方入口 -->
        <ul v-if="g.items?.length" class="link-list">
          <li v-for="item in g.items" :key="item.label">
            <a :href="item.href" target="_blank" rel="noreferrer">
              <span class="link-title">{{ item.label }}</span>
              <span class="link-note">{{ item.note }}</span>
              <span class="link-open" aria-hidden="true">↗</span>
            </a>
          </li>
        </ul>

        <!-- 历年优秀论文：97 份，组件内按年份折叠 -->
        <PaperLibrary v-if="g.embed === 'papers'" />

        <p v-if="g.placeholder" class="todo-box">
          <span class="todo-tag">待补充</span>
          {{ g.placeholder }}
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="strip">
          <div>
            <h2>手上有资料愿意共享？</h2>
            <p>讲义、模板、代码都可以交给学术部汇总，统一放进资料库。</p>
          </div>
          <a class="btn" :href="feishu.url" target="_blank" rel="noreferrer">进入飞书资料库</a>
        </div>
      </div>
    </section>
  </main>
</template>
