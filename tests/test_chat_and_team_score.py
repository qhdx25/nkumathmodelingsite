"""聊天临时附件和团队综合能力评分测试。"""

import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import Settings, settings
from app.db.base import SessionLocal
from app.models.message import Message
from app.services.chat import classify_attachment
from app.services.storage import cleanup_expired_attachments, storage
from tests.test_regressions import _create_team, _register_and_login

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
)


def test_chat_attachment_upload_download_and_24h_cleanup(client, bob_token):
    headers = {"Authorization": f"Bearer {bob_token}"}
    team_id = client.get("/api/v1/teams/mine", headers=headers).json()[0]["id"]
    policy = client.get("/api/v1/messages/chat-policy").json()
    assert policy["retention_hours"] == 24
    assert policy["max_bytes"] == settings.CHAT_ATTACHMENT_MAX_BYTES

    uploaded = client.post(
        f"/api/v1/messages/teams/{team_id}/attachments",
        files={"file": ("团队截图.png", PNG_BYTES, "image/png")},
        data={"content": "这是需求截图"},
        headers=headers,
    )
    assert uploaded.status_code == 201, uploaded.text
    message = uploaded.json()
    assert message["message_type"] == "resource"
    assert message["attachment"]["name"] == "团队截图.png"
    assert message["attachment"]["kind"] == "image"
    assert message["attachment"]["expired"] is False
    assert message["attachment"]["download_url"]

    downloaded = client.get(
        f"/api/v1/messages/attachments/{message['id']}/download",
        headers=headers,
    )
    assert downloaded.status_code == 200
    assert downloaded.content == PNG_BYTES
    assert downloaded.headers["content-type"].startswith("image/png")
    assert downloaded.headers["x-content-type-options"] == "nosniff"

    # 把消息改成已过期，再执行与生产定时任务相同的清理函数。
    with SessionLocal() as db:
        row = db.get(Message, message["id"])
        assert row is not None and row.attachment_key
        local_path = Path(settings.CHAT_UPLOAD_DIR) / row.attachment_key
        assert local_path.exists()
        row.attachment_expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.commit()
        removed = asyncio.run(cleanup_expired_attachments(db, storage))
        assert removed >= 1
        db.expire_all()
        assert db.get(Message, message["id"]).attachment_key is None

    assert not local_path.exists()
    expired = client.get(
        f"/api/v1/messages/attachments/{message['id']}/download",
        headers=headers,
    )
    assert expired.status_code == 410


def test_chat_attachment_rejects_oversize_and_non_member(
    client, bob_token, monkeypatch
):
    headers = {"Authorization": f"Bearer {bob_token}"}
    team_id = client.get("/api/v1/teams/mine", headers=headers).json()[0]["id"]
    monkeypatch.setattr(settings, "CHAT_ATTACHMENT_MAX_BYTES", 3)
    too_large = client.post(
        f"/api/v1/messages/teams/{team_id}/attachments",
        files={"file": ("large.txt", b"1234", "text/plain")},
        headers=headers,
    )
    assert too_large.status_code == 413

    _, outsider_headers = _register_and_login(
        client, "attachment_outsider", "测试大学"
    )
    forbidden = client.post(
        f"/api/v1/messages/teams/{team_id}/attachments",
        files={"file": ("secret.txt", b"x", "text/plain")},
        headers=outsider_headers,
    )
    assert forbidden.status_code == 403


def test_attachment_kind_detection_covers_images_videos_and_files():
    assert classify_attachment("photo.png", "image/png") == "image"
    assert classify_attachment("demo.mp4", "video/mp4") == "video"
    assert classify_attachment("report.pdf", "application/pdf") == "file"
    # SVG 可能携带脚本，不作为可内联的图片处理。
    assert classify_attachment("drawing.svg", "image/svg+xml") == "file"


def test_attachment_retention_cannot_exceed_24_hours():
    with pytest.raises(ValidationError):
        Settings(CHAT_ATTACHMENT_TTL_HOURS=25)


def test_team_composite_score_uses_skills_awards_and_experience(client):
    leader, leader_headers = _register_and_login(
        client, "score_leader", "评分大学"
    )
    member, member_headers = _register_and_login(
        client, "score_member", "评分大学"
    )
    team = _create_team(client, leader_headers, "综合评分测试队", max_size=2)
    added = client.post(
        f"/api/v1/teams/{team['id']}/members/{member['id']}",
        headers=leader_headers,
    )
    assert added.status_code == 200, added.text
    score_before = client.get(
        f"/api/v1/teams/{team['id']}/profile"
    ).json()["composite_score"]

    capabilities = client.get("/api/v1/capabilities").json()[:6]
    profile_update = client.patch(
        "/api/v1/profile/me",
        json={
            "skills": [
                {"capability_id": capability["id"], "level": 5}
                for capability in capabilities
            ],
            "projects": [
                {"title": "预测模型项目", "role": "算法负责人"},
            ],
            "competitions": [
                {
                    "title": "全国大学生数学建模竞赛",
                    "role": "建模手",
                    "description": "获得全国一等奖",
                    "award_level": "national",
                }
            ],
        },
        headers=member_headers,
    )
    assert profile_update.status_code == 200, profile_update.text
    assert leader["id"] != member["id"]

    response = client.get(f"/api/v1/teams/{team['id']}/profile")
    assert response.status_code == 200, response.text
    score = response.json()
    assert 0 <= score["composite_score"] <= 100
    assert score["composite_score"] > score_before
    assert score["score_grade"] in {"A", "B", "C", "D"}
    assert set(score["score_breakdown"]) == {
        "skill_strength",
        "skill_coverage",
        "awards",
        "experience",
        "composition",
    }
    assert score["score_breakdown"]["awards"]["score"] > 0
    assert score["score_breakdown"]["skill_coverage"]["score"] >= 0.8
    assert "有效奖项" in score["score_summary"]
