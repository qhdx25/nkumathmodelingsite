"""能力维度接口（教程第 01 章：从内存字典改成数据库驱动）。

这里保留了教程里的 `category: CapabilityCategory | None = None` 查询参数，
正是你之前追问过的 01.2.3 节写法——只不过数据现在来自数据库而不是内存字典。
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.api.deps import DB, Paging, require_role
from app.models.capability import Capability
from app.models.user import UserRole
from app.schemas.capability import CapabilityCategory, CapabilityCreate, CapabilityOut

router = APIRouter(prefix="/capabilities", tags=["能力维度"])


@router.get(
    "",
    response_model=list[CapabilityOut],
    summary="获取能力维度列表",
    description="传 category 时按类别筛选；不传则返回全部。",
)
def list_capabilities(
    db: DB,
    paging: Paging,
    category: CapabilityCategory | None = None,
) -> list[Capability]:
    """db / paging 是由 Depends 注入的，不会出现在请求参数文档里；
    只有 category 是真正的查询参数——FastAPI 靠 Annotated 里的 Depends 区分二者。
    """
    skip, limit = paging
    stmt = select(Capability)
    if category is not None:
        stmt = stmt.where(Capability.category == category)
    return list(db.scalars(stmt.offset(skip).limit(limit)).all())


@router.get(
    "/{capability_id}",
    response_model=CapabilityOut,
    summary="按 ID 获取单个能力维度",
)
def get_capability(capability_id: int, db: DB) -> Capability:
    cap = db.get(Capability, capability_id)
    if cap is None:
        raise HTTPException(status_code=404, detail="能力维度不存在")
    return cap


@router.post(
    "",
    response_model=CapabilityOut,
    status_code=201,
    summary="新建能力维度（仅管理员）",
)
def create_capability(
    payload: CapabilityCreate,
    db: DB,
    current=Depends(require_role(UserRole.SCHOOL_ADMIN, UserRole.PLATFORM_ADMIN)),
) -> Capability:
    """require_role(...) 是依赖工厂：返回的函数再由 Depends 注入。"""
    cap = Capability(
        name=payload.name,
        category=payload.category,
        weight=payload.weight,
        description=payload.description,
    )
    db.add(cap)
    db.commit()
    db.refresh(cap)
    return cap
