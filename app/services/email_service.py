"""
Email Service

Handles email sending via SendGrid for transactional emails.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from flask import current_app, render_template_string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Attachment,
    Email,
    FileContent,
    FileName,
    FileType,
    Mail,
    To,
)


class EmailService:
    """
    Service for sending transactional emails via SendGrid.
    """

    FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@jobezie.com")
    FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "Jobezie")

    # Email templates
    TEMPLATES = {
        "welcome": {
            "subject": "Welcome to Jobezie! Let's Start Your Career Journey",
            "template": """
Hello {{ name }},

Welcome to Jobezie! We're excited to help you take control of your career journey.

Here's what you can do next:
1. Complete your profile to get personalized recommendations
2. Upload your resume for ATS optimization
3. Add recruiters to your pipeline
4. Generate AI-powered outreach messages

If you have any questions, just reply to this email.

Best of luck on your job search!

The Jobezie Team
            """,
        },
        "password_reset": {
            "subject": "Reset Your Jobezie Password",
            "template": """
Hello {{ name }},

We received a request to reset your password. Click the link below to create a new password:

{{ reset_url }}

This link will expire in 1 hour.

If you didn't request this, you can safely ignore this email.

The Jobezie Team
            """,
        },
        "email_verification": {
            "subject": "Verify Your Jobezie Email",
            "template": """
Hello {{ name }},

Please verify your email address by clicking the link below:

{{ verification_url }}

This link will expire in 24 hours.

The Jobezie Team
            """,
        },
        "subscription_confirmed": {
            "subject": "Your Jobezie {{ tier }} Subscription is Active!",
            "template": """
Hello {{ name }},

Great news! Your {{ tier }} subscription is now active.

Your new features include:
{% for feature in features %}
- {{ feature }}
{% endfor %}

Start using your new features now at: {{ dashboard_url }}

If you have any questions about your subscription, just reply to this email.

The Jobezie Team
            """,
        },
        "subscription_cancelled": {
            "subject": "Your Jobezie Subscription Has Been Cancelled",
            "template": """
Hello {{ name }},

We're sorry to see you go. Your subscription has been cancelled and will remain active until {{ end_date }}.

After that date, your account will be downgraded to the free Basic tier.

If you change your mind, you can resubscribe anytime at: {{ resubscribe_url }}

We'd love to hear your feedback on how we can improve. Just reply to this email.

The Jobezie Team
            """,
        },
        "payment_failed": {
            "subject": "Action Required: Payment Failed for Your Jobezie Subscription",
            "template": """
Hello {{ name }},

We were unable to process your payment for your Jobezie subscription.

Please update your payment method to avoid service interruption:
{{ update_payment_url }}

If you're having trouble, please reply to this email and we'll help.

The Jobezie Team
            """,
        },
        "weekly_summary": {
            "subject": "Your Weekly Jobezie Summary",
            "template": """
Hello {{ name }},

Here's your weekly career activity summary:

PIPELINE ACTIVITY
- Messages sent: {{ messages_sent }}
- Responses received: {{ responses_received }}
- Response rate: {{ response_rate }}%
- New recruiters added: {{ recruiters_added }}

TOP PRIORITIES THIS WEEK
{% for priority in priorities %}
- {{ priority }}
{% endfor %}

Keep up the momentum! Log in to continue your progress: {{ dashboard_url }}

The Jobezie Team
            """,
        },
        "follow_up_reminder": {
            "subject": "Time to Follow Up: {{ recruiter_name }} at {{ company }}",
            "template": """
Hello {{ name }},

It's been {{ days }} days since you last contacted {{ recruiter_name }} at {{ company }}.

Based on research, following up between 5-7 days increases response rates by 22%.

Quick actions:
- Send a follow-up: {{ message_url }}
- View recruiter details: {{ recruiter_url }}

The Jobezie Team
            """,
        },
    }

    @staticmethod
    def _get_client() -> Optional[SendGridAPIClient]:
        """Get SendGrid client."""
        api_key = os.getenv("SENDGRID_API_KEY")
        if not api_key:
            current_app.logger.warning("SendGrid API key not configured")
            return None
        return SendGridAPIClient(api_key)

    @classmethod
    def send_email(
        cls,
        to_email: str,
        subject: str,
        content: str,
        content_type: str = "text/plain",
        attachments: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Send an email via SendGrid.

        Args:
            to_email: Recipient email address
            subject: Email subject
            content: Email body content
            content_type: Content type (text/plain or text/html)
            attachments: Optional list of attachments

        Returns:
            Dictionary with send result
        """
        client = cls._get_client()
        if not client:
            return {
                "success": False,
                "error": "Email service not configured",
            }

        message = Mail(
            from_email=Email(cls.FROM_EMAIL, cls.FROM_NAME),
            to_emails=To(to_email),
            subject=subject,
            plain_text_content=content if content_type == "text/plain" else None,
            html_content=content if content_type == "text/html" else None,
        )

        # Add attachments if any
        if attachments:
            for att in attachments:
                attachment = Attachment(
                    FileContent(att["content"]),
                    FileName(att["filename"]),
                    FileType(att.get("type", "application/octet-stream")),
                )
                message.add_attachment(attachment)

        try:
            response = client.send(message)

            return {
                "success": response.status_code in [200, 202],
                "status_code": response.status_code,
            }

        except Exception as e:
            current_app.logger.error(f"SendGrid error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }

    @classmethod
    def send_template_email(
        cls,
        to_email: str,
        template_name: str,
        context: Dict,
    ) -> Dict:
        """
        Send an email using a predefined template.

        Args:
            to_email: Recipient email address
            template_name: Name of template to use
            context: Dictionary of template variables

        Returns:
            Dictionary with send result
        """
        template = cls.TEMPLATES.get(template_name)
        if not template:
            return {
                "success": False,
                "error": f"Unknown template: {template_name}",
            }

        # Render template with context
        subject = render_template_string(template["subject"], **context)
        content = render_template_string(template["template"], **context)

        return cls.send_email(to_email, subject, content)

    @classmethod
    def send_welcome_email(cls, user) -> Dict:
        """Send welcome email to new user."""
        return cls.send_template_email(
            to_email=user.email,
            template_name="welcome",
            context={
                "name": user.first_name or "there",
            },
        )

    @classmethod
    def send_password_reset_email(cls, user, reset_token: str) -> Dict:
        """Send password reset email."""
        base_url = os.getenv("FRONTEND_URL", "https://app.jobezie.com")
        reset_url = f"{base_url}/reset-password?token={reset_token}"

        return cls.send_template_email(
            to_email=user.email,
            template_name="password_reset",
            context={
                "name": user.first_name or "there",
                "reset_url": reset_url,
            },
        )

    @classmethod
    def send_verification_email(cls, user, verification_token: str) -> Dict:
        """Send email verification email."""
        base_url = os.getenv("FRONTEND_URL", "https://app.jobezie.com")
        verification_url = f"{base_url}/verify-email?token={verification_token}"

        return cls.send_template_email(
            to_email=user.email,
            template_name="email_verification",
            context={
                "name": user.first_name or "there",
                "verification_url": verification_url,
            },
        )

    @classmethod
    def send_subscription_confirmed_email(cls, user, tier: str, features: List[str]) -> Dict:
        """Send subscription confirmation email."""
        base_url = os.getenv("FRONTEND_URL", "https://app.jobezie.com")

        return cls.send_template_email(
            to_email=user.email,
            template_name="subscription_confirmed",
            context={
                "name": user.first_name or "there",
                "tier": tier.title(),
                "features": features,
                "dashboard_url": f"{base_url}/dashboard",
            },
        )

    @classmethod
    def send_subscription_cancelled_email(cls, user, end_date: datetime) -> Dict:
        """Send subscription cancellation email."""
        base_url = os.getenv("FRONTEND_URL", "https://app.jobezie.com")

        return cls.send_template_email(
            to_email=user.email,
            template_name="subscription_cancelled",
            context={
                "name": user.first_name or "there",
                "end_date": end_date.strftime("%B %d, %Y"),
                "resubscribe_url": f"{base_url}/pricing",
            },
        )

    @classmethod
    def send_payment_failed_email(cls, user) -> Dict:
        """Send payment failure notification email."""
        base_url = os.getenv("FRONTEND_URL", "https://app.jobezie.com")

        return cls.send_template_email(
            to_email=user.email,
            template_name="payment_failed",
            context={
                "name": user.first_name or "there",
                "update_payment_url": f"{base_url}/settings/billing",
            },
        )

    @classmethod
    def send_weekly_summary_email(
        cls,
        user,
        stats: Dict,
        priorities: List[str],
    ) -> Dict:
        """Send weekly summary email."""
        base_url = os.getenv("FRONTEND_URL", "https://app.jobezie.com")

        return cls.send_template_email(
            to_email=user.email,
            template_name="weekly_summary",
            context={
                "name": user.first_name or "there",
                "messages_sent": stats.get("messages_sent", 0),
                "responses_received": stats.get("responses_received", 0),
                "response_rate": stats.get("response_rate", 0),
                "recruiters_added": stats.get("recruiters_added", 0),
                "priorities": priorities,
                "dashboard_url": f"{base_url}/dashboard",
            },
        )

    @classmethod
    def send_follow_up_reminder_email(
        cls,
        user,
        recruiter,
        days_since_contact: int,
    ) -> Dict:
        """Send follow-up reminder email."""
        base_url = os.getenv("FRONTEND_URL", "https://app.jobezie.com")

        return cls.send_template_email(
            to_email=user.email,
            template_name="follow_up_reminder",
            context={
                "name": user.first_name or "there",
                "recruiter_name": recruiter.full_name,
                "company": recruiter.company or "their company",
                "days": days_since_contact,
                "message_url": f"{base_url}/messages/new?recruiter={recruiter.id}",
                "recruiter_url": f"{base_url}/recruiters/{recruiter.id}",
            },
        )
