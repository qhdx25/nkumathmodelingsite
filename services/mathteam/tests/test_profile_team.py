"""画像与团队测试（教程第 05、06 章）。"""


def test_my_profile_and_update(client, auth_headers):
    resp = client.get("/api/v1/profile/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "alice"
    assert len(data["skills"]) == 3  # 种子数据里 alice 有三项技能

    # 整体替换技能：删除旧的 3 项，写入新的 2 项
    caps = client.get("/api/v1/capabilities").json()
    by_name = {c["name"]: c["id"] for c in caps}
    update = client.patch(
        "/api/v1/profile/me",
        json={
            "skills": [
                {"capability_id": by_name["数学理论"], "level": 5},
                {"capability_id": by_name["论文写作"], "level": 2},
            ],
            "preference": {
                "preferred_roles": ["writer"],
                "weekly_hours": 12,
                "preferred_track": "math_modeling",
            },
        },
        headers=auth_headers,
    )
    assert update.status_code == 200, update.text
    assert {s["name"] for s in update.json()["skills"]} == {"数学理论", "论文写作"}
    assert update.json()["preference"]["weekly_hours"] == 12

    # 不存在的 capability_id 应被服务层拦截
    bad = client.patch(
        "/api/v1/profile/me",
        json={"skills": [{"capability_id": 99999, "level": 3}]},
        headers=auth_headers,
    )
    assert bad.status_code == 400


def test_team_profile_and_add_member(client, bob_token, auth_headers):
    headers_bob = {"Authorization": f"Bearer {bob_token}"}
    mine = client.get("/api/v1/teams/mine", headers=headers_bob)
    assert mine.status_code == 200
    team = mine.json()[0]
    assert team["name"] == "数模先锋队"
    assert team["member_count"] == 1

    detail = client.get(f"/api/v1/teams/{team['id']}")
    assert detail.json()["members"][0]["role"] == "leader"

    profile = client.get(f"/api/v1/teams/{team['id']}/profile")
    assert profile.status_code == 200
    assert "数学理论" in profile.json()["gaps"]  # 队长 Bob 没有数学理论能力

    # 普通学生不能拉人
    assert client.post(
        f"/api/v1/teams/{team['id']}/members/3", headers=auth_headers
    ).status_code == 403
    # 队长可以
    added = client.post(
        f"/api/v1/teams/{team['id']}/members/3", headers=headers_bob
    )
    assert added.status_code == 200
    assert added.json()["member_count"] == 2
