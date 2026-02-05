"""
Jobezie Flask Extensions

Centralized extension initialization to avoid circular imports.
Extensions are initialized without app context and bound later in the app factory.
"""

import os

import redis
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


class TokenBlocklist:
    """
    Token blocklist manager with Redis backend and in-memory fallback.

    Stores revoked JWT token IDs (JTIs) to invalidate tokens on logout.
    Tokens automatically expire after the JWT access token lifetime.
    """

    BLOCKLIST_PREFIX = "token_blocklist:"
    DEFAULT_EXPIRY = 3600  # 1 hour (matches JWT_ACCESS_TOKEN_EXPIRES)

    def __init__(self):
        self._redis_client = None
        self._fallback_set = set()
        self._use_redis = False

    def init_app(self, app):
        """Initialize with Flask app to get Redis URL from config."""
        redis_url = app.config.get("CACHE_REDIS_URL") or os.environ.get("REDIS_URL")

        if redis_url:
            try:
                self._redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self._redis_client.ping()
                self._use_redis = True
                app.logger.info("Token blocklist: Using Redis backend")
            except (redis.ConnectionError, redis.RedisError) as e:
                app.logger.warning(f"Token blocklist: Redis unavailable ({e}), using in-memory fallback")
                self._use_redis = False
        else:
            app.logger.info("Token blocklist: No Redis URL configured, using in-memory storage")

    def add(self, jti: str, expires_in: int = None) -> None:
        """Add a token JTI to the blocklist."""
        expiry = expires_in or self.DEFAULT_EXPIRY

        if self._use_redis and self._redis_client:
            try:
                key = f"{self.BLOCKLIST_PREFIX}{jti}"
                self._redis_client.setex(key, expiry, "revoked")
                return
            except redis.RedisError:
                pass  # Fall through to in-memory

        self._fallback_set.add(jti)

    def __contains__(self, jti: str) -> bool:
        """Check if a token JTI is in the blocklist."""
        if self._use_redis and self._redis_client:
            try:
                key = f"{self.BLOCKLIST_PREFIX}{jti}"
                return self._redis_client.exists(key) > 0
            except redis.RedisError:
                pass  # Fall through to in-memory

        return jti in self._fallback_set


# Token Blocklist instance
token_blocklist = TokenBlocklist()


def init_extensions(app):
    """Initialize all Flask extensions with the app instance."""
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})
    cache.init_app(app)
    limiter.init_app(app)
    token_blocklist.init_app(app)

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

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """Check if token JTI is in the blocklist (revoked tokens)."""
        jti = jwt_payload["jti"]
        return jti in token_blocklist
