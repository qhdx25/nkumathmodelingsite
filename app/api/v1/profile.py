"""个人能力画像接口（教程第 05 章）。"""
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUser, DB
from app.models.application import Application
from app.models.team import TeamMember, TeamRole
from app.models.user import User, UserRole
from app.schemas.profile import ProfileOut, ProfileUpdate
from app.services.profile import get_profile, update_profile

router = APIRouter(prefix="/profile", tags=["个人画像"])


@router.get("/me", response_model=ProfileOut, summary="查看我的画像")
def read_my_profile(current: CurrentUser, db: DB) -> dict:
    return get_profile(db, current)


@router.patch("/me", response_model=ProfileOut, summary="更新我的画像")
def update_my_profile(payload: ProfileUpdate, current: CurrentUser, db: DB) -> dict:
    return update_profile(db, current, payload)


@router.get("/users/{user_id}", response_model=ProfileOut, summary="查看他人画像")
def read_user_profile(user_id: int, db: DB, current: CurrentUser) -> dict:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not _can_view_profile(db, current, user):
        raise HTTPException(status_code=403, detail="无权查看该用户画像")
    return get_profile(db, user)


def _can_view_profile(db, current: User, target: User) -> bool:
    """本人、平台管理员、同队成员及收到其申请的队长可查看画像。"""
    if current.id == target.id or current.role == UserRole.PLATFORM_ADMIN:
        return True
    if (
        current.role == UserRole.SCHOOL_ADMIN
        and current.school is not None
        and current.school == target.school
    ):
        return True

    leader_team_ids = set(
        db.scalars(
            select(TeamMember.team_id).where(
                TeamMember.user_id == current.id,
                TeamMember.role == TeamRole.LEADER,
            )
        ).all()
    )
    if not leader_team_ids:
        return False

    target_team_ids = set(
        db.scalars(
            select(TeamMember.team_id).where(
                TeamMember.user_id == target.id,
                TeamMember.team_id.in_(leader_team_ids),
            )
        ).all()
    )
    if target_team_ids:
        return True

    return (
        db.scalar(
            select(Application.id).where(
                Application.applicant_id == target.id,
                Application.team_id.in_(leader_team_ids),
            )
        )
        is not None
    )
