"""招募发布与首页展示接口（教程第 07 章）。"""
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import CurrentUser, DB, Paging, require_recruitment_owner
from app.models.recruitment import Recruitment
from app.schemas.common import Page
from app.schemas.recruitment import (
    RecruitmentCreate,
    RecruitmentOut,
    RecruitmentUpdate,
    TeamCard,
)
from app.services import recruitment as recruitment_service

router = APIRouter(prefix="/recruitments", tags=["招募"])


@router.get("", response_model=Page[RecruitmentOut], summary="招募列表（筛选+分页）")
def list_recruitments(
    db: DB,
    paging: Paging,
    track: str | None = Query(None, description="按竞赛方向精确筛选"),
    skill: str | None = Query(None, description="按所需技能筛选"),
) -> dict:
    items, total = recruitment_service.list_recruitments(
        db, paging[0], paging[1], track=track, skill=skill
    )
    return {"items": items, "total": total, "skip": paging[0], "limit": paging[1]}


@router.get("/cards", response_model=Page[TeamCard], summary="首页队伍卡片")
def home_cards(
    db: DB,
    paging: Paging,
    track: str | None = Query(None, description="按竞赛方向精确筛选"),
    skill: str | None = Query(None, description="按所需技能筛选"),
) -> dict:
    """和列表接口共用服务函数，只是把字段裁剪成卡片结构。"""
    items, total = recruitment_service.list_recruitments(
        db, paging[0], paging[1], track=track, skill=skill
    )
    return {
        "items": recruitment_service.build_cards(db, items),
        "total": total,
        "skip": paging[0],
        "limit": paging[1],
    }


@router.get("/{recruitment_id}", response_model=RecruitmentOut, summary="招募详情")
def read_recruitment(recruitment_id: int, db: DB) -> dict:
    rec = db.get(Recruitment, recruitment_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="招募信息不存在")
    return recruitment_service.serialize_recruitment(db, rec)


@router.post(
    "/teams/{team_id}",
    response_model=RecruitmentOut,
    status_code=201,
    summary="队长发布招募",
)
def create_recruitment(
    team_id: int,
    payload: RecruitmentCreate,
    current: CurrentUser,
    db: DB,
) -> dict:
    rec = recruitment_service.create_recruitment(db, team_id, payload, current.id)
    return recruitment_service.serialize_recruitment(db, rec)


@router.patch("/{recruitment_id}", response_model=RecruitmentOut, summary="修改招募")
def patch_recruitment(
    recruitment_id: int,
    payload: RecruitmentUpdate,
    db: DB,
    current=Depends(require_recruitment_owner),
) -> dict:
    """require_team_leader 需要 team_id 路径参数，因此这里把 team_id 放进路径。"""
    rec = db.get(Recruitment, recruitment_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="招募信息不存在")
    updated = recruitment_service.update(db, rec, payload)
    return recruitment_service.serialize_recruitment(db, updated)


@router.post("/{recruitment_id}/close", response_model=RecruitmentOut, summary="关闭招募")
def close_recruitment(
    recruitment_id: int,
    db: DB,
    current=Depends(require_recruitment_owner),
) -> dict:
    rec = db.get(Recruitment, recruitment_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="招募信息不存在")
    return recruitment_service.serialize_recruitment(
        db, recruitment_service.close(db, rec, current.id)
    )
