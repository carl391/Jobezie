"""
Authentication Routes

Handles user registration, login, token refresh, logout, and password management.
"""

import secrets
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from app.extensions import db, token_blocklist
from app.models.user import User
from app.services.email_service import EmailService
from app.utils.validators import ValidationError, validate_email, validate_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user.

    Request Body:
        email: User's email address (required)
        password: User's password (required, min 8 chars)
        first_name: User's first name (optional)
        last_name: User's last name (optional)

    Returns:
        201: User created successfully with tokens
        400: Validation error
        409: Email already exists
    """
    data = request.get_json()

    if not data:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "invalid_request",
                    "message": "Request body is required",
                }
            ),
            400,
        )

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    first_name = data.get("first_name", "").strip() or None
    last_name = data.get("last_name", "").strip() or None

    # Validate email
    try:
        validate_email(email)
    except ValidationError as e:
        return (
            jsonify({"success": False, "error": "validation_error", "message": str(e)}),
            400,
        )

    # Validate password
    try:
        validate_password(password)
    except ValidationError as e:
        return (
            jsonify({"success": False, "error": "validation_error", "message": str(e)}),
            400,
        )

    # Validate birth year (age gate)
    birth_year = data.get("birth_year")
    if birth_year is not None:
        try:
            birth_year = int(birth_year)
        except (TypeError, ValueError):
            return (
                jsonify(
                    {"success": False, "error": "validation_error", "message": "Invalid birth year"}
                ),
                400,
            )
        current_year = datetime.now().year
        if birth_year < 1900 or birth_year > current_year:
            return (
                jsonify(
                    {"success": False, "error": "validation_error", "message": "Invalid birth year"}
                ),
                400,
            )
        if current_year - birth_year < 13:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "age_requirement",
                        "message": "You must be at least 13 years old to use Jobezie.",
                        "code": "AGE_REQUIREMENT_NOT_MET",
                    }
                ),
                403,
            )

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return (
            jsonify(
                {
                    "success": False,
                    "error": "email_exists",
                    "message": "An account with this email already exists",
                }
            ),
            409,
        )

    # Create user with verification token
    user = User(email=email, first_name=first_name, last_name=last_name)
    user.set_password(password)
    user.verification_token = secrets.token_urlsafe(32)

    if birth_year is not None:
        user.birth_year = birth_year

    db.session.add(user)
    db.session.commit()

    # Send welcome email
    try:
        EmailService.send_welcome_email(user)
    except Exception as e:
        # Log error but don't fail registration
        print(f"Failed to send welcome email: {e}")

    # Send verification email
    try:
        EmailService.send_verification_email(user, user.verification_token)
    except Exception as e:
        # Log error but don't fail registration
        print(f"Failed to send verification email: {e}")

    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return (
        jsonify(
            {
                "success": True,
                "message": "User registered successfully",
                "data": {
                    "user": user.to_dict(),
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
            }
        ),
        201,
    )


@auth_bp.route("/verify-email", methods=["POST"])
def verify_email():
    """
    Verify user's email address using verification token.

    Request Body:
        token: Email verification token (required)

    Returns:
        200: Email verified successfully
        400: Invalid or missing token
        404: Token not found or already used
    """
    data = request.get_json()

    if not data:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "invalid_request",
                    "message": "Request body is required",
                }
            ),
            400,
        )

    token = data.get("token", "").strip()

    if not token:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "validation_error",
                    "message": "Verification token is required",
                }
            ),
            400,
        )

    # Find user by verification token
    user = User.query.filter_by(verification_token=token).first()

    if not user:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "invalid_token",
                    "message": "Invalid or expired verification token",
                }
            ),
            404,
        )

    if user.email_verified:
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Email already verified",
                }
            ),
            200,
        )

    # Verify the email
    user.email_verified = True
    user.verification_token = None  # Clear the token after use
    db.session.commit()

    return (
        jsonify(
            {
                "success": True,
                "message": "Email verified successfully",
            }
        ),
        200,
    )


@auth_bp.route("/resend-verification", methods=["POST"])
@jwt_required()
def resend_verification():
    """
    Resend email verification to current user.

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        200: Verification email sent
        400: Email already verified
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "user_not_found",
                    "message": "User not found",
                }
            ),
            404,
        )

    if user.email_verified:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "already_verified",
                    "message": "Email is already verified",
                }
            ),
            400,
        )

    # Generate new verification token
    user.verification_token = secrets.token_urlsafe(32)
    db.session.commit()

    # Send verification email
    try:
        EmailService.send_verification_email(user, user.verification_token)
    except Exception:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "email_error",
                    "message": "Failed to send verification email",
                }
            ),
            500,
        )

    return (
        jsonify(
            {
                "success": True,
                "message": "Verification email sent",
            }
        ),
        200,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and return tokens.

    Request Body:
        email: User's email address (required)
        password: User's password (required)

    Returns:
        200: Login successful with tokens
        400: Validation error
        401: Invalid credentials
    """
    data = request.get_json()

    if not data:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "invalid_request",
                    "message": "Request body is required",
                }
            ),
            400,
        )

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "validation_error",
                    "message": "Email and password are required",
                }
            ),
            400,
        )

    # Find user
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "invalid_credentials",
                    "message": "Invalid email or password",
                }
            ),
            401,
        )

    if not user.is_active:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "account_disabled",
                    "message": "This account has been disabled",
                }
            ),
            401,
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.session.commit()

    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return (
        jsonify(
            {
                "success": True,
                "message": "Login successful",
                "data": {
                    "user": user.to_dict(include_private=True),
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
            }
        ),
        200,
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token.

    Headers:
        Authorization: Bearer <refresh_token>

    Returns:
        200: New access token
        401: Invalid or expired refresh token
    """
    current_user_id = get_jwt_identity()

    # Verify user still exists and is active
    user = User.query.get(current_user_id)
    if not user or not user.is_active:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "invalid_user",
                    "message": "User not found or account disabled",
                }
            ),
            401,
        )

    access_token = create_access_token(identity=current_user_id)

    return jsonify({"success": True, "data": {"access_token": access_token}}), 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Logout user by revoking current token.

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        200: Logout successful
    """
    jti = get_jwt()["jti"]
    token_blocklist.add(jti)

    return jsonify({"success": True, "message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user's profile.

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        200: User profile data
        401: Not authenticated
        404: User not found
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "user_not_found",
                    "message": "User not found",
                }
            ),
            404,
        )

    return (
        jsonify({"success": True, "data": {"user": user.to_dict(include_private=True)}}),
        200,
    )


@auth_bp.route("/password", methods=["PUT"])
@jwt_required()
def change_password():
    """
    Change current user's password.

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        current_password: Current password (required)
        new_password: New password (required, min 8 chars)

    Returns:
        200: Password changed successfully
        400: Validation error
        401: Current password incorrect
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "user_not_found",
                    "message": "User not found",
                }
            ),
            404,
        )

    data = request.get_json()

    if not data:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "invalid_request",
                    "message": "Request body is required",
                }
            ),
            400,
        )

    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")

    # Verify current password
    if not user.check_password(current_password):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "invalid_password",
                    "message": "Current password is incorrect",
                }
            ),
            401,
        )

    # Validate new password
    try:
        validate_password(new_password)
    except ValidationError as e:
        return (
            jsonify({"success": False, "error": "validation_error", "message": str(e)}),
            400,
        )

    # Update password
    user.set_password(new_password)
    db.session.commit()

    return jsonify({"success": True, "message": "Password changed successfully"}), 200


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """
    Request password reset email.

    Request Body:
        email: User's email address (required)

    Returns:
        200: Reset email sent (always returns success to prevent email enumeration)
    """
    data = request.get_json()

    if not data:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "invalid_request",
                    "message": "Request body is required",
                }
            ),
            400,
        )

    email = data.get("email", "").strip().lower()

    # Always return success to prevent email enumeration
    # In production, this would send an email if user exists
    user = User.query.filter_by(email=email).first()

    if user:
        # Generate reset token and send email via SendGrid
        import uuid

        reset_token = str(uuid.uuid4())
        user.verification_token = reset_token
        db.session.commit()

        # Send password reset email
        from app.services.email_service import EmailService

        EmailService.send_password_reset_email(user, reset_token)

    return (
        jsonify(
            {
                "success": True,
                "message": "If an account exists with this email, a password reset link has been sent",
            }
        ),
        200,
    )


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """
    Reset password using token from email.

    Request Body:
        token: Reset token from email (required)
        new_password: New password (required, min 8 chars)

    Returns:
        200: Password reset successful
        400: Invalid or expired token
    """
    data = request.get_json()

    if not data:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "invalid_request",
                    "message": "Request body is required",
                }
            ),
            400,
        )

    token = data.get("token", "")
    new_password = data.get("new_password", "")

    if not token:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "validation_error",
                    "message": "Reset token is required",
                }
            ),
            400,
        )

    # Find user with token
    user = User.query.filter_by(verification_token=token).first()

    if not user:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "invalid_token",
                    "message": "Invalid or expired reset token",
                }
            ),
            400,
        )

    # Validate new password
    try:
        validate_password(new_password)
    except ValidationError as e:
        return (
            jsonify({"success": False, "error": "validation_error", "message": str(e)}),
            400,
        )

    # Update password and clear token
    user.set_password(new_password)
    user.verification_token = None
    db.session.commit()

    return (
        jsonify(
            {
                "success": True,
                "message": "Password reset successful. You can now log in with your new password.",
            }
        ),
        200,
    )


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """
    Update current user's profile and onboarding status.

    Headers:
        Authorization: Bearer <access_token>

    Request Body (all optional):
        first_name: User's first name
        last_name: User's last name
        phone: Phone number
        location: Location
        linkedin_url: LinkedIn profile URL
        years_experience: Years of experience (integer)
        career_stage: Career stage (entry_level, early_career, mid_level, senior, executive)
        current_role: Current job title
        target_roles: List of target roles
        target_industries: List of target industries
        onboarding_step: Current onboarding step (1-7)
        onboarding_completed: Whether onboarding is complete

    Returns:
        200: Profile updated successfully
        400: Validation error
        404: User not found
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "user_not_found",
                    "message": "User not found",
                }
            ),
            404,
        )

    data = request.get_json()

    if not data:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "invalid_request",
                    "message": "Request body is required",
                }
            ),
            400,
        )

    # Update basic profile fields
    if "first_name" in data:
        user.first_name = data["first_name"].strip() if data["first_name"] else None
    if "last_name" in data:
        user.last_name = data["last_name"].strip() if data["last_name"] else None
    if "phone" in data:
        user.phone = data["phone"].strip() if data["phone"] else None
    if "location" in data:
        user.location = data["location"].strip() if data["location"] else None
    if "linkedin_url" in data:
        user.linkedin_url = data["linkedin_url"].strip() if data["linkedin_url"] else None

    # Update career information
    if "years_experience" in data:
        user.years_experience = data["years_experience"]
        # Auto-detect career stage if not provided
        if "career_stage" not in data and data["years_experience"] is not None:
            user.career_stage = User.detect_career_stage(data["years_experience"])
    if "career_stage" in data:
        user.career_stage = data["career_stage"]
    if "current_role" in data:
        user.current_role = data["current_role"].strip() if data["current_role"] else None
    if "target_roles" in data:
        user.target_roles = data["target_roles"] if isinstance(data["target_roles"], list) else []
    if "target_industries" in data:
        user.target_industries = (
            data["target_industries"] if isinstance(data["target_industries"], list) else []
        )
    if "technical_skills" in data:
        user.technical_skills = (
            data["technical_skills"] if isinstance(data["technical_skills"], list) else []
        )
    if "search_status" in data:
        user.search_status = data["search_status"]
    if "location_preferences" in data:
        user.location_preferences = data["location_preferences"]

    if "ai_disclosures_dismissed" in data:
        valid_keys = {
            "ats_scoring",
            "message_generation",
            "ai_coach",
            "skills_gap",
            "linkedin_optimizer",
            "resume_generation",
            "recruiter_research",
            "career_readiness",
        }
        raw = data["ai_disclosures_dismissed"]
        if isinstance(raw, list):
            user.ai_disclosures_dismissed = [k for k in raw if k in valid_keys]

    if "cookie_consent" in data:
        if data["cookie_consent"] in ("accepted", "declined"):
            user.cookie_consent = data["cookie_consent"]

    # Update onboarding status
    if "onboarding_step" in data:
        user.onboarding_step = data["onboarding_step"]
    if "onboarding_completed" in data:
        user.onboarding_completed = data["onboarding_completed"]

    db.session.commit()

    return (
        jsonify(
            {
                "success": True,
                "message": "Profile updated successfully",
                "data": {"user": user.to_dict(include_private=True)},
            }
        ),
        200,
    )


@auth_bp.route("/tour/status", methods=["GET"])
@jwt_required()
def get_tour_status():
    """
    Get tour completion status for current user.

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        200: Tour status
        404: User not found
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "user_not_found",
                    "message": "User not found",
                }
            ),
            404,
        )

    return (
        jsonify(
            {
                "success": True,
                "tour_completed": user.tour_completed,
                "completed_tours": user.completed_tours or [],
            }
        ),
        200,
    )


@auth_bp.route("/tour/complete", methods=["POST"])
@jwt_required()
def complete_tour():
    """
    Mark a tour as completed for current user.

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        tour_id: ID of the tour to mark as completed (default: "main")

    Returns:
        200: Tour marked as completed
        404: User not found
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "user_not_found",
                    "message": "User not found",
                }
            ),
            404,
        )

    data = request.get_json() or {}
    tour_id = data.get("tour_id", "main")

    # Initialize completed_tours if None
    if user.completed_tours is None:
        user.completed_tours = []

    # Add tour to completed list if not already there
    if tour_id not in user.completed_tours:
        user.completed_tours = user.completed_tours + [tour_id]

    # Mark main tour as completed if it's the main tour
    if tour_id == "main":
        user.tour_completed = True

    db.session.commit()

    return (
        jsonify(
            {
                "success": True,
                "message": "Tour marked as completed",
                "tour_completed": user.tour_completed,
                "completed_tours": user.completed_tours,
            }
        ),
        200,
    )
