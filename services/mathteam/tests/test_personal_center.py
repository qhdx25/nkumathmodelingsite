"""个人中心、协会管理员与私有简历的回归测试。"""

from tests.conftest import login
from tests.test_regressions import _create_team, _publish, _register_and_login


def test_personal_center_basic_information_can_be_updated(client, auth_headers):
    response = client.patch(
        "/api/v1/profile/me",
        json={
            "real_name": "Alice Zhang",
            "student_number": "20260001",
            "college": "数学科学学院",
            "school": "清华大学",
            "phone": "13800138000",
            "email": "alice.new@example.com",
            "qq": "12345678",
            "wechat": "alice_wechat",
            "github": "alice-zhang",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    profile = response.json()
    assert profile["student_number"] == "20260001"
    assert profile["college"] == "数学科学学院"
    assert profile["email"] == "alice.new@example.com"
    assert profile["github"] == "alice-zhang"

    me = client.get("/api/v1/auth/me", headers=auth_headers).json()
    assert me["student_number"] == "20260001"
    assert me["qq"] == "12345678"

    duplicate_email = client.patch(
        "/api/v1/profile/me",
        json={"email": "bob@example.com"},
        headers=auth_headers,
    )
    assert duplicate_email.status_code == 409

    bad_qq = client.patch(
        "/api/v1/profile/me",
        json={"qq": "abc"},
        headers=auth_headers,
    )
    assert bad_qq.status_code == 422


def test_private_resume_visibility_and_application_workflow(client):
    leader, leader_headers = _register_and_login(
        client, "resume_leader", "简历测试大学"
    )
    applicant, applicant_headers = _register_and_login(
        client, "resume_applicant", "简历测试大学"
    )
    _, outsider_headers = _register_and_login(
        client, "resume_outsider", "其他大学"
    )
    team = _create_team(client, leader_headers, "简历可见性测试队", max_size=3)
    recruitment = _publish(
        client,
        leader_headers,
        team["id"],
        title="简历可见性测试招募",
        target_size=3,
    )
    assert recruitment.status_code == 201, recruitment.text

    pdf_bytes = b"%PDF-1.4\nresume-content\n%%EOF"
    uploaded = client.post(
        "/api/v1/profile/me/resume",
        files={
            "file": (
                "我的简历.pdf",
                pdf_bytes,
                "application/pdf",
            )
        },
        headers=applicant_headers,
    )
    assert uploaded.status_code == 200, uploaded.text
    assert uploaded.json()["name"] == "我的简历.pdf"
    own_profile = client.get(
        "/api/v1/profile/me", headers=applicant_headers
    ).json()
    assert own_profile["resume"]["size"] == len(pdf_bytes)

    # 尚未提交申请时，队长和无关用户都不能看到。
    assert client.get(
        f"/api/v1/profile/users/{applicant['id']}", headers=leader_headers
    ).status_code == 403
    assert client.get(
        f"/api/v1/profile/users/{applicant['id']}/resume",
        headers=outsider_headers,
    ).status_code == 403

    applied = client.post(
        f"/api/v1/applications/recruitments/{recruitment.json()['id']}",
        json={"message": "提交简历申请"},
        headers=applicant_headers,
    )
    assert applied.status_code == 201, applied.text

    leader_view = client.get(
        f"/api/v1/profile/users/{applicant['id']}", headers=leader_headers
    )
    assert leader_view.status_code == 200, leader_view.text
    assert leader_view.json()["resume"]["name"] == "我的简历.pdf"
    downloaded = client.get(
        f"/api/v1/profile/users/{applicant['id']}/resume",
        headers=leader_headers,
    )
    assert downloaded.status_code == 200
    assert downloaded.content == pdf_bytes
    assert downloaded.headers["content-disposition"].startswith("attachment")

    association_token = login(client, "association")
    association_headers = {"Authorization": f"Bearer {association_token}"}
    association_view = client.get(
        f"/api/v1/profile/users/{applicant['id']}",
        headers=association_headers,
    )
    assert association_view.status_code == 200
    assert association_view.json()["resume"]["name"] == "我的简历.pdf"
    assert client.get(
        f"/api/v1/profile/users/{applicant['id']}/resume",
        headers=association_headers,
    ).status_code == 200

    # 平台管理员可查看画像，但严格按需求不能查看私有简历文件。
    admin_token = login(client, "admin")
    platform_headers = {"Authorization": f"Bearer {admin_token}"}
    platform_profile = client.get(
        f"/api/v1/profile/users/{applicant['id']}",
        headers=platform_headers,
    )
    assert platform_profile.status_code == 200
    assert platform_profile.json()["resume"] is None
    assert client.get(
        f"/api/v1/profile/users/{applicant['id']}/resume",
        headers=platform_headers,
    ).status_code == 403

    deleted = client.delete("/api/v1/profile/me/resume", headers=applicant_headers)
    assert deleted.status_code == 200
    assert client.get(
        "/api/v1/profile/me", headers=applicant_headers
    ).json()["resume"] is None


def test_association_admin_is_read_only_and_can_export(client):
    association_token = login(client, "association")
    headers = {"Authorization": f"Bearer {association_token}"}

    assert client.get("/api/v1/admin/users", headers=headers).status_code == 200
    assert client.get("/api/v1/admin/stats", headers=headers).status_code == 200
    teams = client.get("/api/v1/admin/teams", headers=headers)
    assert teams.status_code == 200
    assert all("composite_score" in team for team in teams.json())

    created = client.post(
        "/api/v1/teams",
        json={
            "name": "协会管理员非法建队",
            "competition_track": "math_modeling",
            "max_size": 3,
        },
        headers=headers,
    )
    assert created.status_code == 403

    # 取一条任意开放招募；即使招募已关闭，身份校验也应先拒绝。
    recruitments = client.get("/api/v1/admin/recruitments", headers=headers)
    assert recruitments.status_code == 200
    if recruitments.json():
        attempt_apply = client.post(
            f"/api/v1/applications/recruitments/{recruitments.json()[0]['id']}",
            json={"message": "协会管理员不应能申请"},
            headers=headers,
        )
        assert attempt_apply.status_code == 403

    user = client.get("/api/v1/admin/users", headers=headers).json()["items"][0]
    assert client.patch(
        f"/api/v1/admin/users/{user['id']}/status",
        params={"status": "disabled"},
        headers=headers,
    ).status_code == 403
    if recruitments.json():
        assert client.delete(
            f"/api/v1/admin/recruitments/{recruitments.json()[0]['id']}",
            headers=headers,
        ).status_code == 403

    exported = client.get("/api/v1/admin/export", headers=headers)
    assert exported.status_code == 200
    assert exported.headers["content-type"].startswith("text/csv")
    text = exported.content.decode("utf-8-sig")
    assert text.startswith("ID,用户名,姓名,学号,学院")
    assert "能力图谱" in text
    assert "竞赛与奖项" in text


def test_association_admin_cannot_be_added_to_a_team(client):
    association_token = login(client, "association")
    association_headers = {"Authorization": f"Bearer {association_token}"}
    association_user = client.get(
        "/api/v1/auth/me", headers=association_headers
    ).json()
    _, leader_headers = _register_and_login(
        client, "association_guard_leader", "身份边界大学"
    )
    team = _create_team(client, leader_headers, "协会身份边界队", max_size=3)
    response = client.post(
        f"/api/v1/teams/{team['id']}/members/{association_user['id']}",
        headers=leader_headers,
    )
    assert response.status_code == 403


def test_platform_admin_can_assign_read_only_association_role(client):
    candidate, _ = _register_and_login(
        client, "association_role_candidate", "身份配置大学"
    )
    candidate_token = login(client, "association_role_candidate", "secret123")
    candidate_headers = {"Authorization": f"Bearer {candidate_token}"}
    platform_headers = {
        "Authorization": f"Bearer {login(client, 'admin')}"
    }

    enabled = client.patch(
        f"/api/v1/admin/users/{candidate['id']}/association-admin",
        params={"enable": True},
        headers=platform_headers,
    )
    assert enabled.status_code == 200, enabled.text
    assert enabled.json()["role"] == "association_admin"
    assert client.get(
        "/api/v1/admin/stats", headers=candidate_headers
    ).status_code == 200

    disabled = client.patch(
        f"/api/v1/admin/users/{candidate['id']}/association-admin",
        params={"enable": False},
        headers=platform_headers,
    )
    assert disabled.status_code == 200
    assert disabled.json()["role"] == "student"
    assert client.get(
        "/api/v1/admin/stats", headers=candidate_headers
    ).status_code == 403
