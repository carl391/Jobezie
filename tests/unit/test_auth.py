"""
Authentication Unit Tests

Tests for user registration, login, token management, and password operations.
"""

import json


class TestRegistration:
    """Tests for user registration endpoint."""

    def test_register_success(self, client, sample_user_data):
        """Test successful user registration."""
        response = client.post(
            "/api/auth/register", json=sample_user_data, content_type="application/json"
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["user"]["email"] == sample_user_data["email"].lower()

    def test_register_duplicate_email(self, client, test_user, sample_user_data):
        """Test registration with existing email fails."""
        sample_user_data["email"] = test_user.email

        response = client.post(
            "/api/auth/register", json=sample_user_data, content_type="application/json"
        )

        assert response.status_code == 409
        data = json.loads(response.data)
        assert data["error"] == "email_exists"

    def test_register_invalid_email(self, client, sample_user_data):
        """Test registration with invalid email fails."""
        sample_user_data["email"] = "invalid-email"

        response = client.post(
            "/api/auth/register", json=sample_user_data, content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == "validation_error"

    def test_register_weak_password(self, client, sample_user_data):
        """Test registration with weak password fails."""
        sample_user_data["password"] = "123"

        response = client.post(
            "/api/auth/register", json=sample_user_data, content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["error"] == "validation_error"

    def test_register_password_no_uppercase(self, client, sample_user_data):
        """Test registration fails when password has no uppercase."""
        sample_user_data["password"] = "password123"

        response = client.post(
            "/api/auth/register", json=sample_user_data, content_type="application/json"
        )

        assert response.status_code == 400

    def test_register_password_no_digit(self, client, sample_user_data):
        """Test registration fails when password has no digit."""
        sample_user_data["password"] = "PasswordNoDigit"

        response = client.post(
            "/api/auth/register", json=sample_user_data, content_type="application/json"
        )

        assert response.status_code == 400

    def test_register_missing_email(self, client, sample_user_data):
        """Test registration with missing email fails."""
        del sample_user_data["email"]

        response = client.post(
            "/api/auth/register", json=sample_user_data, content_type="application/json"
        )

        assert response.status_code == 400

    def test_register_missing_password(self, client, sample_user_data):
        """Test registration with missing password fails."""
        del sample_user_data["password"]

        response = client.post(
            "/api/auth/register", json=sample_user_data, content_type="application/json"
        )

        assert response.status_code == 400

    def test_register_empty_body(self, client):
        """Test registration with empty body fails."""
        response = client.post("/api/auth/register", json={}, content_type="application/json")

        assert response.status_code == 400


class TestLogin:
    """Tests for user login endpoint."""

    def test_login_success(self, client, test_user, sample_login_data):
        """Test successful login."""
        response = client.post(
            "/api/auth/login", json=sample_login_data, content_type="application/json"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

    def test_login_wrong_password(self, client, test_user, sample_login_data):
        """Test login with wrong password fails."""
        sample_login_data["password"] = "WrongPassword123"

        response = client.post(
            "/api/auth/login", json=sample_login_data, content_type="application/json"
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data["error"] == "invalid_credentials"

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user fails."""
        response = client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "Password123"},
            content_type="application/json",
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data["error"] == "invalid_credentials"

    def test_login_missing_email(self, client):
        """Test login with missing email fails."""
        response = client.post(
            "/api/auth/login",
            json={"password": "Password123"},
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_login_missing_password(self, client, test_user):
        """Test login with missing password fails."""
        response = client.post(
            "/api/auth/login",
            json={"email": test_user.email},
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_login_case_insensitive_email(self, client, test_user, sample_login_data):
        """Test login email is case insensitive."""
        sample_login_data["email"] = sample_login_data["email"].upper()

        response = client.post(
            "/api/auth/login", json=sample_login_data, content_type="application/json"
        )

        assert response.status_code == 200


class TestTokenRefresh:
    """Tests for token refresh endpoint."""

    def test_refresh_success(self, client, test_user, sample_login_data):
        """Test successful token refresh."""
        # First login to get refresh token
        login_response = client.post(
            "/api/auth/login", json=sample_login_data, content_type="application/json"
        )
        refresh_token = json.loads(login_response.data)["data"]["refresh_token"]

        # Use refresh token to get new access token
        response = client.post(
            "/api/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "access_token" in data["data"]

    def test_refresh_with_access_token_fails(self, client, auth_headers):
        """Test that access token cannot be used for refresh."""
        response = client.post("/api/auth/refresh", headers=auth_headers)

        # Should fail because we used access token instead of refresh token
        assert response.status_code == 422 or response.status_code == 401

    def test_refresh_missing_token(self, client):
        """Test refresh without token fails."""
        response = client.post("/api/auth/refresh")

        assert response.status_code == 401


class TestLogout:
    """Tests for logout endpoint."""

    def test_logout_success(self, client, auth_headers):
        """Test successful logout."""
        response = client.post("/api/auth/logout", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_logout_without_token(self, client):
        """Test logout without token fails."""
        response = client.post("/api/auth/logout")

        assert response.status_code == 401


class TestGetCurrentUser:
    """Tests for get current user endpoint."""

    def test_get_me_success(self, client, test_user, auth_headers):
        """Test successful get current user."""
        response = client.get("/api/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["data"]["user"]["email"] == test_user.email

    def test_get_me_without_token(self, client):
        """Test get current user without token fails."""
        response = client.get("/api/auth/me")

        assert response.status_code == 401


class TestChangePassword:
    """Tests for change password endpoint."""

    def test_change_password_success(self, client, test_user, auth_headers):
        """Test successful password change."""
        response = client.put(
            "/api/auth/password",
            headers=auth_headers,
            json={
                "current_password": "TestPassword123",
                "new_password": "NewPassword456",
            },
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

        # Verify new password works
        login_response = client.post(
            "/api/auth/login",
            json={"email": test_user.email, "password": "NewPassword456"},
            content_type="application/json",
        )
        assert login_response.status_code == 200

    def test_change_password_wrong_current(self, client, auth_headers):
        """Test password change with wrong current password fails."""
        response = client.put(
            "/api/auth/password",
            headers=auth_headers,
            json={
                "current_password": "WrongPassword123",
                "new_password": "NewPassword456",
            },
        )

        assert response.status_code == 401

    def test_change_password_weak_new_password(self, client, auth_headers):
        """Test password change with weak new password fails."""
        response = client.put(
            "/api/auth/password",
            headers=auth_headers,
            json={"current_password": "TestPassword123", "new_password": "123"},
        )

        assert response.status_code == 400


class TestForgotPassword:
    """Tests for forgot password endpoint."""

    def test_forgot_password_existing_user(self, client, test_user):
        """Test forgot password for existing user."""
        response = client.post(
            "/api/auth/forgot-password",
            json={"email": test_user.email},
            content_type="application/json",
        )

        # Should always return 200 to prevent email enumeration
        assert response.status_code == 200

    def test_forgot_password_nonexistent_user(self, client):
        """Test forgot password for nonexistent user (returns 200 for security)."""
        response = client.post(
            "/api/auth/forgot-password",
            json={"email": "nonexistent@example.com"},
            content_type="application/json",
        )

        # Should still return 200 to prevent email enumeration
        assert response.status_code == 200


class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert data["service"] == "jobezie-api"
