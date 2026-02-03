"""
Labor Market Routes

Provides labor market intelligence endpoints.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User
from app.services.labor_market_service import (
    LaborMarketService,
    get_market_overview_sync,
)

labor_market_bp = Blueprint('labor_market', __name__, url_prefix='/api/labor-market')


@labor_market_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_market_overview():
    """
    Get overall labor market overview.

    Returns:
        200: Market overview with key indicators
    """
    overview = get_market_overview_sync()

    return jsonify({
        'success': True,
        'data': overview
    }), 200


@labor_market_bp.route('/shortage', methods=['GET'])
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
    role = request.args.get('role')

    if not role:
        return jsonify({
            'success': False,
            'error': 'validation_error',
            'message': 'Role parameter is required'
        }), 400

    industry = request.args.get('industry')
    location = request.args.get('location')

    shortage = LaborMarketService.calculate_shortage_score(
        role=role,
        industry=industry,
        location=location,
    )

    return jsonify({
        'success': True,
        'data': shortage
    }), 200


@labor_market_bp.route('/salary', methods=['GET'])
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
    role = request.args.get('role')

    if not role:
        return jsonify({
            'success': False,
            'error': 'validation_error',
            'message': 'Role parameter is required'
        }), 400

    experience = request.args.get('experience', 'mid')
    location = request.args.get('location')

    benchmark = LaborMarketService.get_salary_benchmark(
        role=role,
        experience_level=experience,
        location=location,
    )

    return jsonify({
        'success': True,
        'data': benchmark
    }), 200


@labor_market_bp.route('/opportunity', methods=['POST'])
@jwt_required()
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
        return jsonify({
            'success': False,
            'error': 'not_found',
            'message': 'User not found'
        }), 404

    data = request.get_json() or {}

    target_role = data.get('target_role')
    if not target_role:
        # Use user's target roles if available
        if user.target_roles:
            target_role = user.target_roles[0]
        else:
            return jsonify({
                'success': False,
                'error': 'validation_error',
                'message': 'Target role is required'
            }), 400

    # Get skills from request or user profile
    skills = data.get('skills')
    if not skills:
        skills = (user.technical_skills or []) + (user.soft_skills or [])

    target_industry = data.get('target_industry')
    if not target_industry and user.target_industries:
        target_industry = user.target_industries[0]

    opportunity = LaborMarketService.calculate_opportunity_score(
        user_skills=skills,
        target_role=target_role,
        target_industry=target_industry,
    )

    return jsonify({
        'success': True,
        'data': opportunity
    }), 200


@labor_market_bp.route('/outlook/<role>', methods=['GET'])
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

    return jsonify({
        'success': True,
        'data': outlook
    }), 200


@labor_market_bp.route('/industries/trending', methods=['GET'])
@jwt_required()
def get_trending_industries():
    """
    Get list of trending industries by growth rate.

    Returns:
        200: List of trending industries
    """
    sorted_industries = sorted(
        LaborMarketService.INDUSTRY_GROWTH.items(),
        key=lambda x: x[1],
        reverse=True
    )

    industries = [
        {
            'name': name,
            'growth_rate': rate,
            'growth_outlook': LaborMarketService._interpret_growth(rate),
        }
        for name, rate in sorted_industries
    ]

    return jsonify({
        'success': True,
        'data': industries
    }), 200


@labor_market_bp.route('/roles/high-demand', methods=['GET'])
@jwt_required()
def get_high_demand_roles():
    """
    Get list of high-demand roles.

    Returns:
        200: List of high-demand roles with shortage scores
    """
    roles = [
        {
            'role': role,
            'growth_rate': data['growth_rate'],
            'shortage_score': data['shortage_score'],
            'demand_level': LaborMarketService._interpret_demand(data['shortage_score']),
        }
        for role, data in LaborMarketService.HIGH_DEMAND_ROLES.items()
    ]

    # Sort by shortage score
    roles.sort(key=lambda x: x['shortage_score'], reverse=True)

    return jsonify({
        'success': True,
        'data': roles
    }), 200
