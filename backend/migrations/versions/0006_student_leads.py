"""Add student leads.

Revision ID: 0006_student_leads
Revises: 0005_privacy_policy_v1_0
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_student_leads"
down_revision: str | Sequence[str] | None = "0005_privacy_policy_v1_0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

type_required_fields = (
    "(lead_type = 'company' AND company_name IS NOT NULL) OR "
    "(lead_type = 'student' AND institution_name IS NOT NULL AND course_name IS NOT NULL)"
)


def add_student_columns(batch_op) -> None:
    batch_op.add_column(
        sa.Column("lead_type", sa.String(length=20), server_default="company", nullable=False)
    )
    batch_op.add_column(sa.Column("institution_name", sa.String(length=255), nullable=True))
    batch_op.add_column(sa.Column("course_name", sa.String(length=255), nullable=True))
    batch_op.add_column(sa.Column("semester", sa.String(length=50), nullable=True))
    batch_op.add_column(sa.Column("linkedin_url", sa.String(length=2048), nullable=True))
    batch_op.add_column(sa.Column("github_url", sa.String(length=2048), nullable=True))
    batch_op.add_column(sa.Column("area_of_interest", sa.String(length=255), nullable=True))
    batch_op.alter_column("company_name", existing_type=sa.String(length=255), nullable=True)
    batch_op.create_check_constraint("ck_leads_type", "lead_type IN ('company', 'student')")
    batch_op.create_check_constraint("ck_leads_type_required_fields", type_required_fields)


def upgrade() -> None:
    recreate = "always" if op.get_context().dialect.name == "sqlite" else "auto"
    with op.batch_alter_table("leads", recreate=recreate) as batch_op:
        add_student_columns(batch_op)


def drop_student_columns(batch_op) -> None:
    batch_op.drop_constraint("ck_leads_type_required_fields", type_="check")
    batch_op.drop_constraint("ck_leads_type", type_="check")
    batch_op.alter_column("company_name", existing_type=sa.String(length=255), nullable=False)
    batch_op.drop_column("area_of_interest")
    batch_op.drop_column("github_url")
    batch_op.drop_column("linkedin_url")
    batch_op.drop_column("semester")
    batch_op.drop_column("course_name")
    batch_op.drop_column("institution_name")
    batch_op.drop_column("lead_type")


def downgrade() -> None:
    op.execute(
        sa.text("UPDATE leads SET company_name = institution_name WHERE lead_type = 'student'")
    )
    recreate = "always" if op.get_context().dialect.name == "sqlite" else "auto"
    with op.batch_alter_table("leads", recreate=recreate) as batch_op:
        drop_student_columns(batch_op)
