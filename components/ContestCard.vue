<script setup>
defineProps({
  contest: { type: Object, required: true },
})
</script>

<template>
  <article class="contest-card">
    <div class="contest-head">
      <span class="contest-abbr">{{ contest.abbr }}</span>
      <span class="contest-level">{{ contest.level }}</span>
      <span class="badge" :class="`badge-${contest.status}`">{{ contest.statusText }}</span>
    </div>

    <div class="contest-body">
      <h3>
        <a v-if="contest.officialUrl" :href="contest.officialUrl" target="_blank" rel="noreferrer">
          {{ contest.name }}
        </a>
        <template v-else>{{ contest.name }}</template>
      </h3>

      <p v-if="contest.note" class="contest-note">{{ contest.note }}</p>

      <div class="contest-meta">
        <div>
          <span>报名截止</span>
          <span>{{ contest.registerBy }}</span>
        </div>
        <div>
          <span>比赛时间</span>
          <span>{{ contest.window }}</span>
        </div>
        <div>
          <span>说明</span>
          <span>{{ contest.extras.join(' · ') }}</span>
        </div>
      </div>

      <div class="contest-actions">
        <a
          v-if="contest.registerUrl"
          class="btn btn-sm btn-solid"
          :href="contest.registerUrl"
          target="_blank"
          rel="noreferrer"
        >
          报名入口
        </a>
        <a
          v-if="contest.officialUrl"
          class="btn btn-sm"
          :href="contest.officialUrl"
          target="_blank"
          rel="noreferrer"
        >
          官网
        </a>
        <span v-if="!contest.registerUrl && !contest.officialUrl" class="btn btn-sm btn-muted">待发布</span>
        <span v-if="contest.siteName" class="contest-site">{{ contest.siteName }}</span>
      </div>
    </div>
  </article>
</template>
