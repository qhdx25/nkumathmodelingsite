"""申请与审批接口（教程第 08 章）。"""
from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import (
    CurrentUser,
    DB,
    require_application_reviewer,
    require_team_leader,
)
from app.models.application import Application
from app.schemas.application import (
    ApplicationCreate,
    ApplicationOut,
    ApplicationWithApplicant,
    ReviewPayload,
)
from app.services import application as application_service

router = APIRouter(prefix="/applications", tags=["申请审批"])


@router.post(
    "/recruitments/{recruitment_id}",
    response_model=ApplicationOut,
    status_code=201,
    summary="提交加入申请",
)
def apply_to_recruitment(
    recruitment_id: int,
    payload: ApplicationCreate,
    current: CurrentUser,
    db: DB,
) -> Application:
    return application_service.apply(db, recruitment_id, current, payload)


@router.get("/mine", response_model=list[ApplicationOut], summary="我的申请记录")
def my_applications(current: CurrentUser, db: DB) -> list[Application]:
    return list(
        db.scalars(
            select(Application)
            .where(Application.applicant_id == current.id)
            .order_by(Application.created_at.desc())
        ).all()
    )


@router.get(
    "/teams/{team_id}",
    response_model=list[ApplicationWithApplicant],
    summary="队长查看本队申请",
)
def team_applications(
    team_id: int,
    db: DB,
    current=Depends(require_team_leader),  # team_id 路径参数自动注入到依赖
) -> list[dict]:
    return application_service.list_for_team(db, team_id)


@router.post(
    "/{application_id}/review",
    response_model=ApplicationOut,
    summary="队长审批申请",
)
def review_application(
    application_id: int,
    payload: ReviewPayload,
    db: DB,
    current=Depends(require_application_reviewer),
) -> Application:
    return application_service.review(
        db, application_id, current, payload.decision, payload.review_note
    )
