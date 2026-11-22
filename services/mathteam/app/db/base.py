"""SQLAlchemy 2.0 引擎与声明式基类（教程第 03 章）。

三层概念别混淆：
    engine    —— 连接池 + 方言，负责“怎么连数据库”
    Session   —— 工作单元，负责“一次请求里的一批读写”
    Base      —— 所有 ORM 模型的父类，负责“类怎么映射成表”

create_all 只创建「已经被导入过」的模型对应的表，所以 init_db() 里必须先 import 所有模型。
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# SQLite 用文件数据库时，默认只允许创建它的线程访问；FastAPI 的同步路由跑在线程池，
# 所以必须关掉 check_same_thread。PostgreSQL 不认识这个参数，因此按方言判断。
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")
_connect_args = {"check_same_thread": False} if _is_sqlite else {}

_engine_kwargs = {
    "connect_args": _connect_args,
    "echo": settings.DEBUG,  # DEBUG=true 时在终端打印执行的 SQL，学习阶段很有用
}
# 内存 SQLite 必须让所有 Session 共用同一个连接，否则每个连接看到的是不同的空库。
# 这正是 pytest 测试常用的隔离方案；文件 SQLite / PostgreSQL 不需要。
if ":memory:" in settings.DATABASE_URL:
    _engine_kwargs["poolclass"] = StaticPool

engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)

# SessionLocal 是“会话工厂”，每次调用都产出一个全新的 Session，不是一个共享的 Session。
# expire_on_commit=False：commit 后对象属性仍可读，避免路由里返回对象时触发 DetachedInstanceError。
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """声明式基类。所有模型继承它，表结构由类里的 Mapped 注解推导。"""
    pass
