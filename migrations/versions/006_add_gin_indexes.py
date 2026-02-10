"""Add GIN indexes on JSONB columns for fast containment queries

Revision ID: 006
Revises: 005
Create Date: 2026-02-09
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade():
    # GIN indexes enable fast @> containment queries on JSONB arrays.
    # Without these, PostgreSQL does a full table scan on every
    # skills-gap, user-match, and opportunity scoring query.
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_target_roles
            ON users USING GIN (target_roles jsonb_path_ops);
        CREATE INDEX IF NOT EXISTS idx_users_target_industries
            ON users USING GIN (target_industries jsonb_path_ops);
        CREATE INDEX IF NOT EXISTS idx_users_technical_skills
            ON users USING GIN (technical_skills jsonb_path_ops);
        CREATE INDEX IF NOT EXISTS idx_users_ai_disclosures
            ON users USING GIN (ai_disclosures_dismissed jsonb_path_ops);
    """)


def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_users_target_roles;")
    op.execute("DROP INDEX IF EXISTS idx_users_target_industries;")
    op.execute("DROP INDEX IF EXISTS idx_users_technical_skills;")
    op.execute("DROP INDEX IF EXISTS idx_users_ai_disclosures;")
