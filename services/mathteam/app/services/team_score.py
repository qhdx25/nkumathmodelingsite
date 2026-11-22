"""团队综合能力评分的可解释规则算法。

综合分由五项规则指标组成，每项先归一化到 [0, 1]，再按权重求和。
算法版本随响应返回，便于后续调整公式后回溯结果。
"""
from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.capability import Capability
from app.models.profile import UserProfile, UserSkill
from app.models.team import Team, TeamMember

TEAM_SCORE_ALGORITHM_VERSION = "team-rule-v1.0"
TEAM_SCORE_WEIGHTS = {
    "skill_strength": 0.35,
    "skill_coverage": 0.20,
    "awards": 0.25,
    "experience": 0.10,
    "composition": 0.10,
}
AWARD_LEVEL_POINTS = {
    "international": 1.00,
    "national": 0.90,
    "provincial": 0.65,
    "school": 0.35,
    "participation": 0.15,
    "other": 0.30,
}


def _clip(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _award_points(competition: dict) -> float:
    """优先使用结构化奖项等级，同时兼容旧数据中的奖项文字。"""
    level = str(competition.get("award_level") or "").lower()
    if level in AWARD_LEVEL_POINTS:
        return AWARD_LEVEL_POINTS[level]

    text = (
        f"{competition.get('title', '')} "
        f"{competition.get('description', '')}"
    ).lower()
    award_markers = ("奖", "获奖", "冠军", "亚军", "季军", "award", "winner")
    if not any(marker in text for marker in award_markers):
        return 0.0

    if any(marker in text for marker in ("国际", "international")):
        base = 1.00
    elif any(marker in text for marker in ("全国", "国家", "national")):
        base = 0.90
    elif any(marker in text for marker in ("省", "赛区", "provincial")):
        base = 0.65
    elif any(marker in text for marker in ("校", "school")):
        base = 0.35
    else:
        base = 0.50

    if any(marker in text for marker in ("一等奖", "第一名", "冠军", "first prize")):
        rank = 1.00
    elif any(marker in text for marker in ("二等奖", "第二名", "亚军", "second prize")):
        rank = 0.80
    elif any(marker in text for marker in ("三等奖", "第三名", "季军", "third prize")):
        rank = 0.65
    else:
        rank = 0.70
    return base * rank


def _grade(score: float) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    return "D"


def compute_team_score(db: Session, team: Team) -> dict:
    member_ids = list(
        db.scalars(
            select(TeamMember.user_id).where(TeamMember.team_id == team.id)
        ).all()
    )
    member_count = len(member_ids)
    capabilities = list(db.scalars(select(Capability)).all())
    skills = (
        db.execute(
            select(UserSkill.user_id, UserSkill.capability_id, UserSkill.level)
            .where(UserSkill.user_id.in_(member_ids))
        ).all()
        if member_ids
        else []
    )

    levels_by_capability: dict[int, list[int]] = defaultdict(list)
    for _user_id, capability_id, level in skills:
        levels_by_capability[capability_id].append(int(level))

    total_weight = sum(cap.weight for cap in capabilities) or 1.0
    if member_count:
        strength = sum(
            (
                sum(levels_by_capability.get(cap.id, []))
                / member_count
                / 5.0
            )
            * cap.weight
            for cap in capabilities
        ) / total_weight
        coverage = sum(
            1 for cap in capabilities if levels_by_capability.get(cap.id)
        ) / (len(capabilities) or 1)
    else:
        strength = coverage = 0.0

    profiles = (
        list(
            db.scalars(
                select(UserProfile).where(UserProfile.user_id.in_(member_ids))
            ).all()
        )
        if member_ids
        else []
    )
    award_total = 0.0
    award_count = 0
    experience_count = 0
    for profile in profiles:
        competitions = profile.competitions or []
        for competition in competitions:
            points = _award_points(competition)
            award_total += points
            if points > 0:
                award_count += 1
        experience_count += len(profile.projects or []) + len(competitions)

    awards = _clip(award_total / max(member_count * 2.0, 1.0))
    experience = _clip(experience_count / max(member_count * 4.0, 1.0))
    composition = _clip(member_count / max(team.max_size, 1))

    raw = {
        "skill_strength": strength,
        "skill_coverage": coverage,
        "awards": awards,
        "experience": experience,
        "composition": composition,
    }
    reasons = {
        "skill_strength": f"团队能力加权深度 {round(strength * 100)}%",
        "skill_coverage": (
            f"覆盖 {round(coverage * len(capabilities))}/{len(capabilities)} "
            "个能力维度"
        ),
        "awards": f"累计识别 {award_count} 项有效奖项",
        "experience": f"成员共有 {experience_count} 项项目/竞赛经历",
        "composition": (
            f"阵容 {member_count}/{team.max_size} 人，"
            f"完成度 {round(composition * 100)}%"
        ),
    }
    breakdown = {
        name: {
            "score": round(raw[name], 3),
            "weight": TEAM_SCORE_WEIGHTS[name],
            "reason": reasons[name],
        }
        for name in TEAM_SCORE_WEIGHTS
    }
    composite_score = round(
        sum(raw[name] * TEAM_SCORE_WEIGHTS[name] for name in raw) * 100,
        1,
    )
    return {
        "composite_score": composite_score,
        "score_grade": _grade(composite_score),
        "score_algorithm_version": TEAM_SCORE_ALGORITHM_VERSION,
        "score_breakdown": breakdown,
        "score_summary": (
            f"{reasons['skill_coverage']}，{reasons['awards']}；"
            f"{reasons['composition']}。"
        ),
    }
