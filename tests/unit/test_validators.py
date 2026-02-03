"""
Validator Unit Tests

Tests for input validation and sanitization functions.
"""

import pytest

from app.utils.validators import (
    ValidationError,
    contains_dangerous_patterns,
    sanitize_string,
    validate_email,
    validate_name,
    validate_password,
    validate_string,
    validate_url,
)


class TestEmailValidation:
    """Tests for email validation."""

    def test_valid_email(self):
        """Test valid email addresses."""
        assert validate_email("user@example.com") == "user@example.com"
        assert validate_email("User@Example.COM") == "user@example.com"
        assert validate_email("user.name@example.co.uk") == "user.name@example.co.uk"
        assert validate_email("user+tag@example.com") == "user+tag@example.com"

    def test_invalid_email_format(self):
        """Test invalid email formats."""
        with pytest.raises(ValidationError):
            validate_email("invalid")

        with pytest.raises(ValidationError):
            validate_email("invalid@")

        with pytest.raises(ValidationError):
            validate_email("@example.com")

        with pytest.raises(ValidationError):
            validate_email("user@.com")

    def test_empty_email(self):
        """Test empty email."""
        with pytest.raises(ValidationError):
            validate_email("")

        with pytest.raises(ValidationError):
            validate_email("   ")

    def test_email_too_long(self):
        """Test email exceeding max length."""
        long_email = "a" * 250 + "@example.com"
        with pytest.raises(ValidationError):
            validate_email(long_email)


class TestPasswordValidation:
    """Tests for password validation."""

    def test_valid_password(self):
        """Test valid passwords."""
        assert validate_password("Password123") == "Password123"
        assert validate_password("SecureP@ss1") == "SecureP@ss1"
        assert validate_password("MyP@ssw0rd!") == "MyP@ssw0rd!"

    def test_password_too_short(self):
        """Test password shorter than minimum."""
        with pytest.raises(ValidationError, match="at least 8 characters"):
            validate_password("Pass1")

    def test_password_no_uppercase(self):
        """Test password without uppercase."""
        with pytest.raises(ValidationError, match="uppercase"):
            validate_password("password123")

    def test_password_no_lowercase(self):
        """Test password without lowercase."""
        with pytest.raises(ValidationError, match="lowercase"):
            validate_password("PASSWORD123")

    def test_password_no_digit(self):
        """Test password without digit."""
        with pytest.raises(ValidationError, match="digit"):
            validate_password("PasswordNoDigit")

    def test_empty_password(self):
        """Test empty password."""
        with pytest.raises(ValidationError):
            validate_password("")

    def test_password_too_long(self):
        """Test password exceeding max length."""
        long_password = "A" * 100 + "a1" + "x" * 30
        with pytest.raises(ValidationError, match="less than 128"):
            validate_password(long_password)


class TestNameValidation:
    """Tests for name validation."""

    def test_valid_names(self):
        """Test valid names."""
        assert validate_name("John") == "John"
        assert validate_name("Mary Jane") == "Mary Jane"
        # Apostrophes are allowed in names (e.g., O'Connor)
        result = validate_name("O'Connor")
        assert "O" in result and "Connor" in result
        assert validate_name("Jean-Pierre") == "Jean-Pierre"

    def test_empty_name(self):
        """Test empty name."""
        with pytest.raises(ValidationError):
            validate_name("")

    def test_name_too_long(self):
        """Test name exceeding max length."""
        long_name = "A" * 101
        with pytest.raises(ValidationError):
            validate_name(long_name)


class TestStringValidation:
    """Tests for generic string validation."""

    def test_valid_string(self):
        """Test valid strings."""
        assert validate_string("Hello World") == "Hello World"
        assert validate_string("Test", min_length=1, max_length=10) == "Test"

    def test_string_too_short(self):
        """Test string shorter than minimum."""
        with pytest.raises(ValidationError):
            validate_string("Hi", min_length=5)

    def test_string_too_long(self):
        """Test string exceeding max length."""
        with pytest.raises(ValidationError):
            validate_string("Hello World", max_length=5)

    def test_optional_empty_string(self):
        """Test optional string can be empty."""
        result = validate_string("", required=False)
        assert result is None

    def test_required_empty_string(self):
        """Test required string cannot be empty."""
        with pytest.raises(ValidationError):
            validate_string("", required=True)


class TestUrlValidation:
    """Tests for URL validation."""

    def test_valid_urls(self):
        """Test valid URLs."""
        assert validate_url("https://example.com") == "https://example.com"
        assert validate_url("http://example.com/path") == "http://example.com/path"
        assert (
            validate_url("https://sub.example.com/path?query=1")
            == "https://sub.example.com/path?query=1"
        )

    def test_invalid_urls(self):
        """Test invalid URLs."""
        with pytest.raises(ValidationError):
            validate_url("not-a-url")

        with pytest.raises(ValidationError):
            validate_url("ftp://example.com")

    def test_javascript_url(self):
        """Test javascript: URLs are blocked."""
        with pytest.raises(ValidationError):
            validate_url("javascript:alert(1)")


class TestSanitization:
    """Tests for string sanitization."""

    def test_html_escape(self):
        """Test HTML entities are escaped."""
        result = sanitize_string('<script>alert("xss")</script>')
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_null_byte_removal(self):
        """Test null bytes are removed."""
        result = sanitize_string("hello\x00world")
        assert "\x00" not in result
        assert "helloworld" == result

    def test_empty_string(self):
        """Test empty string returns empty."""
        assert sanitize_string("") == ""
        assert sanitize_string(None) is None


class TestDangerousPatterns:
    """Tests for dangerous pattern detection."""

    def test_script_tags(self):
        """Test script tags are detected."""
        assert contains_dangerous_patterns("<script>alert(1)</script>") is True
        assert contains_dangerous_patterns("<SCRIPT>alert(1)</SCRIPT>") is True

    def test_javascript_protocol(self):
        """Test javascript: protocol is detected."""
        assert contains_dangerous_patterns("javascript:alert(1)") is True

    def test_event_handlers(self):
        """Test event handlers are detected."""
        assert contains_dangerous_patterns("onclick=alert(1)") is True
        assert contains_dangerous_patterns("onerror=alert(1)") is True

    def test_sql_injection(self):
        """Test SQL injection patterns are detected."""
        assert contains_dangerous_patterns("'; DROP TABLE users;--") is True
        assert contains_dangerous_patterns("' OR '1'='1") is True
        assert contains_dangerous_patterns("UNION SELECT * FROM users") is True

    def test_safe_strings(self):
        """Test safe strings are not flagged."""
        assert contains_dangerous_patterns("Hello World") is False
        assert contains_dangerous_patterns("user@example.com") is False
        assert contains_dangerous_patterns("Normal text with some numbers 123") is False
