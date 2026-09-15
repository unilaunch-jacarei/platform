"""Create lead and page-view tables.

Revision ID: 0002_leads
Revises: 0001_baseline
"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op
from fastapi_users_db_sqlalchemy.generics import GUID

revision: str = "0002_leads"
down_revision: str | Sequence[str] | None = "0001_baseline"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "leads",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("job_title", sa.String(length=120), nullable=True),
        sa.Column("company_size", sa.String(length=20), nullable=True),
        sa.Column("website", sa.String(length=2048), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("privacy_consent", sa.Boolean(), nullable=False),
        sa.Column(
            "privacy_consent_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="new", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_leads_email", "leads", ["email"], unique=False)

    op.create_table(
        "lead_page_views",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("event_key", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_key"),
    )


def downgrade() -> None:
    op.drop_table("lead_page_views")
    op.drop_index("ix_leads_email", table_name="leads")
    op.drop_table("leads")
