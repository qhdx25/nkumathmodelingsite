<script setup>
const steps = [
  { n: '01', title: '注册会员', body: '填写基本信息与建模经历，成为协会会员后可参加全部培训与内部赛。' },
  { n: '02', title: '选择方向', body: '秘书处（策划室 / 办公室 / 财务室）、竞赛部、宣传部、工作委员会，四个方向同步招干事。' },
  { n: '03', title: '参加面试', body: '每学期开学后两周内安排，内容为自我介绍 + 一个简短的情景问题，不考察建模水平。' },
  { n: '04', title: '进入部门', body: '通过后进入试用期，一学期后转正；会员身份与干事身份可以同时具备。' },
]

const roles = [
  { name: '秘书处 · 策划室', body: '赛事策划、流程设计、跨部门协调' },
  { name: '秘书处 · 办公室', body: '会务、档案、值班与物资' },
  { name: '秘书处 · 财务室', body: '预算、报销与账目公示' },
  { name: '竞赛部', body: '赛事承办、报名审核、成绩与积分统计' },
  { name: '宣传部', body: '公众号运营、海报与影像记录' },
  { name: '工作委员会', body: '培训组织、资料整理、专项工作' },
]

const faq = [
  { q: '建模零基础可以加入吗？', a: '可以。招干事不考察建模水平，培训从零开始；会员也可先参加培训再决定是否报名参赛。' },
  { q: '大一可以报名吗？', a: '可以，协会面向全校本硕博同学，低年级同学是每年招新的主要对象。' },
  { q: '需要投入多少时间？', a: '日常以赛事节点为主，赛前一个月较忙；非赛期每周约 2–4 小时。' },
  { q: '招新什么时候开始？', a: '每年 9 月开学后启动，春季学期视部门空缺补招，通知见「最新动态」与学院公众号。' },
]
</script>

<template>
  <main class="page">
    <section class="page-head">
      <div class="container">
        <h1>加入我们</h1>
        <p class="page-lead">
          南开大学数学建模协会每年 9 月招新，会员与干事两条通道同时开放，零基础也可以从培训开始。
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>招新流程</h2>
          <span class="head-note">2026 年招新 · 9 月启动</span>
        </div>
        <ol class="recruit-steps">
          <li v-for="s in steps" :key="s.n">
            <span class="recruit-n">{{ s.n }}</span>
            <h3>{{ s.title }}</h3>
            <p>{{ s.body }}</p>
          </li>
        </ol>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>招新方向</h2>
          <span class="head-note">四个方向，按兴趣选择</span>
        </div>
        <ul class="recruit-roles">
          <li v-for="r in roles" :key="r.name">
            <h3>{{ r.name }}</h3>
            <p>{{ r.body }}</p>
          </li>
        </ul>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>报名方式</h2>
        </div>
        <div class="recruit-apply">
          <p>
            招新通知发布后，通过学院公众号推文内的表单填写报名信息；也欢迎在「组队平台」先找队友一起参加校内赛。
          </p>
          <p class="recruit-meta">
            咨询：数学科学学院学生工作办公室 · 协会秘书处
          </p>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>常见问题</h2>
        </div>
        <dl class="recruit-faq">
          <div v-for="item in faq" :key="item.q">
            <dt>{{ item.q }}</dt>
            <dd>{{ item.a }}</dd>
          </div>
        </dl>
      </div>
    </section>
  </main>
</template>
