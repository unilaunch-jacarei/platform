use super::models::PostgresUserModel;
use crate::application::auth::ports::AuthRepository;
use crate::application::usuarios::ports::RepositoryError;
use crate::domain::auth::{ResetTokenHash, SessionId};
use crate::domain::usuarios::{Email, HashedPassword, Usuario, UsuarioId};
use async_trait::async_trait;
use sqlx::PgPool;

pub struct PostgresAuthRepository {
    pool: PgPool,
}

impl PostgresAuthRepository {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }
}

#[async_trait]
impl AuthRepository for PostgresAuthRepository {
    async fn find_user_by_email(&self, email: &Email) -> Result<Option<Usuario>, RepositoryError> {
        let record = sqlx::query_as!(
            PostgresUserModel,
            r#"SELECT id, nome, email, password_hash FROM usuarios WHERE email = $1"#,
            email.as_str()
        )
        .fetch_optional(&self.pool)
        .await
        .map_err(|e| RepositoryError::Database(e.to_string()))?;

        match record {
            Some(model) => model
                .try_into_domain()
                .map(Some)
                .map_err(RepositoryError::Internal),
            None => Ok(None),
        }
    }

    async fn create_session(
        &self,
        user_id: UsuarioId,
        session_id: &SessionId,
    ) -> Result<(), RepositoryError> {
        sqlx::query!(
            r#"INSERT INTO sessoes (id, usuario_id, expires_at)
               VALUES ($1, $2, NOW() + INTERVAL '8 hours')"#,
            session_id.as_str(),
            user_id.value()
        )
        .execute(&self.pool)
        .await
        .map_err(|e| RepositoryError::Database(e.to_string()))?;

        Ok(())
    }

    async fn find_user_id_by_session(
        &self,
        session_id: &SessionId,
    ) -> Result<Option<UsuarioId>, RepositoryError> {
        let session = sqlx::query!(
            r#"WITH renewed AS (
                   UPDATE sessoes
                   SET expires_at = LEAST(
                       NOW() + INTERVAL '8 hours',
                       created_at + INTERVAL '24 hours'
                   )
                   WHERE id = $1
                     AND expires_at > NOW()
                     AND expires_at <= NOW() + INTERVAL '30 minutes'
                   RETURNING usuario_id
               )
               SELECT usuario_id FROM renewed
               UNION ALL
               SELECT usuario_id FROM sessoes
               WHERE id = $1 AND expires_at > NOW()
               LIMIT 1"#,
            session_id.as_str()
        )
        .fetch_optional(&self.pool)
        .await
        .map_err(|e| RepositoryError::Database(e.to_string()))?;

        Ok(session.and_then(|row| row.usuario_id).map(UsuarioId::new))
    }

    async fn delete_session(&self, session_id: &SessionId) -> Result<(), RepositoryError> {
        sqlx::query!("DELETE FROM sessoes WHERE id = $1", session_id.as_str())
            .execute(&self.pool)
            .await
            .map_err(|e| RepositoryError::Database(e.to_string()))?;

        Ok(())
    }

    async fn create_password_reset(
        &self,
        user_id: UsuarioId,
        token_hash: &ResetTokenHash,
    ) -> Result<(), RepositoryError> {
        sqlx::query!(
            r#"INSERT INTO password_reset_tokens (usuario_id, token_hash, expires_at)
               VALUES ($1, $2, NOW() + INTERVAL '1 hour')"#,
            user_id.value(),
            token_hash.as_str()
        )
        .execute(&self.pool)
        .await
        .map_err(|e| RepositoryError::Database(e.to_string()))?;

        Ok(())
    }

    async fn consume_password_reset(
        &self,
        token_hash: &ResetTokenHash,
        password_hash: &HashedPassword,
    ) -> Result<bool, RepositoryError> {
        let mut transaction = self
            .pool
            .begin()
            .await
            .map_err(|e| RepositoryError::Database(e.to_string()))?;

        let token = sqlx::query!(
            r#"SELECT id, usuario_id
               FROM password_reset_tokens
               WHERE token_hash = $1
                 AND used_at IS NULL
                 AND expires_at > NOW()
               FOR UPDATE"#,
            token_hash.as_str()
        )
        .fetch_optional(&mut *transaction)
        .await
        .map_err(|e| RepositoryError::Database(e.to_string()))?;

        let Some(token) = token else {
            return Ok(false);
        };

        sqlx::query!(
            "UPDATE usuarios SET password_hash = $1 WHERE id = $2",
            password_hash.as_str(),
            token.usuario_id
        )
        .execute(&mut *transaction)
        .await
        .map_err(|e| RepositoryError::Database(e.to_string()))?;

        sqlx::query!(
            "UPDATE password_reset_tokens SET used_at = NOW() WHERE id = $1",
            token.id
        )
        .execute(&mut *transaction)
        .await
        .map_err(|e| RepositoryError::Database(e.to_string()))?;

        sqlx::query!(
            "DELETE FROM sessoes WHERE usuario_id = $1",
            token.usuario_id
        )
        .execute(&mut *transaction)
        .await
        .map_err(|e| RepositoryError::Database(e.to_string()))?;

        transaction
            .commit()
            .await
            .map_err(|e| RepositoryError::Database(e.to_string()))?;

        Ok(true)
    }
}
