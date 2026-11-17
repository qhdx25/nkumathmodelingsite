<script setup>
import PaperLibrary from '../components/PaperLibrary.vue'
import { feishu, groups } from '../data/materials'
</script>

<template>
  <main class="page">
    <section class="page-head">
      <div class="container">
        <h1 class="materials-page-title">建模资料</h1>
        <p class="page-lead">
          <strong class="materials-page-subtitle">资料共享，共同进步</strong><br />历年真题、获奖论文与工具资料，按五类归档。真题与论文以外部链接为主，
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

    <details v-for="g in groups" :id="g.id" :key="g.id" class="section material-section material-details"><summary class="section-head"><h2>{{ g.title }}</h2><span class="material-toggle"><span>展开 / 收起</span></span></summary><div class="material-details-body"><div class="container">
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
    </div></div></details>

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

<style scoped>.material-details{margin:0;border-top:1px solid var(--line)}.material-details summary{list-style:none;cursor:pointer}.material-details summary::-webkit-details-marker{display:none}.material-details summary:after{content:'+';color:var(--accent);font-size:20px}.material-details[open] summary:after{content:'-'} .material-details-body{display:grid;grid-template-rows:0fr;transition:grid-template-rows 280ms ease;overflow:hidden}.material-details[open] .material-details-body{grid-template-rows:1fr}.material-details-body>.container{min-height:0}@media(prefers-reduced-motion:reduce){.material-details-body{transition:none}}</style>

<style scoped>.material-details>.section-head{justify-content:flex-start;gap:8px}.material-toggle{display:inline-flex;align-items:center;gap:5px;color:var(--faint);font-size:12px}.material-details summary:after{content:none}.material-toggle:before{content:'›';display:inline-block;color:var(--accent);font-size:20px;line-height:1;transition:transform 280ms ease}.material-details[open] .material-toggle:before{transform:rotate(90deg)}.material-details-body{transition:grid-template-rows 420ms cubic-bezier(.22,.61,.36,1)}@media(prefers-reduced-motion:reduce){.material-toggle:before{transition:none}}</style>
