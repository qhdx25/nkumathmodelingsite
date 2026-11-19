"""pytest 全局夹具。

关键点：必须在 import app 之前设置 DATABASE_URL，
因为 app.core.config.settings 在模块导入时就把环境变量读走了。
内存 SQLite + StaticPool 让每个测试进程拥有干净独立的数据库。
"""
import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db.base import SessionLocal  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    """整个测试会话共用一个 TestClient；with 语句会触发 lifespan（建表+种子数据）。"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db():
    with SessionLocal() as session:
        yield session


def login(client, username: str, password: str = "123456") -> str:
    """登录拿 token 的小工具函数。"""
    response = client.post(
        "/api/v1/auth/login", data={"username": username, "password": password}
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def alice_token(client) -> str:
    return login(client, "alice")


@pytest.fixture
def bob_token(client) -> str:
    return login(client, "bob")


@pytest.fixture
def admin_token(client) -> str:
    return login(client, "admin")


@pytest.fixture
def auth_headers(alice_token) -> dict:
    return {"Authorization": f"Bearer {alice_token}"}
