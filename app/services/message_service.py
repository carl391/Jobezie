"""
Message Service

Handles message generation, quality scoring, and outreach management.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.extensions import db
from app.models.message import Message, MessageStatus
from app.models.recruiter import Recruiter
from app.services.scoring.message import calculate_message_quality, validate_message_length

# Message templates for AI generation context
MESSAGE_TEMPLATES = {
    "initial_outreach": {
        "structure": [
            "Personalized greeting with recruiter name",
            "Brief mention of their work/company",
            "Your relevant experience (1-2 quantified achievements)",
            "Clear value proposition",
            "Single clear call-to-action",
        ],
        "word_limit": 150,
        "tone": "professional but warm",
    },
    "follow_up": {
        "structure": [
            "Reference previous outreach",
            "Add new value (insight, achievement, or question)",
            "Restate interest",
            "Soft call-to-action",
        ],
        "word_limit": 75,
        "tone": "persistent but respectful",
    },
    "thank_you": {
        "structure": [
            "Express genuine gratitude",
            "Reference specific discussion points",
            "Reiterate fit/interest",
            "Look forward to next steps",
        ],
        "word_limit": 125,
        "tone": "warm and appreciative",
    },
    "check_in": {
        "structure": [
            "Brief greeting",
            "Reason for check-in (time elapsed or new development)",
            "Continued interest",
            "Open for discussion",
        ],
        "word_limit": 100,
        "tone": "casual and friendly",
    },
}


class MessageService:
    """Service for message management and quality scoring."""

    @staticmethod
    def create_message(
        user_id: str,
        body: str,
        message_type: str = "initial_outreach",
        subject: Optional[str] = None,
        recruiter_id: Optional[str] = None,
        signature: Optional[str] = None,
        is_ai_generated: bool = False,
        generation_prompt: Optional[str] = None,
        generation_context: Optional[Dict] = None,
        ai_model_used: Optional[str] = None,
    ) -> Tuple[Message, Dict]:
        """
        Create a new message with quality scoring.

        Args:
            user_id: User's ID
            body: Message body text
            message_type: Type of message
            subject: Email subject line
            recruiter_id: Target recruiter ID
            signature: Message signature
            is_ai_generated: Whether message was AI-generated
            generation_prompt: Prompt used for AI generation
            generation_context: Context data used for generation
            ai_model_used: AI model used (claude, openai)

        Returns:
            Tuple of (Message object, quality score result)
        """
        # Get recruiter info for personalization checking
        recruiter_name = None
        company_name = None
        if recruiter_id:
            recruiter = Recruiter.query.get(recruiter_id)
            if recruiter:
                recruiter_name = recruiter.first_name
                company_name = recruiter.company

        # Calculate quality score
        quality_result = calculate_message_quality(
            message_text=body,
            message_type=message_type,
            recruiter_name=recruiter_name,
            company_name=company_name,
        )

        message = Message(
            user_id=user_id,
            recruiter_id=recruiter_id,
            message_type=message_type,
            subject=subject,
            body=body,
            signature=signature,
            is_ai_generated=is_ai_generated,
            generation_prompt=generation_prompt,
            generation_context=generation_context or {},
            ai_model_used=ai_model_used,
            status=MessageStatus.DRAFT.value,
        )

        # Store quality scores
        message.quality_score = quality_result["total_score"]
        message.quality_words_score = quality_result["components"]["words"]
        message.quality_personalization_score = quality_result["components"]["personalization"]
        message.quality_metrics_score = quality_result["components"]["metrics"]
        message.quality_cta_score = quality_result["components"]["cta"]
        message.quality_tone_score = quality_result["components"]["tone"]
        message.quality_feedback = quality_result["feedback"]
        message.quality_suggestions = quality_result["suggestions"]
        message.word_count = quality_result["word_count"]
        message.has_personalization = quality_result["has_personalization"]
        message.has_metrics = quality_result["has_metrics"]
        message.has_cta = quality_result["has_cta"]
        message.personalization_elements = quality_result["personalization_elements"]

        db.session.add(message)
        db.session.commit()

        return message, quality_result

    @staticmethod
    def get_message(message_id: str, user_id: str) -> Optional[Message]:
        """Get a message by ID, verifying ownership."""
        return Message.query.filter_by(id=message_id, user_id=user_id).first()

    @staticmethod
    def get_user_messages(
        user_id: str,
        recruiter_id: Optional[str] = None,
        status: Optional[str] = None,
        message_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Message], int]:
        """
        Get messages for a user with filtering.

        Args:
            user_id: User's ID
            recruiter_id: Filter by recruiter
            status: Filter by status
            message_type: Filter by message type
            limit: Maximum results
            offset: Pagination offset

        Returns:
            Tuple of (message list, total count)
        """
        query = Message.query.filter_by(user_id=user_id)

        if recruiter_id:
            query = query.filter_by(recruiter_id=recruiter_id)
        if status:
            query = query.filter_by(status=status)
        if message_type:
            query = query.filter_by(message_type=message_type)

        total = query.count()

        messages = query.order_by(Message.created_at.desc()).offset(offset).limit(limit).all()

        return messages, total

    @staticmethod
    def update_message(
        message_id: str,
        user_id: str,
        body: Optional[str] = None,
        subject: Optional[str] = None,
        signature: Optional[str] = None,
    ) -> Tuple[Message, Dict]:
        """
        Update a message and recalculate quality score.

        Args:
            message_id: Message ID
            user_id: User ID for verification
            body: New message body
            subject: New subject line
            signature: New signature

        Returns:
            Tuple of (updated Message, new quality result)
        """
        message = MessageService.get_message(message_id, user_id)
        if not message:
            raise ValueError("Message not found")

        if message.status == MessageStatus.SENT.value:
            raise ValueError("Cannot edit sent messages")

        # Update fields
        if body is not None:
            message.body = body
        if subject is not None:
            message.subject = subject
        if signature is not None:
            message.signature = signature

        # Recalculate quality
        recruiter_name = None
        company_name = None
        if message.recruiter_id:
            recruiter = Recruiter.query.get(message.recruiter_id)
            if recruiter:
                recruiter_name = recruiter.first_name
                company_name = recruiter.company

        quality_result = calculate_message_quality(
            message_text=message.body,
            message_type=message.message_type,
            recruiter_name=recruiter_name,
            company_name=company_name,
        )

        # Update quality scores
        message.quality_score = quality_result["total_score"]
        message.quality_words_score = quality_result["components"]["words"]
        message.quality_personalization_score = quality_result["components"]["personalization"]
        message.quality_metrics_score = quality_result["components"]["metrics"]
        message.quality_cta_score = quality_result["components"]["cta"]
        message.quality_tone_score = quality_result["components"]["tone"]
        message.quality_feedback = quality_result["feedback"]
        message.quality_suggestions = quality_result["suggestions"]
        message.word_count = quality_result["word_count"]
        message.has_personalization = quality_result["has_personalization"]
        message.has_metrics = quality_result["has_metrics"]
        message.has_cta = quality_result["has_cta"]
        message.personalization_elements = quality_result["personalization_elements"]

        message.version += 1
        message.updated_at = datetime.utcnow()

        db.session.commit()

        return message, quality_result

    @staticmethod
    def mark_as_sent(message_id: str, user_id: str) -> Message:
        """Mark a message as sent."""
        message = MessageService.get_message(message_id, user_id)
        if not message:
            raise ValueError("Message not found")

        message.status = MessageStatus.SENT.value
        message.sent_at = datetime.utcnow()

        db.session.commit()

        return message

    @staticmethod
    def mark_as_opened(message_id: str, user_id: str) -> Message:
        """Mark a message as opened."""
        message = MessageService.get_message(message_id, user_id)
        if not message:
            raise ValueError("Message not found")

        if message.status == MessageStatus.SENT.value:
            message.status = MessageStatus.OPENED.value
            message.opened_at = datetime.utcnow()
            db.session.commit()

        return message

    @staticmethod
    def mark_as_responded(message_id: str, user_id: str) -> Message:
        """Mark a message as having received a response."""
        message = MessageService.get_message(message_id, user_id)
        if not message:
            raise ValueError("Message not found")

        message.status = MessageStatus.RESPONDED.value
        message.responded_at = datetime.utcnow()

        db.session.commit()

        return message

    @staticmethod
    def delete_message(message_id: str, user_id: str) -> bool:
        """Delete a message."""
        message = MessageService.get_message(message_id, user_id)
        if not message:
            raise ValueError("Message not found")

        if message.status == MessageStatus.SENT.value:
            raise ValueError("Cannot delete sent messages")

        db.session.delete(message)
        db.session.commit()

        return True

    @staticmethod
    def get_generation_context(
        user_id: str,
        recruiter_id: str,
        message_type: str = "initial_outreach",
        resume_id: Optional[str] = None,
    ) -> Dict:
        """
        Build context for AI message generation.

        Collects user profile, recruiter info, resume data, and
        template guidelines for AI generation.

        Args:
            user_id: User's ID
            recruiter_id: Target recruiter ID
            message_type: Type of message to generate
            resume_id: Optional resume to pull achievements from

        Returns:
            Dictionary with generation context
        """
        from app.models.resume import Resume
        from app.models.user import User

        context = {
            "message_type": message_type,
            "template": MESSAGE_TEMPLATES.get(message_type, MESSAGE_TEMPLATES["initial_outreach"]),
            "user": {},
            "recruiter": {},
            "achievements": [],
            "guidelines": {
                "word_limit": 150,
                "must_include": [
                    "recruiter name",
                    "specific value proposition",
                    "single CTA",
                ],
                "avoid": ["generic phrases", "multiple asks", "lengthy paragraphs"],
            },
        }

        # Get user info
        user = User.query.get(user_id)
        if user:
            context["user"] = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "title": user.current_role,
                "industries": user.target_industries,
                "target_roles": user.target_roles,
                "location": user.location,
            }

        # Get recruiter info
        recruiter = Recruiter.query.get(recruiter_id)
        if recruiter:
            context["recruiter"] = {
                "first_name": recruiter.first_name,
                "last_name": recruiter.last_name,
                "company": recruiter.company,
                "title": recruiter.title,
                "specialty": recruiter.specialty,
                "industries": recruiter.industries,
                "locations": recruiter.locations,
            }

        # Get achievements from resume
        if resume_id:
            resume = Resume.query.get(resume_id)
            if resume and resume.parsed_sections:
                experience = resume.parsed_sections.get("experience", "")
                # Extract bullet points as potential achievements
                import re

                bullets = re.findall(r"[•\-\*]\s*([^\n]+)", experience)
                context["achievements"] = bullets[:5]  # Top 5

        return context

    @staticmethod
    def validate_message(body: str, message_type: str = "initial_outreach") -> Dict:
        """
        Validate message length without full scoring.

        Quick validation for real-time feedback.
        """
        return validate_message_length(body, message_type)

    @staticmethod
    def get_quality_tips(message_type: str = "initial_outreach") -> Dict:
        """
        Get quality tips for a message type.

        Returns research-backed tips for writing effective messages.
        """
        template = MESSAGE_TEMPLATES.get(message_type, MESSAGE_TEMPLATES["initial_outreach"])

        tips = {
            "structure": template["structure"],
            "word_limit": template["word_limit"],
            "tone": template["tone"],
            "research_insights": [],
        }

        # Add research-backed insights
        if message_type == "initial_outreach":
            tips["research_insights"] = [
                "Messages under 150 words get 22% higher response rate",
                "Using recruiter name increases open rate by 41%",
                "Single CTA reduces decision paralysis",
                "Quantified achievements get 40% more interviews",
            ]
        elif message_type == "follow_up":
            tips["research_insights"] = [
                "80% of sales require 5+ follow-ups",
                "Follow up 5-7 days after initial outreach",
                "Add new value with each follow-up",
                "Keep follow-ups even shorter than initial message",
            ]
        elif message_type == "thank_you":
            tips["research_insights"] = [
                "Send within 24 hours of interview",
                "Reference specific conversation points",
                "Reiterate enthusiasm for the role",
                "Keep it concise and genuine",
            ]

        return tips

    @staticmethod
    def get_message_stats(user_id: str) -> Dict:
        """
        Get message statistics for user dashboard.

        Returns counts, quality averages, and effectiveness metrics.
        """
        messages = Message.query.filter_by(user_id=user_id).all()

        stats = {
            "total": len(messages),
            "by_status": {
                "draft": 0,
                "ready": 0,
                "sent": 0,
                "opened": 0,
                "responded": 0,
            },
            "by_type": {
                "initial_outreach": 0,
                "follow_up": 0,
                "thank_you": 0,
                "check_in": 0,
            },
            "avg_quality_score": 0,
            "open_rate": 0,
            "response_rate": 0,
            "avg_word_count": 0,
        }

        if not messages:
            return stats

        quality_scores = []
        word_counts = []
        sent_count = 0
        opened_count = 0
        responded_count = 0

        for msg in messages:
            # Count by status
            if msg.status in stats["by_status"]:
                stats["by_status"][msg.status] += 1

            # Count by type
            if msg.message_type in stats["by_type"]:
                stats["by_type"][msg.message_type] += 1

            # Collect metrics
            if msg.quality_score:
                quality_scores.append(msg.quality_score)
            if msg.word_count:
                word_counts.append(msg.word_count)

            # Track effectiveness
            if msg.status in [
                MessageStatus.SENT.value,
                MessageStatus.OPENED.value,
                MessageStatus.RESPONDED.value,
            ]:
                sent_count += 1
            if msg.status in [
                MessageStatus.OPENED.value,
                MessageStatus.RESPONDED.value,
            ]:
                opened_count += 1
            if msg.status == MessageStatus.RESPONDED.value:
                responded_count += 1

        # Calculate averages
        if quality_scores:
            stats["avg_quality_score"] = round(sum(quality_scores) / len(quality_scores), 1)
        if word_counts:
            stats["avg_word_count"] = round(sum(word_counts) / len(word_counts), 1)
        if sent_count > 0:
            stats["open_rate"] = round((opened_count / sent_count) * 100, 1)
            stats["response_rate"] = round((responded_count / sent_count) * 100, 1)

        return stats
