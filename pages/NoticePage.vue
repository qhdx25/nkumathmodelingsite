<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { imgUrl } from '../assets/resolver'
import PageRail from '../components/PageRail.vue'
import { categories, listNotices } from '../data/notices'

const all = computed(() => listNotices('all'))
const live = computed(() => all.value.filter((n) => n.status.tone === 'live'))
const award = computed(() => all.value.filter((n) => n.category === 'award'))
const files = computed(() => all.value.filter((n) => n.category === 'files'))
const minutes = computed(() => all.value.filter((n) => n.category === 'minutes'))
const total = computed(() => all.value.length)
const latest = computed(() => all.value[0]?.date ?? '')

const catLabel = (id) => categories.find((c) => c.id === id)?.label ?? ''
// 外部条目没有站内页图，别显示「共 0 页」
const pageText = (n) => (n.pages ? ` · 共 ${n.pages} 页` : '')

// 有公示中的文件才把「正在公示」放在最前
const sections = computed(() => {
  const base = [
    { id: 'award', label: '获奖与成绩' },
    { id: 'files', label: '赛务文件' },
    { id: 'minutes', label: '会议纪要' },
    { id: 'rule', label: '公示说明' },
  ]
  return live.value.length ? [{ id: 'live', label: '正在公示' }, ...base] : base
})
</script>

<template>
  <main class="page comp-page notice-page">
    <div class="comp-body">
      <PageRail :sections="sections" />

      <div class="comp-flow">
        <section class="page-head">
          <div class="container">
            <p class="eyebrow">Disclosure · 2026</p>
            <h1>信息公示</h1>
            <p class="page-lead">
              协会对外公开的获奖名单、赛务文件与会议纪要。文件按类别分栏陈列，可在站内逐页阅读，
              也可跳转发布单位的原文核对。当前收录 <strong>{{ total }}</strong> 份<template v-if="live.length">，其中
              <strong>{{ live.length }}</strong> 份处于公示期</template><template v-else>，暂无文件处于公示期</template>。
            </p>
            <p class="head-note-inline">最近更新 {{ latest }}</p>
          </div>
        </section>

        <section v-if="live.length" id="live" class="section">
          <div class="container">
            <div class="section-head">
              <h2>正在公示</h2>
              <span class="head-note">异议请在公示期内按原文渠道提出</span>
            </div>
            <div class="notice-list">
              <RouterLink v-for="n in live" :key="n.slug" class="notice-row" :to="`/notice/${n.slug}`">
                <span v-if="n.image" class="row-thumb"><img :src="imgUrl(n.image)" :alt="n.title" /></span>
                <div class="notice-main">
                  <div class="notice-tags">
                    <span class="tag" :class="`tag-${n.category}`">{{ catLabel(n.category) }}</span>
                    <span class="status" :class="`is-${n.status.tone}`">{{ n.status.text }}</span>
                  </div>
                  <h3>{{ n.title }}</h3>
                  <p class="notice-sub">{{ n.sub }}</p>
                  <p class="notice-meta">{{ n.issuer }} · {{ n.date }}{{ pageText(n) }}</p>
                </div>
                <span class="notice-go" aria-hidden="true">›</span>
              </RouterLink>
            </div>
          </div>
        </section>

        <section id="award" class="section">
          <div class="container">
            <div class="section-head">
              <h2>获奖与成绩</h2>
              <span class="head-note">{{ award.length }} 份</span>
            </div>
            <div class="notice-cards">
              <RouterLink v-for="n in award" :key="n.slug" class="notice-card" :to="`/notice/${n.slug}`">
                <span class="nc-media">
                  <img :src="imgUrl(n.image)" :alt="n.title" />
                  <span class="nc-cat">{{ catLabel(n.category) }}</span>
                  <span class="nc-title">{{ n.title }}</span>
                </span>
                <span class="nc-body">
                  <span class="nc-sub">{{ n.sub }}</span>
                  <span class="nc-meta">{{ n.issuer }} · {{ n.date }}{{ pageText(n) }}</span>
                  <span class="nc-state" :class="`is-${n.status.tone}`">{{ n.status.text }}</span>
                  <span class="nc-more">查看 →</span>
                </span>
              </RouterLink>
            </div>
          </div>
        </section>

        <section id="files" class="section">
          <div class="container">
            <div class="section-head">
              <h2>赛务文件</h2>
              <span class="head-note">报名通知、赛制与选拔办法</span>
            </div>
            <div class="notice-cards">
              <RouterLink v-for="n in files" :key="n.slug" class="notice-card" :to="`/notice/${n.slug}`">
                <span class="nc-media">
                  <img :src="imgUrl(n.image)" :alt="n.title" />
                  <span class="nc-cat">{{ catLabel(n.category) }}</span>
                  <span class="nc-title">{{ n.title }}</span>
                </span>
                <span class="nc-body">
                  <span class="nc-sub">{{ n.sub }}</span>
                  <span class="nc-meta">{{ n.issuer }} · {{ n.date }}{{ pageText(n) }}</span>
                  <span class="nc-state" :class="`is-${n.status.tone}`">{{ n.status.text }}</span>
                  <span class="nc-more">查看 →</span>
                </span>
              </RouterLink>
            </div>
          </div>
        </section>

        <section id="minutes" class="section">
          <div class="container">
            <div class="section-head">
              <h2>会议纪要</h2>
              <span class="head-note">涉及人事与资金，公开范围由理事会决定</span>
            </div>
            <div class="notice-list">
              <RouterLink v-for="n in minutes" :key="n.slug" class="notice-row" :to="`/notice/${n.slug}`">
                <span v-if="n.image" class="row-thumb"><img :src="imgUrl(n.image)" :alt="n.title" loading="lazy" /></span>
                <div class="notice-main">
                  <div class="notice-tags">
                    <span class="tag" :class="`tag-${n.category}`">{{ catLabel(n.category) }}</span>
                    <span class="tag tag-internal">内部文件</span>
                    <span class="status" :class="`is-${n.status.tone}`">{{ n.status.text }}</span>
                  </div>
                  <h3>{{ n.title }}</h3>
                  <p class="notice-sub">{{ n.sub }}</p>
                  <p class="notice-meta">{{ n.issuer }} · {{ n.date }}{{ pageText(n) }}</p>
                </div>
                <span class="notice-go" aria-hidden="true">›</span>
              </RouterLink>
            </div>
          </div>
        </section>

        <section id="rule" class="section">
          <div class="container">
            <div class="section-head">
              <h2>公示说明</h2>
            </div>
            <ul class="rule-list">
              <li><strong>来源</strong>获奖名单与赛务文件以发布单位原文为准，站内为整理后的逐页图片或摘要。</li>
              <li><strong>异议</strong>处于公示期的文件，按原文说明的渠道与时限提出，协会不代收异议材料。</li>
              <li><strong>范围</strong>会议纪要涉及协会内部人事与资金事项，公开范围由理事会决定；如需撤下请告知。</li>
              <li><strong>纠错</strong>姓名、队名、指导教师等文字错误，请注明文件与页数，我们核对原文后更正。</li>
            </ul>
            <p class="section-foot">资料整理：协会秘书处 · 数据截至 2026-11</p>
          </div>
        </section>
      </div>
    </div>
  </main>
</template>
