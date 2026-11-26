"""私有简历的存储、可见性判断与响应序列化。"""
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BusinessError
from app.models.application import Application
from app.models.team import TeamMember, TeamRole
from app.models.user import User
from app.services.chat import normalize_attachment_mime
from app.services.storage import LocalAttachmentStorage

RESUME_EXTENSIONS = {".pdf", ".doc", ".docx"}
RESUME_MIME_TYPES = {
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
    ),
}

resume_storage = LocalAttachmentStorage(settings.RESUME_UPLOAD_DIR)


def validate_resume(filename: str, content_type: str | None) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in RESUME_EXTENSIONS:
        raise BusinessError("简历仅支持 PDF、DOC、DOCX 格式", code=40001)
    actual_mime = normalize_attachment_mime(filename, content_type)
    expected_mime = RESUME_MIME_TYPES[suffix]
    if actual_mime not in {"application/octet-stream", expected_mime}:
        raise BusinessError("简历文件类型与扩展名不匹配", code=40001)
    return expected_mime


def can_view_resume(db: Session, viewer: User, target: User) -> bool:
    """简历仅本人、管理员和收到申请人入队申请的队长可查看。"""
    if viewer.id == target.id:
        return True
    if viewer.is_admin:
        return True

    leader_team_ids = set(
        db.scalars(
            select(TeamMember.team_id).where(
                TeamMember.user_id == viewer.id,
                TeamMember.role == TeamRole.LEADER,
            )
        ).all()
    )
    if not leader_team_ids:
        return False
    return (
        db.scalar(
            select(Application.id).where(
                Application.applicant_id == target.id,
                Application.team_id.in_(leader_team_ids),
            )
        )
        is not None
    )


def serialize_resume(user: User) -> dict | None:
    if not user.resume_name:
        return None
    return {
        "name": user.resume_name,
        "mime_type": user.resume_mime or "application/octet-stream",
        "size": user.resume_size or 0,
        "uploaded_at": (
            user.resume_uploaded_at.isoformat()
            if user.resume_uploaded_at
            else None
        ),
        "download_url": f"{settings.API_PREFIX}/profile/users/{user.id}/resume",
    }
