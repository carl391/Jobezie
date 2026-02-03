"""
Activity Service

Handles activity tracking, pipeline management, and Kanban board functionality.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from app.extensions import db
from app.models.activity import Activity, ActivityType, PipelineItem, PipelineStage
from app.models.recruiter import Recruiter
from app.services.scoring.engagement import calculate_priority_score


class ActivityService:
    """Service for activity tracking and pipeline management."""

    @staticmethod
    def log_activity(
        user_id: str,
        activity_type: str,
        description: Optional[str] = None,
        recruiter_id: Optional[str] = None,
        resume_id: Optional[str] = None,
        message_id: Optional[str] = None,
        extra_data: Optional[Dict] = None,
        pipeline_stage: Optional[str] = None,
        previous_stage: Optional[str] = None,
    ) -> Activity:
        """
        Log a new activity.

        Args:
            user_id: User's ID
            activity_type: Type of activity
            description: Human-readable description
            recruiter_id: Related recruiter ID
            resume_id: Related resume ID
            message_id: Related message ID
            extra_data: Additional context data
            pipeline_stage: Current pipeline stage (for stage changes)
            previous_stage: Previous stage (for stage changes)

        Returns:
            New Activity object
        """
        activity = Activity(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            recruiter_id=recruiter_id,
            resume_id=resume_id,
            message_id=message_id,
            extra_data=extra_data or {},
            pipeline_stage=pipeline_stage,
            previous_stage=previous_stage,
        )

        db.session.add(activity)
        db.session.commit()

        return activity

    @staticmethod
    def get_user_activities(
        user_id: str,
        activity_type: Optional[str] = None,
        recruiter_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Activity], int]:
        """
        Get activities for a user with filtering.

        Args:
            user_id: User's ID
            activity_type: Filter by activity type
            recruiter_id: Filter by recruiter
            start_date: Filter activities after this date
            end_date: Filter activities before this date
            limit: Maximum results
            offset: Pagination offset

        Returns:
            Tuple of (activity list, total count)
        """
        query = Activity.query.filter_by(user_id=user_id)

        if activity_type:
            query = query.filter_by(activity_type=activity_type)
        if recruiter_id:
            query = query.filter_by(recruiter_id=recruiter_id)
        if start_date:
            query = query.filter(Activity.created_at >= start_date)
        if end_date:
            query = query.filter(Activity.created_at <= end_date)

        total = query.count()

        activities = query.order_by(Activity.created_at.desc()).offset(offset).limit(limit).all()

        return activities, total

    @staticmethod
    def get_recent_activities(user_id: str, limit: int = 10) -> List[Activity]:
        """Get most recent activities for dashboard timeline."""
        return (
            Activity.query.filter_by(user_id=user_id)
            .order_by(Activity.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_activity_counts(user_id: str, days: int = 30) -> Dict:
        """
        Get activity counts by type for the specified period.

        Args:
            user_id: User's ID
            days: Number of days to look back

        Returns:
            Dictionary with counts by activity type
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        activities = Activity.query.filter(
            Activity.user_id == user_id, Activity.created_at >= start_date
        ).all()

        counts = {t.value: 0 for t in ActivityType}
        for activity in activities:
            if activity.activity_type in counts:
                counts[activity.activity_type] += 1

        return {
            "period_days": days,
            "total": len(activities),
            "by_type": counts,
        }

    # Pipeline / Kanban Management

    @staticmethod
    def get_pipeline(user_id: str) -> Dict[str, List[Dict]]:
        """
        Get full Kanban pipeline for a user.

        Returns:
            Dictionary with stage keys and lists of pipeline items
        """
        pipeline = {stage.value: [] for stage in PipelineStage}

        items = PipelineItem.query.filter_by(user_id=user_id).order_by(PipelineItem.position).all()

        for item in items:
            recruiter = Recruiter.query.get(item.recruiter_id)
            if recruiter:
                pipeline[item.stage].append(
                    {
                        "id": str(item.id),
                        "recruiter_id": str(item.recruiter_id),
                        "recruiter_name": recruiter.full_name,
                        "company": recruiter.company,
                        "position": item.position,
                        "priority_score": item.priority_score,
                        "days_in_stage": item.days_in_stage,
                        "last_activity_date": (
                            item.last_activity_date.isoformat() if item.last_activity_date else None
                        ),
                        "next_action": item.next_action,
                        "next_action_date": (
                            item.next_action_date.isoformat() if item.next_action_date else None
                        ),
                        "engagement_score": recruiter.engagement_score,
                        "fit_score": recruiter.fit_score,
                    }
                )

        return pipeline

    @staticmethod
    def move_pipeline_item(
        user_id: str,
        item_id: str,
        new_stage: str,
        new_position: Optional[int] = None,
    ) -> PipelineItem:
        """
        Move a pipeline item to a new stage or position.

        Args:
            user_id: User's ID for verification
            item_id: Pipeline item ID
            new_stage: Target stage
            new_position: Position within stage (optional)

        Returns:
            Updated PipelineItem
        """
        item = PipelineItem.query.filter_by(id=item_id, user_id=user_id).first()

        if not item:
            raise ValueError("Pipeline item not found")

        # Validate stage
        valid_stages = [s.value for s in PipelineStage]
        if new_stage not in valid_stages:
            raise ValueError(f"Invalid stage: {new_stage}")

        old_stage = item.stage

        # Update stage if changed
        if old_stage != new_stage:
            item.stage = new_stage
            item.entered_stage_at = datetime.utcnow()
            item.days_in_stage = 0

            # Log stage change activity
            ActivityService.log_activity(
                user_id=user_id,
                activity_type=ActivityType.STATUS_CHANGE.value,
                description=f"Moved to {new_stage}",
                recruiter_id=item.recruiter_id,
                pipeline_stage=new_stage,
                previous_stage=old_stage,
            )

            # Update recruiter status
            recruiter = Recruiter.query.get(item.recruiter_id)
            if recruiter:
                recruiter.status = new_stage

        # Update position
        if new_position is not None:
            # Reorder items in the stage
            items_in_stage = (
                PipelineItem.query.filter_by(user_id=user_id, stage=new_stage)
                .filter(PipelineItem.id != item_id)
                .order_by(PipelineItem.position)
                .all()
            )

            # Insert at new position
            for i, other_item in enumerate(items_in_stage):
                if i >= new_position:
                    other_item.position = i + 1
                else:
                    other_item.position = i

            item.position = new_position
        else:
            # Add to end of stage
            max_pos = (
                db.session.query(db.func.max(PipelineItem.position))
                .filter_by(user_id=user_id, stage=new_stage)
                .scalar()
                or -1
            )
            item.position = max_pos + 1

        item.updated_at = datetime.utcnow()
        db.session.commit()

        return item

    @staticmethod
    def update_days_in_stage(user_id: str) -> int:
        """
        Update days_in_stage for all pipeline items.

        Should be run periodically (e.g., daily).

        Returns:
            Number of items updated
        """
        items = PipelineItem.query.filter_by(user_id=user_id).all()

        count = 0
        for item in items:
            if item.entered_stage_at:
                days = (datetime.utcnow() - item.entered_stage_at).days
                if days != item.days_in_stage:
                    item.days_in_stage = days
                    count += 1

        db.session.commit()
        return count

    @staticmethod
    def update_priority_scores(user_id: str) -> int:
        """
        Recalculate priority scores for all pipeline items.

        Should be run periodically or after significant changes.

        Returns:
            Number of items updated
        """
        items = PipelineItem.query.filter_by(user_id=user_id).all()

        count = 0
        for item in items:
            recruiter = Recruiter.query.get(item.recruiter_id)
            if not recruiter:
                continue

            days_since = 0
            if recruiter.last_contact_date:
                days_since = (datetime.utcnow() - recruiter.last_contact_date).days

            pending_actions = 1 if item.next_action else 0

            new_score = calculate_priority_score(
                days_since_contact=days_since,
                pending_actions=pending_actions,
                engagement_score=recruiter.engagement_score or 50,
                fit_score=recruiter.fit_score or 50,
                has_responded=recruiter.has_responded or False,
                status=item.stage,
            )

            if new_score != item.priority_score:
                item.priority_score = new_score
                recruiter.priority_score = new_score
                count += 1

        db.session.commit()
        return count

    @staticmethod
    def get_pipeline_stats(user_id: str) -> Dict:
        """
        Get pipeline statistics for dashboard.

        Returns:
            Dictionary with stage counts and metrics
        """
        stats = {
            "total": 0,
            "by_stage": {},
            "avg_days_in_stage": {},
            "items_needing_action": 0,
            "stale_items": 0,  # No activity in 14+ days
        }

        items = PipelineItem.query.filter_by(user_id=user_id).all()
        stats["total"] = len(items)

        # Initialize stage counts
        for stage in PipelineStage:
            stats["by_stage"][stage.value] = 0
            stats["avg_days_in_stage"][stage.value] = 0

        if not items:
            return stats

        # Calculate metrics
        stage_days = {stage.value: [] for stage in PipelineStage}

        for item in items:
            stats["by_stage"][item.stage] += 1
            stage_days[item.stage].append(item.days_in_stage or 0)

            if item.next_action:
                stats["items_needing_action"] += 1

            if item.days_in_stage and item.days_in_stage >= 14:
                stats["stale_items"] += 1

        # Calculate averages
        for stage, days_list in stage_days.items():
            if days_list:
                stats["avg_days_in_stage"][stage] = round(sum(days_list) / len(days_list), 1)

        return stats

    @staticmethod
    def get_activity_timeline(
        user_id: str,
        recruiter_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict]:
        """
        Get activity timeline for display.

        Args:
            user_id: User's ID
            recruiter_id: Optional filter by recruiter
            limit: Maximum items to return

        Returns:
            List of timeline items with formatted data
        """
        query = Activity.query.filter_by(user_id=user_id)

        if recruiter_id:
            query = query.filter_by(recruiter_id=recruiter_id)

        activities = query.order_by(Activity.created_at.desc()).limit(limit).all()

        timeline = []
        for activity in activities:
            item = {
                "id": str(activity.id),
                "type": activity.activity_type,
                "description": activity.description
                or ActivityService._get_default_description(activity),
                "timestamp": activity.created_at.isoformat(),
                "recruiter_id": (str(activity.recruiter_id) if activity.recruiter_id else None),
                "extra_data": activity.extra_data,
            }

            # Add recruiter name if available
            if activity.recruiter_id:
                recruiter = Recruiter.query.get(activity.recruiter_id)
                if recruiter:
                    item["recruiter_name"] = recruiter.full_name
                    item["company"] = recruiter.company

            timeline.append(item)

        return timeline

    @staticmethod
    def _get_default_description(activity: Activity) -> str:
        """Generate default description based on activity type."""
        descriptions = {
            ActivityType.RECRUITER_ADDED.value: "Added new recruiter",
            ActivityType.MESSAGE_SENT.value: "Sent outreach message",
            ActivityType.MESSAGE_OPENED.value: "Message was opened",
            ActivityType.RESPONSE_RECEIVED.value: "Received response",
            ActivityType.INTERVIEW_SCHEDULED.value: "Interview scheduled",
            ActivityType.INTERVIEW_COMPLETED.value: "Interview completed",
            ActivityType.OFFER_RECEIVED.value: "Received offer",
            ActivityType.OFFER_ACCEPTED.value: "Accepted offer",
            ActivityType.OFFER_DECLINED.value: "Declined offer",
            ActivityType.STATUS_CHANGE.value: f"Status changed to {activity.pipeline_stage}",
            ActivityType.RESUME_UPLOADED.value: "Uploaded resume",
            ActivityType.RESUME_TAILORED.value: "Created tailored resume",
            ActivityType.RESEARCH_COMPLETED.value: "Completed research",
            ActivityType.FOLLOW_UP_SENT.value: "Sent follow-up",
            ActivityType.NOTE_ADDED.value: "Added note",
        }

        return descriptions.get(activity.activity_type, "Activity recorded")

    @staticmethod
    def get_weekly_summary(user_id: str) -> Dict:
        """
        Get weekly activity summary for dashboard.

        Returns:
            Dictionary with weekly metrics and highlights
        """
        start_of_week = datetime.utcnow() - timedelta(days=7)

        activities = Activity.query.filter(
            Activity.user_id == user_id, Activity.created_at >= start_of_week
        ).all()

        summary = {
            "total_activities": len(activities),
            "messages_sent": 0,
            "responses_received": 0,
            "interviews_scheduled": 0,
            "recruiters_added": 0,
            "resumes_tailored": 0,
            "highlights": [],
        }

        for activity in activities:
            if activity.activity_type == ActivityType.MESSAGE_SENT.value:
                summary["messages_sent"] += 1
            elif activity.activity_type == ActivityType.RESPONSE_RECEIVED.value:
                summary["responses_received"] += 1
            elif activity.activity_type == ActivityType.INTERVIEW_SCHEDULED.value:
                summary["interviews_scheduled"] += 1
            elif activity.activity_type == ActivityType.RECRUITER_ADDED.value:
                summary["recruiters_added"] += 1
            elif activity.activity_type == ActivityType.RESUME_TAILORED.value:
                summary["resumes_tailored"] += 1

        # Generate highlights
        if summary["responses_received"] > 0:
            summary["highlights"].append(f"Received {summary['responses_received']} response(s)")
        if summary["interviews_scheduled"] > 0:
            summary["highlights"].append(
                f"Scheduled {summary['interviews_scheduled']} interview(s)"
            )
        if summary["messages_sent"] > 5:
            summary["highlights"].append(
                f"Sent {summary['messages_sent']} messages - great outreach!"
            )

        return summary
