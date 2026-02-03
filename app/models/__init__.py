"""
Jobezie Database Models

Import all models here for easy access and to ensure they're registered
with SQLAlchemy before migrations are created.
"""

from app.models.user import User, SubscriptionTier, CareerStage, GUID, JSONType
from app.models.resume import Resume, ResumeVersion
from app.models.recruiter import Recruiter, RecruiterStatus, RecruiterNote
from app.models.message import Message, MessageType, MessageStatus
from app.models.activity import Activity, ActivityType, PipelineStage, PipelineItem

__all__ = [
    # User
    'User',
    'SubscriptionTier',
    'CareerStage',
    'GUID',
    'JSONType',
    # Resume
    'Resume',
    'ResumeVersion',
    # Recruiter
    'Recruiter',
    'RecruiterStatus',
    'RecruiterNote',
    # Message
    'Message',
    'MessageType',
    'MessageStatus',
    # Activity
    'Activity',
    'ActivityType',
    'PipelineStage',
    'PipelineItem',
]
