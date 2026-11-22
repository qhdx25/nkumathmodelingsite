<script setup>
import { computed, ref } from 'vue'
import { papers } from '../data/papers'

const active = ref(papers[0]?.year)
const current = computed(() => papers.find((y) => y.year === active.value) ?? papers[0])
const orderedGroups = computed(() => {
  const groups = current.value?.groups ?? []
  return [...groups].sort((a, b) => {
    const rank = (title) => /国一|一等奖/.test(title) ? 0 : /国二|二等奖/.test(title) ? 1 : /省奖/.test(title) ? 99 : 50
    return rank(a.title) - rank(b.title)
  })
})

const countOf = (g) => g.subs.reduce((n, s) => n + s.items.length, 0)
const totalOf = (y) => y.groups.reduce((n, g) => n + countOf(g), 0)
const grandTotal = papers.reduce((n, y) => n + totalOf(y), 0)
</script>

<template>
  <div class="papers">
    <div class="papers-head">
      <div class="paper-years" role="group" aria-label="按年份筛选">
        <button
          v-for="y in papers"
          :key="y.year"
          type="button"
          class="chip"
          :class="{ 'is-active': y.year === active }"
          :aria-pressed="y.year === active"
          @click="active = y.year"
        >
          {{ y.year }}<span class="chip-count">{{ totalOf(y) }}</span>
        </button>
      </div>

    </div>

    <div class="paper-groups">
      <details v-for="(g, i) in orderedGroups" :key="g.k" class="paper-group" >
        <summary>
          <span class="paper-key">{{ g.k }}</span>
          <span class="paper-gtitle">{{ g.title }}</span>
          <span class="paper-gcount">{{ countOf(g) }} 篇</span>
        </summary>

        <div class="paper-subs">
          <div v-for="s in g.subs" :key="s.k" class="paper-sub">
            <h4>
              <span class="paper-subkey">{{ s.k }}</span>
              <span>{{ s.title }}</span>
              <em>{{ s.items.length }} 篇</em>
            </h4>
            <ul>
              <li v-for="item in s.items" :key="item.href">
                <a :href="item.href" target="_blank" rel="noreferrer">
                  <span class="paper-tag">{{ item.tag }}</span>
                  <span class="paper-ititle">{{ item.t }}</span>
                  <span class="paper-open" aria-hidden="true">↗</span>
                </a>
              </li>
            </ul>
          </div>
        </div>
      </details>
    </div>
  </div>
</template>
