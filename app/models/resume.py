"""
Resume Model

Handles resume storage, parsing results, and ATS scoring.
"""

import uuid
from datetime import datetime

from app.extensions import db
from app.models.user import GUID, JSONType


class Resume(db.Model):
    """
    Resume model for storing uploaded resumes and analysis results.

    ATS Scoring Categories (100 points total):
    - Compatibility (15%): File format, parsing success
    - Keywords (15%): Industry/role keyword density
    - Achievements (25%): Quantified accomplishments
    - Formatting (15%): Structure, readability
    - Progression (15%): Career advancement pattern
    - Completeness (10%): All sections present
    - Fit (5%): Match to target role
    """

    __tablename__ = "resumes"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), db.ForeignKey("users.id"), nullable=False, index=True)

    # File Information
    title = db.Column(db.String(255), nullable=True)  # Display title
    file_name = db.Column(db.String(255), nullable=True)  # Original filename
    file_type = db.Column(db.String(50), nullable=True)  # 'pdf', 'docx', 'txt'
    file_size = db.Column(db.Integer, nullable=True)  # bytes
    file_path = db.Column(db.String(500), nullable=True)  # Storage path

    # Parsed Content
    raw_text = db.Column(db.Text, nullable=True)
    parsed_sections = db.Column(JSONType(), default=dict)  # Structured sections

    # Extracted Data
    contact_info = db.Column(JSONType(), default=dict)
    work_experience = db.Column(JSONType(), default=list)
    education = db.Column(JSONType(), default=list)
    skills = db.Column(JSONType(), default=list)
    certifications = db.Column(JSONType(), default=list)
    summary = db.Column(db.Text, nullable=True)

    # ATS Scores (0-100 each)
    ats_total_score = db.Column(db.Integer, nullable=True)
    ats_compatibility_score = db.Column(db.Integer, nullable=True)  # 15%
    ats_keywords_score = db.Column(db.Integer, nullable=True)  # 15%
    ats_achievements_score = db.Column(db.Integer, nullable=True)  # 25%
    ats_formatting_score = db.Column(db.Integer, nullable=True)  # 15%
    ats_progression_score = db.Column(db.Integer, nullable=True)  # 15%
    ats_completeness_score = db.Column(db.Integer, nullable=True)  # 10%
    ats_fit_score = db.Column(db.Integer, nullable=True)  # 5%

    # ATS Analysis Details
    ats_recommendations = db.Column(JSONType(), default=list)
    missing_keywords = db.Column(JSONType(), default=list)
    weak_sections = db.Column(JSONType(), default=list)

    # Tailoring
    is_tailored = db.Column(db.Boolean, default=False)
    target_job_title = db.Column(db.String(255), nullable=True)
    target_company = db.Column(db.String(255), nullable=True)
    source_resume_id = db.Column(GUID(), db.ForeignKey("resumes.id"), nullable=True)

    # Status
    is_master = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    parse_status = db.Column(db.String(50), default="pending")

    # Timestamps
    analyzed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref=db.backref("resumes", lazy="dynamic"))
    tailored_versions = db.relationship(
        "Resume", backref=db.backref("source_resume", remote_side=[id])
    )

    def __repr__(self):
        return f"<Resume {self.id} - {self.title}>"

    @property
    def word_count(self) -> int:
        """Return the word count of the resume."""
        if not self.raw_text:
            return 0
        return len(self.raw_text.split())

    @property
    def ats_score_breakdown(self) -> dict:
        """Return ATS score breakdown with weights."""
        return {
            "total": self.ats_total_score,
            "components": {
                "compatibility": {
                    "score": self.ats_compatibility_score,
                    "weight": 15,
                },
                "keywords": {
                    "score": self.ats_keywords_score,
                    "weight": 15,
                },
                "achievements": {
                    "score": self.ats_achievements_score,
                    "weight": 25,
                },
                "formatting": {
                    "score": self.ats_formatting_score,
                    "weight": 15,
                },
                "progression": {
                    "score": self.ats_progression_score,
                    "weight": 15,
                },
                "completeness": {
                    "score": self.ats_completeness_score,
                    "weight": 10,
                },
                "fit": {
                    "score": self.ats_fit_score,
                    "weight": 5,
                },
            },
        }

    def to_dict(self, include_analysis: bool = False) -> dict:
        """Convert resume to dictionary representation."""
        data = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "word_count": self.word_count,
            "is_master": self.is_master,
            "is_tailored": self.is_tailored,
            "target_job_title": self.target_job_title,
            "parse_status": self.parse_status,
            "ats_total_score": self.ats_total_score,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_analysis:
            data.update(
                {
                    "ats_breakdown": self.ats_score_breakdown,
                    "recommendations": self.ats_recommendations,
                    "missing_keywords": self.missing_keywords,
                    "weak_sections": self.weak_sections,
                    "parsed_sections": self.parsed_sections,
                    "contact_info": self.contact_info,
                }
            )

        return data


class ResumeVersion(db.Model):
    """
    Resume version for tracking changes and tailored versions.

    Stores snapshots of resume content at different points in time.
    """

    __tablename__ = "resume_versions"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    resume_id = db.Column(GUID(), db.ForeignKey("resumes.id"), nullable=False, index=True)

    # Version Info
    version_number = db.Column(db.Integer, default=1)
    change_summary = db.Column(db.String(500), nullable=True)

    # Content Snapshot
    raw_text = db.Column(db.Text, nullable=True)
    parsed_sections = db.Column(JSONType(), default=dict)

    # Score Snapshot
    ats_score = db.Column(db.Integer, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    resume = db.relationship("Resume", backref=db.backref("versions", lazy="dynamic"))

    def __repr__(self):
        return f"<ResumeVersion {self.resume_id} v{self.version_number}>"

    def to_dict(self) -> dict:
        """Convert version to dictionary representation."""
        return {
            "id": str(self.id),
            "resume_id": str(self.resume_id),
            "version_number": self.version_number,
            "change_summary": self.change_summary,
            "ats_score": self.ats_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
