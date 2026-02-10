"""Add admin infrastructure

Revision ID: 004
Revises: 2506d6ebb235
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "004"
down_revision = "2506d6ebb235"
branch_labels = None
depends_on = None


def upgrade():
    # Add is_admin column to users table
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean, nullable=False, server_default="false"),
    )

    # Create admin_audit_log table
    op.create_table(
        "admin_audit_log",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "admin_user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=True),
        sa.Column("target_id", sa.String(36), nullable=True),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Indexes
    op.create_index("ix_audit_admin_user", "admin_audit_log", ["admin_user_id"])
    op.create_index("ix_audit_action", "admin_audit_log", ["action"])
    op.create_index("ix_audit_created", "admin_audit_log", ["created_at"])
    op.create_index(
        "ix_users_is_admin", "users", ["is_admin"], postgresql_where=sa.text("is_admin = true")
    )


def downgrade():
    op.drop_index("ix_users_is_admin", table_name="users")
    op.drop_table("admin_audit_log")
    op.drop_column("users", "is_admin")
