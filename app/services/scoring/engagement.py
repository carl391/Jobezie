"""
Engagement & Fit Scoring Algorithms

Calculates recruiter engagement score and fit score.

Engagement Formula:
engagement = response_rate(40%) + open_rate(30%) + recency(30%)

Fit Formula:
fit = industry(30%) + location(20%) + specialty(25%) + tier(15%) + depth(10%)
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


# Engagement Score Weights
ENGAGEMENT_WEIGHTS = {
    'response_rate': 40,
    'open_rate': 30,
    'recency': 30,
}

# Fit Score Weights
FIT_WEIGHTS = {
    'industry': 30,
    'location': 20,
    'specialty': 25,
    'tier': 15,
    'depth': 10,
}

# Recency decay parameters (days)
RECENCY_DECAY = {
    'fresh': 7,      # Full score within 7 days
    'warm': 14,      # 75% score within 14 days
    'cooling': 30,   # 50% score within 30 days
    'cold': 60,      # 25% score within 60 days
}


def calculate_engagement_score(
    messages_sent: int,
    messages_opened: int,
    responses_received: int,
    last_contact_date: Optional[datetime] = None,
) -> Dict:
    """
    Calculate recruiter engagement score.

    Args:
        messages_sent: Total messages sent to recruiter
        messages_opened: Messages that were opened
        responses_received: Responses received from recruiter
        last_contact_date: Date of last contact

    Returns:
        Dictionary with total score and component breakdown
    """
    # Calculate response rate score
    response_score = _calculate_response_rate_score(messages_sent, responses_received)

    # Calculate open rate score
    open_score = _calculate_open_rate_score(messages_sent, messages_opened)

    # Calculate recency score
    recency_score = _calculate_recency_score(last_contact_date)

    # Calculate weighted total
    total_score = int(
        response_score * (ENGAGEMENT_WEIGHTS['response_rate'] / 100) +
        open_score * (ENGAGEMENT_WEIGHTS['open_rate'] / 100) +
        recency_score * (ENGAGEMENT_WEIGHTS['recency'] / 100)
    )

    return {
        'total_score': total_score,
        'components': {
            'response_rate': response_score,
            'open_rate': open_score,
            'recency': recency_score,
        },
        'metrics': {
            'messages_sent': messages_sent,
            'messages_opened': messages_opened,
            'responses_received': responses_received,
            'response_rate': round((responses_received / messages_sent * 100) if messages_sent > 0 else 0, 1),
            'open_rate': round((messages_opened / messages_sent * 100) if messages_sent > 0 else 0, 1),
        }
    }


def _calculate_response_rate_score(messages_sent: int, responses_received: int) -> int:
    """
    Score based on response rate.

    Benchmarks (from recruiter research):
    - Entry level: 8-12% good
    - Mid level: 25-35% good
    - Senior level: 15-25% good

    We use a general benchmark of 20% as good.
    """
    if messages_sent == 0:
        return 50  # No data yet

    response_rate = responses_received / messages_sent

    if response_rate >= 0.40:
        return 100
    elif response_rate >= 0.25:
        return 85
    elif response_rate >= 0.15:
        return 70
    elif response_rate >= 0.08:
        return 55
    elif response_rate >= 0.01:
        return 40
    else:
        return 25


def _calculate_open_rate_score(messages_sent: int, messages_opened: int) -> int:
    """
    Score based on email open rate.

    Benchmark: 24% average, 44% with personalization.
    """
    if messages_sent == 0:
        return 50  # No data yet

    open_rate = messages_opened / messages_sent

    if open_rate >= 0.60:
        return 100
    elif open_rate >= 0.44:
        return 85
    elif open_rate >= 0.30:
        return 70
    elif open_rate >= 0.20:
        return 55
    else:
        return 40


def _calculate_recency_score(last_contact_date: Optional[datetime]) -> int:
    """
    Score based on how recently recruiter was contacted.

    Uses decay function - more recent = higher score.
    """
    if not last_contact_date:
        return 0  # Never contacted

    days_since = (datetime.utcnow() - last_contact_date).days

    if days_since <= RECENCY_DECAY['fresh']:
        return 100
    elif days_since <= RECENCY_DECAY['warm']:
        return 75
    elif days_since <= RECENCY_DECAY['cooling']:
        return 50
    elif days_since <= RECENCY_DECAY['cold']:
        return 25
    else:
        return 10


def calculate_fit_score(
    user_industries: List[str],
    user_location: Optional[str],
    user_target_roles: List[str],
    user_salary_expectation: Optional[int],
    recruiter_industries: List[str],
    recruiter_locations: List[str],
    recruiter_specialty: Optional[str],
    recruiter_company_type: Optional[str],
    recruiter_salary_range: Optional[Tuple[int, int]] = None,
) -> Dict:
    """
    Calculate how well a recruiter fits the user's job search.

    Args:
        user_industries: User's target industries
        user_location: User's location/preference
        user_target_roles: User's target job roles
        user_salary_expectation: User's salary expectation
        recruiter_industries: Industries recruiter works in
        recruiter_locations: Locations recruiter covers
        recruiter_specialty: Recruiter's role specialty
        recruiter_company_type: Agency, corporate, executive search
        recruiter_salary_range: Salary range recruiter typically handles

    Returns:
        Dictionary with total score and component breakdown
    """
    # Calculate each component
    industry_score = _calculate_industry_fit(user_industries, recruiter_industries)
    location_score = _calculate_location_fit(user_location, recruiter_locations)
    specialty_score = _calculate_specialty_fit(user_target_roles, recruiter_specialty)
    tier_score = _calculate_tier_fit(user_salary_expectation, recruiter_company_type, recruiter_salary_range)
    depth_score = _calculate_depth_score(
        recruiter_industries, recruiter_locations, recruiter_specialty
    )

    # Calculate weighted total
    total_score = int(
        industry_score * (FIT_WEIGHTS['industry'] / 100) +
        location_score * (FIT_WEIGHTS['location'] / 100) +
        specialty_score * (FIT_WEIGHTS['specialty'] / 100) +
        tier_score * (FIT_WEIGHTS['tier'] / 100) +
        depth_score * (FIT_WEIGHTS['depth'] / 100)
    )

    return {
        'total_score': total_score,
        'components': {
            'industry': industry_score,
            'location': location_score,
            'specialty': specialty_score,
            'tier': tier_score,
            'depth': depth_score,
        }
    }


def _calculate_industry_fit(user_industries: List[str], recruiter_industries: List[str]) -> int:
    """Calculate industry overlap score."""
    if not user_industries or not recruiter_industries:
        return 50  # No data

    user_set = {i.lower() for i in user_industries}
    recruiter_set = {i.lower() for i in recruiter_industries}

    overlap = user_set.intersection(recruiter_set)

    if not overlap:
        return 20

    overlap_ratio = len(overlap) / len(user_set)

    if overlap_ratio >= 0.5:
        return 100
    elif overlap_ratio >= 0.25:
        return 75
    else:
        return 50


def _calculate_location_fit(user_location: Optional[str], recruiter_locations: List[str]) -> int:
    """Calculate location match score."""
    if not user_location or not recruiter_locations:
        return 70  # Assume remote/flexible

    user_loc = user_location.lower()
    recruiter_locs = [loc.lower() for loc in recruiter_locations]

    # Exact match
    if user_loc in recruiter_locs:
        return 100

    # Partial match (same state/region)
    user_parts = user_loc.replace(',', ' ').split()
    for recruiter_loc in recruiter_locs:
        recruiter_parts = recruiter_loc.replace(',', ' ').split()
        if any(part in recruiter_parts for part in user_parts if len(part) > 2):
            return 75

    # Check for remote/nationwide
    if any(term in ' '.join(recruiter_locs) for term in ['remote', 'nationwide', 'national', 'global']):
        return 80

    return 40


def _calculate_specialty_fit(user_target_roles: List[str], recruiter_specialty: Optional[str]) -> int:
    """Calculate role specialty match."""
    if not user_target_roles or not recruiter_specialty:
        return 50  # No data

    specialty_lower = recruiter_specialty.lower()
    roles_lower = [r.lower() for r in user_target_roles]

    # Check for direct matches
    for role in roles_lower:
        role_words = role.split()
        specialty_words = specialty_lower.split()

        # Any significant word overlap
        overlap = set(role_words).intersection(set(specialty_words))
        if overlap and any(len(w) > 3 for w in overlap):
            return 100

    # Check for related terms
    role_text = ' '.join(roles_lower)
    if any(term in specialty_lower for term in role_text.split() if len(term) > 4):
        return 70

    return 40


def _calculate_tier_fit(
    user_salary: Optional[int],
    recruiter_type: Optional[str],
    salary_range: Optional[Tuple[int, int]]
) -> int:
    """
    Calculate tier/level fit based on salary and recruiter type.

    Executive search firms typically handle senior roles.
    Staffing agencies may focus on entry-mid level.
    """
    score = 70  # Base score

    if user_salary and salary_range:
        min_sal, max_sal = salary_range
        if min_sal <= user_salary <= max_sal:
            score = 100
        elif user_salary > max_sal * 0.8 or user_salary < min_sal * 1.2:
            score = 60
        else:
            score = 40

    # Adjust based on recruiter type
    if recruiter_type:
        type_lower = recruiter_type.lower()
        if user_salary and user_salary > 150000:
            if 'executive' in type_lower or 'retained' in type_lower:
                score = min(100, score + 20)
        elif user_salary and user_salary < 60000:
            if 'staffing' in type_lower or 'temp' in type_lower:
                score = min(100, score + 10)

    return score


def _calculate_depth_score(
    industries: List[str],
    locations: List[str],
    specialty: Optional[str]
) -> int:
    """
    Score recruiter profile completeness/depth.

    Better profiles indicate more serious/professional recruiters.
    """
    score = 0

    if industries and len(industries) > 0:
        score += 30
        if len(industries) >= 2:
            score += 10

    if locations and len(locations) > 0:
        score += 30
        if len(locations) >= 2:
            score += 10

    if specialty:
        score += 20

    return min(100, score)


def calculate_priority_score(
    days_since_contact: int,
    pending_actions: int,
    engagement_score: int,
    fit_score: int,
    has_responded: bool,
    status: str,
) -> int:
    """
    Calculate priority score for follow-up recommendations.

    Formula:
    priority = days_since(30%) + pending(25%) + potential(20%) + research(15%) + response(10%)
    """
    # Days since contact (peaks at 5-7 days for follow-up)
    if days_since_contact < 0:
        days_score = 0  # Never contacted
    elif 5 <= days_since_contact <= 7:
        days_score = 100  # Optimal follow-up window
    elif days_since_contact < 5:
        days_score = 50  # Too soon
    elif days_since_contact <= 14:
        days_score = 80
    else:
        days_score = max(20, 100 - (days_since_contact - 7) * 3)

    # Pending actions
    pending_score = min(100, pending_actions * 25)

    # Potential (combined engagement + fit)
    potential_score = (engagement_score + fit_score) // 2

    # Response history bonus
    response_score = 100 if has_responded else 30

    # Status adjustment
    status_multiplier = {
        'new': 1.0,
        'researching': 0.8,
        'contacted': 1.2,
        'responded': 1.5,
        'interviewing': 1.3,
        'offer': 0.5,
        'accepted': 0.1,
        'declined': 0.1,
    }.get(status, 1.0)

    # Calculate weighted score
    raw_score = (
        days_score * 0.30 +
        pending_score * 0.25 +
        potential_score * 0.20 +
        30 * 0.15 +  # Research placeholder
        response_score * 0.10
    )

    return int(min(100, raw_score * status_multiplier))
