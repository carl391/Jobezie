"""
Jobezie Database Models

Import all models here for easy access and to ensure they're registered
with SQLAlchemy before migrations are created.
"""

from app.models.activity import Activity, ActivityType, PipelineItem, PipelineStage
from app.models.admin_audit_log import AdminAuditLog
from app.models.data_export_request import DataExportRequest
from app.models.labor_market import (
    LaborMarketData,
    Occupation,
    OccupationSkill,
    ShortageScore,
    Skill,
)
from app.models.message import Message, MessageStatus, MessageType
from app.models.notification import Notification, NotificationType
from app.models.recruiter import Recruiter, RecruiterNote, RecruiterStatus
from app.models.resume import Resume, ResumeVersion
from app.models.user import GUID, CareerStage, JSONType, SubscriptionTier, User

__all__ = [
    # User
    "User",
    "SubscriptionTier",
    "CareerStage",
    "GUID",
    "JSONType",
    # Resume
    "Resume",
    "ResumeVersion",
    # Recruiter
    "Recruiter",
    "RecruiterStatus",
    "RecruiterNote",
    # Message
    "Message",
    "MessageType",
    "MessageStatus",
    # Notification
    "Notification",
    "NotificationType",
    # Activity
    "Activity",
    "ActivityType",
    "PipelineStage",
    "PipelineItem",
    # Labor Market
    "Occupation",
    "Skill",
    "OccupationSkill",
    "LaborMarketData",
    "ShortageScore",
    # Admin
    "AdminAuditLog",
    # Data Export
    "DataExportRequest",
]
