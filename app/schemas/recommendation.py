"""推荐结果 Schema（教程第 09 章）。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DimensionScore(BaseModel):
    """单个评分维度：分数 + 权重 + 人类可读理由。"""

    score: float = Field(ge=0, le=1)
    weight: float = Field(ge=0, le=1)
    reason: str


class ScoreDetail(BaseModel):
    """六个评分维度的明细，体现“可解释推荐”。"""

    skill_match: DimensionScore
    complement: DimensionScore
    experience: DimensionScore
    role_fit: DimensionScore
    time_fit: DimensionScore
    preference_fit: DimensionScore


class RecommendationItem(BaseModel):
    """一次推荐里的单个候选。"""

    target_type: str
    target_id: int
    title: str
    team_id: int | None = None
    score: float = Field(ge=0, le=1)
    breakdown: ScoreDetail
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    target_type: str
    target_id: int
    score: float
    breakdown: dict
    strengths: list[str]
    gaps: list[str]
    algorithm_version: str
    created_at: datetime
