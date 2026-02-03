"""
LinkedIn Optimizer Routes

Provides LinkedIn profile optimization endpoints.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User
from app.services.linkedin_service import LinkedInService

linkedin_bp = Blueprint('linkedin', __name__, url_prefix='/api/linkedin')


@linkedin_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_profile():
    """
    Analyze LinkedIn profile and provide optimization score.

    Request Body:
        headline: Profile headline (optional)
        summary: About section (optional)
        experience: List of experience entries (optional)
        skills: List of skills (optional)
        education: List of education entries (optional)
        photo: Boolean if has photo (optional)
        location: Location string (optional)
        industry: Industry string (optional)

    Returns:
        200: Analysis with scores and recommendations
    """
    data = request.get_json() or {}

    analysis = LinkedInService.analyze_profile(data)

    return jsonify({
        'success': True,
        'data': analysis
    }), 200


@linkedin_bp.route('/headline/generate', methods=['POST'])
@jwt_required()
def generate_headline():
    """
    Generate optimized LinkedIn headline options.

    Request Body:
        current_role: Current job title (required)
        target_role: Target job title (optional)
        industry: Industry sector (optional)
        key_skills: List of skills to highlight (optional)
        achievements: List of achievements to mention (optional)

    Returns:
        200: Multiple headline options with scores
        400: Missing current_role
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    data = request.get_json() or {}

    current_role = data.get('current_role')
    if not current_role:
        # Use user's current role if available
        if user and user.current_role:
            current_role = user.current_role
        else:
            return jsonify({
                'success': False,
                'error': 'validation_error',
                'message': 'Current role is required'
            }), 400

    # Get optional fields from request or user profile
    target_role = data.get('target_role')
    if not target_role and user and user.target_roles:
        target_role = user.target_roles[0]

    industry = data.get('industry')
    if not industry and user and user.target_industries:
        industry = user.target_industries[0]

    key_skills = data.get('key_skills')
    if not key_skills and user:
        key_skills = (user.technical_skills or [])[:3]

    achievements = data.get('achievements', [])

    headlines = LinkedInService.generate_headline(
        current_role=current_role,
        target_role=target_role,
        industry=industry,
        key_skills=key_skills,
        achievements=achievements,
    )

    return jsonify({
        'success': True,
        'data': headlines
    }), 200


@linkedin_bp.route('/summary/generate', methods=['POST'])
@jwt_required()
def generate_summary():
    """
    Generate optimized LinkedIn summary/about section.

    Request Body:
        current_role: Current job title (required)
        years_experience: Years of experience (required)
        industry: Industry sector (required)
        key_skills: List of skills (required)
        achievements: List of achievements (required)
        career_goals: Career objectives (optional)

    Returns:
        200: Generated summary with structure
        400: Missing required fields
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    data = request.get_json() or {}

    # Get required fields
    current_role = data.get('current_role')
    if not current_role and user and user.current_role:
        current_role = user.current_role

    years_experience = data.get('years_experience')
    if years_experience is None and user and user.years_experience:
        years_experience = user.years_experience

    industry = data.get('industry')
    if not industry and user and user.target_industries:
        industry = user.target_industries[0]

    key_skills = data.get('key_skills')
    if not key_skills and user:
        key_skills = (user.technical_skills or [])[:5]

    achievements = data.get('achievements', [])

    # Validate required fields
    if not current_role:
        return jsonify({
            'success': False,
            'error': 'validation_error',
            'message': 'Current role is required'
        }), 400

    if years_experience is None:
        return jsonify({
            'success': False,
            'error': 'validation_error',
            'message': 'Years of experience is required'
        }), 400

    if not industry:
        return jsonify({
            'success': False,
            'error': 'validation_error',
            'message': 'Industry is required'
        }), 400

    if not key_skills:
        return jsonify({
            'success': False,
            'error': 'validation_error',
            'message': 'Key skills are required'
        }), 400

    summary = LinkedInService.generate_summary(
        current_role=current_role,
        years_experience=years_experience,
        industry=industry,
        key_skills=key_skills,
        achievements=achievements,
        career_goals=data.get('career_goals'),
    )

    return jsonify({
        'success': True,
        'data': summary
    }), 200


@linkedin_bp.route('/experience/optimize', methods=['POST'])
@jwt_required()
def optimize_experience():
    """
    Optimize a single experience entry.

    Request Body:
        title: Job title (required)
        company: Company name (required)
        description: Current description (required)
        target_keywords: Keywords to incorporate (optional)

    Returns:
        200: Optimized experience with suggestions
        400: Missing required fields
    """
    data = request.get_json() or {}

    if not data.get('title') or not data.get('company'):
        return jsonify({
            'success': False,
            'error': 'validation_error',
            'message': 'Title and company are required'
        }), 400

    if not data.get('description'):
        return jsonify({
            'success': False,
            'error': 'validation_error',
            'message': 'Description is required for optimization'
        }), 400

    optimized = LinkedInService.optimize_experience(
        experience_entry={
            'title': data['title'],
            'company': data['company'],
            'description': data['description'],
        },
        target_keywords=data.get('target_keywords'),
    )

    return jsonify({
        'success': True,
        'data': optimized
    }), 200


@linkedin_bp.route('/visibility', methods=['POST'])
@jwt_required()
def calculate_visibility():
    """
    Calculate LinkedIn visibility/searchability score.

    Request Body:
        headline: Profile headline (optional)
        summary: About section (optional)
        experience: List of experience entries (optional)
        skills: List of skills (optional)
        education: List of education entries (optional)
        photo: Boolean if has photo (optional)
        location: Location string (optional)
        industry: Industry string (optional)

    Returns:
        200: Visibility score with improvement suggestions
    """
    data = request.get_json() or {}

    visibility = LinkedInService.calculate_visibility_score(data)

    return jsonify({
        'success': True,
        'data': visibility
    }), 200


@linkedin_bp.route('/keywords/<industry>', methods=['GET'])
@jwt_required()
def get_industry_keywords(industry: str):
    """
    Get recommended keywords for an industry.

    Path Parameters:
        industry: Industry sector

    Returns:
        200: List of recommended keywords
    """
    keywords = LinkedInService.INDUSTRY_KEYWORDS.get(
        industry.lower(),
        []
    )

    if not keywords:
        # Return generic keywords if industry not found
        keywords = ['professional', 'experienced', 'dedicated', 'results-driven']

    return jsonify({
        'success': True,
        'data': {
            'industry': industry,
            'keywords': keywords,
            'usage_tips': [
                'Include 3-5 keywords in your headline',
                'Weave keywords naturally into your summary',
                'Use keywords in experience descriptions',
                'Add relevant keywords as skills',
            ],
        }
    }), 200


@linkedin_bp.route('/tips', methods=['GET'])
@jwt_required()
def get_optimization_tips():
    """
    Get general LinkedIn optimization tips.

    Returns:
        200: Optimization tips and best practices
    """
    tips = {
        'headline': [
            'Use all 220 characters',
            'Include your target role for searches',
            'Add 2-3 industry keywords',
            'Mention your value proposition',
        ],
        'summary': [
            'Start with a compelling hook',
            'Keep paragraphs short (2-3 sentences)',
            'Include quantified achievements',
            'End with a call-to-action',
            'Aim for 200-300 words',
        ],
        'experience': [
            'Start bullets with action verbs',
            'Include specific metrics (%, $, numbers)',
            'Add 3-5 bullet points per role',
            'Focus on impact, not just duties',
        ],
        'skills': [
            'Add at least 20 relevant skills',
            'Put most important skills first',
            'Request endorsements from colleagues',
            'Include both hard and soft skills',
        ],
        'engagement': [
            'Post industry content weekly',
            'Comment on others\' posts',
            'Share articles with your insights',
            'Congratulate connections on achievements',
        ],
    }

    return jsonify({
        'success': True,
        'data': tips
    }), 200
