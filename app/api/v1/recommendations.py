"""智能推荐接口（教程第 09 章）。"""
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DB
from app.models.recommendation import Recommendation
from app.recommender.engine import (
    ALGORITHM_VERSION,
    recommend_members,
    recommend_recruitments,
)
from app.schemas.recommendation import RecommendationItem, RecommendationOut
from app.services.team import is_leader

router = APIRouter(prefix="/recommendations", tags=["智能推荐"])


def _persist(db, user_id: int, items: list[dict]) -> None:
    """把评分明细与算法版本落库，日后可回看“当时为什么推荐”。"""
    for item in items:
        db.add(
            Recommendation(
                user_id=user_id,
                target_type=item["target_type"],
                target_id=item["target_id"],
                score=item["score"],
                breakdown=item["breakdown"],
                strengths=item["strengths"],
                gaps=item["gaps"],
                algorithm_version=ALGORITHM_VERSION,
            )
        )
    db.commit()


@router.get("/teams", response_model=list[RecommendationItem], summary="为我推荐团队")
def recommend_teams(
    current: CurrentUser,
    db: DB,
    top_k: int = Query(10, ge=1, le=50),
) -> list[dict]:
    items = recommend_recruitments(db, current, top_k)
    _persist(db, current.id, items)
    return items


@router.get("/members", response_model=list[RecommendationItem], summary="为队伍推荐成员")
def recommend_candidates(
    current: CurrentUser,
    db: DB,
    team_id: int = Query(..., description="队伍 ID"),
    top_k: int = Query(10, ge=1, le=50),
) -> list[dict]:
    """队长的反向推荐（设计说明书 2.4 的“队伍找人”方向）。"""
    if not is_leader(db, team_id, current.id):
        raise HTTPException(status_code=403, detail="只有队长可以查看候选成员")
    items = recommend_members(db, team_id, top_k)
    _persist(db, current.id, items)
    return items


@router.get("/history", response_model=list[RecommendationOut], summary="我的推荐历史")
def recommendation_history(current: CurrentUser, db: DB) -> list[Recommendation]:
    return list(
        db.scalars(
            select(Recommendation)
            .where(Recommendation.user_id == current.id)
            .order_by(Recommendation.created_at.desc())
            .limit(100)
        ).all()
    )
