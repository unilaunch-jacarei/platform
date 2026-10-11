"""merge board members and leads migrations

Revision ID: 90946901eb13
Revises: 93e5ba010a2a
Create Date: 2026-10-11 20:38:22.045963
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



revision: str = '90946901eb13'
down_revision: Union[str, Sequence[str], None] = '93e5ba010a2a'
branch_labels: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
