"""Add account deletion and data export support

Revision ID: 005
Revises: 004
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Soft-delete support on users table
    op.add_column(
        "users",
        sa.Column("deletion_requested_at", sa.DateTime, nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("deletion_scheduled_for", sa.DateTime, nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="false"),
    )

    # Index for finding accounts pending hard-delete
    op.create_index(
        "idx_users_pending_deletion",
        "users",
        ["deletion_scheduled_for"],
        postgresql_where=sa.text(
            "deletion_requested_at IS NOT NULL AND is_deleted = false"
        ),
    )

    # 2. Data export requests tracking
    op.create_table(
        "data_export_requests",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("file_path", sa.Text, nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger, nullable=True),
        sa.Column("download_token", sa.String(64), unique=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
    )

    op.create_index("idx_export_user", "data_export_requests", ["user_id"])
    op.create_index("idx_export_token", "data_export_requests", ["download_token"])
    op.create_index("idx_export_status", "data_export_requests", ["status"])


def downgrade():
    op.drop_table("data_export_requests")
    op.drop_index("idx_users_pending_deletion", table_name="users")
    op.drop_column("users", "is_deleted")
    op.drop_column("users", "deletion_scheduled_for")
    op.drop_column("users", "deletion_requested_at")
