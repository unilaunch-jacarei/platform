-- The SQLx bookkeeping table is created in the public schema by default.
-- It must not be exposed through PostgREST without row-level security.
ALTER TABLE public._sqlx_migrations ENABLE ROW LEVEL SECURITY;
