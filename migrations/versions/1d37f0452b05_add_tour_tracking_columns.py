"""add tour tracking columns

Revision ID: 1d37f0452b05
Revises: 001_initial
Create Date: 2026-02-05 04:22:06.915974
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d37f0452b05'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade():
    # Add tour tracking columns to users table
    op.add_column('users', sa.Column('tour_completed', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('completed_tours', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('users', 'completed_tours')
    op.drop_column('users', 'tour_completed')
