"""Add labor market data tables

Revision ID: 002_add_labor_market
Revises: 1d37f0452b05
Create Date: 2026-02-05

Creates tables for:
- occupations (O*NET occupation data)
- skills (O*NET skills taxonomy)
- occupation_skills (occupation-skill mappings)
- labor_market_data (BLS JOLTS, OES, OOH data)
- shortage_scores (pre-calculated shortage scores)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '002_add_labor_market'
down_revision = '1d37f0452b05'
branch_labels = None
depends_on = None


def upgrade():
    # Occupations from O*NET
    op.create_table('occupations',
        sa.Column('id', sa.String(20), primary_key=True),  # O*NET SOC code
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('job_zone', sa.Integer),  # 1-5 education level
        sa.Column('bright_outlook', sa.Boolean, default=False),
        sa.Column('green', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Skills from O*NET
    op.create_table('skills',
        sa.Column('id', sa.String(50), primary_key=True),  # O*NET element ID
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('category', sa.String(50)),  # abilities, knowledge, skills, etc.
        sa.Column('description', sa.Text),
    )

    # Occupation-Skill mappings
    op.create_table('occupation_skills',
        sa.Column('occupation_id', sa.String(20), sa.ForeignKey('occupations.id', ondelete='CASCADE')),
        sa.Column('skill_id', sa.String(50), sa.ForeignKey('skills.id', ondelete='CASCADE')),
        sa.Column('importance', sa.Float),  # 0-100
        sa.Column('level', sa.Float),  # 0-100
        sa.PrimaryKeyConstraint('occupation_id', 'skill_id'),
    )

    # Labor market data from BLS
    op.create_table('labor_market_data',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('occupation_code', sa.String(20)),
        sa.Column('industry_code', sa.String(20)),
        sa.Column('region', sa.String(50), default='national'),
        sa.Column('source', sa.String(20)),  # BLS_JOLTS, BLS_OES, BLS_OOH
        sa.Column('data_date', sa.Date),
        sa.Column('openings', sa.Integer),
        sa.Column('hires', sa.Integer),
        sa.Column('quits', sa.Integer),
        sa.Column('employment', sa.Integer),
        sa.Column('median_salary', sa.Integer),
        sa.Column('salary_10th_pct', sa.Integer),
        sa.Column('salary_90th_pct', sa.Integer),
        sa.Column('projected_growth_10yr', sa.Float),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_labor_market_occupation', 'labor_market_data', ['occupation_code'])
    op.create_index('ix_labor_market_industry', 'labor_market_data', ['industry_code'])
    op.create_index('ix_labor_market_date', 'labor_market_data', ['data_date'])

    # Pre-calculated shortage scores
    op.create_table('shortage_scores',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('occupation_code', sa.String(20)),
        sa.Column('industry_code', sa.String(20)),
        sa.Column('region', sa.String(50), default='national'),
        sa.Column('shortage_score', sa.Integer),  # 0-100
        sa.Column('components', JSONB),
        sa.Column('calculated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_shortage_occupation', 'shortage_scores', ['occupation_code'])
    op.create_index('ix_shortage_industry', 'shortage_scores', ['industry_code'])


def downgrade():
    op.drop_table('shortage_scores')
    op.drop_table('labor_market_data')
    op.drop_table('occupation_skills')
    op.drop_table('skills')
    op.drop_table('occupations')
