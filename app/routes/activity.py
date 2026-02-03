"""
Activity Routes

API endpoints for activity tracking and Kanban pipeline management.
"""

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models.activity import ActivityType, PipelineStage
from app.services.activity_service import ActivityService

activity_bp = Blueprint("activity", __name__, url_prefix="/api/activities")


@activity_bp.route("", methods=["POST"])
@jwt_required()
def log_activity():
    """
    Log a new activity.

    Request body:
        activity_type: Required - Type of activity
        description: Human-readable description
        recruiter_id: Related recruiter ID
        resume_id: Related resume ID
        message_id: Related message ID
        extra_data: Additional context data

    Returns:
        JSON with new activity data
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    activity_type = data.get("activity_type")
    if not activity_type:
        return jsonify({"error": "activity_type is required"}), 400

    # Validate activity type
    valid_types = [t.value for t in ActivityType]
    if activity_type not in valid_types:
        return (
            jsonify({"error": f'Invalid activity_type. Must be one of: {", ".join(valid_types)}'}),
            400,
        )

    activity = ActivityService.log_activity(
        user_id=user_id,
        activity_type=activity_type,
        description=data.get("description"),
        recruiter_id=data.get("recruiter_id"),
        resume_id=data.get("resume_id"),
        message_id=data.get("message_id"),
        extra_data=data.get("extra_data"),
    )

    return (
        jsonify(
            {
                "message": "Activity logged",
                "activity": activity.to_dict(),
            }
        ),
        201,
    )


@activity_bp.route("", methods=["GET"])
@jwt_required()
def get_activities():
    """
    Get activities for the current user.

    Query params:
        activity_type: Filter by activity type
        recruiter_id: Filter by recruiter
        start_date: Filter activities after this date (ISO format)
        end_date: Filter activities before this date (ISO format)
        limit: Maximum results (default: 50)
        offset: Pagination offset (default: 0)

    Returns:
        JSON with activities array and pagination info
    """
    user_id = get_jwt_identity()

    activity_type = request.args.get("activity_type")
    recruiter_id = request.args.get("recruiter_id")
    limit = min(int(request.args.get("limit", 50)), 100)
    offset = int(request.args.get("offset", 0))

    start_date = None
    end_date = None

    if request.args.get("start_date"):
        try:
            start_date = datetime.fromisoformat(
                request.args.get("start_date").replace("Z", "+00:00")
            )
        except ValueError:
            pass

    if request.args.get("end_date"):
        try:
            end_date = datetime.fromisoformat(request.args.get("end_date").replace("Z", "+00:00"))
        except ValueError:
            pass

    activities, total = ActivityService.get_user_activities(
        user_id=user_id,
        activity_type=activity_type,
        recruiter_id=recruiter_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )

    return (
        jsonify(
            {
                "activities": [a.to_dict() for a in activities],
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + len(activities)) < total,
            }
        ),
        200,
    )


@activity_bp.route("/recent", methods=["GET"])
@jwt_required()
def get_recent():
    """
    Get most recent activities for dashboard.

    Query params:
        limit: Maximum results (default: 10)

    Returns:
        JSON array of recent activities
    """
    user_id = get_jwt_identity()
    limit = min(int(request.args.get("limit", 10)), 25)

    activities = ActivityService.get_recent_activities(user_id, limit)

    return (
        jsonify(
            {
                "activities": [a.to_dict() for a in activities],
            }
        ),
        200,
    )


@activity_bp.route("/counts", methods=["GET"])
@jwt_required()
def get_counts():
    """
    Get activity counts by type.

    Query params:
        days: Number of days to look back (default: 30)

    Returns:
        JSON with counts by activity type
    """
    user_id = get_jwt_identity()
    days = min(int(request.args.get("days", 30)), 365)

    counts = ActivityService.get_activity_counts(user_id, days)

    return jsonify(counts), 200


@activity_bp.route("/timeline", methods=["GET"])
@jwt_required()
def get_timeline():
    """
    Get activity timeline for display.

    Query params:
        recruiter_id: Filter by recruiter
        limit: Maximum items (default: 20)

    Returns:
        JSON array of timeline items
    """
    user_id = get_jwt_identity()
    recruiter_id = request.args.get("recruiter_id")
    limit = min(int(request.args.get("limit", 20)), 50)

    timeline = ActivityService.get_activity_timeline(
        user_id=user_id,
        recruiter_id=recruiter_id,
        limit=limit,
    )

    return (
        jsonify(
            {
                "timeline": timeline,
            }
        ),
        200,
    )


@activity_bp.route("/weekly-summary", methods=["GET"])
@jwt_required()
def get_weekly_summary():
    """
    Get weekly activity summary.

    Returns:
        JSON with weekly metrics and highlights
    """
    user_id = get_jwt_identity()
    summary = ActivityService.get_weekly_summary(user_id)

    return jsonify(summary), 200


@activity_bp.route("/types", methods=["GET"])
@jwt_required()
def get_types():
    """
    Get available activity types.

    Returns:
        JSON with type definitions
    """
    types = [{"value": t.value, "label": t.value.replace("_", " ").title()} for t in ActivityType]

    return jsonify({"types": types}), 200


# Pipeline / Kanban Endpoints


@activity_bp.route("/pipeline", methods=["GET"])
@jwt_required()
def get_pipeline():
    """
    Get full Kanban pipeline.

    Returns:
        JSON with stages as keys and arrays of pipeline items
    """
    user_id = get_jwt_identity()
    pipeline = ActivityService.get_pipeline(user_id)

    return (
        jsonify(
            {
                "pipeline": pipeline,
                "stages": [s.value for s in PipelineStage],
            }
        ),
        200,
    )


@activity_bp.route("/pipeline/stats", methods=["GET"])
@jwt_required()
def get_pipeline_stats():
    """
    Get pipeline statistics.

    Returns:
        JSON with stage counts and metrics
    """
    user_id = get_jwt_identity()
    stats = ActivityService.get_pipeline_stats(user_id)

    return jsonify(stats), 200


@activity_bp.route("/pipeline/stages", methods=["GET"])
@jwt_required()
def get_stages():
    """
    Get available pipeline stages.

    Returns:
        JSON with stage definitions
    """
    stages = [{"value": s.value, "label": s.value.replace("_", " ").title()} for s in PipelineStage]

    return jsonify({"stages": stages}), 200


@activity_bp.route("/pipeline/<item_id>/move", methods=["PUT"])
@jwt_required()
def move_item(item_id):
    """
    Move a pipeline item to a new stage or position.

    Request body:
        stage: Target stage
        position: Position within stage (optional)

    Returns:
        JSON with updated pipeline item
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    stage = data.get("stage")
    if not stage:
        return jsonify({"error": "stage is required"}), 400

    try:
        item = ActivityService.move_pipeline_item(
            user_id=user_id,
            item_id=item_id,
            new_stage=stage,
            new_position=data.get("position"),
        )

        return (
            jsonify(
                {
                    "message": f"Moved to {stage}",
                    "item": item.to_dict(),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@activity_bp.route("/pipeline/refresh", methods=["POST"])
@jwt_required()
def refresh_pipeline():
    """
    Refresh pipeline metrics (days in stage, priority scores).

    Should be called periodically or after significant changes.

    Returns:
        JSON with update counts
    """
    user_id = get_jwt_identity()

    days_updated = ActivityService.update_days_in_stage(user_id)
    priorities_updated = ActivityService.update_priority_scores(user_id)

    return (
        jsonify(
            {
                "message": "Pipeline refreshed",
                "days_in_stage_updated": days_updated,
                "priority_scores_updated": priorities_updated,
            }
        ),
        200,
    )
