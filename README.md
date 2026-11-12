# NKU-shumo-demo

南开大学数学建模协会官网改版 Demo。基于原站点（`qhdx25/nkumathmodelingsite`）的技术栈重做首页与竞赛页。

- 技术栈：Vue 3 + Vite 7 + vue-router 5，纯静态、无后端
- 体量：构建后入口 JS 40 KB（gzip）、CSS 5.5 KB（gzip），按路由分包
- 配色：南开大学官网 `www.nankai.edu.cn` 的青莲紫 `#710a53`，辅以浅紫 `#8d3a74`、金 `#cfa972`
- 位图：页面设计本身**零位图**；信息公示的文档页图按需加载，不影响首屏

## 本地运行

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # 产物在 dist/
```

## 目录结构

```
├── App.vue                     外壳：Header + RouterView + Footer
├── router.js                   6 个页面 + 404 兜底，全部路由级懒加载，带 title
├── data/
│   ├── site.js                 导航、简介、统计、最新动态、轮播、页脚
│   ├── contests.js             竞赛日历、赛事信息、成绩公示、积分公示
│   └── notices.js              公示文件元数据 + 公示期状态计算
├── components/
│   ├── SiteHeader.vue          全站唯一导航（原站点复制了 5 份）
│   ├── SiteFooter.vue
│   ├── NewsFeed.vue            最新动态：主推 + 列表，仿南开官网样式
│   ├── ContestCard.vue         赛事卡：状态徽章 / 时间窗 / 报名入口
│   ├── HeroSlider.vue          首屏轮播：整块可点击、图片留空自动降级为占位
│   ├── PageReader.vue          文档阅读器：翻页 / 缩略图 / 方向键 / 进度条
│   └── PlaceholderBlock.vue    统一占位块
├── pages/
│   ├── HomePage.vue            精简首页
│   ├── CompetitionPage.vue     竞赛日历 / 赛事信息 / 成绩公示 / 积分公示
│   ├── NoticePage.vue          信息公示列表（按类别筛选）
│   ├── NoticeDetailPage.vue    公示详情：摘要 / 要点 / 文档阅读器 / 同类文件
│   ├── MaterialsPage.vue       资料库入口
│   ├── CommitteePage.vue       组织架构（姓名待确认公示方案）
│   └── NotFoundPage.vue
└── assets/main.css             单一全局样式，青莲紫 + 米白

public/
├── pages/<slug>/p01.webp…      公示文档的逐页图（正文）
├── pages/<slug>/t01.webp…      同一批的缩略图
└── files/*.pdf                 可下载原件（获奖名单初稿过大，暂未入库）
```

## 信息公示模块

- 列表 `/notice` 支持按「获奖公示 / 会议纪要」筛选，条目显示类别、发布单位、日期、页数、公示期状态
- 详情 `/notice/:slug` 左侧是摘要与要点，右侧是逐页阅读器；有原件时给出「下载 PDF」，有官方来源时给出外链
- **页图是预渲染的静态 WebP，不依赖任何 PDF 运行时**。生成方式：

```bash
# 需要 poppler(pdftoppm) 与 sharp
pdftoppm -scale-to-x 1100 -scale-to-y -1 -r 150 -png 原件.pdf /tmp/p
# 再逐页 sharp → webp（正文 q 72~82，缩略图宽 150）
```

- 新增一份公示文件：放进 `public/pages/<slug>/`、在 `data/notices.js` 里加一条、`file` 指向 `public/files/` 中的 PDF 即可，页面无需改动
- 会议纪要标了 `internal: true`，列表和详情会显示「内部文件」与披露提醒；要撤下只需删掉对应条目

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
| 信息公示 | 无 | 获奖名单 / 会议纪要，可逐页阅读、下载原件 |
| 文档阅读 | 无 | 站内翻页 + 缩略图 + 方向键，移动端可用 |

## 待补充（页面内已用占位块标出）

1. **竞赛日历图片** —— 建议 2400×1600、300 KB 内，放 `assets/calendar.png`
2. **获奖名单明细** —— 五校联赛首届（32 队参赛 / 18 队获奖 / 金 3 银 6 铜 9）等；国赛初稿名单已进信息公示，但南开队伍所在页码待标注
3. **积分公示表** —— 姓名 / 学号后四位 / 赛事 / 积分 / 累计
4. **成员名单** —— 按「部门 / 职务 / 姓名」三列提供，公示方案待定
5. **培训与讲座排期** —— 主题 / 时间 / 地点 / 主讲

## 数据来源

- 赛事时间与报名入口：各赛事官网（COMAP、mcm.edu.cn、mathorcup.org、赛氪等）
- 动态条目：南开新闻网、数学科学学院公众号原文
- 协会简介：2026 招新推文与十周年座谈会报道
- 公示文件：全国大学生数学建模竞赛组委会公示页、协会二届理事会 / 常务理事会会议纪要原件

> 标注「参考」的时间为上一赛季日期，仅用于提示大致时间窗，正式报名请以官网通知为准。
