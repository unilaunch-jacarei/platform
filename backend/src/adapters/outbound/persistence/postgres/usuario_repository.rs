use super::models::PostgresUserModel;
use crate::application::usuarios::ports::{RepositoryError, UsuarioRepository};
use crate::domain::usuarios::{Email, HashedPassword, Nome, Usuario, UsuarioId};
use async_trait::async_trait;
use sqlx::PgPool;

pub struct PostgresUsuarioRepository {
    pool: PgPool,
}

impl PostgresUsuarioRepository {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }
}

#[async_trait]
impl UsuarioRepository for PostgresUsuarioRepository {
    async fn find_by_id(&self, id: UsuarioId) -> Result<Option<Usuario>, RepositoryError> {
        let record = sqlx::query_as!(
            PostgresUserModel,
            r#"SELECT id, nome, email, password_hash FROM usuarios WHERE id = $1"#,
            id.value()
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

    async fn create(
        &self,
        nome: &Nome,
        email: &Email,
        password_hash: &HashedPassword,
    ) -> Result<UsuarioId, RepositoryError> {
        let result = sqlx::query!(
            r#"INSERT INTO usuarios (nome, email, password_hash)
               VALUES ($1, $2, $3)
               RETURNING id"#,
            nome.as_str(),
            email.as_str(),
            password_hash.as_str()
        )
        .fetch_one(&self.pool)
        .await
        .map_err(|e| RepositoryError::Database(e.to_string()))?;

        Ok(UsuarioId::new(result.id))
    }
}
