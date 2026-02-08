"""
Notification Service

Generates and manages user notifications including follow-up reminders,
usage warnings, and achievement notifications.
"""

import logging
from datetime import datetime, timedelta

from app.extensions import db
from app.models.notification import Notification, NotificationType
from app.models.recruiter import Recruiter
from app.models.user import User

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing user notifications."""

    @staticmethod
    def get_notifications(user_id, limit=20, offset=0, unread_only=False):
        """
        Get notifications for a user.

        Args:
            user_id: User UUID
            limit: Max notifications to return
            offset: Pagination offset
            unread_only: If True, only return unread notifications

        Returns:
            Tuple of (notifications list, total count)
        """
        query = Notification.query.filter_by(user_id=user_id)

        if unread_only:
            query = query.filter_by(is_read=False)

        total = query.count()
        notifications = (
            query.order_by(Notification.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return notifications, total

    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread notifications for a user."""
        return Notification.query.filter_by(
            user_id=user_id, is_read=False
        ).count()

    @staticmethod
    def mark_read(notification_id, user_id):
        """
        Mark a single notification as read.

        Args:
            notification_id: Notification UUID
            user_id: User UUID (for ownership check)

        Returns:
            Updated notification or None

        Raises:
            ValueError: If notification not found or not owned by user
        """
        notification = Notification.query.filter_by(
            id=notification_id, user_id=user_id
        ).first()

        if not notification:
            raise ValueError("Notification not found")

        notification.is_read = True
        db.session.commit()
        return notification

    @staticmethod
    def mark_all_read(user_id):
        """
        Mark all notifications as read for a user.

        Args:
            user_id: User UUID

        Returns:
            Number of notifications marked as read
        """
        count = Notification.query.filter_by(
            user_id=user_id, is_read=False
        ).update({"is_read": True})
        db.session.commit()
        return count

    @staticmethod
    def create_notification(user_id, title, body=None, notification_type=None,
                            action_url=None, metadata=None):
        """
        Create a new notification.

        Args:
            user_id: User UUID
            title: Notification title
            body: Optional notification body text
            notification_type: NotificationType value
            action_url: Optional URL for notification action
            metadata: Optional additional data

        Returns:
            Created Notification instance
        """
        notification = Notification(
            user_id=user_id,
            title=title,
            body=body,
            notification_type=notification_type or NotificationType.SYSTEM.value,
            action_url=action_url,
            extra_data=metadata or {},
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @classmethod
    def generate_follow_up_reminders(cls, user_id):
        """
        Generate follow-up reminder notifications based on recruiter data.

        Checks for recruiters that haven't been contacted in 7+ days
        and creates reminder notifications if one doesn't already exist.

        Args:
            user_id: User UUID

        Returns:
            Number of new reminders generated
        """
        # Get recruiters needing follow-up (contacted 7+ days ago, not in terminal stages)
        cutoff = datetime.utcnow() - timedelta(days=7)
        terminal_stages = ["accepted", "declined", "offer"]

        recruiters = (
            Recruiter.query.filter(
                Recruiter.user_id == user_id,
                Recruiter.is_deleted == False,  # noqa: E712
                Recruiter.last_contact_date.isnot(None),
                Recruiter.last_contact_date < cutoff,
                ~Recruiter.status.in_(terminal_stages),
            )
            .order_by(Recruiter.last_contact_date.asc())
            .limit(10)
            .all()
        )

        new_count = 0
        for recruiter in recruiters:
            days_since = (datetime.utcnow() - recruiter.last_contact_date).days

            # Check if we already have a recent reminder for this recruiter
            existing = Notification.query.filter(
                Notification.user_id == user_id,
                Notification.notification_type == NotificationType.FOLLOW_UP_REMINDER.value,
                Notification.is_read == False,  # noqa: E712
                Notification.extra_data["recruiter_id"].astext == str(recruiter.id),
            ).first()

            if existing:
                continue

            full_name = f"{recruiter.first_name} {recruiter.last_name}".strip()
            company = recruiter.company or "Unknown Company"

            cls.create_notification(
                user_id=user_id,
                title=f"Follow up with {full_name}",
                body=f"It's been {days_since} days since you last contacted {full_name} at {company}. "
                     f"Send a follow-up to keep the conversation going.",
                notification_type=NotificationType.FOLLOW_UP_REMINDER.value,
                action_url=f"/messages?recruiterId={recruiter.id}",
                metadata={
                    "recruiter_id": str(recruiter.id),
                    "recruiter_name": full_name,
                    "company": company,
                    "days_since_contact": days_since,
                },
            )
            new_count += 1

        return new_count

    @classmethod
    def generate_usage_warnings(cls, user_id):
        """
        Generate usage warning notifications when approaching tier limits.

        Creates notifications when a user has used 80%+ of any tier limit.

        Args:
            user_id: User UUID

        Returns:
            Number of new warnings generated
        """
        user = User.query.get(user_id)
        if not user:
            return 0

        limits = user.get_tier_limits()
        new_count = 0

        usage_checks = [
            ("messages", user.monthly_message_count, limits.get("ai_messages", 0)),
            ("recruiters", user.monthly_recruiter_count, limits.get("recruiters", 0)),
            ("tailored_resumes", user.monthly_tailoring_count, limits.get("tailored_resumes", 0)),
        ]

        for name, used, limit_val in usage_checks:
            if limit_val <= 0:
                continue  # Unlimited

            usage_pct = (used / limit_val) * 100 if limit_val > 0 else 0

            if usage_pct >= 80:
                # Check if we already warned about this
                existing = Notification.query.filter(
                    Notification.user_id == user_id,
                    Notification.notification_type == NotificationType.USAGE_WARNING.value,
                    Notification.is_read == False,  # noqa: E712
                    Notification.extra_data["usage_type"].astext == name,
                ).first()

                if existing:
                    continue

                friendly_name = name.replace("_", " ").title()
                remaining = limit_val - used

                cls.create_notification(
                    user_id=user_id,
                    title=f"{friendly_name} limit almost reached",
                    body=f"You've used {used} of {limit_val} {friendly_name.lower()} this month. "
                         f"{remaining} remaining.",
                    notification_type=NotificationType.USAGE_WARNING.value,
                    action_url="/settings",
                    metadata={
                        "usage_type": name,
                        "used": used,
                        "limit": limit_val,
                        "percentage": round(usage_pct),
                    },
                )
                new_count += 1

        return new_count
