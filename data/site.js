// 站点基础数据：导航、简介、动态、入口、页脚
// 说明：动态条目均来自公开来源（南开新闻网 / 学院公众号），链接可直达原文

export const nav = [
  { label: '首页', to: '/' },
  { label: '竞赛', to: '/competition' },
  { label: '校队培训', to: '/training' },
  { label: '建模资料', to: '/materials' },
  { label: '组队平台', to: '/team' },
]

// 页脚次级入口：不在主导航里，但内容不能丢
export const subNav = [
  { label: '委员会', to: '/committee' },
  { label: '信息公示', to: '/notice' },
]

// 首屏轮播位：image 置空时渲染占位块，填入图片路径即自动切换为图片
// 每张都可点击跳转，url 换掉即可
export const banners = [
  {
    id: 'banner-1',
    tag: '学院新闻',
    title: '第一届天津市五校数学建模联赛答辩会在南开举行',
    url: 'https://news.nankai.edu.cn/zhxw/system/2026/11/01/030075089.shtml',
    image: '',
    linkLabel: '南开新闻网原文',
  },
  {
    id: 'banner-2',
    tag: '协会动态',
    title: '2026 招新：加入数学建模协会，从好奇到上手',
    url: 'http://mp.weixin.qq.com/s?__biz=MzkwMzY1NTI1OA==&mid=2247497554&idx=1&sn=bcf90d69a11e11d46a4f709f50f802db',
    image: '',
    linkLabel: '学院公众号推文',
  },
  {
    id: 'banner-3',
    tag: '赛事通知',
    title: '2027 年美国大学生数学建模竞赛报名已开放',
    url: 'https://www.contest.comap.com/undergraduate/contests/mcm/register.php',
    image: '',
    linkLabel: 'COMAP 官方报名页',
  },
]

export const stats = [
  { value: '2016', label: '协会成立', note: '2026 年成立十周年' },
  { value: '1200+', label: '覆盖参赛学生', note: '面向全校本硕博' },
  { value: '近 300', label: '年均参赛队伍', note: '承办校内最大数模赛事' },
  { value: '10 年', label: '持续运营', note: '以赛促学，学以致用' },
]

export const intro = [
  {
    kicker: '我们是谁',
    title: '数学科学学院下属的学生社团',
    body:
      '南开大学数学建模协会成立于 2016 年，接受学校和学院委托，统筹开展校内数学建模相关工作，服务范围覆盖全校理工科与经管学科的本硕博同学。',
  },
  {
    kicker: '我们做什么',
    title: '承办校内最大规模的数模赛事',
    body:
      '协会核心工作是承办南开大学数学建模竞赛（兼全国大学生数学建模竞赛南开代表队选拔赛）。赛事每年 8 月举办，近 300 支队伍参赛，并承担国赛队伍的选拔与培训组织。',
  },
  {
    kicker: '怎么运转',
    title: '理事会决策，四部门执行',
    body:
      '会员代表大会选举产生理事会与常务理事会；下设秘书处（策划室、办公室、财务室）、竞赛部、宣传部与工作委员会，各司其职、协同运转。',
  },
]

// 最新动态：主推第一条 + 列表其余
export const news = [
  {
    date: '2026.11',
    fullDate: '2026-11-01',
    title: '第一届天津市五校数学建模联赛答辩会在南开举行',
    summary:
      '五校 32 支队伍参赛、18 支获奖，评选出金奖 3 项、银奖 6 项、铜奖 9 项。协会负责人作年度工作汇报。',
    source: '南开新闻网',
    url: 'https://news.nankai.edu.cn/zhxw/system/2026/11/01/030075089.shtml',
    featured: true,
  },
  {
    date: '2026.09',
    title: '南开大学数学建模协会 2026 招新启动',
    summary: '会员注册与干事招募同步开放，秘书处、竞赛部、宣传部、工作委员会四个方向。',
    source: '学院公众号',
    url: 'http://mp.weixin.qq.com/s?__biz=MzkwMzY1NTI1OA==&mid=2247497554&idx=1&sn=bcf90d69a11e11d46a4f709f50f802db',
  },
  {
    date: '2026.05',
    fullDate: '2026-05-07',
    title: '南开大学数学建模协会成立十周年座谈会举行',
    summary: '学院与教练组代表回顾十年历程，提出培养"善于沟通工程与数学的翻译队伍"。',
    source: '南开新闻网',
    url: 'https://news.nankai.edu.cn/dcxy/system/2026/05/07/030071789.shtml',
  },
  {
    date: '2026.04',
    title: '2026 年全国大学生数学建模竞赛（兼校赛）报名通知',
    summary: '三人一队、全员为南开在籍本科生，通过飞书群云文档填报组队信息。',
    source: '学院公众号',
    url: 'http://mp.weixin.qq.com/s?__biz=MzU2OTEwNzkzMA==&mid=2247563028&idx=2&sn=3bdb8fff58088c42c1ce36c9f44d3eb3',
  },
  {
    date: '2026.04',
    title: '南开大学数学建模代表队春季补选通知',
    summary: '个人参赛完成一篇建模论文，与校队学员共同排名，按排名确定补选名单。',
    source: '学院公众号',
    url: 'http://mp.weixin.qq.com/s?__biz=MzU2OTEwNzkzMA==&mid=2247562931&idx=4&sn=324e77052cc00498b44f8ab5a1f1176e',
  },
]

export const newsMore = {
  label: '更多动态',
  hint: '关注「南开数院学工」公众号',
  url: 'https://www.cim.nankai.edu.cn/',
}

export const entries = [
  {
    kicker: '竞赛',
    title: '竞赛信息与成绩公示',
    body: '竞赛日历、近期赛事报名入口、成绩与积分公示。',
    to: '/competition',
    action: '进入竞赛页',
  },
  {
    kicker: '训练',
    title: '校队培训',
    body: '培训资料、训练体系与代表队培训通知。',
    to: '/training',
    action: '查看培训',
  },
  {
    kicker: '资料',
    title: '建模资料',
    body: '历年真题、优秀论文、LaTeX / Python / MATLAB 资料。',
    to: '/materials',
    action: '打开资料库',
  },
  {
    kicker: '组队',
    title: '组队平台',
    body: '发布招募、寻找队友、交流经验。',
    to: '/team',
    action: '进入组队平台',
  },
]

export const footerLinks = [
  { label: '南开大学', href: 'https://www.nankai.edu.cn' },
  { label: '数学科学学院', href: 'https://www.cim.nankai.edu.cn' },
  { label: '南开新闻网', href: 'https://news.nankai.edu.cn' },
]

// 原站校区信息，收进页脚
export const campuses = [
  { name: '八里台校区', address: '天津市南开区卫津路 94 号', postcode: '300071' },
  { name: '津南校区', address: '天津海河教育园区同砚路 38 号', postcode: '300350' },
  { name: '泰达校区', address: '天津经济技术开发区宏达街 23 号', postcode: '300457' },
]

// 原站「数学底色」时间线，收进委员会页作为沿革
export const history = [
  { year: '1920', title: '南开数学起点', desc: '南开数学系由姜立夫创立，是中国高校较早设立的数学系之一。' },
  { year: '1985', title: '陈省身数学研究所', desc: '由陈省身先生倡议创办并亲任所长，成为南开数学走向世界的学术名片。' },
  { year: '1997', title: '数学科学学院成立', desc: '形成更完整的人才培养与科研组织结构，为建模训练提供课程与学术支撑。' },
  { year: '今天', title: '服务建模训练', desc: '数学、统计与数据科学等学科资源，为协会的培训、选拔与竞赛提供土壤。' },
]
