"""
ATS (Applicant Tracking System) Scoring Algorithm

Calculates resume ATS compatibility score based on 7 categories.

Formula:
ats_score = compatibility(15) + keywords(15) + achievements(25) +
            formatting(15) + progression(15) + completeness(10) + fit(5)
"""

import re
from typing import Dict, List, Optional, Tuple

# ATS Score Weights (must sum to 100)
ATS_WEIGHTS = {
    "compatibility": 15,
    "keywords": 15,
    "achievements": 25,
    "formatting": 15,
    "progression": 15,
    "completeness": 10,
    "fit": 5,
}

# Required resume sections
REQUIRED_SECTIONS = [
    "contact",
    "summary",
    "experience",
    "education",
    "skills",
]

# Action verbs that indicate achievements
ACTION_VERBS = [
    "achieved",
    "accomplished",
    "accelerated",
    "advanced",
    "amplified",
    "built",
    "boosted",
    "consolidated",
    "created",
    "cultivated",
    "delivered",
    "developed",
    "drove",
    "earned",
    "enabled",
    "engineered",
    "established",
    "exceeded",
    "expanded",
    "founded",
    "generated",
    "grew",
    "headed",
    "implemented",
    "improved",
    "increased",
    "initiated",
    "innovated",
    "launched",
    "led",
    "managed",
    "maximized",
    "modernized",
    "negotiated",
    "optimized",
    "orchestrated",
    "outperformed",
    "overhauled",
    "pioneered",
    "produced",
    "reduced",
    "redesigned",
    "reorganized",
    "resolved",
    "revamped",
    "saved",
    "scaled",
    "secured",
    "simplified",
    "spearheaded",
    "streamlined",
    "strengthened",
    "surpassed",
    "transformed",
    "tripled",
    "unified",
    "upgraded",
]

# Quantification patterns (looking for numbers, percentages, dollar amounts)
METRIC_PATTERNS = [
    r"\$[\d,]+[KMB]?",  # Dollar amounts
    r"\d+%",  # Percentages
    r"\d+x",  # Multipliers
    r"\d{1,3}(?:,\d{3})+",  # Large numbers with commas
    r"\b\d+\+?\s*(?:years?|months?|weeks?|days?)\b",  # Time periods
    r"\b\d+\+?\s*(?:people|employees|team members?|clients?|customers?)\b",  # Team/client sizes
]


def calculate_ats_score(
    resume_text: str,
    parsed_sections: Optional[Dict] = None,
    job_keywords: Optional[List[str]] = None,
    target_role: Optional[str] = None,
    file_type: Optional[str] = None,
) -> Dict:
    """
    Calculate comprehensive ATS score for a resume.

    Args:
        resume_text: Full text content of resume
        parsed_sections: Structured sections if available
        job_keywords: Target keywords from job description
        target_role: Target job role for fit scoring
        file_type: File format ('pdf', 'docx', 'txt')

    Returns:
        Dictionary with total score, component scores, and recommendations
    """
    if not resume_text:
        return {
            "total_score": 0,
            "components": {k: 0 for k in ATS_WEIGHTS.keys()},
            "recommendations": ["Resume text is empty"],
            "missing_keywords": [],
            "weak_sections": ["all"],
        }

    # Calculate each component
    compatibility, compat_feedback = _score_compatibility(resume_text, file_type)
    keywords, keyword_feedback, missing = _score_keywords(resume_text, job_keywords)
    achievements, achieve_feedback = _score_achievements(resume_text)
    formatting, format_feedback = _score_formatting(resume_text, parsed_sections)
    progression, progress_feedback = _score_progression(resume_text, parsed_sections)
    completeness, complete_feedback, weak_sections = _score_completeness(
        resume_text, parsed_sections
    )
    fit, fit_feedback = _score_fit(resume_text, target_role)

    # Calculate weighted total
    total_score = int(
        compatibility * (ATS_WEIGHTS["compatibility"] / 100)
        + keywords * (ATS_WEIGHTS["keywords"] / 100)
        + achievements * (ATS_WEIGHTS["achievements"] / 100)
        + formatting * (ATS_WEIGHTS["formatting"] / 100)
        + progression * (ATS_WEIGHTS["progression"] / 100)
        + completeness * (ATS_WEIGHTS["completeness"] / 100)
        + fit * (ATS_WEIGHTS["fit"] / 100)
    )

    # Compile recommendations
    recommendations = []
    recommendations.extend(compat_feedback)
    recommendations.extend(keyword_feedback)
    recommendations.extend(achieve_feedback)
    recommendations.extend(format_feedback)
    recommendations.extend(progress_feedback)
    recommendations.extend(complete_feedback)
    recommendations.extend(fit_feedback)

    # Sort by importance (limit to top 5)
    recommendations = recommendations[:5]

    return {
        "total_score": total_score,
        "components": {
            "compatibility": compatibility,
            "keywords": keywords,
            "achievements": achievements,
            "formatting": formatting,
            "progression": progression,
            "completeness": completeness,
            "fit": fit,
        },
        "recommendations": recommendations,
        "missing_keywords": missing,
        "weak_sections": weak_sections,
    }


def _score_compatibility(resume_text: str, file_type: Optional[str]) -> Tuple[int, List[str]]:
    """
    Score file format and parsing compatibility.

    Criteria:
    - File format compatibility
    - Text extractability
    - No complex formatting issues
    """
    score = 100
    feedback = []

    # File type scoring
    if file_type:
        if file_type.lower() == "docx":
            score = 100  # Best compatibility
        elif file_type.lower() == "pdf":
            score = 90  # Good but can have parsing issues
        elif file_type.lower() == "txt":
            score = 85  # Plain text loses formatting
        else:
            score = 60
            feedback.append("Consider using .docx format for best ATS compatibility")

    # Check for potential parsing issues in text
    if resume_text:
        # Check for excessive special characters
        special_char_ratio = len(re.findall(r"[^\w\s.,;:\-()@/]", resume_text)) / len(resume_text)
        if special_char_ratio > 0.05:
            score -= 15
            feedback.append("Reduce special characters and symbols for better ATS parsing")

        # Check for very short content
        word_count = len(resume_text.split())
        if word_count < 200:
            score -= 20
            feedback.append("Resume content seems sparse - add more detail")

    return max(0, min(100, score)), feedback


def _score_keywords(
    resume_text: str, job_keywords: Optional[List[str]]
) -> Tuple[int, List[str], List[str]]:
    """
    Score keyword density and relevance.

    Criteria:
    - Presence of target keywords
    - Natural keyword integration
    - Industry-relevant terms
    """
    feedback = []
    missing = []

    if not job_keywords:
        # No target keywords provided - give baseline score
        return 70, ["Add job-specific keywords from target job descriptions"], []

    resume_lower = resume_text.lower()
    found_count = 0
    total_keywords = len(job_keywords)

    for keyword in job_keywords:
        if keyword.lower() in resume_lower:
            found_count += 1
        else:
            missing.append(keyword)

    # Calculate match percentage
    if total_keywords > 0:
        match_rate = found_count / total_keywords
        score = int(match_rate * 100)
    else:
        score = 70

    if missing:
        if len(missing) > 3:
            feedback.append(f'Add these high-priority keywords: {", ".join(missing[:3])}')
        else:
            feedback.append(f'Consider adding: {", ".join(missing)}')

    return max(0, min(100, score)), feedback, missing


def _score_achievements(resume_text: str) -> Tuple[int, List[str]]:
    """
    Score quantified achievements and impact statements.

    Research shows resumes with quantified achievements get 40% more interviews.

    Criteria:
    - Action verb usage
    - Quantified metrics (numbers, percentages, dollar amounts)
    - Impact statements
    """
    feedback = []
    score = 50  # Base score

    resume_lower = resume_text.lower()

    # Count action verbs
    action_verb_count = sum(1 for verb in ACTION_VERBS if verb in resume_lower)
    if action_verb_count >= 10:
        score += 20
    elif action_verb_count >= 5:
        score += 10
    else:
        feedback.append("Start bullet points with strong action verbs (led, achieved, increased)")

    # Count quantified metrics
    metric_count = 0
    for pattern in METRIC_PATTERNS:
        metric_count += len(re.findall(pattern, resume_text))

    if metric_count >= 8:
        score += 30
    elif metric_count >= 4:
        score += 15
    else:
        feedback.append("Quantify achievements with numbers, percentages, or dollar amounts")

    # Check for STAR-formatted bullet points (situational context + result)
    bullets = re.findall(r"[•\-\*]\s*([^\n]+)", resume_text)
    result_keywords = [
        "resulting",
        "achieved",
        "led to",
        "which",
        "saving",
        "generating",
        "improving",
    ]

    result_bullets = sum(1 for b in bullets if any(kw in b.lower() for kw in result_keywords))
    if len(bullets) > 0:
        result_rate = result_bullets / len(bullets)
        if result_rate >= 0.5:
            score += 10
        elif result_rate < 0.25:
            feedback.append(
                'Add results and outcomes to your bullet points (e.g., "...resulting in 25% increase")'
            )

    return max(0, min(100, score)), feedback


def _score_formatting(resume_text: str, parsed_sections: Optional[Dict]) -> Tuple[int, List[str]]:
    """
    Score resume structure and formatting.

    Criteria:
    - Clear section headers
    - Consistent formatting
    - Appropriate length
    - White space and readability
    """
    feedback = []
    score = 70  # Base score

    # Check word count (optimal: 475-600 words per research)
    word_count = len(resume_text.split())
    if 400 <= word_count <= 800:
        score += 15
    elif word_count < 300:
        score -= 20
        feedback.append("Resume is too short - aim for 475-600 words")
    elif word_count > 1000:
        score -= 10
        feedback.append("Consider condensing - resumes over 800 words may lose reader attention")

    # Check for section headers
    common_headers = [
        "experience",
        "education",
        "skills",
        "summary",
        "objective",
        "work history",
    ]
    headers_found = sum(1 for h in common_headers if h in resume_text.lower())

    if headers_found >= 4:
        score += 15
    elif headers_found < 2:
        score -= 20
        feedback.append("Use clear section headers (Experience, Education, Skills)")

    # Check for bullet points
    bullet_count = len(re.findall(r"[•\-\*]\s", resume_text))
    if bullet_count >= 10:
        score += 10
    elif bullet_count < 3:
        feedback.append("Use bullet points to highlight achievements and responsibilities")

    return max(0, min(100, score)), feedback


def _score_progression(resume_text: str, parsed_sections: Optional[Dict]) -> Tuple[int, List[str]]:
    """
    Score career progression and growth pattern.

    Criteria:
    - Clear timeline
    - Role advancement
    - Increasing responsibility
    """
    feedback = []
    score = 70  # Base score

    # Look for date patterns
    date_patterns = re.findall(
        r"(19|20)\d{2}\s*[-–]\s*(19|20)\d{2}|(19|20)\d{2}\s*[-–]\s*[Pp]resent",
        resume_text,
    )

    if len(date_patterns) >= 3:
        score += 15  # Multiple positions shown
    elif len(date_patterns) < 1:
        score -= 20
        feedback.append("Include employment dates to show career timeline")

    # Look for progression indicators
    progression_terms = [
        "promoted",
        "advanced",
        "senior",
        "lead",
        "manager",
        "director",
        "head of",
        "principal",
        "chief",
        "vp",
        "vice president",
    ]
    resume_lower = resume_text.lower()
    progression_count = sum(1 for term in progression_terms if term in resume_lower)

    if progression_count >= 2:
        score += 15
    elif progression_count == 0:
        feedback.append("Highlight career progression and increasing responsibilities")

    return max(0, min(100, score)), feedback


def _score_completeness(
    resume_text: str, parsed_sections: Optional[Dict]
) -> Tuple[int, List[str], List[str]]:
    """
    Score presence of all essential sections.

    Required sections:
    - Contact info
    - Summary/Objective
    - Work Experience
    - Education
    - Skills
    """
    feedback = []
    weak_sections = []

    # Check for each required section
    section_checks = {
        "contact": bool(re.search(r"[\w\.-]+@[\w\.-]+|[\d\-\(\)]{10,}", resume_text)),
        "summary": any(
            s in resume_text.lower() for s in ["summary", "objective", "profile", "about"]
        ),
        "experience": any(
            s in resume_text.lower() for s in ["experience", "employment", "work history"]
        ),
        "education": "education" in resume_text.lower() or "degree" in resume_text.lower(),
        "skills": "skill" in resume_text.lower() or "expertise" in resume_text.lower(),
    }

    present_count = sum(section_checks.values())
    total_required = len(REQUIRED_SECTIONS)

    score = int((present_count / total_required) * 100)

    for section, present in section_checks.items():
        if not present:
            weak_sections.append(section)
            feedback.append(f"Add a {section.title()} section to your resume")

    return max(0, min(100, score)), feedback, weak_sections


def _score_fit(resume_text: str, target_role: Optional[str]) -> Tuple[int, List[str]]:
    """
    Score resume fit for target role.

    Without a target role, provides baseline score.
    """
    feedback = []

    if not target_role:
        return 70, ["Tailor your resume for specific job postings to improve fit score"]

    # Check if target role or similar terms appear in resume
    resume_lower = resume_text.lower()
    role_lower = target_role.lower()

    # Extract key terms from target role
    role_terms = [t for t in role_lower.split() if len(t) > 3]

    if role_lower in resume_lower:
        score = 100
    elif any(term in resume_lower for term in role_terms):
        score = 80
    else:
        score = 50
        feedback.append(f'Consider incorporating "{target_role}" terminology into your resume')

    return max(0, min(100, score)), feedback
