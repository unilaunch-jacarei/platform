"""create work sessions and gamification tables

Revision ID: 20261104_gamification
Revises: 61fcef0dc03b
"""

from typing import Sequence

import fastapi_users_db_sqlalchemy
import sqlalchemy as sa
from alembic import op

revision: str = "20261104_gamification"
down_revision: str | Sequence[str] | None = "61fcef0dc03b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    guid = fastapi_users_db_sqlalchemy.generics.GUID()
    op.create_table(
        "work_sessions",
        sa.Column("id", guid, nullable=False),
        sa.Column("user_id", guid, nullable=False),
        sa.Column("work_type", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("total_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "work_type IN ('back', 'front', 'fullstack', 'banco_de_dados', 'api')",
            name="ck_work_sessions_work_type",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'paused', 'completed', 'cancelled')",
            name="ck_work_sessions_status",
        ),
        sa.CheckConstraint("total_seconds >= 0", name="ck_work_sessions_total_seconds"),
        sa.ForeignKeyConstraint(["user_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_work_sessions_user_id", "work_sessions", ["user_id"])
    op.create_index("ix_work_sessions_work_type", "work_sessions", ["work_type"])
    op.create_index("ix_work_sessions_status", "work_sessions", ["status"])

    op.create_table(
        "work_session_intervals",
        sa.Column("id", guid, nullable=False),
        sa.Column("session_id", guid, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint(
            "duration_seconds >= 0",
            name="ck_work_session_intervals_duration_seconds",
        ),
        sa.ForeignKeyConstraint(["session_id"], ["work_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_work_session_intervals_session_id", "work_session_intervals", ["session_id"])

    op.create_table(
        "work_hour_entries",
        sa.Column("id", guid, nullable=False),
        sa.Column("user_id", guid, nullable=False),
        sa.Column("work_type", sa.String(length=30), nullable=False),
        sa.Column("seconds_delta", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_id", guid, nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "work_type IN ('back', 'front', 'fullstack', 'banco_de_dados', 'api')",
            name="ck_work_hour_entries_work_type",
        ),
        sa.CheckConstraint("seconds_delta <> 0", name="ck_work_hour_entries_seconds_delta"),
        sa.ForeignKeyConstraint(["user_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_type", "source_id", name="uq_work_hour_entries_source"),
    )
    op.create_index("ix_work_hour_entries_user_id", "work_hour_entries", ["user_id"])
    op.create_index("ix_work_hour_entries_work_type", "work_hour_entries", ["work_type"])

    op.create_table(
        "user_progress",
        sa.Column("user_id", guid, nullable=False),
        sa.Column("total_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "user_work_type_progress",
        sa.Column("id", guid, nullable=False),
        sa.Column("user_id", guid, nullable=False),
        sa.Column("work_type", sa.String(length=30), nullable=False),
        sa.Column("total_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "work_type IN ('back', 'front', 'fullstack', 'banco_de_dados', 'api')",
            name="ck_user_work_type_progress_work_type",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "work_type", name="uq_user_work_type_progress"),
    )
    op.create_index("ix_user_work_type_progress_user_id", "user_work_type_progress", ["user_id"])

    op.create_table(
        "user_achievements",
        sa.Column("id", guid, nullable=False),
        sa.Column("user_id", guid, nullable=False),
        sa.Column("achievement_code", sa.String(length=30), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("progress_snapshot_seconds", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "achievement_code", name="uq_user_achievements_user_code"),
    )
    op.create_index("ix_user_achievements_user_id", "user_achievements", ["user_id"])

    op.create_table(
        "work_hour_adjustments",
        sa.Column("id", guid, nullable=False),
        sa.Column("user_id", guid, nullable=False),
        sa.Column("admin_id", guid, nullable=False),
        sa.Column("work_type", sa.String(length=30), nullable=False),
        sa.Column("seconds_delta", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=1000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "work_type IN ('back', 'front', 'fullstack', 'banco_de_dados', 'api')",
            name="ck_work_hour_adjustments_work_type",
        ),
        sa.CheckConstraint(
            "seconds_delta <> 0",
            name="ck_work_hour_adjustments_seconds_delta",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["admin_id"], ["usuarios.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_work_hour_adjustments_user_id", "work_hour_adjustments", ["user_id"])
    op.create_index("ix_work_hour_adjustments_admin_id", "work_hour_adjustments", ["admin_id"])
    op.create_index("ix_work_hour_adjustments_work_type", "work_hour_adjustments", ["work_type"])


def downgrade() -> None:
    op.drop_table("work_hour_adjustments")
    op.drop_table("user_achievements")
    op.drop_index("ix_user_work_type_progress_user_id", table_name="user_work_type_progress")
    op.drop_table("user_work_type_progress")
    op.drop_table("user_progress")
    op.drop_index("ix_work_hour_entries_work_type", table_name="work_hour_entries")
    op.drop_index("ix_work_hour_entries_user_id", table_name="work_hour_entries")
    op.drop_table("work_hour_entries")
    op.drop_index("ix_work_session_intervals_session_id", table_name="work_session_intervals")
    op.drop_table("work_session_intervals")
    op.drop_index("ix_work_sessions_status", table_name="work_sessions")
    op.drop_index("ix_work_sessions_work_type", table_name="work_sessions")
    op.drop_index("ix_work_sessions_user_id", table_name="work_sessions")
    op.drop_table("work_sessions")
