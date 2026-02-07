"""
Tests for Dashboard Routes

Validates dashboard stats, career readiness, and weekly stats endpoints.
"""

from app.extensions import db
from app.models.recruiter import Recruiter
from app.models.resume import Resume


def get_data(response):
    """Extract data from standardized API response."""
    json_data = response.json
    if isinstance(json_data, dict) and "data" in json_data and "success" in json_data:
        return json_data["data"]
    return json_data


class TestDashboard:
    """Tests for the main dashboard endpoint."""

    def test_get_dashboard(self, client, auth_headers):
        """Get dashboard returns all expected sections."""
        response = client.get("/api/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = get_data(response)
        assert "user" in data
        assert "stats" in data
        assert "career_readiness" in data
        assert "pipeline_summary" in data
        assert "recent_activities" in data
        assert "usage" in data

    def test_dashboard_stats_structure(self, client, auth_headers):
        """Dashboard stats contain all expected fields."""
        response = client.get("/api/dashboard", headers=auth_headers)
        data = get_data(response)
        stats = data["stats"]
        assert "resumes" in stats
        assert "recruiters" in stats
        assert "active_recruiters" in stats
        assert "messages" in stats
        assert "messages_this_week" in stats
        assert "response_rate" in stats

    def test_dashboard_usage_shows_limits(self, client, auth_headers):
        """Dashboard usage section shows used + limit for each category."""
        response = client.get("/api/dashboard", headers=auth_headers)
        data = get_data(response)
        usage = data["usage"]
        for category in ["recruiters", "messages", "research", "tailored_resumes"]:
            assert "used" in usage[category]
            assert "limit" in usage[category]

    def test_dashboard_with_data(self, client, auth_headers, test_user, app):
        """Dashboard reflects actual data counts."""
        with app.app_context():
            # Add some recruiters
            for i in range(3):
                db.session.add(
                    Recruiter(
                        user_id=test_user.id,
                        first_name=f"R{i}",
                        last_name="Test",
                    )
                )
            # Add a resume
            db.session.add(
                Resume(
                    user_id=test_user.id,
                    title="Test",
                    file_name="t.pdf",
                    file_type="pdf",
                    raw_text="Content",
                )
            )
            db.session.commit()

        response = client.get("/api/dashboard", headers=auth_headers)
        data = get_data(response)
        assert data["stats"]["recruiters"] == 3
        assert data["stats"]["resumes"] == 1

    def test_dashboard_pipeline_has_all_stages(self, client, auth_headers):
        """Pipeline summary includes all 8 stages."""
        response = client.get("/api/dashboard", headers=auth_headers)
        data = get_data(response)
        pipeline = data["pipeline_summary"]
        expected_stages = [
            "new", "researching", "contacted", "responded",
            "interviewing", "offer", "accepted", "declined",
        ]
        for stage in expected_stages:
            assert stage in pipeline, f"Missing pipeline stage: {stage}"


class TestCareerReadiness:
    """Tests for career readiness endpoint."""

    def test_get_readiness(self, client, auth_headers):
        """Get career readiness returns score and breakdown."""
        response = client.get("/api/dashboard/readiness", headers=auth_headers)
        assert response.status_code == 200
        data = get_data(response)
        assert "total_score" in data
        assert "context" in data
        assert "benchmarks" in data

    def test_readiness_benchmarks(self, client, auth_headers):
        """Readiness includes helpful benchmarks."""
        response = client.get("/api/dashboard/readiness", headers=auth_headers)
        data = get_data(response)
        benchmarks = data["benchmarks"]
        assert benchmarks["optimal_recruiters"] == 10
        assert benchmarks["weekly_message_target"] == 5
        assert benchmarks["good_response_rate"] == 20
        assert benchmarks["good_ats_score"] == 70


class TestWeeklyStats:
    """Tests for weekly stats endpoint."""

    def test_get_weekly_stats(self, client, auth_headers):
        """Get weekly stats returns 7 days of data."""
        response = client.get("/api/dashboard/stats/weekly", headers=auth_headers)
        assert response.status_code == 200
        data = get_data(response)
        assert "daily" in data
        assert "totals" in data
        assert len(data["daily"]) == 7

    def test_weekly_stats_daily_structure(self, client, auth_headers):
        """Each daily entry has expected fields."""
        response = client.get("/api/dashboard/stats/weekly", headers=auth_headers)
        data = get_data(response)
        day = data["daily"][0]
        assert "date" in day
        assert "day_name" in day
        assert "messages_sent" in day
        assert "recruiters_added" in day
        assert "activities" in day

    def test_weekly_stats_totals(self, client, auth_headers):
        """Totals contain expected fields."""
        response = client.get("/api/dashboard/stats/weekly", headers=auth_headers)
        data = get_data(response)
        totals = data["totals"]
        assert "messages_sent" in totals
        assert "responses_received" in totals
        assert "recruiters_added" in totals
        assert "activities" in totals
