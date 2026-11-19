"""个人能力画像表（教程第 05 章，设计说明书 2.2 节）。

建模决策：
- 技能熟练度是“可查询、可统计”的结构化数据 → 用关系表 user_skills；
- 项目/竞赛经历、偏好是“整体读写、不单独查询”的半结构化数据 → 用 JSON 列。

这样设计后，第 6 章的团队画像可以在 SQL 层对 user_skills 做聚合，
而画像更新时只需整体替换 JSON 列，避免复杂的多表 join。
"""
from sqlalchemy import JSON, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserSkill(Base):
    __tablename__ = "user_skills"
    # 联合唯一约束：同一用户同一能力维度只能有一条记录，数据库层面杜绝重复
    __table_args__ = (
        UniqueConstraint("user_id", "capability_id", name="uq_user_capability"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    capability_id: Mapped[int] = mapped_column(ForeignKey("capabilities.id"))
    level: Mapped[int] = mapped_column(Integer)  # 1=了解 … 5=精通

    user: Mapped["User"] = relationship("User", back_populates="skills")
    capability: Mapped["Capability"] = relationship("Capability")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    # user_id 同时是主键和外键 → 一个用户最多一条画像记录（一对一）
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    # JSON 列里存 list[dict]，Python 侧用 model_dump() 得到的结构整体赋值
    projects: Mapped[list] = mapped_column(JSON, default=list)
    competitions: Mapped[list] = mapped_column(JSON, default=list)
    preference: Mapped[dict] = mapped_column(JSON, default=dict)

    user: Mapped["User"] = relationship("User", back_populates="profile")
