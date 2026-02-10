"""
AI Routes

API endpoints for AI-powered career assistance features.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.services.ai_service import (
    AIService,
    career_coaching_sync,
    evaluate_answer_sync,
    generate_message_sync,
    interview_prep_sync,
    optimize_resume_sync,
)
from app.services.message_service import MessageService
from app.services.resume_service import ResumeService
from app.utils.decorators import feature_limit
from app.utils.validators import validate_text_fields

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
@feature_limit("ai_messages")
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

    # Increment usage counter
    from app.models.user import User

    current_user = User.query.get(user_id)
    if current_user:
        current_user.monthly_message_count += 1
        db.session.commit()

    return jsonify(response_data), 200


@ai_bp.route("/optimize-resume", methods=["POST"])
@jwt_required()
@feature_limit("research")
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

    # Increment usage counter
    from app.models.user import User

    current_user = User.query.get(user_id)
    if current_user:
        current_user.monthly_research_count += 1
        db.session.commit()

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
@feature_limit("coach_daily")
def career_coach():
    """
    Get AI career coaching response with algorithm-first context.

    The career coach receives algorithmic scores as context, implementing
    the algorithm-first principle: scores calculated by algorithm, then
    passed to AI for contextual advice.

    Request body:
        question: Required - User's question
        conversation_id: Optional - Continue existing conversation

    Returns:
        JSON with coaching response
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    # Validate and sanitize text fields
    schema = {
        "question": {"required": True, "max_length": 5000},
    }
    validated, errors = validate_text_fields(data, schema)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    question = validated["question"]

    # Get user context from profile
    from app.models.user import User

    user = User.query.get(user_id)

    user_context = None
    algorithm_context = None

    if user:
        user_context = {
            "current_role": user.current_role,
            "target_roles": user.target_roles or [],
            "industries": user.target_industries or [],
            "experience_level": user.career_stage,
            "location": user.location,
        }

        # Algorithm-first: Fetch computed scores as context for AI
        algorithm_context = _get_algorithm_context(user_id, user)

    # Get conversation history if continuing
    conversation_history = data.get("conversation_history", [])

    result = career_coaching_sync(
        question=question,
        user_context=user_context,
        conversation_history=conversation_history,
        algorithm_context=algorithm_context,
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

    # Increment usage counter
    user = User.query.get(user_id)
    if user:
        user.daily_coach_count += 1
        db.session.commit()

    return (
        jsonify(
            {
                "response": result["response"],
                "provider": result["provider"],
                "algorithm_context": algorithm_context,
            }
        ),
        200,
    )


def _get_algorithm_context(user_id: str, user) -> dict:
    """
    Fetch algorithm-computed scores to provide context for AI coaching.

    This implements the algorithm-first principle: deterministic algorithms
    calculate scores, then AI uses those scores for personalized advice.

    Returns dict with:
        - ats_score: Latest resume ATS score
        - readiness_score: Career readiness score
        - engagement_avg: Average recruiter engagement
        - market_shortage: Shortage scores for target roles
    """
    from app.models.recruiter import Recruiter
    from app.models.resume import Resume
    from app.services.labor_market_service import LaborMarketService
    from app.services.scoring import calculate_career_readiness

    context = {
        "ats_score": None,
        "readiness_score": None,
        "engagement_avg": None,
        "market_shortage": [],
        "skills_gap": None,
    }

    try:
        # Get latest resume ATS score
        latest_resume = (
            Resume.query.filter_by(user_id=user_id, is_master=True)
            .order_by(Resume.updated_at.desc())
            .first()
        )
        if not latest_resume:
            latest_resume = (
                Resume.query.filter_by(user_id=user_id).order_by(Resume.updated_at.desc()).first()
            )
        if latest_resume and latest_resume.ats_total_score:
            context["ats_score"] = {
                "total": latest_resume.ats_total_score,
                "weak_sections": latest_resume.weak_sections or [],
            }

        # Get career readiness score
        readiness = calculate_career_readiness(user_id)
        if readiness:
            context["readiness_score"] = {
                "total": readiness.get("total_score"),
                "components": readiness.get("components", {}),
            }

        # Get average recruiter engagement
        recruiters = Recruiter.query.filter_by(user_id=user_id).all()
        if recruiters:
            engagement_scores = [r.engagement_score for r in recruiters if r.engagement_score]
            if engagement_scores:
                context["engagement_avg"] = {
                    "average": sum(engagement_scores) // len(engagement_scores),
                    "count": len(recruiters),
                    "active": len(
                        [r for r in recruiters if r.pipeline_stage not in ["archived", "rejected"]]
                    ),
                }

        # Get market shortage for target roles
        target_roles = user.target_roles or []
        target_industries = user.target_industries or []
        primary_industry = target_industries[0] if target_industries else None

        for role in target_roles[:3]:  # Limit to top 3 roles
            shortage = LaborMarketService.calculate_shortage_score(
                role=role,
                industry=primary_industry,
            )
            context["market_shortage"].append(
                {
                    "role": role,
                    "score": shortage["total_score"],
                    "interpretation": shortage["interpretation"],
                }
            )

        # Get skills gap for primary target role (uses O*NET skills, abilities, knowledge)
        if target_roles:
            user_skills = (user.technical_skills or []) + (user.soft_skills or [])
            skills_gap = LaborMarketService.get_skills_gap_by_category(
                user_skills=user_skills,
                target_role=target_roles[0],
            )
            if "error" not in skills_gap:
                context["skills_gap"] = skills_gap

    except Exception:
        # Don't fail the request if context gathering fails
        pass

    return context


@ai_bp.route("/interview-prep", methods=["POST"])
@jwt_required()
@feature_limit("interview_prep")
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

    action = data.get("action", "generate")

    if action == "evaluate":
        # Evaluate a user's answer to an interview question
        eval_schema = {
            "job_title": {"required": True, "max_length": 200},
            "interview_type": {"required": False, "max_length": 50},
            "question": {"required": True, "max_length": 2000},
            "user_answer": {"required": True, "max_length": 5000},
        }
        validated, errors = validate_text_fields(data, eval_schema)
        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        result = evaluate_answer_sync(
            job_title=validated["job_title"],
            interview_type=validated.get("interview_type") or "behavioral",
            question=validated["question"],
            user_answer=validated["user_answer"],
        )

        if not result["success"]:
            return jsonify({"error": result.get("error", "Failed to evaluate answer")}), 500

        return (
            jsonify(
                {
                    "evaluation": result["evaluation"],
                    "provider": result["provider"],
                }
            ),
            200,
        )

    # Default: generate interview prep materials
    schema = {
        "job_title": {"required": True, "max_length": 200},
        "company": {"required": False, "max_length": 200},
        "interview_type": {"required": False, "max_length": 50},
    }
    validated, errors = validate_text_fields(data, schema)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    job_title = validated["job_title"]

    # Get user experience from resume if provided
    user_experience = None
    if data.get("resume_id"):
        resume = ResumeService.get_resume(data["resume_id"], user_id)
        if resume and resume.parsed_sections:
            experience = resume.parsed_sections.get("experience", "")
            user_experience = experience[:2000]  # Truncate

    result = interview_prep_sync(
        job_title=job_title,
        company=validated.get("company"),
        interview_type=validated.get("interview_type") or "behavioral",
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

    # Increment usage counter
    from app.models.user import User

    current_user = User.query.get(user_id)
    if current_user:
        current_user.monthly_interview_prep_count += 1
        db.session.commit()

    return (
        jsonify(
            {
                "job_title": job_title,
                "company": validated.get("company"),
                "interview_type": validated.get("interview_type") or "behavioral",
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
