# 官网与协会组队平台部署

官网保持根目录 Vue 项目，`/team` 为协会组队平台入口。独立模块位于 `services/mathteam/`，来源 Team 分支提交 `226a437`，官网基础为 main 提交 `078321c`。通过目录迁入整合，不强行合并无共同祖先的历史。

## 官网 Vercel 项目

- Root Directory：仓库根目录。
- 安装：`npm ci`；构建：`npm run build`；产物：`dist`。
- 配置 `VITE_TEAM_PLATFORM_URL=https://你的组队平台域名` 并重新构建。未设置时显示接入中，不提供无效按钮。
- 保留根目录 vercel.json，官网其他导航不变。

## 平台前端 Vercel 项目

- 新建独立项目，Root Directory 为 `services/mathteam/web`。
- 安装：`npm ci`；构建：`npm run build`；产物：`dist`。
- 配置 `VITE_API_BASE=https://你的后端域名/api/v1`。
- 配置 `VITE_WS_BASE=wss://你的后端域名/ws`。
- 两项均为构建时环境变量，修改后重新部署。生产环境不使用 Vite 开发代理。
- 子目录 vercel.json 提供 SPA 回退，支持直接访问登录、团队详情等页面。

## 后端

在支持持久运行与 WebSocket 的容器或服务器部署 `services/mathteam`，使用其中 Dockerfile。对外使用 HTTPS/WSS，将流量转发至容器 8000 端口。不要将后端数据库地址写入前端变量。

环境变量：

```dotenv
ENVIRONMENT=production
SECRET_KEY=替换为随机长密钥
DATABASE_URL=postgresql+psycopg://用户:密码@数据库地址:5432/mathteam
AUTO_CREATE_TABLES=false
SEED_DEMO_DATA=false
ALLOWED_ORIGINS=https://你的组队平台域名
CHAT_UPLOAD_DIR=/data/chat
RESUME_UPLOAD_DIR=/data/resumes
```

首次发布先在同环境执行 `alembic upgrade head`，再启动应用。挂载持久卷到 `/data`；数据库使用独立 PostgreSQL 并配置备份。生产库不复制本地演示 SQLite 数据库。跨域 WebSocket 代理需保留 Upgrade 与 Sec-WebSocket-Protocol 头。

## 上线验收与回滚

1. 后端 `/health` 正常，迁移成功，生产环境无演示账号。
2. 平台首页、注册、登录、刷新团队详情正常。
3. 验证组队申请审批、权限隔离、简历上传下载及聊天连接。
4. 官网预览中配置平台预览地址，检查 `/team` 和原有培训、资料页面。
5. 验收通过后通过 PR 合并集成分支，再发布三个服务。

平台部署失败时可回滚独立平台；官网入口地址可恢复或清空后重新构建。涉及数据库变更先确认兼容性，不直接自动降级生产数据库。
