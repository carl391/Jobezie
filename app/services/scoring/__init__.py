"""
Jobezie Scoring Services

Algorithm-driven scoring modules for:
- ATS Resume Scoring
- Career Readiness
- Engagement Scoring
- Message Quality
- Shortage Score
- User Match
- Opportunity Score

All scoring is deterministic and algorithm-based (not AI-generated)
for transparency, consistency, and auditability.
"""

from app.services.scoring.ats import calculate_ats_score
from app.services.scoring.engagement import (
    calculate_engagement_score,
    calculate_fit_score,
    calculate_priority_score,
)
from app.services.scoring.message import (
    calculate_message_quality,
    validate_message_length,
)
from app.services.scoring.readiness import calculate_career_readiness

# Future imports when algorithms are implemented:
# from app.services.scoring.shortage import calculate_shortage_score
# from app.services.scoring.match import calculate_user_match
# from app.services.scoring.opportunity import calculate_opportunity_score

__all__ = [
    "calculate_ats_score",
    "calculate_career_readiness",
    "calculate_engagement_score",
    "calculate_fit_score",
    "calculate_priority_score",
    "calculate_message_quality",
    "validate_message_length",
]
