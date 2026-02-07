"""
Tests for Labor Market Routes

Validates all labor market endpoints including shortage scores,
salary benchmarks, opportunity analysis, and O*NET integration.
"""

from app.extensions import db
from app.models.user import User


def get_data(response):
    """Extract data from standardized API response."""
    json_data = response.json
    if isinstance(json_data, dict) and "data" in json_data and "success" in json_data:
        return json_data["data"]
    return json_data


class TestMarketOverview:
    """Tests for market overview endpoint."""

    def test_get_overview(self, client, auth_headers):
        """Get market overview returns data."""
        response = client.get("/api/labor-market/overview", headers=auth_headers)
        assert response.status_code == 200
        data = get_data(response)
        assert isinstance(data, dict)


class TestShortageScore:
    """Tests for shortage score endpoint."""

    def test_get_shortage_with_role(self, client, auth_headers):
        """Get shortage score with role parameter."""
        response = client.get(
            "/api/labor-market/shortage?role=Software%20Engineer",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = get_data(response)
        assert "total_score" in data

    def test_shortage_missing_role(self, client, auth_headers):
        """Shortage without role returns 400."""
        response = client.get("/api/labor-market/shortage", headers=auth_headers)
        assert response.status_code == 400

    def test_shortage_with_industry(self, client, auth_headers):
        """Shortage with industry parameter."""
        response = client.get(
            "/api/labor-market/shortage?role=Data%20Scientist&industry=technology",
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_shortage_with_location(self, client, auth_headers):
        """Shortage with location parameter."""
        response = client.get(
            "/api/labor-market/shortage?role=DevOps%20Engineer&location=San%20Francisco",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestSalaryBenchmark:
    """Tests for salary benchmark endpoint."""

    def test_get_salary(self, client, auth_headers):
        """Get salary benchmark for a role."""
        response = client.get(
            "/api/labor-market/salary?role=Software%20Engineer",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = get_data(response)
        assert isinstance(data, dict)

    def test_salary_missing_role(self, client, auth_headers):
        """Salary without role returns 400."""
        response = client.get("/api/labor-market/salary", headers=auth_headers)
        assert response.status_code == 400

    def test_salary_with_experience(self, client, auth_headers):
        """Salary with experience level."""
        response = client.get(
            "/api/labor-market/salary?role=Software%20Engineer&experience=senior",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestOpportunityScore:
    """Tests for opportunity score endpoint."""

    def test_calculate_opportunity(self, client, auth_headers):
        """Calculate opportunity score with explicit request data."""
        response = client.post(
            "/api/labor-market/opportunity",
            json={
                "target_role": "Software Engineer",
                "skills": ["Python", "Django", "Communication"],
                "target_industry": "technology",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_opportunity_different_role(self, client, auth_headers):
        """Calculate opportunity for Data Scientist role."""
        response = client.post(
            "/api/labor-market/opportunity",
            json={
                "target_role": "Data Scientist",
                "skills": ["Python", "Machine Learning", "SQL"],
                "target_industry": "technology",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_opportunity_missing_role(self, client, auth_headers):
        """Opportunity without target_role and no profile roles returns 400."""
        response = client.post(
            "/api/labor-market/opportunity",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 400


class TestJobOutlook:
    """Tests for job outlook endpoint."""

    def test_get_outlook(self, client, auth_headers):
        """Get job outlook for a role."""
        response = client.get(
            "/api/labor-market/outlook/Software%20Engineer",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestTrendingIndustries:
    """Tests for trending industries endpoint."""

    def test_get_trending(self, client, auth_headers):
        """Get trending industries list."""
        response = client.get(
            "/api/labor-market/industries/trending",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = get_data(response)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "name" in data[0]
        assert "growth_rate" in data[0]
        assert "growth_outlook" in data[0]

    def test_trending_sorted_by_growth(self, client, auth_headers):
        """Trending industries are sorted by growth rate descending."""
        response = client.get(
            "/api/labor-market/industries/trending",
            headers=auth_headers,
        )
        data = get_data(response)
        rates = [d["growth_rate"] for d in data]
        assert rates == sorted(rates, reverse=True)


class TestHighDemandRoles:
    """Tests for high demand roles endpoint."""

    def test_get_high_demand(self, client, auth_headers):
        """Get high demand roles list."""
        response = client.get(
            "/api/labor-market/roles/high-demand",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = get_data(response)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "role" in data[0]
        assert "shortage_score" in data[0]
        assert "demand_level" in data[0]

    def test_high_demand_sorted_by_shortage(self, client, auth_headers):
        """High demand roles are sorted by shortage score descending."""
        response = client.get(
            "/api/labor-market/roles/high-demand",
            headers=auth_headers,
        )
        data = get_data(response)
        scores = [d["shortage_score"] for d in data]
        assert scores == sorted(scores, reverse=True)


class TestSkillsMap:
    """Tests for skills map endpoint."""

    def test_get_skills_map(self, client, auth_headers):
        """Get skills map for user."""
        response = client.get(
            "/api/labor-market/skills-map",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = get_data(response)
        assert "skills" in data
        assert "abilities" in data
        assert "knowledge" in data
        assert "total_matched" in data
        assert "coverage_by_category" in data


class TestSkillsGap:
    """Tests for skills gap analysis endpoint."""

    def test_skills_gap_with_role(self, client, auth_headers, test_user, app):
        """Get skills gap analysis for target role."""
        with app.app_context():
            user = User.query.get(test_user.id)
            user.target_roles = ["Software Engineer"]
            user.technical_skills = ["Python", "JavaScript"]
            db.session.commit()

        response = client.post(
            "/api/labor-market/skills-gap",
            json={"target_role": "Software Engineer"},
            headers=auth_headers,
        )
        # May 404 if occupation not in DB, or 200 with gap data
        assert response.status_code in [200, 404]

    def test_skills_gap_missing_role(self, client, auth_headers):
        """Skills gap without role and no profile roles returns 400."""
        response = client.post(
            "/api/labor-market/skills-gap",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 400
