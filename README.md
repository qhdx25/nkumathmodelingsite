# NKU-shumo-demo

南开大学数学建模协会官网改版 Demo。基于原站点（`qhdx25/nkumathmodelingsite`）的技术栈重做首页与竞赛页。

- 技术栈：Vue 3 + Vite 7 + vue-router 5，纯静态、无后端
- 体量：源码约 1,300 行，构建后 JS 39 KB（gzip）、CSS 3.7 KB（gzip）
- 位图：**零**。所有图片位置用占位块占位，接入真实素材后替换即可

## 本地运行

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # 产物在 dist/
```

## 目录结构

```
├── App.vue                     外壳：Header + RouterView + Footer
├── router.js                   4 个页面 + 404 兜底，全部路由级懒加载
├── data/
│   ├── site.js                 导航、简介、统计、最新动态、页脚
│   └── contests.js             竞赛日历、赛事信息、成绩公示、积分公示
├── components/
│   ├── SiteHeader.vue          全站唯一导航（原站点复制了 5 份）
│   ├── SiteFooter.vue
│   ├── NewsFeed.vue            最新动态：主推 + 列表，仿南开官网样式
│   ├── ContestCard.vue         赛事卡：状态徽章 / 时间窗 / 报名入口
│   └── PlaceholderBlock.vue    统一占位块
├── pages/
│   ├── HomePage.vue            精简首页
│   ├── CompetitionPage.vue     竞赛日历 / 赛事信息 / 成绩公示 / 积分公示
│   ├── MaterialsPage.vue       资料库入口
│   ├── CommitteePage.vue       组织架构（姓名待确认公示方案）
│   └── NotFoundPage.vue
└── assets/main.css             单一全局样式，南开紫 + 米白
```

## 相对原站点的改动

| 项 | 原站点 | 本 Demo |
|---|---|---|
| 首页区块 | 6 个（轮播 / 概览 / 数学底色 / 协会 / 培训 / 校区） | 3 个（首屏 / 简介三卡 / 最新动态 / 快速入口） |
| 最新动态 | 无 | 主推 1 条 + 列表 4 条，来源标注、可跳原文 |
| 竞赛页 | 无独立页面 | 日历 / 赛事信息 / 成绩公示 / 积分公示 四区块 |
| 首屏图片 | 6.85 MB，4 张同时加载 | 0 字节，纯 CSS 与内联 SVG |
| 导航 | 5 个文件各写一份且不一致 | 单一 `SiteHeader.vue` |
| 站内跳转 | `<a href>` 整页刷新 | `RouterLink` |
| 404 | 空白页 | 独立 404 页 |
| 路由 | 同步 import，单 chunk 138 KB | 懒加载，首页仅 97 KB |
| 成员姓名 | 30 余人真实姓名公开展示 | 按「部门—职务」呈现，姓名待定 |

## 待补充（页面内已用占位块标出）

1. **竞赛日历图片** —— 建议 2400×1600、300 KB 内，放 `assets/calendar.png`
2. **获奖名单明细** —— 五校联赛首届（32 队参赛 / 18 队获奖 / 金 3 银 6 铜 9）等
3. **积分公示表** —— 姓名 / 学号后四位 / 赛事 / 积分 / 累计
4. **成员名单** —— 按「部门 / 职务 / 姓名」三列提供，公示方案待定
5. **培训与讲座排期** —— 主题 / 时间 / 地点 / 主讲

## 数据来源

- 赛事时间与报名入口：各赛事官网（COMAP、mcm.edu.cn、mathorcup.org、赛氪等）
- 动态条目：南开新闻网、数学科学学院公众号原文
- 协会简介：2026 招新推文与十周年座谈会报道

> 标注「参考」的时间为上一赛季日期，仅用于提示大致时间窗，正式报名请以官网通知为准。
