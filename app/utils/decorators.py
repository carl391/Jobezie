"""
Custom Decorators

Provides decorators for route protection, subscription checking,
and other common patterns.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from app.models.user import User, SubscriptionTier


def admin_required(fn):
    """
    Decorator to require admin privileges.

    Usage:
        @app.route('/admin/users')
        @jwt_required()
        @admin_required
        def admin_users():
            ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({
                'success': False,
                'error': 'user_not_found',
                'message': 'User not found'
            }), 404

        # Check if user has admin flag (you'd add this field to User model)
        if not getattr(user, 'is_admin', False):
            return jsonify({
                'success': False,
                'error': 'forbidden',
                'message': 'Admin privileges required'
            }), 403

        return fn(*args, **kwargs)

    return wrapper


def subscription_required(*allowed_tiers):
    """
    Decorator to require specific subscription tier(s).

    Usage:
        @app.route('/premium/feature')
        @jwt_required()
        @subscription_required(SubscriptionTier.PRO, SubscriptionTier.EXPERT)
        def premium_feature():
            ...

    Args:
        allowed_tiers: SubscriptionTier values that can access this route
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return jsonify({
                    'success': False,
                    'error': 'user_not_found',
                    'message': 'User not found'
                }), 404

            # Convert string tiers to enum values for comparison
            tier_values = [t.value if isinstance(t, SubscriptionTier) else t for t in allowed_tiers]

            if user.subscription_tier not in tier_values:
                return jsonify({
                    'success': False,
                    'error': 'subscription_required',
                    'message': f'This feature requires a {" or ".join(tier_values)} subscription',
                    'current_tier': user.subscription_tier,
                    'required_tiers': tier_values
                }), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def feature_limit(feature_name: str, count: int = 1):
    """
    Decorator to check and enforce feature usage limits.

    Usage:
        @app.route('/api/messages/generate', methods=['POST'])
        @jwt_required()
        @feature_limit('ai_messages')
        def generate_message():
            ...

    Args:
        feature_name: Name of the feature to check (maps to tier_limits)
        count: How many uses this action consumes (default 1)
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return jsonify({
                    'success': False,
                    'error': 'user_not_found',
                    'message': 'User not found'
                }), 404

            if not user.can_use_feature(feature_name, count):
                limits = user.tier_limits
                return jsonify({
                    'success': False,
                    'error': 'limit_exceeded',
                    'message': f'You have reached your {feature_name} limit for this period',
                    'limit': limits.get(feature_name, 0),
                    'current_tier': user.subscription_tier,
                    'upgrade_url': '/api/subscriptions/checkout'
                }), 429

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def get_current_user():
    """
    Helper to get the current authenticated user.

    Returns:
        User object or None if not authenticated
    """
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        return User.query.get(current_user_id)
    except Exception:
        return None


def verified_email_required(fn):
    """
    Decorator to require verified email address.

    Usage:
        @app.route('/api/sensitive/action')
        @jwt_required()
        @verified_email_required
        def sensitive_action():
            ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({
                'success': False,
                'error': 'user_not_found',
                'message': 'User not found'
            }), 404

        if not user.email_verified:
            return jsonify({
                'success': False,
                'error': 'email_not_verified',
                'message': 'Please verify your email address to access this feature'
            }), 403

        return fn(*args, **kwargs)

    return wrapper


def onboarding_completed_required(fn):
    """
    Decorator to require completed onboarding.

    Usage:
        @app.route('/api/dashboard')
        @jwt_required()
        @onboarding_completed_required
        def dashboard():
            ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({
                'success': False,
                'error': 'user_not_found',
                'message': 'User not found'
            }), 404

        if not user.onboarding_completed:
            return jsonify({
                'success': False,
                'error': 'onboarding_incomplete',
                'message': 'Please complete the onboarding process',
                'onboarding_step': user.onboarding_step
            }), 403

        return fn(*args, **kwargs)

    return wrapper
