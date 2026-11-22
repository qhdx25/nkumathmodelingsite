"""密码哈希与 JWT 令牌（教程第 04 章）。

安全底线：
1. 数据库里永远只存 bcrypt 哈希后的密码，绝不存明文；
2. bcrypt 自带随机盐，同样的密码每次哈希结果都不同，无法反推原文；
3. JWT 用 SECRET_KEY 签名，令牌内容只是 Base64 编码（不是加密），别往里放敏感信息。
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# schemes=["bcrypt"] 指定哈希算法；deprecated="auto" 让旧算法在校验时自动升级
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """注册时调用：明文 → 哈希串。"""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """登录时调用：把用户输入的明文和库里的哈希比对，只返回 True/False。"""
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """签发 JWT。

    sub（subject）是 JWT 标准字段，这里放用户 ID 的字符串形式。
    exp（expiration）用 UTC 时间戳，jose 会自动按它判断令牌是否过期。
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> str | None:
    """校验签名与过期时间，成功返回 sub（用户 ID 字符串），失败返回 None。"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        # 签名不对、令牌过期、格式错误都会抛 JWTError，统一当作未登录处理
        return None
    return payload.get("sub")
