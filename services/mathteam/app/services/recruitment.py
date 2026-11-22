"""招募与首页服务（教程第 07 章）。"""
from datetime import datetime, timezone
import json

from sqlalchemy import cast, func, or_, select, String
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessError
from app.models.application import Application, ApplicationStatus
from app.models.message import Notification
from app.models.recruitment import Recruitment, RecruitmentStatus
from app.models.team import Team, TeamMember, TeamStatus
from app.schemas.recruitment import RecruitmentCreate, RecruitmentUpdate


def _member_counts(db: Session, team_ids: list[int]) -> dict[int, int]:
    """一次 GROUP BY 查出多支团队的人数，避免卡片循环里逐条查询（N+1）。"""
    if not team_ids:
        return {}
    rows = db.execute(
        select(TeamMember.team_id, func.count(TeamMember.id))
        .where(TeamMember.team_id.in_(team_ids))
        .group_by(TeamMember.team_id)
    ).all()
    return {tid: int(cnt) for tid, cnt in rows}


def list_recruitments(
    db: Session,
    skip: int,
    limit: int,
    track: str | None = None,
    skill: str | None = None,
    only_open: bool = True,
) -> tuple[list[dict], int]:
    """动态条件 + 分页：返回 (当前页数据, 总条数)。

    动态 WHERE 的写法是「先造基础语句，再按条件追加 where」，
    不要靠 if/else 拼字符串 SQL——那样会有注入风险。
    """
    stmt = select(Recruitment)
    if only_open:
        stmt = stmt.where(Recruitment.status == RecruitmentStatus.OPEN)
    if track:
        stmt = stmt.where(Recruitment.competition_track == track)
    if skill:
        # 同时匹配原字符和 ensure_ascii 转义形式，兼容 SQLite 的 JSON 文本存储。
        escaped_skill = json.dumps(skill, ensure_ascii=True)[1:-1]
        stmt = stmt.where(
            or_(
                cast(Recruitment.required_skills, String).contains(skill),
                cast(Recruitment.required_skills, String).contains(escaped_skill),
            )
        )

    total = len(db.scalars(stmt).all())
    rows = db.scalars(stmt.order_by(Recruitment.created_at.desc()).offset(skip).limit(limit)).all()
    return [serialize_recruitment(db, r) for r in rows], total


def serialize_recruitment(db: Session, r: Recruitment) -> dict:
    """ORM 对象 → 响应字典，并补上 current_members（计算字段）。"""
    team = db.get(Team, r.team_id)
    count = _member_counts(db, [r.team_id]).get(r.team_id, 0)
    return {
        "id": r.id,
        "team_id": r.team_id,
        "title": r.title,
        "competition_track": r.competition_track,
        "target_size": r.target_size,
        "required_roles": r.required_roles or [],
        "required_skills": r.required_skills or [],
        "description": r.description,
        "status": r.status,
        "created_at": r.created_at,
        "current_members": count,
        "_team_name": team.name if team else "",
        "_team_status": team.status.value if team else "",
    }


def build_cards(db: Session, recruitments: list[dict]) -> list[dict]:
    """把 serialize 出来的完整字典裁剪成首页卡片字段。"""
    return [
        {
            "id": r["id"],
            "team_id": r["team_id"],
            "title": r["title"],
            "competition_track": r["competition_track"],
            "target_size": r["target_size"],
            "required_skills": r["required_skills"],
            "current_members": r["current_members"],
            "team_name": r["_team_name"],
            "team_status": r["_team_status"],
        }
        for r in recruitments
    ]


def create_recruitment(
    db: Session, team_id: int, payload: RecruitmentCreate, leader_id: int
) -> Recruitment:
    team = db.get(Team, team_id)
    if team is None:
        raise BusinessError("团队不存在", code=40401, http_status=404)
    from app.services.team import is_leader, team_member_count

    if not is_leader(db, team_id, leader_id):
        raise BusinessError("只有队长可以发布招募", code=40301, http_status=403)
    existing = db.scalar(
        select(Recruitment).where(
            Recruitment.team_id == team_id,
            Recruitment.status == RecruitmentStatus.OPEN,
        )
    )
    if existing is not None:
        raise BusinessError("该团队已有开放招募", code=40022)

    member_count = team_member_count(db, team_id)
    _validate_target_size(payload.target_size, member_count, team.max_size)

    rec = Recruitment(
        team_id=team_id,
        title=payload.title,
        competition_track=payload.competition_track,
        target_size=payload.target_size,
        required_roles=payload.required_roles,
        required_skills=payload.required_skills,
        description=payload.description,
        status=RecruitmentStatus.OPEN,
    )
    team.status = TeamStatus.RECRUITING
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def update(
    db: Session, recruitment: Recruitment, payload: RecruitmentUpdate
) -> Recruitment:
    """PATCH 部分更新：exclude_unset 区分「没传」和「显式传 None」。"""
    data = payload.model_dump(exclude_unset=True)
    if data.get("target_size") is not None:
        from app.services.team import team_member_count

        team = db.get(Team, recruitment.team_id)
        if team is None:
            raise BusinessError("团队不存在", code=40401, http_status=404)
        _validate_target_size(
            data["target_size"], team_member_count(db, team.id), team.max_size
        )
    for field, value in data.items():
        setattr(recruitment, field, value)
    db.commit()
    db.refresh(recruitment)
    return recruitment


def _validate_target_size(target_size: int, current: int, max_size: int) -> None:
    """target_size 表示团队目标总人数，必须位于当前人数和团队上限之间。"""
    if target_size <= current:
        raise BusinessError("招募目标人数必须大于当前团队人数", code=40020)
    if target_size > max_size:
        raise BusinessError("招募目标人数不能超过团队容量", code=40021)


def close_completed_recruitments(
    db: Session,
    team_id: int,
    member_count: int,
    reviewer_id: int | None = None,
    exclude_application_id: int | None = None,
) -> None:
    """成员变化后关闭达标招募，并结束其余待处理申请。"""
    recruitments = db.scalars(
        select(Recruitment).where(
            Recruitment.team_id == team_id,
            Recruitment.status == RecruitmentStatus.OPEN,
        )
    ).all()
    for recruitment in recruitments:
        if member_count >= recruitment.target_size:
            recruitment.status = RecruitmentStatus.CLOSED
            team = db.get(Team, team_id)
            if team is not None:
                if member_count >= team.max_size:
                    team.status = TeamStatus.ACTIVE
                elif team.status == TeamStatus.RECRUITING:
                    team.status = TeamStatus.FORMING
            pending = db.scalars(
                select(Application).where(
                    Application.recruitment_id == recruitment.id,
                    Application.status == ApplicationStatus.PENDING,
                )
            ).all()
            now = datetime.now(timezone.utc)
            for application in pending:
                if application.id == exclude_application_id:
                    continue
                application.status = ApplicationStatus.REJECTED
                application.review_note = "招募已满或关闭"
                application.reviewed_at = now
                application.reviewed_by = reviewer_id
                db.add(
                    Notification(
                        user_id=application.applicant_id,
                        title="申请结果通知",
                        content="该招募已达到目标人数，申请已结束",
                    )
                )


def close(
    db: Session, recruitment: Recruitment, reviewer_id: int | None = None
) -> Recruitment:
    """关闭招募，并把尚未处理的申请明确结束。"""
    recruitment.status = RecruitmentStatus.CLOSED
    team = db.get(Team, recruitment.team_id)
    if team is not None and team.status == TeamStatus.RECRUITING:
        team.status = TeamStatus.FORMING
    pending = db.scalars(
        select(Application).where(
            Application.recruitment_id == recruitment.id,
            Application.status == ApplicationStatus.PENDING,
        )
    ).all()
    now = datetime.now(timezone.utc)
    for application in pending:
        application.status = ApplicationStatus.REJECTED
        application.review_note = "招募已关闭"
        application.reviewed_at = now
        application.reviewed_by = reviewer_id
        db.add(
            Notification(
                user_id=application.applicant_id,
                title="申请结果通知",
                content="该招募已关闭，申请已结束",
            )
        )
    db.commit()
    db.refresh(recruitment)
    return recruitment
