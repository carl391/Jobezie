"""Initial database schema

Revision ID: 001_initial
Revises:
Create Date: 2025-02-03
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        # Authentication
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('email_verified', sa.Boolean(), default=False),
        sa.Column('verification_token', sa.String(255), nullable=True),
        # Basic Profile
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('linkedin_url', sa.String(500), nullable=True),
        # Career Information
        sa.Column('years_experience', sa.Integer(), nullable=True),
        sa.Column('career_stage', sa.String(50), nullable=True),
        sa.Column('current_role', sa.String(200), nullable=True),
        sa.Column('target_roles', sa.Text(), nullable=True),  # JSON
        sa.Column('target_industries', sa.Text(), nullable=True),  # JSON
        sa.Column('target_companies', sa.Text(), nullable=True),  # JSON
        # Skills
        sa.Column('technical_skills', sa.Text(), nullable=True),  # JSON
        sa.Column('soft_skills', sa.Text(), nullable=True),  # JSON
        sa.Column('languages', sa.Text(), nullable=True),  # JSON
        sa.Column('certifications', sa.Text(), nullable=True),  # JSON
        # Preferences
        sa.Column('salary_expectation', sa.Integer(), nullable=True),
        sa.Column('remote_preference', sa.String(50), nullable=True),
        sa.Column('relocation_willing', sa.Boolean(), default=False),
        sa.Column('communication_style', sa.String(50), default='balanced'),
        # Subscription
        sa.Column('subscription_tier', sa.String(50), default='basic'),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=True),
        sa.Column('subscription_expires_at', sa.DateTime(), nullable=True),
        # Usage Tracking
        sa.Column('monthly_recruiter_count', sa.Integer(), default=0),
        sa.Column('monthly_research_count', sa.Integer(), default=0),
        sa.Column('monthly_message_count', sa.Integer(), default=0),
        sa.Column('monthly_resume_count', sa.Integer(), default=0),
        sa.Column('monthly_tailoring_count', sa.Integer(), default=0),
        sa.Column('daily_coach_count', sa.Integer(), default=0),
        sa.Column('monthly_interview_prep_count', sa.Integer(), default=0),
        sa.Column('usage_reset_date', sa.DateTime(), nullable=True),
        # Onboarding
        sa.Column('onboarding_completed', sa.Boolean(), default=False),
        sa.Column('onboarding_step', sa.Integer(), default=1),
        # Account Status
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Resumes table
    op.create_table(
        'resumes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False, index=True),
        # File Information
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('file_name', sa.String(255), nullable=True),
        sa.Column('file_type', sa.String(50), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        # Parsed Content
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('parsed_sections', sa.Text(), nullable=True),  # JSON
        # Extracted Data
        sa.Column('contact_info', sa.Text(), nullable=True),  # JSON
        sa.Column('work_experience', sa.Text(), nullable=True),  # JSON
        sa.Column('education', sa.Text(), nullable=True),  # JSON
        sa.Column('skills', sa.Text(), nullable=True),  # JSON
        sa.Column('certifications', sa.Text(), nullable=True),  # JSON
        sa.Column('summary', sa.Text(), nullable=True),
        # ATS Scores
        sa.Column('ats_total_score', sa.Integer(), nullable=True),
        sa.Column('ats_compatibility_score', sa.Integer(), nullable=True),
        sa.Column('ats_keywords_score', sa.Integer(), nullable=True),
        sa.Column('ats_achievements_score', sa.Integer(), nullable=True),
        sa.Column('ats_formatting_score', sa.Integer(), nullable=True),
        sa.Column('ats_progression_score', sa.Integer(), nullable=True),
        sa.Column('ats_completeness_score', sa.Integer(), nullable=True),
        sa.Column('ats_fit_score', sa.Integer(), nullable=True),
        # ATS Analysis Details
        sa.Column('ats_recommendations', sa.Text(), nullable=True),  # JSON
        sa.Column('missing_keywords', sa.Text(), nullable=True),  # JSON
        sa.Column('weak_sections', sa.Text(), nullable=True),  # JSON
        # Tailoring
        sa.Column('is_tailored', sa.Boolean(), default=False),
        sa.Column('target_job_title', sa.String(255), nullable=True),
        sa.Column('target_company', sa.String(255), nullable=True),
        sa.Column('source_resume_id', sa.String(36), sa.ForeignKey('resumes.id'), nullable=True),
        # Status
        sa.Column('is_master', sa.Boolean(), default=False),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('parse_status', sa.String(50), default='pending'),
        # Timestamps
        sa.Column('analyzed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Resume Versions table
    op.create_table(
        'resume_versions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('resume_id', sa.String(36), sa.ForeignKey('resumes.id'), nullable=False, index=True),
        sa.Column('version_number', sa.Integer(), default=1),
        sa.Column('change_summary', sa.String(500), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('parsed_sections', sa.Text(), nullable=True),  # JSON
        sa.Column('ats_score', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # Recruiters table
    op.create_table(
        'recruiters',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False, index=True),
        # Basic Information
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('linkedin_url', sa.String(500), nullable=True),
        # Company Information
        sa.Column('company', sa.String(200), nullable=True),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('company_type', sa.String(100), nullable=True),
        # Specialty Information
        sa.Column('specialty', sa.String(200), nullable=True),
        sa.Column('industries', sa.Text(), nullable=True),  # JSON
        sa.Column('locations', sa.Text(), nullable=True),  # JSON
        sa.Column('roles_recruited', sa.Text(), nullable=True),  # JSON
        sa.Column('salary_range_min', sa.Integer(), nullable=True),
        sa.Column('salary_range_max', sa.Integer(), nullable=True),
        # Source
        sa.Column('source', sa.String(200), nullable=True),
        # Pipeline Status
        sa.Column('status', sa.String(50), default='new', index=True),
        sa.Column('priority_score', sa.Integer(), default=0),
        # Engagement Metrics
        sa.Column('messages_sent', sa.Integer(), default=0),
        sa.Column('messages_opened', sa.Integer(), default=0),
        sa.Column('responses_received', sa.Integer(), default=0),
        sa.Column('has_responded', sa.Boolean(), default=False),
        sa.Column('engagement_score', sa.Integer(), default=0),
        sa.Column('engagement_components', sa.Text(), nullable=True),  # JSON
        # Fit Score
        sa.Column('fit_score', sa.Integer(), default=0),
        sa.Column('fit_components', sa.Text(), nullable=True),  # JSON
        # AI Research Data
        sa.Column('research_data', sa.Text(), nullable=True),  # JSON
        sa.Column('research_summary', sa.Text(), nullable=True),
        sa.Column('recent_posts', sa.Text(), nullable=True),  # JSON
        sa.Column('mutual_connections', sa.Text(), nullable=True),  # JSON
        sa.Column('company_news', sa.Text(), nullable=True),  # JSON
        sa.Column('conversation_starters', sa.Text(), nullable=True),  # JSON
        sa.Column('personalization_hooks', sa.Text(), nullable=True),  # JSON
        sa.Column('researched_at', sa.DateTime(), nullable=True),
        # Contact History
        sa.Column('last_contact_date', sa.DateTime(), nullable=True),
        sa.Column('last_response_date', sa.DateTime(), nullable=True),
        sa.Column('next_action', sa.String(255), nullable=True),
        sa.Column('next_action_date', sa.DateTime(), nullable=True),
        sa.Column('follow_up_count', sa.Integer(), default=0),
        # Notes
        sa.Column('notes_text', sa.Text(), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),  # JSON
        # Timestamps
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Recruiter Notes table
    op.create_table(
        'recruiter_notes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('recruiter_id', sa.String(36), sa.ForeignKey('recruiters.id'), nullable=False, index=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('note_type', sa.String(50), default='general'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('recruiter_id', sa.String(36), sa.ForeignKey('recruiters.id'), nullable=True, index=True),
        # Message Content
        sa.Column('message_type', sa.String(50), default='initial_outreach'),
        sa.Column('subject', sa.String(255), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('signature', sa.Text(), nullable=True),
        # Generation Context
        sa.Column('generation_prompt', sa.Text(), nullable=True),
        sa.Column('generation_context', sa.Text(), nullable=True),  # JSON
        sa.Column('ai_model_used', sa.String(100), nullable=True),
        sa.Column('is_ai_generated', sa.Boolean(), default=False),
        # Quality Scores
        sa.Column('quality_score', sa.Integer(), nullable=True),
        sa.Column('quality_words_score', sa.Integer(), nullable=True),
        sa.Column('quality_personalization_score', sa.Integer(), nullable=True),
        sa.Column('quality_metrics_score', sa.Integer(), nullable=True),
        sa.Column('quality_cta_score', sa.Integer(), nullable=True),
        sa.Column('quality_tone_score', sa.Integer(), nullable=True),
        # Quality Analysis
        sa.Column('quality_feedback', sa.Text(), nullable=True),  # JSON
        sa.Column('quality_suggestions', sa.Text(), nullable=True),  # JSON
        # Message Stats
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('has_personalization', sa.Boolean(), default=False),
        sa.Column('has_metrics', sa.Boolean(), default=False),
        sa.Column('has_cta', sa.Boolean(), default=False),
        sa.Column('personalization_elements', sa.Text(), nullable=True),  # JSON
        # Status & Tracking
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('opened_at', sa.DateTime(), nullable=True),
        sa.Column('responded_at', sa.DateTime(), nullable=True),
        # Version Control
        sa.Column('version', sa.Integer(), default=1),
        sa.Column('parent_message_id', sa.String(36), sa.ForeignKey('messages.id'), nullable=True),
        # Timestamps
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Activities table
    op.create_table(
        'activities',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False, index=True),
        # Activity Details
        sa.Column('activity_type', sa.String(50), nullable=False, index=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('extra_data', sa.Text(), nullable=True),  # JSON
        # Related Entities
        sa.Column('recruiter_id', sa.String(36), sa.ForeignKey('recruiters.id'), nullable=True, index=True),
        sa.Column('resume_id', sa.String(36), sa.ForeignKey('resumes.id'), nullable=True),
        sa.Column('message_id', sa.String(36), sa.ForeignKey('messages.id'), nullable=True),
        # Pipeline Information
        sa.Column('pipeline_stage', sa.String(50), nullable=True, index=True),
        sa.Column('previous_stage', sa.String(50), nullable=True),
        # Priority
        sa.Column('priority_score', sa.Integer(), default=0),
        sa.Column('is_urgent', sa.Boolean(), default=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        # Status
        sa.Column('is_completed', sa.Boolean(), default=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        # Timestamps
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), index=True),
    )

    # Pipeline Items table
    op.create_table(
        'pipeline_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('recruiter_id', sa.String(36), sa.ForeignKey('recruiters.id'), nullable=False, index=True),
        # Stage & Position
        sa.Column('stage', sa.String(50), nullable=False, index=True),
        sa.Column('position', sa.Integer(), default=0),
        # Quick Stats
        sa.Column('last_activity_date', sa.DateTime(), nullable=True),
        sa.Column('next_action', sa.String(255), nullable=True),
        sa.Column('next_action_date', sa.DateTime(), nullable=True),
        # Priority Score Components
        sa.Column('priority_score', sa.Integer(), default=0),
        sa.Column('days_in_stage', sa.Integer(), default=0),
        # Timestamps
        sa.Column('entered_stage_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade():
    op.drop_table('pipeline_items')
    op.drop_table('activities')
    op.drop_table('messages')
    op.drop_table('recruiter_notes')
    op.drop_table('recruiters')
    op.drop_table('resume_versions')
    op.drop_table('resumes')
    op.drop_table('users')
