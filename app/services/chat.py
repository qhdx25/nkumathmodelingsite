"""聊天消息序列化与附件分类。"""
from datetime import datetime, timezone
from mimetypes import guess_type

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BusinessError
from app.models.message import Message
from app.models.team import TeamMember

IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
}
VIDEO_MIME_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
    "video/x-msvideo",
}


def ensure_team_member(db: Session, team_id: int, user_id: int) -> None:
    membership = db.scalar(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        )
    )
    if membership is None:
        raise BusinessError("不是团队成员", code=40301, http_status=403)


def classify_attachment(filename: str | None, content_type: str | None) -> str:
    mime = normalize_attachment_mime(filename, content_type)
    if mime in IMAGE_MIME_TYPES:
        return "image"
    if mime in VIDEO_MIME_TYPES:
        return "video"
    # 避免把 SVG 或未知 image/* 内联展示，防止脚本随同源页面执行。
    return "file"


def normalize_attachment_mime(
    filename: str | None, content_type: str | None
) -> str:
    mime = (content_type or "").split(";", 1)[0].strip().lower()
    if not mime or mime == "application/octet-stream":
        mime = (guess_type(filename or "")[0] or mime).lower()
    return (mime or "application/octet-stream")[:120]


def attachment_is_expired(expires_at: datetime | None) -> bool:
    if expires_at is None:
        return False
    current = datetime.now(timezone.utc)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at <= current


def serialize_message(msg: Message, sender_name: str) -> dict:
    attachment = None
    if msg.attachment_name:
        expired = (
            msg.attachment_key is None
            or attachment_is_expired(msg.attachment_expires_at)
        )
        attachment = {
            "name": msg.attachment_name,
            "kind": msg.attachment_kind or "file",
            "mime_type": msg.attachment_mime or "application/octet-stream",
            "size": msg.attachment_size or 0,
            "expires_at": (
                msg.attachment_expires_at.isoformat()
                if msg.attachment_expires_at
                else None
            ),
            "expired": expired,
            "download_url": None
            if expired
            else (
                f"{settings.API_PREFIX}/messages/attachments/"
                f"{msg.id}/download"
            ),
        }
    return {
        "id": msg.id,
        "team_id": msg.team_id,
        "sender_id": msg.sender_id,
        "sender_name": sender_name,
        "content": msg.content,
        "message_type": msg.message_type.value,
        "attachment": attachment,
        "created_at": msg.created_at.isoformat(),
    }
