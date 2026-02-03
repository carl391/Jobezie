"""
User Model

Core user model with authentication, profile data, and subscription management.
"""

import uuid
from datetime import datetime
from enum import Enum

import bcrypt
from sqlalchemy import TypeDecorator, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB

from app.extensions import db


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.
    Uses String(36) for compatibility with existing database schema.
    """
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


class JSONType(TypeDecorator):
    """
    Platform-independent JSON type.
    Uses PostgreSQL's JSONB when available, otherwise uses Text with JSON serialization.
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_JSONB())
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            import json
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        import json
        return json.loads(value) if isinstance(value, str) else value


class SubscriptionTier(str, Enum):
    """Subscription tier enumeration."""
    BASIC = 'basic'
    PRO = 'pro'
    EXPERT = 'expert'
    CAREER_KEEPER = 'career_keeper'


class CareerStage(str, Enum):
    """Career stage enumeration."""
    ENTRY_LEVEL = 'entry_level'
    EARLY_CAREER = 'early_career'
    MID_LEVEL = 'mid_level'
    SENIOR = 'senior'
    EXECUTIVE = 'executive'


class User(db.Model):
    """
    User model for Jobezie platform.

    Handles authentication, profile information, subscription status,
    and usage tracking for tier limits.
    """

    __tablename__ = 'users'

    # Primary Key
    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)

    # Authentication
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255), nullable=True)

    # Basic Profile
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    linkedin_url = db.Column(db.String(500), nullable=True)

    # Career Information
    years_experience = db.Column(db.Integer, nullable=True)
    career_stage = db.Column(db.String(50), nullable=True)
    current_role = db.Column(db.String(200), nullable=True)
    target_roles = db.Column(JSONType(), default=list)
    target_industries = db.Column(JSONType(), default=list)
    target_companies = db.Column(JSONType(), default=list)

    # Skills
    technical_skills = db.Column(JSONType(), default=list)
    soft_skills = db.Column(JSONType(), default=list)
    languages = db.Column(JSONType(), default=list)
    certifications = db.Column(JSONType(), default=list)

    # Preferences
    salary_expectation = db.Column(db.Integer, nullable=True)
    remote_preference = db.Column(db.String(50), nullable=True)  # 'remote', 'hybrid', 'onsite'
    relocation_willing = db.Column(db.Boolean, default=False)
    communication_style = db.Column(db.String(50), default='balanced')  # 'formal', 'casual', 'balanced'

    # Subscription
    subscription_tier = db.Column(db.String(50), default=SubscriptionTier.BASIC.value)
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True)
    subscription_expires_at = db.Column(db.DateTime, nullable=True)

    # Usage Tracking (monthly limits)
    monthly_recruiter_count = db.Column(db.Integer, default=0)
    monthly_research_count = db.Column(db.Integer, default=0)
    monthly_message_count = db.Column(db.Integer, default=0)
    monthly_resume_count = db.Column(db.Integer, default=0)
    monthly_tailoring_count = db.Column(db.Integer, default=0)
    daily_coach_count = db.Column(db.Integer, default=0)
    monthly_interview_prep_count = db.Column(db.Integer, default=0)
    usage_reset_date = db.Column(db.DateTime, nullable=True)

    # Onboarding
    onboarding_completed = db.Column(db.Boolean, default=False)
    onboarding_step = db.Column(db.Integer, default=1)

    # Account Status
    is_active = db.Column(db.Boolean, default=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        parts = [self.first_name, self.last_name]
        return ' '.join(p for p in parts if p) or 'Anonymous'

    @property
    def tier_limits(self) -> dict:
        """Return usage limits based on subscription tier."""
        limits = {
            SubscriptionTier.BASIC.value: {
                'recruiters': 5,
                'tailored_resumes': 2,
                'ai_messages': 10,
                'research': 5,
                'coach_daily': 10,
                'interview_prep': 0,
                'skills_gap': 1,
            },
            SubscriptionTier.PRO.value: {
                'recruiters': 50,
                'tailored_resumes': 10,
                'ai_messages': 100,
                'research': 25,
                'coach_daily': 50,
                'interview_prep': 3,
                'skills_gap': 5,
            },
            SubscriptionTier.EXPERT.value: {
                'recruiters': -1,  # Unlimited
                'tailored_resumes': -1,
                'ai_messages': -1,
                'research': -1,
                'coach_daily': -1,
                'interview_prep': -1,
                'skills_gap': -1,
            },
            SubscriptionTier.CAREER_KEEPER.value: {
                'recruiters': 5,
                'tailored_resumes': 1,
                'ai_messages': 10,
                'research': 2,
                'coach_daily': 10,
                'interview_prep': 1,
                'skills_gap': 1,
            },
        }
        return limits.get(self.subscription_tier, limits[SubscriptionTier.BASIC.value])

    def can_use_feature(self, feature: str, count: int = 1) -> bool:
        """Check if user can use a feature based on tier limits."""
        limit = self.tier_limits.get(feature, 0)
        if limit == -1:  # Unlimited
            return True

        current_usage = {
            'recruiters': self.monthly_recruiter_count,
            'tailored_resumes': self.monthly_tailoring_count,
            'ai_messages': self.monthly_message_count,
            'research': self.monthly_research_count,
            'coach_daily': self.daily_coach_count,
            'interview_prep': self.monthly_interview_prep_count,
            'skills_gap': self.monthly_research_count,  # Shares with research
        }

        return current_usage.get(feature, 0) + count <= limit

    def to_dict(self, include_private: bool = False) -> dict:
        """
        Convert user to dictionary representation.

        Args:
            include_private: Include sensitive fields like subscription details
        """
        data = {
            'id': str(self.id),
            'email': self.email,
            'email_verified': self.email_verified,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'location': self.location,
            'linkedin_url': self.linkedin_url,
            'years_experience': self.years_experience,
            'career_stage': self.career_stage,
            'current_role': self.current_role,
            'target_roles': self.target_roles,
            'target_industries': self.target_industries,
            'technical_skills': self.technical_skills,
            'soft_skills': self.soft_skills,
            'subscription_tier': self.subscription_tier,
            'onboarding_completed': self.onboarding_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

        if include_private:
            data.update({
                'phone': self.phone,
                'target_companies': self.target_companies,
                'salary_expectation': self.salary_expectation,
                'remote_preference': self.remote_preference,
                'relocation_willing': self.relocation_willing,
                'communication_style': self.communication_style,
                'stripe_customer_id': self.stripe_customer_id,
                'subscription_expires_at': self.subscription_expires_at.isoformat() if self.subscription_expires_at else None,
                'tier_limits': self.tier_limits,
                'usage': {
                    'recruiters': self.monthly_recruiter_count,
                    'messages': self.monthly_message_count,
                    'research': self.monthly_research_count,
                    'tailoring': self.monthly_tailoring_count,
                    'coach_today': self.daily_coach_count,
                    'interview_prep': self.monthly_interview_prep_count,
                },
                'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            })

        return data

    @staticmethod
    def detect_career_stage(years: int) -> str:
        """
        Detect career stage from years of experience.

        Algorithm-based detection as specified in project requirements.
        """
        if years is None:
            return CareerStage.ENTRY_LEVEL.value
        elif years <= 2:
            return CareerStage.ENTRY_LEVEL.value
        elif years <= 5:
            return CareerStage.EARLY_CAREER.value
        elif years <= 10:
            return CareerStage.MID_LEVEL.value
        elif years <= 15:
            return CareerStage.SENIOR.value
        else:
            return CareerStage.EXECUTIVE.value
