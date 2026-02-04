"""
Jobezie Flask Extensions

Centralized extension initialization to avoid circular imports.
Extensions are initialized without app context and bound later in the app factory.
"""

from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Database
db = SQLAlchemy()

# JWT Authentication
jwt = JWTManager()

# Database Migrations
migrate = Migrate()

# CORS
cors = CORS()

# Caching
cache = Cache()

# Rate Limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["100 per minute"])


def init_extensions(app):
    """Initialize all Flask extensions with the app instance."""
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})
    cache.init_app(app)
    limiter.init_app(app)

    # Configure JWT callbacks
    _configure_jwt_callbacks(app)


def _configure_jwt_callbacks(app):
    """Configure JWT error handlers and callbacks."""

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {
            "success": False,
            "error": "token_expired",
            "message": "The token has expired. Please log in again.",
        }, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {
            "success": False,
            "error": "invalid_token",
            "message": "Invalid token. Please log in again.",
        }, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {
            "success": False,
            "error": "authorization_required",
            "message": "Authorization token is missing.",
        }, 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {
            "success": False,
            "error": "token_revoked",
            "message": "The token has been revoked.",
        }, 401
