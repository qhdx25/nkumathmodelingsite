# app/schemas/capability.py
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class CapabilityCategory(str, Enum):
    FOUNDATION = "foundation"      # 数学理论
    IMPLEMENTATION = "implementation"  # 编程实现
    ANALYSIS = "analysis"          # 数据分析
    MODELING = "modeling"          # 建模分析
    WRITING = "writing"            # 论文写作
    COLLABORATION = "collaboration"    # 竞赛协作


class CapabilityCreate(BaseModel):
    name: str = Field(min_length=2, max_length=30, description="维度名称")
    category: CapabilityCategory
    weight: float = Field(default=1.0, gt=0, le=5, description="评分权重")
    description: str | None = Field(default=None, max_length=200)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("维度名称不能为空")
        return cleaned


class CapabilityOut(BaseModel):
    id: int
    name: str
    category: CapabilityCategory
    weight: float
    description: str | None = None