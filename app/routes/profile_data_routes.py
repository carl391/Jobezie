"""
User data rights routes - account deletion + DSAR data export.

Endpoints:
    DELETE /api/profile/account                - Request account deletion
    POST  /api/profile/account/cancel-deletion - Cancel pending deletion
    POST  /api/profile/export                  - Request data export
    GET   /api/profile/export/status           - Check export status
    GET   /api/profile/export/download/<token> - Download export ZIP (token-based)

Register:
    from app.routes.profile_data_routes import profile_data_bp
    app.register_blueprint(profile_data_bp)
"""

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models.user import User
from app.services.account_service import (
    cancel_account_deletion,
    create_data_export,
    get_export_download,
    get_export_status,
    request_account_deletion,
)

profile_data_bp = Blueprint("profile_data", __name__, url_prefix="/api/profile")


# ───────────────────────────────────────────
# Account Deletion
# ───────────────────────────────────────────


@profile_data_bp.route("/account", methods=["DELETE"])
@jwt_required()
def delete_account():
    """
    Request account deletion with 30-day grace period.

    Body: { "password": "...", "confirmation": "DELETE" }

    - Password verification prevents unauthorized deletion
    - Typing "DELETE" prevents accidental clicks
    - Subscription cancelled immediately
    - Data retained for 30 days (can cancel)
    - After 30 days, hard-delete cascade runs
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    data = request.get_json() or {}

    # Require password
    password = data.get("password", "")
    if not password:
        return jsonify({"error": "Password required for account deletion"}), 400
    if not user.check_password(password):
        return jsonify({"error": "Incorrect password"}), 401

    # Require explicit confirmation
    confirmation = data.get("confirmation", "")
    if confirmation != "DELETE":
        return jsonify({"error": "Please type DELETE to confirm"}), 400

    result = request_account_deletion(user.id)
    status_code = result.pop("status_code", 200)
    return jsonify(result), status_code


@profile_data_bp.route("/account/cancel-deletion", methods=["POST"])
@jwt_required()
def cancel_deletion():
    """Cancel a pending account deletion (within 30-day grace period)."""
    user_id = get_jwt_identity()

    result = cancel_account_deletion(user_id)
    status_code = result.pop("status_code", 200)
    return jsonify(result), status_code


# ───────────────────────────────────────────
# Data Export (DSAR)
# ───────────────────────────────────────────


@profile_data_bp.route("/export", methods=["POST"])
@jwt_required()
def request_export():
    """
    Request a full data export (DSAR compliance).

    Generates a ZIP containing: profile, recruiters, messages,
    activities, resumes, scores, coach history, subscriptions.

    Returns a download_token valid for 7 days.
    """
    user_id = get_jwt_identity()

    result = create_data_export(user_id)
    status_code = result.pop("status_code", 200)
    return jsonify(result), status_code


@profile_data_bp.route("/export/status", methods=["GET"])
@jwt_required()
def export_status():
    """Get status of the most recent data export request."""
    user_id = get_jwt_identity()

    result = get_export_status(user_id)
    return jsonify(result), 200


@profile_data_bp.route("/export/download/<token>", methods=["GET"])
def download_export(token):
    """
    Download a completed data export.

    No JWT required - uses secure one-time token from email.
    Token expires after 7 days.
    """
    if not token or len(token) < 16:
        return jsonify({"error": "Invalid download token"}), 400

    result = get_export_download(token)

    if "error" in result:
        status_code = result.pop("status_code", 404)
        return jsonify(result), status_code

    return send_file(
        result["file_path"],
        mimetype="application/zip",
        as_attachment=True,
        download_name="jobezie_data_export.zip",
    )
