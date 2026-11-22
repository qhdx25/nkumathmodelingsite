"""数据库初始化与演示种子数据。

两个动作：
1. create_all() —— 按模型定义建表（学习/开发用；生产用 Alembic 迁移）；
2. seed_demo_data() —— 幂等地插入能力维度和演示账号，让项目启动后立刻可体验完整流程。

“幂等”= 重复执行不会产生重复数据：每条插入前先查是否存在。
"""
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base, SessionLocal, engine
from app.models import (  # noqa: F401 —— 导入即注册全部表到 Base.metadata
    Capability,
    Recruitment,
    Team,
    TeamMember,
    TeamRole,
    TeamStatus,
    User,
    UserProfile,
    UserRole,
    UserSkill,
    RecruitmentStatus,
)
from app.schemas.capability import CapabilityCategory

# 六大能力维度（设计说明书 2.2 节）
CAPABILITY_SEED = [
    ("数学理论", CapabilityCategory.FOUNDATION, 1.0, "数学基础理论储备"),
    ("编程实现", CapabilityCategory.IMPLEMENTATION, 1.2, "算法实现与代码能力"),
    ("数据分析", CapabilityCategory.ANALYSIS, 1.1, "数据清洗、统计与可视化"),
    ("建模分析", CapabilityCategory.MODELING, 1.3, "模型构建与求解"),
    ("论文写作", CapabilityCategory.WRITING, 1.0, "论文结构与学术表达"),
    ("竞赛协作", CapabilityCategory.COLLABORATION, 0.9, "团队沟通与任务推进"),
]

# 演示账号：password 字段只是种子数据来源，插入时会被哈希，绝不入库明文
USER_SEED = [
    ("alice", "alice@example.com", "Alice", "清华大学", UserRole.STUDENT, "123456"),
    ("bob", "bob@example.com", "Bob", "北京大学", UserRole.LEADER, "123456"),
    ("carol", "carol@example.com", "Carol", "浙江大学", UserRole.STUDENT, "123456"),
    ("association", "association@example.com", "协会管理员", "平台", UserRole.ASSOCIATION_ADMIN, "123456"),
    ("admin", "admin@example.com", "Admin", "平台", UserRole.PLATFORM_ADMIN, "123456"),
]


def seed_demo_data(db: Session) -> None:
    """插入演示数据；已存在则跳过，保证反复启动不会重复。"""
    # --- 能力维度 ---
    if db.scalar(select(func.count()).select_from(Capability)) == 0:
        for name, category, weight, desc in CAPABILITY_SEED:
            db.add(
                Capability(
                    name=name, category=category, weight=weight, description=desc
                )
            )
        db.flush()  # 先拿到自增 id，后面给用户技能用

    caps = {c.name: c for c in db.scalars(select(Capability)).all()}

    # --- 用户 ---
    users: dict[str, User] = {}
    for username, email, real_name, school, role, plain_pwd in USER_SEED:
        user = db.scalar(select(User).where(User.username == username))
        if user is None:
            user = User(
                username=username,
                email=email,
                hashed_password=hash_password(plain_pwd),
                real_name=real_name,
                school=school,
                role=role,
            )
            db.add(user)
        users[username] = user
    db.flush()

    # --- 给 alice / bob 填技能，让团队画像和推荐有数据可算 ---
    for username, skills in {
        "alice": {"数学理论": 5, "编程实现": 4, "建模分析": 4},
        "bob": {"编程实现": 5, "论文写作": 4, "竞赛协作": 5},
        "carol": {"数据分析": 5, "论文写作": 3},
    }.items():
        uid = users[username].id
        exists = db.scalar(
            select(func.count())
            .select_from(UserSkill)
            .where(UserSkill.user_id == uid)
        )
        if exists == 0:
            for cap_name, level in skills.items():
                db.add(UserSkill(user_id=uid, capability_id=caps[cap_name].id, level=level))
            db.add(
                UserProfile(
                    user_id=uid,
                    projects=[],
                    competitions=[],
                    preference={"weekly_hours": 10, "preferred_track": "math_modeling"},
                )
            )

    # --- Bob 的队伍 + 一条开放招募，供首页展示与申请闭环使用 ---
    team = db.scalar(select(Team).where(Team.name == "数模先锋队"))
    if team is None:
        team = Team(
            name="数模先锋队",
            description="备战全国大学生数学建模竞赛，缺论文写作与数据分析队友。",
            competition_track="math_modeling",
            max_size=3,
            status=TeamStatus.RECRUITING,
            created_by=users["bob"].id,
        )
        db.add(team)
        db.flush()
        db.add(
            TeamMember(team_id=team.id, user_id=users["bob"].id, role=TeamRole.LEADER)
        )
        db.add(
            Recruitment(
                team_id=team.id,
                title="数模国赛招队友（论文/数据方向）",
                competition_track="math_modeling",
                target_size=3,
                required_roles=["writer", "analyst"],
                required_skills=["论文写作", "数据分析"],
                description="已有一名建模和一名编程，诚邀论文写作与数据分析高手加入。",
                status=RecruitmentStatus.OPEN,
            )
        )
    # 兼容旧演示库：修正历史数据中“目标人数小于当前人数/团队容量”的状态。
    from app.models.application import Application, ApplicationStatus
    from app.services.recruitment import close_completed_recruitments

    for open_rec in db.scalars(
        select(Recruitment).where(Recruitment.status == RecruitmentStatus.OPEN)
    ).all():
        member_count = int(
            db.scalar(
                select(func.count())
                .select_from(TeamMember)
                .where(TeamMember.team_id == open_rec.team_id)
            )
            or 0
        )
        team = db.get(Team, open_rec.team_id)
        if team is None:
            continue
        open_rec.target_size = min(
            team.max_size, max(open_rec.target_size, member_count)
        )
        if member_count >= team.max_size:
            team.status = TeamStatus.ACTIVE
        close_completed_recruitments(db, team.id, member_count)
        if open_rec.status == RecruitmentStatus.CLOSED:
            for application in db.scalars(
                select(Application).where(
                    Application.recruitment_id == open_rec.id,
                    Application.status == ApplicationStatus.PENDING,
                )
            ).all():
                application.status = ApplicationStatus.REJECTED
                application.review_note = "招募已关闭"
                application.reviewed_at = datetime.now(timezone.utc)
                application.reviewed_by = team.created_by

    # 状态为 active 但尚未满员的旧数据恢复为组建中，避免错误显示“组队完成”。
    for team in db.scalars(select(Team)).all():
        member_count = int(
            db.scalar(
                select(func.count())
                .select_from(TeamMember)
                .where(TeamMember.team_id == team.id)
            )
            or 0
        )
        if team.status == TeamStatus.ACTIVE and member_count < team.max_size:
            team.status = TeamStatus.FORMING

    db.commit()


def init_db() -> None:
    """应用启动时调用一次。"""
    # 导入模型触发类定义，Base.metadata 才完整
    import app.models  # noqa: F401

    if settings.AUTO_CREATE_TABLES:
        Base.metadata.create_all(bind=engine)

    if settings.SEED_DEMO_DATA:
        with SessionLocal() as db:
            seed_demo_data(db)
