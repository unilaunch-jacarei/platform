CREATE TABLE password_reset_tokens (
    id BIGSERIAL PRIMARY KEY,
    usuario_id BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    token_hash char(64) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX password_reset_tokens_user_id_idx
    ON password_reset_tokens (usuario_id);

CREATE INDEX password_reset_tokens_expires_at_idx
    ON password_reset_tokens (expires_at);