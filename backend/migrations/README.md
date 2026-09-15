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
