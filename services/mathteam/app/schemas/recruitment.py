"""招募相关 Schema（教程第 07 章）。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.recruitment import RecruitmentStatus


class RecruitmentCreate(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    competition_track: str = Field(max_length=50)
    target_size: int = Field(
        ge=1, le=6, description="目标团队总人数（包含现有成员）"
    )
    required_roles: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    description: str | None = Field(default=None, max_length=500)


class RecruitmentUpdate(BaseModel):
    """PATCH 部分更新：所有字段都可选，None 表示“不改”。"""

    title: str | None = Field(default=None, min_length=2, max_length=100)
    competition_track: str | None = Field(default=None, max_length=50)
    target_size: int | None = Field(
        default=None, ge=1, le=6, description="目标团队总人数（包含现有成员）"
    )
    required_roles: list[str] | None = None
    required_skills: list[str] | None = None
    description: str | None = None


class RecruitmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_id: int
    title: str
    competition_track: str
    target_size: int
    required_roles: list[str]
    required_skills: list[str]
    description: str | None = None
    status: RecruitmentStatus
    created_at: datetime
    current_members: int = 0   # 由服务层填充，不是 ORM 字段


class TeamCard(BaseModel):
    """首页卡片：只放列表页需要的字段，减小响应体积。"""

    id: int
    team_id: int
    title: str
    competition_track: str
    target_size: int
    required_skills: list[str]
    current_members: int
    team_name: str
    team_status: str
