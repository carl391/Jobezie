"""
Tests for Phase 2 Models

Tests the Resume, Recruiter, Message, and Activity models.
"""

import pytest
from datetime import datetime, timedelta

from app.extensions import db
from app.models.user import User
from app.models.resume import Resume, ResumeVersion
from app.models.recruiter import Recruiter, RecruiterNote
from app.models.message import Message, MessageType, MessageStatus
from app.models.activity import Activity, ActivityType, PipelineItem, PipelineStage


class TestResumeModel:
    """Tests for Resume model."""

    def test_create_resume(self, app, test_user):
        """Test creating a resume."""
        with app.app_context():
            resume = Resume(
                user_id=test_user.id,
                title='My Resume',
                file_name='resume.pdf',
                file_type='pdf',
                file_size=1024,
                raw_text='Sample resume text',
                is_master=True,
            )
            db.session.add(resume)
            db.session.commit()

            assert resume.id is not None
            assert resume.file_name == 'resume.pdf'
            assert resume.is_master is True

    def test_resume_ats_scores(self, app, test_user):
        """Test ATS score fields on resume."""
        with app.app_context():
            resume = Resume(
                user_id=test_user.id,
                title='ATS Test Resume',
                file_name='resume.pdf',
                file_type='pdf',
                raw_text='Resume content',
                ats_total_score=75,
                ats_achievements_score=80,
                ats_keywords_score=70,
            )
            db.session.add(resume)
            db.session.commit()

            assert resume.ats_total_score == 75
            assert resume.ats_achievements_score == 80

    def test_resume_to_dict(self, app, test_user):
        """Test resume serialization."""
        with app.app_context():
            resume = Resume(
                user_id=test_user.id,
                title='Test Resume',
                file_name='test.pdf',
                file_type='pdf',
                raw_text='Content',
                ats_total_score=80,
            )
            db.session.add(resume)
            db.session.commit()

            data = resume.to_dict()
            assert 'id' in data
            assert data['file_name'] == 'test.pdf'
            assert data['ats_total_score'] == 80

    def test_resume_version(self, app, test_user):
        """Test creating resume versions."""
        with app.app_context():
            resume = Resume(
                user_id=test_user.id,
                title='Resume Version Test',
                file_name='resume.pdf',
                file_type='pdf',
                raw_text='Original content',
            )
            db.session.add(resume)
            db.session.commit()

            version = ResumeVersion(
                resume_id=resume.id,
                version_number=1,
                raw_text='Original content',
                ats_score=70,
            )
            db.session.add(version)
            db.session.commit()

            assert version.resume_id == resume.id
            assert version.version_number == 1


class TestRecruiterModel:
    """Tests for Recruiter model."""

    def test_create_recruiter(self, app, test_user):
        """Test creating a recruiter."""
        with app.app_context():
            recruiter = Recruiter(
                user_id=test_user.id,
                first_name='Jane',
                last_name='Smith',
                email='jane@techcorp.com',
                company='TechCorp',
                title='Senior Recruiter',
            )
            db.session.add(recruiter)
            db.session.commit()

            assert recruiter.id is not None
            assert recruiter.full_name == 'Jane Smith'

    def test_recruiter_industries(self, app, test_user):
        """Test recruiter with industry list."""
        with app.app_context():
            recruiter = Recruiter(
                user_id=test_user.id,
                first_name='John',
                last_name='Doe',
                industries=['technology', 'finance', 'healthcare'],
                locations=['San Francisco', 'New York'],
            )
            db.session.add(recruiter)
            db.session.commit()

            assert 'technology' in recruiter.industries
            assert len(recruiter.locations) == 2

    def test_recruiter_engagement_scores(self, app, test_user):
        """Test recruiter engagement score fields."""
        with app.app_context():
            recruiter = Recruiter(
                user_id=test_user.id,
                first_name='Test',
                last_name='Recruiter',
                engagement_score=75,
                fit_score=80,
                priority_score=85,
                messages_sent=10,
                messages_opened=6,
                responses_received=3,
            )
            db.session.add(recruiter)
            db.session.commit()

            assert recruiter.engagement_score == 75
            assert recruiter.fit_score == 80

    def test_recruiter_to_dict(self, app, test_user):
        """Test recruiter serialization."""
        with app.app_context():
            recruiter = Recruiter(
                user_id=test_user.id,
                first_name='Jane',
                last_name='Smith',
                company='TechCorp',
                engagement_score=70,
            )
            db.session.add(recruiter)
            db.session.commit()

            data = recruiter.to_dict()
            assert data['full_name'] == 'Jane Smith'
            assert data['company'] == 'TechCorp'

    def test_recruiter_note(self, app, test_user):
        """Test adding notes to recruiter."""
        with app.app_context():
            recruiter = Recruiter(
                user_id=test_user.id,
                first_name='Test',
                last_name='Recruiter',
            )
            db.session.add(recruiter)
            db.session.commit()

            note = RecruiterNote(
                recruiter_id=recruiter.id,
                content='Had a great call today',
                note_type='call',
            )
            db.session.add(note)
            db.session.commit()

            assert note.recruiter_id == recruiter.id
            assert note.note_type == 'call'


class TestMessageModel:
    """Tests for Message model."""

    def test_create_message(self, app, test_user):
        """Test creating a message."""
        with app.app_context():
            message = Message(
                user_id=test_user.id,
                body='Hi, I am interested in opportunities at your company.',
                message_type=MessageType.INITIAL_OUTREACH.value,
                status=MessageStatus.DRAFT.value,
            )
            db.session.add(message)
            db.session.commit()

            assert message.id is not None
            assert message.message_type == 'initial_outreach'

    def test_message_quality_scores(self, app, test_user):
        """Test message quality score fields."""
        with app.app_context():
            message = Message(
                user_id=test_user.id,
                body='Test message content',
                quality_score=85,
                quality_words_score=90,
                quality_personalization_score=80,
                quality_metrics_score=75,
                quality_cta_score=100,
                word_count=120,
            )
            db.session.add(message)
            db.session.commit()

            assert message.quality_score == 85
            assert message.is_within_word_limit is True

    def test_message_word_count(self, app, test_user):
        """Test word count calculation."""
        with app.app_context():
            message = Message(
                user_id=test_user.id,
                body='One two three four five',
            )
            db.session.add(message)
            db.session.commit()

            count = message.calculate_word_count()
            assert count == 5
            assert message.word_count == 5

    def test_message_quality_breakdown(self, app, test_user):
        """Test quality breakdown property."""
        with app.app_context():
            message = Message(
                user_id=test_user.id,
                body='Test',
                quality_score=80,
                quality_words_score=90,
                quality_personalization_score=80,
                quality_metrics_score=70,
                quality_cta_score=100,
                quality_tone_score=80,
            )
            db.session.add(message)
            db.session.commit()

            breakdown = message.quality_breakdown
            assert breakdown['total'] == 80
            assert 'components' in breakdown
            assert breakdown['components']['words']['weight'] == 25

    def test_message_statuses(self, app, test_user):
        """Test message status transitions."""
        with app.app_context():
            message = Message(
                user_id=test_user.id,
                body='Test',
                status=MessageStatus.DRAFT.value,
            )
            db.session.add(message)
            db.session.commit()

            assert message.status == 'draft'

            message.status = MessageStatus.SENT.value
            message.sent_at = datetime.utcnow()
            db.session.commit()

            assert message.status == 'sent'
            assert message.sent_at is not None


class TestActivityModel:
    """Tests for Activity model."""

    def test_create_activity(self, app, test_user):
        """Test creating an activity."""
        with app.app_context():
            activity = Activity(
                user_id=test_user.id,
                activity_type=ActivityType.MESSAGE_SENT.value,
                description='Sent outreach message',
            )
            db.session.add(activity)
            db.session.commit()

            assert activity.id is not None
            assert activity.activity_type == 'message_sent'

    def test_activity_with_recruiter(self, app, test_user):
        """Test activity linked to recruiter."""
        with app.app_context():
            recruiter = Recruiter(
                user_id=test_user.id,
                first_name='Test',
                last_name='Recruiter',
            )
            db.session.add(recruiter)
            db.session.commit()

            activity = Activity(
                user_id=test_user.id,
                activity_type=ActivityType.RECRUITER_ADDED.value,
                description='Added new recruiter',
                recruiter_id=recruiter.id,
            )
            db.session.add(activity)
            db.session.commit()

            assert activity.recruiter_id == recruiter.id

    def test_activity_pipeline_stage(self, app, test_user):
        """Test activity with pipeline stage change."""
        with app.app_context():
            activity = Activity(
                user_id=test_user.id,
                activity_type=ActivityType.STATUS_CHANGE.value,
                pipeline_stage=PipelineStage.RESPONDED.value,
                previous_stage=PipelineStage.CONTACTED.value,
            )
            db.session.add(activity)
            db.session.commit()

            assert activity.pipeline_stage == 'responded'
            assert activity.previous_stage == 'contacted'

    def test_activity_overdue(self, app, test_user):
        """Test activity overdue detection."""
        with app.app_context():
            # Not overdue (no due date)
            activity1 = Activity(
                user_id=test_user.id,
                activity_type=ActivityType.FOLLOW_UP_SENT.value,
            )

            # Overdue
            activity2 = Activity(
                user_id=test_user.id,
                activity_type=ActivityType.FOLLOW_UP_SENT.value,
                due_date=datetime.utcnow() - timedelta(days=1),
                is_completed=False,
            )

            # Not overdue (completed)
            activity3 = Activity(
                user_id=test_user.id,
                activity_type=ActivityType.FOLLOW_UP_SENT.value,
                due_date=datetime.utcnow() - timedelta(days=1),
                is_completed=True,
            )

            db.session.add_all([activity1, activity2, activity3])
            db.session.commit()

            assert activity1.is_overdue is False
            assert activity2.is_overdue is True
            assert activity3.is_overdue is False


class TestPipelineItemModel:
    """Tests for PipelineItem model."""

    def test_create_pipeline_item(self, app, test_user):
        """Test creating a pipeline item."""
        with app.app_context():
            recruiter = Recruiter(
                user_id=test_user.id,
                first_name='Test',
                last_name='Recruiter',
            )
            db.session.add(recruiter)
            db.session.commit()

            item = PipelineItem(
                user_id=test_user.id,
                recruiter_id=recruiter.id,
                stage=PipelineStage.NEW.value,
                position=0,
            )
            db.session.add(item)
            db.session.commit()

            assert item.id is not None
            assert item.stage == 'new'

    def test_pipeline_item_tracking(self, app, test_user):
        """Test pipeline item tracking fields."""
        with app.app_context():
            recruiter = Recruiter(
                user_id=test_user.id,
                first_name='Test',
                last_name='Recruiter',
            )
            db.session.add(recruiter)
            db.session.commit()

            item = PipelineItem(
                user_id=test_user.id,
                recruiter_id=recruiter.id,
                stage=PipelineStage.CONTACTED.value,
                priority_score=75,
                days_in_stage=5,
                next_action='Follow up',
                next_action_date=datetime.utcnow() + timedelta(days=2),
            )
            db.session.add(item)
            db.session.commit()

            assert item.priority_score == 75
            assert item.days_in_stage == 5
            assert item.next_action == 'Follow up'
