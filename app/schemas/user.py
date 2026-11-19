"""用户相关 Schema（教程第 04 章）。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserRole, UserStatus


class UserCreate(BaseModel):
    """注册请求体：注意没有 role 字段，防止用户自己注册成管理员。"""

    username: str = Field(min_length=3, max_length=50, description="登录用户名")
    email: EmailStr  # 需要 email-validator 包，Pydantic 会自动校验格式
    password: str = Field(min_length=8, max_length=72, description="明文密码，入库前哈希")
    real_name: str | None = Field(default=None, max_length=50)
    school: str | None = Field(default=None, max_length=100)

    @field_validator("username")
    @classmethod
    def strip_username(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("用户名不能为空")
        return cleaned


class UserOut(BaseModel):
    """用户出参：白名单里没有 hashed_password，密码永远不会被序列化出去。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    real_name: str | None = None
    school: str | None = None
    role: UserRole
    status: UserStatus
    created_at: datetime


class Token(BaseModel):
    """OAuth2 标准令牌响应：/docs 的 Authorize 按钮依赖这两个字段名。"""

    access_token: str
    token_type: str = "bearer"


class UserBrief(BaseModel):
    """嵌套在其他响应里的精简用户信息。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    real_name: str | None = None
    school: str | None = None
