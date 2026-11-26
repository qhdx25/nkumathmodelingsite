"""个人中心、能力画像与私有简历接口。"""
from datetime import datetime, timezone
from urllib.parse import quote

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.api.deps import CurrentUser, DB
from app.models.application import Application
from app.models.team import TeamMember, TeamRole
from app.models.user import User
from app.core.config import settings
from app.schemas.profile import ProfileOut, ProfileUpdate, ResumeOut
from app.services.profile import get_profile, update_profile
from app.services.resume import (
    can_view_resume,
    resume_storage,
    serialize_resume,
    validate_resume,
)
from app.services.storage import safe_filename

router = APIRouter(prefix="/profile", tags=["个人画像"])


@router.get("/me", response_model=ProfileOut, summary="查看我的画像")
def read_my_profile(current: CurrentUser, db: DB) -> dict:
    return get_profile(db, current, viewer=current)


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
    return get_profile(db, user, viewer=current)


@router.post("/me/resume", response_model=ResumeOut, summary="上传或替换简历")
async def upload_resume(
    current: CurrentUser,
    db: DB,
    file: UploadFile = File(...),
) -> dict:
    filename = safe_filename(file.filename)
    mime = validate_resume(filename, file.content_type)
    stored = await resume_storage.save(
        file,
        original_name=filename,
        max_bytes=settings.RESUME_MAX_BYTES,
    )
    old_key = current.resume_key
    current.resume_key = stored.key
    current.resume_name = filename
    current.resume_mime = mime
    current.resume_size = stored.size
    current.resume_uploaded_at = datetime.now(timezone.utc)
    try:
        db.commit()
        db.refresh(current)
    except Exception:
        db.rollback()
        await resume_storage.delete(stored.key)
        raise
    if old_key and old_key != stored.key:
        await resume_storage.delete(old_key)
    return serialize_resume(current)


@router.delete("/me/resume", summary="删除本人简历")
async def delete_resume(current: CurrentUser, db: DB) -> dict:
    old_key = current.resume_key
    current.resume_key = None
    current.resume_name = None
    current.resume_mime = None
    current.resume_size = None
    current.resume_uploaded_at = None
    db.commit()
    if old_key:
        await resume_storage.delete(old_key)
    return {"message": "简历已删除"}


@router.get(
    "/users/{user_id}/resume",
    summary="下载私有简历",
    response_class=StreamingResponse,
)
async def download_resume(
    user_id: int,
    db: DB,
    current: CurrentUser,
) -> StreamingResponse:
    user = db.get(User, user_id)
    if user is None or not user.resume_name:
        raise HTTPException(status_code=404, detail="简历不存在")
    if not can_view_resume(db, current, user):
        raise HTTPException(status_code=403, detail="无权查看该用户简历")
    if not user.resume_key or not await resume_storage.exists(user.resume_key):
        raise HTTPException(status_code=404, detail="简历文件不存在")

    response = StreamingResponse(
        resume_storage.iter_chunks(user.resume_key),
        media_type=user.resume_mime or "application/octet-stream",
    )
    response.headers["Content-Disposition"] = (
        f"attachment; filename*=UTF-8''{quote(user.resume_name)}"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "private, no-store"
    response.headers["Content-Length"] = str(user.resume_size or 0)
    return response


def _can_view_profile(db, current: User, target: User) -> bool:
    """本人、管理员、同队成员及收到其申请的队长可查看画像。"""
    if current.id == target.id or current.is_admin:
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
