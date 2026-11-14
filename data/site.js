// 站点基础数据：导航、简介、动态、入口、页脚
// 说明：动态条目均来自公开来源（南开新闻网 / 学院公众号），链接可直达原文

export const nav = [
  { label: '首页', to: '/' },
  { label: '最新动态', to: '/news' },
  { label: '竞赛', to: '/competition' },
  { label: '校队培训', to: '/training' },
  { label: '建模资料', to: '/materials' },
  { label: '组队平台', to: '/team' },
  { label: '信息公示', to: '/notice' },
]

// 顶部信息条右侧的小链接（对标南开官网那一排）
export const topLinks = [
  { label: '加入我们', to: '/recruit' },
  { label: '联系我们', to: '/committee' },
  { label: '资料下载', to: '/materials' },
  { label: '信息公示', to: '/notice' },
  { label: 'English', to: '/en' },
]

// 大图底部紫色横条上的栏目（8 个，与官网同构）
export const stripNav = [
  { label: '最新动态', to: '/news' },
  { label: '通知公告', to: '/notice' },
  { label: '赛事信息', to: '/competition' },
  { label: '校队培训', to: '/training' },
  { label: '建模资料', to: '/materials' },
  { label: '组织架构', to: '/committee' },
  { label: '组队平台', to: '/team' },
]

// 页脚次级入口：不在主导航里，但内容不能丢
export const subNav = [
  { label: '委员会', to: '/committee' },
  { label: '信息公示', to: '/notice' },
]

// 首屏大图轮播：图片来源为南开校园实拍，credit 为摄影署名
export const banners = [
  {
    id: 'nku-01',
    image: '/img/hero/nku-01.jpg',
    credit: '摄影：宗琪琪',
    url: 'https://news.nankai.edu.cn/zhxw/system/2026/11/01/030075089.shtml',
  },
  { id: 'nku-02', image: '/img/hero/nku-02.jpg', credit: '摄影：周嵩娴', url: '' },
  { id: 'nku-03', image: '/img/hero/nku-03.jpg', credit: '摄影：郭子昂', url: '' },
  { id: 'nku-04', image: '/img/hero/nku-04.jpg', credit: '摄影：宗琪琪', url: '' },
  { id: 'nku-05', image: '/img/hero/nku-05.jpg', credit: '摄影：郭子昂', url: '' },
  { id: 'nku-06', image: '/img/hero/nku-06.jpg', credit: '南开大学主楼 · 晚霞', url: '' },
]

export const stats = [
  { value: '2016', label: '协会成立', note: '2026 年成立十周年' },
  { value: '1200+', label: '覆盖参赛学生', note: '面向全校本硕博' },
  { value: '近 300', label: '年均参赛队伍', note: '承办校内最大数模赛事' },
  { value: '10 年', label: '持续运营', note: '以赛促学，学以致用' },
]

export const intro = [
  {
    kicker: '简介',
    title: '数学科学学院下属的学生社团',
    body:
      '南开大学数学建模协会成立于 2016 年，接受学校和学院委托，统筹开展校内数学建模相关工作，服务范围覆盖全校理工科与经管学科的本硕博同学。',
  },
  {
    kicker: '职能',
    title: '承办校内最大规模的数模赛事',
    body:
      '协会核心工作是承办南开大学数学建模竞赛（兼全国大学生数学建模竞赛南开代表队选拔赛）。赛事每年 8 月举办，近 300 支队伍参赛，并承担国赛队伍的选拔与培训组织。',
  },
  {
    kicker: '运转',
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

// 系列专题：对标官网「系列专题」那一排图卡
export const series = [
  {
    tag: '专题',
    title: '天津市五校数学建模联赛',
    note: '五校轮值举办 · 南开承办首届',
    image: '/img/news/wx-league.jpg',
    to: '/news',
  },
  {
    tag: '专题',
    title: '“华为杯”研究生数学建模竞赛',
    note: '研究生组 · 每年 9 月开赛',
    image: '/img/news/wx-huawei.jpg',
    to: '/competition',
  },
  {
    tag: '专题',
    title: '全国大学生数学建模竞赛',
    note: '兼校赛 · 国赛代表队选拔',
    image: '/img/hero/nku-02.jpg',
    to: '/competition',
  },
  {
    tag: '专题',
    title: '校队选拔与梯队训练',
    note: '春季补选 · 教练组带训',
    image: '/img/hero/nku-05.jpg',
    to: '/training',
  },
]

// 栏目总览：与紫色横条上的 8 个栏目一一对应，每个栏目给出更细的落点
export const directory = [
  {
    label: '最新动态',
    to: '/news',
    desc: '协会新闻、活动纪要与媒体报道',
    links: ['五校联赛答辩会', '成立十周年座谈会', '2026 招新启动'],
  },
  {
    label: '通知公告',
    to: '/notice',
    desc: '报名通知、名单公示与信息发布',
    links: ['国赛报名通知', '获奖名单公示', '积分与排名公示'],
  },
  {
    label: '赛事信息',
    to: '/competition',
    desc: '竞赛日历、报名入口与成绩查询',
    links: ['全年竞赛日历', '近期赛事报名', '成绩与积分'],
  },
  {
    label: '校队培训',
    to: '/training',
    desc: '训练体系、讲义回放与选拔安排',
    links: ['培训体系说明', '讲义与回放', '校队选拔办法'],
  },
  {
    label: '建模资料',
    to: '/materials',
    desc: '历年真题、优秀论文与工具链',
    links: ['历年竞赛真题', '优秀论文选编', 'LaTeX / Python / MATLAB'],
  },
  {
    label: '组织架构',
    to: '/committee',
    desc: '理事会、秘书处与四个部门',
    links: ['理事会与常务理事会', '秘书处与竞赛部', '协会章程'],
  },
  {
    label: '组队平台',
    to: '/team',
    desc: '发布招募、寻找队友与经验交流',
    links: ['发布招募信息', '寻找队友', '赛后经验交流'],
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
