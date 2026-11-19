"""WebSocket / REST 消息 Schema（教程第 10 章）。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.message import MessageType


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_id: int
    sender_id: int
    sender_name: str = ""      # 服务层填充
    content: str
    message_type: MessageType
    created_at: datetime


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    content: str | None = None
    is_read: bool
    created_at: datetime
