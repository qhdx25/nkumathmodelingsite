"""可解释的加权推荐引擎（教程第 09 章，设计说明书 2.4 / 3.3 节）。

评分公式：
    score = Σ (维度得分 × 维度权重)

六个维度都归一化到 [0,1]，所以总分也在 [0,1]，便于比较和展示。
权重写在 WEIGHTS 字典里，算法版本写在 ALGORITHM_VERSION 里，
每次推荐都会把明细和版本落库，方便日后评估与替换算法。
"""
import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.capability import Capability
from app.models.profile import UserProfile, UserSkill
from app.models.recruitment import Recruitment, RecruitmentStatus
from app.models.team import Team, TeamMember
from app.models.user import User, UserRole, UserStatus

ALGORITHM_VERSION = "rule-v1.0"
WEIGHTS = {
    "skill_match": 0.30,     # 所需技能命中率
    "complement": 0.25,      # 能补足团队短板的程度
    "experience": 0.15,      # 竞赛经历
    "role_fit": 0.15,        # 角色偏好 vs 需求
    "time_fit": 0.10,        # 每周可投入时间
    "preference_fit": 0.05,  # 竞赛方向偏好
}


def normalize(value: float, low: float, high: float) -> float:
    """线性归一化到 [0,1]。high<=low 时返回 0，避免除零。"""
    if high <= low:
        return 0.0
    return float(np.clip((value - low) / (high - low), 0.0, 1.0))


def jaccard(a: list[str], b: list[str]) -> float:
    """集合相似度：交集大小 / 并集大小。"""
    set_a, set_b = set(a), set(b)
    if not set_a and not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def get_user_skill_map(db: Session, user_id: int) -> dict[str, int]:
    """{能力名称: 熟练度}，一次 join 查询取全。"""
    rows = db.execute(
        select(Capability.name, UserSkill.level)
        .join(UserSkill, UserSkill.capability_id == Capability.id)
        .where(UserSkill.user_id == user_id)
    ).all()
    return {name: int(level) for name, level in rows}


def get_team_gaps(db: Session, team_id: int, all_caps: list[str]) -> list[str]:
    """团队里没人掌握的能力维度 = 短板。"""
    covered = set(
        db.scalars(
            select(Capability.name)
            .join(UserSkill, UserSkill.capability_id == Capability.id)
            .join(TeamMember, TeamMember.user_id == UserSkill.user_id)
            .where(TeamMember.team_id == team_id)
        ).all()
    )
    return [name for name in all_caps if name not in covered]


def score_match(
    db: Session,
    user: User,
    *,
    required_skills: list[str],
    required_roles: list[str],
    competition_track: str,
    gaps: list[str],
) -> dict:
    """核心评分函数：六个维度 + 每个维度的理由。"""
    skill_map = get_user_skill_map(db, user.id)
    profile = db.get(UserProfile, user.id)
    pref = profile.preference if profile and profile.preference else {}

    # 1. 技能匹配：所需技能里命中了多少
    required = set(required_skills)
    matched = required & set(skill_map)
    skill_score = len(matched) / len(required) if required else 0.5

    # 2. 互补性：自己的强项(Skill>=4)能补团队几个短板
    strong = {name for name, lv in skill_map.items() if lv >= 4}
    filled = strong & set(gaps)
    complement_score = len(filled) / len(gaps) if gaps else 0.5

    # 3. 竞赛经历：用经历条数归一化（0~3 段映射到 0~1）
    comp_count = len(profile.competitions) if profile and profile.competitions else 0
    experience_score = normalize(comp_count, 0, 3)

    # 4. 角色匹配：偏好角色与需求角色的 Jaccard 相似度
    preferred = list(pref.get("preferred_roles", []))
    role_score = jaccard(preferred, required_roles) if required_roles else 0.5

    # 5. 时间投入：每周 0~20 小时映射到 0~1
    hours = pref.get("weekly_hours", 0)
    time_score = normalize(hours, 0, 20)

    # 6. 方向偏好：完全一致 1.0，否则 0.5（保守估计）
    pref_score = 1.0 if pref.get("preferred_track") == competition_track else 0.5

    raw = {
        "skill_match": skill_score,
        "complement": complement_score,
        "experience": experience_score,
        "role_fit": role_score,
        "time_fit": time_score,
        "preference_fit": pref_score,
    }
    reasons = {
        "skill_match": f"匹配 {len(matched)}/{len(required)} 项所需技能",
        "complement": f"可补足团队 {len(filled)} 项短板",
        "experience": f"有 {comp_count} 段竞赛经历",
        "role_fit": "角色偏好与需求匹配" if role_score > 0.5 else "角色偏好与需求一般",
        "time_fit": f"每周可投入 {hours} 小时",
        "preference_fit": (
            "竞赛方向符合偏好" if pref_score == 1.0 else "竞赛方向未明确匹配偏好"
        ),
    }
    breakdown = {
        key: {
            "score": round(raw[key], 3),
            "weight": weight,
            "reason": reasons[key],
        }
        for key, weight in WEIGHTS.items()
    }
    total = sum(raw[key] * weight for key, weight in WEIGHTS.items())

    return {
        "score": round(total, 3),
        "breakdown": breakdown,
        "strengths": [name for name, lv in skill_map.items() if lv >= 4],
        "gaps": [name for name in gaps if name not in skill_map],
        "algorithm_version": ALGORITHM_VERSION,
    }


def score_student_for_recruitment(db: Session, user: User, rec: Recruitment) -> dict:
    """学生 ↔ 招募：把招募信息翻译成评分输入。"""
    all_caps = [c.name for c in db.scalars(select(Capability)).all()]
    gaps = get_team_gaps(db, rec.team_id, all_caps)
    return score_match(
        db,
        user,
        required_skills=rec.required_skills or [],
        required_roles=rec.required_roles or [],
        competition_track=rec.competition_track,
        gaps=gaps,
    )


def recommend_recruitments(db: Session, user: User, top_k: int = 10) -> list[dict]:
    """学生视角：推荐最适合加入的招募。"""
    joined_team_ids = set(
        db.scalars(
            select(TeamMember.team_id).where(TeamMember.user_id == user.id)
        ).all()
    )
    recs = db.scalars(
        select(Recruitment).where(Recruitment.status == RecruitmentStatus.OPEN)
    ).all()

    items = []
    for rec in recs:
        if rec.team_id in joined_team_ids:
            continue
        result = score_student_for_recruitment(db, user, rec)
        items.append(
            {
                "target_type": "recruitment",
                "target_id": rec.id,
                "title": rec.title,
                "team_id": rec.team_id,
                **result,
            }
        )
    items.sort(key=lambda x: x["score"], reverse=True)
    return items[:top_k]


def recommend_members(db: Session, team_id: int, top_k: int = 10) -> list[dict]:
    """队长视角：按团队短板找候选成员（设计说明书 2.4 的双向推荐）。"""
    team = db.get(Team, team_id)
    if team is None:
        return []
    rec = db.scalar(
        select(Recruitment).where(
            Recruitment.team_id == team_id,
            Recruitment.status == RecruitmentStatus.OPEN,
        )
    )
    all_caps = [c.name for c in db.scalars(select(Capability)).all()]
    gaps = get_team_gaps(db, team_id, all_caps)
    existing_ids = set(
        db.scalars(
            select(TeamMember.user_id).where(TeamMember.team_id == team_id)
        ).all()
    )
    if len(existing_ids) >= team.max_size:
        return []
    candidates = db.scalars(
        select(User).where(
            User.status == UserStatus.ACTIVE,
            User.role.in_([UserRole.STUDENT, UserRole.LEADER]),
        )
    ).all()

    items = []
    for user in candidates:
        if user.id in existing_ids:
            continue
        result = score_match(
            db,
            user,
            required_skills=(rec.required_skills if rec else []) or [],
            required_roles=(rec.required_roles if rec else []) or [],
            competition_track=team.competition_track,
            gaps=gaps,
        )
        items.append(
            {
                "target_type": "user",
                "target_id": user.id,
                "title": user.real_name or user.username,
                "team_id": team_id,
                **result,
            }
        )
    items.sort(key=lambda x: x["score"], reverse=True)
    return items[:top_k]
