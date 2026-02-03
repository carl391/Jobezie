"""
Resume Service

Handles resume parsing, ATS scoring, and optimization.
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from werkzeug.datastructures import FileStorage

from app.extensions import db
from app.models.resume import Resume, ResumeVersion
from app.services.scoring.ats import calculate_ats_score


# Supported file types
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class ResumeService:
    """Service for resume management and ATS optimization."""

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed."""
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension from filename."""
        if '.' in filename:
            return filename.rsplit('.', 1)[1].lower()
        return ''

    @staticmethod
    def upload_resume(
        user_id: str,
        file: FileStorage,
        title: Optional[str] = None,
        is_master: bool = False,
    ) -> Tuple[Resume, Dict]:
        """
        Upload and process a new resume.

        Args:
            user_id: User's ID
            file: Uploaded file object
            title: Optional title for the resume
            is_master: Whether this is the master resume

        Returns:
            Tuple of (Resume object, processing result dict)
        """
        if not file or not file.filename:
            raise ValueError("No file provided")

        if not ResumeService.allowed_file(file.filename):
            raise ValueError(f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}")

        # Read file content
        file_content = file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise ValueError(f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB")

        file_type = ResumeService.get_file_extension(file.filename)

        # Parse resume text (simplified - in production would use a parsing library)
        resume_text = ResumeService._extract_text(file_content, file_type)

        # If setting as master, unset existing master
        if is_master:
            Resume.query.filter_by(
                user_id=user_id,
                is_master=True
            ).update({'is_master': False})

        # Create resume record
        resume = Resume(
            user_id=user_id,
            title=title or file.filename,
            file_name=file.filename,
            file_type=file_type,
            file_size=len(file_content),
            raw_text=resume_text,
            is_master=is_master,
        )

        # Parse sections
        parsed_sections = ResumeService._parse_sections(resume_text)
        resume.parsed_sections = parsed_sections

        # Extract contact info
        contact_info = ResumeService._extract_contact_info(resume_text)
        resume.contact_info = contact_info

        # Calculate initial ATS score
        ats_result = calculate_ats_score(
            resume_text=resume_text,
            parsed_sections=parsed_sections,
            file_type=file_type,
        )

        # Store scores
        resume.ats_total_score = ats_result['total_score']
        resume.ats_compatibility_score = ats_result['components']['compatibility']
        resume.ats_keywords_score = ats_result['components']['keywords']
        resume.ats_achievements_score = ats_result['components']['achievements']
        resume.ats_formatting_score = ats_result['components']['formatting']
        resume.ats_progression_score = ats_result['components']['progression']
        resume.ats_completeness_score = ats_result['components']['completeness']
        resume.ats_fit_score = ats_result['components']['fit']
        resume.ats_recommendations = ats_result['recommendations']
        resume.weak_sections = ats_result['weak_sections']

        db.session.add(resume)
        db.session.commit()

        return resume, ats_result

    @staticmethod
    def _extract_text(content: bytes, file_type: str) -> str:
        """
        Extract text from file content.

        Note: In production, this would use libraries like:
        - PyPDF2 or pdfplumber for PDFs
        - python-docx for DOCX files
        """
        if file_type == 'txt':
            return content.decode('utf-8', errors='ignore')

        # Placeholder for PDF/DOCX parsing
        # In production, integrate proper parsing libraries
        try:
            return content.decode('utf-8', errors='ignore')
        except Exception:
            return ""

    @staticmethod
    def _parse_sections(text: str) -> Dict:
        """
        Parse resume into sections.

        Identifies common resume sections like Experience, Education, Skills.
        """
        sections = {
            'contact': '',
            'summary': '',
            'experience': '',
            'education': '',
            'skills': '',
            'certifications': '',
            'other': '',
        }

        if not text:
            return sections

        # Common section headers
        section_patterns = {
            'summary': r'(?:summary|objective|profile|about\s*me)',
            'experience': r'(?:experience|employment|work\s*history|professional\s*experience)',
            'education': r'(?:education|academic|degrees?|qualifications)',
            'skills': r'(?:skills|expertise|competenc|technical\s*skills|core\s*competencies)',
            'certifications': r'(?:certifications?|licenses?|credentials)',
        }

        text_lower = text.lower()
        lines = text.split('\n')

        current_section = 'contact'  # First section is usually contact
        current_content = []

        for line in lines:
            line_lower = line.lower().strip()

            # Check if line is a section header
            found_section = None
            for section, pattern in section_patterns.items():
                if re.match(rf'^{pattern}\s*:?\s*$', line_lower) or \
                   re.match(rf'^[•\-\*]?\s*{pattern}\s*:?\s*$', line_lower):
                    found_section = section
                    break

            if found_section:
                # Save previous section
                sections[current_section] = '\n'.join(current_content).strip()
                current_section = found_section
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        sections[current_section] = '\n'.join(current_content).strip()

        return sections

    @staticmethod
    def _extract_contact_info(text: str) -> Dict:
        """Extract contact information from resume text."""
        contact = {
            'email': None,
            'phone': None,
            'linkedin': None,
            'location': None,
        }

        if not text:
            return contact

        # Email pattern
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            contact['email'] = email_match.group()

        # Phone pattern (various formats)
        phone_match = re.search(r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}', text)
        if phone_match:
            contact['phone'] = phone_match.group()

        # LinkedIn pattern
        linkedin_match = re.search(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
        if linkedin_match:
            contact['linkedin'] = linkedin_match.group()

        return contact

    @staticmethod
    def get_resume(resume_id: str, user_id: str) -> Optional[Resume]:
        """Get a resume by ID, verifying ownership."""
        return Resume.query.filter_by(
            id=resume_id,
            user_id=user_id,
            is_deleted=False
        ).first()

    @staticmethod
    def get_user_resumes(
        user_id: str,
        include_deleted: bool = False
    ) -> List[Resume]:
        """Get all resumes for a user."""
        query = Resume.query.filter_by(user_id=user_id)
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
        return query.order_by(Resume.created_at.desc()).all()

    @staticmethod
    def get_master_resume(user_id: str) -> Optional[Resume]:
        """Get user's master resume."""
        return Resume.query.filter_by(
            user_id=user_id,
            is_master=True,
            is_deleted=False
        ).first()

    @staticmethod
    def score_for_job(
        resume_id: str,
        user_id: str,
        job_keywords: List[str],
        target_role: Optional[str] = None,
    ) -> Dict:
        """
        Score a resume against a specific job posting.

        Args:
            resume_id: Resume ID
            user_id: User ID for verification
            job_keywords: Keywords from job description
            target_role: Target job title

        Returns:
            ATS score result with job-specific feedback
        """
        resume = ResumeService.get_resume(resume_id, user_id)
        if not resume:
            raise ValueError("Resume not found")

        result = calculate_ats_score(
            resume_text=resume.raw_text,
            parsed_sections=resume.parsed_sections,
            job_keywords=job_keywords,
            target_role=target_role,
            file_type=resume.file_type,
        )

        # Store job-specific keywords if missing
        if result['missing_keywords']:
            resume.missing_keywords = result['missing_keywords']
            db.session.commit()

        return result

    @staticmethod
    def create_tailored_version(
        resume_id: str,
        user_id: str,
        target_job_title: str,
        target_company: Optional[str] = None,
        optimized_text: str = None,
    ) -> Resume:
        """
        Create a tailored version of a resume for a specific job.

        Args:
            resume_id: Source resume ID
            user_id: User ID
            target_job_title: Job title this version targets
            target_company: Company name
            optimized_text: AI-optimized resume text

        Returns:
            New Resume object (tailored version)
        """
        source_resume = ResumeService.get_resume(resume_id, user_id)
        if not source_resume:
            raise ValueError("Source resume not found")

        # Create new resume as tailored version
        tailored = Resume(
            user_id=user_id,
            title=f"{source_resume.title} - {target_job_title}",
            file_name=source_resume.file_name,
            file_type=source_resume.file_type,
            file_size=source_resume.file_size,
            raw_text=optimized_text or source_resume.raw_text,
            parsed_sections=source_resume.parsed_sections,
            contact_info=source_resume.contact_info,
            is_master=False,
            is_tailored=True,
            target_job_title=target_job_title,
            target_company=target_company,
            source_resume_id=source_resume.id,
        )

        # Re-calculate ATS score for tailored version
        ats_result = calculate_ats_score(
            resume_text=tailored.raw_text,
            parsed_sections=tailored.parsed_sections,
            target_role=target_job_title,
            file_type=tailored.file_type,
        )

        tailored.ats_total_score = ats_result['total_score']
        tailored.ats_compatibility_score = ats_result['components']['compatibility']
        tailored.ats_keywords_score = ats_result['components']['keywords']
        tailored.ats_achievements_score = ats_result['components']['achievements']
        tailored.ats_formatting_score = ats_result['components']['formatting']
        tailored.ats_progression_score = ats_result['components']['progression']
        tailored.ats_completeness_score = ats_result['components']['completeness']
        tailored.ats_fit_score = ats_result['components']['fit']
        tailored.ats_recommendations = ats_result['recommendations']

        # Create version record
        version = ResumeVersion(
            resume=tailored,
            version_number=1,
            raw_text=tailored.raw_text,
            ats_score=tailored.ats_total_score,
            change_summary=f"Tailored for {target_job_title}" +
                          (f" at {target_company}" if target_company else ""),
        )

        db.session.add(tailored)
        db.session.add(version)
        db.session.commit()

        return tailored

    @staticmethod
    def set_master_resume(resume_id: str, user_id: str) -> Resume:
        """Set a resume as the master resume."""
        resume = ResumeService.get_resume(resume_id, user_id)
        if not resume:
            raise ValueError("Resume not found")

        # Unset existing master
        Resume.query.filter_by(
            user_id=user_id,
            is_master=True
        ).update({'is_master': False})

        resume.is_master = True
        db.session.commit()

        return resume

    @staticmethod
    def delete_resume(resume_id: str, user_id: str) -> bool:
        """Soft delete a resume."""
        resume = ResumeService.get_resume(resume_id, user_id)
        if not resume:
            raise ValueError("Resume not found")

        resume.is_deleted = True
        resume.deleted_at = datetime.utcnow()
        db.session.commit()

        return True

    @staticmethod
    def get_optimization_suggestions(resume_id: str, user_id: str) -> Dict:
        """
        Get detailed optimization suggestions for a resume.

        Returns prioritized suggestions based on ATS analysis.
        """
        resume = ResumeService.get_resume(resume_id, user_id)
        if not resume:
            raise ValueError("Resume not found")

        suggestions = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': [],
            'score_potential': 0,
        }

        # Analyze weak areas
        if resume.ats_achievements_score and resume.ats_achievements_score < 70:
            suggestions['high_priority'].append({
                'category': 'achievements',
                'current_score': resume.ats_achievements_score,
                'suggestion': 'Add more quantified achievements (numbers, percentages, dollar amounts)',
                'impact': 'high',
                'potential_gain': 25 - (resume.ats_achievements_score * 0.25),
            })

        if resume.ats_keywords_score and resume.ats_keywords_score < 70:
            suggestions['high_priority'].append({
                'category': 'keywords',
                'current_score': resume.ats_keywords_score,
                'suggestion': 'Add industry-specific keywords from target job descriptions',
                'missing': resume.missing_keywords[:5] if resume.missing_keywords else [],
                'impact': 'high',
                'potential_gain': 15 - (resume.ats_keywords_score * 0.15),
            })

        if resume.ats_formatting_score and resume.ats_formatting_score < 70:
            suggestions['medium_priority'].append({
                'category': 'formatting',
                'current_score': resume.ats_formatting_score,
                'suggestion': 'Use clear section headers and bullet points',
                'impact': 'medium',
                'potential_gain': 15 - (resume.ats_formatting_score * 0.15),
            })

        if resume.ats_completeness_score and resume.ats_completeness_score < 80:
            suggestions['medium_priority'].append({
                'category': 'completeness',
                'current_score': resume.ats_completeness_score,
                'suggestion': f"Add missing sections: {', '.join(resume.weak_sections or [])}",
                'impact': 'medium',
                'potential_gain': 10 - (resume.ats_completeness_score * 0.10),
            })

        if resume.ats_progression_score and resume.ats_progression_score < 70:
            suggestions['low_priority'].append({
                'category': 'progression',
                'current_score': resume.ats_progression_score,
                'suggestion': 'Highlight career progression and increasing responsibilities',
                'impact': 'low',
                'potential_gain': 15 - (resume.ats_progression_score * 0.15),
            })

        # Calculate total potential score gain
        for priority_level in ['high_priority', 'medium_priority', 'low_priority']:
            for item in suggestions[priority_level]:
                suggestions['score_potential'] += item.get('potential_gain', 0)

        suggestions['score_potential'] = round(suggestions['score_potential'], 1)

        return suggestions
