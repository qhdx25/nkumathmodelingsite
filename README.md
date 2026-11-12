# NKU-shumo-demo

南开大学数学建模协会官网改版 Demo。基于原站点（`qhdx25/nkumathmodelingsite`）重做信息架构与视觉。

- 技术栈：Vue 3 + Vite 7 + vue-router 5，纯静态、无后端
- 配色：南开大学官网 `www.nankai.edu.cn` 的青莲紫 `#710a53`，辅以浅紫 `#8d3a74`、金 `#cfa972`
- 构建产物：入口 JS 41 KB（gzip）、CSS 6.8 KB（gzip），按路由分包

## 本地运行

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # 产物在 dist/
```

## 信息架构

主导航五个入口（首页 + 四个栏目）：

| 页面 | 路由 | 内容 | 状态 |
|---|---|---|---|
| 首页 | `/` | 轮播图位 / 简介 / 最新动态 / 栏目入口 | 已建 |
| 竞赛 | `/competition` | 竞赛日历、竞赛信息发布、成绩公示、积分公示 | 已建 |
| 校队培训 | `/training` | 培训资料链接、训练体系、代表队培训通知 | **待建设**（骨架已留） |
| 建模资料 | `/materials` | 历年真题、历年优秀论文、LaTeX、Python、MATLAB | 已建（三类待补） |
| 组队平台 | `/team` | 论坛形态的组队与交流 | **待建设**（骨架已留） |

不在主导航、从页脚进入：`/committee`（组织架构、会议纪要、沿革）、`/notice`（公示文件库）。

## 原站内容去向

原站 4 个页面、11 个数据区块，映射关系如下（**没有丢内容**）：

| 原站内容 | 现在的位置 |
|---|---|
| `slides` 首屏轮播 | 首页轮播位（图片留空 + 整块超链接） |
| `overviewStats` 南开概览 4 条 | 首页数据条（改为协会自身数据）+ 页脚校训与三校区地址 |
| `mathTimeline` 数学沿革 4 条 | 委员会页「南开数学与协会」时间轴 |
| `associationCards` 协会框架 4 卡 | 首页快速入口 4 卡（改为竞赛 / 培训 / 资料 / 组队） |
| `materialCards` 飞书资料入口 | 建模资料页顶部卡片 |
| `resourceColumns` 培训 4 栏 | 校队培训页「四个阶段」 |
| `awardPapers` 97 份获奖论文 | 建模资料 › 历年优秀论文（按年份折叠） |
| `campusCards` 三校区 | 页脚「校区地址」 |
| `committeeOverview` / `committeeDepartments` | 委员会页治理结构与部门 |
| 原站没有的 | 新增：竞赛四区块、信息公示、组队平台 |

原站把上百份论文摊在一个超长页面上，现在改为「年份切换 → 分组折叠」，默认只展开第一组。

## 目录结构

```
├── App.vue                     外壳：Header + RouterView + Footer
├── router.js                   8 条路由 + 404，全部懒加载，带 title
├── data/
│   ├── site.js                 导航、轮播、简介、动态、入口、页脚、沿革
│   ├── contests.js             竞赛日历、赛事、成绩、积分
│   ├── notices.js              公示文件元数据 + 公示期状态计算
│   ├── papers.js               97 份获奖论文（自原站搬迁）
│   ├── materials.js            资料五分类
│   ├── training.js             培训资料与通知
│   └── team.js                 组队平台板块与规划
├── components/
│   ├── SiteHeader.vue          全站唯一导航
│   ├── SiteFooter.vue          四列：简介 / 导航 / 更多 / 校区地址
│   ├── HeroSlider.vue          首屏轮播：整块可点击，图空则降级占位
│   ├── NewsFeed.vue            最新动态：主推 + 列表
│   ├── ContestCard.vue         赛事卡
│   ├── PageReader.vue          文档翻页阅读器
│   ├── PaperLibrary.vue        论文库：年份切换 + 分组折叠
│   └── PlaceholderBlock.vue    统一占位块
├── pages/                      8 个页面
└── assets/main.css             单一全局样式

public/
├── pages/<slug>/p01.webp…      公示文档逐页图
├── pages/<slug>/t01.webp…      缩略图
└── files/*.pdf                 可下载原件（获奖名单初稿 63 MB，未入库）
```

## 占位与待补充

页面内已用占位块或「待补充」标出，逐条对应：

1. **首屏轮播图** —— 三条图位已接好链接，填 `data/site.js` 的 `banners[].image` 即可
2. **竞赛日历图** —— 同学在做，`3:2` 图位留在 `/competition#calendar`
3. **获奖名单明细** —— 五校联赛等分赛事名单；国赛初稿已在信息公示
4. **积分公示表** —— 他人负责，`16:6` 图位已留
5. **培训资料与培训通知** —— 校队培训负责人提供
6. **LaTeX / Python / MATLAB 三类资料** —— 缺什么已写在页面上
7. **组队平台** —— 版式为骨架，功能待实现（规划见页面底部）
8. **成员名单** —— 姓名公示方案待定，当前只列职务与人数

## 文档阅读器（信息公示）

- 列表 `/notice` 按类别筛选；详情 `/notice/:slug` 左侧摘要要点、右侧逐页阅读
- 页图是预渲染的静态 WebP，**不依赖任何 PDF 运行时**：

```bash
pdftoppm -scale-to-x 1100 -scale-to-y -1 -r 150 -png 原件.pdf /tmp/p
# 再逐页 sharp → webp（扫描件 q72，文字件 q82，缩略图宽 150）
```

- 新增一份公示文件：放 `public/pages/<slug>/`，在 `data/notices.js` 加一条，`file` 指向 `public/files/` 里的 PDF

## 数据来源

- 赛事时间与报名入口：各赛事官网（COMAP、mcm.edu.cn、mathorcup.org、赛氪等）
- 动态条目：南开新闻网、数学科学学院公众号原文
- 协会简介：2026 招新推文与十周年座谈会报道
- 公示文件：全国大学生数学建模竞赛组委会公示页、协会理事会 / 常务理事会会议纪要原件

> 标注「参考」的时间为上一赛季日期，仅用于提示时间窗，正式报名以官网通知为准。
