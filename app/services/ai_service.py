"""
AI Service

Handles AI-powered features using Claude API (primary) or OpenAI (fallback).
Provides message generation, resume optimization, and career coaching.
"""

import os
from typing import Dict, List, Optional

from flask import current_app


class AIService:
    """
    Service for AI-powered career assistance.

    Uses Claude API as primary provider, OpenAI as fallback.
    """

    SYSTEM_PROMPTS = {
        "message_generator": """You are an expert career coach helping job seekers write
highly effective recruiter outreach messages. You understand that:

1. Messages under 150 words get 22% higher response rates
2. Personalization with recruiter name increases open rates by 41%
3. Quantified achievements get 40% more interview callbacks
4. A single, clear call-to-action reduces decision paralysis

Write concise, professional messages that are warm but not overly casual.
Focus on the value the candidate brings, not just what they want.""",
        "resume_optimizer": """You are an expert resume writer and ATS optimization specialist.
You understand that:

1. ATS systems scan for keywords, clear formatting, and standard sections
2. Quantified achievements significantly increase interview callbacks
3. Strong action verbs (led, achieved, increased) make impact statements stand out
4. Resume length should be appropriate for experience level (1-2 pages max)

Provide specific, actionable suggestions for improving resume content and formatting.""",
        "career_coach": """You are an experienced career coach specializing in job search strategy.
You help users:

1. Identify their unique value proposition
2. Develop effective networking strategies
3. Prepare for interviews
4. Negotiate offers
5. Navigate career transitions

Provide personalized, actionable advice based on the user's specific situation.
Be encouraging but realistic about job market conditions.""",
        "interview_prep": """You are an expert interview coach who has helped thousands
of candidates succeed. You understand:

1. Behavioral interview techniques (STAR method)
2. Technical interview patterns for various industries
3. Common questions and effective answer structures
4. Body language and presentation tips

Help candidates prepare confident, structured responses that highlight their strengths.""",
    }

    MODEL_CONFIG = {
        "claude": {
            "default_model": "claude-sonnet-4-20250514",
            "max_tokens": 1024,
            "temperature": 0.7,
        },
        "openai": {
            "default_model": "gpt-4-turbo-preview",
            "max_tokens": 1024,
            "temperature": 0.7,
        },
    }

    @staticmethod
    def get_provider() -> str:
        """Determine which AI provider to use based on configuration."""
        if os.getenv("ANTHROPIC_API_KEY"):
            return "claude"
        elif os.getenv("OPENAI_API_KEY"):
            return "openai"
        return "none"

    @staticmethod
    async def generate_message(
        context: Dict,
        message_type: str = "initial_outreach",
        provider: Optional[str] = None,
    ) -> Dict:
        """
        Generate an outreach message using AI.

        Args:
            context: Generation context from MessageService.get_generation_context()
            message_type: Type of message to generate
            provider: Force specific provider (claude/openai)

        Returns:
            Dictionary with generated message and metadata
        """
        provider = provider or AIService.get_provider()

        if provider == "none":
            return {
                "success": False,
                "error": "No AI provider configured",
                "message": None,
            }

        # Build prompt from context
        prompt = AIService._build_message_prompt(context, message_type)

        try:
            if provider == "claude":
                response = await AIService._call_claude(
                    system_prompt=AIService.SYSTEM_PROMPTS["message_generator"],
                    user_prompt=prompt,
                )
            else:
                response = await AIService._call_openai(
                    system_prompt=AIService.SYSTEM_PROMPTS["message_generator"],
                    user_prompt=prompt,
                )

            return {
                "success": True,
                "message": response["content"],
                "provider": provider,
                "model": response["model"],
                "tokens_used": response.get("tokens_used"),
            }

        except Exception as e:
            current_app.logger.error(f"AI message generation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": None,
            }

    @staticmethod
    async def optimize_resume(
        resume_text: str,
        target_role: Optional[str] = None,
        job_keywords: Optional[List[str]] = None,
        weak_sections: Optional[List[str]] = None,
        provider: Optional[str] = None,
    ) -> Dict:
        """
        Get AI suggestions for resume optimization.

        Args:
            resume_text: Current resume content
            target_role: Target job title
            job_keywords: Keywords to incorporate
            weak_sections: Sections needing improvement
            provider: Force specific provider

        Returns:
            Dictionary with optimization suggestions
        """
        provider = provider or AIService.get_provider()

        if provider == "none":
            return {
                "success": False,
                "error": "No AI provider configured",
                "suggestions": None,
            }

        prompt = AIService._build_resume_prompt(
            resume_text, target_role, job_keywords, weak_sections
        )

        try:
            if provider == "claude":
                response = await AIService._call_claude(
                    system_prompt=AIService.SYSTEM_PROMPTS["resume_optimizer"],
                    user_prompt=prompt,
                )
            else:
                response = await AIService._call_openai(
                    system_prompt=AIService.SYSTEM_PROMPTS["resume_optimizer"],
                    user_prompt=prompt,
                )

            return {
                "success": True,
                "suggestions": response["content"],
                "provider": provider,
                "model": response["model"],
            }

        except Exception as e:
            current_app.logger.error(f"AI resume optimization error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "suggestions": None,
            }

    @staticmethod
    async def career_coaching(
        question: str,
        user_context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None,
        algorithm_context: Optional[Dict] = None,
        provider: Optional[str] = None,
    ) -> Dict:
        """
        Get AI career coaching response with algorithm-first context.

        This implements the algorithm-first principle: algorithmic scores are
        calculated first, then passed to AI for contextual, personalized advice.

        Args:
            question: User's question
            user_context: User profile information
            conversation_history: Previous messages in conversation
            algorithm_context: Pre-computed algorithmic scores (ATS, readiness, etc.)
            provider: Force specific provider

        Returns:
            Dictionary with coaching response
        """
        provider = provider or AIService.get_provider()

        if provider == "none":
            return {
                "success": False,
                "error": "No AI provider configured",
                "response": None,
            }

        prompt = AIService._build_coaching_prompt(question, user_context, algorithm_context)

        try:
            if provider == "claude":
                response = await AIService._call_claude(
                    system_prompt=AIService.SYSTEM_PROMPTS["career_coach"],
                    user_prompt=prompt,
                    conversation_history=conversation_history,
                )
            else:
                response = await AIService._call_openai(
                    system_prompt=AIService.SYSTEM_PROMPTS["career_coach"],
                    user_prompt=prompt,
                    conversation_history=conversation_history,
                )

            return {
                "success": True,
                "response": response["content"],
                "provider": provider,
                "model": response["model"],
            }

        except Exception as e:
            current_app.logger.error(f"AI career coaching error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": None,
            }

    @staticmethod
    async def interview_prep(
        job_title: str,
        company: Optional[str] = None,
        interview_type: str = "behavioral",
        user_experience: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> Dict:
        """
        Generate interview preparation materials.

        Args:
            job_title: Role being interviewed for
            company: Company name (for research)
            interview_type: Type of interview (behavioral, technical, case)
            user_experience: User's background for tailoring
            provider: Force specific provider

        Returns:
            Dictionary with prep materials and practice questions
        """
        provider = provider or AIService.get_provider()

        if provider == "none":
            return {
                "success": False,
                "error": "No AI provider configured",
                "prep_materials": None,
            }

        prompt = AIService._build_interview_prompt(
            job_title, company, interview_type, user_experience
        )

        try:
            if provider == "claude":
                response = await AIService._call_claude(
                    system_prompt=AIService.SYSTEM_PROMPTS["interview_prep"],
                    user_prompt=prompt,
                    max_tokens=2048,  # Longer for interview prep
                )
            else:
                response = await AIService._call_openai(
                    system_prompt=AIService.SYSTEM_PROMPTS["interview_prep"],
                    user_prompt=prompt,
                    max_tokens=2048,
                )

            return {
                "success": True,
                "prep_materials": response["content"],
                "provider": provider,
                "model": response["model"],
            }

        except Exception as e:
            current_app.logger.error(f"AI interview prep error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "prep_materials": None,
            }

    # Private helper methods

    @staticmethod
    def _build_message_prompt(context: Dict, message_type: str) -> str:
        """Build prompt for message generation."""
        template = context.get("template", {})
        user = context.get("user", {})
        recruiter = context.get("recruiter", {})
        achievements = context.get("achievements", [])

        prompt = f"""Generate a {message_type.replace('_', ' ')} message for a recruiter.

RECRUITER INFORMATION:
- Name: {recruiter.get('first_name', 'the recruiter')} {recruiter.get('last_name', '')}
- Company: {recruiter.get('company', 'their company')}
- Title: {recruiter.get('title', '')}
- Specialty: {recruiter.get('specialty', '')}

USER INFORMATION:
- Name: {user.get('first_name', '')} {user.get('last_name', '')}
- Current Title: {user.get('title', '')}
- Target Roles: {', '.join(user.get('target_roles', []))}

KEY ACHIEVEMENTS TO HIGHLIGHT:
{chr(10).join(f'- {a}' for a in achievements[:3]) if achievements else '- [User should add quantified achievements]'}

MESSAGE STRUCTURE:
{chr(10).join(f'{i+1}. {s}' for i, s in enumerate(template.get('structure', [])))}

CONSTRAINTS:
- Word limit: {template.get('word_limit', 150)} words
- Tone: {template.get('tone', 'professional but warm')}
- Must include recruiter's name
- Must have single clear call-to-action
- Use specific achievements with numbers when possible

Generate the message now:"""

        return prompt

    @staticmethod
    def _build_resume_prompt(
        resume_text: str,
        target_role: Optional[str],
        job_keywords: Optional[List[str]],
        weak_sections: Optional[List[str]],
    ) -> str:
        """Build prompt for resume optimization."""
        prompt = f"""Analyze this resume and provide specific optimization suggestions.

RESUME CONTENT:
{resume_text[:4000]}  # Truncate if too long

TARGET ROLE: {target_role or 'Not specified'}

KEYWORDS TO INCORPORATE: {', '.join(job_keywords[:10]) if job_keywords else 'Not specified'}

WEAK SECTIONS IDENTIFIED: {', '.join(weak_sections) if weak_sections else 'None identified'}

Please provide:
1. 3-5 specific improvements for the experience section (with rewritten examples)
2. Missing keywords that should be added naturally
3. Formatting suggestions for better ATS compatibility
4. Any sections that should be added or expanded

Focus on quantified achievements and strong action verbs."""

        return prompt

    @staticmethod
    def _build_coaching_prompt(
        question: str,
        user_context: Optional[Dict],
        algorithm_context: Optional[Dict] = None,
    ) -> str:
        """
        Build prompt for career coaching with algorithm-first context.

        The algorithm context provides pre-computed scores that the AI should
        reference when giving advice. This ensures advice is data-driven.
        """
        context_str = ""
        if user_context:
            context_str = f"""
USER PROFILE:
- Current Role: {user_context.get('current_role', 'Not specified')}
- Target Roles: {', '.join(user_context.get('target_roles', []))}
- Industries: {', '.join(user_context.get('industries', []))}
- Experience Level: {user_context.get('experience_level', 'Not specified')}
- Location: {user_context.get('location', 'Not specified')}
"""

        # Add algorithm-computed context (algorithm-first principle)
        algo_str = ""
        if algorithm_context:
            algo_str = "\nALGORITHM-COMPUTED METRICS (use these to inform your advice):"

            if algorithm_context.get("ats_score"):
                ats = algorithm_context["ats_score"]
                algo_str += f"""
- Resume ATS Score: {ats.get('total', 'N/A')}/100
  Weak sections: {', '.join(ats.get('weak_sections', [])) or 'None identified'}"""

            if algorithm_context.get("readiness_score"):
                readiness = algorithm_context["readiness_score"]
                algo_str += f"""
- Career Readiness Score: {readiness.get('total', 'N/A')}/100"""
                if readiness.get("components"):
                    comps = readiness["components"]
                    algo_str += f"""
  Components: Profile {comps.get('profile', 'N/A')}%, Resume {comps.get('resume', 'N/A')}%, Network {comps.get('network', 'N/A')}%, Activity {comps.get('activity', 'N/A')}%"""

            if algorithm_context.get("engagement_avg"):
                eng = algorithm_context["engagement_avg"]
                algo_str += f"""
- Recruiter Engagement: {eng.get('average', 'N/A')}/100 avg across {eng.get('count', 0)} recruiters ({eng.get('active', 0)} active)"""

            if algorithm_context.get("market_shortage"):
                shortages = algorithm_context["market_shortage"]
                if shortages:
                    algo_str += "\n- Market Shortage Scores:"
                    for s in shortages:
                        algo_str += f"\n  {s['role']}: {s['score']}/100 ({s['interpretation']})"

        prompt = f"""Please provide career coaching advice for the following question:
{context_str}{algo_str}

USER QUESTION:
{question}

Provide specific, actionable advice. Reference the algorithm-computed metrics above
when relevant to give data-driven recommendations. If relevant, include:
- Step-by-step recommendations based on their current scores
- Specific areas to improve based on weak sections identified
- Resources or tools they might find helpful
- Common pitfalls to avoid
- Timeline expectations where applicable"""

        return prompt

    @staticmethod
    def _build_interview_prompt(
        job_title: str,
        company: Optional[str],
        interview_type: str,
        user_experience: Optional[str],
    ) -> str:
        """Build prompt for interview preparation."""
        prompt = f"""Create interview preparation materials for:

POSITION: {job_title}
COMPANY: {company or 'Not specified'}
INTERVIEW TYPE: {interview_type}
CANDIDATE BACKGROUND: {user_experience or 'General background'}

Please provide:

1. TOP 5 LIKELY QUESTIONS
For each question, provide:
- The question
- Why interviewers ask this
- A strong answer framework
- Key points to include

2. COMPANY/ROLE RESEARCH POINTS
- Key areas to research before the interview
- Relevant industry trends

3. QUESTIONS TO ASK THE INTERVIEWER
- 3-5 thoughtful questions to demonstrate engagement

4. PREPARATION CHECKLIST
- What to do 1 day before
- What to do morning of
- What to bring"""

        return prompt

    @staticmethod
    async def _call_claude(
        system_prompt: str,
        user_prompt: str,
        conversation_history: Optional[List[Dict]] = None,
        max_tokens: int = 1024,
    ) -> Dict:
        """
        Call Claude API.

        Note: In production, use the actual Anthropic SDK.
        This is a placeholder implementation.
        """
        import anthropic

        client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )

        messages = []

        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                messages.append(
                    {
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", ""),
                    }
                )

        messages.append(
            {
                "role": "user",
                "content": user_prompt,
            }
        )

        config = AIService.MODEL_CONFIG["claude"]

        response = client.messages.create(
            model=config["default_model"],
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
        )

        return {
            "content": response.content[0].text,
            "model": config["default_model"],
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
        }

    @staticmethod
    async def _call_openai(
        system_prompt: str,
        user_prompt: str,
        conversation_history: Optional[List[Dict]] = None,
        max_tokens: int = 1024,
    ) -> Dict:
        """
        Call OpenAI API.

        Note: In production, use the actual OpenAI SDK.
        This is a placeholder implementation.
        """
        from openai import OpenAI

        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                messages.append(
                    {
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", ""),
                    }
                )

        messages.append(
            {
                "role": "user",
                "content": user_prompt,
            }
        )

        config = AIService.MODEL_CONFIG["openai"]

        response = client.chat.completions.create(
            model=config["default_model"],
            messages=messages,
            max_tokens=max_tokens,
            temperature=config["temperature"],
        )

        return {
            "content": response.choices[0].message.content,
            "model": config["default_model"],
            "tokens_used": response.usage.total_tokens,
        }


# Synchronous wrappers for use in Flask routes
def generate_message_sync(*args, **kwargs):
    """Synchronous wrapper for generate_message."""
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(AIService.generate_message(*args, **kwargs))
    finally:
        loop.close()


def optimize_resume_sync(*args, **kwargs):
    """Synchronous wrapper for optimize_resume."""
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(AIService.optimize_resume(*args, **kwargs))
    finally:
        loop.close()


def career_coaching_sync(*args, **kwargs):
    """Synchronous wrapper for career_coaching."""
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(AIService.career_coaching(*args, **kwargs))
    finally:
        loop.close()


def interview_prep_sync(*args, **kwargs):
    """Synchronous wrapper for interview_prep."""
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(AIService.interview_prep(*args, **kwargs))
    finally:
        loop.close()
