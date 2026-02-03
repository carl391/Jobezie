"""
Jobezie Flask Application Factory

Creates and configures the Flask application instance.
"""

from flask import Flask, jsonify

from app.config import config, get_config
from app.extensions import db, init_extensions


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

    # Register shell context
    _register_shell_context(app)

    # Health check endpoint
    @app.route("/health")
    def health_check():
        return jsonify({"status": "healthy", "service": "jobezie-api"})

    return app


def _register_blueprints(app):
    """Register Flask blueprints."""
    from app.routes.activity import activity_bp
    from app.routes.ai import ai_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.labor_market import labor_market_bp
    from app.routes.linkedin import linkedin_bp
    from app.routes.message import message_bp
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
        }
