"""
Input Validation Utilities

Provides validation functions for user input with security hardening
against XSS, SQL injection, and other common attacks.
"""

import html
import re
from typing import Optional


class ValidationError(Exception):
    """Raised when validation fails."""

    pass


# Dangerous patterns for security validation
DANGEROUS_PATTERNS = [
    # XSS patterns
    r"<script[^>]*>",
    r"javascript:",
    r"on\w+\s*=",
    r"<iframe[^>]*>",
    r"<object[^>]*>",
    r"<embed[^>]*>",
    # SQL injection patterns
    r"'\s*;\s*drop\s+table",
    r"'\s*;\s*delete\s+from",
    r"'\s*or\s+'1'\s*=\s*'1",
    r"'\s*or\s+1\s*=\s*1",
    r"union\s+select",
    r"insert\s+into",
    # Command injection patterns
    r"\bexec\s*\(",
    r"\beval\s*\(",
    r"__import__",
    r"\bos\.",
    r"\bsubprocess\.",
]

# Email validation pattern (RFC 5322 simplified)
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Name validation pattern
NAME_PATTERN = re.compile(r"^[\w\s\'-]+$", re.UNICODE)


def validate_email(email: str) -> str:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        Normalized email (lowercase, stripped)

    Raises:
        ValidationError: If email is invalid
    """
    if not email:
        raise ValidationError("Email is required")

    email = email.strip().lower()

    if len(email) > 255:
        raise ValidationError("Email must be less than 255 characters")

    if not EMAIL_PATTERN.match(email):
        raise ValidationError("Invalid email format")

    # Check for dangerous patterns
    if contains_dangerous_patterns(email):
        raise ValidationError("Email contains invalid characters")

    return email


def validate_password(password: str, min_length: int = 8) -> str:
    """
    Validate password strength.

    Requirements:
    - Minimum 8 characters (configurable)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit

    Args:
        password: Password to validate
        min_length: Minimum password length (default 8)

    Returns:
        Password (unchanged)

    Raises:
        ValidationError: If password doesn't meet requirements
    """
    if not password:
        raise ValidationError("Password is required")

    if len(password) < min_length:
        raise ValidationError(f"Password must be at least {min_length} characters")

    if len(password) > 128:
        raise ValidationError("Password must be less than 128 characters")

    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one digit")

    return password


def validate_name(name: str, field_name: str = "Name", max_length: int = 100) -> str:
    """
    Validate a name field.

    Args:
        name: Name to validate
        field_name: Field name for error messages
        max_length: Maximum allowed length

    Returns:
        Sanitized name

    Raises:
        ValidationError: If name is invalid
    """
    if not name:
        raise ValidationError(f"{field_name} is required")

    name = name.strip()

    if len(name) > max_length:
        raise ValidationError(f"{field_name} must be less than {max_length} characters")

    # Validate pattern BEFORE sanitization (apostrophes, hyphens are valid in names)
    if not NAME_PATTERN.match(name):
        raise ValidationError(f"{field_name} contains invalid characters")

    # Sanitize after validation for safe storage/display
    return sanitize_string(name)


def validate_url(url: str, field_name: str = "URL") -> str:
    """
    Validate URL format.

    Args:
        url: URL to validate
        field_name: Field name for error messages

    Returns:
        Sanitized URL

    Raises:
        ValidationError: If URL is invalid
    """
    if not url:
        raise ValidationError(f"{field_name} is required")

    url = url.strip()

    if len(url) > 2000:
        raise ValidationError(f"{field_name} must be less than 2000 characters")

    # Basic URL pattern
    url_pattern = re.compile(
        r"^https?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if not url_pattern.match(url):
        raise ValidationError(f"Invalid {field_name} format")

    # Check for javascript: URLs
    if "javascript:" in url.lower():
        raise ValidationError(f"{field_name} contains invalid protocol")

    return url


def validate_string(
    value: str,
    field_name: str = "Field",
    min_length: int = 0,
    max_length: int = 2000,
    required: bool = True,
) -> Optional[str]:
    """
    Validate and sanitize a string field.

    Args:
        value: String to validate
        field_name: Field name for error messages
        min_length: Minimum length (default 0)
        max_length: Maximum length (default 2000)
        required: Whether field is required

    Returns:
        Sanitized string or None if not required and empty

    Raises:
        ValidationError: If string is invalid
    """
    if not value or not value.strip():
        if required:
            raise ValidationError(f"{field_name} is required")
        return None

    value = sanitize_string(value.strip())

    if len(value) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters")

    if len(value) > max_length:
        raise ValidationError(f"{field_name} must be less than {max_length} characters")

    if contains_dangerous_patterns(value):
        raise ValidationError(f"{field_name} contains invalid content")

    return value


def sanitize_string(value: str) -> str:
    """
    Sanitize a string by escaping HTML entities.

    Args:
        value: String to sanitize

    Returns:
        Sanitized string
    """
    if not value:
        return value

    # Escape HTML entities
    value = html.escape(value, quote=True)

    # Remove null bytes
    value = value.replace("\x00", "")

    # Normalize unicode (NFKC normalization)
    import unicodedata

    value = unicodedata.normalize("NFKC", value)

    return value


def contains_dangerous_patterns(value: str) -> bool:
    """
    Check if a string contains dangerous patterns.

    Args:
        value: String to check

    Returns:
        True if dangerous patterns found
    """
    if not value:
        return False

    value_lower = value.lower()

    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, value_lower, re.IGNORECASE):
            return True

    return False


def validate_list(
    items: list, field_name: str = "Items", max_items: int = 100, validate_item=None
) -> list:
    """
    Validate a list of items.

    Args:
        items: List to validate
        field_name: Field name for error messages
        max_items: Maximum number of items allowed
        validate_item: Optional function to validate each item

    Returns:
        Validated list

    Raises:
        ValidationError: If list is invalid
    """
    if not isinstance(items, list):
        raise ValidationError(f"{field_name} must be a list")

    if len(items) > max_items:
        raise ValidationError(f"{field_name} cannot have more than {max_items} items")

    if validate_item:
        return [validate_item(item) for item in items]

    # Default: sanitize strings
    return [sanitize_string(str(item)) if item else None for item in items]


def validate_integer(
    value, field_name: str = "Value", min_value: int = None, max_value: int = None
) -> int:
    """
    Validate and convert to integer.

    Args:
        value: Value to validate
        field_name: Field name for error messages
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Validated integer

    Raises:
        ValidationError: If value is invalid
    """
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a valid integer")

    if min_value is not None and value < min_value:
        raise ValidationError(f"{field_name} must be at least {min_value}")

    if max_value is not None and value > max_value:
        raise ValidationError(f"{field_name} must be at most {max_value}")

    return value
