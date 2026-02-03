"""
Activity Model

Handles activity tracking, pipeline management, and Kanban board functionality.
"""

import uuid
from datetime import datetime
from enum import Enum

from app.extensions import db
from app.models.user import GUID, JSONType


class ActivityType(str, Enum):
    """Type of activity recorded."""

    RECRUITER_ADDED = "recruiter_added"
    MESSAGE_SENT = "message_sent"
    MESSAGE_OPENED = "message_opened"
    RESPONSE_RECEIVED = "response_received"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    OFFER_RECEIVED = "offer_received"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_DECLINED = "offer_declined"
    STATUS_CHANGE = "status_change"
    RESUME_UPLOADED = "resume_uploaded"
    RESUME_TAILORED = "resume_tailored"
    RESEARCH_COMPLETED = "research_completed"
    FOLLOW_UP_SENT = "follow_up_sent"
    NOTE_ADDED = "note_added"


class PipelineStage(str, Enum):
    """Kanban pipeline stages."""

    NEW = "new"
    RESEARCHING = "researching"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class Activity(db.Model):
    """
    Activity model for tracking user actions and recruiter pipeline.

    Used for:
    - Activity timeline on dashboard
    - Kanban board visualization
    - Priority score calculations
    - Analytics and reporting
    """

    __tablename__ = "activities"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey("users.id"), nullable=False, index=True)

    # Activity Details
    activity_type = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.String(500), nullable=True)
    extra_data = db.Column(JSONType(), default=dict)  # Additional context

    # Related Entities
    recruiter_id = db.Column(GUID(), db.ForeignKey("recruiters.id"), nullable=True, index=True)
    resume_id = db.Column(GUID(), db.ForeignKey("resumes.id"), nullable=True)
    message_id = db.Column(GUID(), db.ForeignKey("messages.id"), nullable=True)

    # Pipeline Information (for Kanban)
    pipeline_stage = db.Column(db.String(50), nullable=True, index=True)
    previous_stage = db.Column(db.String(50), nullable=True)

    # Priority (for sorting and recommendations)
    priority_score = db.Column(db.Integer, default=0)  # 0-100
    is_urgent = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)

    # Status
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = db.relationship("User", backref=db.backref("activities", lazy="dynamic"))
    recruiter = db.relationship("Recruiter", backref=db.backref("activities", lazy="dynamic"))
    resume = db.relationship("Resume", backref=db.backref("activities", lazy="dynamic"))
    message = db.relationship("Message", backref=db.backref("activities", lazy="dynamic"))

    def __repr__(self):
        return f"<Activity {self.activity_type} - {self.created_at}>"

    @property
    def is_overdue(self) -> bool:
        """Check if activity is past due date."""
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date and not self.is_completed

    def to_dict(self) -> dict:
        """Convert activity to dictionary representation."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "activity_type": self.activity_type,
            "description": self.description,
            "extra_data": self.extra_data,
            "recruiter_id": str(self.recruiter_id) if self.recruiter_id else None,
            "resume_id": str(self.resume_id) if self.resume_id else None,
            "message_id": str(self.message_id) if self.message_id else None,
            "pipeline_stage": self.pipeline_stage,
            "priority_score": self.priority_score,
            "is_urgent": self.is_urgent,
            "is_overdue": self.is_overdue,
            "is_completed": self.is_completed,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": (self.completed_at.isoformat() if self.completed_at else None),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PipelineItem(db.Model):
    """
    Pipeline item for Kanban board management.

    Separate from Activity to allow for board customization
    and drag-drop reordering.
    """

    __tablename__ = "pipeline_items"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey("users.id"), nullable=False, index=True)
    recruiter_id = db.Column(GUID(), db.ForeignKey("recruiters.id"), nullable=False, index=True)

    # Stage & Position
    stage = db.Column(db.String(50), nullable=False, index=True)
    position = db.Column(db.Integer, default=0)  # For ordering within column

    # Quick Stats (denormalized for performance)
    last_activity_date = db.Column(db.DateTime, nullable=True)
    next_action = db.Column(db.String(255), nullable=True)
    next_action_date = db.Column(db.DateTime, nullable=True)

    # Priority Score Components
    priority_score = db.Column(db.Integer, default=0)
    days_in_stage = db.Column(db.Integer, default=0)

    # Timestamps
    entered_stage_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref=db.backref("pipeline_items", lazy="dynamic"))
    recruiter = db.relationship("Recruiter", backref=db.backref("pipeline_item", uselist=False))

    def __repr__(self):
        return f"<PipelineItem {self.recruiter_id} @ {self.stage}>"

    def to_dict(self) -> dict:
        """Convert pipeline item to dictionary representation."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "recruiter_id": str(self.recruiter_id),
            "stage": self.stage,
            "position": self.position,
            "priority_score": self.priority_score,
            "days_in_stage": self.days_in_stage,
            "last_activity_date": (
                self.last_activity_date.isoformat() if self.last_activity_date else None
            ),
            "next_action": self.next_action,
            "next_action_date": (
                self.next_action_date.isoformat() if self.next_action_date else None
            ),
            "entered_stage_at": (
                self.entered_stage_at.isoformat() if self.entered_stage_at else None
            ),
        }
