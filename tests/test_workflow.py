"""完整业务闭环测试：申请 → 审批 → 成员变更 → 通知（教程第 08 章）。"""
from tests.conftest import login


def test_application_and_review_flow(client, auth_headers, bob_token):
    headers_bob = {"Authorization": f"Bearer {bob_token}"}

    # 新注册一个学生来申请（避免与种子用户/其他测试冲突）
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "username": "eve",
            "email": "eve@mail.nankai.edu.cn",
            "password": "secret123",
        },
    )
    assert resp.status_code == 201
    eve_token = client.post(
        "/api/v1/auth/login",
        data={"username": "eve", "password": "secret123"},
    ).json()["access_token"]
    eve_headers = {"Authorization": f"Bearer {eve_token}"}

    rec = next(
        item
        for item in client.get("/api/v1/recruitments").json()["items"]
        if item["team_id"] == 1
    )
    assert rec["status"] == "open"

    # 1) 提交申请
    applied = client.post(
        f"/api/v1/applications/recruitments/{rec['id']}",
        json={"message": "我有论文写作经验"},
        headers=eve_headers,
    )
    assert applied.status_code == 201, applied.text
    application_id = applied.json()["id"]

    # 2) 重复申请被拦截
    duplicate = client.post(
        f"/api/v1/applications/recruitments/{rec['id']}",
        json={"message": "再申请一次"},
        headers=eve_headers,
    )
    assert duplicate.status_code == 400

    # 3) 学生不能审批，队长可以
    assert client.post(
        f"/api/v1/applications/{application_id}/review",
        json={"decision": "accept"},
        headers=eve_headers,
    ).status_code == 403

    approved = client.post(
        f"/api/v1/applications/{application_id}/review",
        json={"decision": "accept", "review_note": "欢迎加入"},
        headers=headers_bob,
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "accepted"

    # 4) 二次审批违反状态机
    again = client.post(
        f"/api/v1/applications/{application_id}/review",
        json={"decision": "reject"},
        headers=headers_bob,
    )
    assert again.status_code == 400

    # 5) 队员列表新增一人，申请者收到通知
    members = client.get(f"/api/v1/teams/{rec['team_id']}").json()["members"]
    assert any(m["username"] == "eve" for m in members)
    notes = client.get("/api/v1/messages/notifications", headers=eve_headers).json()
    assert any("申请结果通知" == n["title"] for n in notes)


def test_recommendations_explainable(client, auth_headers, bob_token):
    # 前面的审批测试会把演示团队招满并关闭招募，这里由尚未组队的 Dave 新建招募，
    # 保证推荐测试不依赖其他测试遗留的团队容量状态。
    dave_token = login(client, "dave", "secret123")
    dave_headers = {"Authorization": f"Bearer {dave_token}"}
    created = client.post(
        "/api/v1/teams",
        json={
            "name": "推荐测试队",
            "competition_track": "optimization",
            "max_size": 3,
        },
        headers=dave_headers,
    )
    assert created.status_code == 201, created.text
    published = client.post(
        f"/api/v1/recruitments/teams/{created.json()['id']}",
        json={
            "title": "推荐测试招募",
            "competition_track": "optimization",
            "target_size": 2,
            "required_roles": ["modeler"],
            "required_skills": ["建模分析"],
        },
        headers=dave_headers,
    )
    assert published.status_code == 201, published.text

    recs = client.get("/api/v1/recommendations/teams", headers=auth_headers)
    assert recs.status_code == 200, recs.text
    items = recs.json()
    assert len(items) >= 1
    first = items[0]
    assert 0 <= first["score"] <= 1
    assert set(first["breakdown"].keys()) == {
        "skill_match", "complement", "experience",
        "role_fit", "time_fit", "preference_fit",
    }
    assert all("reason" in d for d in first["breakdown"].values())

    history = client.get("/api/v1/recommendations/history", headers=auth_headers)
    assert history.status_code == 200
    assert history.json()[0]["algorithm_version"] == "rule-v1.0"

    # 队长反向找人
    headers_bob = {"Authorization": f"Bearer {bob_token}"}
    candidates = client.get(
        "/api/v1/recommendations/members?team_id=1&top_k=3", headers=headers_bob
    )
    assert candidates.status_code == 200
    assert len(candidates.json()) <= 3


def test_websocket_chat(client, bob_token):
    """WebSocket 端点用 TestClient 的 websocket_connect 测试。"""
    with client.websocket_connect(f"/ws/teams/1?token={bob_token}") as ws:
        ws.receive_json()  # 系统消息：XXX 加入了聊天室
        presence = ws.receive_json()
        assert presence["type"] == "presence"
        assert presence["online_user_ids"]
        ws.send_json({"content": "大家好，我来写论文部分"})
        data = ws.receive_json()
        while data["type"] != "message":
            data = ws.receive_json()
        assert data["type"] == "message"
        assert data["content"] == "大家好，我来写论文部分"

    # 历史消息走 REST
    history = client.get(
        "/api/v1/messages/teams/1",
        headers={"Authorization": f"Bearer {bob_token}"},
    )
    assert history.status_code == 200
    assert any("论文部分" in m["content"] for m in history.json())
