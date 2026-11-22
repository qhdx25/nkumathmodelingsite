"""能力维度表（教程第 01、03 章）。

对应设计说明书 2.2 节的六大能力维度。这是全项目最基础的一张“字典表”，
用户技能、团队画像、推荐算法都通过 capability_id 引用它。
"""
from sqlalchemy import Enum, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.schemas.capability import CapabilityCategory


class Capability(Base):
    __tablename__ = "capabilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    # SQLAlchemy 的 Enum 列存的是枚举「名字」(FOUNDATION)，
    # 而 Pydantic 对外暴露的是枚举「值」(foundation)，两者由框架自动转换。
    category: Mapped[CapabilityCategory] = mapped_column(Enum(CapabilityCategory))
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
