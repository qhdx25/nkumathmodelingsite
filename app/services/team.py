"""团队服务与团队能力画像（教程第 06 章）。"""
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessError
from app.models.capability import Capability
from app.models.profile import UserSkill
from app.models.team import Team, TeamMember, TeamRole, TeamStatus
from app.models.user import User, UserRole
from app.schemas.team import TeamCreate


def create_team(db: Session, current: User, payload: TeamCreate) -> Team:
    """建队并把创建者设为队长。两个 insert 必须在同一事务里。"""
    team = Team(
        name=payload.name,
        description=payload.description,
        competition_track=payload.competition_track,
        max_size=payload.max_size,
        status=TeamStatus.RECRUITING,
        created_by=current.id,
    )
    db.add(team)
    db.flush()  # 拿到 team.id 才能写关联表
    db.add(TeamMember(team_id=team.id, user_id=current.id, role=TeamRole.LEADER))
    # 全局角色同步标记为队长；注意真正的权限判断仍看 TeamMember.role
    if current.role == UserRole.STUDENT:
        current.role = UserRole.LEADER
    db.commit()
    db.refresh(team)
    return team


def team_member_count(db: Session, team_id: int) -> int:
    return int(
        db.scalar(
            select(func.count()).select_from(TeamMember).where(TeamMember.team_id == team_id)
        )
        or 0
    )


def is_leader(db: Session, team_id: int, user_id: int) -> bool:
    return (
        db.scalar(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
                TeamMember.role == TeamRole.LEADER,
            )
        )
        is not None
    )


def add_member(
    db: Session,
    team_id: int,
    user: User,
    force: bool = False,
    reviewer_id: int | None = None,
) -> TeamMember:
    """添加成员：校验状态、容量、重复加入。

    force=True 表示队长直接拉人（第 6 章练习接口），审批通过也走同一函数。
    """
    # 直接拉人时也锁团队行，避免两个并发请求同时通过容量检查。
    team = db.scalar(select(Team).where(Team.id == team_id).with_for_update())
    if team is None:
        raise BusinessError("团队不存在", code=40401, http_status=404)
    if team.status == TeamStatus.ARCHIVED:
        raise BusinessError("已归档团队不能添加成员", code=40002)
    if not force and team.status != TeamStatus.RECRUITING:
        raise BusinessError("团队不在招募状态", code=40002)
    if team_member_count(db, team_id) >= team.max_size:
        raise BusinessError("团队已满员", code=40003)

    exists = db.scalar(
        select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == user.id
        )
    )
    if exists:
        raise BusinessError("用户已在团队中", code=40004)

    member = TeamMember(team_id=team_id, user_id=user.id, role=TeamRole.MEMBER)
    db.add(member)
    new_count = team_member_count(db, team_id) + 1
    if new_count >= team.max_size:
        team.status = TeamStatus.ACTIVE
    from app.services.recruitment import close_completed_recruitments

    close_completed_recruitments(
        db, team_id, new_count, reviewer_id=reviewer_id
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise BusinessError("用户已在团队中", code=40004) from None
    db.refresh(member)
    return member


def compute_team_profile(db: Session, team_id: int) -> dict:
    """团队能力画像：在 SQL 层做聚合，再在 Python 层比对全量维度找短板。"""
    team = db.get(Team, team_id)
    if team is None:
        raise BusinessError("团队不存在", code=40401, http_status=404)

    # 一条 GROUP BY 查询同时拿到人数与平均熟练度，避免把所有技能行拉回 Python
    rows = db.execute(
        select(Capability.id, Capability.name, func.count(UserSkill.user_id), func.avg(UserSkill.level))
        .join(UserSkill, UserSkill.capability_id == Capability.id)
        .join(TeamMember, TeamMember.user_id == UserSkill.user_id)
        .where(TeamMember.team_id == team_id)
        .group_by(Capability.id, Capability.name)
    ).all()
    coverage = {
        name: {"members": int(cnt), "avg_level": round(float(avg), 2)}
        for _id, name, cnt, avg in rows
    }

    all_caps = db.scalars(select(Capability.name)).all()
    gaps = [name for name in all_caps if name not in coverage]
    weak = [name for name, stat in coverage.items() if stat["avg_level"] < 3]

    return {
        "team_id": team.id,
        "team_name": team.name,
        "member_count": team_member_count(db, team_id),
        "coverage": coverage,
        "gaps": gaps,
        "weak": weak,
    }
