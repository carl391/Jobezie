"""
Message Quality Scoring Algorithm

Calculates outreach message effectiveness based on research-backed criteria.

Formula:
quality = words(25%) + personalization(25%) + metrics(25%) + cta(20%) + tone(5%)

Research Backing:
- < 150 words = 22% higher response rate
- Name + company personalization = 15% higher response
- Quantified achievements = 40% more interviews
"""

import re
from typing import Dict, List, Optional, Tuple

# Message Quality Weights (must sum to 100)
MESSAGE_WEIGHTS = {
    "words": 25,
    "personalization": 25,
    "metrics": 25,
    "cta": 20,
    "tone": 5,
}

# Optimal message lengths by type
OPTIMAL_LENGTHS = {
    "initial_outreach": (100, 150),
    "follow_up": (50, 75),
    "thank_you": (100, 125),
    "check_in": (50, 100),
}

# Call-to-action patterns
CTA_PATTERNS = [
    r"would you be (?:open|available|willing|interested)",
    r"could we (?:schedule|set up|arrange|connect)",
    r"i\'d (?:love|like|appreciate|welcome) to (?:discuss|chat|talk|connect)",
    r"do you have (?:time|availability|a moment)",
    r"let me know if",
    r"please (?:let me know|feel free)",
    r"when (?:would be|is) a good time",
    r"available for a (?:call|chat|conversation|discussion)",
]

# Formal/professional phrases
PROFESSIONAL_PHRASES = [
    "i hope this message finds you well",
    "thank you for your time",
    "i appreciate your consideration",
    "looking forward to",
    "please do not hesitate",
    "at your earliest convenience",
    "best regards",
    "sincerely",
]

# Personalization indicators
PERSONALIZATION_TYPES = {
    "name": r"\b(?:Hi|Dear|Hello)\s+[A-Z][a-z]+",
    "company": r"at\s+[A-Z][A-Za-z\s]+|company\s+like\s+[A-Z]",
    "role": r"(?:your|the)\s+(?:role|position|work)\s+(?:as|in|at)",
    "recent_work": r"(?:recent|latest|your)\s+(?:work|project|article|post|achievement)",
    "mutual": r"(?:mutual|shared|common)\s+(?:connection|colleague|friend)",
    "specific_detail": r"(?:noticed|saw|read|impressed by|interested in)\s+(?:your|the)",
}


def calculate_message_quality(
    message_text: str,
    message_type: str = "initial_outreach",
    recruiter_name: Optional[str] = None,
    company_name: Optional[str] = None,
) -> Dict:
    """
    Calculate message quality score.

    Args:
        message_text: The message content
        message_type: Type of message (initial_outreach, follow_up, thank_you, check_in)
        recruiter_name: Recruiter's name for personalization check
        company_name: Company name for personalization check

    Returns:
        Dictionary with total score, component scores, and feedback
    """
    if not message_text:
        return {
            "total_score": 0,
            "word_count": 0,
            "components": {k: 0 for k in MESSAGE_WEIGHTS.keys()},
            "feedback": ["Message is empty"],
            "suggestions": ["Write a personalized outreach message"],
            "has_personalization": False,
            "has_metrics": False,
            "has_cta": False,
            "personalization_elements": [],
        }

    # Calculate each component
    words_score, word_count, words_feedback = _score_word_count(message_text, message_type)
    personal_score, personal_elements, personal_feedback = _score_personalization(
        message_text, recruiter_name, company_name
    )
    metrics_score, metrics_feedback = _score_metrics(message_text)
    cta_score, has_cta, cta_feedback = _score_cta(message_text)
    tone_score, tone_feedback = _score_tone(message_text, message_type)

    # Calculate weighted total
    total_score = int(
        words_score * (MESSAGE_WEIGHTS["words"] / 100)
        + personal_score * (MESSAGE_WEIGHTS["personalization"] / 100)
        + metrics_score * (MESSAGE_WEIGHTS["metrics"] / 100)
        + cta_score * (MESSAGE_WEIGHTS["cta"] / 100)
        + tone_score * (MESSAGE_WEIGHTS["tone"] / 100)
    )

    # Compile feedback
    feedback = []
    suggestions = []

    for item in (
        words_feedback + personal_feedback + metrics_feedback + cta_feedback + tone_feedback
    ):
        if item.startswith("✓"):
            feedback.append(item)
        else:
            suggestions.append(item)

    return {
        "total_score": total_score,
        "word_count": word_count,
        "components": {
            "words": words_score,
            "personalization": personal_score,
            "metrics": metrics_score,
            "cta": cta_score,
            "tone": tone_score,
        },
        "feedback": feedback[:5],
        "suggestions": suggestions[:5],
        "has_personalization": len(personal_elements) > 0,
        "has_metrics": metrics_score >= 50,
        "has_cta": has_cta,
        "personalization_elements": personal_elements,
    }


def _score_word_count(message_text: str, message_type: str) -> Tuple[int, int, List[str]]:
    """
    Score message length against optimal range.

    Research shows <150 words = 22% higher response rate for outreach.
    """
    feedback = []
    word_count = len(message_text.split())

    min_words, max_words = OPTIMAL_LENGTHS.get(message_type, (100, 150))

    if min_words <= word_count <= max_words:
        score = 100
        feedback.append(f"✓ Perfect length ({word_count} words)")
    elif word_count < min_words:
        # Too short
        deficit = min_words - word_count
        score = max(0, 100 - (deficit * 3))
        feedback.append(
            f"Add {deficit} more words for optimal length ({min_words}-{max_words} words)"
        )
    else:
        # Too long
        excess = word_count - max_words
        score = max(0, 100 - (excess * 2))
        if word_count > 150:
            feedback.append(
                f"Reduce to under 150 words for 22% higher response rate (currently {word_count})"
            )
        else:
            feedback.append(f"Consider shortening to {max_words} words or less")

    return score, word_count, feedback


def _score_personalization(
    message_text: str, recruiter_name: Optional[str], company_name: Optional[str]
) -> Tuple[int, List[str], List[str]]:
    """
    Score personalization level.

    Checks for name, company, role, recent work, and specific details.
    """
    feedback = []
    elements_found = []
    score = 0

    message_lower = message_text.lower()

    # Check for recruiter name
    if recruiter_name and recruiter_name.lower() in message_lower:
        score += 30
        elements_found.append("recruiter_name")
    elif re.search(PERSONALIZATION_TYPES["name"], message_text):
        score += 20
        elements_found.append("greeting_with_name")
    else:
        feedback.append("Address the recruiter by name for better response rate")

    # Check for company name
    if company_name and company_name.lower() in message_lower:
        score += 30
        elements_found.append("company_name")
    elif re.search(PERSONALIZATION_TYPES["company"], message_text, re.IGNORECASE):
        score += 20
        elements_found.append("company_mention")
    else:
        feedback.append("Mention the company name to show genuine interest")

    # Check for other personalization elements
    if re.search(PERSONALIZATION_TYPES["recent_work"], message_lower):
        score += 20
        elements_found.append("recent_work")
        feedback.append("✓ References specific work/content")

    if re.search(PERSONALIZATION_TYPES["specific_detail"], message_lower):
        score += 20
        elements_found.append("specific_detail")
        feedback.append("✓ Includes specific details")

    if re.search(PERSONALIZATION_TYPES["mutual"], message_lower):
        score += 15
        elements_found.append("mutual_connection")

    if not elements_found:
        feedback.append(
            "Add personalization - reference something specific about them or their company"
        )

    return min(100, score), elements_found, feedback


def _score_metrics(message_text: str) -> Tuple[int, List[str]]:
    """
    Score inclusion of quantified achievements.

    Research shows quantified achievements get 40% more interviews.
    """
    feedback = []
    score = 0

    # Look for numbers and metrics
    metric_patterns = [
        r"\$[\d,]+[KMB]?",  # Dollar amounts
        r"\d+%",  # Percentages
        r"\d+x",  # Multipliers
        r"\d{1,3}(?:,\d{3})+",  # Large numbers
        r"\b\d+\s*(?:years?|months?|clients?|projects?|users?|customers?)\b",
    ]

    metrics_found = 0
    for pattern in metric_patterns:
        matches = re.findall(pattern, message_text, re.IGNORECASE)
        metrics_found += len(matches)

    if metrics_found >= 3:
        score = 100
        feedback.append("✓ Strong quantified achievements included")
    elif metrics_found >= 2:
        score = 80
        feedback.append("✓ Good use of metrics")
    elif metrics_found == 1:
        score = 50
        feedback.append('Add more quantified achievements (e.g., "increased sales by 25%")')
    else:
        score = 20
        feedback.append(
            "Include specific numbers and metrics to stand out (40% more interview callbacks)"
        )

    return score, feedback


def _score_cta(message_text: str) -> Tuple[int, bool, List[str]]:
    """
    Score call-to-action clarity.

    Best practice: Single, clear CTA reduces confusion.
    """
    feedback = []
    message_lower = message_text.lower()

    cta_count = 0
    for pattern in CTA_PATTERNS:
        if re.search(pattern, message_lower):
            cta_count += 1

    if cta_count == 1:
        score = 100
        has_cta = True
        feedback.append("✓ Clear, single call-to-action")
    elif cta_count == 0:
        score = 20
        has_cta = False
        feedback.append('Add a clear call-to-action (e.g., "Would you be open to a brief call?")')
    elif cta_count > 1:
        score = 60
        has_cta = True
        feedback.append("Use single CTA for better conversion - too many asks can confuse")

    return score, has_cta, feedback


def _score_tone(message_text: str, message_type: str) -> Tuple[int, List[str]]:
    """
    Score professional tone and appropriateness.
    """
    feedback = []
    score = 70  # Base score

    message_lower = message_text.lower()

    # Check for professional phrases
    professional_count = sum(1 for phrase in PROFESSIONAL_PHRASES if phrase in message_lower)
    if professional_count >= 2:
        score += 15
    elif professional_count >= 1:
        score += 10

    # Check for issues
    issues = []

    # Too casual
    casual_indicators = ["hey!", "yo", "sup", "lol", "!!!", "???", "gonna", "wanna"]
    if any(indicator in message_lower for indicator in casual_indicators):
        score -= 20
        issues.append("Consider more professional tone")

    # Too formal/stiff
    overly_formal = ["pursuant to", "herewith", "aforementioned", "henceforth"]
    if any(phrase in message_lower for phrase in overly_formal):
        score -= 10
        issues.append("Tone may be overly formal - aim for professional but approachable")

    # Desperate/needy language
    desperate = [
        "i really need",
        "please help",
        "desperate",
        "any job",
        "anything available",
    ]
    if any(phrase in message_lower for phrase in desperate):
        score -= 30
        issues.append("Avoid desperate language - focus on value you can provide")

    if not issues:
        feedback.append("✓ Appropriate professional tone")
    else:
        feedback.extend(issues)

    return max(0, min(100, score)), feedback


def validate_message_length(message_text: str, message_type: str = "initial_outreach") -> Dict:
    """
    Quick validation of message length without full scoring.

    Returns simple pass/fail with word count.
    """
    word_count = len(message_text.split())
    min_words, max_words = OPTIMAL_LENGTHS.get(message_type, (100, 150))

    return {
        "word_count": word_count,
        "min_recommended": min_words,
        "max_recommended": max_words,
        "is_optimal": min_words <= word_count <= max_words,
        "is_under_150": word_count <= 150,
    }
