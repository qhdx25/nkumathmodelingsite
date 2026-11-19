"""团队群聊 WebSocket 端点（教程第 10 章）。

架构：WebSocket 只负责实时推送，历史消息仍由 REST 接口提供。
客户端连接：ws://127.0.0.1:8000/ws/teams/1?token=<JWT>
"""
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.message import Message, MessageType
from app.models.team import TeamMember
from app.models.user import User, UserStatus
from app.ws.manager import manager

router = APIRouter()


@router.websocket("/ws/teams/{team_id}")
async def team_chat(
    websocket: WebSocket,
    team_id: int,
    token: str | None = Query(
        None, description="兼容旧客户端的 JWT；新客户端建议使用 WebSocket 子协议"
    ),
    db: Session = Depends(get_db),
) -> None:
    # 1) 认证：WebSocket 握手阶段也能用 Depends，但浏览器 JS 不能设置自定义头，
    #    所以这里改用查询参数传 token（生产环境建议 wss:// 防止 URL 泄漏）。
    protocols = [
        item.strip()
        for item in websocket.headers.get("sec-websocket-protocol", "").split(",")
        if item.strip()
    ]
    protocol_token = (
        protocols[1]
        if len(protocols) >= 2 and protocols[0].lower() == "bearer"
        else None
    )
    accepted_protocol = "bearer" if protocol_token else None
    auth_token = protocol_token or token
    user_id_str = decode_token(auth_token) if auth_token else None
    if user_id_str is None:
        await websocket.close(code=4401, reason="未登录或令牌过期")
        return
    try:
        user = db.get(User, int(user_id_str))
    except (TypeError, ValueError):
        user = None
    if user is None:
        await websocket.close(code=4401, reason="用户不存在")
        return
    if user.status != UserStatus.ACTIVE:
        await websocket.close(code=4403, reason="账号已被停用")
        return

    # 2) 授权：只有团队成员能进入房间
    membership = db.scalar(
        select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == user.id
        )
    )
    if membership is None:
        await websocket.close(code=4403, reason="不是团队成员")
        return

    await manager.connect(team_id, websocket, subprotocol=accepted_protocol)
    await manager.broadcast(
        team_id,
        {"type": "system", "content": f"{user.username} 加入了聊天室", "sender_id": 0},
    )

    try:
        while True:
            # 3) 收消息 → 落库 → 广播给房间内所有人（包括自己）
            data = await websocket.receive_json()
            content = str(data.get("content", "")).strip()
            if not content:
                await websocket.send_json({"type": "error", "content": "消息不能为空"})
                continue
            msg = Message(
                team_id=team_id,
                sender_id=user.id,
                content=content,
                message_type=MessageType.TEXT,
            )
            db.add(msg)
            db.commit()
            db.refresh(msg)
            await manager.broadcast(
                team_id,
                {
                    "type": "message",
                    "id": msg.id,
                    "sender_id": user.id,
                    "sender_name": user.username,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                },
            )
    except WebSocketDisconnect:
        manager.disconnect(team_id, websocket)
        await manager.broadcast(
            team_id,
            {"type": "system", "content": f"{user.username} 离开了聊天室", "sender_id": 0},
        )
