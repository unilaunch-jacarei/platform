# Database migrations

Run migrations from `backend/` with:

```bash
uv run alembic upgrade head
```

Generate a migration after changing ORM models with:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

The baseline represents the existing `usuarios` table. Existing databases that were created
with `Base.metadata.create_all()` must be marked with `uv run alembic stamp 0001_baseline` once;
new databases should use `uv run alembic upgrade head`.
