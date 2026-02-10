"""
Labor Market Data Models

Models for O*NET occupation/skills data and BLS labor market statistics.
"""

from datetime import datetime

from app.extensions import db
from app.models.user import JSONType


class Occupation(db.Model):
    """
    O*NET occupation data.

    Contains occupation titles and metadata from O*NET database.
    """

    __tablename__ = "occupations"

    id = db.Column(db.String(20), primary_key=True)  # O*NET SOC code (e.g., "15-1252.00")
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    job_zone = db.Column(db.Integer)  # 1-5 education/training level
    bright_outlook = db.Column(db.Boolean, default=False)
    green = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    skills = db.relationship(
        "OccupationSkill", back_populates="occupation", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Occupation {self.id}: {self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "job_zone": self.job_zone,
            "bright_outlook": self.bright_outlook,
            "green": self.green,
        }


class Skill(db.Model):
    """
    O*NET skills taxonomy.

    Contains skills, abilities, knowledge, and other work-related competencies.
    """

    __tablename__ = "skills"

    id = db.Column(db.String(50), primary_key=True)  # O*NET element ID
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # skills, abilities, knowledge, etc.
    description = db.Column(db.Text)

    # Relationships
    occupations = db.relationship(
        "OccupationSkill", back_populates="skill", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Skill {self.id}: {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
        }


class OccupationSkill(db.Model):
    """
    Mapping between occupations and skills with importance/level scores.
    """

    __tablename__ = "occupation_skills"

    occupation_id = db.Column(
        db.String(20),
        db.ForeignKey("occupations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id = db.Column(
        db.String(50),
        db.ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    )
    importance = db.Column(db.Float)  # 0-100
    level = db.Column(db.Float)  # 0-100

    # Relationships
    occupation = db.relationship("Occupation", back_populates="skills")
    skill = db.relationship("Skill", back_populates="occupations")


class LaborMarketData(db.Model):
    """
    BLS labor market statistics.

    Contains data from JOLTS (job openings, hires, quits),
    OES (salary data), and OOH (10-year projections).
    """

    __tablename__ = "labor_market_data"

    id = db.Column(db.Integer, primary_key=True)
    occupation_code = db.Column(db.String(20), index=True)
    industry_code = db.Column(db.String(20), index=True)
    region = db.Column(db.String(50), default="national")
    source = db.Column(db.String(20))  # BLS_JOLTS, BLS_OES, BLS_OOH
    data_date = db.Column(db.Date, index=True)

    # JOLTS data
    openings = db.Column(db.Integer)  # Job openings (thousands)
    hires = db.Column(db.Integer)  # Hires (thousands)
    quits = db.Column(db.Integer)  # Voluntary quits (thousands)

    # Employment data
    employment = db.Column(db.Integer)  # Total employment

    # Salary data (OES)
    median_salary = db.Column(db.Integer)
    salary_10th_pct = db.Column(db.Integer)
    salary_90th_pct = db.Column(db.Integer)

    # Projections (OOH)
    projected_growth_10yr = db.Column(db.Float)  # Percentage

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<LaborMarketData {self.source} {self.data_date}>"

    def to_dict(self):
        return {
            "id": self.id,
            "occupation_code": self.occupation_code,
            "industry_code": self.industry_code,
            "region": self.region,
            "source": self.source,
            "data_date": self.data_date.isoformat() if self.data_date else None,
            "openings": self.openings,
            "hires": self.hires,
            "quits": self.quits,
            "employment": self.employment,
            "median_salary": self.median_salary,
            "projected_growth_10yr": self.projected_growth_10yr,
        }


class ShortageScore(db.Model):
    """
    Pre-calculated shortage scores for occupations.

    Caches shortage calculations for faster queries.
    """

    __tablename__ = "shortage_scores"

    id = db.Column(db.Integer, primary_key=True)
    occupation_code = db.Column(db.String(20), index=True)
    industry_code = db.Column(db.String(20), index=True)
    region = db.Column(db.String(50), default="national")
    shortage_score = db.Column(db.Integer)  # 0-100
    components = db.Column(JSONType)  # Breakdown by component
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ShortageScore {self.occupation_code}: {self.shortage_score}>"

    def to_dict(self):
        return {
            "occupation_code": self.occupation_code,
            "industry_code": self.industry_code,
            "region": self.region,
            "shortage_score": self.shortage_score,
            "components": self.components,
            "calculated_at": self.calculated_at.isoformat() if self.calculated_at else None,
        }
