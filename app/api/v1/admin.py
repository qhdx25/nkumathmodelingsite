"""后台管理接口（教程第 11 章，设计说明书 2.8 节）。

权限范围：
- 平台管理员：可管理全部数据；
- 学校管理员：只能管理同校用户（scoped_users 里按 school 过滤）。
关键管理操作都会写 AdminLog 留痕。
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select

from app.api.deps import DB, Paging, require_role
from app.models.admin_log import AdminLog
from app.models.application import Application
from app.models.capability import Capability
from app.models.message import Message
from app.models.recruitment import Recruitment
from app.models.team import Team
from app.models.user import User, UserRole, UserStatus
from app.schemas.common import Page
from app.schemas.user import UserOut

router = APIRouter(prefix="/admin", tags=["后台管理"])

admin_only = require_role(UserRole.SCHOOL_ADMIN, UserRole.PLATFORM_ADMIN)


def scoped_users(db, admin: User):
    """按管理员范围返回用户查询：学校管理员只能看到同校用户。"""
    stmt = select(User)
    if admin.role == UserRole.SCHOOL_ADMIN:
        stmt = stmt.where(User.school == admin.school) if admin.school else stmt.where(False)
    return stmt


def scoped_teams(db, admin: User):
    """学校管理员只看到由本校用户创建的团队。"""
    stmt = select(Team).join(User, User.id == Team.created_by)
    if admin.role == UserRole.SCHOOL_ADMIN:
        stmt = stmt.where(User.school == admin.school) if admin.school else stmt.where(False)
    return stmt


def scoped_recruitments(db, admin: User):
    """招募归属按其所属团队创建者的学校确定。"""
    stmt = (
        select(Recruitment)
        .join(Team, Team.id == Recruitment.team_id)
        .join(User, User.id == Team.created_by)
    )
    if admin.role == UserRole.SCHOOL_ADMIN:
        stmt = stmt.where(User.school == admin.school) if admin.school else stmt.where(False)
    return stmt


def _log(db, admin_id: int, action: str, target_type: str, target_id: int, detail: str) -> None:
    db.add(
        AdminLog(
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
        )
    )


@router.get("/users", response_model=Page[UserOut], summary="用户列表（分权限范围）")
def list_users(
    db: DB,
    paging: Paging,
    admin=Depends(admin_only),
) -> dict:
    stmt = scoped_users(db, admin)
    total = len(db.scalars(stmt).all())
    users = db.scalars(stmt.offset(paging[0]).limit(paging[1])).all()
    return {"items": users, "total": total, "skip": paging[0], "limit": paging[1]}


@router.patch("/users/{user_id}/status", response_model=UserOut, summary="启停账号")
def set_user_status(
    user_id: int,
    status: UserStatus,
    db: DB,
    admin=Depends(admin_only),
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if admin.role == UserRole.SCHOOL_ADMIN and user.school != admin.school:
        raise HTTPException(status_code=403, detail="只能管理本校用户")
    user.status = status
    _log(db, admin.id, "set_user_status", "user", user.id, f"status={status.value}")
    db.commit()
    db.refresh(user)
    return user


@router.get("/teams", response_model=list[dict], summary="全部团队")
def list_all_teams(
    db: DB, admin=Depends(admin_only), skip: int = 0, limit: int = 50
) -> list[dict]:
    teams = db.scalars(scoped_teams(db, admin).offset(skip).limit(limit)).all()
    return [{"id": t.id, "name": t.name, "status": t.status.value, "max_size": t.max_size} for t in teams]


@router.get("/recruitments", response_model=list[dict], summary="全部招募信息")
def list_all_recruitments(
    db: DB, admin=Depends(admin_only), skip: int = 0, limit: int = 50
) -> list[dict]:
    recs = db.scalars(
        scoped_recruitments(db, admin).offset(skip).limit(limit)
    ).all()
    return [
        {"id": r.id, "title": r.title, "status": r.status.value, "team_id": r.team_id}
        for r in recs
    ]


@router.delete("/recruitments/{recruitment_id}", summary="下架违规招募")
def remove_recruitment(
    recruitment_id: int, db: DB, admin=Depends(admin_only)
) -> dict:
    rec = db.get(Recruitment, recruitment_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="招募信息不存在")
    if admin.role == UserRole.SCHOOL_ADMIN:
        team = db.get(Team, rec.team_id)
        creator = db.get(User, team.created_by) if team else None
        if creator is None or creator.school != admin.school:
            raise HTTPException(status_code=403, detail="只能管理本校招募")
    _log(db, admin.id, "delete_recruitment", "recruitment", rec.id, rec.title)
    db.delete(rec)
    db.commit()
    return {"message": "已删除"}


@router.get("/stats", summary="运营数据统计")
def platform_stats(db: DB, admin=Depends(admin_only)) -> dict:
    """一次发出多条 COUNT 查询；真实项目里可按天缓存结果。"""
    def count(stmt) -> int:
        return int(db.scalar(select(func.count()).select_from(stmt.subquery())) or 0)

    users_stmt = scoped_users(db, admin)
    teams_stmt = scoped_teams(db, admin)
    recruitments_stmt = scoped_recruitments(db, admin)
    applications_stmt = (
        select(Application)
        .join(Team, Team.id == Application.team_id)
        .join(User, User.id == Team.created_by)
    )
    messages_stmt = (
        select(Message)
        .join(Team, Team.id == Message.team_id)
        .join(User, User.id == Team.created_by)
    )
    admin_logs_stmt = select(AdminLog).join(User, User.id == AdminLog.admin_id)
    if admin.role == UserRole.SCHOOL_ADMIN:
        if admin.school:
            applications_stmt = applications_stmt.where(User.school == admin.school)
            messages_stmt = messages_stmt.where(User.school == admin.school)
            admin_logs_stmt = admin_logs_stmt.where(User.school == admin.school)
        else:
            applications_stmt = applications_stmt.where(False)
            messages_stmt = messages_stmt.where(False)
            admin_logs_stmt = admin_logs_stmt.where(False)

    return {
        "users": count(users_stmt),
        "teams": count(teams_stmt),
        "capabilities": count(select(Capability)),
        "recruitments": count(recruitments_stmt),
        "applications": count(applications_stmt),
        "messages": count(messages_stmt),
        "admin_logs": count(admin_logs_stmt),
    }
