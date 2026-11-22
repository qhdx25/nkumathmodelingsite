"""后台管理接口（教程第 11 章，设计说明书 2.8 节）。

权限范围：
- 平台管理员：可管理全部数据；
- 学校管理员：只能管理同校用户（scoped_users 里按 school 过滤）。
- 协会管理员：只读查看全部组队、评分和画像信息，并可导出表格。
关键管理操作都会写 AdminLog 留痕。
"""
import csv
import io
from datetime import datetime, timezone
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import func, select

from app.api.deps import DB, Paging, require_role
from app.models.admin_log import AdminLog
from app.models.application import Application
from app.models.capability import Capability
from app.models.message import Message
from app.models.profile import UserProfile, UserSkill
from app.models.recruitment import Recruitment
from app.models.team import Team, TeamMember
from app.models.user import User, UserRole, UserStatus
from app.schemas.common import Page
from app.schemas.user import UserOut
from app.services.team import team_member_count
from app.services.team_score import compute_team_score

router = APIRouter(prefix="/admin", tags=["后台管理"])

admin_reader = require_role(
    UserRole.ASSOCIATION_ADMIN,
    UserRole.SCHOOL_ADMIN,
    UserRole.PLATFORM_ADMIN,
)
management_admin = require_role(UserRole.SCHOOL_ADMIN, UserRole.PLATFORM_ADMIN)
platform_admin = require_role(UserRole.PLATFORM_ADMIN)


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
    admin=Depends(admin_reader),
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
    admin=Depends(management_admin),
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
    db: DB,
    admin=Depends(admin_reader),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict]:
    teams = db.scalars(scoped_teams(db, admin).offset(skip).limit(limit)).all()
    result = []
    for team in teams:
        creator = db.get(User, team.created_by)
        score = compute_team_score(db, team)
        result.append(
            {
                "id": team.id,
                "name": team.name,
                "status": team.status.value,
                "max_size": team.max_size,
                "member_count": team_member_count(db, team.id),
                "competition_track": team.competition_track,
                "creator_name": (
                    creator.real_name or creator.username if creator else "—"
                ),
                "school": creator.school if creator else None,
                "composite_score": score["composite_score"],
                "score_grade": score["score_grade"],
            }
        )
    return result


@router.get("/recruitments", response_model=list[dict], summary="全部招募信息")
def list_all_recruitments(
    db: DB, admin=Depends(admin_reader), skip: int = 0, limit: int = 50
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
    recruitment_id: int, db: DB, admin=Depends(management_admin)
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
def platform_stats(db: DB, admin=Depends(admin_reader)) -> dict:
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


@router.patch(
    "/users/{user_id}/association-admin",
    response_model=UserOut,
    summary="设置或取消协会管理员",
)
def set_association_admin(
    user_id: int,
    db: DB,
    admin=Depends(platform_admin),
    enable: bool = Query(True),
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.id == admin.id or user.role in {
        UserRole.SCHOOL_ADMIN,
        UserRole.PLATFORM_ADMIN,
    }:
        raise HTTPException(
            status_code=400,
            detail="不能修改管理员或当前账号的身份",
        )
    membership = db.scalar(
        select(TeamMember).where(TeamMember.user_id == user.id)
    )
    if enable and membership is not None:
        raise HTTPException(
            status_code=400,
            detail="该用户已在团队中，不能转为协会管理员",
        )
    user.role = UserRole.ASSOCIATION_ADMIN if enable else UserRole.STUDENT
    _log(
        db,
        admin.id,
        "set_association_admin",
        "user",
        user.id,
        f"enabled={enable}",
    )
    db.commit()
    db.refresh(user)
    return user


def _csv_cell(value: object) -> str:
    """避免导出的文本被表格软件当作公式执行。"""
    text = "" if value is None else str(value)
    if text.startswith(("=", "+", "-", "@")):
        return f"'{text}"
    return text


@router.get("/export", summary="一键导出组队、评分与画像表格")
def export_association_table(
    db: DB,
    admin=Depends(admin_reader),
) -> Response:
    users = list(db.scalars(scoped_users(db, admin).order_by(User.id)).all())
    profiles = {
        profile.user_id: profile
        for profile in db.scalars(select(UserProfile)).all()
    }
    skills: dict[int, list[str]] = {}
    for user_id, name, level in db.execute(
        select(UserSkill.user_id, Capability.name, UserSkill.level).join(
            Capability, Capability.id == UserSkill.capability_id
        )
    ).all():
        skills.setdefault(user_id, []).append(f"{name}:{level}/5")

    team_rows = db.execute(
        select(TeamMember.user_id, Team).join(
            Team, Team.id == TeamMember.team_id
        )
    ).all()
    team_by_user = {user_id: team for user_id, team in team_rows}
    score_cache: dict[int, dict] = {}

    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(
        [
            "ID",
            "用户名",
            "姓名",
            "学号",
            "学院",
            "学校",
            "电话",
            "邮箱",
            "QQ",
            "微信",
            "GitHub",
            "身份",
            "团队",
            "团队状态",
            "团队人数",
            "团队综合评分",
            "评分等级",
            "能力图谱",
            "项目经历",
            "竞赛与奖项",
            "简历",
        ]
    )
    for user in users:
        profile = profiles.get(user.id)
        team = team_by_user.get(user.id)
        score = None
        if team is not None:
            if team.id not in score_cache:
                score_cache[team.id] = compute_team_score(db, team)
            score = score_cache[team.id]
        competitions = profile.competitions if profile else []
        projects = profile.projects if profile else []
        row = [
            user.id,
            user.username,
            user.real_name,
            user.student_number,
            user.college,
            user.school,
            user.phone,
            user.email,
            user.qq,
            user.wechat,
            user.github,
            {
                UserRole.STUDENT: "学生",
                UserRole.LEADER: "队长",
                UserRole.ASSOCIATION_ADMIN: "协会管理员",
                UserRole.SCHOOL_ADMIN: "学校管理员",
                UserRole.PLATFORM_ADMIN: "平台管理员",
            }[user.role],
            team.name if team else "",
            team.status.value if team else "",
            team_member_count(db, team.id) if team else 0,
            score["composite_score"] if score else "",
            score["score_grade"] if score else "",
            "；".join(skills.get(user.id, [])),
            "；".join(
                f"{item.get('title', '')}({item.get('role', '')})"
                for item in projects
            ),
            "；".join(
                f"{item.get('title', '')}"
                f"({item.get('award_level') or '经历'})"
                for item in competitions
            ),
            user.resume_name or "",
        ]
        writer.writerow([_csv_cell(value) for value in row])
    data = ("\ufeff" + output.getvalue()).encode("utf-8")
    _log(db, admin.id, "export_table", "association", 0, "csv")
    db.commit()
    filename = datetime.now(timezone.utc).strftime(
        "MathTeam组队与能力信息_%Y%m%d_%H%M.csv"
    )
    return Response(
        content=data,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                f"attachment; filename*=UTF-8''{quote(filename)}"
            )
        },
    )
