"""
Jobezie Flask Application Factory

Creates and configures the Flask application instance.
"""

from flask import Flask, jsonify

from app.config import config, get_config
from app.extensions import db, init_extensions, limiter


def create_app(config_name=None):
    """
    Application factory for creating Flask app instances.

    Args:
        config_name: Configuration to use ('development', 'testing', 'production')
                    If None, uses FLASK_ENV environment variable.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        app_config = get_config()
    else:
        app_config = config.get(config_name, config["default"])

    app.config.from_object(app_config)

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    # Register response wrapper for consistent API format
    _register_response_wrapper(app)

    # Register shell context
    _register_shell_context(app)

    # Register CLI commands
    from app.cli import register_commands
    register_commands(app)

    # Auto-seed O*NET data if tables are empty (runs once at startup)
    _auto_seed_onet(app)

    # Health check endpoint
    @app.route("/health")
    def health_check():
        status = {"status": "healthy", "service": "jobezie-api"}
        try:
            db.session.execute(db.text("SELECT 1"))
            status["database"] = "connected"
        except Exception:
            status["status"] = "degraded"
            status["database"] = "disconnected"
        return jsonify(status), 200 if status["status"] == "healthy" else 503

    # API documentation endpoint (rate limited, environment-aware)
    @app.route("/")
    @limiter.limit("10 per minute")
    def api_docs():
        # Minimal info in production
        if not app.config.get("DEBUG", False):
            return jsonify({
                "service": "Jobezie API",
                "version": "2.0.0",
                "status": "online",
                "health": "/health",
                "documentation": "https://github.com/carl391/Jobezie"
            })

        # Full documentation in development only
        return jsonify({
            "service": "Jobezie API",
            "version": "2.0.0",
            "description": "AI-powered career assistant API",
            "environment": "development",
            "health": "/health",
            "endpoints": {
                "auth": {
                    "base": "/api/auth",
                    "routes": {
                        "POST /register": "Create new user account",
                        "POST /login": "Authenticate and get tokens",
                        "POST /logout": "Invalidate current token",
                        "POST /refresh": "Refresh access token",
                        "POST /password-reset-request": "Request password reset",
                        "POST /password-reset": "Reset password with token"
                    }
                },
                "resumes": {
                    "base": "/api/resumes",
                    "routes": {
                        "GET /": "List user's resumes",
                        "POST /": "Create new resume",
                        "GET /<id>": "Get resume details",
                        "PUT /<id>": "Update resume",
                        "DELETE /<id>": "Delete resume",
                        "POST /<id>/analyze": "Get ATS score analysis",
                        "POST /<id>/tailor": "Tailor resume for job description"
                    }
                },
                "recruiters": {
                    "base": "/api/recruiters",
                    "routes": {
                        "GET /": "List recruiters (Kanban board)",
                        "POST /": "Add new recruiter",
                        "GET /<id>": "Get recruiter details",
                        "PUT /<id>": "Update recruiter",
                        "DELETE /<id>": "Delete recruiter",
                        "POST /<id>/notes": "Add note to recruiter",
                        "PUT /<id>/stage": "Update pipeline stage"
                    }
                },
                "messages": {
                    "base": "/api/messages",
                    "routes": {
                        "GET /": "List messages",
                        "POST /": "Create message",
                        "GET /<id>": "Get message details",
                        "POST /generate": "AI-generate outreach message"
                    }
                },
                "activities": {
                    "base": "/api/activities",
                    "routes": {
                        "GET /": "List activities timeline",
                        "POST /": "Log new activity",
                        "GET /pipeline": "Get pipeline overview"
                    }
                },
                "dashboard": {
                    "base": "/api/dashboard",
                    "routes": {
                        "GET /stats": "Get dashboard statistics",
                        "GET /readiness": "Get career readiness score",
                        "GET /follow-ups": "Get recommended follow-ups"
                    }
                },
                "ai": {
                    "base": "/api/ai",
                    "routes": {
                        "POST /generate-message": "Generate outreach message",
                        "POST /optimize-resume": "Get resume optimization suggestions",
                        "POST /career-coach": "Get career coaching advice"
                    }
                }
            },
            "authentication": "Bearer token (JWT) required for most endpoints",
            "rate_limits": "100 requests/minute per IP",
            "documentation": "https://github.com/carl391/Jobezie"
        })

    return app


def _register_response_wrapper(app):
    """Wrap all API JSON responses in standardized {success, data} format."""
    import json as _json

    @app.after_request
    def wrap_json_response(response):
        # Only wrap JSON responses for /api/ routes
        if not response.content_type or 'application/json' not in response.content_type:
            return response

        # Skip non-API routes (health check, root docs)
        from flask import request as _req
        if not _req.path.startswith('/api/'):
            return response

        try:
            data = response.get_json(silent=True)
        except Exception:
            return response

        if data is None:
            return response

        # Already wrapped — has 'success' key at top level
        if isinstance(data, dict) and 'success' in data:
            return response

        # Wrap based on status code
        if response.status_code < 400:
            wrapped = {"success": True, "data": data}
        else:
            wrapped = {
                "success": False,
                "error": data.get("error", "unknown_error") if isinstance(data, dict) else "error",
                "message": data.get("message", data.get("error", "An error occurred")) if isinstance(data, dict) else str(data),
            }

        response.data = _json.dumps(wrapped)
        response.content_length = len(response.data)
        return response


def _register_blueprints(app):
    """Register Flask blueprints."""
    from app.routes.activity import activity_bp
    from app.routes.ai import ai_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.labor_market import labor_market_bp
    from app.routes.linkedin import linkedin_bp
    from app.routes.message import message_bp
    from app.routes.notification import notification_bp
    from app.routes.recruiter import recruiter_bp
    from app.routes.resume import resume_bp
    from app.routes.subscription import subscription_bp

    # Auth routes
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Phase 2 routes
    app.register_blueprint(resume_bp)  # url_prefix in blueprint
    app.register_blueprint(recruiter_bp)  # url_prefix in blueprint
    app.register_blueprint(message_bp)  # url_prefix in blueprint
    app.register_blueprint(activity_bp)  # url_prefix in blueprint
    app.register_blueprint(ai_bp)  # url_prefix in blueprint
    app.register_blueprint(dashboard_bp)  # url_prefix in blueprint

    # Phase 3 routes
    app.register_blueprint(labor_market_bp)  # url_prefix in blueprint
    app.register_blueprint(linkedin_bp)  # url_prefix in blueprint

    # Phase 4 routes
    app.register_blueprint(subscription_bp)  # url_prefix in blueprint
    app.register_blueprint(notification_bp)  # url_prefix in blueprint


def _register_error_handlers(app):
    """Register custom error handlers."""

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "bad_request",
                    "message": (
                        str(error.description) if hasattr(error, "description") else "Bad request"
                    ),
                }
            ),
            400,
        )

    @app.errorhandler(401)
    def unauthorized(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "unauthorized",
                    "message": "Authentication required",
                }
            ),
            401,
        )

    @app.errorhandler(403)
    def forbidden(error):
        return (
            jsonify({"success": False, "error": "forbidden", "message": "Access denied"}),
            403,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "not_found",
                    "message": "Resource not found",
                }
            ),
            404,
        )

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "validation_error",
                    "message": (
                        str(error.description)
                        if hasattr(error, "description")
                        else "Validation failed"
                    ),
                }
            ),
            422,
        )

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please slow down.",
                }
            ),
            429,
        )

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "internal_error",
                    "message": "An unexpected error occurred",
                }
            ),
            500,
        )


def _register_shell_context(app):
    """Register shell context for flask shell command."""

    @app.shell_context_processor
    def make_shell_context():
        from app.models.activity import Activity, PipelineItem
        from app.models.message import Message
        from app.models.notification import Notification
        from app.models.recruiter import Recruiter, RecruiterNote
        from app.models.resume import Resume, ResumeVersion
        from app.models.user import User

        return {
            "db": db,
            "User": User,
            "Resume": Resume,
            "ResumeVersion": ResumeVersion,
            "Recruiter": Recruiter,
            "RecruiterNote": RecruiterNote,
            "Message": Message,
            "Activity": Activity,
            "PipelineItem": PipelineItem,
            "Notification": Notification,
        }


def _auto_seed_onet(app):
    """Seed O*NET data on first startup if tables are empty."""
    import os
    import logging

    logger = logging.getLogger(__name__)

    with app.app_context():
        try:
            from app.models.labor_market import Occupation
            count = Occupation.query.count()
            if count > 0:
                return  # Already seeded

            onet_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "onet")
            occupation_file = os.path.join(onet_path, "Occupation Data.txt")
            if not os.path.exists(occupation_file):
                logger.warning("O*NET data files not found, skipping auto-seed")
                return

            logger.info("Auto-seeding O*NET data (tables are empty)...")
            from app.cli import _seed_onet_data
            _seed_onet_data(onet_path)
            logger.info("O*NET auto-seed complete")
        except Exception as e:
            logger.error(f"O*NET auto-seed failed: {e}")
