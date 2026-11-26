"""个人中心、管理员与私有简历的回归测试。"""

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

    admin_token = login(client, "admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    admin_view = client.get(
        f"/api/v1/profile/users/{applicant['id']}",
        headers=admin_headers,
    )
    assert admin_view.status_code == 200
    assert admin_view.json()["resume"]["name"] == "我的简历.pdf"
    admin_download = client.get(
        f"/api/v1/profile/users/{applicant['id']}/resume",
        headers=admin_headers,
    )
    assert admin_download.status_code == 200
    assert admin_download.content == pdf_bytes

    deleted = client.delete("/api/v1/profile/me/resume", headers=applicant_headers)
    assert deleted.status_code == 200
    assert client.get(
        "/api/v1/profile/me", headers=applicant_headers
    ).json()["resume"] is None


def test_admin_has_full_backend_access_and_can_export(client):
    admin_token = login(client, "admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    assert client.get("/api/v1/admin/users", headers=headers).status_code == 200
    assert client.get("/api/v1/admin/stats", headers=headers).status_code == 200
    teams = client.get("/api/v1/admin/teams", headers=headers)
    assert teams.status_code == 200
    assert all("composite_score" in team for team in teams.json())

    users = client.get("/api/v1/admin/users", headers=headers).json()["items"]
    user = next(item for item in users if item["username"] == "carol")
    current_admin = next(item for item in users if item["username"] == "admin")
    self_disable = client.patch(
        f"/api/v1/admin/users/{current_admin['id']}/status",
        params={"status": "disabled"},
        headers=headers,
    )
    assert self_disable.status_code == 400
    disabled = client.patch(
        f"/api/v1/admin/users/{user['id']}/status",
        params={"status": "disabled"},
        headers=headers,
    )
    assert disabled.status_code == 200
    assert disabled.json()["status"] == "disabled"
    enabled = client.patch(
        f"/api/v1/admin/users/{user['id']}/status",
        params={"status": "active"},
        headers=headers,
    )
    assert enabled.status_code == 200

    exported = client.get("/api/v1/admin/export", headers=headers)
    assert exported.status_code == 200
    assert exported.headers["content-type"].startswith("text/csv")
    text = exported.content.decode("utf-8-sig")
    assert text.startswith("ID,用户名,姓名,学号,学院")
    assert "能力图谱" in text
    assert "竞赛与奖项" in text


def test_admin_can_be_added_to_a_team(client):
    candidate, _ = _register_and_login(
        client, "admin_team_candidate", "管理员参赛大学"
    )
    admin_headers = {
        "Authorization": f"Bearer {login(client, 'admin')}"
    }
    promoted = client.patch(
        f"/api/v1/admin/users/{candidate['id']}/admin",
        params={"enable": True},
        headers=admin_headers,
    )
    assert promoted.status_code == 200

    _, leader_headers = _register_and_login(
        client, "admin_team_leader", "管理员参赛大学"
    )
    team = _create_team(client, leader_headers, "管理员参赛测试队", max_size=3)
    response = client.post(
        f"/api/v1/teams/{team['id']}/members/{candidate['id']}",
        headers=leader_headers,
    )
    assert response.status_code == 200, response.text

    candidate_token = login(client, "admin_team_candidate", "secret123")
    candidate_headers = {"Authorization": f"Bearer {candidate_token}"}
    candidate_me = client.get("/api/v1/auth/me", headers=candidate_headers).json()
    assert candidate_me["role"] == "student"
    assert candidate_me["is_admin"] is True
    assert client.get(
        "/api/v1/admin/stats", headers=candidate_headers
    ).status_code == 200


def test_admin_can_assign_and_remove_admin_role(client):
    candidate, _ = _register_and_login(
        client, "admin_role_candidate", "身份配置大学"
    )
    candidate_token = login(client, "admin_role_candidate", "secret123")
    candidate_headers = {"Authorization": f"Bearer {candidate_token}"}
    admin_headers = {
        "Authorization": f"Bearer {login(client, 'admin')}"
    }

    enabled = client.patch(
        f"/api/v1/admin/users/{candidate['id']}/admin",
        params={"enable": True},
        headers=admin_headers,
    )
    assert enabled.status_code == 200, enabled.text
    assert enabled.json()["role"] == "student"
    assert enabled.json()["is_admin"] is True
    assert client.get(
        "/api/v1/admin/stats", headers=candidate_headers
    ).status_code == 200

    disabled = client.patch(
        f"/api/v1/admin/users/{candidate['id']}/admin",
        params={"enable": False},
        headers=admin_headers,
    )
    assert disabled.status_code == 200
    assert disabled.json()["role"] == "student"
    assert disabled.json()["is_admin"] is False
    assert client.get(
        "/api/v1/admin/stats", headers=candidate_headers
    ).status_code == 403


def test_team_leader_can_become_admin_without_losing_team_role(client):
    leader, leader_headers = _register_and_login(
        client, "promoted_team_leader", "管理员兼任测试大学"
    )
    _create_team(client, leader_headers, "管理员兼任测试队", max_size=3)
    admin_headers = {
        "Authorization": f"Bearer {login(client, 'admin')}"
    }

    promoted = client.patch(
        f"/api/v1/admin/users/{leader['id']}/admin",
        params={"enable": True},
        headers=admin_headers,
    )
    assert promoted.status_code == 200, promoted.text
    assert promoted.json()["role"] == "leader"
    assert promoted.json()["is_admin"] is True

    demoted = client.patch(
        f"/api/v1/admin/users/{leader['id']}/admin",
        params={"enable": False},
        headers=admin_headers,
    )
    assert demoted.status_code == 200, demoted.text
    assert demoted.json()["role"] == "leader"
    assert demoted.json()["is_admin"] is False


def test_admin_can_create_team_and_retain_backend_access(client):
    candidate, _ = _register_and_login(
        client, "admin_creating_team", "管理员建队大学"
    )
    admin_headers = {
        "Authorization": f"Bearer {login(client, 'admin')}"
    }
    promoted = client.patch(
        f"/api/v1/admin/users/{candidate['id']}/admin",
        params={"enable": True},
        headers=admin_headers,
    )
    assert promoted.status_code == 200

    candidate_token = login(client, "admin_creating_team", "secret123")
    candidate_headers = {"Authorization": f"Bearer {candidate_token}"}
    team = _create_team(
        client,
        candidate_headers,
        "管理员正常参赛队",
        max_size=3,
    )
    me = client.get("/api/v1/auth/me", headers=candidate_headers).json()
    assert team["id"]
    assert me["role"] == "leader"
    assert me["is_admin"] is True
    assert client.get(
        "/api/v1/admin/stats", headers=candidate_headers
    ).status_code == 200
