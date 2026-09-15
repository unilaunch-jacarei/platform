"""Add lead domain constraints.

Revision ID: 0003_lead_constraints
Revises: 0002_leads
"""
from typing import Sequence

from alembic import op

revision: str = "0003_lead_constraints"
down_revision: str | Sequence[str] | None = "0002_leads"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("leads", recreate="always") as batch_op:
        batch_op.create_check_constraint(
            "ck_leads_company_size",
            "company_size IS NULL OR company_size IN "
            "('1-10', '11-50', '51-200', '201-500', '501+')",
        )
        batch_op.create_check_constraint(
            "ck_leads_status",
            "status IN ('new', 'contacted', 'qualified', 'converted', 'discarded')",
        )
        batch_op.create_check_constraint("ck_leads_privacy_consent", "privacy_consent = true")


def downgrade() -> None:
    with op.batch_alter_table("leads", recreate="always") as batch_op:
        batch_op.drop_constraint("ck_leads_privacy_consent", type_="check")
        batch_op.drop_constraint("ck_leads_status", type_="check")
        batch_op.drop_constraint("ck_leads_company_size", type_="check")
