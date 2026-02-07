"""
Tests for Tier Gating

Validates that feature limits are correctly enforced across all tiers,
routes block users who have exceeded limits, and usage counters increment.
"""

from app.extensions import db
from app.models.user import User


def get_data(response):
    """Extract data from standardized API response."""
    json_data = response.json
    if isinstance(json_data, dict) and "data" in json_data and "success" in json_data:
        return json_data["data"]
    return json_data


class TestTierLimits:
    """Tests that tier_limits returns correct values for each tier."""

    def test_basic_tier_limits(self, app):
        """BASIC tier has restricted limits."""
        with app.app_context():
            user = User(email="t@t.com", subscription_tier="basic")
            user.set_password("TestPassword123")
            limits = user.tier_limits
            assert limits["recruiters"] == 5
            assert limits["tailored_resumes"] == 2
            assert limits["ai_messages"] == 10
            assert limits["research"] == 5
            assert limits["coach_daily"] == 10
            assert limits["interview_prep"] == 0
            assert limits["skills_gap"] == 1

    def test_pro_tier_limits(self, app):
        """PRO tier has higher limits."""
        with app.app_context():
            user = User(email="t@t.com", subscription_tier="pro")
            user.set_password("TestPassword123")
            limits = user.tier_limits
            assert limits["recruiters"] == 50
            assert limits["tailored_resumes"] == 10
            assert limits["ai_messages"] == 100
            assert limits["research"] == 25
            assert limits["coach_daily"] == 50
            assert limits["interview_prep"] == 3
            assert limits["skills_gap"] == 5

    def test_expert_tier_unlimited(self, app):
        """EXPERT tier has unlimited (-1) for all features."""
        with app.app_context():
            user = User(email="t@t.com", subscription_tier="expert")
            user.set_password("TestPassword123")
            limits = user.tier_limits
            for key in limits:
                assert limits[key] == -1, f"{key} should be unlimited"

    def test_career_keeper_tier_limits(self, app):
        """CAREER_KEEPER tier has reduced limits."""
        with app.app_context():
            user = User(email="t@t.com", subscription_tier="career_keeper")
            user.set_password("TestPassword123")
            limits = user.tier_limits
            assert limits["recruiters"] == 5
            assert limits["tailored_resumes"] == 1
            assert limits["ai_messages"] == 10
            assert limits["research"] == 2
            assert limits["interview_prep"] == 1
            assert limits["skills_gap"] == 1


class TestCanUseFeature:
    """Tests for the can_use_feature method."""

    def test_basic_can_use_recruiter_at_zero(self, app):
        """BASIC user with 0 recruiters can use feature."""
        with app.app_context():
            user = User(
                email="t@t.com",
                subscription_tier="basic",
                monthly_recruiter_count=0,
            )
            user.set_password("TestPassword123")
            assert user.can_use_feature("recruiters") is True

    def test_basic_blocked_at_limit(self, app):
        """BASIC user at limit is blocked."""
        with app.app_context():
            user = User(
                email="t@t.com",
                subscription_tier="basic",
                monthly_recruiter_count=5,
            )
            user.set_password("TestPassword123")
            assert user.can_use_feature("recruiters") is False

    def test_basic_blocked_over_limit(self, app):
        """BASIC user over limit is blocked."""
        with app.app_context():
            user = User(
                email="t@t.com",
                subscription_tier="basic",
                monthly_message_count=12,
            )
            user.set_password("TestPassword123")
            assert user.can_use_feature("ai_messages") is False

    def test_basic_interview_prep_always_blocked(self, app):
        """BASIC user always blocked from interview prep (limit=0)."""
        with app.app_context():
            user = User(
                email="t@t.com",
                subscription_tier="basic",
                monthly_interview_prep_count=0,
            )
            user.set_password("TestPassword123")
            assert user.can_use_feature("interview_prep") is False

    def test_pro_can_use_interview_prep(self, app):
        """PRO user with 0 usage can use interview prep."""
        with app.app_context():
            user = User(
                email="t@t.com",
                subscription_tier="pro",
                monthly_interview_prep_count=0,
            )
            user.set_password("TestPassword123")
            assert user.can_use_feature("interview_prep") is True

    def test_pro_blocked_at_interview_limit(self, app):
        """PRO user at interview prep limit is blocked."""
        with app.app_context():
            user = User(
                email="t@t.com",
                subscription_tier="pro",
                monthly_interview_prep_count=3,
            )
            user.set_password("TestPassword123")
            assert user.can_use_feature("interview_prep") is False

    def test_expert_never_blocked(self, app):
        """EXPERT user is never blocked, unlimited usage."""
        with app.app_context():
            user = User(
                email="t@t.com",
                subscription_tier="expert",
                monthly_recruiter_count=999,
                monthly_message_count=999,
                monthly_research_count=999,
                monthly_interview_prep_count=999,
            )
            user.set_password("TestPassword123")
            assert user.can_use_feature("recruiters") is True
            assert user.can_use_feature("ai_messages") is True
            assert user.can_use_feature("interview_prep") is True
            assert user.can_use_feature("research") is True

    def test_boundary_one_below_limit(self, app):
        """User one below limit can still use feature."""
        with app.app_context():
            user = User(
                email="t@t.com",
                subscription_tier="basic",
                monthly_recruiter_count=4,
            )
            user.set_password("TestPassword123")
            assert user.can_use_feature("recruiters") is True

    def test_boundary_exactly_at_limit(self, app):
        """User exactly at limit is blocked."""
        with app.app_context():
            user = User(
                email="t@t.com",
                subscription_tier="basic",
                monthly_recruiter_count=5,
            )
            user.set_password("TestPassword123")
            assert user.can_use_feature("recruiters") is False


class TestRouteEnforcement:
    """Tests that routes actually enforce tier limits via @feature_limit."""

    def test_create_recruiter_blocked_at_limit(self, client, auth_headers_at_limit):
        """Creating a recruiter is blocked when at limit."""
        response = client.post(
            "/api/recruiters",
            json={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@test.com",
                "company": "TestCorp",
            },
            headers=auth_headers_at_limit,
        )
        assert response.status_code == 429
        assert response.json["success"] is False
        assert "limit" in response.json.get("error", "")

    def test_create_message_blocked_at_limit(self, client, auth_headers_at_limit):
        """Creating a message is blocked when at limit."""
        response = client.post(
            "/api/messages",
            json={
                "body": "Hello, I'd love to connect.",
                "message_type": "initial_outreach",
            },
            headers=auth_headers_at_limit,
        )
        assert response.status_code == 429
        assert response.json["success"] is False

    def test_interview_prep_blocked_basic(self, client, auth_headers):
        """BASIC user blocked from interview prep (limit=0)."""
        response = client.post(
            "/api/ai/interview-prep",
            json={"job_title": "Software Engineer"},
            headers=auth_headers,
        )
        assert response.status_code == 429
        assert response.json["success"] is False

    def test_interview_prep_allowed_pro(self, client, auth_headers_pro):
        """PRO user can access interview prep."""
        response = client.post(
            "/api/ai/interview-prep",
            json={},  # Missing job_title, should get 400 not 429
            headers=auth_headers_pro,
        )
        # Should get 400 for missing job_title, not 429 for limit
        assert response.status_code == 400

    def test_expert_bypasses_all_limits(self, client, auth_headers_expert):
        """EXPERT user is never blocked by limits."""
        # Try to create a recruiter — should pass limit check
        response = client.post(
            "/api/recruiters",
            json={
                "first_name": "Test",
                "last_name": "Recruiter",
                "email": "r@test.com",
                "company": "TestCorp",
            },
            headers=auth_headers_expert,
        )
        assert response.status_code == 201


class TestCounterIncrement:
    """Tests that usage counters increment after successful operations."""

    def test_recruiter_counter_increments(self, client, auth_headers, test_user, app):
        """Creating a recruiter increments monthly_recruiter_count."""
        response = client.post(
            "/api/recruiters",
            json={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@test.com",
                "company": "TestCorp",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201

        with app.app_context():
            user = User.query.get(test_user.id)
            assert user.monthly_recruiter_count == 1

    def test_message_counter_increments(self, client, auth_headers, test_user, app):
        """Creating a message increments monthly_message_count."""
        response = client.post(
            "/api/messages",
            json={
                "body": "Hi, I noticed your work and would love to connect.",
                "message_type": "initial_outreach",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201

        with app.app_context():
            user = User.query.get(test_user.id)
            assert user.monthly_message_count == 1

    def test_multiple_creates_increment_counter(self, client, auth_headers, test_user, app):
        """Multiple creates correctly increment the counter."""
        for i in range(3):
            client.post(
                "/api/recruiters",
                json={
                    "first_name": f"Recruiter{i}",
                    "last_name": "Test",
                    "email": f"r{i}@test.com",
                },
                headers=auth_headers,
            )

        with app.app_context():
            user = User.query.get(test_user.id)
            assert user.monthly_recruiter_count == 3


class TestUsageReset:
    """Tests for monthly usage reset."""

    def test_reset_clears_all_counters(self, app):
        """reset_monthly_usage zeros all counters."""
        with app.app_context():
            user = User(
                email="t@t.com",
                subscription_tier="basic",
                monthly_recruiter_count=5,
                monthly_message_count=10,
                monthly_research_count=5,
                monthly_tailoring_count=2,
                daily_coach_count=10,
                monthly_interview_prep_count=3,
            )
            user.set_password("TestPassword123")
            user.reset_monthly_usage()

            assert user.monthly_recruiter_count == 0
            assert user.monthly_message_count == 0
            assert user.monthly_research_count == 0
            assert user.monthly_tailoring_count == 0
            assert user.daily_coach_count == 0
            assert user.monthly_interview_prep_count == 0
            assert user.usage_reset_date is not None
