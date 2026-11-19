"""团队表与“带属性的多对多”（教程第 06 章，设计说明书 2.3 节）。

为什么不用简单的 secondary=association_table？
因为“谁是队长”这个信息属于「用户与团队的关系」本身，而不是属于用户或团队。
把它放在关联对象 TeamMember.role 上，才能表达“张三在 A 队是队长、在 B 队是队员”。
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TeamRole(str, enum.Enum):
    LEADER = "leader"
    MEMBER = "member"


class TeamStatus(str, enum.Enum):
    FORMING = "forming"        # 组建中
    RECRUITING = "recruiting"  # 招募中
    ACTIVE = "active"          # 比赛中
    ARCHIVED = "archived"      # 已归档


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    competition_track: Mapped[str] = mapped_column(String(50), index=True)
    max_size: Mapped[int] = mapped_column(Integer, default=3)
    status: Mapped[TeamStatus] = mapped_column(
        Enum(TeamStatus), default=TeamStatus.FORMING, index=True
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)

    members: Mapped[list["TeamMember"]] = relationship(
        "TeamMember", back_populates="team", cascade="all, delete-orphan"
    )
    recruitments: Mapped[list["Recruitment"]] = relationship(
        "Recruitment", back_populates="team", cascade="all, delete-orphan"
    )


class TeamMember(Base):
    __tablename__ = "team_members"
    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uq_team_member"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[TeamRole] = mapped_column(Enum(TeamRole), default=TeamRole.MEMBER)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    team: Mapped["Team"] = relationship("Team", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="memberships")
