"""preserve task audit logs on task deletion

Revision ID: 0009_preserve_task_audit_logs
Revises: 61fcef0dc03b
Create Date: 2026-11-13 09:20:00.000000

Os logs de auditoria passam a sobreviver à exclusão da tarefa: a coluna
``task_id`` vira opcional com ``ON DELETE SET NULL`` e um snapshot de
``task_title`` é mantido para preservar o contexto.

A alteração de foreign key é aplicada apenas em dialectos que a suportam
(PostgreSQL, alvo de deploy). Em SQLite o schema é criado via
``Base.metadata.create_all``; ainda assim o downgrade/upgrade mantém a coluna
opcional para não quebrar ambientes locais.
"""

from typing import Sequence

import fastapi_users_db_sqlalchemy.generics
import sqlalchemy as sa
from alembic import op

revision: str = "0009_preserve_task_audit_logs"
down_revision: str | Sequence[str] | None = "61fcef0dc03b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "task_audit_logs",
        sa.Column("task_title", sa.String(length=255), nullable=True),
    )
    op.execute(
        "UPDATE task_audit_logs SET task_title = ("
        "SELECT tasks.title FROM tasks WHERE tasks.id = task_audit_logs.task_id"
        ") WHERE task_id IS NOT NULL"
    )

    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("task_audit_logs") as batch_op:
            batch_op.alter_column(
                "task_id",
                existing_type=fastapi_users_db_sqlalchemy.generics.GUID(),
                nullable=True,
            )
        return

    op.alter_column(
        "task_audit_logs",
        "task_id",
        existing_type=fastapi_users_db_sqlalchemy.generics.GUID(),
        nullable=True,
    )
    op.drop_constraint("task_audit_logs_task_id_fkey", "task_audit_logs", type_="foreignkey")
    op.create_foreign_key(
        "fk_task_audit_logs_task_id_tasks",
        "task_audit_logs",
        "tasks",
        ["task_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        op.drop_constraint(
            "fk_task_audit_logs_task_id_tasks", "task_audit_logs", type_="foreignkey"
        )
        op.create_foreign_key(
            "task_audit_logs_task_id_fkey",
            "task_audit_logs",
            "tasks",
            ["task_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # O downgrade não consegue reatar logs cujas tarefas já foram removidas.
    # Para restaurar o NOT NULL, removemos esses registros órfãos (lossy).
    op.execute("DELETE FROM task_audit_logs WHERE task_id IS NULL")

    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("task_audit_logs") as batch_op:
            batch_op.alter_column(
                "task_id",
                existing_type=fastapi_users_db_sqlalchemy.generics.GUID(),
                nullable=False,
            )
    else:
        op.alter_column(
            "task_audit_logs",
            "task_id",
            existing_type=fastapi_users_db_sqlalchemy.generics.GUID(),
            nullable=False,
        )

    op.drop_column("task_audit_logs", "task_title")
