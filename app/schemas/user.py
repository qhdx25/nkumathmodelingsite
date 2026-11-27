"""用户相关 Schema（教程第 04 章）。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserRole, UserStatus

NANKAI_EMAIL_DOMAIN = "mail.nankai.edu.cn"


class UserCreate(BaseModel):
    """注册请求体：注意没有 role 字段，防止用户自己注册成管理员。"""

    username: str = Field(min_length=3, max_length=50, description="登录用户名")
    email: EmailStr = Field(
        description=f"仅支持 @{NANKAI_EMAIL_DOMAIN} 邮箱注册"
    )
    password: str = Field(min_length=8, max_length=72, description="明文密码，入库前哈希")
    real_name: str | None = Field(default=None, max_length=50)
    school: str | None = Field(default=None, max_length=100)
    student_number: str | None = Field(default=None, max_length=40)
    college: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=30)

    @field_validator("username")
    @classmethod
    def strip_username(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("用户名不能为空")
        return cleaned

    @field_validator("email")
    @classmethod
    def require_nankai_email(cls, email: EmailStr) -> EmailStr:
        domain = str(email).rsplit("@", 1)[-1].lower()
        if domain != NANKAI_EMAIL_DOMAIN:
            raise ValueError(f"仅支持 @{NANKAI_EMAIL_DOMAIN} 邮箱注册")
        return email


class UserOut(BaseModel):
    """用户出参：白名单里没有 hashed_password，密码永远不会被序列化出去。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    real_name: str | None = None
    school: str | None = None
    student_number: str | None = None
    college: str | None = None
    phone: str | None = None
    qq: str | None = None
    wechat: str | None = None
    github: str | None = None
    role: UserRole
    is_admin: bool
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
    student_number: str | None = None
    college: str | None = None
