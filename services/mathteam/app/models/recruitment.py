"""招募信息表（教程第 07 章，设计说明书 2.5、2.6 节）。

required_roles / required_skills 用 JSON 数组存：
- 数量不定，建多张子表会让查询变复杂；
- 只在“展示卡片”和“推荐打分”时整体读取，不需要单独按某个 role 做外键 join。
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RecruitmentStatus(str, enum.Enum):
    OPEN = "open"        # 招募中
    CLOSED = "closed"    # 已关闭


class Recruitment(Base):
    __tablename__ = "recruitments"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(100))
    competition_track: Mapped[str] = mapped_column(String(50), index=True)
    target_size: Mapped[int] = mapped_column(Integer)
    required_roles: Mapped[list] = mapped_column(JSON, default=list)
    required_skills: Mapped[list] = mapped_column(JSON, default=list)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[RecruitmentStatus] = mapped_column(
        Enum(RecruitmentStatus), default=RecruitmentStatus.OPEN, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)

    team: Mapped["Team"] = relationship("Team", back_populates="recruitments")
