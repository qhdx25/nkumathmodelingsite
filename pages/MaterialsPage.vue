<script setup>
import PlaceholderBlock from '../components/PlaceholderBlock.vue'

const feishu = {
  title: '建模资料总入口',
  desc: '历年竞赛真题、优秀论文、常用模型与工具教程，均在飞书知识库内按分类整理。',
  url: 'https://nankai.feishu.cn/wiki/CMSXwe42YiGJtpkxSYHcaO5inwb',
}

const groups = [
  { kicker: '真题', title: '历年竞赛真题', body: '国赛、美赛、MathorCup、五校联赛等历年题目与数据附件。' },
  { kicker: '论文', title: '获奖论文合集', body: '按赛事与题目分类的优秀论文，含获奖等级与队伍信息。' },
  { kicker: '方法', title: '常用模型与算法', body: '预测、优化、评价、分类四类模型的模板代码与使用说明。' },
  { kicker: '工具', title: '工具与教程', body: 'Python / MATLAB 环境配置、绘图规范、论文排版模板。' },
]
</script>

<template>
  <main class="page">
    <section class="page-head">
      <div class="container">
        <p class="kicker">建模资料</p>
        <h1>资料共享，共同进步</h1>
        <p class="page-lead">
          所有资料集中在飞书知识库，按赛事、方法、工具三类归档，持续由学术部维护。
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <a class="feishu-card" :href="feishu.url" target="_blank" rel="noreferrer">
          <div>
            <p class="card-kicker">飞书知识库</p>
            <h2>{{ feishu.title }}</h2>
            <p>{{ feishu.desc }}</p>
          </div>
          <span class="btn btn-solid">打开资料库 ↗</span>
        </a>

        <div class="entry-grid entry-grid-4">
          <article v-for="item in groups" :key="item.title" class="entry-card">
            <p class="card-kicker">{{ item.kicker }}</p>
            <h3>{{ item.title }}</h3>
            <p>{{ item.body }}</p>
          </article>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <div>
            <p class="kicker">培训与讲座</p>
            <h2>专题培训安排</h2>
          </div>
          <span class="badge badge-soon">待补充</span>
        </div>

        <PlaceholderBlock
          title="讲座与培训排期"
          desc="按学期列出专题培训主题、主讲人、时间地点与回放链接。"
          requirement="提供本学期培训计划表（主题 / 时间 / 地点 / 主讲），接入后做成时间轴。"
          ratio="16 / 5"
          compact
        />
      </div>
    </section>
  </main>
</template>
