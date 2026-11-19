"""申请与审批服务（教程第 08 章，设计说明书 2.5 节）。

这一章是业务校验的集大成者：状态机 + 唯一约束 + 事务 + 行锁。
"""
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessError
from app.models.application import Application, ApplicationStatus
from app.models.capability import Capability
from app.models.message import Notification
from app.models.profile import UserSkill
from app.models.recruitment import Recruitment, RecruitmentStatus
from app.models.team import Team, TeamMember, TeamRole, TeamStatus
from app.models.user import User
from app.schemas.application import ApplicationCreate


# 状态机：键是当前状态，值是允许流转到的目标状态集合
ALLOWED_TRANSITIONS: dict[ApplicationStatus, set[ApplicationStatus]] = {
    ApplicationStatus.PENDING: {ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED},
    ApplicationStatus.ACCEPTED: set(),
    ApplicationStatus.REJECTED: set(),
}


def transition(current: ApplicationStatus, target: ApplicationStatus) -> None:
    """显式流转函数：拒绝任何跳跃或逆向操作。"""
    if target not in ALLOWED_TRANSITIONS[current]:
        raise BusinessError(
            f"不允许从 {current.value} 流转到 {target.value}", code=40010
        )


def _notify(db: Session, user_id: int, title: str, content: str) -> None:
    """写一条站内通知；在线推送由 WebSocket 层负责。"""
    db.add(Notification(user_id=user_id, title=title, content=content))


def apply(
    db: Session, recruitment_id: int, applicant: User, payload: ApplicationCreate
) -> Application:
    """学生提交申请。"""
    rec = db.get(Recruitment, recruitment_id)
    if rec is None:
        raise BusinessError("招募信息不存在", code=40401, http_status=404)
    if rec.status != RecruitmentStatus.OPEN:
        raise BusinessError("该招募已关闭", code=40011)

    team = db.get(Team, rec.team_id)
    if team is None:
        raise BusinessError("团队不存在", code=40401, http_status=404)

    # 预检查：唯一约束会在并发时兜底，但先查一次能给出更友好的错误
    dup = db.scalar(
        select(Application).where(
            Application.recruitment_id == recruitment_id,
            Application.applicant_id == applicant.id,
        )
    )
    if dup:
        raise BusinessError("你已经申请过该招募", code=40012)

    existing_membership = db.scalar(
        select(TeamMember).where(TeamMember.user_id == applicant.id)
    )
    if existing_membership is not None:
        if existing_membership.team_id == team.id:
            raise BusinessError("你已经是该团队成员", code=40013)
        raise BusinessError("每个人只能加入一个团队", code=40005)

    members = db.scalar(
        select(func.count())
        .select_from(TeamMember)
        .where(TeamMember.team_id == team.id)
    )
    if int(members or 0) >= team.max_size:
        raise BusinessError("团队已满员", code=40003)
    if int(members or 0) >= rec.target_size:
        raise BusinessError("该招募已达到目标人数", code=40003)

    application = Application(
        recruitment_id=rec.id,
        team_id=team.id,
        applicant_id=applicant.id,
        message=payload.message,
        status=ApplicationStatus.PENDING,
    )
    db.add(application)
    _notify(
        db,
        team.created_by,
        "新的入队申请",
        f"{applicant.username} 申请加入「{team.name}」",
    )
    db.commit()
    db.refresh(application)
    return application


def review(
    db: Session, application_id: int, reviewer: User, decision: str, note: str | None
) -> Application:
    """队长审批（本章核心）。

    并发安全的关键：with_for_update() 对团队行加排他锁，
    两个队长同时批准不同申请时，后一个会等前一个提交后再数人数，从而不会超员。
    """
    application = db.get(Application, application_id)
    if application is None:
        raise BusinessError("申请不存在", code=40401, http_status=404)

    target = ApplicationStatus.ACCEPTED if decision == "accept" else ApplicationStatus.REJECTED
    transition(application.status, target)

    recruitment = db.scalar(
        select(Recruitment)
        .where(Recruitment.id == application.recruitment_id)
        .with_for_update()
    )
    if recruitment is None:
        raise BusinessError("招募信息不存在", code=40401, http_status=404)
    if recruitment.status != RecruitmentStatus.OPEN:
        raise BusinessError("该招募已关闭，不能继续审批", code=40011)

    applicant = None
    if target == ApplicationStatus.ACCEPTED:
        applicant = db.scalar(
            select(User)
            .where(User.id == application.applicant_id)
            .with_for_update()
        )
        if applicant is None:
            raise BusinessError("申请用户不存在", code=40401, http_status=404)

    # 锁住团队行（SQLite 会忽略 FOR UPDATE，PostgreSQL 下真正生效）
    team = db.scalar(
        select(Team).where(Team.id == application.team_id).with_for_update()
    )
    if team is None:
        raise BusinessError("团队不存在", code=40401, http_status=404)

    if target == ApplicationStatus.ACCEPTED:
        existing_membership = db.scalar(
            select(TeamMember).where(
                TeamMember.user_id == application.applicant_id
            )
        )
        if (
            existing_membership is not None
            and existing_membership.team_id != team.id
        ):
            raise BusinessError("申请人已加入其他团队", code=40005)

        members = db.scalar(
            select(func.count())
            .select_from(TeamMember)
            .where(TeamMember.team_id == team.id)
        )
        if int(members or 0) >= team.max_size:
            raise BusinessError("团队已满员，无法通过申请", code=40003)
        if int(members or 0) >= recruitment.target_size:
            raise BusinessError("该招募已达到目标人数", code=40003)
        if existing_membership is None:
            db.add(
                TeamMember(
                    team_id=team.id,
                    user_id=application.applicant_id,
                    role=TeamRole.MEMBER,
                )
            )
        new_count = int(members or 0) + 1
        if new_count >= team.max_size:
            team.status = TeamStatus.ACTIVE
        from app.services.recruitment import close_completed_recruitments

        close_completed_recruitments(
            db,
            team.id,
            new_count,
            reviewer_id=reviewer.id,
            exclude_application_id=application.id,
        )

    application.status = target
    application.review_note = note
    application.reviewed_at = datetime.now(timezone.utc)
    application.reviewed_by = reviewer.id
    _notify(
        db,
        application.applicant_id,
        "申请结果通知",
        f"你的申请已{'通过' if target == ApplicationStatus.ACCEPTED else '被拒绝'}",
    )
    db.commit()
    db.refresh(application)
    return application


def list_for_team(db: Session, team_id: int) -> list[dict]:
    """队长查看本团队申请，附带申请者资料与技能（批量查询避免 N+1）。"""
    rows = db.execute(
        select(Application, User)
        .join(User, User.id == Application.applicant_id)
        .where(Application.team_id == team_id)
        .order_by(Application.created_at.desc())
    ).all()
    applicant_ids = [u.id for _a, u in rows]
    skill_rows = db.execute(
        select(UserSkill.user_id, Capability.name, UserSkill.level)
        .join(Capability, Capability.id == UserSkill.capability_id)
        .where(UserSkill.user_id.in_(applicant_ids))
    ).all() if applicant_ids else []
    skills_by_user: dict[int, list[dict]] = {}
    for uid, name, level in skill_rows:
        skills_by_user.setdefault(uid, []).append({"name": name, "level": level})

    result = []
    for app, user in rows:
        result.append(
            {
                "id": app.id,
                "recruitment_id": app.recruitment_id,
                "team_id": app.team_id,
                "applicant_id": app.applicant_id,
                "status": app.status,
                "message": app.message,
                "review_note": app.review_note,
                "created_at": app.created_at,
                "reviewed_at": app.reviewed_at,
                "applicant": {
                    "id": user.id,
                    "username": user.username,
                    "real_name": user.real_name,
                    "school": user.school,
                },
                "skills": skills_by_user.get(user.id, []),
            }
        )
    return result
