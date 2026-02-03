"""
Jobezie Database Models

Import all models here for easy access and to ensure they're registered
with SQLAlchemy before migrations are created.
"""

from app.models.activity import Activity, ActivityType, PipelineItem, PipelineStage
from app.models.message import Message, MessageStatus, MessageType
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
    # Activity
    "Activity",
    "ActivityType",
    "PipelineStage",
    "PipelineItem",
]
