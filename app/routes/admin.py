"""
Admin Routes

Handles admin authentication and administrative operations.
"""

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
)

from app.extensions import db
from app.models.user import User
from app.utils.admin_helpers import log_admin_action

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/login", methods=["POST"])
def admin_login():
    """
    Admin-only login endpoint.

    Request Body:
        email: Admin user's email (required)
        password: Admin user's password (required)

    Returns:
        200: Login successful with tokens
        400: Missing fields
        401: Invalid credentials
        403: Not an admin
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

    if not user.is_admin:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "forbidden",
                    "message": "Admin privileges required",
                }
            ),
            403,
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.session.commit()

    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    # Log admin login
    log_admin_action(
        admin_user_id=str(user.id),
        action="admin_login",
        details={"email": user.email},
    )

    return (
        jsonify(
            {
                "success": True,
                "message": "Admin login successful",
                "data": {
                    "user": user.to_dict(include_private=True),
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
            }
        ),
        200,
    )
