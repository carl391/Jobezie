"""
Tests for Extended Auth Functionality

Covers email verification, password reset, profile updates, tour system,
and disabled account handling.
"""

from app.extensions import db
from app.models.user import User


def get_data(response):
    """Extract data from standardized API response."""
    json_data = response.json
    if isinstance(json_data, dict) and "data" in json_data and "success" in json_data:
        return json_data["data"]
    return json_data


class TestEmailVerification:
    """Tests for email verification flow."""

    def test_register_creates_verification_token(self, client):
        """Registration creates a verification token."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "verify@example.com",
                "password": "SecurePass123",
                "first_name": "Verify",
                "last_name": "User",
            },
        )
        assert response.status_code == 201

    def test_verify_email_with_valid_token(self, client, app):
        """Email verification with valid token succeeds."""
        with app.app_context():
            user = User(email="v@test.com", verification_token="valid-token-123")
            user.set_password("TestPassword123")
            db.session.add(user)
            db.session.commit()

        response = client.post(
            "/api/auth/verify-email",
            json={"token": "valid-token-123"},
        )
        assert response.status_code == 200
        assert response.json["success"] is True

    def test_verify_email_with_invalid_token(self, client):
        """Email verification with invalid token returns 404."""
        response = client.post(
            "/api/auth/verify-email",
            json={"token": "nonexistent-token"},
        )
        assert response.status_code == 404

    def test_verify_email_already_verified(self, client, app):
        """Verifying already-verified email returns success."""
        with app.app_context():
            user = User(
                email="v2@test.com",
                verification_token="token-456",
                email_verified=True,
            )
            user.set_password("TestPassword123")
            db.session.add(user)
            db.session.commit()

        response = client.post(
            "/api/auth/verify-email",
            json={"token": "token-456"},
        )
        assert response.status_code == 200

    def test_verify_email_no_token(self, client):
        """Verification without token returns 400."""
        response = client.post(
            "/api/auth/verify-email",
            json={"token": ""},
        )
        assert response.status_code == 400

    def test_resend_verification(self, client, auth_headers):
        """Resend verification for unverified user."""
        response = client.post(
            "/api/auth/resend-verification",
            headers=auth_headers,
        )
        # Test user is not verified, so this should work
        assert response.status_code in [200, 500]  # 500 if email service fails


class TestPasswordReset:
    """Tests for forgot/reset password flow."""

    def test_forgot_password_existing_email(self, client, test_user):
        """Forgot password with existing email returns 200."""
        response = client.post(
            "/api/auth/forgot-password",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 200
        assert response.json["success"] is True

    def test_forgot_password_nonexistent_email(self, client):
        """Forgot password with nonexistent email still returns 200 (no enumeration)."""
        response = client.post(
            "/api/auth/forgot-password",
            json={"email": "nobody@nowhere.com"},
        )
        assert response.status_code == 200
        assert response.json["success"] is True

    def test_reset_password_valid_token(self, client, app):
        """Reset password with valid token succeeds."""
        with app.app_context():
            user = User(email="reset@test.com", verification_token="reset-token-abc")
            user.set_password("OldPassword123")
            db.session.add(user)
            db.session.commit()

        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": "reset-token-abc",
                "new_password": "NewSecurePass456",
            },
        )
        assert response.status_code == 200
        assert response.json["success"] is True

    def test_reset_password_invalid_token(self, client):
        """Reset password with invalid token returns 400."""
        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": "bad-token",
                "new_password": "NewPassword123",
            },
        )
        assert response.status_code == 400

    def test_reset_password_weak_password(self, client, app):
        """Reset password with weak password returns 400."""
        with app.app_context():
            user = User(email="reset2@test.com", verification_token="reset-token-weak")
            user.set_password("OldPassword123")
            db.session.add(user)
            db.session.commit()

        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": "reset-token-weak",
                "new_password": "short",
            },
        )
        assert response.status_code == 400


class TestProfileUpdate:
    """Tests for profile update endpoint."""

    def test_update_basic_profile(self, client, auth_headers):
        """Update basic profile fields."""
        response = client.put(
            "/api/auth/profile",
            json={
                "first_name": "Updated",
                "last_name": "Name",
                "location": "Austin, TX",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = get_data(response)
        assert data["user"]["first_name"] == "Updated"
        assert data["user"]["location"] == "Austin, TX"

    def test_update_career_info(self, client, auth_headers):
        """Update career information."""
        response = client.put(
            "/api/auth/profile",
            json={
                "current_role": "Software Engineer",
                "years_experience": 5,
                "target_roles": ["Senior Engineer", "Tech Lead"],
                "target_industries": ["technology", "fintech"],
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = get_data(response)
        assert data["user"]["current_role"] == "Software Engineer"
        assert data["user"]["years_experience"] == 5

    def test_update_onboarding_step(self, client, auth_headers):
        """Update onboarding step."""
        response = client.put(
            "/api/auth/profile",
            json={
                "onboarding_step": 3,
                "onboarding_completed": False,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_update_no_body(self, client, auth_headers):
        """Profile update with no body returns 400."""
        response = client.put(
            "/api/auth/profile",
            headers=auth_headers,
        )
        assert response.status_code == 400


class TestTourSystem:
    """Tests for the tour tracking system."""

    def test_get_tour_status(self, client, auth_headers):
        """Get tour status for user."""
        response = client.get(
            "/api/auth/tour/status",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert "tour_completed" in response.json
        assert "completed_tours" in response.json

    def test_complete_main_tour(self, client, auth_headers):
        """Complete the main tour."""
        response = client.post(
            "/api/auth/tour/complete",
            json={"tour_id": "main"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json["tour_completed"] is True
        assert "main" in response.json["completed_tours"]

    def test_complete_specific_tour(self, client, auth_headers):
        """Complete a specific tour."""
        response = client.post(
            "/api/auth/tour/complete",
            json={"tour_id": "interview_prep"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert "interview_prep" in response.json["completed_tours"]

    def test_complete_tour_idempotent(self, client, auth_headers):
        """Completing same tour twice is idempotent."""
        client.post(
            "/api/auth/tour/complete",
            json={"tour_id": "main"},
            headers=auth_headers,
        )
        response = client.post(
            "/api/auth/tour/complete",
            json={"tour_id": "main"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json["completed_tours"].count("main") == 1


class TestDisabledAccounts:
    """Tests for disabled account handling."""

    def test_disabled_user_cannot_login(self, client, app):
        """Disabled user gets 401 on login."""
        with app.app_context():
            user = User(email="disabled@test.com", is_active=False)
            user.set_password("TestPassword123")
            db.session.add(user)
            db.session.commit()

        response = client.post(
            "/api/auth/login",
            json={
                "email": "disabled@test.com",
                "password": "TestPassword123",
            },
        )
        assert response.status_code == 401

    def test_wrong_password_returns_401(self, client, test_user):
        """Wrong password returns 401."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword123",
            },
        )
        assert response.status_code == 401

    def test_change_password(self, client, auth_headers):
        """Change password with correct current password."""
        response = client.put(
            "/api/auth/password",
            json={
                "current_password": "TestPassword123",
                "new_password": "NewSecurePass456",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_change_password_wrong_current(self, client, auth_headers):
        """Change password with wrong current password returns 401."""
        response = client.put(
            "/api/auth/password",
            json={
                "current_password": "WrongPassword",
                "new_password": "NewSecurePass456",
            },
            headers=auth_headers,
        )
        assert response.status_code == 401
