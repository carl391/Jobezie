"""
Recruiter CRM Routes

API endpoints for recruiter management and engagement tracking.
"""

from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models.activity import PipelineStage
from app.models.user import User
from app.services.recruiter_service import RecruiterService
from app.utils.decorators import feature_limit
from app.utils.validators import validate_text_fields

recruiter_bp = Blueprint("recruiter", __name__, url_prefix="/api/recruiters")


@recruiter_bp.route("", methods=["POST"])
@jwt_required()
@feature_limit("recruiters")
def create_recruiter():
    """
    Add a new recruiter to the CRM.

    Request body:
        first_name: Required - Recruiter's first name
        last_name: Required - Recruiter's last name
        email: Email address
        company: Company name
        title: Job title
        linkedin_url: LinkedIn profile URL
        phone: Phone number
        industries: List of industries they recruit for
        locations: List of locations they cover
        specialty: Role specialty
        company_type: Agency, corporate, executive search
        source: Where the recruiter was found
        notes: Initial notes

    Returns:
        JSON with new recruiter data
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    # Validate and sanitize text fields
    schema = {
        "first_name": {"required": True, "max_length": 100},
        "last_name": {"required": True, "max_length": 100},
        "email": {"required": False, "max_length": 254},
        "company": {"required": False, "max_length": 200},
        "title": {"required": False, "max_length": 200},
        "linkedin_url": {"required": False, "max_length": 500},
        "phone": {"required": False, "max_length": 30},
        "specialty": {"required": False, "max_length": 200},
        "company_type": {"required": False, "max_length": 50},
        "source": {"required": False, "max_length": 200},
        "notes": {"required": False, "max_length": 5000},
    }
    validated, errors = validate_text_fields(data, schema)
    if errors:
        return jsonify({"success": False, "data": {"errors": errors}}), 400

    try:
        recruiter = RecruiterService.create_recruiter(
            user_id=user_id,
            first_name=validated["first_name"],
            last_name=validated["last_name"],
            email=validated.get("email"),
            company=validated.get("company"),
            title=validated.get("title"),
            linkedin_url=validated.get("linkedin_url"),
            phone=validated.get("phone"),
            industries=data.get("industries"),  # Lists handled separately
            locations=data.get("locations"),
            specialty=validated.get("specialty"),
            company_type=validated.get("company_type"),
            source=validated.get("source"),
            notes=validated.get("notes"),
        )

        # Increment usage counter
        current_user = User.query.get(user_id)
        if current_user:
            current_user.monthly_recruiter_count += 1
            db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "message": "Recruiter added successfully",
                        "recruiter": recruiter.to_dict(),
                    },
                }
            ),
            201,
        )

    except Exception as e:
        current_app.logger.error(f"Create recruiter error: {str(e)}")
        return jsonify({"success": False, "data": {"error": "Failed to create recruiter"}}), 500


@recruiter_bp.route("", methods=["GET"])
@jwt_required()
def get_recruiters():
    """
    Get all recruiters for the current user.

    Query params:
        status: Filter by pipeline status
        industry: Filter by industry
        location: Filter by location
        sort_by: Sort field (priority, name, company, last_contact, engagement, fit)
        limit: Maximum results (default: 50)
        offset: Pagination offset (default: 0)

    Returns:
        JSON with recruiters array and pagination info
    """
    user_id = get_jwt_identity()

    status = request.args.get("status")
    industry = request.args.get("industry")
    location = request.args.get("location")
    sort_by = request.args.get("sort_by", "priority")
    limit = min(int(request.args.get("limit", 50)), 100)
    offset = int(request.args.get("offset", 0))

    recruiters, total = RecruiterService.get_user_recruiters(
        user_id=user_id,
        status=status,
        industry=industry,
        location=location,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )

    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "recruiters": [r.to_dict() for r in recruiters],
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + len(recruiters)) < total,
                },
            }
        ),
        200,
    )


@recruiter_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    """
    Get pipeline statistics for dashboard.

    Returns:
        JSON with stats by stage, response rate, and averages
    """
    user_id = get_jwt_identity()
    stats = RecruiterService.get_pipeline_stats(user_id)

    return jsonify({"success": True, "data": stats}), 200


@recruiter_bp.route("/stages", methods=["GET"])
@jwt_required()
def get_stages():
    """
    Get available pipeline stages.

    Returns:
        JSON with stage definitions
    """
    stages = [{"value": s.value, "label": s.value.replace("_", " ").title()} for s in PipelineStage]

    return jsonify({"success": True, "data": {"stages": stages}}), 200


@recruiter_bp.route("/recommendations", methods=["GET"])
@jwt_required()
def get_recommendations():
    """
    Get follow-up recommendations sorted by priority.

    Query params:
        limit: Maximum recommendations (default: 10)

    Returns:
        JSON with recommended actions
    """
    user_id = get_jwt_identity()
    limit = min(int(request.args.get("limit", 10)), 25)

    recommendations = RecruiterService.get_follow_up_recommendations(user_id, limit)

    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "recommendations": recommendations,
                    "count": len(recommendations),
                },
            }
        ),
        200,
    )


@recruiter_bp.route("/<recruiter_id>", methods=["GET"])
@jwt_required()
def get_recruiter(recruiter_id):
    """
    Get a specific recruiter by ID.

    Returns:
        JSON with recruiter data including engagement and fit scores
    """
    user_id = get_jwt_identity()
    recruiter = RecruiterService.get_recruiter(recruiter_id, user_id)

    if not recruiter:
        return jsonify({"success": False, "data": {"error": "Recruiter not found"}}), 404

    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "recruiter": recruiter.to_dict(include_engagement=True),
                },
            }
        ),
        200,
    )


@recruiter_bp.route("/<recruiter_id>", methods=["PUT"])
@jwt_required()
def update_recruiter(recruiter_id):
    """
    Update recruiter information.

    Request body:
        Any updatable recruiter fields

    Returns:
        JSON with updated recruiter data
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    try:
        recruiter = RecruiterService.update_recruiter(
            recruiter_id=recruiter_id, user_id=user_id, **data
        )

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "message": "Recruiter updated",
                        "recruiter": recruiter.to_dict(),
                    },
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"success": False, "data": {"error": str(e)}}), 404


@recruiter_bp.route("/<recruiter_id>", methods=["DELETE"])
@jwt_required()
def delete_recruiter(recruiter_id):
    """
    Delete a recruiter from CRM.

    Returns:
        JSON with success message
    """
    user_id = get_jwt_identity()

    try:
        RecruiterService.delete_recruiter(recruiter_id, user_id)
        return jsonify({"success": True, "data": {"message": "Recruiter deleted"}}), 200
    except ValueError as e:
        return jsonify({"success": False, "data": {"error": str(e)}}), 404


@recruiter_bp.route("/<recruiter_id>/stage", methods=["PUT"])
@jwt_required()
def update_stage(recruiter_id):
    """
    Move recruiter to a new pipeline stage.

    Request body:
        stage: New pipeline stage value

    Returns:
        JSON with updated recruiter data
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    stage = data.get("stage")
    if not stage:
        return jsonify({"success": False, "data": {"error": "stage is required"}}), 400

    try:
        recruiter = RecruiterService.update_pipeline_stage(
            recruiter_id=recruiter_id,
            user_id=user_id,
            new_stage=stage,
        )

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "message": f"Recruiter moved to {stage}",
                        "recruiter": recruiter.to_dict(),
                    },
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"success": False, "data": {"error": str(e)}}), 400


@recruiter_bp.route("/<recruiter_id>/message-sent", methods=["POST"])
@jwt_required()
def record_message_sent(recruiter_id):
    """
    Record that a message was sent to recruiter.

    Request body:
        message_id: Optional - ID of the message sent

    Returns:
        JSON with updated recruiter engagement data
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    try:
        recruiter = RecruiterService.record_message_sent(
            recruiter_id=recruiter_id,
            user_id=user_id,
            message_id=data.get("message_id"),
        )

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "message": "Message recorded",
                        "engagement_score": recruiter.engagement_score,
                        "messages_sent": recruiter.messages_sent,
                    },
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"success": False, "data": {"error": str(e)}}), 404


@recruiter_bp.route("/<recruiter_id>/message-opened", methods=["POST"])
@jwt_required()
def record_message_opened(recruiter_id):
    """
    Record that a message was opened by recruiter.

    Returns:
        JSON with updated engagement data
    """
    user_id = get_jwt_identity()

    try:
        recruiter = RecruiterService.record_message_opened(
            recruiter_id=recruiter_id,
            user_id=user_id,
        )

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "message": "Open recorded",
                        "engagement_score": recruiter.engagement_score,
                        "messages_opened": recruiter.messages_opened,
                    },
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"success": False, "data": {"error": str(e)}}), 404


@recruiter_bp.route("/<recruiter_id>/response", methods=["POST"])
@jwt_required()
def record_response(recruiter_id):
    """
    Record a response from recruiter.

    Request body:
        is_positive: Whether response was positive (default: true)

    Returns:
        JSON with updated recruiter data
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    try:
        recruiter = RecruiterService.record_response(
            recruiter_id=recruiter_id,
            user_id=user_id,
            is_positive=data.get("is_positive", True),
        )

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "message": "Response recorded",
                        "recruiter": recruiter.to_dict(include_engagement=True),
                    },
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"success": False, "data": {"error": str(e)}}), 404


@recruiter_bp.route("/<recruiter_id>/fit-score", methods=["POST"])
@jwt_required()
def calculate_fit(recruiter_id):
    """
    Calculate fit score for a recruiter against user's profile.

    Request body:
        user_industries: User's target industries
        user_location: User's location preference
        user_target_roles: User's target job roles
        user_salary_expectation: User's salary expectation

    Returns:
        JSON with fit score breakdown
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    try:
        result = RecruiterService.calculate_fit_score(
            recruiter_id=recruiter_id,
            user_id=user_id,
            user_industries=data.get("user_industries", []),
            user_location=data.get("user_location"),
            user_target_roles=data.get("user_target_roles", []),
            user_salary_expectation=data.get("user_salary_expectation"),
        )

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "fit_score": result["total_score"],
                        "components": result["components"],
                    },
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"success": False, "data": {"error": str(e)}}), 404


@recruiter_bp.route("/<recruiter_id>/notes", methods=["GET"])
@jwt_required()
def get_notes(recruiter_id):
    """
    Get all notes for a recruiter.

    Returns:
        JSON array of notes
    """
    user_id = get_jwt_identity()

    try:
        notes = RecruiterService.get_notes(recruiter_id, user_id)
        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "notes": [n.to_dict() for n in notes],
                    },
                }
            ),
            200,
        )
    except ValueError as e:
        return jsonify({"success": False, "data": {"error": str(e)}}), 404


@recruiter_bp.route("/<recruiter_id>/notes", methods=["POST"])
@jwt_required()
def add_note(recruiter_id):
    """
    Add a note to a recruiter.

    Request body:
        content: Note content
        note_type: Type of note (general, call, email, meeting, research)

    Returns:
        JSON with new note data
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    # Validate and sanitize text fields
    schema = {
        "content": {"required": True, "max_length": 10000},
        "note_type": {"required": False, "max_length": 50},
    }
    validated, errors = validate_text_fields(data, schema)
    if errors:
        return jsonify({"success": False, "data": {"errors": errors}}), 400

    try:
        note = RecruiterService.add_note(
            recruiter_id=recruiter_id,
            user_id=user_id,
            content=validated["content"],
            note_type=validated.get("note_type") or "general",
        )

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "message": "Note added",
                        "note": note.to_dict(),
                    },
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"success": False, "data": {"error": str(e)}}), 404


@recruiter_bp.route("/<recruiter_id>/next-action", methods=["PUT"])
@jwt_required()
def set_next_action(recruiter_id):
    """
    Set next action for a recruiter.

    Request body:
        action: Description of next action
        due_date: ISO format date when action is due

    Returns:
        JSON with updated recruiter data
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    action = data.get("action")
    if not action:
        return jsonify({"success": False, "data": {"error": "action is required"}}), 400

    due_date = None
    if data.get("due_date"):
        try:
            due_date = datetime.fromisoformat(data["due_date"].replace("Z", "+00:00"))
        except ValueError:
            return jsonify({"success": False, "data": {"error": "Invalid due_date format"}}), 400

    try:
        recruiter = RecruiterService.set_next_action(
            recruiter_id=recruiter_id,
            user_id=user_id,
            action=action,
            due_date=due_date,
        )

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "message": "Next action set",
                        "recruiter": recruiter.to_dict(),
                    },
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"success": False, "data": {"error": str(e)}}), 404
