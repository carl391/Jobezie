"""
Message Model

Handles outreach messages with AI generation and quality scoring.
"""

import uuid
from datetime import datetime
from enum import Enum

from app.extensions import db
from app.models.user import GUID, JSONType


class MessageType(str, Enum):
    """Type of outreach message."""

    INITIAL_OUTREACH = "initial_outreach"
    FOLLOW_UP = "follow_up"
    THANK_YOU = "thank_you"
    CHECK_IN = "check_in"


class MessageStatus(str, Enum):
    """Message status in lifecycle."""

    DRAFT = "draft"
    READY = "ready"
    SENT = "sent"
    OPENED = "opened"
    RESPONDED = "responded"


class Message(db.Model):
    """
    Message model for recruiter outreach.

    Quality Score Formula (100 points):
    quality = words(25%) + personalization(25%) + metrics(25%) + cta(20%) + tone(5%)

    Evidence-Based Constraints:
    - < 150 words = 22% higher response rate
    - Personalized subject = 41% higher open rate
    - Single CTA = reduces confusion
    """

    __tablename__ = "messages"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey("users.id"), nullable=False, index=True)
    recruiter_id = db.Column(GUID(), db.ForeignKey("recruiters.id"), nullable=True, index=True)

    # Message Content
    message_type = db.Column(db.String(50), default=MessageType.INITIAL_OUTREACH.value)
    subject = db.Column(db.String(255), nullable=True)
    body = db.Column(db.Text, nullable=False)
    signature = db.Column(db.Text, nullable=True)

    # Generation Context
    generation_prompt = db.Column(db.Text, nullable=True)
    generation_context = db.Column(JSONType(), default=dict)  # User profile, recruiter data used
    ai_model_used = db.Column(db.String(100), nullable=True)  # 'claude', 'openai'
    is_ai_generated = db.Column(db.Boolean, default=False)

    # Quality Scores (0-100 each)
    quality_score = db.Column(db.Integer, nullable=True)
    quality_words_score = db.Column(db.Integer, nullable=True)  # 25%
    quality_personalization_score = db.Column(db.Integer, nullable=True)  # 25%
    quality_metrics_score = db.Column(db.Integer, nullable=True)  # 25%
    quality_cta_score = db.Column(db.Integer, nullable=True)  # 20%
    quality_tone_score = db.Column(db.Integer, nullable=True)  # 5%

    # Quality Analysis
    quality_feedback = db.Column(JSONType(), default=list)
    quality_suggestions = db.Column(JSONType(), default=list)

    # Message Stats
    word_count = db.Column(db.Integer, nullable=True)
    has_personalization = db.Column(db.Boolean, default=False)
    has_metrics = db.Column(db.Boolean, default=False)
    has_cta = db.Column(db.Boolean, default=False)
    personalization_elements = db.Column(JSONType(), default=list)  # What was personalized

    # Status & Tracking
    status = db.Column(db.String(50), default=MessageStatus.DRAFT.value)
    sent_at = db.Column(db.DateTime, nullable=True)
    opened_at = db.Column(db.DateTime, nullable=True)
    responded_at = db.Column(db.DateTime, nullable=True)

    # Version Control (for edits)
    version = db.Column(db.Integer, default=1)
    parent_message_id = db.Column(GUID(), db.ForeignKey("messages.id"), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref=db.backref("messages", lazy="dynamic"))
    recruiter = db.relationship("Recruiter", backref=db.backref("messages", lazy="dynamic"))
    versions = db.relationship("Message", backref=db.backref("parent_message", remote_side=[id]))

    def __repr__(self):
        return f"<Message {self.id} - {self.message_type}>"

    @property
    def quality_breakdown(self) -> dict:
        """Return quality score breakdown with weights."""
        return {
            "total": self.quality_score,
            "components": {
                "words": {
                    "score": self.quality_words_score,
                    "weight": 25,
                    "weighted": (self.quality_words_score or 0) * 0.25,
                },
                "personalization": {
                    "score": self.quality_personalization_score,
                    "weight": 25,
                    "weighted": (self.quality_personalization_score or 0) * 0.25,
                },
                "metrics": {
                    "score": self.quality_metrics_score,
                    "weight": 25,
                    "weighted": (self.quality_metrics_score or 0) * 0.25,
                },
                "cta": {
                    "score": self.quality_cta_score,
                    "weight": 20,
                    "weighted": (self.quality_cta_score or 0) * 0.20,
                },
                "tone": {
                    "score": self.quality_tone_score,
                    "weight": 5,
                    "weighted": (self.quality_tone_score or 0) * 0.05,
                },
            },
        }

    @property
    def is_within_word_limit(self) -> bool:
        """Check if message is within optimal word limit (<150 words)."""
        return (self.word_count or 0) <= 150

    def calculate_word_count(self) -> int:
        """Calculate and store word count."""
        if not self.body:
            self.word_count = 0
        else:
            self.word_count = len(self.body.split())
        return self.word_count

    def to_dict(self, include_generation: bool = False) -> dict:
        """Convert message to dictionary representation."""
        data = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "recruiter_id": str(self.recruiter_id) if self.recruiter_id else None,
            "message_type": self.message_type,
            "subject": self.subject,
            "body": self.body,
            "word_count": self.word_count,
            "is_within_word_limit": self.is_within_word_limit,
            "quality_score": self.quality_score,
            "quality_breakdown": self.quality_breakdown,
            "feedback": self.quality_feedback,
            "suggestions": self.quality_suggestions,
            "has_personalization": self.has_personalization,
            "has_metrics": self.has_metrics,
            "has_cta": self.has_cta,
            "status": self.status,
            "is_ai_generated": self.is_ai_generated,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_generation:
            data.update(
                {
                    "generation_prompt": self.generation_prompt,
                    "generation_context": self.generation_context,
                    "ai_model_used": self.ai_model_used,
                    "personalization_elements": self.personalization_elements,
                }
            )

        return data
