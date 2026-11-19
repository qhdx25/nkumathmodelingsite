"""数据库会话依赖（教程第 03 章 2.4 节）。

FastAPI 的 Depends 支持「生成器依赖」：
    yield 之前 → 请求处理前执行（创建 Session）
    yield 之后 → 响应发送后执行（关闭 Session）
这样每个请求独占一个 Session，既不会泄漏连接，也不会被多个请求共用。
"""
from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.base import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db          # 把这个 Session 注入路由函数
    finally:
        db.close()        # 无论成功还是异常，都保证归还连接


# 用法（路由函数签名）：
#   def list_items(db: Session = Depends(get_db)):
#       ...
