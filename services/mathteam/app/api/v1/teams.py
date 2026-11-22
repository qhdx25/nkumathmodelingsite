"""团队管理与画像接口（教程第 06 章）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUser, DB, require_team_leader
from app.models.team import Team, TeamMember
from app.models.user import User
from app.schemas.team import TeamCreate, TeamDetail, TeamOut, TeamProfileOut
from app.services import team as team_service

router = APIRouter(prefix="/teams", tags=["团队"])


def team_out(db, team: Team) -> dict:
    """把 ORM 对象转成字典并补上计算字段 member_count。"""
    return {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "competition_track": team.competition_track,
        "max_size": team.max_size,
        "status": team.status,
        "created_by": team.created_by,
        "created_at": team.created_at,
        "member_count": team_service.team_member_count(db, team.id),
    }


# 静态路径 /mine 必须定义在 /{team_id} 之前，
# 否则 "mine" 会被当成 team_id 去解析成 int，直接 422。
@router.get("/mine", response_model=list[TeamOut], summary="我加入的团队")
def my_teams(current: CurrentUser, db: DB) -> list[dict]:
    teams = db.scalars(
        select(Team)
        .join(TeamMember, TeamMember.team_id == Team.id)
        .where(TeamMember.user_id == current.id)
        .distinct()
    ).all()
    return [team_out(db, t) for t in teams]


@router.post("", response_model=TeamOut, status_code=201, summary="创建团队")
def create_team(payload: TeamCreate, current: CurrentUser, db: DB) -> dict:
    team = team_service.create_team(db, current, payload)
    out = team_out(db, team)
    out["member_count"] = 1  # 创建者即队长
    return out


@router.get("/{team_id}", response_model=TeamDetail, summary="团队详情")
def read_team(team_id: int, db: DB) -> dict:
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="团队不存在")
    out = team_out(db, team)
    out["members"] = [
        {
            "user_id": m.user_id,
            "username": m.user.username,
            "role": m.role,
            "joined_at": m.joined_at,
        }
        for m in team.members
    ]
    return out


@router.get("/{team_id}/profile", response_model=TeamProfileOut, summary="团队能力画像")
def team_profile(team_id: int, db: DB) -> dict:
    return team_service.compute_team_profile(db, team_id)


@router.post(
    "/{team_id}/members/{user_id}",
    response_model=TeamDetail,
    summary="队长添加成员",
)
def add_member(
    team_id: int,
    user_id: int,
    db: DB,
    current=Depends(require_team_leader),  # team_id 路径参数会被自动注入依赖
) -> dict:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    team_service.add_member(
        db, team_id, user, force=True, reviewer_id=current.id
    )
    return read_team(team_id, db)
