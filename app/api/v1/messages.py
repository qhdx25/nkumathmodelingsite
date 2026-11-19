"""历史消息与通知接口（教程第 10 章）。

实时推送走 WebSocket `/ws/teams/{team_id}`；
历史查询走这里的 REST 接口，两者分工明确。
"""
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DB
from app.models.message import Message, Notification
from app.models.team import TeamMember
from app.models.user import User, UserRole
from app.schemas.message import MessageOut, NotificationOut

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
    membership = db.scalar(
        select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == current.id
        )
    )
    if membership is None and current.role != UserRole.PLATFORM_ADMIN:
        raise HTTPException(status_code=403, detail="不是团队成员")

    rows = db.execute(
        select(Message, User.username)
        .join(User, User.id == Message.sender_id)
        .where(Message.team_id == team_id)
        .order_by(Message.created_at.asc())
        .offset(skip)
        .limit(limit)
    ).all()
    return [
        {
            "id": msg.id,
            "team_id": msg.team_id,
            "sender_id": msg.sender_id,
            "sender_name": username,
            "content": msg.content,
            "message_type": msg.message_type,
            "created_at": msg.created_at,
        }
        for msg, username in rows
    ]


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
