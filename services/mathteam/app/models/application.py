"""加入申请表（教程第 08 章，设计说明书 2.5 节）。

两个关键约束：
1. UniqueConstraint(recruitment_id, applicant_id) —— 同一人不能重复申请同一招募；
2. 状态字段只允许按状态机流转：pending → accepted / rejected，见 services/application.py。

审批时还会用 with_for_update() 锁住团队行，防止并发通过导致队伍超员。
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint(
            "recruitment_id", "applicant_id", name="uq_recruitment_applicant"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    recruitment_id: Mapped[int] = mapped_column(
        ForeignKey("recruitments.id", ondelete="CASCADE"), index=True
    )
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), index=True
    )
    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.PENDING, index=True
    )
    review_note: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reviewed_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
