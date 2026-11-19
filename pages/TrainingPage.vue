<script setup>
import HeroSlider from '../components/HeroSlider.vue'
import { lessonLinks, lessonLinks2025, notices } from '../data/training'
const years=['2026','2025']
const yearLessons = (year) => (year === '2025' ? lessonLinks2025 : lessonLinks).map((lesson, index) => ({ ...lesson, href: year === '2026' && index === 0 ? 'https://nankai.feishu.cn/wiki/Ko5ewYHiNiS95qkGtiJcoifvnbc' : year === '2026' && index === 1 ? 'https://nankai.feishu.cn/wiki/Ko5ewYHiNiS95qkGtiJcoifvnbc#share-VMpgddV9CoJr0Nx6By9cBorXngk' : lesson.href }))
const heroItems=Array.from({length:6},(_,i)=>({id:`hero-${i}`,image:`/img/hero/nku-0${i+1}.jpg`,title:'南开大学数学建模协会',url:'#'}))
</script>
<template><main class="page training-page"><HeroSlider :items="heroItems"/><section class="page-head"><div class="container"><h1>校队培训</h1></div></section><section class="section"><div class="container"><div class="section-head"><h2>校队选拔及培训通知</h2></div><ul class="link-list"><li v-for="n in notices" :key="n.title" class="link-row notice-row"><div><span class="link-title">{{n.title}}</span><div v-for="location in n.locations" :key="location" class="notice-detail">{{location}}</div><div class="notice-detail">授课人：{{n.teacher}}</div><div class="notice-detail">{{n.preparation}}</div></div></li></ul></div></section><section class="section"><div class="container"><div class="section-head"><h2>历年培训资料</h2></div><div class="year-directories"><details v-for="year in years" :key="year" class="year-directory"><summary>{{year}} 年 <small>展开 / 收起</small></summary><div class="year-directory-body"><div class="lesson-list"><a v-for="lesson in yearLessons(year)" :key="`${year}-${lesson.title}`" class="lesson-row-link" :href="lesson.href" target="_blank" rel="noopener noreferrer"><span>{{lesson.title}}</span><span>{{lesson.href === '#' ? '链接待补充' : '查看资料 ↗'}}</span></a></div></div></details></div></div></section></main></template>
<style scoped>.year-directories{display:grid;gap:18px}.year-directory{border-top:1px solid var(--line);border-bottom:1px solid var(--line-soft)}.year-directory summary{padding:16px 0;cursor:pointer;font-size:22px;font-weight:600;list-style:none}.year-directory summary::-webkit-details-marker{display:none}.year-directory summary:before{content:'›';display:inline-block;margin-right:8px;color:var(--accent);transition:transform 280ms ease}.year-directory[open] summary:before{transform:rotate(90deg)}.year-directory summary small{margin-left:8px;color:var(--faint);font-size:12px;font-weight:400}.year-directory-body{display:grid;grid-template-rows:0fr;overflow:hidden;transition:grid-template-rows 420ms cubic-bezier(.22,.61,.36,1)}.year-directory[open] .year-directory-body{grid-template-rows:1fr}.year-directory-body>div{min-height:0}.lesson-list{padding:0 0 16px 28px}.lesson-list p{margin:8px 0}.lesson-list a{color:var(--accent)}@media(prefers-reduced-motion:reduce){.year-directory summary:before{transition:none}.year-directory-body{transition:none}}</style>
<style scoped>
.year-directory summary { transition: transform 220ms ease, box-shadow 220ms ease, color 220ms ease; }
.year-directory summary:hover { transform: scale(1.025); box-shadow: 0 10px 26px rgba(113, 10, 83, 0.16); color: var(--accent); }
@media (prefers-reduced-motion: reduce) { .year-directory summary { transition: none; } }
</style>
<style scoped>
.lesson-list p { margin:8px 0; }
.lesson-list p:hover { transform: scale(1.025); box-shadow: 0 10px 26px rgba(113, 10, 83, 0.16); color: var(--accent); }
.lesson-list p:hover a { color: var(--accent); }
@media (prefers-reduced-motion: reduce) { .lesson-list p { margin:8px 0; } }
</style>
<style scoped>
.lesson-list p { margin:8px 0; }
.lesson-list p:hover { transform:scale(1.02); }
.lesson-list p a { position:relative; z-index:1; padding:14px 0; }
.lesson-list p span { padding:14px 0; }
</style>

<style scoped>.lesson-row-link{display:flex;width:100%;box-sizing:border-box;align-items:center;justify-content:space-between;gap:16px;padding:8px 14px;color:var(--text);text-decoration:none;transition:transform 220ms ease,box-shadow 220ms ease,color 220ms ease}.lesson-row-link:hover{transform:scale(1.02);box-shadow:0 10px 26px rgba(113,10,83,.16);color:var(--accent)}.lesson-row-link span:last-child{color:var(--accent)}@media(prefers-reduced-motion:reduce){.lesson-row-link{transition:none}}</style>
