"""
LinkedIn Optimizer Service

Provides LinkedIn profile optimization, headline generation, and visibility scoring.
"""

import re
from typing import Dict, List, Optional
from datetime import datetime

from flask import current_app


class LinkedInService:
    """
    Service for LinkedIn profile optimization.

    Provides analysis and recommendations for improving LinkedIn presence.
    """

    # LinkedIn character limits
    LIMITS = {
        'headline': 220,
        'summary': 2600,
        'experience_description': 2000,
        'skills': 50,
    }

    # Headline formula weights
    HEADLINE_WEIGHTS = {
        'role_clarity': 25,
        'value_proposition': 25,
        'keywords': 25,
        'achievements': 15,
        'cta': 10,
    }

    # Profile completeness sections
    PROFILE_SECTIONS = [
        'headline',
        'summary',
        'experience',
        'education',
        'skills',
        'photo',
        'banner',
        'contact_info',
        'certifications',
        'recommendations',
    ]

    # Industry keywords for optimization
    INDUSTRY_KEYWORDS = {
        'technology': [
            'software', 'engineering', 'developer', 'cloud', 'data',
            'agile', 'product', 'technical', 'systems', 'architecture'
        ],
        'finance': [
            'finance', 'investment', 'banking', 'portfolio', 'risk',
            'analysis', 'trading', 'compliance', 'accounting', 'advisory'
        ],
        'marketing': [
            'marketing', 'digital', 'brand', 'growth', 'content',
            'strategy', 'campaigns', 'analytics', 'social', 'engagement'
        ],
        'healthcare': [
            'healthcare', 'clinical', 'patient', 'medical', 'nursing',
            'health', 'care', 'hospital', 'treatment', 'diagnosis'
        ],
        'sales': [
            'sales', 'revenue', 'business development', 'account',
            'client', 'partnership', 'quota', 'pipeline', 'closing', 'growth'
        ],
    }

    # Power words for LinkedIn
    POWER_WORDS = [
        'achieved', 'accelerated', 'built', 'created', 'delivered',
        'designed', 'developed', 'drove', 'enabled', 'established',
        'generated', 'grew', 'implemented', 'improved', 'increased',
        'launched', 'led', 'managed', 'optimized', 'pioneered',
        'reduced', 'scaled', 'spearheaded', 'streamlined', 'transformed',
    ]

    @classmethod
    def analyze_profile(
        cls,
        profile_data: Dict,
    ) -> Dict:
        """
        Analyze LinkedIn profile and provide optimization score.

        Args:
            profile_data: Dictionary with profile sections

        Returns:
            Analysis with scores and recommendations
        """
        scores = {}
        recommendations = []

        # Analyze each section
        headline_analysis = cls._analyze_headline(profile_data.get('headline', ''))
        scores['headline'] = headline_analysis['score']
        recommendations.extend(headline_analysis['recommendations'])

        summary_analysis = cls._analyze_summary(profile_data.get('summary', ''))
        scores['summary'] = summary_analysis['score']
        recommendations.extend(summary_analysis['recommendations'])

        experience_analysis = cls._analyze_experience(
            profile_data.get('experience', [])
        )
        scores['experience'] = experience_analysis['score']
        recommendations.extend(experience_analysis['recommendations'])

        skills_analysis = cls._analyze_skills(
            profile_data.get('skills', []),
            profile_data.get('target_role', '')
        )
        scores['skills'] = skills_analysis['score']
        recommendations.extend(skills_analysis['recommendations'])

        # Calculate completeness
        completeness = cls._calculate_completeness(profile_data)

        # Calculate total score
        total_score = int(
            scores.get('headline', 0) * 0.20 +
            scores.get('summary', 0) * 0.25 +
            scores.get('experience', 0) * 0.30 +
            scores.get('skills', 0) * 0.15 +
            completeness * 0.10
        )

        return {
            'total_score': total_score,
            'interpretation': cls._interpret_score(total_score),
            'section_scores': scores,
            'completeness': completeness,
            'recommendations': recommendations[:10],
            'priority_actions': cls._get_priority_actions(scores, completeness),
        }

    @classmethod
    def generate_headline(
        cls,
        current_role: str,
        target_role: Optional[str] = None,
        industry: Optional[str] = None,
        key_skills: Optional[List[str]] = None,
        achievements: Optional[List[str]] = None,
    ) -> Dict:
        """
        Generate optimized LinkedIn headline options.

        Args:
            current_role: Current job title
            target_role: Target job title (if different)
            industry: Industry sector
            key_skills: Top skills to highlight
            achievements: Key achievements to mention

        Returns:
            Multiple headline options with scores
        """
        headlines = []

        role_to_use = target_role or current_role

        # Option 1: Role + Value Proposition
        if key_skills:
            headline1 = f"{role_to_use} | Specializing in {', '.join(key_skills[:2])}"
            headlines.append({
                'text': headline1[:cls.LIMITS['headline']],
                'type': 'role_value',
                'score': 75,
            })

        # Option 2: Role + Achievement
        if achievements:
            achievement = achievements[0][:50]
            headline2 = f"{role_to_use} | {achievement}"
            headlines.append({
                'text': headline2[:cls.LIMITS['headline']],
                'type': 'role_achievement',
                'score': 80,
            })

        # Option 3: Industry Expert
        if industry:
            headline3 = f"{role_to_use} | {industry.title()} Professional"
            if key_skills:
                headline3 += f" | {key_skills[0]}"
            headlines.append({
                'text': headline3[:cls.LIMITS['headline']],
                'type': 'industry_expert',
                'score': 70,
            })

        # Option 4: Problem Solver
        headline4 = f"{role_to_use} | Helping companies "
        if industry == 'technology':
            headline4 += "build scalable solutions"
        elif industry == 'sales':
            headline4 += "accelerate revenue growth"
        elif industry == 'marketing':
            headline4 += "drive brand engagement"
        else:
            headline4 += "achieve their goals"
        headlines.append({
            'text': headline4[:cls.LIMITS['headline']],
            'type': 'problem_solver',
            'score': 85,
        })

        # Option 5: Keywords Focused
        keywords = cls.INDUSTRY_KEYWORDS.get(
            (industry or '').lower(),
            ['professional', 'experienced', 'dedicated']
        )
        headline5 = f"{role_to_use} | {keywords[0].title()} | {keywords[1].title()}"
        if key_skills:
            headline5 += f" | {key_skills[0]}"
        headlines.append({
            'text': headline5[:cls.LIMITS['headline']],
            'type': 'keyword_rich',
            'score': 72,
        })

        # Sort by score
        headlines.sort(key=lambda x: x['score'], reverse=True)

        return {
            'headlines': headlines,
            'best_option': headlines[0] if headlines else None,
            'tips': [
                'Include your target role for recruiter searches',
                'Add 2-3 keywords relevant to your industry',
                'Mention a specific value you bring',
                f'Keep under {cls.LIMITS["headline"]} characters',
            ],
        }

    @classmethod
    def generate_summary(
        cls,
        current_role: str,
        years_experience: int,
        industry: str,
        key_skills: List[str],
        achievements: List[str],
        career_goals: Optional[str] = None,
    ) -> Dict:
        """
        Generate optimized LinkedIn summary/about section.

        Args:
            current_role: Current job title
            years_experience: Years of experience
            industry: Industry sector
            key_skills: Key skills to highlight
            achievements: Key achievements
            career_goals: Career objectives

        Returns:
            Generated summary with structure
        """
        # Build summary sections
        sections = []

        # Hook/Opening
        opening = f"With {years_experience}+ years in {industry}, "
        opening += f"I help organizations {cls._get_value_statement(industry)}."
        sections.append(('opening', opening))

        # Skills & Expertise
        if key_skills:
            skills_section = "Areas of expertise include: "
            skills_section += ", ".join(key_skills[:5])
            sections.append(('expertise', skills_section))

        # Achievements
        if achievements:
            achievements_section = "Key accomplishments:\n"
            for achievement in achievements[:3]:
                achievements_section += f"- {achievement}\n"
            sections.append(('achievements', achievements_section.strip()))

        # Career goals / CTA
        if career_goals:
            cta_section = f"Currently focused on: {career_goals}"
        else:
            cta_section = "Always open to connecting with fellow professionals "
            cta_section += f"in {industry}. Let's chat!"
        sections.append(('cta', cta_section))

        # Combine
        full_summary = "\n\n".join(text for _, text in sections)

        # Check length
        if len(full_summary) > cls.LIMITS['summary']:
            full_summary = full_summary[:cls.LIMITS['summary'] - 3] + "..."

        return {
            'summary': full_summary,
            'character_count': len(full_summary),
            'character_limit': cls.LIMITS['summary'],
            'sections': [
                {'name': name, 'content': text}
                for name, text in sections
            ],
            'tips': [
                'Start with a compelling hook in the first 2 lines',
                'Include 3-5 industry keywords naturally',
                'Highlight 2-3 quantified achievements',
                'End with a call-to-action',
                'Use short paragraphs for readability',
            ],
        }

    @classmethod
    def optimize_experience(
        cls,
        experience_entry: Dict,
        target_keywords: Optional[List[str]] = None,
    ) -> Dict:
        """
        Optimize a single experience entry.

        Args:
            experience_entry: Experience data (title, company, description)
            target_keywords: Keywords to incorporate

        Returns:
            Optimized experience with suggestions
        """
        title = experience_entry.get('title', '')
        company = experience_entry.get('company', '')
        description = experience_entry.get('description', '')

        # Analyze current description
        has_metrics = bool(re.search(r'\d+%|\$\d+|\d+ (year|month|people|team)', description))
        has_power_words = any(word in description.lower() for word in cls.POWER_WORDS)
        bullet_count = description.count('•') + description.count('-')

        # Generate optimized bullets
        optimized_bullets = []

        if description:
            # Extract key points
            sentences = re.split(r'[.•\-\n]', description)
            for sentence in sentences[:5]:
                sentence = sentence.strip()
                if len(sentence) > 20:
                    optimized = cls._enhance_bullet(sentence)
                    optimized_bullets.append(optimized)

        # Score
        score = 50  # Base
        if has_metrics:
            score += 20
        if has_power_words:
            score += 15
        if bullet_count >= 3:
            score += 15

        return {
            'original': experience_entry,
            'analysis': {
                'score': score,
                'has_metrics': has_metrics,
                'has_power_words': has_power_words,
                'bullet_count': bullet_count,
            },
            'optimized_bullets': optimized_bullets,
            'suggestions': [
                'Add specific metrics (%, $, numbers)',
                'Start bullets with action verbs',
                'Include 3-5 bullet points per role',
                'Highlight impact, not just responsibilities',
            ],
        }

    @classmethod
    def calculate_visibility_score(
        cls,
        profile_data: Dict,
    ) -> Dict:
        """
        Calculate LinkedIn visibility/searchability score.

        Args:
            profile_data: Profile information

        Returns:
            Visibility score with improvement suggestions
        """
        score = 0
        factors = {}

        # Headline keywords (25 points)
        headline = profile_data.get('headline', '')
        headline_keywords = cls._count_keywords(headline)
        headline_score = min(25, headline_keywords * 5)
        factors['headline_keywords'] = headline_score
        score += headline_score

        # Summary optimization (20 points)
        summary = profile_data.get('summary', '')
        summary_score = min(20, len(summary) // 100)
        if summary and len(summary) > 500:
            summary_score = 20
        factors['summary'] = summary_score
        score += summary_score

        # Skills count (20 points)
        skills = profile_data.get('skills', [])
        skills_score = min(20, len(skills) * 2)
        factors['skills'] = skills_score
        score += skills_score

        # Experience detail (20 points)
        experience = profile_data.get('experience', [])
        experience_score = min(20, len(experience) * 4)
        factors['experience'] = experience_score
        score += experience_score

        # Completeness (15 points)
        completeness = cls._calculate_completeness(profile_data)
        completeness_score = int(completeness * 0.15)
        factors['completeness'] = completeness_score
        score += completeness_score

        return {
            'visibility_score': score,
            'interpretation': cls._interpret_visibility(score),
            'factors': factors,
            'improvements': cls._get_visibility_improvements(factors),
        }

    # Private helper methods

    @classmethod
    def _analyze_headline(cls, headline: str) -> Dict:
        """Analyze headline quality."""
        if not headline:
            return {
                'score': 0,
                'recommendations': ['Add a professional headline'],
            }

        score = 50  # Base
        recommendations = []

        # Check length
        if len(headline) < 50:
            recommendations.append('Expand headline to use more of the 220 character limit')
        elif len(headline) > 150:
            score += 10

        # Check for keywords
        keyword_count = cls._count_keywords(headline)
        if keyword_count >= 2:
            score += 20
        else:
            recommendations.append('Add industry-relevant keywords to your headline')

        # Check for value proposition
        if any(word in headline.lower() for word in ['help', 'specialize', 'expert', 'leader']):
            score += 15
        else:
            recommendations.append('Include a value proposition in your headline')

        # Check for pipe separators (LinkedIn style)
        if '|' in headline or '•' in headline:
            score += 5

        return {
            'score': min(100, score),
            'recommendations': recommendations,
        }

    @classmethod
    def _analyze_summary(cls, summary: str) -> Dict:
        """Analyze summary/about section."""
        if not summary:
            return {
                'score': 0,
                'recommendations': ['Write a compelling About section'],
            }

        score = 40  # Base
        recommendations = []

        # Check length
        word_count = len(summary.split())
        if word_count < 50:
            recommendations.append('Expand your summary (aim for 200-300 words)')
        elif word_count >= 150:
            score += 20
        elif word_count >= 100:
            score += 10

        # Check for metrics/numbers
        if re.search(r'\d+', summary):
            score += 15
        else:
            recommendations.append('Add specific numbers and achievements')

        # Check for power words
        power_word_count = sum(1 for word in cls.POWER_WORDS if word in summary.lower())
        if power_word_count >= 3:
            score += 15
        else:
            recommendations.append('Use action verbs like achieved, built, led, grew')

        # Check for CTA
        if any(phrase in summary.lower() for phrase in ['reach out', 'connect', 'let\'s chat', 'contact']):
            score += 10
        else:
            recommendations.append('End with a call-to-action')

        return {
            'score': min(100, score),
            'recommendations': recommendations,
        }

    @classmethod
    def _analyze_experience(cls, experience: List[Dict]) -> Dict:
        """Analyze experience section."""
        if not experience:
            return {
                'score': 0,
                'recommendations': ['Add your work experience'],
            }

        score = 40  # Base for having experience
        recommendations = []

        # Check number of entries
        if len(experience) >= 3:
            score += 15
        elif len(experience) == 1:
            recommendations.append('Add more roles to show career progression')

        # Check descriptions
        has_descriptions = sum(1 for exp in experience if exp.get('description'))
        if has_descriptions == len(experience):
            score += 20
        elif has_descriptions < len(experience):
            recommendations.append('Add descriptions to all experience entries')

        # Check for metrics
        all_descriptions = ' '.join(exp.get('description', '') for exp in experience)
        if re.search(r'\d+%|\$\d+', all_descriptions):
            score += 15
        else:
            recommendations.append('Add quantified achievements (%, $, numbers)')

        # Check for bullets
        if '•' in all_descriptions or '-' in all_descriptions:
            score += 10
        else:
            recommendations.append('Use bullet points for readability')

        return {
            'score': min(100, score),
            'recommendations': recommendations,
        }

    @classmethod
    def _analyze_skills(cls, skills: List[str], target_role: str) -> Dict:
        """Analyze skills section."""
        if not skills:
            return {
                'score': 0,
                'recommendations': ['Add at least 10 relevant skills'],
            }

        score = 30  # Base
        recommendations = []

        # Check count
        if len(skills) >= 20:
            score += 30
        elif len(skills) >= 10:
            score += 20
        else:
            recommendations.append(f'Add more skills (you have {len(skills)}, aim for 15-20)')

        # Check for industry alignment
        # This would normally check against target role requirements
        score += 20

        # Check for endorsements (if data available)
        score += 20  # Placeholder

        return {
            'score': min(100, score),
            'recommendations': recommendations,
        }

    @classmethod
    def _calculate_completeness(cls, profile_data: Dict) -> int:
        """Calculate profile completeness percentage."""
        completed = 0

        if profile_data.get('headline'):
            completed += 1
        if profile_data.get('summary') and len(profile_data['summary']) > 100:
            completed += 1
        if profile_data.get('experience'):
            completed += 1
        if profile_data.get('education'):
            completed += 1
        if profile_data.get('skills') and len(profile_data['skills']) >= 5:
            completed += 1
        if profile_data.get('photo'):
            completed += 1
        if profile_data.get('location'):
            completed += 1
        if profile_data.get('industry'):
            completed += 1

        return int((completed / 8) * 100)

    @staticmethod
    def _count_keywords(text: str) -> int:
        """Count industry keywords in text."""
        text_lower = text.lower()
        count = 0
        all_keywords = set()
        for keywords in LinkedInService.INDUSTRY_KEYWORDS.values():
            all_keywords.update(keywords)

        for keyword in all_keywords:
            if keyword in text_lower:
                count += 1
        return count

    @staticmethod
    def _interpret_score(score: int) -> str:
        """Interpret profile score."""
        if score >= 80:
            return 'Excellent - Your profile is well-optimized'
        elif score >= 60:
            return 'Good - A few improvements could boost visibility'
        elif score >= 40:
            return 'Fair - Significant optimization opportunities'
        else:
            return 'Needs Work - Major improvements recommended'

    @staticmethod
    def _interpret_visibility(score: int) -> str:
        """Interpret visibility score."""
        if score >= 80:
            return 'High Visibility - You appear in many searches'
        elif score >= 60:
            return 'Moderate Visibility - Room for improvement'
        elif score >= 40:
            return 'Low Visibility - May miss relevant opportunities'
        else:
            return 'Very Low Visibility - Urgent optimization needed'

    @staticmethod
    def _get_value_statement(industry: str) -> str:
        """Get industry-specific value statement."""
        statements = {
            'technology': 'build innovative solutions that scale',
            'finance': 'optimize financial performance and manage risk',
            'marketing': 'drive growth through strategic campaigns',
            'healthcare': 'improve patient outcomes and operational efficiency',
            'sales': 'accelerate revenue and build lasting client relationships',
        }
        return statements.get(industry.lower(), 'achieve their strategic objectives')

    @staticmethod
    def _enhance_bullet(text: str) -> str:
        """Enhance a bullet point with action verb."""
        text = text.strip()
        # Check if already starts with action verb
        first_word = text.split()[0].lower() if text else ''
        if first_word in LinkedInService.POWER_WORDS:
            return text

        # Add a placeholder enhancement suggestion
        return f"[Consider starting with action verb] {text}"

    @staticmethod
    def _get_priority_actions(scores: Dict, completeness: int) -> List[Dict]:
        """Get prioritized action items."""
        actions = []

        if completeness < 80:
            actions.append({
                'action': 'Complete all profile sections',
                'priority': 'high',
                'impact': 'Incomplete profiles get 40% less views',
            })

        if scores.get('headline', 0) < 70:
            actions.append({
                'action': 'Optimize your headline',
                'priority': 'high',
                'impact': 'First thing recruiters see in search results',
            })

        if scores.get('summary', 0) < 60:
            actions.append({
                'action': 'Write a compelling About section',
                'priority': 'medium',
                'impact': 'Key for establishing credibility',
            })

        if scores.get('experience', 0) < 60:
            actions.append({
                'action': 'Add metrics to experience descriptions',
                'priority': 'medium',
                'impact': 'Quantified achievements get more attention',
            })

        return actions[:5]

    @staticmethod
    def _get_visibility_improvements(factors: Dict) -> List[str]:
        """Get visibility improvement suggestions."""
        improvements = []

        if factors.get('headline_keywords', 0) < 20:
            improvements.append('Add more searchable keywords to your headline')

        if factors.get('skills', 0) < 15:
            improvements.append('Add more relevant skills (aim for 20+)')

        if factors.get('summary', 0) < 15:
            improvements.append('Expand your About section with keywords')

        if factors.get('experience', 0) < 15:
            improvements.append('Detail your experience with industry terms')

        return improvements[:5]
