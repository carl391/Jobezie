"""
Message Routes

API endpoints for message management and quality scoring.
"""

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models.user import User
from app.services.message_service import MessageService
from app.utils.decorators import feature_limit
from app.utils.validators import validate_text_fields

message_bp = Blueprint("message", __name__, url_prefix="/api/messages")


@message_bp.route("", methods=["POST"])
@jwt_required()
@feature_limit("ai_messages")
def create_message():
    """
    Create a new message with quality scoring.

    Request body:
        body: Required - Message body text
        message_type: Type of message (initial_outreach, follow_up, thank_you, check_in)
        subject: Email subject line
        recruiter_id: Target recruiter ID
        signature: Message signature
        is_ai_generated: Whether message was AI-generated
        generation_prompt: Prompt used for AI generation
        ai_model_used: AI model used (claude, openai)

    Returns:
        JSON with message data and quality score analysis
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    # Validate and sanitize text fields
    schema = {
        'body': {'required': True, 'max_length': 10000},
        'subject': {'required': False, 'max_length': 500},
        'signature': {'required': False, 'max_length': 500},
        'message_type': {'required': False, 'max_length': 50},
        'generation_prompt': {'required': False, 'max_length': 5000},
    }
    validated, errors = validate_text_fields(data, schema)
    if errors:
        return jsonify({'success': False, 'data': {'errors': errors}}), 400

    try:
        message, quality_result = MessageService.create_message(
            user_id=user_id,
            body=validated["body"],
            message_type=validated.get("message_type") or "initial_outreach",
            subject=validated.get("subject"),
            recruiter_id=data.get("recruiter_id"),
            signature=validated.get("signature"),
            is_ai_generated=data.get("is_ai_generated", False),
            generation_prompt=validated.get("generation_prompt"),
            generation_context=data.get("generation_context"),
            ai_model_used=data.get("ai_model_used"),
        )

        # Increment usage counter
        current_user = User.query.get(user_id)
        if current_user:
            current_user.monthly_message_count += 1
            db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "message": message.to_dict(),
                        "quality_analysis": {
                            "score": quality_result["total_score"],
                            "components": quality_result["components"],
                            "feedback": quality_result["feedback"],
                            "suggestions": quality_result["suggestions"],
                            "word_count": quality_result["word_count"],
                            "is_within_word_limit": quality_result["word_count"] <= 150,
                        },
                    },
                }
            ),
            201,
        )

    except Exception as e:
        current_app.logger.error(f"Create message error: {str(e)}")
        return jsonify({"success": False, "data": {"error": "Failed to create message"}}), 500


@message_bp.route("", methods=["GET"])
@jwt_required()
def get_messages():
    """
    Get messages for the current user.

    Query params:
        recruiter_id: Filter by recruiter
        status: Filter by status
        message_type: Filter by message type
        limit: Maximum results (default: 50)
        offset: Pagination offset (default: 0)

    Returns:
        JSON with messages array and pagination info
    """
    user_id = get_jwt_identity()

    recruiter_id = request.args.get("recruiter_id")
    status = request.args.get("status")
    message_type = request.args.get("message_type")
    limit = min(int(request.args.get("limit", 50)), 100)
    offset = int(request.args.get("offset", 0))

    messages, total = MessageService.get_user_messages(
        user_id=user_id,
        recruiter_id=recruiter_id,
        status=status,
        message_type=message_type,
        limit=limit,
        offset=offset,
    )

    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "messages": [m.to_dict() for m in messages],
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + len(messages)) < total,
                },
            }
        ),
        200,
    )


@message_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    """
    Get message statistics for dashboard.

    Returns:
        JSON with counts, averages, and effectiveness metrics
    """
    user_id = get_jwt_identity()
    stats = MessageService.get_message_stats(user_id)

    return jsonify({"success": True, "data": stats}), 200


@message_bp.route("/tips/<message_type>", methods=["GET"])
@jwt_required()
def get_tips(message_type):
    """
    Get quality tips for a message type.

    Returns:
        JSON with structure, word limit, tone, and research insights
    """
    tips = MessageService.get_quality_tips(message_type)
    return jsonify({"success": True, "data": tips}), 200


@message_bp.route("/validate", methods=["POST"])
@jwt_required()
def validate_message():
    """
    Quick validation of message length.

    Request body:
        body: Message text
        message_type: Type of message

    Returns:
        JSON with validation result
    """
    data = request.get_json() or {}

    body = data.get("body", "")
    message_type = data.get("message_type", "initial_outreach")

    result = MessageService.validate_message(body, message_type)

    return jsonify({"success": True, "data": result}), 200


@message_bp.route("/context", methods=["POST"])
@jwt_required()
def get_generation_context():
    """
    Get context for AI message generation.

    Request body:
        recruiter_id: Required - Target recruiter ID
        message_type: Type of message to generate
        resume_id: Optional resume ID to pull achievements from

    Returns:
        JSON with generation context for AI
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    recruiter_id = data.get("recruiter_id")
    if not recruiter_id:
        return jsonify({"success": False, "data": {"error": "recruiter_id is required"}}), 400

    context = MessageService.get_generation_context(
        user_id=user_id,
        recruiter_id=recruiter_id,
        message_type=data.get("message_type", "initial_outreach"),
        resume_id=data.get("resume_id"),
    )

    return jsonify({"success": True, "data": context}), 200


@message_bp.route("/<message_id>", methods=["GET"])
@jwt_required()
def get_message(message_id):
    """
    Get a specific message by ID.

    Returns:
        JSON with message data including quality analysis
    """
    user_id = get_jwt_identity()
    message = MessageService.get_message(message_id, user_id)

    if not message:
        return jsonify({"success": False, "data": {"error": "Message not found"}}), 404

    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "message": message.to_dict(include_generation=True),
                },
            }
        ),
        200,
    )


@message_bp.route("/<message_id>", methods=["PUT"])
@jwt_required()
def update_message(message_id):
    """
    Update a message and recalculate quality score.

    Request body:
        body: New message body
        subject: New subject line
        signature: New signature

    Returns:
        JSON with updated message and new quality analysis
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    try:
        message, quality_result = MessageService.update_message(
            message_id=message_id,
            user_id=user_id,
            body=data.get("body"),
            subject=data.get("subject"),
            signature=data.get("signature"),
        )

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "message": message.to_dict(),
                        "quality_analysis": {
                            "score": quality_result["total_score"],
                            "components": quality_result["components"],
                            "feedback": quality_result["feedback"],
                            "suggestions": quality_result["suggestions"],
                            "word_count": quality_result["word_count"],
                        },
                    },
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"success": False, "data": {"error": str(e)}}), 400


@message_bp.route("/<message_id>", methods=["DELETE"])
@jwt_required()
def delete_message(message_id):
    """
    Delete a message.

    Returns:
        JSON with success message
    """
    user_id = get_jwt_identity()

    try:
        MessageService.delete_message(message_id, user_id)
        return jsonify({"success": True, "message": "Message deleted", "data": {}}), 200
    except ValueError as e:
        return jsonify({"success": False, "data": {"error": str(e)}}), 400


@message_bp.route("/<message_id>/send", methods=["POST"])
@jwt_required()
def mark_sent(message_id):
    """
    Mark a message as sent.

    Returns:
        JSON with updated message data
    """
    user_id = get_jwt_identity()

    try:
        message = MessageService.mark_as_sent(message_id, user_id)
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Message marked as sent",
                    "data": {"message": message.to_dict()},
                }
            ),
            200,
        )
    except ValueError as e:
        return jsonify({"success": False, "data": {"error": str(e)}}), 404


@message_bp.route("/<message_id>/opened", methods=["POST"])
@jwt_required()
def mark_opened(message_id):
    """
    Mark a message as opened.

    Returns:
        JSON with updated message data
    """
    user_id = get_jwt_identity()

    try:
        message = MessageService.mark_as_opened(message_id, user_id)
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Message marked as opened",
                    "data": {"message": message.to_dict()},
                }
            ),
            200,
        )
    except ValueError as e:
        return jsonify({"success": False, "data": {"error": str(e)}}), 404


@message_bp.route("/<message_id>/responded", methods=["POST"])
@jwt_required()
def mark_responded(message_id):
    """
    Mark a message as having received a response.

    Returns:
        JSON with updated message data
    """
    user_id = get_jwt_identity()

    try:
        message = MessageService.mark_as_responded(message_id, user_id)
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Response recorded",
                    "data": {"message": message.to_dict()},
                }
            ),
            200,
        )
    except ValueError as e:
        return jsonify({"success": False, "data": {"error": str(e)}}), 404


@message_bp.route("/<message_id>/score", methods=["GET"])
@jwt_required()
def get_quality_score(message_id):
    """
    Get detailed quality score breakdown for a message.

    Returns:
        JSON with full quality analysis
    """
    user_id = get_jwt_identity()
    message = MessageService.get_message(message_id, user_id)

    if not message:
        return jsonify({"success": False, "data": {"error": "Message not found"}}), 404

    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "message_id": str(message.id),
                    "quality_breakdown": message.quality_breakdown,
                    "word_count": message.word_count,
                    "is_within_word_limit": message.is_within_word_limit,
                    "has_personalization": message.has_personalization,
                    "has_metrics": message.has_metrics,
                    "has_cta": message.has_cta,
                    "personalization_elements": message.personalization_elements,
                    "feedback": message.quality_feedback,
                    "suggestions": message.quality_suggestions,
                },
            }
        ),
        200,
    )
