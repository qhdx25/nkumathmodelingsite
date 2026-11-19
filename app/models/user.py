"""用户表与角色枚举（教程第 04 章，设计说明书 2.1 节）。

设计要点：
- 角色用 Enum 列而不是自由字符串，杜绝拼错 "admin"/"administrator" 这类问题；
- 密码字段叫 hashed_password，名字本身就是提醒：里面绝不是明文；
- “队长”权限有两层含义：全局角色 USER_ROLE.LEADER，以及某支团队里
  TeamMember.role == LEADER（与具体团队关联），后者才是真正的授权依据。
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    """统一的时间戳生成函数，作为 column 的 default（传函数对象，不是调用结果）。"""
    return datetime.now(timezone.utc)


class UserRole(str, enum.Enum):
    STUDENT = "student"          # 普通学生
    LEADER = "leader"            # 队长（全局标识，实际权限看团队成员表）
    SCHOOL_ADMIN = "school_admin"      # 学校管理员
    PLATFORM_ADMIN = "platform_admin"  # 平台管理员


class UserStatus(str, enum.Enum):
    ACTIVE = "active"       # 正常
    DISABLED = "disabled"   # 被停用，禁止登录


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
    real_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    school: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.STUDENT, index=True
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus), default=UserStatus.ACTIVE, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    # 关系属性本身不是数据库列，是 SQLAlchemy 提供的“导航器”。
    # 字符串形式的类名 "UserSkill" 可以避免循环导入问题。
    skills: Mapped[list["UserSkill"]] = relationship(
        "UserSkill", back_populates="user", cascade="all, delete-orphan"
    )
    profile: Mapped["UserProfile | None"] = relationship(
        "UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    memberships: Mapped[list["TeamMember"]] = relationship(
        "TeamMember", back_populates="user"
    )
