"""v1 版本路由汇总。

main.py 只需 include 这一个 router：
    app.include_router(api_router, prefix=settings.API_PREFIX)
版本升级时新建 v2 包，互不干扰。
"""
from fastapi import APIRouter

from app.api.v1 import (
    admin,
    applications,
    auth,
    capabilities,
    messages,
    profile,
    recommendations,
    recruitments,
    teams,
)

router = APIRouter()
router.include_router(auth.router)
router.include_router(capabilities.router)
router.include_router(profile.router)
router.include_router(teams.router)
router.include_router(recruitments.router)
router.include_router(applications.router)
router.include_router(recommendations.router)
router.include_router(messages.router)
router.include_router(admin.router)
