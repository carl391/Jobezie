"""
Jobezie API Routes

All route blueprints are defined in separate modules and registered
in the app factory.
"""

from app.routes.auth import auth_bp
from app.routes.resume import resume_bp
from app.routes.recruiter import recruiter_bp
from app.routes.message import message_bp
from app.routes.activity import activity_bp
from app.routes.ai import ai_bp

__all__ = [
    'auth_bp',
    'resume_bp',
    'recruiter_bp',
    'message_bp',
    'activity_bp',
    'ai_bp',
]
