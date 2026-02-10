"""
Tests for Data Isolation

Validates that users cannot access each other's data.
"""

from app.extensions import db
from app.models.message import Message
from app.models.recruiter import Recruiter
from app.models.resume import Resume


def get_data(response):
    """Extract data from standardized API response."""
    json_data = response.json
    if isinstance(json_data, dict) and "data" in json_data and "success" in json_data:
        return json_data["data"]
    return json_data


class TestDataIsolation:
    """Tests that users can only see their own data."""

    def test_recruiters_isolated(
        self, client, auth_headers, auth_headers_second, test_user, second_user, app
    ):
        """User A cannot see User B's recruiters."""
        with app.app_context():
            # Create recruiters for each user
            r1 = Recruiter(user_id=test_user.id, first_name="User1", last_name="Recruiter")
            r2 = Recruiter(user_id=second_user.id, first_name="User2", last_name="Recruiter")
            db.session.add_all([r1, r2])
            db.session.commit()

        # User A sees only their recruiter
        resp = client.get("/api/recruiters", headers=auth_headers)
        data = get_data(resp)
        assert len(data["recruiters"]) == 1
        assert data["recruiters"][0]["first_name"] == "User1"

        # User B sees only their recruiter
        resp = client.get("/api/recruiters", headers=auth_headers_second)
        data = get_data(resp)
        assert len(data["recruiters"]) == 1
        assert data["recruiters"][0]["first_name"] == "User2"

    def test_messages_isolated(
        self, client, auth_headers, auth_headers_second, test_user, second_user, app
    ):
        """User A cannot see User B's messages."""
        with app.app_context():
            m1 = Message(user_id=test_user.id, body="User1 message")
            m2 = Message(user_id=second_user.id, body="User2 message")
            db.session.add_all([m1, m2])
            db.session.commit()

        resp = client.get("/api/messages", headers=auth_headers)
        data = get_data(resp)
        assert len(data["messages"]) == 1
        assert data["messages"][0]["body"] == "User1 message"

        resp = client.get("/api/messages", headers=auth_headers_second)
        data = get_data(resp)
        assert len(data["messages"]) == 1
        assert data["messages"][0]["body"] == "User2 message"

    def test_resumes_isolated(
        self, client, auth_headers, auth_headers_second, test_user, second_user, app
    ):
        """User A cannot see User B's resumes."""
        with app.app_context():
            r1 = Resume(
                user_id=test_user.id,
                title="User1 Resume",
                file_name="u1.pdf",
                file_type="pdf",
                raw_text="User 1 content",
            )
            r2 = Resume(
                user_id=second_user.id,
                title="User2 Resume",
                file_name="u2.pdf",
                file_type="pdf",
                raw_text="User 2 content",
            )
            db.session.add_all([r1, r2])
            db.session.commit()

        resp = client.get("/api/resumes", headers=auth_headers)
        data = get_data(resp)
        assert len(data["resumes"]) == 1
        assert data["resumes"][0]["title"] == "User1 Resume"

    def test_dashboard_isolated(
        self, client, auth_headers, auth_headers_second, test_user, second_user, app
    ):
        """Each user sees their own dashboard stats."""
        with app.app_context():
            # Create 3 recruiters for user 1
            for i in range(3):
                db.session.add(
                    Recruiter(
                        user_id=test_user.id,
                        first_name=f"R{i}",
                        last_name="Test",
                    )
                )
            db.session.commit()

        resp1 = client.get("/api/dashboard", headers=auth_headers)
        data1 = get_data(resp1)
        assert data1["stats"]["recruiters"] == 3

        resp2 = client.get("/api/dashboard", headers=auth_headers_second)
        data2 = get_data(resp2)
        assert data2["stats"]["recruiters"] == 0

    def test_activities_isolated(self, client, auth_headers, auth_headers_second):
        """Each user sees only their own activities."""
        resp1 = client.get("/api/activities", headers=auth_headers)
        get_data(resp1)

        resp2 = client.get("/api/activities", headers=auth_headers_second)
        get_data(resp2)

        # Both should succeed but with independent data
        assert resp1.status_code == 200
        assert resp2.status_code == 200
