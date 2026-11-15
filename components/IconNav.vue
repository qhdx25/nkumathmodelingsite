<script setup>
// 首页底部图标导航：细线图标 + 标签，横向六格（移动端 3×2）
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  lang: { type: String, default: 'zh' },
})
const isEn = computed(() => props.lang === 'en')

const ICONS = {
  calendar:
    '<rect x="3.4" y="5.2" width="17.2" height="15.2" rx="1.6"/><path d="M3.4 9.6h17.2M8 2.9v4.2M16 2.9v4.2"/><path d="m9.1 14.7 2 2 3.7-3.7"/>',
  board:
    '<rect x="3.2" y="4.2" width="17.6" height="11.4" rx="1.2"/><path d="M12 15.6v3.3M8.6 21.4l3.4-2.5 3.4 2.5"/><path d="m7.4 12.2 3-3 2.2 2.2 3.9-4.1"/>',
  folder:
    '<path d="M3.4 7.1V6a1.6 1.6 0 0 1 1.6-1.6h3.9l2 2.1h7.5A1.6 1.6 0 0 1 20 8.1v1.1"/><path d="M3.4 9.2h16.9l-1 9.5a1.6 1.6 0 0 1-1.6 1.4H5.6A1.6 1.6 0 0 1 4 18.7L3.4 9.2Z"/><path d="M12 12.2v4.6M9.9 14.7l2.1 2.1 2.1-2.1"/>',
  users:
    '<circle cx="9.3" cy="8.4" r="3.1"/><path d="M3.4 20.2c0-3.3 2.6-5.6 5.9-5.6s5.9 2.3 5.9 5.6"/><path d="M16.2 5.7a3.1 3.1 0 0 1 0 5.5M17.7 14.9c2.2.7 3.4 2.5 3.4 5.1"/>',
  megaphone:
    '<path d="M3.6 10.3v3.6l11.2 5V5.3L3.6 10.3Z"/><path d="M6.9 15.8v3.4a1.6 1.6 0 0 0 3.2 0v-2.2"/><path d="M18.1 9.3a3.6 3.6 0 0 1 0 5.6"/>',
  join:
    '<circle cx="9.9" cy="8.2" r="3.3"/><path d="M3.6 20.2c0-3.4 2.8-6 6.3-6 1.6 0 3 .5 4.1 1.5"/><path d="M17.6 13.4v5M15.1 15.9h5"/>',
}

const items = computed(() => [
  { label: isEn.value ? 'Competitions' : '赛事信息', to: '/competition', icon: ICONS.calendar },
  { label: isEn.value ? 'Training' : '校队培训', to: '/training', icon: ICONS.board },
  { label: isEn.value ? 'Resources' : '建模资料', to: '/materials', icon: ICONS.folder },
  { label: isEn.value ? 'Team up' : '组队平台', to: '/team', icon: ICONS.users },
  { label: isEn.value ? 'Notices' : '信息公示', to: '/notice', icon: ICONS.megaphone },
  { label: isEn.value ? 'Join us' : '加入我们', to: '/recruit', icon: ICONS.join },
])
</script>

<template>
  <nav class="icon-nav" :aria-label="isEn ? 'Quick links' : '快捷入口'">
    <div class="container">
      <ul class="icon-nav-list">
        <li v-for="item in items" :key="item.to">
          <RouterLink :to="item.to">
            <span class="in-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3"
                   stroke-linecap="round" stroke-linejoin="round" v-html="item.icon" />
            </span>
            <span class="in-label">{{ item.label }}</span>
          </RouterLink>
        </li>
      </ul>
    </div>
  </nav>
</template>
