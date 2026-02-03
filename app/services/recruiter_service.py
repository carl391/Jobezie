"""
Recruiter CRM Service

Handles recruiter management, engagement tracking, and fit scoring.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.extensions import db
from app.models.activity import PipelineItem, PipelineStage
from app.models.recruiter import Recruiter, RecruiterNote
from app.services.scoring.engagement import (
    calculate_engagement_score,
    calculate_fit_score,
    calculate_priority_score,
)


class RecruiterService:
    """Service for recruiter CRM management."""

    @staticmethod
    def create_recruiter(
        user_id: str,
        first_name: str,
        last_name: str,
        email: Optional[str] = None,
        company: Optional[str] = None,
        title: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        phone: Optional[str] = None,
        industries: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        specialty: Optional[str] = None,
        company_type: Optional[str] = None,
        source: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Recruiter:
        """
        Add a new recruiter to the CRM.

        Args:
            user_id: User's ID
            first_name: Recruiter's first name
            last_name: Recruiter's last name
            email: Email address
            company: Company name
            title: Job title
            linkedin_url: LinkedIn profile URL
            phone: Phone number
            industries: Industries they recruit for
            locations: Geographic locations they cover
            specialty: Role specialty (e.g., "Software Engineering")
            company_type: Agency, corporate, executive search
            source: Where the recruiter was found
            notes: Initial notes

        Returns:
            New Recruiter object
        """
        recruiter = Recruiter(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            company=company,
            title=title,
            linkedin_url=linkedin_url,
            phone=phone,
            industries=industries or [],
            locations=locations or [],
            specialty=specialty,
            company_type=company_type,
            source=source,
            status=PipelineStage.NEW.value,
        )

        db.session.add(recruiter)
        db.session.flush()  # Get ID for pipeline item

        # Create initial pipeline item
        pipeline_item = PipelineItem(
            user_id=user_id,
            recruiter_id=recruiter.id,
            stage=PipelineStage.NEW.value,
            position=0,
        )
        db.session.add(pipeline_item)

        # Add initial note if provided
        if notes:
            note = RecruiterNote(
                recruiter_id=recruiter.id,
                content=notes,
                note_type="general",
            )
            db.session.add(note)

        db.session.commit()

        return recruiter

    @staticmethod
    def get_recruiter(recruiter_id: str, user_id: str) -> Optional[Recruiter]:
        """Get a recruiter by ID, verifying ownership."""
        return Recruiter.query.filter_by(id=recruiter_id, user_id=user_id).first()

    @staticmethod
    def get_user_recruiters(
        user_id: str,
        status: Optional[str] = None,
        industry: Optional[str] = None,
        location: Optional[str] = None,
        sort_by: str = "priority",
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Recruiter], int]:
        """
        Get recruiters for a user with filtering and sorting.

        Args:
            user_id: User's ID
            status: Filter by pipeline status
            industry: Filter by industry
            location: Filter by location
            sort_by: Sort field (priority, name, company, last_contact)
            limit: Maximum results
            offset: Pagination offset

        Returns:
            Tuple of (recruiter list, total count)
        """
        query = Recruiter.query.filter_by(user_id=user_id)

        if status:
            query = query.filter_by(status=status)

        # Note: Industry and location filtering would need contains for JSON arrays
        # This is database-specific; simplified here

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        if sort_by == "priority":
            query = query.order_by(Recruiter.priority_score.desc())
        elif sort_by == "name":
            query = query.order_by(Recruiter.last_name, Recruiter.first_name)
        elif sort_by == "company":
            query = query.order_by(Recruiter.company)
        elif sort_by == "last_contact":
            query = query.order_by(Recruiter.last_contact_date.desc())
        elif sort_by == "engagement":
            query = query.order_by(Recruiter.engagement_score.desc())
        elif sort_by == "fit":
            query = query.order_by(Recruiter.fit_score.desc())
        else:
            query = query.order_by(Recruiter.created_at.desc())

        recruiters = query.offset(offset).limit(limit).all()

        return recruiters, total

    @staticmethod
    def update_recruiter(recruiter_id: str, user_id: str, **updates) -> Recruiter:
        """
        Update recruiter information.

        Args:
            recruiter_id: Recruiter ID
            user_id: User ID for verification
            **updates: Fields to update

        Returns:
            Updated Recruiter object
        """
        recruiter = RecruiterService.get_recruiter(recruiter_id, user_id)
        if not recruiter:
            raise ValueError("Recruiter not found")

        allowed_fields = {
            "first_name",
            "last_name",
            "email",
            "company",
            "title",
            "linkedin_url",
            "phone",
            "industries",
            "locations",
            "specialty",
            "company_type",
            "salary_range_min",
            "salary_range_max",
        }

        for field, value in updates.items():
            if field in allowed_fields and value is not None:
                setattr(recruiter, field, value)

        recruiter.updated_at = datetime.utcnow()
        db.session.commit()

        return recruiter

    @staticmethod
    def delete_recruiter(recruiter_id: str, user_id: str) -> bool:
        """Delete a recruiter from CRM."""
        recruiter = RecruiterService.get_recruiter(recruiter_id, user_id)
        if not recruiter:
            raise ValueError("Recruiter not found")

        # Delete associated pipeline item
        PipelineItem.query.filter_by(recruiter_id=recruiter_id).delete()

        db.session.delete(recruiter)
        db.session.commit()

        return True

    @staticmethod
    def update_pipeline_stage(
        recruiter_id: str,
        user_id: str,
        new_stage: str,
    ) -> Recruiter:
        """
        Move recruiter to a new pipeline stage.

        Args:
            recruiter_id: Recruiter ID
            user_id: User ID
            new_stage: New pipeline stage

        Returns:
            Updated Recruiter object
        """
        recruiter = RecruiterService.get_recruiter(recruiter_id, user_id)
        if not recruiter:
            raise ValueError("Recruiter not found")

        # Validate stage
        valid_stages = [s.value for s in PipelineStage]
        if new_stage not in valid_stages:
            raise ValueError(f"Invalid stage. Must be one of: {', '.join(valid_stages)}")

        recruiter.status = new_stage

        # Update pipeline item
        pipeline_item = PipelineItem.query.filter_by(recruiter_id=recruiter_id).first()

        if pipeline_item:
            pipeline_item.stage = new_stage
            pipeline_item.entered_stage_at = datetime.utcnow()
            pipeline_item.days_in_stage = 0

        # Recalculate priority
        RecruiterService._update_priority_score(recruiter)

        db.session.commit()

        return recruiter

    @staticmethod
    def record_message_sent(
        recruiter_id: str,
        user_id: str,
        message_id: Optional[str] = None,
    ) -> Recruiter:
        """
        Record that a message was sent to recruiter.

        Updates engagement metrics and priority score.
        """
        recruiter = RecruiterService.get_recruiter(recruiter_id, user_id)
        if not recruiter:
            raise ValueError("Recruiter not found")

        recruiter.messages_sent = (recruiter.messages_sent or 0) + 1
        recruiter.last_contact_date = datetime.utcnow()

        # Move to contacted stage if new
        if recruiter.status == PipelineStage.NEW.value:
            recruiter.status = PipelineStage.CONTACTED.value

        RecruiterService._update_engagement_score(recruiter)
        RecruiterService._update_priority_score(recruiter)

        db.session.commit()

        return recruiter

    @staticmethod
    def record_message_opened(
        recruiter_id: str,
        user_id: str,
    ) -> Recruiter:
        """Record that a message was opened by recruiter."""
        recruiter = RecruiterService.get_recruiter(recruiter_id, user_id)
        if not recruiter:
            raise ValueError("Recruiter not found")

        recruiter.messages_opened = (recruiter.messages_opened or 0) + 1

        RecruiterService._update_engagement_score(recruiter)

        db.session.commit()

        return recruiter

    @staticmethod
    def record_response(
        recruiter_id: str,
        user_id: str,
        is_positive: bool = True,
    ) -> Recruiter:
        """
        Record a response from recruiter.

        Args:
            recruiter_id: Recruiter ID
            user_id: User ID
            is_positive: Whether response was positive
        """
        recruiter = RecruiterService.get_recruiter(recruiter_id, user_id)
        if not recruiter:
            raise ValueError("Recruiter not found")

        recruiter.responses_received = (recruiter.responses_received or 0) + 1
        recruiter.has_responded = True
        recruiter.last_response_date = datetime.utcnow()

        # Move to responded stage
        if recruiter.status in [PipelineStage.NEW.value, PipelineStage.CONTACTED.value]:
            recruiter.status = PipelineStage.RESPONDED.value

        RecruiterService._update_engagement_score(recruiter)
        RecruiterService._update_priority_score(recruiter)

        db.session.commit()

        return recruiter

    @staticmethod
    def calculate_fit_score(
        recruiter_id: str,
        user_id: str,
        user_industries: List[str],
        user_location: Optional[str],
        user_target_roles: List[str],
        user_salary_expectation: Optional[int],
    ) -> Dict:
        """
        Calculate and store fit score for a recruiter.

        Args:
            recruiter_id: Recruiter ID
            user_id: User ID
            user_industries: User's target industries
            user_location: User's location preference
            user_target_roles: User's target job roles
            user_salary_expectation: User's salary expectation

        Returns:
            Fit score breakdown
        """
        recruiter = RecruiterService.get_recruiter(recruiter_id, user_id)
        if not recruiter:
            raise ValueError("Recruiter not found")

        salary_range = None
        if recruiter.salary_range_min and recruiter.salary_range_max:
            salary_range = (recruiter.salary_range_min, recruiter.salary_range_max)

        result = calculate_fit_score(
            user_industries=user_industries,
            user_location=user_location,
            user_target_roles=user_target_roles,
            user_salary_expectation=user_salary_expectation,
            recruiter_industries=recruiter.industries or [],
            recruiter_locations=recruiter.locations or [],
            recruiter_specialty=recruiter.specialty,
            recruiter_company_type=recruiter.company_type,
            recruiter_salary_range=salary_range,
        )

        recruiter.fit_score = result["total_score"]
        recruiter.fit_components = result["components"]

        RecruiterService._update_priority_score(recruiter)

        db.session.commit()

        return result

    @staticmethod
    def _update_engagement_score(recruiter: Recruiter) -> None:
        """Update engagement score based on current metrics."""
        result = calculate_engagement_score(
            messages_sent=recruiter.messages_sent or 0,
            messages_opened=recruiter.messages_opened or 0,
            responses_received=recruiter.responses_received or 0,
            last_contact_date=recruiter.last_contact_date,
        )

        recruiter.engagement_score = result["total_score"]
        recruiter.engagement_components = result["components"]

    @staticmethod
    def _update_priority_score(recruiter: Recruiter) -> None:
        """Update priority score for follow-up recommendations."""
        days_since = 0
        if recruiter.last_contact_date:
            days_since = (datetime.utcnow() - recruiter.last_contact_date).days

        # Count pending actions (simplified)
        pending_actions = 0
        if recruiter.next_action:
            pending_actions = 1
        if not recruiter.has_responded and recruiter.messages_sent:
            pending_actions += 1

        score = calculate_priority_score(
            days_since_contact=days_since,
            pending_actions=pending_actions,
            engagement_score=recruiter.engagement_score or 50,
            fit_score=recruiter.fit_score or 50,
            has_responded=recruiter.has_responded or False,
            status=recruiter.status or "new",
        )

        recruiter.priority_score = score

    @staticmethod
    def add_note(
        recruiter_id: str,
        user_id: str,
        content: str,
        note_type: str = "general",
    ) -> RecruiterNote:
        """
        Add a note to a recruiter.

        Args:
            recruiter_id: Recruiter ID
            user_id: User ID
            content: Note content
            note_type: Type of note (general, call, email, meeting, research)

        Returns:
            New RecruiterNote object
        """
        recruiter = RecruiterService.get_recruiter(recruiter_id, user_id)
        if not recruiter:
            raise ValueError("Recruiter not found")

        note = RecruiterNote(
            recruiter_id=recruiter_id,
            content=content,
            note_type=note_type,
        )

        db.session.add(note)
        db.session.commit()

        return note

    @staticmethod
    def get_notes(recruiter_id: str, user_id: str) -> List[RecruiterNote]:
        """Get all notes for a recruiter."""
        recruiter = RecruiterService.get_recruiter(recruiter_id, user_id)
        if not recruiter:
            raise ValueError("Recruiter not found")

        return (
            RecruiterNote.query.filter_by(recruiter_id=recruiter_id)
            .order_by(RecruiterNote.created_at.desc())
            .all()
        )

    @staticmethod
    def set_next_action(
        recruiter_id: str,
        user_id: str,
        action: str,
        due_date: Optional[datetime] = None,
    ) -> Recruiter:
        """
        Set next action for a recruiter.

        Args:
            recruiter_id: Recruiter ID
            user_id: User ID
            action: Description of next action
            due_date: When action is due

        Returns:
            Updated Recruiter object
        """
        recruiter = RecruiterService.get_recruiter(recruiter_id, user_id)
        if not recruiter:
            raise ValueError("Recruiter not found")

        recruiter.next_action = action
        recruiter.next_action_date = due_date

        # Update pipeline item
        pipeline_item = PipelineItem.query.filter_by(recruiter_id=recruiter_id).first()

        if pipeline_item:
            pipeline_item.next_action = action
            pipeline_item.next_action_date = due_date

        RecruiterService._update_priority_score(recruiter)

        db.session.commit()

        return recruiter

    @staticmethod
    def get_follow_up_recommendations(user_id: str, limit: int = 10) -> List[Dict]:
        """
        Get recommended follow-up actions sorted by priority.

        Returns recruiters needing follow-up with action suggestions.
        """
        recruiters = (
            Recruiter.query.filter_by(user_id=user_id)
            .filter(
                Recruiter.status.in_(
                    [
                        PipelineStage.CONTACTED.value,
                        PipelineStage.RESPONDED.value,
                        PipelineStage.INTERVIEWING.value,
                    ]
                )
            )
            .order_by(Recruiter.priority_score.desc())
            .limit(limit)
            .all()
        )

        recommendations = []
        for recruiter in recruiters:
            days_since = 0
            if recruiter.last_contact_date:
                days_since = (datetime.utcnow() - recruiter.last_contact_date).days

            action = RecruiterService._suggest_action(recruiter, days_since)

            recommendations.append(
                {
                    "recruiter_id": str(recruiter.id),
                    "recruiter_name": recruiter.full_name,
                    "company": recruiter.company,
                    "status": recruiter.status,
                    "priority_score": recruiter.priority_score,
                    "days_since_contact": days_since,
                    "suggested_action": action["action"],
                    "action_type": action["type"],
                    "urgency": action["urgency"],
                }
            )

        return recommendations

    @staticmethod
    def _suggest_action(recruiter: Recruiter, days_since: int) -> Dict:
        """Generate action suggestion based on recruiter state."""
        if recruiter.status == PipelineStage.RESPONDED.value:
            return {
                "action": "Schedule a call to discuss opportunities",
                "type": "schedule_call",
                "urgency": "high" if days_since > 2 else "medium",
            }

        if recruiter.status == PipelineStage.INTERVIEWING.value:
            return {
                "action": "Send thank you note if interview completed",
                "type": "thank_you",
                "urgency": "high",
            }

        if not recruiter.has_responded:
            if days_since >= 7:
                return {
                    "action": "Send follow-up message",
                    "type": "follow_up",
                    "urgency": "high" if days_since >= 14 else "medium",
                }
            elif days_since >= 3:
                return {
                    "action": "Consider sending follow-up in a few days",
                    "type": "follow_up",
                    "urgency": "low",
                }

        return {
            "action": "Review and update recruiter information",
            "type": "research",
            "urgency": "low",
        }

    @staticmethod
    def get_pipeline_stats(user_id: str) -> Dict:
        """Get pipeline statistics for dashboard."""
        stats = {
            "total": 0,
            "by_stage": {},
            "response_rate": 0,
            "avg_engagement": 0,
            "avg_fit": 0,
        }

        recruiters = Recruiter.query.filter_by(user_id=user_id).all()
        stats["total"] = len(recruiters)

        if not recruiters:
            return stats

        # Count by stage
        for stage in PipelineStage:
            count = sum(1 for r in recruiters if r.status == stage.value)
            stats["by_stage"][stage.value] = count

        # Calculate response rate
        total_contacted = sum(1 for r in recruiters if r.messages_sent and r.messages_sent > 0)
        total_responded = sum(1 for r in recruiters if r.has_responded)
        if total_contacted > 0:
            stats["response_rate"] = round((total_responded / total_contacted) * 100, 1)

        # Calculate averages
        engagement_scores = [r.engagement_score for r in recruiters if r.engagement_score]
        fit_scores = [r.fit_score for r in recruiters if r.fit_score]

        if engagement_scores:
            stats["avg_engagement"] = round(sum(engagement_scores) / len(engagement_scores), 1)
        if fit_scores:
            stats["avg_fit"] = round(sum(fit_scores) / len(fit_scores), 1)

        return stats
