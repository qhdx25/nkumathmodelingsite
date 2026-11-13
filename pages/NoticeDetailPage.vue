<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import PageReader from '../components/PageReader.vue'
import { categories, getNotice, listNotices } from '../data/notices'

const route = useRoute()
const doc = computed(() => getNotice(route.params.slug))

const catLabel = (id) => categories.find((c) => c.id === id)?.label ?? ''

// 同类别其他文件，最多 4 条
const related = computed(() => {
  if (!doc.value) return []
  return listNotices(doc.value.category)
    .filter((n) => n.slug !== doc.value.slug)
    .slice(0, 4)
})
</script>

<template>
  <main class="page">
    <template v-if="doc">
      <section class="page-head">
        <div class="container">
          <nav class="crumb" aria-label="位置">
            <RouterLink to="/">首页</RouterLink>
            <span aria-hidden="true">/</span>
            <RouterLink to="/notice">信息公示</RouterLink>
            <span aria-hidden="true">/</span>
            <span class="crumb-cur">{{ catLabel(doc.category) }}</span>
          </nav>

          <div class="notice-tags">
            <span class="tag" :class="`tag-${doc.category}`">{{ catLabel(doc.category) }}</span>
            <span v-if="doc.internal" class="tag tag-internal">内部文件</span>
            <span class="status" :class="`is-${doc.status.tone}`">{{ doc.status.text }}</span>
          </div>

          <h1 class="notice-title">{{ doc.title }}</h1>
          <p class="notice-sub">{{ doc.sub }}</p>

          <dl class="notice-facts">
            <div>
              <dt>发布单位</dt>
              <dd>{{ doc.issuer }}</dd>
            </div>
            <div>
              <dt>发布日期</dt>
              <dd>{{ doc.date }}</dd>
            </div>
            <div>
              <dt>页数</dt>
              <dd>{{ doc.pages }} 页</dd>
            </div>
            <div v-if="doc.period">
              <dt>公示期</dt>
              <dd>{{ doc.period.from }} — {{ doc.period.to }}</dd>
            </div>
          </dl>

          <div class="notice-actions">
            <a v-if="doc.file" class="btn btn-solid" :href="doc.file" download>下载 PDF</a>
            <a
              v-if="doc.sourceUrl"
              class="btn"
              :class="doc.file ? 'btn-ghost' : 'btn-solid'"
              :href="doc.sourceUrl"
              target="_blank"
              rel="noreferrer"
            >
              {{ doc.sourceLabel || '查看官方原文' }} ↗
            </a>
            <span class="notice-actions-note">站内为逐页图片，清晰度以原件为准。</span>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="container">
          <div class="notice-body">
            <div class="notice-side">
              <div class="notice-abstract">
                <p class="card-kicker">摘要</p>
                <p class="abstract-text">{{ doc.summary }}</p>
              </div>

              <div v-if="doc.points?.length" class="notice-points">
                <p class="card-kicker">要点</p>
                <ul>
                  <li v-for="(p, i) in doc.points" :key="i">{{ p }}</li>
                </ul>
              </div>

              <p v-if="doc.internal" class="notice-internal-note">
                本文件为协会内部会议纪要，涉及人事与资金事项。公开前请与理事会确认披露范围。
              </p>
            </div>

            <div class="notice-reader">
              <PageReader :base="doc.reader" :pages="doc.pages" :title="doc.title" />
            </div>
          </div>
        </div>
      </section>

      <section v-if="related.length" class="section">
        <div class="container">
          <div class="section-head">
            <h2>其他公示文件</h2>
            <RouterLink class="head-link" to="/notice">全部 →</RouterLink>
          </div>

          <div class="related-grid">
            <RouterLink
              v-for="n in related"
              :key="n.slug"
              class="related-card"
              :to="`/notice/${n.slug}`"
            >
              <p class="related-date">{{ n.date }}</p>
              <h3>{{ n.title }}</h3>
              <p>{{ n.sub }}</p>
              <span class="text-link">共 {{ n.pages }} 页 →</span>
            </RouterLink>
          </div>
        </div>
      </section>
    </template>

    <section v-else class="section">
      <div class="container">
        <h1>没有找到这份文件</h1>
        <p class="page-lead">链接可能已更新，或该文件尚未发布。</p>
        <p style="margin-top: 18px">
          <RouterLink class="btn btn-solid" to="/notice">返回信息公示</RouterLink>
        </p>
      </div>
    </section>
  </main>
</template>
