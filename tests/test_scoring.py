"""
Tests for Scoring Algorithms

Tests the ATS, Engagement, Message Quality, and Career Readiness scoring.
"""

from datetime import datetime, timedelta

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


class TestATSScoring:
    """Tests for ATS resume scoring."""

    def test_empty_resume(self):
        """Test scoring with empty resume."""
        result = calculate_ats_score("")
        assert result["total_score"] == 0
        assert "all" in result["weak_sections"]

    def test_basic_resume(self):
        """Test scoring with basic resume text."""
        resume = """
        John Doe
        john@email.com | 555-1234

        Summary
        Experienced software engineer with 5 years of experience.

        Experience
        Software Engineer at Tech Corp
        2019 - Present
        - Developed web applications using Python and JavaScript
        - Led team of 3 developers

        Education
        BS Computer Science, State University, 2018

        Skills
        Python, JavaScript, SQL, Docker
        """
        result = calculate_ats_score(resume)
        assert result["total_score"] > 0
        assert result["components"]["completeness"] > 0

    def test_achievements_scoring(self):
        """Test that quantified achievements boost score."""
        resume_without_metrics = """
        Experience
        Software Engineer
        - Worked on various projects
        - Collaborated with team members
        - Participated in meetings
        """

        resume_with_metrics = """
        Experience
        Software Engineer
        - Increased sales by 25% through optimization
        - Managed team of 10 engineers delivering $2M revenue
        - Reduced operational costs by $50K annually
        - Improved application performance by 3x
        - Led 5 major projects resulting in 40% efficiency gains
        - Achieved 100% customer satisfaction rating
        """

        result_without = calculate_ats_score(resume_without_metrics)
        result_with = calculate_ats_score(resume_with_metrics)

        # Resume with metrics should score higher on achievements
        assert (
            result_with["components"]["achievements"]
            >= result_without["components"]["achievements"]
        )

    def test_keywords_matching(self):
        """Test keyword matching against job description."""
        resume = """
        Software Engineer with expertise in Python, Django, and AWS.
        Built microservices architecture and REST APIs.
        """
        keywords = ["python", "django", "aws", "microservices", "kubernetes"]

        result = calculate_ats_score(resume, job_keywords=keywords)

        assert "kubernetes" in result["missing_keywords"]
        assert result["components"]["keywords"] > 0


class TestEngagementScoring:
    """Tests for recruiter engagement scoring."""

    def test_no_messages(self):
        """Test score with no messages sent."""
        result = calculate_engagement_score(
            messages_sent=0,
            messages_opened=0,
            responses_received=0,
        )
        # Should give neutral/baseline scores
        assert result["total_score"] >= 0

    def test_good_response_rate(self):
        """Test score with good response rate."""
        result = calculate_engagement_score(
            messages_sent=10,
            messages_opened=6,
            responses_received=4,  # 40% response rate
        )
        assert result["components"]["response_rate"] == 100

    def test_poor_response_rate(self):
        """Test score with poor response rate."""
        result = calculate_engagement_score(
            messages_sent=100,
            messages_opened=20,
            responses_received=0,
        )
        assert result["components"]["response_rate"] < 50

    def test_recency_fresh(self):
        """Test recency score for fresh contact."""
        result = calculate_engagement_score(
            messages_sent=5,
            messages_opened=3,
            responses_received=1,
            last_contact_date=datetime.utcnow() - timedelta(days=3),
        )
        assert result["components"]["recency"] == 100

    def test_recency_cold(self):
        """Test recency score for old contact."""
        result = calculate_engagement_score(
            messages_sent=5,
            messages_opened=3,
            responses_received=1,
            last_contact_date=datetime.utcnow() - timedelta(days=90),
        )
        assert result["components"]["recency"] < 25


class TestFitScoring:
    """Tests for recruiter fit scoring."""

    def test_perfect_fit(self):
        """Test score with perfect industry/location match."""
        result = calculate_fit_score(
            user_industries=["technology", "software"],
            user_location="San Francisco, CA",
            user_target_roles=["Software Engineer"],
            user_salary_expectation=150000,
            recruiter_industries=["technology", "software"],
            recruiter_locations=["San Francisco, CA", "Remote"],
            recruiter_specialty="Software Engineering",
            recruiter_company_type="executive search",
            recruiter_salary_range=(120000, 200000),
        )
        assert result["total_score"] >= 80

    def test_no_overlap(self):
        """Test score with no industry overlap."""
        result = calculate_fit_score(
            user_industries=["technology"],
            user_location="New York",
            user_target_roles=["Software Engineer"],
            user_salary_expectation=100000,
            recruiter_industries=["healthcare", "finance"],
            recruiter_locations=["Chicago"],
            recruiter_specialty="Nursing",
            recruiter_company_type="staffing",
        )
        assert result["components"]["industry"] <= 30


class TestPriorityScoring:
    """Tests for priority/follow-up scoring."""

    def test_optimal_follow_up_window(self):
        """Test high priority in optimal follow-up window (5-7 days)."""
        score = calculate_priority_score(
            days_since_contact=6,
            pending_actions=1,
            engagement_score=70,
            fit_score=80,
            has_responded=False,
            status="contacted",
        )
        assert score >= 70

    def test_responded_high_priority(self):
        """Test high priority when recruiter has responded."""
        score = calculate_priority_score(
            days_since_contact=3,
            pending_actions=1,
            engagement_score=80,
            fit_score=80,
            has_responded=True,
            status="responded",
        )
        # Responded status with high engagement should be high priority
        assert score >= 70

    def test_stale_low_priority(self):
        """Test lower priority for stale contacts."""
        score = calculate_priority_score(
            days_since_contact=60,
            pending_actions=0,
            engagement_score=30,
            fit_score=50,
            has_responded=False,
            status="contacted",
        )
        assert score < 50


class TestMessageQualityScoring:
    """Tests for message quality scoring."""

    def test_empty_message(self):
        """Test scoring with empty message."""
        result = calculate_message_quality("")
        assert result["total_score"] == 0
        assert "Message is empty" in result["feedback"]

    def test_optimal_length(self):
        """Test scoring with optimal message length."""
        # Generate a message around 120 words
        message = "Hi Sarah, " + ("word " * 110) + "Would you be open to a call?"
        result = calculate_message_quality(message)
        assert result["components"]["words"] >= 70

    def test_too_long_message(self):
        """Test scoring with overly long message."""
        message = "word " * 300  # Way over 150 words
        result = calculate_message_quality(message)
        assert result["components"]["words"] < 50
        assert any("150 words" in s for s in result["suggestions"])

    def test_personalization_detection(self):
        """Test detection of personalization elements."""
        message = """
        Hi Sarah,

        I noticed your recent work at TechCorp on the AI project.
        I'd love to discuss how my experience could contribute to your team.
        """
        result = calculate_message_quality(
            message,
            recruiter_name="Sarah",
            company_name="TechCorp",
        )
        assert result["has_personalization"]
        assert "recruiter_name" in result["personalization_elements"]

    def test_metrics_detection(self):
        """Test detection of quantified achievements."""
        message = """
        Hi,
        I increased revenue by 25% and managed a team of 10 engineers,
        delivering $2M in cost savings.
        """
        result = calculate_message_quality(message)
        assert result["has_metrics"]
        assert result["components"]["metrics"] >= 80

    def test_cta_detection(self):
        """Test detection of call-to-action."""
        # Use a clearer CTA pattern that matches the regex
        message = (
            "Hi, I'd love to discuss opportunities. Would you be open to a brief call next week?"
        )
        result = calculate_message_quality(message)
        assert result["has_cta"]
        assert result["components"]["cta"] >= 60  # May have multiple CTAs

    def test_no_cta(self):
        """Test low score when no CTA present."""
        message = "Hi, here is my background. Thanks for reading."
        result = calculate_message_quality(message)
        assert not result["has_cta"]
        assert result["components"]["cta"] < 50


class TestMessageValidation:
    """Tests for quick message validation."""

    def test_validate_optimal(self):
        """Test validation of optimal length message."""
        message = "word " * 120
        result = validate_message_length(message, "initial_outreach")
        assert result["is_optimal"]
        assert result["is_under_150"]

    def test_validate_too_short(self):
        """Test validation of too short message."""
        message = "Hi there."
        result = validate_message_length(message, "initial_outreach")
        assert not result["is_optimal"]
        assert result["word_count"] < result["min_recommended"]


class TestCareerReadinessScoring:
    """Tests for career readiness scoring."""

    def test_complete_profile(self):
        """Test readiness with complete profile data."""
        result = calculate_career_readiness(
            profile_completeness=0.9,  # 90%
            resume_ats_score=75,
            has_resume=True,
            active_recruiters=15,
            messages_this_week=6,
            response_rate=0.30,
        )
        assert result["total_score"] >= 60
        assert "components" in result
        assert "recommendations" in result

    def test_new_user(self):
        """Test readiness for new user with minimal data."""
        result = calculate_career_readiness(
            profile_completeness=0.3,
            resume_ats_score=None,
            has_resume=False,
            active_recruiters=0,
            messages_this_week=0,
            response_rate=0,
        )
        assert result["total_score"] < 40
        assert len(result["recommendations"]) > 0
        assert len(result["next_actions"]) > 0

    def test_readiness_levels(self):
        """Test that different scores produce different totals."""
        # High readiness
        result_high = calculate_career_readiness(
            profile_completeness=1.0,
            resume_ats_score=90,
            has_resume=True,
            active_recruiters=15,
            messages_this_week=7,
            response_rate=0.35,
        )

        # Low readiness
        result_low = calculate_career_readiness(
            profile_completeness=0.2,
            resume_ats_score=None,
            has_resume=False,
            active_recruiters=0,
            messages_this_week=0,
            response_rate=0,
        )

        assert result_high["total_score"] > result_low["total_score"]
        assert result_high["total_score"] >= 70
        assert result_low["total_score"] < 30
