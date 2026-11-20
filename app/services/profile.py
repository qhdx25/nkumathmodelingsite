"""个人画像服务（教程第 05 章）。"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessError
from app.models.capability import Capability
from app.models.profile import UserProfile, UserSkill
from app.models.user import User
from app.schemas.profile import Preference, ProfileUpdate
from app.services.resume import can_view_resume, serialize_resume


def get_profile(db: Session, user: User, viewer: User | None = None) -> dict:
    """拼接画像：技能（联表取名称）+ 经历 + 偏好。"""
    viewer = viewer or user
    # join 一次查出技能与维度名称，避免循环里 N+1 查询
    rows = db.execute(
        select(UserSkill, Capability)
        .join(Capability, Capability.id == UserSkill.capability_id)
        .where(UserSkill.user_id == user.id)
        .order_by(Capability.id)
    ).all()
    skills = [
        {
            "capability_id": cap.id,
            "name": cap.name,
            "category": cap.category.value,
            "level": skill.level,
            "weight": cap.weight,
        }
        for skill, cap in rows
    ]

    profile = db.get(UserProfile, user.id)
    return {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "real_name": user.real_name,
        "school": user.school,
        "student_number": user.student_number,
        "college": user.college,
        "phone": user.phone,
        "email": user.email,
        "qq": user.qq,
        "wechat": user.wechat,
        "github": user.github,
        "skills": skills,
        "projects": profile.projects if profile and profile.projects else [],
        "competitions": profile.competitions if profile and profile.competitions else [],
        "preference": profile.preference if profile and profile.preference else {},
        "resume": (
            serialize_resume(user)
            if can_view_resume(db, viewer, user)
            else None
        ),
    }


def update_profile(db: Session, user: User, payload: ProfileUpdate) -> dict:
    """整体更新画像：多表写在同一个事务里。

    先校验所有 capability_id 存在，再删旧技能、写新技能，最后更新 JSON 列。
    任何一步失败都 rollback，避免“技能改了、偏好没改”的不一致状态。
    """
    try:
        if "email" in payload.model_fields_set and payload.email is None:
            raise BusinessError("邮箱不能为空", code=40001)
        if payload.email is not None and payload.email != user.email:
            duplicate = db.scalar(
                select(User).where(
                    User.email == str(payload.email),
                    User.id != user.id,
                )
            )
            if duplicate is not None:
                raise BusinessError("该邮箱已被其他账号使用", code=40901, http_status=409)

        for field in (
            "real_name",
            "school",
            "student_number",
            "college",
            "phone",
            "email",
            "qq",
            "wechat",
            "github",
        ):
            if field in payload.model_fields_set:
                value = getattr(payload, field)
                setattr(user, field, str(value) if field == "email" and value else value)

        if payload.skills is not None:
            # 一次性查出所有引用的维度，逐个 db.get 会产生 N+1 查询
            ids = [s.capability_id for s in payload.skills]
            caps = db.scalars(select(Capability).where(Capability.id.in_(ids))).all() if ids else []
            if len(caps) != len(set(ids)):
                raise BusinessError("存在不存在的能力维度 ID", code=40001)
            old_skills = db.scalars(
                select(UserSkill).where(UserSkill.user_id == user.id)
            ).all()
            for skill in old_skills:
                db.delete(skill)
            db.flush()  # 先执行删除，避免与同 (user, capability) 的新行撞唯一约束

            for item in payload.skills:
                db.add(
                    UserSkill(
                        user_id=user.id,
                        capability_id=item.capability_id,
                        level=item.level,
                    )
                )

        profile = db.get(UserProfile, user.id)
        if profile is None:
            profile = UserProfile(
                user_id=user.id,
                projects=[],
                competitions=[],
                preference=Preference().model_dump(mode="json"),
            )
            db.add(profile)

        # JSON 列必须“整体重新赋值”，SQLAlchemy 才能检测到变化
        if payload.projects is not None:
            profile.projects = [p.model_dump(mode="json") for p in payload.projects]
        if payload.competitions is not None:
            profile.competitions = [
                c.model_dump(mode="json") for c in payload.competitions
            ]
        if payload.preference is not None:
            profile.preference = payload.preference.model_dump(mode="json")

        db.commit()
    except Exception:
        db.rollback()
        raise
    return get_profile(db, user, viewer=user)
