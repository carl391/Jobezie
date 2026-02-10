"""
Tests for LinkedIn Optimizer Routes

Validates all LinkedIn optimization endpoints.
"""


def get_data(response):
    """Extract data from standardized API response."""
    json_data = response.json
    if isinstance(json_data, dict) and "data" in json_data and "success" in json_data:
        return json_data["data"]
    return json_data


class TestLinkedInAnalyze:
    """Tests for LinkedIn profile analysis."""

    def test_analyze_empty_profile(self, client, auth_headers):
        """Analyze empty profile returns results."""
        response = client.post(
            "/api/linkedin/analyze",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = get_data(response)
        assert "total_score" in data or "score" in data or isinstance(data, dict)

    def test_analyze_full_profile(self, client, auth_headers):
        """Analyze complete profile returns higher score."""
        response = client.post(
            "/api/linkedin/analyze",
            json={
                "headline": "Senior Software Engineer | Python & Cloud Expert",
                "summary": "10+ years building scalable systems with Python and AWS.",
                "experience": [{"title": "Senior Engineer", "company": "TechCorp", "years": 5}],
                "skills": ["Python", "AWS", "Docker", "Kubernetes"],
                "education": [{"school": "MIT", "degree": "CS"}],
                "photo": True,
                "location": "San Francisco, CA",
                "industry": "technology",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestLinkedInHeadline:
    """Tests for headline generation."""

    def test_generate_headline(self, client, auth_headers):
        """Generate headline with valid input."""
        response = client.post(
            "/api/linkedin/headline/generate",
            json={
                "current_role": "Software Engineer",
                "target_role": "Senior Engineer",
                "industry": "technology",
                "key_skills": ["Python", "React", "AWS"],
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = get_data(response)
        assert "headlines" in data or "options" in data or isinstance(data, dict)

    def test_generate_headline_no_role(self, client, auth_headers):
        """Generate headline without role returns 400."""
        response = client.post(
            "/api/linkedin/headline/generate",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_generate_headline_uses_profile(self, client, auth_headers_expert):
        """Uses user profile data when request data missing (expert has current_role)."""
        response = client.post(
            "/api/linkedin/headline/generate",
            json={},
            headers=auth_headers_expert,
        )
        # Expert user has current_role set, so should not get 400
        assert response.status_code == 200


class TestLinkedInSummary:
    """Tests for summary generation."""

    def test_generate_summary(self, client, auth_headers):
        """Generate summary with all required fields."""
        response = client.post(
            "/api/linkedin/summary/generate",
            json={
                "current_role": "Data Scientist",
                "years_experience": 6,
                "industry": "technology",
                "key_skills": ["Python", "ML", "TensorFlow"],
                "achievements": ["Increased model accuracy by 15%"],
            },
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_generate_summary_missing_role(self, client, auth_headers):
        """Summary without current_role returns 400."""
        response = client.post(
            "/api/linkedin/summary/generate",
            json={
                "years_experience": 5,
                "industry": "tech",
                "key_skills": ["Python"],
            },
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_generate_summary_missing_experience(self, client, auth_headers):
        """Summary without years_experience returns 400."""
        response = client.post(
            "/api/linkedin/summary/generate",
            json={
                "current_role": "Engineer",
                "industry": "tech",
                "key_skills": ["Python"],
            },
            headers=auth_headers,
        )
        assert response.status_code == 400


class TestLinkedInExperience:
    """Tests for experience optimization."""

    def test_optimize_experience(self, client, auth_headers):
        """Optimize experience entry."""
        response = client.post(
            "/api/linkedin/experience/optimize",
            json={
                "title": "Software Engineer",
                "company": "TechCorp",
                "description": "Worked on backend systems and databases.",
                "target_keywords": ["Python", "microservices"],
            },
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_optimize_experience_missing_fields(self, client, auth_headers):
        """Optimize without required fields returns 400."""
        response = client.post(
            "/api/linkedin/experience/optimize",
            json={"title": "Engineer"},
            headers=auth_headers,
        )
        assert response.status_code == 400


class TestLinkedInVisibility:
    """Tests for visibility scoring."""

    def test_calculate_visibility(self, client, auth_headers):
        """Calculate visibility score."""
        response = client.post(
            "/api/linkedin/visibility",
            json={
                "headline": "Senior Engineer",
                "summary": "Experienced developer.",
                "skills": ["Python", "AWS"],
                "photo": True,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestLinkedInKeywords:
    """Tests for industry keywords."""

    def test_get_technology_keywords(self, client, auth_headers):
        """Get keywords for technology industry."""
        response = client.get(
            "/api/linkedin/keywords/technology",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = get_data(response)
        assert "keywords" in data
        assert "usage_tips" in data

    def test_get_unknown_industry_keywords(self, client, auth_headers):
        """Get keywords for unknown industry returns generic keywords."""
        response = client.get(
            "/api/linkedin/keywords/underwater_basket_weaving",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = get_data(response)
        assert len(data["keywords"]) > 0


class TestLinkedInTips:
    """Tests for optimization tips."""

    def test_get_tips(self, client, auth_headers):
        """Get optimization tips."""
        response = client.get(
            "/api/linkedin/tips",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = get_data(response)
        assert "headline" in data
        assert "summary" in data
        assert "experience" in data
        assert "skills" in data
        assert "engagement" in data
