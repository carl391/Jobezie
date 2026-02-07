"""
Tests for Subscription Routes

Validates tier information, status, checkout, and management endpoints.
Note: Actual Stripe interactions are not tested (no Stripe key in testing).
"""


def get_data(response):
    """Extract data from standardized API response."""
    json_data = response.json
    if isinstance(json_data, dict) and "data" in json_data and "success" in json_data:
        return json_data["data"]
    return json_data


class TestTierInfo:
    """Tests for tier information endpoint."""

    def test_get_tiers(self, client):
        """Get subscription tiers (public endpoint, no auth)."""
        response = client.get("/api/subscription/tiers")
        assert response.status_code == 200
        data = get_data(response)
        assert isinstance(data, (list, dict))

    def test_tiers_include_all_plans(self, client):
        """Tiers include BASIC, PRO, EXPERT, CAREER_KEEPER."""
        response = client.get("/api/subscription/tiers")
        data = get_data(response)
        if isinstance(data, list):
            tier_names = [t.get("name", "").lower() for t in data]
            for expected in ["basic", "pro", "expert", "career_keeper"]:
                assert expected in tier_names, f"Missing tier: {expected}"


class TestSubscriptionStatus:
    """Tests for subscription status endpoint."""

    def test_get_status_basic(self, client, auth_headers):
        """Get subscription status for BASIC user."""
        response = client.get("/api/subscription/status", headers=auth_headers)
        assert response.status_code == 200
        data = get_data(response)
        assert data["tier"] == "basic"

    def test_get_status_pro(self, client, auth_headers_pro):
        """Get subscription status for PRO user."""
        response = client.get("/api/subscription/status", headers=auth_headers_pro)
        assert response.status_code == 200
        data = get_data(response)
        assert data["tier"] == "pro"

    def test_get_status_expert(self, client, auth_headers_expert):
        """Get subscription status for EXPERT user."""
        response = client.get("/api/subscription/status", headers=auth_headers_expert)
        assert response.status_code == 200
        data = get_data(response)
        assert data["tier"] == "expert"

    def test_status_requires_auth(self, client):
        """Status without auth returns 401."""
        response = client.get("/api/subscription/status")
        assert response.status_code == 401


class TestCheckout:
    """Tests for checkout session creation."""

    def test_checkout_missing_tier(self, client, auth_headers):
        """Checkout without tier returns 400."""
        response = client.post(
            "/api/subscription/checkout",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_checkout_with_tier(self, client, auth_headers):
        """Checkout with tier (may fail without Stripe key, but should not 500)."""
        response = client.post(
            "/api/subscription/checkout",
            json={"tier": "pro"},
            headers=auth_headers,
        )
        # 200 if Stripe configured, 400 if not (graceful error)
        assert response.status_code in [200, 400]


class TestPortal:
    """Tests for customer portal creation."""

    def test_portal_no_stripe_customer(self, client, auth_headers):
        """Portal for user without Stripe customer returns 400."""
        response = client.post(
            "/api/subscription/portal",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 400


class TestCancellation:
    """Tests for subscription cancellation."""

    def test_cancel_no_subscription(self, client, auth_headers):
        """Cancel without active subscription returns 400."""
        response = client.post(
            "/api/subscription/cancel",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_reactivate_no_subscription(self, client, auth_headers):
        """Reactivate without cancelled subscription returns 400."""
        response = client.post(
            "/api/subscription/reactivate",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 400
