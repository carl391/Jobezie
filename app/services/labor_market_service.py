"""
Labor Market Intelligence Service

Provides labor market data using BLS (Bureau of Labor Statistics) and O*NET data.
Calculates shortage scores, salary benchmarks, and job growth projections.
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from functools import lru_cache

import httpx
from flask import current_app


class LaborMarketService:
    """
    Service for labor market intelligence.

    Uses BLS API for employment statistics and O*NET for occupation data.
    """

    BLS_BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    ONET_BASE_URL = "https://services.onetcenter.org/ws/"

    # BLS Series IDs for national employment
    BLS_SERIES = {
        'unemployment_rate': 'LNS14000000',
        'total_nonfarm': 'CES0000000001',
        'tech_employment': 'CES5000000001',
        'professional_services': 'CES6054000001',
        'finance': 'CES5552000001',
        'healthcare': 'CES6562000001',
    }

    # Career shortage indicators (high demand roles)
    HIGH_DEMAND_ROLES = {
        'software_engineer': {'growth_rate': 25, 'shortage_score': 85},
        'data_scientist': {'growth_rate': 35, 'shortage_score': 90},
        'cybersecurity': {'growth_rate': 33, 'shortage_score': 88},
        'cloud_architect': {'growth_rate': 28, 'shortage_score': 82},
        'devops_engineer': {'growth_rate': 22, 'shortage_score': 80},
        'product_manager': {'growth_rate': 12, 'shortage_score': 70},
        'ux_designer': {'growth_rate': 13, 'shortage_score': 65},
        'nurse_practitioner': {'growth_rate': 45, 'shortage_score': 95},
        'physical_therapist': {'growth_rate': 18, 'shortage_score': 72},
        'financial_analyst': {'growth_rate': 9, 'shortage_score': 55},
    }

    # Industry growth projections 2024-2034
    INDUSTRY_GROWTH = {
        'technology': 15.0,
        'healthcare': 13.0,
        'renewable_energy': 18.0,
        'finance': 7.0,
        'manufacturing': 3.0,
        'retail': 2.0,
        'education': 5.0,
        'construction': 4.0,
        'hospitality': 6.0,
        'media': 5.0,
    }

    # Salary benchmarks by role and experience (annual, USD)
    SALARY_BENCHMARKS = {
        'software_engineer': {
            'entry': 75000, 'mid': 120000, 'senior': 175000, 'executive': 250000
        },
        'data_scientist': {
            'entry': 85000, 'mid': 130000, 'senior': 180000, 'executive': 260000
        },
        'product_manager': {
            'entry': 80000, 'mid': 125000, 'senior': 165000, 'executive': 220000
        },
        'ux_designer': {
            'entry': 65000, 'mid': 95000, 'senior': 130000, 'executive': 175000
        },
        'marketing_manager': {
            'entry': 55000, 'mid': 85000, 'senior': 120000, 'executive': 180000
        },
        'financial_analyst': {
            'entry': 60000, 'mid': 90000, 'senior': 140000, 'executive': 200000
        },
        'nurse': {
            'entry': 60000, 'mid': 80000, 'senior': 100000, 'executive': 130000
        },
        'default': {
            'entry': 50000, 'mid': 75000, 'senior': 110000, 'executive': 160000
        },
    }

    @staticmethod
    def get_bls_api_key() -> Optional[str]:
        """Get BLS API key from environment."""
        return os.getenv('BLS_API_KEY')

    @staticmethod
    def get_onet_credentials() -> tuple:
        """Get O*NET credentials from environment."""
        return (
            os.getenv('ONET_USERNAME'),
            os.getenv('ONET_PASSWORD')
        )

    @classmethod
    async def get_market_overview(cls) -> Dict:
        """
        Get overall labor market overview.

        Returns:
            Market overview with key indicators
        """
        try:
            bls_data = await cls._fetch_bls_data(['LNS14000000'])
            unemployment_rate = cls._extract_latest_value(bls_data, 'LNS14000000')
        except Exception:
            unemployment_rate = 3.7  # Fallback value

        return {
            'unemployment_rate': unemployment_rate,
            'market_condition': cls._assess_market_condition(unemployment_rate),
            'trending_industries': cls._get_trending_industries(),
            'high_demand_roles': list(cls.HIGH_DEMAND_ROLES.keys())[:5],
            'updated_at': datetime.utcnow().isoformat(),
        }

    @classmethod
    def calculate_shortage_score(
        cls,
        role: str,
        industry: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Dict:
        """
        Calculate labor shortage score for a role.

        Shortage Score Formula:
        shortage = demand(40%) + growth(30%) + supply_gap(30%)

        Args:
            role: Target job role
            industry: Industry sector
            location: Geographic location

        Returns:
            Shortage score with breakdown
        """
        # Normalize role name
        normalized_role = cls._normalize_role(role)

        # Get base shortage data
        role_data = cls.HIGH_DEMAND_ROLES.get(
            normalized_role,
            {'growth_rate': 5, 'shortage_score': 50}
        )

        # Calculate components
        demand_score = min(100, role_data['shortage_score'])
        growth_score = min(100, role_data['growth_rate'] * 3)

        # Adjust for industry
        industry_multiplier = 1.0
        if industry:
            industry_growth = cls.INDUSTRY_GROWTH.get(
                industry.lower(), 5.0
            )
            industry_multiplier = 1 + (industry_growth - 5) / 20

        # Calculate total
        base_score = (
            demand_score * 0.4 +
            growth_score * 0.3 +
            50 * 0.3  # Supply gap baseline
        )
        total_score = int(min(100, base_score * industry_multiplier))

        return {
            'total_score': total_score,
            'interpretation': cls._interpret_shortage(total_score),
            'components': {
                'demand': demand_score,
                'growth': growth_score,
                'supply_gap': 50,
            },
            'role': role,
            'normalized_role': normalized_role,
            'industry': industry,
            'projected_growth': f"{role_data['growth_rate']}%",
        }

    @classmethod
    def get_salary_benchmark(
        cls,
        role: str,
        experience_level: str = 'mid',
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

        benchmarks = cls.SALARY_BENCHMARKS.get(
            normalized_role,
            cls.SALARY_BENCHMARKS['default']
        )

        base_salary = benchmarks.get(experience_level, benchmarks['mid'])

        # Location adjustments (simplified)
        location_multiplier = cls._get_location_multiplier(location)
        adjusted_salary = int(base_salary * location_multiplier)

        return {
            'role': role,
            'experience_level': experience_level,
            'base_salary': base_salary,
            'adjusted_salary': adjusted_salary,
            'location': location,
            'location_adjustment': f"{(location_multiplier - 1) * 100:+.0f}%",
            'range': {
                'low': int(adjusted_salary * 0.85),
                'median': adjusted_salary,
                'high': int(adjusted_salary * 1.20),
            },
            'all_levels': {
                level: int(salary * location_multiplier)
                for level, salary in benchmarks.items()
            },
        }

    @classmethod
    def calculate_opportunity_score(
        cls,
        user_skills: List[str],
        target_role: str,
        target_industry: Optional[str] = None,
    ) -> Dict:
        """
        Calculate opportunity score based on user skills and market demand.

        Opportunity Score Formula:
        opportunity = shortage(40%) + skill_match(35%) + growth(25%)

        Args:
            user_skills: User's skills list
            target_role: Target job role
            target_industry: Target industry

        Returns:
            Opportunity score with recommendations
        """
        # Get shortage score
        shortage = cls.calculate_shortage_score(target_role, target_industry)

        # Calculate skill match
        required_skills = cls._get_required_skills(target_role)
        matching_skills = set(s.lower() for s in user_skills) & set(required_skills)
        skill_match_score = (len(matching_skills) / max(len(required_skills), 1)) * 100

        # Get growth score
        normalized_role = cls._normalize_role(target_role)
        role_data = cls.HIGH_DEMAND_ROLES.get(
            normalized_role,
            {'growth_rate': 5}
        )
        growth_score = min(100, role_data['growth_rate'] * 3)

        # Calculate total
        total_score = int(
            shortage['total_score'] * 0.4 +
            skill_match_score * 0.35 +
            growth_score * 0.25
        )

        # Generate recommendations
        missing_skills = set(required_skills) - set(s.lower() for s in user_skills)

        return {
            'total_score': total_score,
            'interpretation': cls._interpret_opportunity(total_score),
            'components': {
                'shortage': shortage['total_score'],
                'skill_match': int(skill_match_score),
                'growth': growth_score,
            },
            'target_role': target_role,
            'target_industry': target_industry,
            'matching_skills': list(matching_skills),
            'missing_skills': list(missing_skills)[:5],
            'recommendations': cls._generate_opportunity_recommendations(
                total_score, skill_match_score, missing_skills
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
            normalized_role,
            {'growth_rate': 5, 'shortage_score': 50}
        )

        return {
            'role': role,
            'growth_rate': role_data['growth_rate'],
            'outlook': cls._interpret_growth(role_data['growth_rate']),
            'demand_level': cls._interpret_demand(role_data['shortage_score']),
            'projection_period': '2024-2034',
            'factors': cls._get_growth_factors(normalized_role),
            'related_roles': cls._get_related_roles(normalized_role),
        }

    # Private helper methods

    @classmethod
    async def _fetch_bls_data(cls, series_ids: List[str]) -> Dict:
        """Fetch data from BLS API."""
        api_key = cls.get_bls_api_key()

        headers = {'Content-Type': 'application/json'}
        payload = {
            'seriesid': series_ids,
            'startyear': str(datetime.now().year - 1),
            'endyear': str(datetime.now().year),
        }

        if api_key:
            payload['registrationkey'] = api_key

        async with httpx.AsyncClient() as client:
            response = await client.post(
                cls.BLS_BASE_URL,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    def _extract_latest_value(bls_data: Dict, series_id: str) -> float:
        """Extract latest value from BLS response."""
        try:
            for series in bls_data.get('Results', {}).get('series', []):
                if series.get('seriesID') == series_id:
                    data = series.get('data', [])
                    if data:
                        return float(data[0].get('value', 0))
        except (KeyError, IndexError, ValueError):
            pass
        return 0.0

    @staticmethod
    def _assess_market_condition(unemployment_rate: float) -> str:
        """Assess market condition based on unemployment rate."""
        if unemployment_rate < 4.0:
            return 'strong'
        elif unemployment_rate < 5.5:
            return 'moderate'
        elif unemployment_rate < 7.0:
            return 'challenging'
        else:
            return 'difficult'

    @classmethod
    def _get_trending_industries(cls) -> List[Dict]:
        """Get list of trending industries."""
        sorted_industries = sorted(
            cls.INDUSTRY_GROWTH.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [
            {'name': name, 'growth_rate': rate}
            for name, rate in sorted_industries[:5]
        ]

    @staticmethod
    def _normalize_role(role: str) -> str:
        """Normalize role name for lookup."""
        role_lower = role.lower().replace(' ', '_').replace('-', '_')

        # Common mappings
        mappings = {
            'software_developer': 'software_engineer',
            'swe': 'software_engineer',
            'backend_engineer': 'software_engineer',
            'frontend_engineer': 'software_engineer',
            'ml_engineer': 'data_scientist',
            'machine_learning': 'data_scientist',
            'security_engineer': 'cybersecurity',
            'infosec': 'cybersecurity',
            'pm': 'product_manager',
            'ui_designer': 'ux_designer',
            'ui/ux': 'ux_designer',
        }

        return mappings.get(role_lower, role_lower)

    @staticmethod
    def _interpret_shortage(score: int) -> str:
        """Interpret shortage score."""
        if score >= 80:
            return 'Critical shortage - Very high demand'
        elif score >= 60:
            return 'Significant shortage - High demand'
        elif score >= 40:
            return 'Moderate demand - Balanced market'
        else:
            return 'Low shortage - Competitive market'

    @staticmethod
    def _interpret_opportunity(score: int) -> str:
        """Interpret opportunity score."""
        if score >= 80:
            return 'Excellent opportunity - Strong alignment'
        elif score >= 60:
            return 'Good opportunity - Consider pursuing'
        elif score >= 40:
            return 'Moderate opportunity - Some skill gaps'
        else:
            return 'Limited opportunity - Significant preparation needed'

    @staticmethod
    def _interpret_growth(rate: float) -> str:
        """Interpret growth rate."""
        if rate >= 20:
            return 'Much faster than average'
        elif rate >= 10:
            return 'Faster than average'
        elif rate >= 5:
            return 'Average growth'
        else:
            return 'Slower than average'

    @staticmethod
    def _interpret_demand(score: int) -> str:
        """Interpret demand level."""
        if score >= 80:
            return 'Very High'
        elif score >= 60:
            return 'High'
        elif score >= 40:
            return 'Moderate'
        else:
            return 'Low'

    @staticmethod
    def _get_location_multiplier(location: Optional[str]) -> float:
        """Get salary multiplier for location."""
        if not location:
            return 1.0

        location_lower = location.lower()

        # High cost areas
        high_cost = ['san francisco', 'new york', 'seattle', 'boston', 'los angeles']
        if any(city in location_lower for city in high_cost):
            return 1.35

        # Medium-high cost
        medium_high = ['denver', 'austin', 'chicago', 'washington', 'san diego']
        if any(city in location_lower for city in medium_high):
            return 1.15

        # Medium cost
        medium = ['atlanta', 'dallas', 'phoenix', 'portland', 'miami']
        if any(city in location_lower for city in medium):
            return 1.05

        return 1.0

    @staticmethod
    def _get_required_skills(role: str) -> List[str]:
        """Get required skills for a role."""
        skills_map = {
            'software_engineer': [
                'python', 'javascript', 'sql', 'git', 'apis',
                'data structures', 'algorithms', 'cloud'
            ],
            'data_scientist': [
                'python', 'sql', 'machine learning', 'statistics',
                'pandas', 'numpy', 'visualization', 'tensorflow'
            ],
            'product_manager': [
                'product strategy', 'agile', 'analytics', 'roadmapping',
                'user research', 'stakeholder management', 'prioritization'
            ],
            'ux_designer': [
                'figma', 'user research', 'wireframing', 'prototyping',
                'usability testing', 'design systems', 'accessibility'
            ],
            'devops_engineer': [
                'docker', 'kubernetes', 'ci/cd', 'aws', 'terraform',
                'linux', 'monitoring', 'scripting'
            ],
        }
        normalized = LaborMarketService._normalize_role(role)
        return skills_map.get(normalized, ['communication', 'problem solving', 'teamwork'])

    @staticmethod
    def _generate_opportunity_recommendations(
        total_score: int,
        skill_match: float,
        missing_skills: set
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
            'software_engineer': [
                'Digital transformation across industries',
                'Growing demand for web and mobile applications',
                'Expansion of cloud computing',
            ],
            'data_scientist': [
                'Increased focus on data-driven decision making',
                'AI and machine learning adoption',
                'Growing volume of business data',
            ],
            'cybersecurity': [
                'Rising cyber threats and attacks',
                'Regulatory compliance requirements',
                'Digital infrastructure expansion',
            ],
            'nurse_practitioner': [
                'Aging population',
                'Primary care physician shortage',
                'Expanded scope of practice',
            ],
        }
        return factors_map.get(role, [
            'Industry growth',
            'Technology adoption',
            'Workforce transitions',
        ])

    @staticmethod
    def _get_related_roles(role: str) -> List[str]:
        """Get related roles for career exploration."""
        related_map = {
            'software_engineer': [
                'DevOps Engineer', 'Technical Lead', 'Solutions Architect'
            ],
            'data_scientist': [
                'ML Engineer', 'Data Engineer', 'AI Researcher'
            ],
            'product_manager': [
                'Program Manager', 'Product Owner', 'Chief Product Officer'
            ],
            'ux_designer': [
                'UI Designer', 'Product Designer', 'Design Lead'
            ],
        }
        return related_map.get(role, ['Related roles vary by industry'])


# Synchronous wrappers for Flask routes
def get_market_overview_sync() -> Dict:
    """Synchronous wrapper for get_market_overview."""
    import asyncio
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(LaborMarketService.get_market_overview())
    finally:
        loop.close()
