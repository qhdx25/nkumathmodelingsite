"""历史消息、附件与通知接口（教程第 10 章）。

实时推送走 WebSocket `/ws/teams/{team_id}`；
历史查询和文件上传走这里的 REST 接口，两者分工明确。
"""
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.api.deps import CurrentUser, DB
from app.core.config import settings
from app.models.message import Message, MessageType, Notification
from app.models.user import User
from app.schemas.message import ChatPolicyOut, MessageOut, NotificationOut
from app.services.chat import (
    attachment_is_expired,
    classify_attachment,
    ensure_team_member,
    normalize_attachment_mime,
    serialize_message,
)
from app.services.storage import (
    notify_attachment_created,
    safe_filename,
    storage,
)
from app.ws.manager import manager

router = APIRouter(prefix="/messages", tags=["团队交流"])


@router.get("/teams/{team_id}", response_model=list[MessageOut], summary="团队聊天记录")
def list_messages(
    team_id: int,
    db: DB,
    current: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict]:
    """先校验成员身份，再做分页查询。"""
    if not current.is_admin:
        ensure_team_member(db, team_id, current.id)

    rows = db.execute(
        select(Message, User.username)
        .join(User, User.id == Message.sender_id)
        .where(Message.team_id == team_id)
        .order_by(Message.created_at.asc())
        .offset(skip)
        .limit(limit)
    ).all()
    return [serialize_message(msg, username) for msg, username in rows]


@router.get("/chat-policy", response_model=ChatPolicyOut, summary="聊天附件限制")
def chat_policy() -> dict:
    """前端据此展示限制，避免在本地重复维护一套不准确的上限。"""
    return {
        "max_bytes": settings.CHAT_ATTACHMENT_MAX_BYTES,
        "retention_hours": settings.CHAT_ATTACHMENT_TTL_HOURS,
        "cleanup_interval_seconds": (
            settings.CHAT_ATTACHMENT_CLEANUP_INTERVAL_SECONDS
        ),
        "allowed_kinds": ["image", "video", "file"],
    }


@router.post(
    "/teams/{team_id}/attachments",
    response_model=MessageOut,
    status_code=201,
    summary="发送图片、视频或文件",
)
async def upload_attachment(
    team_id: int,
    db: DB,
    current: CurrentUser,
    file: UploadFile = File(...),
    content: str = Form(default="", max_length=1000),
) -> dict:
    ensure_team_member(db, team_id, current.id)
    filename = safe_filename(file.filename)
    mime = normalize_attachment_mime(filename, file.content_type)
    kind = classify_attachment(filename, mime)
    stored = await storage.save(
        file,
        original_name=filename,
        max_bytes=settings.CHAT_ATTACHMENT_MAX_BYTES,
    )
    message = Message(
        team_id=team_id,
        sender_id=current.id,
        content=(content.strip() or f"[{kind}] {filename}")[:1000],
        message_type=MessageType.RESOURCE,
        attachment_key=stored.key,
        attachment_name=filename,
        attachment_mime=mime,
        attachment_size=stored.size,
        attachment_kind=kind,
        attachment_expires_at=(
            datetime.now(timezone.utc)
            + timedelta(hours=settings.CHAT_ATTACHMENT_TTL_HOURS)
        ),
    )
    try:
        db.add(message)
        db.commit()
        db.refresh(message)
    except Exception:
        db.rollback()
        await storage.delete(stored.key)
        raise

    payload = serialize_message(message, current.username)
    notify_attachment_created()
    await manager.broadcast(team_id, {"type": "message", **payload})
    return payload


@router.get(
    "/attachments/{message_id}/download",
    summary="下载聊天附件",
    response_class=StreamingResponse,
)
async def download_attachment(
    message_id: int,
    db: DB,
    current: CurrentUser,
) -> StreamingResponse:
    message = db.get(Message, message_id)
    if message is None or not message.attachment_name:
        raise HTTPException(status_code=404, detail="附件不存在")
    if not current.is_admin:
        ensure_team_member(db, message.team_id, current.id)
    if (
        message.attachment_key is None
        or attachment_is_expired(message.attachment_expires_at)
    ):
        raise HTTPException(
            status_code=410,
            detail=(
                f"附件已超过 {settings.CHAT_ATTACHMENT_TTL_HOURS} 小时保留期"
            ),
        )
    if not await storage.exists(message.attachment_key):
        raise HTTPException(status_code=410, detail="附件文件已过期")
    # 仅可信的图片/视频 MIME 允许内联，其他文件一律作为附件下载。
    inline = message.attachment_kind in {"image", "video"}
    disposition = "inline" if inline else "attachment"
    response = StreamingResponse(
        storage.iter_chunks(message.attachment_key),
        media_type=message.attachment_mime or "application/octet-stream",
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "private, max-age=3600"
    response.headers["Content-Disposition"] = (
        f"{disposition}; filename*=UTF-8''{quote(message.attachment_name)}"
    )
    response.headers["Content-Length"] = str(message.attachment_size or 0)
    return response


@router.get("/notifications", response_model=list[NotificationOut], summary="我的通知")
def my_notifications(current: CurrentUser, db: DB) -> list[Notification]:
    return list(
        db.scalars(
            select(Notification)
            .where(Notification.user_id == current.id)
            .order_by(Notification.created_at.desc())
            .limit(100)
        ).all()
    )
