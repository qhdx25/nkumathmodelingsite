<script setup>
defineProps({
  title: { type: String, required: true },
  desc: { type: String, default: '' },
  requirement: { type: String, default: '' },
  ratio: { type: String, default: '16 / 9' },
  compact: { type: Boolean, default: false },
})
</script>

<template>
  <div class="placeholder" :class="{ 'is-compact': compact }" :style="{ aspectRatio: ratio }">
    <span class="ph-badge">待补充</span>
    <div class="ph-body">
      <p class="ph-title">{{ title }}</p>
      <p v-if="desc" class="ph-desc">{{ desc }}</p>
      <p v-if="requirement" class="ph-req">{{ requirement }}</p>
    </div>
  </div>
</template>
