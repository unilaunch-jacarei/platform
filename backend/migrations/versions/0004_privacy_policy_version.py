"""Store the privacy policy version accepted by each lead.

Revision ID: 0004_privacy_policy_version
Revises: 0003_lead_constraints
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_privacy_policy_version"
down_revision: str | Sequence[str] | None = "0003_lead_constraints"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "leads",
        sa.Column(
            "privacy_policy_version",
            sa.String(length=50),
            server_default="v1",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("leads", "privacy_policy_version")
