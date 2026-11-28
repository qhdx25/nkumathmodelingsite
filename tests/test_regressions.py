"""针对审查报告问题的回归测试。"""

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from starlette.websockets import WebSocketDisconnect

from app.core.config import Settings
from app.models.user import User, UserStatus
from tests.conftest import login


def _register_and_login(client, username: str, college: str) -> tuple[dict, dict]:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"{username}@mail.nankai.edu.cn",
            "password": "secret123",
            "real_name": f"{username} 测试姓名",
            "college": college,
        },
    )
    assert response.status_code == 201, response.text
    token = login(client, username, "secret123")
    return response.json(), {"Authorization": f"Bearer {token}"}


def _create_team(
    client,
    headers: dict,
    name: str,
    *,
    school_track: str = "math_modeling",
    max_size: int = 3,
) -> dict:
    response = client.post(
        "/api/v1/teams",
        json={
            "name": name,
            "competition_track": school_track,
            "max_size": max_size,
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _publish(
    client,
    headers: dict,
    team_id: int,
    *,
    title: str,
    target_size: int,
    track: str = "math_modeling",
    skills: list[str] | None = None,
):
    return client.post(
        f"/api/v1/recruitments/teams/{team_id}",
        json={
            "title": title,
            "competition_track": track,
            "target_size": target_size,
            "required_roles": [],
            "required_skills": skills or [],
        },
        headers=headers,
    )


def test_home_cards_apply_filters_and_capacity_rules(client, db):
    leader, leader_headers = _register_and_login(
        client, "filter_leader", "清华大学"
    )
    applicant, applicant_headers = _register_and_login(
        client, "filter_applicant", "北京大学"
    )
    team = _create_team(
        client,
        leader_headers,
        "筛选容量测试队",
        school_track="filter_track",
        max_size=3,
    )

    too_large = _publish(
        client,
        leader_headers,
        team["id"],
        title="超出团队容量",
        target_size=4,
        track="filter_track",
    )
    assert too_large.status_code == 400

    no_growth = _publish(
        client,
        leader_headers,
        team["id"],
        title="没有新增名额",
        target_size=1,
        track="filter_track",
    )
    assert no_growth.status_code == 400

    created = _publish(
        client,
        leader_headers,
        team["id"],
        title="筛选专用招募",
        target_size=3,
        track="filter_track",
        skills=["筛选专用技能"],
    )
    assert created.status_code == 201, created.text

    filtered = client.get(
        "/api/v1/recruitments/cards",
        params={"track": "filter_track", "skill": "筛选专用技能"},
    )
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["id"] == created.json()["id"]

    empty = client.get(
        "/api/v1/recruitments/cards",
        params={"track": "filter_track", "skill": "不存在的技能"},
    )
    assert empty.status_code == 200
    assert empty.json()["total"] == 0

    # 普通用户不能查看无关画像；申请后，队长应能查看申请者画像。
    assert client.get(f"/api/v1/profile/users/{leader['id']}").status_code == 401
    assert (
        client.get(
            f"/api/v1/profile/users/{applicant['id']}",
            headers=leader_headers,
        ).status_code
        == 403
    )
    applied = client.post(
        f"/api/v1/applications/recruitments/{created.json()['id']}",
        json={"message": "申请加入"},
        headers=applicant_headers,
    )
    assert applied.status_code == 201, applied.text
    assert (
        client.get(
            f"/api/v1/profile/users/{applicant['id']}",
            headers=leader_headers,
        ).status_code
        == 200
    )

    # 成员变化后，目标人数低于当前人数的修改必须被拒绝。
    added = client.post(
        f"/api/v1/teams/{team['id']}/members/{applicant['id']}",
        headers=leader_headers,
    )
    assert added.status_code == 200, added.text
    lower_target = client.patch(
        f"/api/v1/recruitments/{created.json()['id']}",
        json={"target_size": 2},
        headers=leader_headers,
    )
    assert lower_target.status_code == 400


def test_closed_recruitment_cannot_be_approved(client):
    leader, leader_headers = _register_and_login(
        client, "closed_leader", "复旦大学"
    )
    applicant, applicant_headers = _register_and_login(
        client, "closed_applicant", "浙江大学"
    )
    team = _create_team(client, leader_headers, "关闭审批测试队", max_size=3)
    recruitment = _publish(
        client,
        leader_headers,
        team["id"],
        title="关闭审批测试招募",
        target_size=3,
    )
    assert recruitment.status_code == 201

    application = client.post(
        f"/api/v1/applications/recruitments/{recruitment.json()['id']}",
        json={"message": "等待审批"},
        headers=applicant_headers,
    )
    assert application.status_code == 201

    closed = client.post(
        f"/api/v1/recruitments/{recruitment.json()['id']}/close",
        headers=leader_headers,
    )
    assert closed.status_code == 200

    review = client.post(
        f"/api/v1/applications/{application.json()['id']}/review",
        json={"decision": "accept"},
        headers=leader_headers,
    )
    assert review.status_code == 400

    detail = client.get(f"/api/v1/teams/{team['id']}").json()
    assert all(
        member["user_id"] != applicant["id"] for member in detail["members"]
    )


def test_full_team_closes_recruitment_and_stops_candidates(client):
    leader, leader_headers = _register_and_login(
        client, "full_leader", "上海交通大学"
    )
    applicant, applicant_headers = _register_and_login(
        client, "full_applicant", "南京大学"
    )
    _, waiting_headers = _register_and_login(
        client, "full_waiting", "东南大学"
    )
    team = _create_team(client, leader_headers, "满员关闭测试队", max_size=2)
    recruitment = _publish(
        client,
        leader_headers,
        team["id"],
        title="只招一人",
        target_size=2,
    )
    assert recruitment.status_code == 201

    application = client.post(
        f"/api/v1/applications/recruitments/{recruitment.json()['id']}",
        json={"message": "加入"},
        headers=applicant_headers,
    )
    assert application.status_code == 201
    waiting = client.post(
        f"/api/v1/applications/recruitments/{recruitment.json()['id']}",
        json={"message": "候补"},
        headers=waiting_headers,
    )
    assert waiting.status_code == 201
    review = client.post(
        f"/api/v1/applications/{application.json()['id']}/review",
        json={"decision": "accept"},
        headers=leader_headers,
    )
    assert review.status_code == 200, review.text

    detail = client.get(
        f"/api/v1/recruitments/{recruitment.json()['id']}"
    ).json()
    assert detail["status"] == "closed"
    assert detail["current_members"] == 2
    waiting_status = client.get(
        "/api/v1/applications/mine", headers=waiting_headers
    ).json()[0]["status"]
    assert waiting_status == "rejected"
    team_detail = client.get(f"/api/v1/teams/{team['id']}").json()
    assert team_detail["member_count"] == team_detail["max_size"]
    assert team_detail["status"] == "active"
    candidates = client.get(
        f"/api/v1/recommendations/members?team_id={team['id']}",
        headers=leader_headers,
    )
    assert candidates.status_code == 200
    assert candidates.json() == []


def test_reaching_recruitment_target_below_capacity_keeps_team_forming(client):
    leader, leader_headers = _register_and_login(
        client, "target_leader", "同济大学"
    )
    applicant, applicant_headers = _register_and_login(
        client, "target_member", "厦门大学"
    )
    team = _create_team(client, leader_headers, "目标人数状态队", max_size=3)
    recruitment = _publish(
        client,
        leader_headers,
        team["id"],
        title="两名成员即可完成招募",
        target_size=2,
    )
    application = client.post(
        f"/api/v1/applications/recruitments/{recruitment.json()['id']}",
        json={"message": "加入"},
        headers=applicant_headers,
    )
    review = client.post(
        f"/api/v1/applications/{application.json()['id']}/review",
        json={"decision": "accept"},
        headers=leader_headers,
    )
    assert review.status_code == 200

    detail = client.get(f"/api/v1/teams/{team['id']}").json()
    assert detail["member_count"] == 2
    assert detail["max_size"] == 3
    assert detail["status"] == "forming"


def test_admin_can_manage_all_schools(client):
    _, leader_a_headers = _register_and_login(
        client, "scope_leader_a", "范围测试大学 A"
    )
    _, leader_b_headers = _register_and_login(
        client, "scope_leader_b", "范围测试大学 B"
    )
    team_a = _create_team(client, leader_a_headers, "A 校团队", max_size=3)
    team_b = _create_team(client, leader_b_headers, "B 校团队", max_size=3)
    rec_a = _publish(
        client,
        leader_a_headers,
        team_a["id"],
        title="A 校招募",
        target_size=2,
    )
    rec_b = _publish(
        client,
        leader_b_headers,
        team_b["id"],
        title="B 校招募",
        target_size=2,
    )
    assert rec_a.status_code == rec_b.status_code == 201

    admin_token = login(client, "admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    teams = client.get("/api/v1/admin/teams", headers=admin_headers).json()
    team_ids = {team["id"] for team in teams}
    assert team_a["id"] in team_ids
    assert team_b["id"] in team_ids

    recruitments = client.get(
        "/api/v1/admin/recruitments", headers=admin_headers
    ).json()
    recruitment_ids = {item["id"] for item in recruitments}
    assert rec_a.json()["id"] in recruitment_ids
    assert rec_b.json()["id"] in recruitment_ids

    stats = client.get("/api/v1/admin/stats", headers=admin_headers).json()
    assert stats["users"] >= 2
    assert stats["teams"] >= 2
    assert stats["recruitments"] >= 2

    removed = client.delete(
        f"/api/v1/admin/recruitments/{rec_b.json()['id']}",
        headers=admin_headers,
    )
    assert removed.status_code == 200


def test_websocket_status_and_subprotocol(client, db):
    leader, leader_headers = _register_and_login(
        client, "ws_leader", "武汉大学"
    )
    team = _create_team(client, leader_headers, "聊天状态测试队", max_size=3)
    token = leader_headers["Authorization"].removeprefix("Bearer ")

    with client.websocket_connect(
        f"/ws/teams/{team['id']}", subprotocols=["bearer", token]
    ) as websocket:
        assert websocket.receive_json()["type"] == "system"

    user = db.scalar(select(User).where(User.id == leader["id"]))
    user.status = UserStatus.DISABLED
    db.commit()
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(
            f"/ws/teams/{team['id']}?token={token}"
        ):
            pass


def test_duplicate_skill_and_recommendation_pool(client, auth_headers):
    capabilities = client.get("/api/v1/capabilities").json()
    six_capabilities = capabilities[:6]
    capability_id = six_capabilities[0]["id"]
    six_skills = client.patch(
        "/api/v1/profile/me",
        json={
            "skills": [
                {"capability_id": capability["id"], "level": 3}
                for capability in six_capabilities
            ]
        },
        headers=auth_headers,
    )
    assert six_skills.status_code == 200
    assert len(six_skills.json()["skills"]) == 6

    duplicate = client.patch(
        "/api/v1/profile/me",
        json={
            "skills": [
                {"capability_id": capability_id, "level": 2},
                {"capability_id": capability_id, "level": 4},
            ]
        },
        headers=auth_headers,
    )
    assert duplicate.status_code == 422
    too_many = client.patch(
        "/api/v1/profile/me",
        json={
            "skills": [
                {"capability_id": capability["id"], "level": 3}
                for capability in six_capabilities
            ]
            + [{"capability_id": capability_id, "level": 4}]
        },
        headers=auth_headers,
    )
    assert too_many.status_code == 422

    _, leader_headers = _register_and_login(
        client, "candidate_leader", "中山大学"
    )
    team = _create_team(client, leader_headers, "候选过滤测试队", max_size=3)
    recommendations = client.get(
        f"/api/v1/recommendations/members?team_id={team['id']}",
        headers=leader_headers,
    )
    assert recommendations.status_code == 200
    target_ids = {item["target_id"] for item in recommendations.json()}
    assert target_ids


def test_production_config_rejects_demo_secrets():
    with pytest.raises(ValidationError):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="dev-only-change-me-in-production",
            SEED_DEMO_DATA=True,
        )
    production = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a-long-random-production-secret",
        SEED_DEMO_DATA=False,
    )
    assert production.SEED_DEMO_DATA is False


def test_user_can_only_join_one_team(client):
    _, leader_a_headers = _register_and_login(
        client, "single_team_leader_a", "测试大学"
    )
    _, leader_b_headers = _register_and_login(
        client, "single_team_leader_b", "测试大学"
    )
    member, member_headers = _register_and_login(
        client, "single_team_member", "测试大学"
    )
    team_a = _create_team(client, leader_a_headers, "唯一团队 A", max_size=3)
    team_b = _create_team(client, leader_b_headers, "唯一团队 B", max_size=3)
    recruitment_b = _publish(
        client,
        leader_b_headers,
        team_b["id"],
        title="唯一团队 B 招募",
        target_size=2,
    )
    assert recruitment_b.status_code == 201

    added = client.post(
        f"/api/v1/teams/{team_a['id']}/members/{member['id']}",
        headers=leader_a_headers,
    )
    assert added.status_code == 200

    second_team = client.post(
        "/api/v1/teams",
        json={
            "name": "重复建队",
            "competition_track": "math_modeling",
            "max_size": 3,
        },
        headers=member_headers,
    )
    assert second_team.status_code == 400

    application = client.post(
        f"/api/v1/applications/recruitments/{recruitment_b.json()['id']}",
        json={"message": "尝试加入第二支团队"},
        headers=member_headers,
    )
    assert application.status_code == 400

    added_again = client.post(
        f"/api/v1/teams/{team_b['id']}/members/{member['id']}",
        headers=leader_b_headers,
    )
    assert added_again.status_code == 400
