"""团队相关 Schema（教程第 06 章）。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.team import TeamRole, TeamStatus


class TeamCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=500)
    competition_track: str = Field(max_length=50)
    max_size: int = Field(default=3, ge=2, le=6)


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    competition_track: str
    max_size: int
    status: TeamStatus
    created_by: int
    created_at: datetime
    member_count: int = 0


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    role: TeamRole
    joined_at: datetime


class TeamDetail(TeamOut):
    """继承 TeamOut，只追加成员列表——Pydantic 的模型继承很好用。"""

    members: list[MemberOut] = Field(default_factory=list)


class TeamProfileOut(BaseModel):
    """团队能力画像：覆盖率、短板、每项技能的统计。"""

    team_id: int
    team_name: str
    member_count: int
    coverage: dict[str, dict] = Field(default_factory=dict)
    gaps: list[str] = Field(default_factory=list)      # 无人掌握
    weak: list[str] = Field(default_factory=list)      # 平均熟练度 < 3
    composite_score: float = Field(ge=0, le=100)
    score_grade: str
    score_algorithm_version: str
    score_breakdown: dict[str, dict] = Field(default_factory=dict)
    score_summary: str
