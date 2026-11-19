"""申请相关 Schema（教程第 08 章）。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.application import ApplicationStatus
from app.schemas.user import UserBrief


class ApplicationCreate(BaseModel):
    message: str | None = Field(default=None, max_length=300)


class ReviewPayload(BaseModel):
    """审批请求体：用 Field(pattern=...) 把 decision 限制成两个值。"""

    decision: str = Field(pattern="^(accept|reject)$", description="accept 或 reject")
    review_note: str | None = Field(default=None, max_length=300)


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recruitment_id: int
    team_id: int
    applicant_id: int
    status: ApplicationStatus
    message: str | None = None
    review_note: str | None = None
    created_at: datetime
    reviewed_at: datetime | None = None


class ApplicationWithApplicant(ApplicationOut):
    """队长视角：在申请基础上附带申请者的简要资料与技能。"""

    applicant: UserBrief | None = None
    skills: list[dict] = Field(default_factory=list)
