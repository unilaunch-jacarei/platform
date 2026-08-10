-- Compatibilidade para bancos que já executaram a migration 0001 anterior.
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS password_hash TEXT;
