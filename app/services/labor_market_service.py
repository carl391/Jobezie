"""
Labor Market Intelligence Service

Provides labor market data using BLS (Bureau of Labor Statistics) and O*NET data.
Calculates shortage scores, salary benchmarks, and job growth projections.
"""

import math
import os
from datetime import datetime
from typing import Dict, List, Optional

import httpx


class LaborMarketService:
    """
    Service for labor market intelligence.

    Uses BLS API for employment statistics and O*NET for occupation data.
    """

    BLS_BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    ONET_BASE_URL = "https://services.onetcenter.org/ws/"

    # BLS Series IDs for national employment
    BLS_SERIES = {
        "unemployment_rate": "LNS14000000",
        "total_nonfarm": "CES0000000001",
        "tech_employment": "CES5000000001",
        "professional_services": "CES6054000001",
        "finance": "CES5552000001",
        "healthcare": "CES6562000001",
    }

    # Career shortage indicators (high demand roles)
    HIGH_DEMAND_ROLES = {
        "software_engineer": {"growth_rate": 25, "shortage_score": 85},
        "data_scientist": {"growth_rate": 35, "shortage_score": 90},
        "cybersecurity": {"growth_rate": 33, "shortage_score": 88},
        "cloud_architect": {"growth_rate": 28, "shortage_score": 82},
        "devops_engineer": {"growth_rate": 22, "shortage_score": 80},
        "product_manager": {"growth_rate": 12, "shortage_score": 70},
        "ux_designer": {"growth_rate": 13, "shortage_score": 65},
        "nurse_practitioner": {"growth_rate": 45, "shortage_score": 95},
        "physical_therapist": {"growth_rate": 18, "shortage_score": 72},
        "financial_analyst": {"growth_rate": 9, "shortage_score": 55},
    }

    # Industry growth projections 2024-2034
    INDUSTRY_GROWTH = {
        "technology": 15.0,
        "healthcare": 13.0,
        "renewable_energy": 18.0,
        "finance": 7.0,
        "manufacturing": 3.0,
        "retail": 2.0,
        "education": 5.0,
        "construction": 4.0,
        "hospitality": 6.0,
        "media": 5.0,
    }

    # Shortage score weights per spec (Differentiator 4)
    # Research basis: 2.2 openings per worker in skilled trades, 70% of jobs in hidden market
    SHORTAGE_WEIGHTS = {
        "openings": 30,  # Openings per unemployed ratio
        "quits": 20,  # Voluntary quit rate (worker confidence indicator)
        "growth": 20,  # Employment growth %
        "salary": 15,  # Salary growth %
        "projection": 15,  # 10-year BLS projection %
    }

    # User match weights per spec
    USER_MATCH_WEIGHTS = {
        "skills": 40,  # Skill alignment with role requirements
        "experience": 20,  # Experience level match
        "location": 15,  # Geographic fit
        "salary": 10,  # Salary expectations alignment
        "interest": 15,  # Career interest alignment
    }

    # Shortage score benchmarks per spec
    SHORTAGE_BENCHMARKS = {
        "openings": {"excellent": 2.0, "high": 1.5, "moderate": 1.0, "low": 0.7},
        "quits": {"excellent": 4.0, "high": 3.0, "moderate": 2.5, "low": 2.0},
        "growth": {"excellent": 5.0, "high": 3.0, "moderate": 1.0, "low": 0.0},
        "salary": {"excellent": 6.0, "high": 4.0, "moderate": 3.0, "low": 2.0},
        "projection": {"excellent": 15.0, "high": 10.0, "moderate": 5.0, "low": 0.0},
    }

    # Salary benchmarks by role and experience (annual, USD)
    SALARY_BENCHMARKS = {
        "software_engineer": {
            "entry": 75000,
            "mid": 120000,
            "senior": 175000,
            "executive": 250000,
        },
        "data_scientist": {
            "entry": 85000,
            "mid": 130000,
            "senior": 180000,
            "executive": 260000,
        },
        "product_manager": {
            "entry": 80000,
            "mid": 125000,
            "senior": 165000,
            "executive": 220000,
        },
        "ux_designer": {
            "entry": 65000,
            "mid": 95000,
            "senior": 130000,
            "executive": 175000,
        },
        "marketing_manager": {
            "entry": 55000,
            "mid": 85000,
            "senior": 120000,
            "executive": 180000,
        },
        "financial_analyst": {
            "entry": 60000,
            "mid": 90000,
            "senior": 140000,
            "executive": 200000,
        },
        "nurse": {"entry": 60000, "mid": 80000, "senior": 100000, "executive": 130000},
        "default": {
            "entry": 50000,
            "mid": 75000,
            "senior": 110000,
            "executive": 160000,
        },
    }

    @staticmethod
    def get_bls_api_key() -> Optional[str]:
        """Get BLS API key from environment."""
        return os.getenv("BLS_API_KEY")

    @staticmethod
    def get_onet_credentials() -> tuple:
        """Get O*NET credentials from environment."""
        return (os.getenv("ONET_USERNAME"), os.getenv("ONET_PASSWORD"))

    @classmethod
    async def get_market_overview(cls) -> Dict:
        """
        Get overall labor market overview.

        Returns:
            Market overview with key indicators
        """
        try:
            bls_data = await cls._fetch_bls_data(["LNS14000000"])
            unemployment_rate = cls._extract_latest_value(bls_data, "LNS14000000")
        except Exception:
            unemployment_rate = 3.7  # Fallback value

        return {
            "unemployment_rate": unemployment_rate,
            "market_condition": cls._assess_market_condition(unemployment_rate),
            "trending_industries": cls._get_trending_industries(),
            "high_demand_roles": list(cls.HIGH_DEMAND_ROLES.keys())[:5],
            "updated_at": datetime.utcnow().isoformat(),
        }

    @classmethod
    def calculate_shortage_score(
        cls,
        role: str,
        industry: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Dict:
        """
        Calculate labor shortage score for a role using 5-factor model.

        Shortage Score Formula (per spec):
        shortage = openings(30) + quits(20) + growth(20) + salary(15) + projection(15) = 100

        Research basis: 2.2 openings per worker in skilled trades, 70% hidden market.

        Args:
            role: Target job role
            industry: Industry sector
            location: Geographic location

        Returns:
            Shortage score with 5-factor breakdown
        """
        normalized_role = cls._normalize_role(role)

        # Get base role data
        role_data = cls.HIGH_DEMAND_ROLES.get(
            normalized_role, {"growth_rate": 5, "shortage_score": 50}
        )

        # Calculate 5-factor components using benchmarks
        # Openings score: Based on role shortage indicator (proxy for openings/unemployed)
        base_shortage = role_data["shortage_score"]
        openings_score = cls._score_against_benchmark(
            base_shortage / 50, cls.SHORTAGE_BENCHMARKS["openings"]  # Convert to ~ratio format
        )

        # Quits score: Higher shortage = more worker confidence to quit
        quits_score = cls._score_against_benchmark(
            base_shortage / 25, cls.SHORTAGE_BENCHMARKS["quits"]  # Proxy quit rate
        )

        # Growth score: Employment growth rate
        growth_rate = role_data["growth_rate"]
        growth_score = cls._score_against_benchmark(growth_rate, cls.SHORTAGE_BENCHMARKS["growth"])

        # Salary score: High-demand roles have higher salary growth
        salary_growth = growth_rate * 0.4  # Proxy: ~40% of employment growth
        salary_score = cls._score_against_benchmark(
            salary_growth, cls.SHORTAGE_BENCHMARKS["salary"]
        )

        # Projection score: 10-year outlook
        projection_score = cls._score_against_benchmark(
            growth_rate, cls.SHORTAGE_BENCHMARKS["projection"]
        )

        # Apply industry adjustment
        industry_multiplier = 1.0
        if industry:
            industry_growth = cls.INDUSTRY_GROWTH.get(industry.lower(), 5.0)
            industry_multiplier = 1 + (industry_growth - 5) / 30

        # Calculate weighted total per spec: openings(30) + quits(20) + growth(20) + salary(15) + projection(15)
        raw_score = (
            openings_score * (cls.SHORTAGE_WEIGHTS["openings"] / 100)
            + quits_score * (cls.SHORTAGE_WEIGHTS["quits"] / 100)
            + growth_score * (cls.SHORTAGE_WEIGHTS["growth"] / 100)
            + salary_score * (cls.SHORTAGE_WEIGHTS["salary"] / 100)
            + projection_score * (cls.SHORTAGE_WEIGHTS["projection"] / 100)
        )
        total_score = int(min(100, raw_score * industry_multiplier))

        return {
            "total_score": total_score,
            "interpretation": cls._interpret_shortage(total_score),
            "components": {
                "openings": int(openings_score),
                "quits": int(quits_score),
                "growth": int(growth_score),
                "salary": int(salary_score),
                "projection": int(projection_score),
            },
            "weights": cls.SHORTAGE_WEIGHTS,
            "role": role,
            "normalized_role": normalized_role,
            "industry": industry,
            "projected_growth": f"{role_data['growth_rate']}%",
        }

    @staticmethod
    def _score_against_benchmark(value: float, benchmarks: Dict[str, float]) -> float:
        """Score a value against benchmark thresholds (0-100 scale)."""
        if value >= benchmarks["excellent"]:
            return 100
        elif value >= benchmarks["high"]:
            return 80
        elif value >= benchmarks["moderate"]:
            return 60
        elif value >= benchmarks["low"]:
            return 40
        else:
            return 20

    @classmethod
    def calculate_user_match(
        cls,
        user_skills: List[str],
        user_experience: str,
        user_location: Optional[str],
        target_salary: Optional[int],
        user_interests: Optional[List[str]],
        target_role: str,
        target_industry: Optional[str] = None,
    ) -> Dict:
        """
        Calculate user-role match score using 5-factor model.

        User Match Formula (per spec):
        match = skills(40) + experience(20) + location(15) + salary(10) + interest(15) = 100

        Args:
            user_skills: User's skill list
            user_experience: Experience level (entry, mid, senior, executive)
            user_location: User's location
            target_salary: User's target salary
            user_interests: User's career interests/industries
            target_role: Target job role
            target_industry: Target industry

        Returns:
            User match score with 5-factor breakdown
        """
        normalized_role = cls._normalize_role(target_role)

        # 1. Skills match (40 points)
        required_skills = cls._get_required_skills(normalized_role)
        matching_skills = set(s.lower() for s in user_skills) & set(required_skills)
        skills_score = (len(matching_skills) / max(len(required_skills), 1)) * 100

        # 2. Experience match (20 points)
        role_data = cls.HIGH_DEMAND_ROLES.get(normalized_role, {"shortage_score": 50})
        experience_levels = {"entry": 25, "mid": 50, "senior": 75, "executive": 100}
        user_exp_value = experience_levels.get(user_experience, 50)
        # Higher shortage roles are more forgiving on experience
        exp_flexibility = role_data.get("shortage_score", 50) / 100
        experience_score = min(100, user_exp_value + (exp_flexibility * 25))

        # 3. Location match (15 points)
        location_score = 100  # Default to full score
        if user_location and target_industry:
            # Adjust based on industry concentration in location
            location_multiplier = cls._get_location_multiplier(user_location)
            location_score = min(100, 70 + (location_multiplier - 1) * 100)

        # 4. Salary alignment (10 points)
        salary_score = 100  # Default to full score
        if target_salary:
            benchmarks = cls.SALARY_BENCHMARKS.get(
                normalized_role, cls.SALARY_BENCHMARKS["default"]
            )
            expected_salary = benchmarks.get(user_experience, benchmarks["mid"])
            # Score based on how close target is to market rate
            salary_ratio = target_salary / expected_salary if expected_salary else 1
            if 0.85 <= salary_ratio <= 1.2:
                salary_score = 100
            elif 0.7 <= salary_ratio <= 1.35:
                salary_score = 70
            else:
                salary_score = 40

        # 5. Interest alignment (15 points)
        interest_score = 50  # Default baseline
        if user_interests:
            interests_lower = [i.lower() for i in user_interests]
            if target_industry and target_industry.lower() in interests_lower:
                interest_score = 100
            elif normalized_role in interests_lower:
                interest_score = 90
            else:
                interest_score = 60

        # Calculate weighted total per spec: skills(40) + experience(20) + location(15) + salary(10) + interest(15)
        total_score = int(
            skills_score * (cls.USER_MATCH_WEIGHTS["skills"] / 100)
            + experience_score * (cls.USER_MATCH_WEIGHTS["experience"] / 100)
            + location_score * (cls.USER_MATCH_WEIGHTS["location"] / 100)
            + salary_score * (cls.USER_MATCH_WEIGHTS["salary"] / 100)
            + interest_score * (cls.USER_MATCH_WEIGHTS["interest"] / 100)
        )

        return {
            "total_score": total_score,
            "interpretation": cls._interpret_user_match(total_score),
            "components": {
                "skills": int(skills_score),
                "experience": int(experience_score),
                "location": int(location_score),
                "salary": int(salary_score),
                "interest": int(interest_score),
            },
            "weights": cls.USER_MATCH_WEIGHTS,
            "matching_skills": list(matching_skills),
            "missing_skills": list(set(required_skills) - set(s.lower() for s in user_skills))[:5],
            "target_role": target_role,
            "target_industry": target_industry,
        }

    @staticmethod
    def _interpret_user_match(score: int) -> str:
        """Interpret user match score."""
        if score >= 80:
            return "Excellent match - Strong alignment with role requirements"
        elif score >= 60:
            return "Good match - Well suited with minor gaps"
        elif score >= 40:
            return "Moderate match - Some areas need development"
        else:
            return "Limited match - Significant skill building needed"

    @classmethod
    def get_skills_gap_by_category(
        cls,
        user_skills: List[str],
        target_role: str,
    ) -> Dict:
        """
        Get skills gap analysis broken down by category (skills, abilities, knowledge).

        Args:
            user_skills: User's skill list
            target_role: Target job role

        Returns:
            Skills gap breakdown by category with matched/missing items
        """
        from app.extensions import db
        from app.models.labor_market import Occupation, OccupationSkill, Skill

        # Normalize role for matching
        normalized = cls._normalize_role(target_role)
        search_term = normalized.replace("_", " ")

        occupation = Occupation.query.filter(Occupation.title.ilike(f"%{search_term}%")).first()

        if not occupation:
            return {"error": "Occupation not found", "role": target_role}

        user_skills_lower = {s.lower() for s in user_skills}
        result = {"role": target_role, "occupation_title": occupation.title, "categories": {}}
        total_matched = 0
        total_required = 0

        for category in ["skills", "abilities", "knowledge"]:
            required = (
                db.session.query(Skill.name)
                .join(OccupationSkill, OccupationSkill.skill_id == Skill.id)
                .filter(OccupationSkill.occupation_id == occupation.id)
                .filter(Skill.category == category)
                .filter(OccupationSkill.importance >= 3.0)
                .all()
            )

            required_names = {s.name.lower() for s in required}
            matched = user_skills_lower & required_names
            missing = required_names - user_skills_lower

            result["categories"][category] = {
                "matched": len(matched),
                "total": len(required_names),
                "pct": int(len(matched) / max(len(required_names), 1) * 100),
                "matched_items": list(matched),
                "missing_items": list(missing)[:5],
            }

            total_matched += len(matched)
            total_required += len(required_names)

        result["overall"] = {
            "matched": total_matched,
            "total": total_required,
            "pct": int(total_matched / max(total_required, 1) * 100),
        }

        return result

    @classmethod
    def get_salary_benchmark(
        cls,
        role: str,
        experience_level: str = "mid",
        location: Optional[str] = None,
    ) -> Dict:
        """
        Get salary benchmark for a role.

        Args:
            role: Job role/title
            experience_level: entry, mid, senior, executive
            location: Geographic location for adjustment

        Returns:
            Salary benchmark with range
        """
        normalized_role = cls._normalize_role(role)

        benchmarks = cls.SALARY_BENCHMARKS.get(normalized_role, cls.SALARY_BENCHMARKS["default"])

        base_salary = benchmarks.get(experience_level, benchmarks["mid"])

        # Location adjustments (simplified)
        location_multiplier = cls._get_location_multiplier(location)
        adjusted_salary = int(base_salary * location_multiplier)

        return {
            "role": role,
            "experience_level": experience_level,
            "base_salary": base_salary,
            "adjusted_salary": adjusted_salary,
            "location": location,
            "location_adjustment": f"{(location_multiplier - 1) * 100:+.0f}%",
            "range": {
                "low": int(adjusted_salary * 0.85),
                "median": adjusted_salary,
                "high": int(adjusted_salary * 1.20),
            },
            "all_levels": {
                level: int(salary * location_multiplier) for level, salary in benchmarks.items()
            },
        }

    @classmethod
    def calculate_opportunity_score(
        cls,
        user_skills: List[str],
        target_role: str,
        target_industry: Optional[str] = None,
        user_experience: str = "mid",
        user_location: Optional[str] = None,
        target_salary: Optional[int] = None,
        user_interests: Optional[List[str]] = None,
    ) -> Dict:
        """
        Calculate opportunity score using geometric mean formula.

        Opportunity Score Formula (per spec):
        opportunity = √(user_match × shortage)  [GEOMETRIC MEAN]

        This formula ensures both user fit AND market demand must be strong.
        A high shortage with low match = moderate opportunity.
        A high match with low shortage = moderate opportunity.
        High match AND high shortage = excellent opportunity.

        Args:
            user_skills: User's skills list
            target_role: Target job role
            target_industry: Target industry
            user_experience: Experience level (entry, mid, senior, executive)
            user_location: User's location
            target_salary: User's target salary
            user_interests: User's career interests

        Returns:
            Opportunity score with geometric mean calculation
        """
        # Get shortage score (market demand)
        shortage = cls.calculate_shortage_score(target_role, target_industry)

        # Get user match score (user fit)
        user_match = cls.calculate_user_match(
            user_skills=user_skills,
            user_experience=user_experience,
            user_location=user_location,
            target_salary=target_salary,
            user_interests=user_interests,
            target_role=target_role,
            target_industry=target_industry,
        )

        # Calculate opportunity using GEOMETRIC MEAN per spec: √(match × shortage)
        match_score = user_match["total_score"]
        shortage_score = shortage["total_score"]
        total_score = int(round(math.sqrt(match_score * shortage_score)))

        # Generate recommendations based on which factor is weaker
        missing_skills = user_match.get("missing_skills", [])

        return {
            "total_score": total_score,
            "interpretation": cls._interpret_opportunity(total_score),
            "formula": "√(user_match × shortage)",
            "components": {
                "user_match": match_score,
                "shortage": shortage_score,
            },
            "user_match_breakdown": user_match["components"],
            "shortage_breakdown": shortage["components"],
            "target_role": target_role,
            "target_industry": target_industry,
            "matching_skills": user_match.get("matching_skills", []),
            "missing_skills": missing_skills,
            "recommendations": cls._generate_opportunity_recommendations(
                total_score, match_score, set(missing_skills)
            ),
        }

    @classmethod
    def get_job_outlook(cls, role: str) -> Dict:
        """
        Get detailed job outlook for a role.

        Args:
            role: Job role/title

        Returns:
            Job outlook with projections
        """
        normalized_role = cls._normalize_role(role)
        role_data = cls.HIGH_DEMAND_ROLES.get(
            normalized_role, {"growth_rate": 5, "shortage_score": 50}
        )

        return {
            "role": role,
            "growth_rate": role_data["growth_rate"],
            "outlook": cls._interpret_growth(role_data["growth_rate"]),
            "demand_level": cls._interpret_demand(role_data["shortage_score"]),
            "projection_period": "2024-2034",
            "factors": cls._get_growth_factors(normalized_role),
            "related_roles": cls._get_related_roles(normalized_role),
        }

    # Private helper methods

    @classmethod
    async def _fetch_bls_data(cls, series_ids: List[str]) -> Dict:
        """Fetch data from BLS API."""
        api_key = cls.get_bls_api_key()

        headers = {"Content-Type": "application/json"}
        payload = {
            "seriesid": series_ids,
            "startyear": str(datetime.now().year - 1),
            "endyear": str(datetime.now().year),
        }

        if api_key:
            payload["registrationkey"] = api_key

        async with httpx.AsyncClient() as client:
            response = await client.post(
                cls.BLS_BASE_URL, json=payload, headers=headers, timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    def _extract_latest_value(bls_data: Dict, series_id: str) -> float:
        """Extract latest value from BLS response."""
        try:
            for series in bls_data.get("Results", {}).get("series", []):
                if series.get("seriesID") == series_id:
                    data = series.get("data", [])
                    if data:
                        return float(data[0].get("value", 0))
        except (KeyError, IndexError, ValueError):
            pass
        return 0.0

    @staticmethod
    def _assess_market_condition(unemployment_rate: float) -> str:
        """Assess market condition based on unemployment rate."""
        if unemployment_rate < 4.0:
            return "strong"
        elif unemployment_rate < 5.5:
            return "moderate"
        elif unemployment_rate < 7.0:
            return "challenging"
        else:
            return "difficult"

    @classmethod
    def _get_trending_industries(cls) -> List[Dict]:
        """Get list of trending industries."""
        sorted_industries = sorted(cls.INDUSTRY_GROWTH.items(), key=lambda x: x[1], reverse=True)
        return [{"name": name, "growth_rate": rate} for name, rate in sorted_industries[:5]]

    @staticmethod
    def _normalize_role(role: str) -> str:
        """Normalize role name for lookup."""
        role_lower = role.lower().replace(" ", "_").replace("-", "_")

        # Common mappings
        mappings = {
            "software_developer": "software_engineer",
            "swe": "software_engineer",
            "backend_engineer": "software_engineer",
            "frontend_engineer": "software_engineer",
            "ml_engineer": "data_scientist",
            "machine_learning": "data_scientist",
            "security_engineer": "cybersecurity",
            "infosec": "cybersecurity",
            "pm": "product_manager",
            "ui_designer": "ux_designer",
            "ui/ux": "ux_designer",
        }

        return mappings.get(role_lower, role_lower)

    @staticmethod
    def _interpret_shortage(score: int) -> str:
        """Interpret shortage score."""
        if score >= 80:
            return "Critical shortage - Very high demand"
        elif score >= 60:
            return "Significant shortage - High demand"
        elif score >= 40:
            return "Moderate demand - Balanced market"
        else:
            return "Low shortage - Competitive market"

    @staticmethod
    def _interpret_opportunity(score: int) -> str:
        """Interpret opportunity score."""
        if score >= 80:
            return "Excellent opportunity - Strong alignment"
        elif score >= 60:
            return "Good opportunity - Consider pursuing"
        elif score >= 40:
            return "Moderate opportunity - Some skill gaps"
        else:
            return "Limited opportunity - Significant preparation needed"

    @staticmethod
    def _interpret_growth(rate: float) -> str:
        """Interpret growth rate."""
        if rate >= 20:
            return "Much faster than average"
        elif rate >= 10:
            return "Faster than average"
        elif rate >= 5:
            return "Average growth"
        else:
            return "Slower than average"

    @staticmethod
    def _interpret_demand(score: int) -> str:
        """Interpret demand level."""
        if score >= 80:
            return "Very High"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Moderate"
        else:
            return "Low"

    @staticmethod
    def _get_location_multiplier(location: Optional[str]) -> float:
        """Get salary multiplier for location."""
        if not location:
            return 1.0

        location_lower = location.lower()

        # High cost areas
        high_cost = ["san francisco", "new york", "seattle", "boston", "los angeles"]
        if any(city in location_lower for city in high_cost):
            return 1.35

        # Medium-high cost
        medium_high = ["denver", "austin", "chicago", "washington", "san diego"]
        if any(city in location_lower for city in medium_high):
            return 1.15

        # Medium cost
        medium = ["atlanta", "dallas", "phoenix", "portland", "miami"]
        if any(city in location_lower for city in medium):
            return 1.05

        return 1.0

    @staticmethod
    def _get_required_skills(role: str) -> List[str]:
        """Get required skills/abilities/knowledge for a role from O*NET database."""
        from app.extensions import db
        from app.models.labor_market import Occupation, OccupationSkill, Skill

        # Normalize role for matching
        normalized = LaborMarketService._normalize_role(role)
        search_term = normalized.replace("_", " ")

        # Find matching occupation by title
        occupation = Occupation.query.filter(Occupation.title.ilike(f"%{search_term}%")).first()

        if not occupation:
            # Fallback to generic skills
            return ["communication", "problem solving", "teamwork"]

        # Get all skills/abilities/knowledge for this occupation (importance >= 3.0)
        occ_skills = (
            db.session.query(Skill.name)
            .join(OccupationSkill, OccupationSkill.skill_id == Skill.id)
            .filter(OccupationSkill.occupation_id == occupation.id)
            .filter(OccupationSkill.importance >= 3.0)
            .all()
        )

        if not occ_skills:
            return ["communication", "problem solving", "teamwork"]

        return [s.name.lower() for s in occ_skills]

    @staticmethod
    def _generate_opportunity_recommendations(
        total_score: int, skill_match: float, missing_skills: set
    ) -> List[str]:
        """Generate recommendations based on opportunity analysis."""
        recommendations = []

        if skill_match < 60:
            recommendations.append(
                f"Focus on developing these key skills: {', '.join(list(missing_skills)[:3])}"
            )

        if total_score >= 70:
            recommendations.append(
                "Market conditions are favorable - consider actively pursuing opportunities"
            )
        elif total_score >= 50:
            recommendations.append(
                "Build your network in this field while developing missing skills"
            )
        else:
            recommendations.append(
                "Consider gaining experience through projects or certifications first"
            )

        if missing_skills:
            recommendations.append(
                "Look for online courses or bootcamps to quickly acquire in-demand skills"
            )

        return recommendations[:3]

    @staticmethod
    def _get_growth_factors(role: str) -> List[str]:
        """Get factors driving growth for a role."""
        factors_map = {
            "software_engineer": [
                "Digital transformation across industries",
                "Growing demand for web and mobile applications",
                "Expansion of cloud computing",
            ],
            "data_scientist": [
                "Increased focus on data-driven decision making",
                "AI and machine learning adoption",
                "Growing volume of business data",
            ],
            "cybersecurity": [
                "Rising cyber threats and attacks",
                "Regulatory compliance requirements",
                "Digital infrastructure expansion",
            ],
            "nurse_practitioner": [
                "Aging population",
                "Primary care physician shortage",
                "Expanded scope of practice",
            ],
        }
        return factors_map.get(
            role,
            [
                "Industry growth",
                "Technology adoption",
                "Workforce transitions",
            ],
        )

    @staticmethod
    def _get_related_roles(role: str) -> List[str]:
        """Get related roles for career exploration."""
        related_map = {
            "software_engineer": [
                "DevOps Engineer",
                "Technical Lead",
                "Solutions Architect",
            ],
            "data_scientist": ["ML Engineer", "Data Engineer", "AI Researcher"],
            "product_manager": [
                "Program Manager",
                "Product Owner",
                "Chief Product Officer",
            ],
            "ux_designer": ["UI Designer", "Product Designer", "Design Lead"],
        }
        return related_map.get(role, ["Related roles vary by industry"])


# Synchronous wrappers for Flask routes
def get_market_overview_sync() -> Dict:
    """Synchronous wrapper for get_market_overview."""
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(LaborMarketService.get_market_overview())
    finally:
        loop.close()
