"""团队消息与通知表（教程第 10 章，设计说明书 2.7 节）。

架构原则：实时与查询分离。
- WebSocket 只负责“把新消息推给在线的人”，不负责历史查询；
- 历史消息走普通 REST GET /teams/{id}/messages，可分页、可缓存；
- 离线用户收不到 WebSocket，于是把通知落库，上线后再拉。
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MessageType(str, enum.Enum):
    TEXT = "text"
    SYSTEM = "system"
    RESOURCE = "resource"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), index=True
    )
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType), default=MessageType.TEXT
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str | None] = mapped_column(String(300), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
