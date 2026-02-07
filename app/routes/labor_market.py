"""
Labor Market Routes

Provides labor market intelligence endpoints.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models.user import User
from app.services.labor_market_service import (
    LaborMarketService,
    get_market_overview_sync,
)
from app.utils.decorators import feature_limit

labor_market_bp = Blueprint("labor_market", __name__, url_prefix="/api/labor-market")


@labor_market_bp.route("/overview", methods=["GET"])
@jwt_required()
def get_market_overview():
    """
    Get overall labor market overview.

    Returns:
        200: Market overview with key indicators
    """
    overview = get_market_overview_sync()

    return jsonify({"success": True, "data": overview}), 200


@labor_market_bp.route("/shortage", methods=["GET"])
@jwt_required()
def get_shortage_score():
    """
    Get labor shortage score for a role.

    Query Parameters:
        role: Target job role (required)
        industry: Industry sector (optional)
        location: Geographic location (optional)

    Returns:
        200: Shortage score with breakdown
        400: Missing role parameter
    """
    role = request.args.get("role")

    if not role:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "validation_error",
                    "message": "Role parameter is required",
                }
            ),
            400,
        )

    industry = request.args.get("industry")
    location = request.args.get("location")

    shortage = LaborMarketService.calculate_shortage_score(
        role=role,
        industry=industry,
        location=location,
    )

    return jsonify({"success": True, "data": shortage}), 200


@labor_market_bp.route("/salary", methods=["GET"])
@jwt_required()
def get_salary_benchmark():
    """
    Get salary benchmark for a role.

    Query Parameters:
        role: Job role/title (required)
        experience: Experience level - entry, mid, senior, executive (optional)
        location: Geographic location (optional)

    Returns:
        200: Salary benchmark with range
        400: Missing role parameter
    """
    role = request.args.get("role")

    if not role:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "validation_error",
                    "message": "Role parameter is required",
                }
            ),
            400,
        )

    experience = request.args.get("experience", "mid")
    location = request.args.get("location")

    benchmark = LaborMarketService.get_salary_benchmark(
        role=role,
        experience_level=experience,
        location=location,
    )

    return jsonify({"success": True, "data": benchmark}), 200


@labor_market_bp.route("/opportunity", methods=["POST"])
@jwt_required()
@feature_limit("research")
def calculate_opportunity():
    """
    Calculate opportunity score based on user skills and target role.

    Request Body:
        target_role: Target job role (required)
        target_industry: Target industry (optional)
        skills: List of user skills (optional, uses profile if not provided)

    Returns:
        200: Opportunity score with recommendations
        400: Missing required fields
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return (
            jsonify({"success": False, "error": "not_found", "message": "User not found"}),
            404,
        )

    data = request.get_json() or {}

    target_role = data.get("target_role")
    if not target_role:
        # Use user's target roles if available
        if user.target_roles:
            target_role = user.target_roles[0]
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "validation_error",
                        "message": "Target role is required",
                    }
                ),
                400,
            )

    # Get skills from request or user profile
    skills = data.get("skills")
    if not skills:
        skills = (user.technical_skills or []) + (user.soft_skills or [])

    target_industry = data.get("target_industry")
    if not target_industry and user.target_industries:
        target_industry = user.target_industries[0]

    opportunity = LaborMarketService.calculate_opportunity_score(
        user_skills=skills,
        target_role=target_role,
        target_industry=target_industry,
    )

    # Increment usage counter
    user.monthly_research_count += 1
    db.session.commit()

    return jsonify({"success": True, "data": opportunity}), 200


@labor_market_bp.route("/outlook/<role>", methods=["GET"])
@jwt_required()
def get_job_outlook(role: str):
    """
    Get detailed job outlook for a role.

    Path Parameters:
        role: Job role/title

    Returns:
        200: Job outlook with projections
    """
    outlook = LaborMarketService.get_job_outlook(role)

    return jsonify({"success": True, "data": outlook}), 200


@labor_market_bp.route("/industries/trending", methods=["GET"])
@jwt_required()
def get_trending_industries():
    """
    Get list of trending industries by growth rate.

    Returns:
        200: List of trending industries
    """
    sorted_industries = sorted(
        LaborMarketService.INDUSTRY_GROWTH.items(), key=lambda x: x[1], reverse=True
    )

    industries = [
        {
            "name": name,
            "growth_rate": rate,
            "growth_outlook": LaborMarketService._interpret_growth(rate),
        }
        for name, rate in sorted_industries
    ]

    return jsonify({"success": True, "data": industries}), 200


@labor_market_bp.route("/roles/high-demand", methods=["GET"])
@jwt_required()
def get_high_demand_roles():
    """
    Get list of high-demand roles.

    Returns:
        200: List of high-demand roles with shortage scores
    """
    roles = [
        {
            "role": role,
            "growth_rate": data["growth_rate"],
            "shortage_score": data["shortage_score"],
            "demand_level": LaborMarketService._interpret_demand(data["shortage_score"]),
        }
        for role, data in LaborMarketService.HIGH_DEMAND_ROLES.items()
    ]

    # Sort by shortage score
    roles.sort(key=lambda x: x["shortage_score"], reverse=True)

    return jsonify({"success": True, "data": roles}), 200


@labor_market_bp.route("/skills-map", methods=["GET"])
@jwt_required()
def get_skills_map():
    """
    Get user's skills organized by O*NET category.

    Returns user's skills matched against O*NET database, organized by
    category (skills, abilities, knowledge) with coverage statistics.

    Returns:
        200: Skills map with matched items and coverage by category
    """
    from app.models.labor_market import Skill

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return (
            jsonify({"success": False, "error": "not_found", "message": "User not found"}),
            404,
        )

    user_skills = (user.technical_skills or []) + (user.soft_skills or [])
    user_skills_lower = {s.lower() for s in user_skills}

    result = {
        "skills": [],
        "abilities": [],
        "knowledge": [],
        "total_matched": 0,
        "coverage_by_category": {},
    }

    for category in ["skills", "abilities", "knowledge"]:
        all_in_category = Skill.query.filter_by(category=category).all()
        matched = [s.name for s in all_in_category if s.name.lower() in user_skills_lower]

        result[category] = matched
        result["total_matched"] += len(matched)
        result["coverage_by_category"][category] = {
            "matched": len(matched),
            "total": len(all_in_category),
            "pct": int(len(matched) / max(len(all_in_category), 1) * 100),
        }

    return jsonify({"success": True, "data": result}), 200


@labor_market_bp.route("/occupations", methods=["GET"])
@jwt_required()
def search_occupations():
    """
    Search O*NET occupations by title.

    Query Parameters:
        q: Search query (required, min 2 chars)
        limit: Max results (default 10)

    Returns:
        200: List of matching occupations with shortage preview
    """
    from app.models.labor_market import Occupation

    query = request.args.get("q", "").strip()
    limit = min(int(request.args.get("limit", 10)), 50)

    if len(query) < 2:
        return jsonify({"success": True, "data": []}), 200

    occupations = (
        Occupation.query.filter(Occupation.title.ilike(f"%{query}%"))
        .order_by(Occupation.bright_outlook.desc(), Occupation.title)
        .limit(limit)
        .all()
    )

    results = []
    for occ in occupations:
        item = occ.to_dict()
        # Add a quick shortage preview
        shortage = LaborMarketService.calculate_shortage_score(occ.title)
        item["shortage_score"] = shortage["total_score"]
        item["demand_level"] = shortage["interpretation"]
        results.append(item)

    return jsonify({"success": True, "data": results}), 200


@labor_market_bp.route("/skills", methods=["GET"])
@jwt_required()
def search_skills():
    """
    Search O*NET skills by name, optionally filtered by category.

    Query Parameters:
        q: Search query (required, min 2 chars)
        category: Filter by category (skills, abilities, knowledge)
        limit: Max results (default 10)

    Returns:
        200: List of matching skills grouped by category
    """
    from app.models.labor_market import Skill

    query = request.args.get("q", "").strip()
    category = request.args.get("category")
    limit = min(int(request.args.get("limit", 20)), 50)

    if len(query) < 2:
        return jsonify({"success": True, "data": []}), 200

    q = Skill.query.filter(Skill.name.ilike(f"%{query}%"))

    if category and category in ("skills", "abilities", "knowledge"):
        q = q.filter(Skill.category == category)

    skills = q.order_by(Skill.category, Skill.name).limit(limit).all()

    results = [s.to_dict() for s in skills]

    return jsonify({"success": True, "data": results}), 200


@labor_market_bp.route("/skills-gap", methods=["POST"])
@jwt_required()
@feature_limit("skills_gap")
def get_skills_gap():
    """
    Get skills gap analysis for a target role.

    Request Body:
        target_role: Target job role (required)
        skills: List of user skills (optional, uses profile if not provided)

    Returns:
        200: Skills gap breakdown by category (skills, abilities, knowledge)
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return (
            jsonify({"success": False, "error": "not_found", "message": "User not found"}),
            404,
        )

    data = request.get_json() or {}

    target_role = data.get("target_role")
    if not target_role:
        if user.target_roles:
            target_role = user.target_roles[0]
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "validation_error",
                        "message": "Target role is required",
                    }
                ),
                400,
            )

    # Get skills from request or user profile
    skills = data.get("skills")
    if not skills:
        skills = (user.technical_skills or []) + (user.soft_skills or [])

    gap_analysis = LaborMarketService.get_skills_gap_by_category(
        user_skills=skills,
        target_role=target_role,
    )

    if "error" in gap_analysis:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "not_found",
                    "message": gap_analysis["error"],
                }
            ),
            404,
        )

    # Increment usage counter (skills_gap shares with research)
    user.monthly_research_count += 1
    db.session.commit()

    return jsonify({"success": True, "data": gap_analysis}), 200
