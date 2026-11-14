<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { categories, listNotices } from '../data/notices'

const active = ref('all')
const rows = computed(() => listNotices(active.value))
const counts = computed(() =>
  Object.fromEntries(categories.map((c) => [c.id, listNotices(c.id).length])),
)
const total = computed(() => counts.value.all ?? 0)

const catLabel = (id) => categories.find((c) => c.id === id)?.label ?? ''
</script>

<template>
  <main class="page">
    <section class="page-head">
      <div class="container">
        <h1>信息公示</h1>
        <p class="page-lead">
          协会对外公开的获奖名单、公示公告与会议纪要。所有文件均可站内逐页阅读，也可下载原件。
          当前共 <strong>{{ total }}</strong> 份文件。
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="notice-filter" role="group" aria-label="按类别筛选">
          <button
            v-for="c in categories"
            :key="c.id"
            type="button"
            class="chip"
            :class="{ 'is-active': active === c.id }"
            :aria-pressed="active === c.id"
            @click="active = c.id"
          >
            {{ c.label }}
            <span class="chip-count">{{ counts[c.id] }}</span>
          </button>
        </div>

        <div class="notice-list">
          <RouterLink
            v-for="n in rows"
            :key="n.slug"
            class="notice-row"
            :to="`/notice/${n.slug}`"
          >
            <div class="notice-main">
              <div class="notice-tags">
                <span class="tag" :class="`tag-${n.category}`">{{ catLabel(n.category) }}</span>
                <span v-if="n.internal" class="tag tag-internal">内部文件</span>
                <span class="status" :class="`is-${n.status.tone}`">{{ n.status.text }}</span>
              </div>
              <h3>{{ n.title }}</h3>
              <p class="notice-sub">{{ n.sub }}</p>
              <p class="notice-meta">
                {{ n.issuer }} · {{ n.date }} · 共 {{ n.pages }} 页
              </p>
            </div>
            <span class="notice-go" aria-hidden="true">›</span>
          </RouterLink>
        </div>

        <p class="section-foot">
          说明：会议纪要涉及协会内部人事与资金事项，公开范围由理事会决定；如需撤下或仅限校内可见，请告知。
        </p>
      </div>
    </section>
  </main>
</template>
