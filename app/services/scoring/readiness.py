"""
Career Readiness Score Calculator

Calculates how prepared a user is for their job search.

Formula:
readiness = profile(20%) + resume(25%) + network(20%) + activity(15%) + response(20%)
"""

from typing import Dict, List, Optional

# Readiness Score Weights
READINESS_WEIGHTS = {
    "profile": 20,
    "resume": 25,
    "network": 20,
    "activity": 15,
    "response": 20,
}

# Profile fields and their importance
PROFILE_FIELDS = {
    "required": [
        "first_name",
        "last_name",
        "email",
        "location",
    ],
    "important": [
        "years_experience",
        "career_stage",
        "current_role",
        "linkedin_url",
    ],
    "recommended": [
        "target_roles",
        "target_industries",
        "technical_skills",
        "salary_expectation",
    ],
}

# Optimal recruiter count for active pipeline
OPTIMAL_RECRUITER_COUNT = 10
MIN_RECRUITER_COUNT = 3

# Weekly outreach targets
WEEKLY_MESSAGE_TARGET = 5


def calculate_career_readiness(
    profile_completeness: float,
    resume_ats_score: Optional[int],
    has_resume: bool,
    active_recruiters: int,
    messages_this_week: int,
    response_rate: float,
    career_stage: str = "mid_level",
) -> Dict:
    """
    Calculate overall career readiness score.

    Args:
        profile_completeness: Percentage of profile completed (0-1)
        resume_ats_score: Latest resume ATS score (0-100)
        has_resume: Whether user has uploaded a resume
        active_recruiters: Number of recruiters not in declined/accepted status
        messages_this_week: Outreach messages sent this week
        response_rate: User's response rate (0-1)
        career_stage: User's career stage for benchmarking

    Returns:
        Dictionary with total score and component breakdown
    """
    # Calculate each component
    profile_score = _calculate_profile_score(profile_completeness)
    resume_score = _calculate_resume_score(resume_ats_score, has_resume)
    network_score = _calculate_network_score(active_recruiters)
    activity_score = _calculate_activity_score(messages_this_week)
    response_score = _calculate_response_score(response_rate, career_stage)

    # Calculate weighted total
    total_score = int(
        profile_score * (READINESS_WEIGHTS["profile"] / 100)
        + resume_score * (READINESS_WEIGHTS["resume"] / 100)
        + network_score * (READINESS_WEIGHTS["network"] / 100)
        + activity_score * (READINESS_WEIGHTS["activity"] / 100)
        + response_score * (READINESS_WEIGHTS["response"] / 100)
    )

    # Generate recommendations
    recommendations = _generate_recommendations(
        profile_score,
        resume_score,
        network_score,
        activity_score,
        response_score,
        profile_completeness,
        resume_ats_score,
        has_resume,
        active_recruiters,
        messages_this_week,
        response_rate,
    )

    return {
        "total_score": total_score,
        "components": {
            "profile": profile_score,
            "resume": resume_score,
            "network": network_score,
            "activity": activity_score,
            "response": response_score,
        },
        "recommendations": recommendations,
        "next_actions": _get_priority_actions(
            profile_score, resume_score, network_score, activity_score
        ),
    }


def _calculate_profile_score(completeness: float) -> int:
    """Score based on profile completeness percentage."""
    return min(100, int(completeness * 100))


def _calculate_resume_score(ats_score: Optional[int], has_resume: bool) -> int:
    """Score based on resume quality."""
    if not has_resume:
        return 0

    if ats_score is None:
        return 40  # Resume uploaded but not analyzed

    return ats_score


def _calculate_network_score(active_recruiters: int) -> int:
    """
    Score based on active recruiter pipeline.

    Optimal is around 10 active recruiters.
    """
    if active_recruiters == 0:
        return 0
    elif active_recruiters >= OPTIMAL_RECRUITER_COUNT:
        return 100
    elif active_recruiters >= MIN_RECRUITER_COUNT:
        # Linear interpolation
        progress = (active_recruiters - MIN_RECRUITER_COUNT) / (
            OPTIMAL_RECRUITER_COUNT - MIN_RECRUITER_COUNT
        )
        return int(50 + (progress * 50))
    else:
        return int((active_recruiters / MIN_RECRUITER_COUNT) * 50)


def _calculate_activity_score(messages_this_week: int) -> int:
    """
    Score based on weekly outreach activity.

    Target: 5 messages per week.
    """
    if messages_this_week == 0:
        return 0
    elif messages_this_week >= WEEKLY_MESSAGE_TARGET:
        return 100
    else:
        return int((messages_this_week / WEEKLY_MESSAGE_TARGET) * 100)


def _calculate_response_score(response_rate: float, career_stage: str) -> int:
    """
    Score based on response rate vs career stage benchmark.

    Benchmarks by career stage:
    - entry_level: 8-12%
    - early_career: 15-20%
    - mid_level: 20-30%
    - senior: 15-25%
    - executive: 10-20%
    """
    benchmarks = {
        "entry_level": 0.10,
        "early_career": 0.18,
        "mid_level": 0.25,
        "senior": 0.20,
        "executive": 0.15,
    }

    benchmark = benchmarks.get(career_stage, 0.20)

    if response_rate == 0:
        return 20  # No responses yet

    # Score as percentage of benchmark, capped at 150%
    ratio = min(1.5, response_rate / benchmark)
    return int(ratio * 66.67)  # 150% = 100 points


def _generate_recommendations(
    profile_score: int,
    resume_score: int,
    network_score: int,
    activity_score: int,
    response_score: int,
    profile_completeness: float,
    resume_ats_score: Optional[int],
    has_resume: bool,
    active_recruiters: int,
    messages_this_week: int,
    response_rate: float,
) -> List[str]:
    """Generate personalized recommendations based on scores."""
    recommendations = []

    # Profile recommendations
    if profile_score < 80:
        missing_pct = 100 - int(profile_completeness * 100)
        recommendations.append(
            f"Complete your profile ({missing_pct}% remaining) to improve job matches"
        )

    # Resume recommendations
    if not has_resume:
        recommendations.append("Upload your resume to get ATS optimization feedback")
    elif resume_ats_score and resume_ats_score < 70:
        recommendations.append(
            f"Improve your ATS score (currently {resume_ats_score}/100) with recommended changes"
        )

    # Network recommendations
    if active_recruiters == 0:
        recommendations.append("Add recruiters to your pipeline to start building connections")
    elif active_recruiters < OPTIMAL_RECRUITER_COUNT:
        more_needed = OPTIMAL_RECRUITER_COUNT - active_recruiters
        recommendations.append(f"Add {more_needed} more recruiters to reach optimal pipeline size")

    # Activity recommendations
    if messages_this_week < WEEKLY_MESSAGE_TARGET:
        more_needed = WEEKLY_MESSAGE_TARGET - messages_this_week
        recommendations.append(f"Send {more_needed} more messages this week to stay on track")

    # Response recommendations
    if response_rate < 0.10 and messages_this_week > 5:
        recommendations.append("Review your message templates - response rate is below average")

    return recommendations[:5]  # Top 5 recommendations


def _get_priority_actions(
    profile_score: int,
    resume_score: int,
    network_score: int,
    activity_score: int,
) -> List[Dict]:
    """Get prioritized action items."""
    actions = []

    if resume_score < 50:
        actions.append(
            {
                "action": "upload_resume" if resume_score == 0 else "improve_resume",
                "priority": "high",
                "impact": "Resume is critical for job applications",
            }
        )

    if profile_score < 70:
        actions.append(
            {
                "action": "complete_profile",
                "priority": "high" if profile_score < 50 else "medium",
                "impact": "Complete profiles get better matches",
            }
        )

    if network_score < 30:
        actions.append(
            {
                "action": "add_recruiters",
                "priority": "medium",
                "impact": "Build your recruiter network",
            }
        )

    if activity_score < 50:
        actions.append(
            {
                "action": "send_messages",
                "priority": "medium",
                "impact": "Consistent outreach improves results",
            }
        )

    return sorted(actions, key=lambda x: 0 if x["priority"] == "high" else 1)


def calculate_profile_completeness(user_data: Dict) -> float:
    """
    Calculate what percentage of the profile is complete.

    Args:
        user_data: Dictionary of user profile fields

    Returns:
        Completeness percentage (0.0 to 1.0)
    """
    total_weight = 0
    filled_weight = 0

    # Required fields (weight: 3)
    for field in PROFILE_FIELDS["required"]:
        total_weight += 3
        if user_data.get(field):
            filled_weight += 3

    # Important fields (weight: 2)
    for field in PROFILE_FIELDS["important"]:
        total_weight += 2
        value = user_data.get(field)
        if value is not None and value != "" and value != []:
            filled_weight += 2

    # Recommended fields (weight: 1)
    for field in PROFILE_FIELDS["recommended"]:
        total_weight += 1
        value = user_data.get(field)
        if value is not None and value != "" and value != []:
            filled_weight += 1

    return filled_weight / total_weight if total_weight > 0 else 0.0
