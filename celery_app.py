"""
Celery Application Configuration

This module configures Celery for background task processing.
Run the worker with: celery -A celery_app worker --loglevel=info
Run the beat scheduler with: celery -A celery_app beat --loglevel=info
"""

import os

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

# Redis URL for Celery broker and result backend
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")


def create_celery_app():
    """Create and configure Celery application."""
    celery = Celery(
        "jobezie",
        broker=REDIS_URL,
        backend=REDIS_URL,
        include=["app.tasks"],
    )

    # Celery configuration
    celery.conf.update(
        # Task settings
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        # Task execution settings
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        worker_prefetch_multiplier=1,
        # Result backend settings
        result_expires=3600,  # Results expire after 1 hour
        # Beat schedule for periodic tasks
        beat_schedule={
            # Send weekly summaries every Monday at 9 AM UTC
            "send-weekly-summaries": {
                "task": "app.tasks.send_weekly_summaries",
                "schedule": crontab(hour=9, minute=0, day_of_week=1),
            },
            # Check for follow-up reminders daily at 10 AM UTC
            "check-follow-up-reminders": {
                "task": "app.tasks.check_follow_up_reminders",
                "schedule": crontab(hour=10, minute=0),
            },
        },
    )

    return celery


# Create the Celery app instance
celery_app = create_celery_app()

# Make sure tasks are autodiscovered when the app is imported
celery_app.autodiscover_tasks(["app"])
