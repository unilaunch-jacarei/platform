# Database migrations

Run migrations from `backend/` with:

```bash
uv run alembic upgrade head
```

Generate a migration after changing ORM models with:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

The baseline represents the existing `usuarios` table. Choose the one-time adoption command
from the actual schema before deploying an image that runs migrations:

- Empty database: run `uv run alembic upgrade head`.
- Database with only `usuarios`: run `uv run alembic stamp 0001_baseline`, then upgrade.
- Database with `usuarios`, `leads`, and `lead_page_views`, but without lead constraints or
  `privacy_policy_version`: stamp `0002_leads`, then upgrade.
- Database already matching the current ORM metadata: verify the schema and stamp `head`.

Never stamp a revision without first checking which tables, columns, and constraints already
exist. Deployments run migrations as a one-shot service before starting application replicas.

## Student lead normalization

Revision `0007_normalize_student_leads` is additive: it creates academic catalogs, adds nullable
foreign keys to `leads`, seeds approved options and backfills existing student leads. It does not
remove the legacy text columns from revision `0006_student_leads`.

The migration creates indexes and recreates `leads` when run on SQLite. PostgreSQL acquires short
DDL locks while adding columns, constraints and indexes. Before production rollout, inspect the
row count and active transactions; use a low-traffic window if the migration cannot complete
within the deployment job's deadline.

After all old backend pods have stopped, run `reconcile-student-leads` once to normalize records
written during the rolling update. The command is idempotent and can be run again safely.

The complete rollout, audit and rollback procedure is documented in
[`docs/STUDENT_LEAD_NORMALIZATION.md`](../../docs/STUDENT_LEAD_NORMALIZATION.md).
