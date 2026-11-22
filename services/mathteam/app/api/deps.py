"""通用依赖：认证、角色守卫、分页（教程第 02、04 章）。

依赖链示意：
    oauth2_scheme（从请求头取 token）
        ↓
    get_current_user（解码 token → 查库 → 得到 User 对象）
        ↓
    get_current_active_user（再检查账号状态）
        ↓
    require_role(...) / require_team_leader(...)（再检查权限）

FastAPI 会自动缓存同一请求内的依赖结果：一个路由同时用
Depends(get_current_user) 和 Depends(get_current_active_user) 时，查库只发生一次。
"""
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_db
from app.models.recruitment import Recruitment
from app.models.team import TeamMember, TeamRole
from app.models.user import User, UserRole, UserStatus

# tokenUrl 要和登录路由的实际地址一致，否则 /docs 的 Authorize 按钮会 404
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """把 Bearer token 解析成当前用户对象；失败一律 401。"""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效或过期的登录凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id_str = decode_token(token)
    if user_id_str is None:
        raise credentials_error
    try:
        user_id = int(user_id_str)
    except (TypeError, ValueError):
        raise credentials_error from None

    user = db.get(User, user_id)
    if user is None:
        raise credentials_error
    return user


def get_current_active_user(
    current: Annotated[User, Depends(get_current_user)],
) -> User:
    """被停用的账号即使 token 有效也不能操作。"""
    if current.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="账号已被停用"
        )
    return current


def require_role(*roles: UserRole) -> Callable[..., User]:
    """依赖工厂：生成一个“必须具备指定全局角色之一”的守卫。

    用法（注意是调用结果赋给变量，不是把函数本身传给 Depends）：
        admin_only = require_role(UserRole.PLATFORM_ADMIN)
        def admin_api(user: User = Depends(admin_only)): ...
    """

    def guard(current: User = Depends(get_current_active_user)) -> User:
        if current.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要角色：{[r.value for r in roles]}",
            )
        return current

    return guard


def ensure_team_leader(db: Session, team_id: int, current: User) -> None:
    """“队长权限与具体团队关联”：必须在该团队的 team_members 里是 LEADER。

    平台管理员放松限制，便于后台管理。路由里拿不到 team_id 路径参数时，
    先查出对象再直接调用这个函数即可。
    """
    if current.role == UserRole.PLATFORM_ADMIN:
        return
    is_leader = db.scalar(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current.id,
            TeamMember.role == TeamRole.LEADER,
        )
    )
    if is_leader is None:
        raise HTTPException(status_code=403, detail="只有该队队长可以执行此操作")


def require_team_leader(
    team_id: int,
    current: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> User:
    """可作为 Depends 使用的版本：team_id 由路径参数自动注入。"""
    ensure_team_leader(db, team_id, current)
    return current


def require_recruitment_owner(
    recruitment_id: int,
    current: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> User:
    """路径里只有 recruitment_id 时，先查到它对应的 team_id 再校验队长身份。"""
    rec = db.get(Recruitment, recruitment_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="招募信息不存在")
    ensure_team_leader(db, rec.team_id, current)
    return current


def require_application_reviewer(
    application_id: int,
    current: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> User:
    """审批权限：必须是申请所属团队的队长。"""
    from app.models.application import Application

    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="申请不存在")
    ensure_team_leader(db, application.team_id, current)
    return current


def pagination(
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(20, ge=1, le=100, description="每页条数"),
) -> tuple[int, int]:
    """把两个查询参数打包成一个依赖，多个列表接口共用。"""
    return skip, limit


# Annotated 写法（Python 3.10+/FastAPI 0.95+）让类型提示更干净，等价旧写法：
#   current: User = Depends(get_current_active_user)
CurrentUser = Annotated[User, Depends(get_current_active_user)]
DB = Annotated[Session, Depends(get_db)]
Paging = Annotated[tuple[int, int], Depends(pagination)]
