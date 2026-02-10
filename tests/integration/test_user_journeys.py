"""
Integration Tests — User Journeys

End-to-end flows testing complete user workflows.
"""

import io

from app.extensions import db
from app.models.recruiter import Recruiter
from app.models.user import User


def get_data(response):
    """Extract data from standardized API response."""
    json_data = response.json
    if isinstance(json_data, dict) and "data" in json_data and "success" in json_data:
        return json_data["data"]
    return json_data


class TestActivationFlow:
    """Tests the full new-user activation flow."""

    def test_register_onboard_upload_resume(self, client, app):
        """New user: register → update profile → upload resume → get dashboard."""
        # Step 1: Register
        resp = client.post(
            "/api/auth/register",
            json={
                "email": "newjobseeker@example.com",
                "password": "SecurePass123",
                "first_name": "Alice",
                "last_name": "Johnson",
            },
        )
        assert resp.status_code == 201
        token = get_data(resp)["access_token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Step 2: Update profile (onboarding)
        resp = client.put(
            "/api/auth/profile",
            json={
                "current_role": "Junior Developer",
                "years_experience": 2,
                "target_roles": ["Software Engineer"],
                "target_industries": ["technology"],
                "technical_skills": ["Python", "JavaScript", "React"],
                "onboarding_step": 3,
            },
            headers=headers,
        )
        assert resp.status_code == 200

        # Step 3: Upload resume
        data = {
            "file": (
                io.BytesIO(
                    b"Alice Johnson, Junior Developer, 2 years experience, Python, JavaScript"
                ),
                "resume.txt",
            ),
            "title": "My Resume",
        }
        resp = client.post(
            "/api/resumes",
            data=data,
            content_type="multipart/form-data",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201

        # Step 4: Get dashboard
        resp = client.get("/api/dashboard", headers=headers)
        assert resp.status_code == 200
        dashboard = get_data(resp)
        assert dashboard["stats"]["resumes"] == 1
        assert dashboard["user"]["full_name"] == "Alice Johnson"


class TestRecruiterPipeline:
    """Tests the full recruiter pipeline progression."""

    def test_add_recruiter_and_progress(self, client, auth_headers, test_user, app):
        """Add recruiter → update stage → send message → log activity."""
        # Step 1: Add recruiter
        resp = client.post(
            "/api/recruiters",
            json={
                "first_name": "Sarah",
                "last_name": "Tech",
                "email": "sarah@techcorp.com",
                "company": "TechCorp",
                "title": "Senior Recruiter",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        recruiter_id = get_data(resp)["recruiter"]["id"]

        # Step 2: Move to contacted stage
        resp = client.put(
            f"/api/recruiters/{recruiter_id}/stage",
            json={"stage": "contacted"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert get_data(resp)["recruiter"]["status"] == "contacted"

        # Step 3: Record message sent
        resp = client.post(
            f"/api/recruiters/{recruiter_id}/message-sent",
            json={},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert get_data(resp)["messages_sent"] >= 1

        # Step 4: Add a note
        resp = client.post(
            f"/api/recruiters/{recruiter_id}/notes",
            json={"content": "Great initial call", "note_type": "call"},
            headers=auth_headers,
        )
        assert resp.status_code == 201

        # Step 5: Verify pipeline stats
        resp = client.get("/api/recruiters/stats", headers=auth_headers)
        assert resp.status_code == 200
        stats = get_data(resp)
        assert stats["total"] >= 1

    def test_full_pipeline_progression(self, client, auth_headers, test_user, app):
        """Recruiter moves through multiple stages."""
        from app.models.activity import PipelineItem

        with app.app_context():
            recruiter = Recruiter(
                user_id=test_user.id,
                first_name="Pipeline",
                last_name="Test",
                status="new",
            )
            db.session.add(recruiter)
            db.session.commit()
            item = PipelineItem(
                user_id=test_user.id,
                recruiter_id=recruiter.id,
                stage="new",
            )
            db.session.add(item)
            db.session.commit()
            rid = str(recruiter.id)

        stages = ["researching", "contacted", "responded", "interviewing", "offer"]
        for stage in stages:
            resp = client.put(
                f"/api/recruiters/{rid}/stage",
                json={"stage": stage},
                headers=auth_headers,
            )
            assert resp.status_code == 200
            assert get_data(resp)["recruiter"]["status"] == stage


class TestMessageFlow:
    """Tests the complete message creation and management flow."""

    def test_create_validate_send_message(self, client, auth_headers, app):
        """Create message → validate → mark sent."""
        # Step 1: Create message
        resp = client.post(
            "/api/messages",
            json={
                "body": "Hi Sarah, I noticed your work at TechCorp and would love to connect. Would you be open to a brief call?",
                "message_type": "initial_outreach",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        msg_data = get_data(resp)
        message_id = msg_data["message"]["id"]

        # Step 2: Validate message
        resp = client.post(
            "/api/messages/validate",
            json={
                "body": "Hi Sarah, I noticed your work at TechCorp and would love to connect.",
                "message_type": "initial_outreach",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        val_data = get_data(resp)
        assert "word_count" in val_data

        # Step 3: Mark as sent
        resp = client.post(
            f"/api/messages/{message_id}/send",
            headers=auth_headers,
        )
        assert resp.status_code == 200

        # Step 4: Verify stats
        resp = client.get("/api/messages/stats", headers=auth_headers)
        assert resp.status_code == 200
        stats = get_data(resp)
        assert stats["total"] >= 1


class TestTierUpgradeFlow:
    """Tests that upgrading tier unlocks more features."""

    def test_basic_blocked_then_pro_allowed(self, client, app):
        """BASIC user blocked from interview prep; after upgrade to PRO, allowed."""
        with app.app_context():
            user = User(
                email="upgrade@test.com",
                first_name="Upgrade",
                last_name="Test",
                subscription_tier="basic",
            )
            user.set_password("TestPassword123")
            db.session.add(user)
            db.session.commit()
            user_id = str(user.id)

        from flask_jwt_extended import create_access_token

        with app.app_context():
            token = create_access_token(identity=user_id)

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # Blocked as BASIC
        resp = client.post(
            "/api/ai/interview-prep",
            json={"job_title": "Software Engineer"},
            headers=headers,
        )
        assert resp.status_code == 429

        # Upgrade to PRO
        with app.app_context():
            user = User.query.get(user_id)
            user.subscription_tier = "pro"
            db.session.commit()

        # Now allowed (gets 400 for missing data, not 429)
        resp = client.post(
            "/api/ai/interview-prep",
            json={},
            headers=headers,
        )
        assert resp.status_code == 400  # Missing job_title, not 429


class TestDashboardReflectsActivity:
    """Tests that dashboard reflects user activity."""

    def test_dashboard_updates_after_actions(self, client, auth_headers, test_user, app):
        """Dashboard stats update after creating recruiters and messages."""
        # Check initial state
        resp = client.get("/api/dashboard", headers=auth_headers)
        initial = get_data(resp)
        assert initial["stats"]["recruiters"] == 0
        assert initial["stats"]["messages"] == 0

        # Add a recruiter
        client.post(
            "/api/recruiters",
            json={"first_name": "Test", "last_name": "R", "company": "Corp"},
            headers=auth_headers,
        )

        # Add a message
        client.post(
            "/api/messages",
            json={"body": "Hello there, let's connect.", "message_type": "initial_outreach"},
            headers=auth_headers,
        )

        # Check updated state
        resp = client.get("/api/dashboard", headers=auth_headers)
        updated = get_data(resp)
        assert updated["stats"]["recruiters"] == 1
        assert updated["stats"]["messages"] == 1
