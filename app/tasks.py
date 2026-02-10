"""
Celery Background Tasks

This module defines background tasks for scheduled operations like
weekly summaries and follow-up reminders.
"""

from datetime import datetime, timedelta

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_weekly_summaries(self):
    """
    Send weekly summary emails to all active users.

    This task runs every Monday at 9 AM UTC. It gathers stats for each user
    and sends them a personalized summary email.
    """
    from app import create_app
    from app.models.message import Message
    from app.models.recruiter import Recruiter
    from app.models.user import User
    from app.services.email_service import EmailService

    app = create_app()

    with app.app_context():
        try:
            # Get date range for the past week
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)

            # Get active users (logged in within last 30 days)
            active_cutoff = datetime.utcnow() - timedelta(days=30)
            active_users = User.query.filter(
                User.last_login_at >= active_cutoff,
                User.email_verified == True,  # noqa: E712
            ).all()

            logger.info(f"Sending weekly summaries to {len(active_users)} active users")

            success_count = 0
            error_count = 0

            for user in active_users:
                try:
                    # Gather stats for this user
                    messages_sent = Message.query.filter(
                        Message.user_id == user.id,
                        Message.created_at >= start_date,
                        Message.created_at <= end_date,
                    ).count()

                    responses = Message.query.filter(
                        Message.user_id == user.id,
                        Message.responded_at >= start_date,
                        Message.responded_at.isnot(None),
                    ).count()

                    recruiters_added = Recruiter.query.filter(
                        Recruiter.user_id == user.id,
                        Recruiter.created_at >= start_date,
                        Recruiter.created_at <= end_date,
                    ).count()

                    response_rate = (responses / messages_sent * 100) if messages_sent > 0 else 0

                    stats = {
                        "messages_sent": messages_sent,
                        "responses_received": responses,
                        "response_rate": round(response_rate, 1),
                        "recruiters_added": recruiters_added,
                    }

                    # Generate priority recommendations
                    priorities = _generate_weekly_priorities(user, stats)

                    # Send email
                    EmailService.send_weekly_summary_email(user, stats, priorities)
                    success_count += 1

                except Exception as e:
                    logger.error(f"Error sending weekly summary to {user.email}: {e}")
                    error_count += 1

            logger.info(f"Weekly summary complete: {success_count} sent, {error_count} errors")
            return {"success": success_count, "errors": error_count}

        except Exception as exc:
            logger.error(f"Weekly summary task failed: {exc}")
            raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def check_follow_up_reminders(self):
    """
    Check for recruiters that need follow-up and send reminder emails.

    This task runs daily at 10 AM UTC. It checks for recruiters in certain
    pipeline stages who haven't been contacted recently.
    """
    from app import create_app
    from app.models.recruiter import Recruiter
    from app.models.user import User
    from app.services.email_service import EmailService

    app = create_app()

    with app.app_context():
        try:
            # Define follow-up thresholds by pipeline stage
            follow_up_days = {
                "contacted": 3,
                "responded": 5,
                "phone_screen": 7,
                "interview": 7,
            }

            success_count = 0
            error_count = 0

            for user in User.query.filter(User.email_verified == True).all():  # noqa: E712
                try:
                    for stage, days_threshold in follow_up_days.items():
                        cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)

                        # Find recruiters needing follow-up
                        recruiters = Recruiter.query.filter(
                            Recruiter.user_id == user.id,
                            Recruiter.status == stage,
                            Recruiter.last_contact_date < cutoff_date,
                        ).all()

                        for recruiter in recruiters:
                            days_since = (datetime.utcnow() - recruiter.last_contact_date).days

                            EmailService.send_follow_up_reminder_email(user, recruiter, days_since)
                            success_count += 1

                except Exception as e:
                    logger.error(f"Error checking follow-ups for {user.email}: {e}")
                    error_count += 1

            logger.info(
                f"Follow-up check complete: {success_count} reminders sent, {error_count} errors"
            )
            return {"reminders_sent": success_count, "errors": error_count}

        except Exception as exc:
            logger.error(f"Follow-up reminder task failed: {exc}")
            raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_verification_reminder(self, user_id: str):
    """
    Send an email verification reminder to a user.

    This task is triggered for users who haven't verified their email
    after a certain period.
    """
    import secrets

    from app import create_app
    from app.extensions import db
    from app.models.user import User
    from app.services.email_service import EmailService

    app = create_app()

    with app.app_context():
        try:
            user = User.query.get(user_id)

            if user and not user.email_verified:
                # Generate a new verification token if needed
                if not user.verification_token:
                    user.verification_token = secrets.token_urlsafe(32)
                    db.session.commit()

                EmailService.send_verification_email(user, user.verification_token)
                logger.info(f"Verification reminder sent to {user.email}")
                return {"success": True, "email": user.email}
            else:
                return {"success": False, "reason": "User not found or already verified"}

        except Exception as exc:
            logger.error(f"Verification reminder task failed for {user_id}: {exc}")
            raise self.retry(exc=exc)


def _generate_weekly_priorities(user, stats: dict) -> list:
    """Generate personalized priority recommendations based on user activity."""
    priorities = []

    if stats["messages_sent"] == 0:
        priorities.append("Send at least 5 outreach messages this week to build momentum")

    if stats["response_rate"] < 20 and stats["messages_sent"] > 0:
        priorities.append(
            "Review your message templates - AI Coach can help improve response rates"
        )

    if stats["recruiters_added"] == 0:
        priorities.append("Add new recruiters to expand your network")

    # Add positive reinforcement if doing well
    if stats["response_rate"] >= 30:
        priorities.append("Great response rate! Keep up the good work")

    # Default priority if nothing else
    if not priorities:
        priorities.append("Keep consistent with your outreach this week")

    return priorities[:3]  # Max 3 priorities
