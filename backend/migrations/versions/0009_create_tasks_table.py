"""create tasks table

Revision ID: 0009_create_tasks_table
Revises: 0008_create_boards_table
Create Date: 2026-10-11 12:00:00.000000
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from fastapi_users_db_sqlalchemy.generics import GUID

revision: str = "0009_create_tasks_table"
down_revision: str | Sequence[str] | None = "0008_create_boards_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_tasks",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("user_id", GUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_tasks_user_id"), "user_tasks", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_tasks_user_id"), table_name="user_tasks")
    op.drop_table("user_tasks")
