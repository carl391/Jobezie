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
    # The initial migration created these columns as TEXT, but they store JSON
    # and the JSONType TypeDecorator uses JSONB on PostgreSQL at runtime.
    # Convert TEXT -> JSONB first so GIN indexes can use jsonb_path_ops.
    op.execute("""
        ALTER TABLE users
            ALTER COLUMN target_roles TYPE JSONB USING COALESCE(target_roles, '[]')::jsonb,
            ALTER COLUMN target_industries TYPE JSONB USING COALESCE(target_industries, '[]')::jsonb,
            ALTER COLUMN technical_skills TYPE JSONB USING COALESCE(technical_skills, '[]')::jsonb,
            ALTER COLUMN ai_disclosures_dismissed TYPE JSONB USING COALESCE(ai_disclosures_dismissed, '[]')::jsonb;
    """)

    # GIN indexes enable fast @> containment queries on JSONB arrays.
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

    op.execute("""
        ALTER TABLE users
            ALTER COLUMN target_roles TYPE TEXT USING target_roles::text,
            ALTER COLUMN target_industries TYPE TEXT USING target_industries::text,
            ALTER COLUMN technical_skills TYPE TEXT USING technical_skills::text,
            ALTER COLUMN ai_disclosures_dismissed TYPE TEXT USING ai_disclosures_dismissed::text;
    """)
