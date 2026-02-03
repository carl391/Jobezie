"""
Recruiter Model

Handles recruiter contacts, engagement tracking, and AI research data.
"""

import uuid
from datetime import datetime
from enum import Enum

from app.extensions import db
from app.models.user import GUID, JSONType


class RecruiterStatus(str, Enum):
    """Recruiter pipeline status."""

    NEW = "new"
    RESEARCHING = "researching"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class Recruiter(db.Model):
    """
    Recruiter model for CRM functionality.

    Engagement Score Formula:
    engagement = response_rate(40%) + open_rate(30%) + recency(30%)

    Fit Score Formula:
    fit = industry(30%) + location(20%) + specialty(25%) + tier(15%) + depth(10%)
    """

    __tablename__ = "recruiters"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey("users.id"), nullable=False, index=True)

    # Basic Information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    linkedin_url = db.Column(db.String(500), nullable=True)

    # Company Information
    company = db.Column(db.String(200), nullable=True)
    title = db.Column(db.String(200), nullable=True)
    company_type = db.Column(
        db.String(100), nullable=True
    )  # 'agency', 'corporate', 'executive_search'

    # Specialty Information
    specialty = db.Column(db.String(200), nullable=True)  # Role specialty
    industries = db.Column(JSONType(), default=list)
    locations = db.Column(JSONType(), default=list)
    roles_recruited = db.Column(JSONType(), default=list)
    salary_range_min = db.Column(db.Integer, nullable=True)
    salary_range_max = db.Column(db.Integer, nullable=True)

    # Source
    source = db.Column(db.String(200), nullable=True)  # Where recruiter was found

    # Pipeline Status
    status = db.Column(db.String(50), default=RecruiterStatus.NEW.value, index=True)
    priority_score = db.Column(db.Integer, default=0)  # 0-100 calculated priority

    # Engagement Metrics
    messages_sent = db.Column(db.Integer, default=0)
    messages_opened = db.Column(db.Integer, default=0)
    responses_received = db.Column(db.Integer, default=0)
    has_responded = db.Column(db.Boolean, default=False)
    engagement_score = db.Column(db.Integer, default=0)  # 0-100 calculated
    engagement_components = db.Column(JSONType(), default=dict)

    # Fit Score
    fit_score = db.Column(db.Integer, default=0)  # 0-100 calculated
    fit_components = db.Column(JSONType(), default=dict)

    # AI Research Data
    research_data = db.Column(JSONType(), default=dict)
    research_summary = db.Column(db.Text, nullable=True)
    recent_posts = db.Column(JSONType(), default=list)
    mutual_connections = db.Column(JSONType(), default=list)
    company_news = db.Column(JSONType(), default=list)
    conversation_starters = db.Column(JSONType(), default=list)
    personalization_hooks = db.Column(JSONType(), default=list)
    researched_at = db.Column(db.DateTime, nullable=True)

    # Contact History
    last_contact_date = db.Column(db.DateTime, nullable=True)
    last_response_date = db.Column(db.DateTime, nullable=True)
    next_action = db.Column(db.String(255), nullable=True)
    next_action_date = db.Column(db.DateTime, nullable=True)
    follow_up_count = db.Column(db.Integer, default=0)

    # Notes
    notes_text = db.Column(db.Text, nullable=True)
    tags = db.Column(JSONType(), default=list)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref=db.backref("recruiters", lazy="dynamic"))

    def __repr__(self):
        return f"<Recruiter {self.full_name} @ {self.company}>"

    @property
    def full_name(self) -> str:
        """Return full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def response_rate(self) -> float:
        """Calculate response rate percentage."""
        if self.messages_sent == 0:
            return 0.0
        return (self.responses_received / self.messages_sent) * 100

    @property
    def open_rate(self) -> float:
        """Calculate open rate percentage."""
        if self.messages_sent == 0:
            return 0.0
        return (self.messages_opened / self.messages_sent) * 100

    @property
    def days_since_contact(self) -> int:
        """Calculate days since last contact."""
        if not self.last_contact_date:
            return -1
        delta = datetime.utcnow() - self.last_contact_date
        return delta.days

    @property
    def needs_follow_up(self) -> bool:
        """Check if recruiter needs follow-up based on 5-7 day research."""
        if self.status in [
            RecruiterStatus.DECLINED.value,
            RecruiterStatus.ACCEPTED.value,
        ]:
            return False
        if self.has_responded:
            return False
        days = self.days_since_contact
        return 5 <= days <= 14 and self.follow_up_count < 3

    def to_dict(self, include_research: bool = False, include_engagement: bool = False) -> dict:
        """Convert recruiter to dictionary representation."""
        data = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "linkedin_url": self.linkedin_url,
            "company": self.company,
            "title": self.title,
            "company_type": self.company_type,
            "specialty": self.specialty,
            "industries": self.industries,
            "locations": self.locations,
            "status": self.status,
            "priority_score": self.priority_score,
            "engagement_score": self.engagement_score,
            "fit_score": self.fit_score,
            "response_rate": round(self.response_rate, 1),
            "messages_sent": self.messages_sent,
            "responses_received": self.responses_received,
            "has_responded": self.has_responded,
            "days_since_contact": self.days_since_contact,
            "needs_follow_up": self.needs_follow_up,
            "last_contact_date": (
                self.last_contact_date.isoformat() if self.last_contact_date else None
            ),
            "next_action": self.next_action,
            "next_action_date": (
                self.next_action_date.isoformat() if self.next_action_date else None
            ),
            "source": self.source,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_engagement:
            data.update(
                {
                    "engagement_components": self.engagement_components,
                    "fit_components": self.fit_components,
                    "messages_opened": self.messages_opened,
                }
            )

        if include_research:
            data.update(
                {
                    "research_summary": self.research_summary,
                    "recent_posts": self.recent_posts,
                    "mutual_connections": self.mutual_connections,
                    "company_news": self.company_news,
                    "conversation_starters": self.conversation_starters,
                    "personalization_hooks": self.personalization_hooks,
                    "researched_at": (
                        self.researched_at.isoformat() if self.researched_at else None
                    ),
                }
            )

        return data


class RecruiterNote(db.Model):
    """
    Notes for recruiters.

    Allows tracking of conversations, research, and other interactions.
    """

    __tablename__ = "recruiter_notes"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    recruiter_id = db.Column(GUID(), db.ForeignKey("recruiters.id"), nullable=False, index=True)

    # Note Content
    content = db.Column(db.Text, nullable=False)
    note_type = db.Column(
        db.String(50), default="general"
    )  # general, call, email, meeting, research

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recruiter = db.relationship("Recruiter", backref=db.backref("notes", lazy="dynamic"))

    def __repr__(self):
        return f"<RecruiterNote {self.id} - {self.note_type}>"

    def to_dict(self) -> dict:
        """Convert note to dictionary representation."""
        return {
            "id": str(self.id),
            "recruiter_id": str(self.recruiter_id),
            "content": self.content,
            "note_type": self.note_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
