"""MathTeam 应用入口。

这个文件现在只做“组装”：创建 FastAPI 实例、挂载中间件/异常处理器/路由、
启动时初始化数据库。所有业务逻辑都在 app/ 包里。

教程第 01 章的临时内存字典 _capabilities 已经在第 03 章被数据库取代，
原来的三个能力维度接口搬到了 app/api/v1/capabilities.py，地址保持不变。
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.db.init_db import init_db
from app.ws.teams import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ lifespan 在服务启动时（yield 前）和关闭时（yield 后）各执行一次。

    比旧版 @app.on_event("startup") 更推荐：启动逻辑和清理逻辑写在一个函数里，
    顺序清晰，也不容易忘记配对。
    """
    init_db()   # 建表 + 幂等插入演示数据
    print(f"[{settings.APP_NAME}] 数据库已就绪 → {settings.DATABASE_URL}")
    yield
    print(f"[{settings.APP_NAME}] 服务已关闭")


app = FastAPI(
    title=settings.APP_NAME,
    description="数学建模竞赛智能组队与协作平台 · 完整参考实现",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS：Vue 3 前端从另一个端口访问后端时，浏览器会先发 OPTIONS 预检请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理器：业务异常、422 校验错误、HTTPException 统一成同一种 JSON 结构
register_exception_handlers(app)

# REST API 统一加 /api/v1 前缀；WebSocket 不带版本前缀
app.include_router(api_router, prefix=settings.API_PREFIX)
app.include_router(ws_router)


@app.get("/", summary="健康检查", tags=["系统"])
def read_root() -> dict:
    """保留教程第 01 章的根路径，方便验证服务是否正常启动。"""
    return {
        "message": "Welcome to MathTeam!",
        "status": "success",
        "docs": "/docs",
        "api": settings.API_PREFIX,
    }


@app.get("/health", summary="存活探针", tags=["系统"])
def health() -> dict:
    """Docker / K8s 健康检查用，不查数据库，永远快速返回。"""
    return {"status": "ok"}
