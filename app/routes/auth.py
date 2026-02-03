"""
Authentication Routes

Handles user registration, login, token refresh, logout, and password management.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)

from app.extensions import db
from app.models.user import User
from app.utils.validators import validate_email, validate_password, ValidationError

auth_bp = Blueprint('auth', __name__)

# In-memory token blocklist (replace with Redis in production)
_token_blocklist = set()


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.

    Request Body:
        email: User's email address (required)
        password: User's password (required, min 8 chars)
        first_name: User's first name (optional)
        last_name: User's last name (optional)

    Returns:
        201: User created successfully with tokens
        400: Validation error
        409: Email already exists
    """
    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'error': 'invalid_request',
            'message': 'Request body is required'
        }), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    first_name = data.get('first_name', '').strip() or None
    last_name = data.get('last_name', '').strip() or None

    # Validate email
    try:
        validate_email(email)
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'validation_error',
            'message': str(e)
        }), 400

    # Validate password
    try:
        validate_password(password)
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'validation_error',
            'message': str(e)
        }), 400

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({
            'success': False,
            'error': 'email_exists',
            'message': 'An account with this email already exists'
        }), 409

    # Create user
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'success': True,
        'message': 'User registered successfully',
        'data': {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return tokens.

    Request Body:
        email: User's email address (required)
        password: User's password (required)

    Returns:
        200: Login successful with tokens
        400: Validation error
        401: Invalid credentials
    """
    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'error': 'invalid_request',
            'message': 'Request body is required'
        }), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({
            'success': False,
            'error': 'validation_error',
            'message': 'Email and password are required'
        }), 400

    # Find user
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({
            'success': False,
            'error': 'invalid_credentials',
            'message': 'Invalid email or password'
        }), 401

    if not user.is_active:
        return jsonify({
            'success': False,
            'error': 'account_disabled',
            'message': 'This account has been disabled'
        }), 401

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.session.commit()

    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'success': True,
        'message': 'Login successful',
        'data': {
            'user': user.to_dict(include_private=True),
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token.

    Headers:
        Authorization: Bearer <refresh_token>

    Returns:
        200: New access token
        401: Invalid or expired refresh token
    """
    current_user_id = get_jwt_identity()

    # Verify user still exists and is active
    user = User.query.get(current_user_id)
    if not user or not user.is_active:
        return jsonify({
            'success': False,
            'error': 'invalid_user',
            'message': 'User not found or account disabled'
        }), 401

    access_token = create_access_token(identity=current_user_id)

    return jsonify({
        'success': True,
        'data': {
            'access_token': access_token
        }
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user by revoking current token.

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        200: Logout successful
    """
    jti = get_jwt()['jti']
    _token_blocklist.add(jti)

    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user's profile.

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        200: User profile data
        401: Not authenticated
        404: User not found
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({
            'success': False,
            'error': 'user_not_found',
            'message': 'User not found'
        }), 404

    return jsonify({
        'success': True,
        'data': {
            'user': user.to_dict(include_private=True)
        }
    }), 200


@auth_bp.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    """
    Change current user's password.

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        current_password: Current password (required)
        new_password: New password (required, min 8 chars)

    Returns:
        200: Password changed successfully
        400: Validation error
        401: Current password incorrect
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({
            'success': False,
            'error': 'user_not_found',
            'message': 'User not found'
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'error': 'invalid_request',
            'message': 'Request body is required'
        }), 400

    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    # Verify current password
    if not user.check_password(current_password):
        return jsonify({
            'success': False,
            'error': 'invalid_password',
            'message': 'Current password is incorrect'
        }), 401

    # Validate new password
    try:
        validate_password(new_password)
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'validation_error',
            'message': str(e)
        }), 400

    # Update password
    user.set_password(new_password)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Password changed successfully'
    }), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Request password reset email.

    Request Body:
        email: User's email address (required)

    Returns:
        200: Reset email sent (always returns success to prevent email enumeration)
    """
    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'error': 'invalid_request',
            'message': 'Request body is required'
        }), 400

    email = data.get('email', '').strip().lower()

    # Always return success to prevent email enumeration
    # In production, this would send an email if user exists
    user = User.query.filter_by(email=email).first()

    if user:
        # Generate reset token and send email via SendGrid
        import uuid
        reset_token = str(uuid.uuid4())
        user.verification_token = reset_token
        db.session.commit()

        # Send password reset email
        from app.services.email_service import EmailService
        EmailService.send_password_reset_email(user, reset_token)

    return jsonify({
        'success': True,
        'message': 'If an account exists with this email, a password reset link has been sent'
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset password using token from email.

    Request Body:
        token: Reset token from email (required)
        new_password: New password (required, min 8 chars)

    Returns:
        200: Password reset successful
        400: Invalid or expired token
    """
    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'error': 'invalid_request',
            'message': 'Request body is required'
        }), 400

    token = data.get('token', '')
    new_password = data.get('new_password', '')

    if not token:
        return jsonify({
            'success': False,
            'error': 'validation_error',
            'message': 'Reset token is required'
        }), 400

    # Find user with token
    user = User.query.filter_by(verification_token=token).first()

    if not user:
        return jsonify({
            'success': False,
            'error': 'invalid_token',
            'message': 'Invalid or expired reset token'
        }), 400

    # Validate new password
    try:
        validate_password(new_password)
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'validation_error',
            'message': str(e)
        }), 400

    # Update password and clear token
    user.set_password(new_password)
    user.verification_token = None
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Password reset successful. You can now log in with your new password.'
    }), 200


# Token blocklist checker for JWT
def check_if_token_revoked(jwt_header, jwt_payload):
    """Check if token is in blocklist."""
    jti = jwt_payload['jti']
    return jti in _token_blocklist
