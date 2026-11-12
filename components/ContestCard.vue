<script setup>
defineProps({
  contest: { type: Object, required: true },
})
</script>

<template>
  <article class="contest-card" :class="`is-${contest.status}`">
    <div class="contest-body">
      <div class="contest-head">
        <span class="badge" :class="`badge-${contest.status}`">{{ contest.statusText }}</span>
        <span class="contest-level">{{ contest.level }}</span>
      </div>

      <h3>{{ contest.name }}</h3>
      <p class="contest-abbr">{{ contest.abbr }}</p>

      <dl class="contest-meta">
        <div>
          <dt>报名截止</dt>
          <dd>{{ contest.registerBy }}</dd>
        </div>
        <div>
          <dt>比赛时间</dt>
          <dd>{{ contest.window }}</dd>
        </div>
      </dl>

      <ul class="contest-tags">
        <li v-for="item in contest.extras" :key="item">{{ item }}</li>
      </ul>

      <p v-if="contest.note" class="contest-note">{{ contest.note }}</p>
    </div>

    <div class="contest-actions">
      <a
        v-if="contest.registerUrl"
        class="btn btn-solid"
        :href="contest.registerUrl"
        target="_blank"
        rel="noreferrer"
      >
        报名入口
      </a>
      <a
        v-if="contest.officialUrl"
        class="btn btn-ghost"
        :href="contest.officialUrl"
        target="_blank"
        rel="noreferrer"
      >
        官网
      </a>
      <span v-if="!contest.registerUrl && !contest.officialUrl" class="btn btn-muted">待发布</span>
      <span v-if="contest.siteName" class="contest-site">{{ contest.siteName }}</span>
    </div>
  </article>
</template>
