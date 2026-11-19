"""WebSocket 连接管理器（教程第 10 章 2.3 节）。

为什么需要管理器？
WebSocket 连接是有状态的长连接，无法像普通请求那样用 Depends 传递。
用一个全局单例按 team_id 分组保存活跃连接，才能实现“给本团队所有人广播”。

注意：这是进程内内存方案，只适用于单进程。
多进程部署时要换成 Redis Pub/Sub，让不同 worker 之间能互相转发消息。
"""
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(
        self, team_id: int, websocket: WebSocket, subprotocol: str | None = None
    ) -> None:
        await websocket.accept(subprotocol=subprotocol)
        self.active[team_id].append(websocket)

    def disconnect(self, team_id: int, websocket: WebSocket) -> None:
        connections = self.active.get(team_id, [])
        if websocket in connections:
            connections.remove(websocket)

    async def broadcast(self, team_id: int, payload: dict) -> None:
        """遍历副本发送，避免发送过程中连接断开修改原列表。"""
        for ws in list(self.active.get(team_id, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                # 单个连接失败不能影响其他人
                self.disconnect(team_id, ws)


# 模块级单例：整个应用共享一份连接表
manager = ConnectionManager()
