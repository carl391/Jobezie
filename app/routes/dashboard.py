"""
Dashboard Routes

Provides dashboard data aggregation and career readiness scoring.
"""

from datetime import datetime, timedelta
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.user import User
from app.models.resume import Resume
from app.models.recruiter import Recruiter, RecruiterStatus
from app.models.message import Message, MessageStatus
from app.models.activity import Activity, PipelineItem
from app.services.scoring.readiness import (
    calculate_career_readiness,
    calculate_profile_completeness,
)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@dashboard_bp.route('', methods=['GET'])
@jwt_required()
def get_dashboard():
    """
    Get aggregated dashboard data for the current user.

    Returns:
        200: Dashboard data with stats, recent activity, and recommendations
        404: User not found
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({
            'success': False,
            'error': 'not_found',
            'message': 'User not found'
        }), 404

    # Get counts
    resume_count = Resume.query.filter_by(
        user_id=user_id,
        is_deleted=False
    ).count()

    master_resume = Resume.query.filter_by(
        user_id=user_id,
        is_master=True,
        is_deleted=False
    ).first()

    recruiter_count = Recruiter.query.filter_by(user_id=user_id).count()

    active_recruiters = Recruiter.query.filter(
        Recruiter.user_id == user_id,
        Recruiter.status.notin_([
            RecruiterStatus.DECLINED.value,
            RecruiterStatus.ACCEPTED.value
        ])
    ).count()

    message_count = Message.query.filter_by(user_id=user_id).count()

    # Messages this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    messages_this_week = Message.query.filter(
        Message.user_id == user_id,
        Message.status == MessageStatus.SENT.value,
        Message.sent_at >= week_ago
    ).count()

    # Response rate calculation
    total_sent = Message.query.filter(
        Message.user_id == user_id,
        Message.status.in_([
            MessageStatus.SENT.value,
            MessageStatus.OPENED.value,
            MessageStatus.RESPONDED.value
        ])
    ).count()

    total_responded = Message.query.filter(
        Message.user_id == user_id,
        Message.status == MessageStatus.RESPONDED.value
    ).count()

    response_rate = (total_responded / total_sent) if total_sent > 0 else 0

    # Pipeline summary
    pipeline_summary = _get_pipeline_summary(user_id)

    # Recent activities (last 10)
    recent_activities = Activity.query.filter_by(
        user_id=user_id
    ).order_by(Activity.created_at.desc()).limit(10).all()

    # Recruiters needing follow-up
    follow_up_recruiters = Recruiter.query.filter(
        Recruiter.user_id == user_id,
        Recruiter.has_responded == False,
        Recruiter.status.notin_([
            RecruiterStatus.DECLINED.value,
            RecruiterStatus.ACCEPTED.value
        ]),
        Recruiter.last_contact_date.isnot(None),
        Recruiter.follow_up_count < 3
    ).all()

    needs_follow_up = [r for r in follow_up_recruiters if r.needs_follow_up]

    # Calculate career readiness score
    profile_completeness = calculate_profile_completeness(user.to_dict(include_private=True))

    readiness = calculate_career_readiness(
        profile_completeness=profile_completeness,
        resume_ats_score=master_resume.ats_total_score if master_resume else None,
        has_resume=resume_count > 0,
        active_recruiters=active_recruiters,
        messages_this_week=messages_this_week,
        response_rate=response_rate,
        career_stage=user.career_stage or 'mid_level',
    )

    return jsonify({
        'success': True,
        'data': {
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.full_name,
                'subscription_tier': user.subscription_tier,
                'onboarding_completed': user.onboarding_completed,
            },
            'stats': {
                'resumes': resume_count,
                'recruiters': recruiter_count,
                'active_recruiters': active_recruiters,
                'messages': message_count,
                'messages_this_week': messages_this_week,
                'response_rate': round(response_rate * 100, 1),
            },
            'master_resume': master_resume.to_dict() if master_resume else None,
            'career_readiness': readiness,
            'pipeline_summary': pipeline_summary,
            'recent_activities': [a.to_dict() for a in recent_activities],
            'follow_up_needed': [
                {
                    'id': str(r.id),
                    'full_name': r.full_name,
                    'company': r.company,
                    'days_since_contact': r.days_since_contact,
                    'follow_up_count': r.follow_up_count,
                }
                for r in needs_follow_up[:5]
            ],
            'usage': {
                'recruiters': {
                    'used': user.monthly_recruiter_count,
                    'limit': user.tier_limits.get('recruiters', 5),
                },
                'messages': {
                    'used': user.monthly_message_count,
                    'limit': user.tier_limits.get('ai_messages', 10),
                },
                'research': {
                    'used': user.monthly_research_count,
                    'limit': user.tier_limits.get('research', 5),
                },
                'tailored_resumes': {
                    'used': user.monthly_tailoring_count,
                    'limit': user.tier_limits.get('tailored_resumes', 2),
                },
            },
        }
    }), 200


@dashboard_bp.route('/readiness', methods=['GET'])
@jwt_required()
def get_career_readiness():
    """
    Get detailed career readiness score and recommendations.

    Returns:
        200: Career readiness score with breakdown and recommendations
        404: User not found
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({
            'success': False,
            'error': 'not_found',
            'message': 'User not found'
        }), 404

    # Get data for readiness calculation
    resume_count = Resume.query.filter_by(
        user_id=user_id,
        is_deleted=False
    ).count()

    master_resume = Resume.query.filter_by(
        user_id=user_id,
        is_master=True,
        is_deleted=False
    ).first()

    active_recruiters = Recruiter.query.filter(
        Recruiter.user_id == user_id,
        Recruiter.status.notin_([
            RecruiterStatus.DECLINED.value,
            RecruiterStatus.ACCEPTED.value
        ])
    ).count()

    # Messages this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    messages_this_week = Message.query.filter(
        Message.user_id == user_id,
        Message.status == MessageStatus.SENT.value,
        Message.sent_at >= week_ago
    ).count()

    # Response rate
    total_sent = Message.query.filter(
        Message.user_id == user_id,
        Message.status.in_([
            MessageStatus.SENT.value,
            MessageStatus.OPENED.value,
            MessageStatus.RESPONDED.value
        ])
    ).count()

    total_responded = Message.query.filter(
        Message.user_id == user_id,
        Message.status == MessageStatus.RESPONDED.value
    ).count()

    response_rate = (total_responded / total_sent) if total_sent > 0 else 0

    # Calculate profile completeness
    profile_completeness = calculate_profile_completeness(user.to_dict(include_private=True))

    # Calculate readiness
    readiness = calculate_career_readiness(
        profile_completeness=profile_completeness,
        resume_ats_score=master_resume.ats_total_score if master_resume else None,
        has_resume=resume_count > 0,
        active_recruiters=active_recruiters,
        messages_this_week=messages_this_week,
        response_rate=response_rate,
        career_stage=user.career_stage or 'mid_level',
    )

    # Add context data
    readiness['context'] = {
        'profile_completeness': round(profile_completeness * 100, 1),
        'resume_ats_score': master_resume.ats_total_score if master_resume else None,
        'has_resume': resume_count > 0,
        'active_recruiters': active_recruiters,
        'messages_this_week': messages_this_week,
        'response_rate': round(response_rate * 100, 1),
        'career_stage': user.career_stage or 'mid_level',
    }

    # Add benchmarks for context
    readiness['benchmarks'] = {
        'optimal_recruiters': 10,
        'weekly_message_target': 5,
        'good_response_rate': 20,
        'good_ats_score': 70,
    }

    return jsonify({
        'success': True,
        'data': readiness
    }), 200


@dashboard_bp.route('/stats/weekly', methods=['GET'])
@jwt_required()
def get_weekly_stats():
    """
    Get weekly statistics for the user.

    Returns:
        200: Weekly stats with day-by-day breakdown
    """
    user_id = get_jwt_identity()

    # Get stats for each day of the past week
    daily_stats = []
    for i in range(7):
        day_start = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=i)
        day_end = day_start + timedelta(days=1)

        messages_sent = Message.query.filter(
            Message.user_id == user_id,
            Message.sent_at >= day_start,
            Message.sent_at < day_end
        ).count()

        responses_received = Message.query.filter(
            Message.user_id == user_id,
            Message.responded_at >= day_start,
            Message.responded_at < day_end
        ).count()

        recruiters_added = Recruiter.query.filter(
            Recruiter.user_id == user_id,
            Recruiter.created_at >= day_start,
            Recruiter.created_at < day_end
        ).count()

        activities = Activity.query.filter(
            Activity.user_id == user_id,
            Activity.created_at >= day_start,
            Activity.created_at < day_end
        ).count()

        daily_stats.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'day_name': day_start.strftime('%A'),
            'messages_sent': messages_sent,
            'responses_received': responses_received,
            'recruiters_added': recruiters_added,
            'activities': activities,
        })

    # Reverse to show oldest first
    daily_stats.reverse()

    # Calculate totals
    totals = {
        'messages_sent': sum(d['messages_sent'] for d in daily_stats),
        'responses_received': sum(d['responses_received'] for d in daily_stats),
        'recruiters_added': sum(d['recruiters_added'] for d in daily_stats),
        'activities': sum(d['activities'] for d in daily_stats),
    }

    return jsonify({
        'success': True,
        'data': {
            'daily': daily_stats,
            'totals': totals,
        }
    }), 200


def _get_pipeline_summary(user_id: str) -> dict:
    """Get summary of recruiters by pipeline stage."""
    stages = [
        RecruiterStatus.NEW.value,
        RecruiterStatus.RESEARCHING.value,
        RecruiterStatus.CONTACTED.value,
        RecruiterStatus.RESPONDED.value,
        RecruiterStatus.INTERVIEWING.value,
        RecruiterStatus.OFFER.value,
        RecruiterStatus.ACCEPTED.value,
        RecruiterStatus.DECLINED.value,
    ]

    summary = {}
    for stage in stages:
        count = Recruiter.query.filter_by(
            user_id=user_id,
            status=stage
        ).count()
        summary[stage] = count

    return summary
