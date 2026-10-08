"""Use privacy policy v1.0 for new leads.

Revision ID: 0005_privacy_policy_v1_0
Revises: 0004_privacy_policy_version
Create Date: 2026-09-15
"""

from alembic import op

revision = "0005_privacy_policy_v1_0"
down_revision = "0004_privacy_policy_version"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if op.get_context().dialect.name == "sqlite":
        with op.batch_alter_table("leads", recreate="always") as batch_op:
            batch_op.alter_column("privacy_policy_version", server_default="v1.0")
    else:
        op.alter_column("leads", "privacy_policy_version", server_default="v1.0")


def downgrade() -> None:
    if op.get_context().dialect.name == "sqlite":
        with op.batch_alter_table("leads", recreate="always") as batch_op:
            batch_op.alter_column("privacy_policy_version", server_default="v1")
    else:
        op.alter_column("leads", "privacy_policy_version", server_default="v1")
