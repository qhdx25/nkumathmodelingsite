"""注册 / 登录 / 当前用户（教程第 04 章）。"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, DB
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User, UserStatus
from app.schemas.user import Token, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
)
def register(payload: UserCreate, db: DB) -> User:
    """注册时忽略客户端传来的 role（Schema 里就没这个字段），杜绝提权。"""
    exists = db.scalar(
        select(User).where(
            (User.username == payload.username) | (User.email == payload.email)
        )
    )
    if exists:
        raise HTTPException(status_code=409, detail="用户名或邮箱已被占用")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        real_name=payload.real_name,
        school=payload.school,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token, summary="登录获取 JWT")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    """OAuth2PasswordRequestForm 要求用表单提交 username/password，
    这样 /docs 的 Authorize 按钮才能直接工作。"""
    user = db.scalar(select(User).where(User.username == form_data.username))
    if (
        user is None
        or not verify_password(form_data.password, user.hashed_password)
        or user.status != UserStatus.ACTIVE
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=UserOut, summary="获取当前登录用户")
def read_me(current: CurrentUser) -> User:
    """依赖链自动完成 token 解析、查库、状态检查，路由里只管返回。"""
    return current
