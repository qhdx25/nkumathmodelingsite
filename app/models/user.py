"""用户表与权限标记（教程第 04 章，设计说明书 2.1 节）。

设计要点：
- role 表示学生 / 队长的参赛身份，is_admin 独立表示后台管理权限；
- 密码字段叫 hashed_password，名字本身就是提醒：里面绝不是明文；
- “队长”权限有两层含义：全局角色 USER_ROLE.LEADER，以及某支团队里
  TeamMember.role == LEADER（与具体团队关联），后者才是真正的授权依据。
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    """统一的时间戳生成函数，作为 column 的 default（传函数对象，不是调用结果）。"""
    return datetime.now(timezone.utc)


class UserRole(str, enum.Enum):
    STUDENT = "student"          # 普通学生
    LEADER = "leader"            # 队长（全局标识，实际权限看团队成员表）


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
    student_number: Mapped[str | None] = mapped_column(
        String(40), nullable=True, index=True
    )
    college: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    qq: Mapped[str | None] = mapped_column(String(30), nullable=True)
    wechat: Mapped[str | None] = mapped_column(String(100), nullable=True)
    github: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resume_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resume_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resume_mime: Mapped[str | None] = mapped_column(String(120), nullable=True)
    resume_size: Mapped[int | None] = mapped_column(nullable=True)
    resume_uploaded_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.STUDENT, index=True
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, index=True, nullable=False
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
