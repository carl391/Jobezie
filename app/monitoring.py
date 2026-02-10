"""
Sentry error monitoring initialization for Jobezie backend.

Setup:
  1. pip install sentry-sdk[flask]     (current Flask)
  2. pip install sentry-sdk[fastapi]   (after FastAPI migration)
  3. Set SENTRY_DSN env var
  4. Call init_sentry(app) in app/__init__.py

Usage:
  from app.monitoring import capture_exception, capture_message

  try:
      risky_operation()
  except Exception as e:
      capture_exception(e)
"""

import os
import logging

logger = logging.getLogger(__name__)

# Sentry SDK is optional — app works without it (dev/test environments)
try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    HAS_SENTRY = True
except ImportError:
    HAS_SENTRY = False
    logger.info('sentry-sdk not installed — error monitoring disabled')


def init_sentry(app=None):
    """
    Initialize Sentry for the Flask backend.

    Call this early in app creation (before routes are registered).

    Required env var:
        SENTRY_DSN — Your Sentry project DSN (from sentry.io)

    Optional env vars:
        SENTRY_ENVIRONMENT — 'production', 'staging', 'development' (default: 'development')
        SENTRY_TRACES_SAMPLE_RATE — 0.0 to 1.0 (default: 0.1 = 10% of requests)
        SENTRY_PROFILES_SAMPLE_RATE — 0.0 to 1.0 (default: 0.1)
    """
    dsn = os.environ.get('SENTRY_DSN', '')

    if not dsn:
        logger.info('SENTRY_DSN not set — Sentry disabled')
        return False

    if not HAS_SENTRY:
        logger.warning('SENTRY_DSN is set but sentry-sdk is not installed. '
                        'Run: pip install sentry-sdk[flask]')
        return False

    environment = os.environ.get('SENTRY_ENVIRONMENT', 'development')
    traces_rate = float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1'))
    profiles_rate = float(os.environ.get('SENTRY_PROFILES_SAMPLE_RATE', '0.1'))

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        integrations=[
            FlaskIntegration(
                transaction_style='url',
            ),
            SqlalchemyIntegration(),
            RedisIntegration(),
            LoggingIntegration(
                level=logging.WARNING,
                event_level=logging.ERROR,
            ),
        ],
        traces_sample_rate=traces_rate,
        profiles_sample_rate=profiles_rate,

        # Release tracking — use git SHA if available
        release=os.environ.get('GIT_SHA', os.environ.get('RENDER_GIT_COMMIT', 'dev')),

        # Don't send PII by default (CCPA compliance)
        send_default_pii=False,

        # Scrub sensitive data from events
        before_send=_scrub_sensitive_data,

        # Filter transactions (skip health checks, static files)
        traces_sampler=_traces_sampler,
    )

    logger.info(f'Sentry initialized: env={environment}, traces={traces_rate}')
    return True


def _scrub_sensitive_data(event, hint):
    """
    Strip sensitive fields from Sentry events before transmission.
    Protects user privacy — passwords, tokens, resume content never leave the server.
    """
    # Scrub request data
    if 'request' in event:
        req = event['request']

        # Remove auth headers
        if 'headers' in req:
            headers = req['headers']
            for sensitive in ['Authorization', 'Cookie', 'X-Api-Key']:
                if sensitive in headers:
                    headers[sensitive] = '[REDACTED]'

        # Remove sensitive body fields
        if 'data' in req and isinstance(req['data'], dict):
            for field in ['password', 'token', 'access_token', 'refresh_token',
                          'credit_card', 'ssn', 'resume_content', 'resume_text']:
                if field in req['data']:
                    req['data'][field] = '[REDACTED]'

    # Scrub user context — keep ID, strip email for privacy
    if 'user' in event:
        user = event['user']
        user.pop('email', None)
        user.pop('ip_address', None)

    return event


def _traces_sampler(sampling_context):
    """
    Custom sampling — skip noisy endpoints, increase sampling for errors.
    """
    transaction = sampling_context.get('transaction_context', {})
    name = transaction.get('name', '')

    # Skip health checks and static files entirely
    skip_patterns = ['/health', '/api/health', '/favicon', '/static', '/robots.txt']
    if any(pattern in name for pattern in skip_patterns):
        return 0.0

    # Sample admin endpoints more heavily (lower traffic, higher value)
    if '/api/admin/' in name:
        return 0.5

    # Sample AI endpoints more heavily (expensive, important to monitor)
    if '/api/coach/' in name or '/api/resumes/' in name:
        return 0.3

    # Default rate from env var
    return float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1'))


# ———————————————————————————————————————————
# Convenience wrappers (safe to call without Sentry installed)
# ———————————————————————————————————————————

def capture_exception(error=None, **kwargs):
    """Send an exception to Sentry. No-op if Sentry not configured."""
    if HAS_SENTRY:
        sentry_sdk.capture_exception(error, **kwargs)


def capture_message(message, level='info', **kwargs):
    """Send a message to Sentry. No-op if Sentry not configured."""
    if HAS_SENTRY:
        sentry_sdk.capture_message(message, level=level, **kwargs)


def set_user_context(user_id, tier=None):
    """
    Tag Sentry events with user context (ID + tier only, no PII).
    Call this after authentication succeeds.
    """
    if HAS_SENTRY:
        sentry_sdk.set_user({'id': str(user_id)})
        if tier:
            sentry_sdk.set_tag('user.tier', tier)


def set_tag(key, value):
    """Add a custom tag to Sentry events."""
    if HAS_SENTRY:
        sentry_sdk.set_tag(key, value)
