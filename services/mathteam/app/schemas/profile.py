"""个人画像 Schema：嵌套模型示例（教程第 05 章 2.2 节）。

写入用 capability_id（数字 ID 稳定、便于校验），
展示时服务层把它换成能力名称，前端拿到的是 SkillView(name=..., level=...)。
"""
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserRole


class SkillLevel(BaseModel):
    capability_id: int
    level: int = Field(ge=1, le=5, description="1=了解，5=精通")


class ProjectExperience(BaseModel):
    title: str
    role: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    award_level: Literal[
        "international",
        "national",
        "provincial",
        "school",
        "participation",
        "other",
    ] | None = Field(
        default=None,
        description="竞赛奖项等级；项目经历可不填",
    )


class Preference(BaseModel):
    preferred_roles: list[str] = Field(default_factory=list)
    avoid_roles: list[str] = Field(default_factory=list)
    preferred_track: str | None = None
    weekly_hours: int = Field(default=10, ge=0, le=80)


class ResumeOut(BaseModel):
    name: str
    mime_type: str
    size: int
    uploaded_at: datetime | None = None
    download_url: str


class ProfileUpdate(BaseModel):
    """个人中心整体更新：基本信息和画像均可按部分更新。"""

    real_name: str | None = Field(default=None, max_length=50)
    school: str | None = Field(default=None, max_length=100)
    student_number: str | None = Field(default=None, max_length=40)
    college: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    qq: str | None = Field(default=None, pattern=r"^\d{5,15}$")
    wechat: str | None = Field(default=None, max_length=100)
    github: str | None = Field(default=None, max_length=100)
    skills: list[SkillLevel] | None = Field(
        default=None,
        max_length=6,
        description="最多六个不重复的能力维度",
    )
    projects: list[ProjectExperience] | None = None
    competitions: list[ProjectExperience] | None = None
    preference: Preference | None = None

    @field_validator("skills")
    @classmethod
    def unique_capability_ids(
        cls, skills: list[SkillLevel] | None
    ) -> list[SkillLevel] | None:
        """同一能力维度只能出现一次，避免触发数据库唯一约束后返回 500。"""
        if skills is None:
            return skills
        ids = [skill.capability_id for skill in skills]
        if len(ids) != len(set(ids)):
            raise ValueError("同一能力维度不能重复添加")
        return skills

    @field_validator(
        "real_name",
        "school",
        "student_number",
        "college",
        "phone",
        "qq",
        "wechat",
        "github",
        mode="before",
    )
    @classmethod
    def blank_string_to_none(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            cleaned = value.strip()
            return cleaned or None
        return value


class SkillView(BaseModel):
    """展示用技能项：名称 + 熟练度 + 权重（用于雷达图）。"""

    capability_id: int
    name: str
    category: str
    level: int
    weight: float


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    role: UserRole
    real_name: str | None = None
    school: str | None = None
    student_number: str | None = None
    college: str | None = None
    phone: str | None = None
    email: EmailStr
    qq: str | None = None
    wechat: str | None = None
    github: str | None = None
    skills: list[SkillView] = Field(default_factory=list)
    projects: list[ProjectExperience] = Field(default_factory=list)
    competitions: list[ProjectExperience] = Field(default_factory=list)
    preference: Preference = Field(default_factory=Preference)
    resume: ResumeOut | None = None
