<script setup>
import { RouterLink } from 'vue-router'
import ContestCard from '../components/ContestCard.vue'
import PlaceholderBlock from '../components/PlaceholderBlock.vue'
import { calendar, contests, dataNote, points, results } from '../data/contests'

const openCount = contests.filter((item) => item.status === 'open').length
</script>

<template>
  <main class="page">
    <section class="page-head">
      <div class="container">
        <p class="kicker">竞赛</p>
        <h1>竞赛信息与成绩公示</h1>
        <p class="page-lead">
          全年赛事节点、报名入口、校内选拔安排，以及成绩与积分公示一览。
          当前有 <strong>{{ openCount }}</strong> 项赛事处于报名期。
        </p>
      </div>
    </section>

    <section class="section" id="calendar">
      <div class="container">
        <div class="section-head">
          <div>
            <p class="kicker">竞赛日历</p>
            <h2>{{ calendar.title }}</h2>
          </div>
          <span class="badge badge-soon">制作中</span>
        </div>

        <div class="calendar-slot">
          <PlaceholderBlock
            :title="calendar.title"
            :desc="calendar.note"
            :requirement="calendar.requirement"
            ratio="3 / 2"
          />
        </div>

        <p class="section-foot">
          图片放入 <code>assets/calendar.png</code> 后，替换本区块即可；不需要改其他代码。
        </p>
      </div>
    </section>

    <section class="section" id="contests">
      <div class="container">
        <div class="section-head">
          <div>
            <p class="kicker">竞赛信息发布</p>
            <h2>近期赛事</h2>
          </div>
          <span class="head-note">更新于 2026.11</span>
        </div>

        <div class="contest-grid">
          <ContestCard v-for="item in contests" :key="item.id" :contest="item" />
        </div>

        <p class="section-foot">{{ dataNote }}</p>
      </div>
    </section>

    <section class="section" id="results">
      <div class="container">
        <div class="section-head">
          <div>
            <p class="kicker">成绩公示</p>
            <h2>已结束赛事</h2>
          </div>
          <span class="head-note">名单整理中</span>
        </div>

        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>赛事</th>
                <th>时间</th>
                <th>结果概览</th>
                <th>奖项分布</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in results" :key="item.event">
                <td class="cell-strong">
                  {{ item.event }}
                  <span class="cell-note">{{ item.note }}</span>
                </td>
                <td>{{ item.time }}</td>
                <td>{{ item.summary }}</td>
                <td>{{ item.detail }}</td>
                <td>
                  <span class="badge" :class="`badge-${item.status}`">{{ item.statusText }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="result-placeholder">
          <PlaceholderBlock
            title="获奖名单明细"
            desc="按赛事分组的完整名单：队伍编号、队名、队员、指导教师、奖项等级。"
            requirement="提供 Excel 或飞书表格链接即可，我来接成表格并支持按赛事筛选。"
            ratio="16 / 4"
            compact
          />
        </div>

        <RouterLink class="notice-callout" to="/notice/cumcm-2026-award-draft">
          <span class="nc-tag">公示中</span>
          <span class="nc-main">
            <strong>2026 高教社杯国赛获奖名单（初稿）</strong>
            <span>45 页 · 公示期 2026-11-08 — 11-14 · 可站内逐页阅读或跳官方原文</span>
          </span>
          <span class="nc-go" aria-hidden="true">›</span>
        </RouterLink>
      </div>
    </section>

    <section class="section" id="points">
      <div class="container">
        <div class="section-head">
          <div>
            <p class="kicker">积分公示</p>
            <h2>{{ points.title }}</h2>
          </div>
          <span class="badge badge-soon">整理中</span>
        </div>

        <p class="points-note">{{ points.note }}</p>

        <PlaceholderBlock
          :title="points.title"
          :desc="points.requirement"
          requirement="支持按姓名 / 赛事 / 学期筛选，建议保留历史累计列。"
          ratio="16 / 6"
          compact
        />
      </div>
    </section>

    <section class="section section-cta">
      <div class="container cta-inner">
        <div>
          <h2>要补充或更正信息？</h2>
          <p>竞赛通知、获奖名单、积分明细都可以直接交给协会竞赛部更新。</p>
        </div>
        <RouterLink class="btn btn-solid" to="/committee">联系委员会</RouterLink>
      </div>
    </section>
  </main>
</template>
