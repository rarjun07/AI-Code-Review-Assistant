"""Create the initial application schema.

Revision ID: 20260719_0001
Revises:
Create Date: 2026-07-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260719_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"], unique=False)

    op.create_table(
        "uploaded_files",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("filepath", sa.String(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(), nullable=True),
        sa.Column("uploaded_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_uploaded_files_id",
        "uploaded_files",
        ["id"],
        unique=False,
    )

    op.create_table(
        "analysis_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("pylint_report", sa.JSON(), nullable=False),
        sa.Column("bandit_report", sa.JSON(), nullable=False),
        sa.Column("radon_report", sa.JSON(), nullable=False),
        sa.Column("ai_review", sa.JSON(), nullable=True),
        sa.Column("documentation_report", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("upload_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["upload_id"], ["uploaded_files.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_analysis_reports_id",
        "analysis_reports",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_analysis_reports_id", table_name="analysis_reports")
    op.drop_table("analysis_reports")
    op.drop_index("ix_uploaded_files_id", table_name="uploaded_files")
    op.drop_table("uploaded_files")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
