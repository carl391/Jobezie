"""
Tests for Phase 2 Routes

Tests the Resume, Recruiter, Message, and Activity API endpoints.
"""

import pytest
import io
from datetime import datetime

from app.extensions import db
from app.models.user import User
from app.models.resume import Resume
from app.models.recruiter import Recruiter
from app.models.message import Message
from app.models.activity import Activity, PipelineItem, PipelineStage


class TestResumeRoutes:
    """Tests for Resume API endpoints."""

    def test_upload_resume(self, client, auth_headers):
        """Test uploading a resume."""
        data = {
            'file': (io.BytesIO(b'Sample resume content for testing'), 'resume.txt'),
            'title': 'My Test Resume',
            'is_master': 'true',
        }
        response = client.post(
            '/api/resumes',
            data=data,
            content_type='multipart/form-data',
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert 'resume' in response.json
        assert response.json['resume']['title'] == 'My Test Resume'
        assert 'ats_analysis' in response.json

    def test_upload_no_file(self, client, auth_headers):
        """Test upload with no file."""
        response = client.post(
            '/api/resumes',
            data={},
            content_type='multipart/form-data',
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_get_resumes(self, client, auth_headers, test_user, app):
        """Test getting all resumes."""
        # Create a resume first
        with app.app_context():
            resume = Resume(
                user_id=test_user.id,
                title='Test Resume',
                file_name='test.pdf',
                file_type='pdf',
                raw_text='Content',
            )
            db.session.add(resume)
            db.session.commit()

        response = client.get('/api/resumes', headers=auth_headers)

        assert response.status_code == 200
        assert 'resumes' in response.json
        assert len(response.json['resumes']) >= 1

    def test_get_master_resume(self, client, auth_headers, test_user, app):
        """Test getting master resume."""
        with app.app_context():
            resume = Resume(
                user_id=test_user.id,
                title='Master Resume',
                file_name='master.pdf',
                file_type='pdf',
                raw_text='Content',
                is_master=True,
            )
            db.session.add(resume)
            db.session.commit()

        response = client.get('/api/resumes/master', headers=auth_headers)

        assert response.status_code == 200
        assert response.json['resume']['title'] == 'Master Resume'

    def test_score_for_job(self, client, auth_headers, test_user, app):
        """Test scoring resume against job keywords."""
        with app.app_context():
            resume = Resume(
                user_id=test_user.id,
                title='Score Test',
                file_name='test.pdf',
                file_type='pdf',
                raw_text='Python developer with Django and AWS experience',
            )
            db.session.add(resume)
            db.session.commit()
            resume_id = str(resume.id)

        response = client.post(
            f'/api/resumes/{resume_id}/score',
            json={
                'job_keywords': ['python', 'django', 'aws', 'kubernetes'],
                'target_role': 'Software Engineer',
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert 'score' in response.json
        assert 'missing_keywords' in response.json


class TestRecruiterRoutes:
    """Tests for Recruiter API endpoints."""

    def test_create_recruiter(self, client, auth_headers):
        """Test creating a recruiter."""
        response = client.post(
            '/api/recruiters',
            json={
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane@techcorp.com',
                'company': 'TechCorp',
                'title': 'Senior Recruiter',
                'industries': ['technology', 'software'],
                'locations': ['San Francisco', 'Remote'],
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json['recruiter']['first_name'] == 'Jane'

    def test_create_recruiter_missing_fields(self, client, auth_headers):
        """Test creating recruiter with missing required fields."""
        response = client.post(
            '/api/recruiters',
            json={'email': 'test@test.com'},
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_get_recruiters(self, client, auth_headers, test_user, app):
        """Test getting all recruiters."""
        with app.app_context():
            recruiter = Recruiter(
                user_id=test_user.id,
                first_name='Test',
                last_name='Recruiter',
            )
            db.session.add(recruiter)
            db.session.commit()

        response = client.get('/api/recruiters', headers=auth_headers)

        assert response.status_code == 200
        assert 'recruiters' in response.json

    def test_get_recruiter_stats(self, client, auth_headers):
        """Test getting pipeline statistics."""
        response = client.get('/api/recruiters/stats', headers=auth_headers)

        assert response.status_code == 200
        assert 'total' in response.json
        assert 'by_stage' in response.json

    def test_update_recruiter_stage(self, client, auth_headers, test_user, app):
        """Test updating recruiter pipeline stage."""
        with app.app_context():
            recruiter = Recruiter(
                user_id=test_user.id,
                first_name='Test',
                last_name='Recruiter',
                status='new',
            )
            db.session.add(recruiter)
            db.session.commit()

            # Also create pipeline item
            item = PipelineItem(
                user_id=test_user.id,
                recruiter_id=recruiter.id,
                stage='new',
            )
            db.session.add(item)
            db.session.commit()
            recruiter_id = str(recruiter.id)

        response = client.put(
            f'/api/recruiters/{recruiter_id}/stage',
            json={'stage': 'contacted'},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json['recruiter']['status'] == 'contacted'

    def test_record_message_sent(self, client, auth_headers, test_user, app):
        """Test recording message sent to recruiter."""
        with app.app_context():
            recruiter = Recruiter(
                user_id=test_user.id,
                first_name='Test',
                last_name='Recruiter',
                messages_sent=0,
            )
            db.session.add(recruiter)
            db.session.commit()
            recruiter_id = str(recruiter.id)

        response = client.post(
            f'/api/recruiters/{recruiter_id}/message-sent',
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json['messages_sent'] == 1

    def test_add_note(self, client, auth_headers, test_user, app):
        """Test adding a note to recruiter."""
        with app.app_context():
            recruiter = Recruiter(
                user_id=test_user.id,
                first_name='Test',
                last_name='Recruiter',
            )
            db.session.add(recruiter)
            db.session.commit()
            recruiter_id = str(recruiter.id)

        response = client.post(
            f'/api/recruiters/{recruiter_id}/notes',
            json={
                'content': 'Great call today',
                'note_type': 'call',
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json['note']['content'] == 'Great call today'


class TestMessageRoutes:
    """Tests for Message API endpoints."""

    def test_create_message(self, client, auth_headers):
        """Test creating a message."""
        response = client.post(
            '/api/messages',
            json={
                'body': 'Hi Sarah, I noticed your work at TechCorp and would love to connect. Would you be open to a brief call?',
                'message_type': 'initial_outreach',
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert 'message' in response.json
        assert 'quality_analysis' in response.json

    def test_create_message_no_body(self, client, auth_headers):
        """Test creating message without body."""
        response = client.post(
            '/api/messages',
            json={'message_type': 'initial_outreach'},
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_get_messages(self, client, auth_headers, test_user, app):
        """Test getting all messages."""
        with app.app_context():
            message = Message(
                user_id=test_user.id,
                body='Test message',
            )
            db.session.add(message)
            db.session.commit()

        response = client.get('/api/messages', headers=auth_headers)

        assert response.status_code == 200
        assert 'messages' in response.json

    def test_get_message_stats(self, client, auth_headers):
        """Test getting message statistics."""
        response = client.get('/api/messages/stats', headers=auth_headers)

        assert response.status_code == 200
        assert 'total' in response.json
        assert 'by_status' in response.json

    def test_validate_message(self, client, auth_headers):
        """Test quick message validation."""
        response = client.post(
            '/api/messages/validate',
            json={
                'body': ' '.join(['word'] * 120),
                'message_type': 'initial_outreach',
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert 'is_optimal' in response.json
        assert 'word_count' in response.json

    def test_get_tips(self, client, auth_headers):
        """Test getting message tips."""
        response = client.get(
            '/api/messages/tips/initial_outreach',
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert 'structure' in response.json
        assert 'research_insights' in response.json

    def test_mark_sent(self, client, auth_headers, test_user, app):
        """Test marking message as sent."""
        with app.app_context():
            message = Message(
                user_id=test_user.id,
                body='Test message',
                status='draft',
            )
            db.session.add(message)
            db.session.commit()
            message_id = str(message.id)

        response = client.post(
            f'/api/messages/{message_id}/send',
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json['data']['status'] == 'sent'


class TestActivityRoutes:
    """Tests for Activity API endpoints."""

    def test_log_activity(self, client, auth_headers):
        """Test logging an activity."""
        response = client.post(
            '/api/activities',
            json={
                'activity_type': 'message_sent',
                'description': 'Sent outreach message',
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json['activity']['activity_type'] == 'message_sent'

    def test_log_activity_invalid_type(self, client, auth_headers):
        """Test logging activity with invalid type."""
        response = client.post(
            '/api/activities',
            json={
                'activity_type': 'invalid_type',
            },
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_get_activities(self, client, auth_headers, test_user, app):
        """Test getting activities."""
        with app.app_context():
            activity = Activity(
                user_id=test_user.id,
                activity_type='message_sent',
            )
            db.session.add(activity)
            db.session.commit()

        response = client.get('/api/activities', headers=auth_headers)

        assert response.status_code == 200
        assert 'activities' in response.json

    def test_get_recent_activities(self, client, auth_headers):
        """Test getting recent activities."""
        response = client.get('/api/activities/recent', headers=auth_headers)

        assert response.status_code == 200
        assert 'activities' in response.json

    def test_get_activity_counts(self, client, auth_headers):
        """Test getting activity counts."""
        response = client.get('/api/activities/counts', headers=auth_headers)

        assert response.status_code == 200
        assert 'by_type' in response.json

    def test_get_pipeline(self, client, auth_headers):
        """Test getting Kanban pipeline."""
        response = client.get('/api/activities/pipeline', headers=auth_headers)

        assert response.status_code == 200
        assert 'pipeline' in response.json
        assert 'stages' in response.json

    def test_get_pipeline_stats(self, client, auth_headers):
        """Test getting pipeline statistics."""
        response = client.get('/api/activities/pipeline/stats', headers=auth_headers)

        assert response.status_code == 200
        assert 'total' in response.json
        assert 'by_stage' in response.json

    def test_get_weekly_summary(self, client, auth_headers):
        """Test getting weekly summary."""
        response = client.get('/api/activities/weekly-summary', headers=auth_headers)

        assert response.status_code == 200
        assert 'total_activities' in response.json
        assert 'messages_sent' in response.json


class TestAIRoutes:
    """Tests for AI API endpoints."""

    def test_ai_status(self, client, auth_headers):
        """Test getting AI service status."""
        response = client.get('/api/ai/status', headers=auth_headers)

        assert response.status_code == 200
        assert 'available' in response.json
        assert 'features' in response.json

    def test_generate_message_no_recruiter(self, client, auth_headers):
        """Test message generation without recruiter ID."""
        response = client.post(
            '/api/ai/generate-message',
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_optimize_resume_not_found(self, client, auth_headers):
        """Test resume optimization with invalid ID."""
        response = client.post(
            '/api/ai/optimize-resume',
            json={'resume_id': '00000000-0000-0000-0000-000000000000'},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_career_coach_no_question(self, client, auth_headers):
        """Test career coach without question."""
        response = client.post(
            '/api/ai/career-coach',
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_interview_prep_no_title(self, client, auth_headers):
        """Test interview prep without job title."""
        response = client.post(
            '/api/ai/interview-prep',
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 400
