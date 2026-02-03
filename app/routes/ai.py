"""
AI Routes

API endpoints for AI-powered career assistance features.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.ai_service import (
    AIService,
    career_coaching_sync,
    generate_message_sync,
    interview_prep_sync,
    optimize_resume_sync,
)
from app.services.message_service import MessageService
from app.services.resume_service import ResumeService

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")


@ai_bp.route("/status", methods=["GET"])
@jwt_required()
def get_status():
    """
    Get AI service status.

    Returns:
        JSON with available provider and configuration
    """
    provider = AIService.get_provider()

    return (
        jsonify(
            {
                "available": provider != "none",
                "provider": provider if provider != "none" else None,
                "features": {
                    "message_generation": provider != "none",
                    "resume_optimization": provider != "none",
                    "career_coaching": provider != "none",
                    "interview_prep": provider != "none",
                },
            }
        ),
        200,
    )


@ai_bp.route("/generate-message", methods=["POST"])
@jwt_required()
def generate_message():
    """
    Generate an outreach message using AI.

    Request body:
        recruiter_id: Required - Target recruiter ID
        message_type: Type of message (default: initial_outreach)
        resume_id: Optional - Resume to pull achievements from
        save_draft: Whether to save as draft (default: true)

    Returns:
        JSON with generated message and quality score
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    recruiter_id = data.get("recruiter_id")
    if not recruiter_id:
        return jsonify({"error": "recruiter_id is required"}), 400

    message_type = data.get("message_type", "initial_outreach")
    resume_id = data.get("resume_id")
    save_draft = data.get("save_draft", True)

    # Get generation context
    context = MessageService.get_generation_context(
        user_id=user_id,
        recruiter_id=recruiter_id,
        message_type=message_type,
        resume_id=resume_id,
    )

    # Generate message
    result = generate_message_sync(context, message_type)

    if not result["success"]:
        return (
            jsonify(
                {
                    "error": result.get("error", "Failed to generate message"),
                }
            ),
            500,
        )

    response_data = {
        "generated_message": result["message"],
        "provider": result["provider"],
        "model": result["model"],
    }

    # Optionally save as draft
    if save_draft and result["message"]:
        message, quality = MessageService.create_message(
            user_id=user_id,
            body=result["message"],
            message_type=message_type,
            recruiter_id=recruiter_id,
            is_ai_generated=True,
            generation_prompt=str(context),
            generation_context=context,
            ai_model_used=result["model"],
        )
        response_data["message_id"] = str(message.id)
        response_data["quality_score"] = quality["total_score"]
        response_data["quality_feedback"] = quality["feedback"]

    return jsonify(response_data), 200


@ai_bp.route("/optimize-resume", methods=["POST"])
@jwt_required()
def optimize_resume():
    """
    Get AI suggestions for resume optimization.

    Request body:
        resume_id: Required - Resume to optimize
        target_role: Optional - Target job title
        job_keywords: Optional - Keywords to incorporate

    Returns:
        JSON with optimization suggestions
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    resume_id = data.get("resume_id")
    if not resume_id:
        return jsonify({"error": "resume_id is required"}), 400

    # Get resume
    resume = ResumeService.get_resume(resume_id, user_id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    # Get current ATS analysis for context
    suggestions_data = ResumeService.get_optimization_suggestions(resume_id, user_id)

    # Generate AI suggestions
    result = optimize_resume_sync(
        resume_text=resume.raw_text,
        target_role=data.get("target_role") or resume.target_job_title,
        job_keywords=data.get("job_keywords", []),
        weak_sections=resume.weak_sections,
    )

    if not result["success"]:
        return (
            jsonify(
                {
                    "error": result.get("error", "Failed to generate suggestions"),
                }
            ),
            500,
        )

    return (
        jsonify(
            {
                "resume_id": str(resume.id),
                "current_score": resume.ats_total_score,
                "algorithm_suggestions": suggestions_data,
                "ai_suggestions": result["suggestions"],
                "provider": result["provider"],
            }
        ),
        200,
    )


@ai_bp.route("/career-coach", methods=["POST"])
@jwt_required()
def career_coach():
    """
    Get AI career coaching response.

    Request body:
        question: Required - User's question
        conversation_id: Optional - Continue existing conversation

    Returns:
        JSON with coaching response
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    question = data.get("question")
    if not question:
        return jsonify({"error": "question is required"}), 400

    # Get user context from profile
    from app.models.user import User

    user = User.query.get(user_id)

    user_context = None
    if user:
        user_context = {
            "current_role": user.current_role,
            "target_roles": user.target_roles or [],
            "industries": user.target_industries or [],
            "experience_level": user.career_stage,
            "location": user.location,
        }

    # Get conversation history if continuing
    conversation_history = data.get("conversation_history", [])

    result = career_coaching_sync(
        question=question,
        user_context=user_context,
        conversation_history=conversation_history,
    )

    if not result["success"]:
        return (
            jsonify(
                {
                    "error": result.get("error", "Failed to get coaching response"),
                }
            ),
            500,
        )

    return (
        jsonify(
            {
                "response": result["response"],
                "provider": result["provider"],
            }
        ),
        200,
    )


@ai_bp.route("/interview-prep", methods=["POST"])
@jwt_required()
def interview_prep():
    """
    Generate interview preparation materials.

    Request body:
        job_title: Required - Role being interviewed for
        company: Optional - Company name
        interview_type: Type of interview (behavioral, technical, case)
        resume_id: Optional - Resume for tailoring prep

    Returns:
        JSON with preparation materials
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    job_title = data.get("job_title")
    if not job_title:
        return jsonify({"error": "job_title is required"}), 400

    # Get user experience from resume if provided
    user_experience = None
    if data.get("resume_id"):
        resume = ResumeService.get_resume(data["resume_id"], user_id)
        if resume and resume.parsed_sections:
            experience = resume.parsed_sections.get("experience", "")
            user_experience = experience[:2000]  # Truncate

    result = interview_prep_sync(
        job_title=job_title,
        company=data.get("company"),
        interview_type=data.get("interview_type", "behavioral"),
        user_experience=user_experience,
    )

    if not result["success"]:
        return (
            jsonify(
                {
                    "error": result.get("error", "Failed to generate prep materials"),
                }
            ),
            500,
        )

    return (
        jsonify(
            {
                "job_title": job_title,
                "company": data.get("company"),
                "interview_type": data.get("interview_type", "behavioral"),
                "prep_materials": result["prep_materials"],
                "provider": result["provider"],
            }
        ),
        200,
    )


@ai_bp.route("/improve-message", methods=["POST"])
@jwt_required()
def improve_message():
    """
    Get AI suggestions to improve an existing message.

    Request body:
        message_id: Required - Message to improve
        focus_areas: Optional - Specific areas to improve

    Returns:
        JSON with improvement suggestions
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    message_id = data.get("message_id")
    if not message_id:
        return jsonify({"error": "message_id is required"}), 400

    from app.models.message import Message

    message = Message.query.filter_by(id=message_id, user_id=user_id).first()

    if not message:
        return jsonify({"error": "Message not found"}), 404

    # Build improvement prompt
    focus_areas = data.get("focus_areas", [])
    focus_str = ", ".join(focus_areas) if focus_areas else "overall quality"

    prompt = f"""Please improve this recruiter outreach message. Focus on: {focus_str}

CURRENT MESSAGE:
{message.body}

CURRENT QUALITY SCORE: {message.quality_score}/100
FEEDBACK: {', '.join(message.quality_suggestions or [])}

Please provide:
1. An improved version of the message (under 150 words)
2. Specific changes you made and why
3. Expected impact on response rate"""

    result = career_coaching_sync(
        question=prompt,
        user_context=None,
    )

    if not result["success"]:
        return (
            jsonify(
                {
                    "error": result.get("error", "Failed to generate improvements"),
                }
            ),
            500,
        )

    return (
        jsonify(
            {
                "message_id": str(message.id),
                "original_score": message.quality_score,
                "improvements": result["response"],
                "provider": result["provider"],
            }
        ),
        200,
    )
