"""基础接口与认证测试（教程第 01、04 章）。"""
from tests.conftest import login


def test_health_and_root(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/").json()["message"] == "Welcome to MathTeam!"
    # 34 条接口路径全部写进 OpenAPI，前端可据此生成类型
    assert len(client.get("/openapi.json").json()["paths"]) >= 30


def test_capability_list_and_filter(client):
    resp = client.get("/api/v1/capabilities")
    assert resp.status_code == 200
    assert len(resp.json()) == 6  # 种子数据：六大能力维度

    filtered = client.get("/api/v1/capabilities?category=foundation")
    assert filtered.status_code == 200
    assert [c["name"] for c in filtered.json()] == ["数学理论"]

    # 非法枚举值 → 422，且错误被统一异常处理器包装
    bad = client.get("/api/v1/capabilities?category=unknown")
    assert bad.status_code == 422
    assert bad.json()["code"] == 42200


def test_create_capability_requires_admin(client, auth_headers, admin_token):
    payload = {"name": "文档阅读", "category": "foundation", "weight": 1.0}
    assert client.post("/api/v1/capabilities", json=payload, headers=auth_headers).status_code == 403
    resp = client.post(
        "/api/v1/capabilities",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "文档阅读"


def test_register_login_and_me(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "username": "dave",
            "email": "dave@example.com",
            "password": "secret123",
            "school": "复旦大学",
        },
    )
    assert resp.status_code == 201, resp.text
    assert "hashed_password" not in resp.json()  # 响应模型过滤掉密码字段

    # 登录必须用表单，不能用 JSON（OAuth2PasswordRequestForm）
    token = login(client, "dave", "secret123")
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["username"] == "dave"
    assert client.get("/api/v1/auth/me").status_code == 401  # 没带 token


def test_duplicate_register_conflict(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": "alice", "email": "new@example.com", "password": "secret123"},
    )
    assert resp.status_code == 409
