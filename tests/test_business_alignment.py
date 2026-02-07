"""
Tests for Business Plan Alignment

Validates that the platform's implementation matches the business plan:
- 4 subscription tiers with correct pricing/limits
- 7 ATS scoring components
- 5 message quality components
- 8 pipeline stages
- All planned features exist and are accessible
"""

from app.extensions import db
from app.models.activity import PipelineStage
from app.models.user import SubscriptionTier, User


class TestSubscriptionTiers:
    """Verify all 4 tiers exist with correct limits."""

    def test_four_tiers_exist(self, app):
        """Platform has exactly 4 subscription tiers."""
        with app.app_context():
            tiers = [t.value for t in SubscriptionTier]
            assert set(tiers) == {"basic", "pro", "expert", "career_keeper"}

    def test_basic_is_free_tier(self, app):
        """BASIC tier is the default (free) tier."""
        with app.app_context():
            user = User(email="t@t.com")
            user.set_password("TestPassword123")
            db.session.add(user)
            db.session.commit()
            assert user.subscription_tier == "basic"

    def test_tier_progression(self, app):
        """PRO has higher limits than BASIC, EXPERT is unlimited."""
        with app.app_context():
            basic = User(email="b@t.com", subscription_tier="basic")
            basic.set_password("Test1234")
            pro = User(email="p@t.com", subscription_tier="pro")
            pro.set_password("Test1234")
            expert = User(email="e@t.com", subscription_tier="expert")
            expert.set_password("Test1234")

            # PRO > BASIC for all features
            for key in basic.tier_limits:
                assert pro.tier_limits[key] > basic.tier_limits[key], (
                    f"PRO {key} ({pro.tier_limits[key]}) should be > "
                    f"BASIC {key} ({basic.tier_limits[key]})"
                )

            # EXPERT unlimited
            for key in expert.tier_limits:
                assert expert.tier_limits[key] == -1, f"EXPERT {key} should be unlimited"


class TestPipelineStages:
    """Verify all 8 pipeline stages exist."""

    def test_eight_stages_exist(self, app):
        """Pipeline has exactly 8 stages."""
        with app.app_context():
            stages = [s.value for s in PipelineStage]
            expected = [
                "new", "researching", "contacted", "responded",
                "interviewing", "offer", "accepted", "declined",
            ]
            assert set(stages) == set(expected)
            assert len(stages) == 8


class TestATSScoring:
    """Verify ATS scoring has all 7 components."""

    def test_ats_seven_components(self, app):
        """ATS scoring has 7 components."""
        from app.services.scoring.ats import calculate_ats_score

        with app.app_context():
            result = calculate_ats_score(
                "Experienced Python developer with 5 years of Django, AWS, and CI/CD."
            )

            assert "total_score" in result
            assert "components" in result
            expected_components = [
                "compatibility", "keywords", "achievements",
                "formatting", "progression", "completeness", "fit",
            ]
            for comp in expected_components:
                assert comp in result["components"], (
                    f"Missing ATS component: {comp}"
                )


class TestMessageQualityScoring:
    """Verify message quality has 5 components."""

    def test_message_five_components(self, app):
        """Message quality scoring has 5 components."""
        from app.services.scoring.message import calculate_message_quality

        with app.app_context():
            result = calculate_message_quality(
                "Hi Sarah, I noticed your work at TechCorp on cloud infrastructure. "
                "As a Senior DevOps Engineer with 5 years of AWS experience, I'd love "
                "to connect and explore how my background could contribute to your team. "
                "Would you be open to a 15-minute call this week?"
            )

            assert "total_score" in result
            assert "components" in result
            # 5 components: words, personalization, metrics, cta, tone
            expected_components = [
                "words", "personalization", "metrics", "cta", "tone",
            ]
            for comp in expected_components:
                assert comp in result["components"], (
                    f"Missing message quality component: {comp}"
                )


class TestAllFeaturesAccessible:
    """Verify all planned features have working endpoints."""

    def test_auth_endpoints_exist(self, client):
        """All auth endpoints respond (not 404)."""
        endpoints = [
            ("POST", "/api/auth/register"),
            ("POST", "/api/auth/login"),
            ("POST", "/api/auth/forgot-password"),
            ("POST", "/api/auth/reset-password"),
            ("POST", "/api/auth/verify-email"),
        ]
        for method, path in endpoints:
            if method == "POST":
                resp = client.post(path, json={})
            else:
                resp = client.get(path)
            assert resp.status_code != 404, f"{method} {path} returned 404"

    def test_protected_endpoints_require_auth(self, client):
        """All protected endpoints return 401 without auth."""
        endpoints = [
            "/api/dashboard",
            "/api/resumes",
            "/api/recruiters",
            "/api/messages",
            "/api/activities",
            "/api/ai/status",
            "/api/linkedin/tips",
            "/api/labor-market/overview",
            "/api/subscription/status",
        ]
        for path in endpoints:
            resp = client.get(path)
            assert resp.status_code in [401, 422], (
                f"GET {path} should require auth, got {resp.status_code}"
            )

    def test_all_core_pages_accessible(self, client, auth_headers):
        """All core API endpoints respond when authenticated."""
        endpoints = [
            "/api/dashboard",
            "/api/resumes",
            "/api/recruiters",
            "/api/messages",
            "/api/activities",
            "/api/ai/status",
            "/api/linkedin/tips",
            "/api/labor-market/overview",
            "/api/labor-market/industries/trending",
            "/api/labor-market/roles/high-demand",
            "/api/subscription/status",
            "/api/dashboard/readiness",
            "/api/dashboard/stats/weekly",
        ]
        for path in endpoints:
            resp = client.get(path, headers=auth_headers)
            assert resp.status_code == 200, (
                f"GET {path} returned {resp.status_code}, expected 200"
            )
