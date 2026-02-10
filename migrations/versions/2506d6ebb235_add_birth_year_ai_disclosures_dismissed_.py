"""add birth_year ai_disclosures_dismissed cookie_consent

Revision ID: 2506d6ebb235
Revises: 003
Create Date: 2026-02-09 19:46:07.853671
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2506d6ebb235'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('search_status', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('location_preferences', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('birth_year', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ai_disclosures_dismissed', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('cookie_consent', sa.String(length=20), nullable=True))


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('cookie_consent')
        batch_op.drop_column('ai_disclosures_dismissed')
        batch_op.drop_column('birth_year')
        batch_op.drop_column('location_preferences')
        batch_op.drop_column('search_status')
