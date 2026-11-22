"""模型汇总模块。

关键坑点：SQLAlchemy 的 Base.metadata 只知道“被 import 过的模型”。
如果这里不集中导入，create_all() 会静默跳过没导入的表，运行时报 "no such table"。
所以任何需要建表的地方都 `from app.models import *`（或 import app.models）。
"""
from app.models.admin_log import AdminLog
from app.models.application import Application, ApplicationStatus
from app.models.capability import Capability
from app.models.message import Message, MessageType, Notification
from app.models.profile import UserProfile, UserSkill
from app.models.recommendation import Recommendation
from app.models.recruitment import Recruitment, RecruitmentStatus
from app.models.team import Team, TeamMember, TeamRole, TeamStatus
from app.models.user import User, UserRole, UserStatus

__all__ = [
    "AdminLog",
    "Application",
    "ApplicationStatus",
    "Capability",
    "Message",
    "MessageType",
    "Notification",
    "UserProfile",
    "UserSkill",
    "Recommendation",
    "Recruitment",
    "RecruitmentStatus",
    "Team",
    "TeamMember",
    "TeamRole",
    "TeamStatus",
    "User",
    "UserRole",
    "UserStatus",
]
