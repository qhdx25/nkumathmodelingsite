<script setup>
const lv = [
  { title: '会员代表大会', desc: '协会最高议事机构，选举产生理事会。' },
  { title: '理事会', desc: '协会日常决策机构，向会员代表大会负责。' },
  { title: '常务理事会', desc: '理事会闭会期间的执行机构，统筹重大事项。' },
]

const departments = [
  {
    name: '秘书处',
    desc: '联络竞赛部与宣传部，承接立项工作，重大事项由秘书长会议专人负责。',
    rooms: [
      { title: '策划室', duty: '活动策划与方案设计，承接立项。' },
      { title: '办公室', duty: '团务、外勤、文书档案与会议纪要。' },
      { title: '财务室', duty: '物资采买、出纳与仓库管理。' },
    ],
  },
  {
    name: '竞赛部',
    desc: '负责各类赛事报名、维护竞赛日历、推进与报名平台合作。',
    rooms: [],
  },
  {
    name: '宣传部',
    desc: '发布报名通知、招募信息与正式通知，转发学术性文章。',
    rooms: [],
  },
  {
    name: '工作委员会',
    desc: '承担跨部门协调，推动部门间配合与事项落地。',
    rooms: [],
  },
]
</script>

<template>
  <main class="page">
    <section class="page-head">
      <div class="container">
        <p class="kicker">组织</p>
        <h1>组织架构与部门职责</h1>
        <p class="page-lead">
          协会在理事会领导下开展工作，下设秘书处、竞赛部、宣传部与工作委员会。
        </p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <div>
            <p class="kicker">治理结构</p>
            <h2>三级议事与执行</h2>
          </div>
        </div>

        <ol class="level-list">
          <li v-for="(item, index) in lv" :key="item.title" class="level-item">
            <span class="level-index">{{ String(index + 1).padStart(2, '0') }}</span>
            <div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.desc }}</p>
            </div>
          </li>
        </ol>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <div>
            <p class="kicker">部门</p>
            <h2>四个执行方向</h2>
          </div>
        </div>

        <div class="dept-grid">
          <article v-for="dept in departments" :key="dept.name" class="dept-card">
            <h3>{{ dept.name }}</h3>
            <p class="dept-desc">{{ dept.desc }}</p>
            <ul v-if="dept.rooms.length" class="dept-rooms">
              <li v-for="room in dept.rooms" :key="room.title">
                <strong>{{ room.title }}</strong>
                <span>{{ room.duty }}</span>
              </li>
            </ul>
          </article>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="notice-card">
          <p class="card-kicker">关于成员名单</p>
          <h3>本 Demo 暂不展示姓名</h3>
          <p>
            原站点将理事会与各部门成员的真实姓名直接放在公开页面上，公网可检索。
            Demo 版改为按「部门 — 职务」呈现，姓名留空待确认。
          </p>
          <ul>
            <li>方案 A：只公示职务与人数，姓名不出现在公网（当前采用）</li>
            <li>方案 B：公示姓名，但仓库转为私有，仅发布构建产物</li>
            <li>方案 C：只公示常务理事会成员姓名，其余按职务</li>
          </ul>
          <p class="notice-foot">确认方案后，把名单按「部门 / 职务 / 姓名」三列给我，即可填入。</p>
        </div>

        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>部门</th>
                <th>职务</th>
                <th>人数</th>
                <th>姓名</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in [
                { dept: '常务理事会', role: '成员', count: '7', name: '待确认公示方案' },
                { dept: '理事会', role: '成员', count: '27', name: '待确认公示方案' },
                { dept: '秘书处', role: '秘书长 / 副秘书长', count: '待补', name: '待确认公示方案' },
                { dept: '竞赛部', role: '部长 / 副部长', count: '待补', name: '待确认公示方案' },
                { dept: '宣传部', role: '部长 / 副部长', count: '待补', name: '待确认公示方案' },
                { dept: '工作委员会', role: '负责人', count: '待补', name: '待确认公示方案' },
              ]" :key="row.dept + row.role">
                <td class="cell-strong">{{ row.dept }}</td>
                <td>{{ row.role }}</td>
                <td>{{ row.count }}</td>
                <td class="cell-muted">{{ row.name }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </main>
</template>
