"""聊天附件的临时存储与清理。

当前实现把文件保存到本地目录，并对文件名做随机化处理。未来接入 OSS 时，
新增一个实现 ``AttachmentStorage`` 协议的适配器即可，消息路由无需修改。
"""
from __future__ import annotations

import asyncio
import os
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BusinessError
from app.models.message import Message

_SAFE_EXTENSION = re.compile(r"^\.[a-z0-9]{1,12}$")
# 上传后唤醒清理任务，使新文件也能按自己的 24 小时到期时间精确清理。
attachment_expiry_event = asyncio.Event()


@dataclass(frozen=True, slots=True)
class StoredObject:
    key: str
    size: int


class AttachmentStorage(Protocol):
    """存储适配器接口；OSS 实现可在此协议下增加预签名 URL 等能力。"""

    async def save(
        self, upload: UploadFile, *, original_name: str, max_bytes: int
    ) -> StoredObject: ...

    def iter_chunks(
        self, key: str, chunk_size: int = 1024 * 1024
    ) -> AsyncIterator[bytes]: ...

    async def delete(self, key: str) -> bool: ...

    async def exists(self, key: str) -> bool: ...


def safe_filename(filename: str | None) -> str:
    """只保留文件名本身，防止客户端传入路径。"""
    name = Path((filename or "attachment").replace("\\", "/")).name
    name = "".join(ch for ch in name if ch >= " " and ch != "\x7f").strip()
    return (name or "attachment")[:255]


class LocalAttachmentStorage:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        path = (self.root / key).resolve()
        if self.root not in path.parents:
            raise ValueError("非法附件路径")
        return path

    async def save(
        self, upload: UploadFile, *, original_name: str, max_bytes: int
    ) -> StoredObject:
        suffix = Path(original_name).suffix.lower()
        if not _SAFE_EXTENSION.fullmatch(suffix):
            suffix = ""
        day = datetime.now(timezone.utc).strftime("%Y%m%d")
        key = f"{day}/{uuid4().hex}{suffix}"
        target = self._path(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + ".part")
        size = 0
        try:
            with temporary.open("xb") as output:
                while chunk := await upload.read(1024 * 1024):
                    size += len(chunk)
                    if size > max_bytes:
                        raise BusinessError(
                            f"文件不能超过 {max_bytes // (1024 * 1024)} MB",
                            code=41301,
                            http_status=413,
                        )
                    output.write(chunk)
            if size == 0:
                raise BusinessError("不能上传空文件", code=40001)
            os.replace(temporary, target)
            return StoredObject(key=key, size=size)
        except Exception:
            temporary.unlink(missing_ok=True)
            target.unlink(missing_ok=True)
            raise
        finally:
            await upload.close()

    async def iter_chunks(
        self, key: str, chunk_size: int = 1024 * 1024
    ) -> AsyncIterator[bytes]:
        with self._path(key).open("rb") as stream:
            while chunk := await asyncio.to_thread(stream.read, chunk_size):
                yield chunk

    async def delete(self, key: str) -> bool:
        path = self._path(key)
        try:
            path.unlink()
            return True
        except FileNotFoundError:
            return False

    async def exists(self, key: str) -> bool:
        return self._path(key).is_file()


async def cleanup_expired_attachments(
    db: Session, storage: AttachmentStorage
) -> int:
    """删除过期文件，并保留消息元数据作为“附件已过期”的历史记录。"""
    now = datetime.now(timezone.utc)
    messages = db.scalars(
        select(Message).where(
            Message.attachment_key.is_not(None),
            Message.attachment_expires_at.is_not(None),
            Message.attachment_expires_at <= now,
        )
    ).all()
    if not messages:
        return 0

    removed_ids: list[int] = []
    for message in messages:
        if not message.attachment_key:
            continue
        try:
            await storage.delete(message.attachment_key)
            removed_ids.append(message.id)
        except (OSError, ValueError):
            # 权限或路径异常时保留数据库引用，下一轮继续重试，避免“元数据
            # 显示已清理但磁盘文件仍永久残留”。
            continue

    db.execute(
        update(Message)
        .where(Message.id.in_(removed_ids))
        .values(attachment_key=None)
    )
    db.commit()
    return len(removed_ids)


def next_attachment_expiry_delay(db: Session) -> float | None:
    """返回距离最近一个附件到期的秒数；没有未过期附件时返回 None。"""
    next_expiry = db.scalar(
        select(func.min(Message.attachment_expires_at)).where(
            Message.attachment_key.is_not(None),
            Message.attachment_expires_at.is_not(None),
        )
    )
    if next_expiry is None:
        return None
    if next_expiry.tzinfo is None:
        next_expiry = next_expiry.replace(tzinfo=timezone.utc)
    return max(
        (next_expiry - datetime.now(timezone.utc)).total_seconds(),
        0.0,
    )


def notify_attachment_created() -> None:
    attachment_expiry_event.set()


storage: AttachmentStorage = LocalAttachmentStorage(settings.CHAT_UPLOAD_DIR)
