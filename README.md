# MathTeam

> 数学建模竞赛智能组队与协作平台

MathTeam 是一个面向高校数学建模竞赛学生的智能组队与协作平台，提供从**能力画像 → 智能匹配 → 队伍招募 → 申请审批 → 团队交流**的一体化服务。

- **文档版本**：V1.0
- **设计依据**：[《MathTeam 项目简要设计说明书 V1.0》](./MathTeam_项目简要设计说明书_V1.0.pdf)
- **技术路线**：Python + FastAPI + Vue 3 + PostgreSQL + ECharts + NumPy / Scikit-learn

---

## 目录

- [项目简介](#项目简介)
- [主要功能模块](#主要功能模块)
- [系统架构与技术栈](#系统架构与技术栈)
- [推荐算法实现路线](#推荐算法实现路线)
- [开发阶段规划](#开发阶段规划)
- [项目特色与实施建议](#项目特色与实施建议)
- [完整参考实现（后端）](#完整参考实现后端)
- [Vue 3 前端工程](#vue-3-前端工程)
- [FastAPI 实战教程](#fastapi-实战教程)
- [快速开始](#快速开始)
- [目录结构](#目录结构)
- [文档来源](#文档来源)

---

## 项目简介

平台围绕“个人能力画像 — 团队能力画像 — 智能匹配推荐 — 队伍招募 — 申请审批 — 团队交流”的业务流程展开，帮助学生发现自身能力优势、寻找合适队友，并帮助队长高效招募成员。

系统采用 **B/S 模式与前后端分离架构**：

- **前端**：页面展示、交互与数据可视化；
- **后端**：用户认证、业务逻辑、能力分析、匹配推荐与数据访问；
- **数据库**：持久化存储用户、团队、技能、招募与交流数据；
- **通信**：浏览器通过 HTTP/REST API 与 FastAPI 后端交互，实时交流场景可使用 WebSocket。

## 主要功能模块

| 模块 | 说明 |
| --- | --- |
| **2.1 用户信息与权限管理** | 注册、登录、资料维护与账号状态管理；按普通学生、队长、学校管理员、平台管理员划分权限，队长权限与具体团队关联；使用 JWT 认证并在接口层执行权限校验。 |
| **2.2 个人能力图谱系统** | 建立覆盖数学理论、编程实现、数据分析、建模分析、论文写作、竞赛协作等维度的技能档案；维护熟练度、项目/竞赛经历、个人偏好与可投入时间；通过结构化标签和可视化图表展示能力分布。 |
| **2.3 团队能力图谱系统** | 汇总成员个人能力形成团队画像，展示团队优势、技能覆盖与能力短板，并在成员变化后更新能力数据。 |
| **2.4 智能匹配与推荐系统** | 支持学生找团队、团队找成员双向匹配；综合技能匹配度、能力互补性、竞赛经历、角色需求、时间安排与个人偏好计算推荐分数；展示推荐理由、优势项与潜在差距。 |
| **2.5 队伍招募与申请审批系统** | 队长创建/编辑/关闭招募，设置竞赛方向、目标人数、角色与能力要求；学生浏览招募并提交申请、查看状态；队长查看申请者画像并审批，系统校验人数与状态以避免超员或重复申请。 |
| **2.6 首页队伍展示系统** | 首页展示招募中的队伍卡片（简介、竞赛方向、招募人数、能力需求、队伍状态），支持按方向/技能筛选并进入详情页。 |
| **2.7 团队交流与社区系统** | 团队内部交流空间与团队间经验分享；可逐步增加消息通知、实时聊天、讨论主题和文件资源分享。 |
| **2.8 后台管理系统** | 面向学校/平台管理员的用户、团队、招募与内容管理；异常信息处理、账号状态管理与基础运营统计；角色权限限制管理范围并记录关键操作。 |

## 系统架构与技术栈

### 架构分层

```
浏览器 (Vue 3 SPA)
   │  HTTP/REST API · WebSocket（实时交流）
   ▼
后端接口层 (FastAPI) —— 认证 / 参数校验 / 统一异常处理
   ▼
业务服务层 —— 用户 / 能力图谱 / 团队 / 招募 / 审批 / 推荐 / 交流
   ▼
数据访问层 (SQLAlchemy 2.0)
   ▼
数据存储层 (PostgreSQL；Redis 可选：缓存 / 会话辅助 / 消息分发)
```

### 技术选型

| 层级 | 技术选型 | 主要用途 |
| --- | --- | --- |
| 前端 | Vue 3、TypeScript、Vite | 构建响应式单页应用与前端工程 |
| UI 与状态 | Element Plus、Pinia、Vue Router | 组件、全局状态与页面路由管理 |
| 前端通信与可视化 | Axios、ECharts | 接口请求、能力画像与统计图表 |
| 后端 | Python、FastAPI、Pydantic | API 服务、业务逻辑与数据校验 |
| ORM 与迁移 | SQLAlchemy 2.0、Alembic | 数据库操作、模型管理与版本迁移 |
| 数据库与缓存 | PostgreSQL、Redis（可选） | 业务数据持久化、缓存与消息分发 |
| 认证与实时通信 | JWT、WebSocket | 身份认证、权限保护与实时消息 |
| 算法 | NumPy、Pandas、Scikit-learn、NetworkX；PyTorch（后续扩展） | 数据处理、匹配评分、关系分析与后续模型训练 |
| 开发与测试 | VS Code、Git、Docker Compose、pytest、Apifox | 开发协作、环境部署、自动化测试与接口调试 |

### 工程建议（第一版）

- 优先使用 PostgreSQL 作为核心关系型数据库，技能分类、用户技能、团队成员、招募信息与申请记录均采用结构化数据管理。
- 后端先采用**模块化单体架构**，按业务领域拆分代码模块，避免初期引入不必要的微服务复杂度。
- Redis、实时聊天与复杂推荐模型按实际需求分阶段加入，不必启动时一次性部署全部组件。
- 推荐记录保存**评分明细和算法版本**，便于解释结果并进行后续效果评估。

## 推荐算法实现路线

1. **第一阶段：规则驱动的加权评分**。将候选团队/成员的技能匹配、能力互补、经验、角色需求、时间安排与偏好等因素归一化后计算综合分数；推荐结果同时给出可解释的理由，而非只显示一个分数。
2. **第二阶段：数据积累后引入机器学习**。待积累足够的真实匹配与组队结果数据后，评估引入 Scikit-learn 等方法。
3. **后续扩展**：PyTorch 属于可选扩展，不作为第一版必需依赖。

## 开发阶段规划

| 阶段 | 主要工作 | 阶段成果 |
| --- | --- | --- |
| 第一阶段：基础工程 | 搭建 Vue 3 与 FastAPI 项目；配置数据库、代码规范、环境变量与基础测试 | 前后端可运行，基础接口连通 |
| 第二阶段：用户与能力 | 实现注册登录、权限控制、个人资料与个人能力图谱 | 用户可维护个人信息与能力画像 |
| 第三阶段：团队与招募 | 实现团队管理、团队能力画像、招募发布、申请与审批 | 完成主要组队业务闭环 |
| 第四阶段：推荐与交流 | 实现双向匹配推荐、推荐解释、团队交流、通知与后台管理 | 形成可演示的完整平台原型 |

## 项目特色与实施建议

- **能力画像驱动组队**：不只依赖用户自我介绍，而是将技能、经历、角色与偏好结构化，提升队伍发现效率。
- **双向匹配**：同时满足学生找团队与团队找成员两类需求。
- **强调能力互补**：推荐不仅考虑相似技能，也分析团队当前短板与候选人的补足价值。
- **推荐过程可解释**：向用户说明匹配优势、能力缺口与推荐依据，增强推荐可信度。
- **循序渐进**：先完成用户、能力、团队、招募、审批与规则推荐，再逐步完善实时聊天、社区与机器学习能力。

第一版优先保证核心业务闭环稳定：

```
用户注册登录 → 完善个人能力画像 → 创建或加入团队
→ 发布招募 → 提交申请与队长审批 → 查看团队能力与匹配推荐
```

聊天、社区运营与复杂 AI 模型可作为后续迭代内容。

## 完整参考实现（后端）

本仓库已经包含设计说明书 **8 个模块的全部后端实现**，代码带有大量教学注释，可直接运行、对照教程阅读：

| 设计说明书模块 | 实现位置 |
| --- | --- |
| 2.1 用户信息与权限 | `app/api/v1/auth.py`、`app/api/deps.py`、`app/models/user.py` |
| 2.2 个人能力图谱 | `app/services/profile.py`、`app/api/v1/profile.py` |
| 2.3 团队能力图谱 | `app/services/team.py`、`app/api/v1/teams.py` |
| 2.4 智能匹配推荐 | `app/recommender/engine.py`、`app/api/v1/recommendations.py` |
| 2.5 招募与申请审批 | `app/services/recruitment.py`、`app/services/application.py` |
| 2.6 首页队伍展示 | `GET /api/v1/recruitments/cards` |
| 2.7 团队交流与通知 | `app/ws/teams.py`、`app/api/v1/messages.py` |
| 2.8 后台管理 | `app/api/v1/admin.py`（含操作日志与分权限范围） |

技术要点：SQLAlchemy 2.0 声明式模型、OAuth2 + JWT 四级角色、依赖注入分页与权限守卫、状态机 + 行锁防止并发超员、六维可解释加权推荐、WebSocket 群聊、统一异常格式、pytest/TestClient 测试与 Alembic 迁移。

### 演示账号（密码统一 `123456`）

| 用户名 | 角色 | 说明 |
| --- | --- | --- |
| `alice` | 学生 | 已填写技能，可申请队伍 |
| `bob` | 队长 | 「数模先锋队」队长，已发布招募 |
| `carol` | 学生 | 已填写技能 |
| `admin` | 平台管理员 | 可访问全部后台接口 |

> 启动时会幂等地写入 6 个能力维度与上述演示数据；重复启动不会产生重复记录，并会修正旧演示库中已经满员但仍开放的招募状态。

## Vue 3 前端工程

`web/` 目录是按设计说明书技术栈实现的完整前端：**Vue 3 + Vite + TypeScript + Element Plus + Pinia + Vue Router + Axios + ECharts**，代码带中文注释，重点说明前后端如何交互。

| 页面 | 路由 | 对应后端接口 |
| --- | --- | --- |
| 首页发现 | `/` | `/recruitments/cards`、`/applications/recruitments/{id}` |
| 登录 / 注册 | `/login` `/register` | `/auth/login`、`/auth/register`、`/auth/me` |
| 能力画像 | `/profile` | `/profile/me`、`/capabilities`（ECharts 雷达图） |
| 我的团队 / 详情 | `/teams` `/teams/:id` | `/teams/*`、`/recommendations/members`（柱状图看短板） |
| 招募广场 | `/recruitments` | `/recruitments/*` |
| 申请管理 | `/applications` | `/applications/mine`、`/applications/teams/{id}`、审批 |
| 智能推荐 | `/recommendations` | `/recommendations/teams|members|history`（六维评分明细） |
| 团队交流 | `/chat` | `/ws/teams/{id}` + `/messages/teams/{id}` |
| 后台管理 | `/admin` | `/admin/*`（统计饼图、用户启停、招募下架） |

工程要点：

- `src/api/index.ts`：Axios 拦截器统一注入 JWT、统一解析后端 `{code,message,data}` 错误结构；用 `ApiClient` 接口修正拦截器改写返回值后的 TypeScript 类型。
- `src/router/index.ts`：路由守卫检查登录与管理员角色，刷新页面后自动恢复用户资料。
- `src/stores/user.ts`：Pinia 管理登录态与 token（localStorage）。
- `vite.config.ts`：开发服务器把 `/api` 与 `/ws` 代理到 `127.0.0.1:8000`，前后端同域、无跨域问题。
- 团队聊天优先通过 WebSocket `bearer` 子协议传递 JWT，避免把 token 写入 URL 和代理访问日志；旧版查询参数入口保留兼容。

启动方式见下方「快速开始」。

## FastAPI 实战教程

本项目配套一套 **12 章的「边做项目边学 FastAPI」实战教程**，适合已有 Python 基础、想通过真实项目掌握 FastAPI 的学习者。教程覆盖上述 8 个功能模块的完整实现，同时系统讲解框架知识。

📘 **[打开教程总览与学习路线](./docs/tutorial/README.md)**

| 阶段 | 章节 |
| --- | --- |
| 入门基础 | [00 环境准备](./docs/tutorial/00-学习路线与环境准备.md) · [01 第一个应用](./docs/tutorial/01-第一个FastAPI应用.md) · [02 工程化](./docs/tutorial/02-工程化与配置管理.md) |
| 数据与认证 | [03 SQLAlchemy](./docs/tutorial/03-数据建模与SQLAlchemy.md) · [04 JWT 认证](./docs/tutorial/04-用户注册登录与JWT认证.md) · [05 个人能力图谱](./docs/tutorial/05-个人能力图谱.md) |
| 业务闭环 | [06 团队画像](./docs/tutorial/06-团队管理与能力画像.md) · [07 招募展示](./docs/tutorial/07-招募发布与首页展示.md) · [08 申请审批](./docs/tutorial/08-申请审批与业务校验.md) |
| 进阶实战 | [09 智能推荐](./docs/tutorial/09-智能匹配推荐.md) · [10 WebSocket](./docs/tutorial/10-团队交流与WebSocket.md) · [11 测试与部署](./docs/tutorial/11-后台管理与测试部署.md) |

每章包含：场景引入 → 知识点精讲 → 项目实战 → 参考实现 → 踩坑指南 → 课后练习，按章节顺序推进即可逐步构建出完整平台。

## 快速开始

### 环境要求

- Python 3.10+（已在 `.venv` 中验证：Python 3.12 / FastAPI 0.164 / Pydantic v2）
- 数据库默认使用 PostgreSQL；本机开发连接为 `postgresql+psycopg://zhengrui@localhost:5432/mathteam`

### 一键管理全部服务

```bash
./scripts/services.sh start    # 启动 PostgreSQL、后端和前端
./scripts/services.sh status   # 查看运行状态
./scripts/services.sh stop     # 关闭全部服务
./scripts/services.sh restart  # 重启全部服务
```

前后端通过 `screen` 静默运行，日志写入 `.run/logs/`；脚本会自动检查数据库、执行 Alembic 迁移并等待健康检查通过。

### 启动后端

```bash
cd MathTeam
source .venv/bin/activate             # Windows: .venv\Scripts\activate
pip install -r requirements.txt       # 首次运行时安装全部依赖
cp .env.example .env                  # 可选：按需修改配置
brew services start postgresql@16      # macOS 本机 PostgreSQL
createdb mathteam                     # 首次运行；数据库已存在时可跳过
.venv/bin/alembic upgrade head         # 创建或升级表结构
uvicorn main:app --reload
```

启动后访问：

- 接口文档：`http://127.0.0.1:8000/docs`（Swagger UI，34 条 API 路径）
- 根接口：`http://127.0.0.1:8000/` —— 返回欢迎信息
- 健康检查：`http://127.0.0.1:8000/health`
- 接口调试：仓库内 `test_main.http` 可作为请求示例

### 登录与调用示例

```bash
# 1) 登录拿 token（用 /docs 的 Authorize 按钮更方便）
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -d "username=alice&password=123456"

# 2) 带 token 访问需要认证的接口
curl -H "Authorization: Bearer <access_token>" \
  http://127.0.0.1:8000/api/v1/profile/me
```

### 启动前端

```bash
cd web
npm install                           # 已安装过可跳过
npm run dev                           # 打开 http://127.0.0.1:5173
```

> 前端依赖安装若遇到 npm 缓存目录权限问题，可加参数：
> `npm install --cache /tmp/mathteam-npm-cache --registry https://registry.npmmirror.com`

生产构建：`npm run build`（先做 `vue-tsc` 类型检查，再输出 `dist/`）。

### 运行测试 / 数据库迁移

```bash
.venv/bin/python -m pytest tests -q     # 17 个测试，覆盖完整业务闭环与关键权限边界
.venv/bin/alembic upgrade head          # 用 Alembic 建表（生产环境）
docker compose up -d                    # 可选：启动 PostgreSQL + Redis
```

> 注意：测试夹具仍使用独立的内存 SQLite，避免测试污染本机 PostgreSQL。开发运行默认使用 PostgreSQL；`AUTO_CREATE_TABLES=true` 可作为兜底建表，但正式环境应改用 Alembic。

> 生产部署还必须设置 `ENVIRONMENT=production`、独立的 `SECRET_KEY`、`SEED_DEMO_DATA=false`，并关闭默认演示账号写入。应用会拒绝以默认密钥加演示数据启动生产配置。

## 目录结构

```
MathTeam/
├── README.md                         # 本文件
├── MathTeam_项目简要设计说明书_V1.0.pdf
├── main.py                           # 应用入口：组装路由/中间件/异常/数据库
├── requirements.txt                  # 依赖清单（按教程章节注释）
├── .env.example                      # 配置示例
├── docker-compose.yml                # PostgreSQL + Redis
├── alembic.ini / migrations/         # Alembic 迁移配置与初始版本
├── docs/tutorial/                    # FastAPI 实战教程（12 章）
├── test_main.http                    # 接口调试示例
├── web/                              # Vue 3 + Vite + TypeScript 前端工程
│   ├── src/api/                      #   Axios 客户端与全部接口封装
│   ├── src/types/                    #   对齐后端 Schema 的 TypeScript 类型
│   ├── src/router/ src/stores/       #   路由守卫与 Pinia 状态
│   ├── src/layouts/ src/components/  #   主布局与通用组件
│   └── src/views/                    #   9 个业务页面
├── app/
│   ├── core/                         # 配置、安全工具、统一异常
│   ├── db/                           # 引擎、Session、建表与种子数据
│   ├── models/                       # 11 张表的 SQLAlchemy 模型
│   ├── schemas/                      # Pydantic 请求/响应模型
│   ├── api/deps.py                   # 认证、角色守卫、分页依赖
│   ├── api/v1/                       # 9 组 REST 路由
│   ├── services/                     # 画像/团队/招募/审批业务层
│   ├── recommender/                  # 六维可解释推荐引擎
│   └── ws/                           # WebSocket 连接管理与群聊
└── tests/                            # pytest 自动化测试
```

## 文档来源

本 README 依据《MathTeam 项目简要设计说明书 V1.0》整理生成，涵盖其全部章节：项目简介、主要功能模块、系统架构与技术栈、开发阶段规划、项目特色与实施建议。详细设计请查阅原始 PDF 文档。
