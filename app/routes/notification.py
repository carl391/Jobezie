"""
Notification Routes

Provides notification management endpoints including listing, marking as read,
and generating follow-up reminders.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.notification_service import NotificationService

notification_bp = Blueprint("notification", __name__, url_prefix="/api/notifications")


@notification_bp.route("", methods=["GET"])
@jwt_required()
def get_notifications():
    """
    Get notifications for the current user.

    Query Parameters:
        limit (int): Max notifications to return (default 20)
        offset (int): Pagination offset (default 0)
        unread_only (bool): If true, only return unread (default false)

    Returns:
        200: List of notifications with pagination info
    """
    user_id = get_jwt_identity()
    limit = min(int(request.args.get("limit", 20)), 50)
    offset = int(request.args.get("offset", 0))
    unread_only = request.args.get("unread_only", "false").lower() == "true"

    notifications, total = NotificationService.get_notifications(
        user_id, limit=limit, offset=offset, unread_only=unread_only
    )

    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "notifications": [n.to_dict() for n in notifications],
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + len(notifications)) < total,
                },
            }
        ),
        200,
    )


@notification_bp.route("/unread-count", methods=["GET"])
@jwt_required()
def get_unread_count():
    """
    Get count of unread notifications.

    Returns:
        200: Unread notification count
    """
    user_id = get_jwt_identity()
    count = NotificationService.get_unread_count(user_id)

    return jsonify({"success": True, "data": {"count": count}}), 200


@notification_bp.route("/<notification_id>/read", methods=["PUT"])
@jwt_required()
def mark_read(notification_id):
    """
    Mark a single notification as read.

    Returns:
        200: Updated notification
        404: Notification not found
    """
    user_id = get_jwt_identity()

    try:
        notification = NotificationService.mark_read(notification_id, user_id)
        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "notification": notification.to_dict(),
                    },
                }
            ),
            200,
        )
    except ValueError as e:
        return jsonify({"success": False, "data": {"error": str(e)}}), 404


@notification_bp.route("/read-all", methods=["PUT"])
@jwt_required()
def mark_all_read():
    """
    Mark all notifications as read.

    Returns:
        200: Count of notifications marked as read
    """
    user_id = get_jwt_identity()
    count = NotificationService.mark_all_read(user_id)

    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "message": f"{count} notifications marked as read",
                    "count": count,
                },
            }
        ),
        200,
    )


@notification_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_notifications():
    """
    Generate notifications (follow-up reminders and usage warnings).

    This endpoint is called on dashboard load or periodically to create
    new notifications based on user activity.

    Returns:
        200: Count of new notifications generated
    """
    user_id = get_jwt_identity()

    follow_ups = NotificationService.generate_follow_up_reminders(user_id)
    usage_warnings = NotificationService.generate_usage_warnings(user_id)

    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "follow_up_reminders": follow_ups,
                    "usage_warnings": usage_warnings,
                    "total_generated": follow_ups + usage_warnings,
                },
            }
        ),
        200,
    )
