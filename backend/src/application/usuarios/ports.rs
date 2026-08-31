use crate::domain::usuarios::{Email, HashedPassword, Nome, Usuario, UsuarioId};
use async_trait::async_trait;

#[derive(Debug)]
pub enum RepositoryError {
    Database(String),
    NotFound,
    Internal(String),
}

impl std::fmt::Display for RepositoryError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Database(msg) => write!(f, "erro no banco de dados: {msg}"),
            Self::NotFound => write!(f, "registro não encontrado"),
            Self::Internal(msg) => write!(f, "erro interno: {msg}"),
        }
    }
}

impl std::error::Error for RepositoryError {}

#[async_trait]
pub trait UsuarioRepository: Send + Sync {
    async fn find_by_id(&self, id: UsuarioId) -> Result<Option<Usuario>, RepositoryError>;
    async fn create(
        &self,
        nome: &Nome,
        email: &Email,
        password_hash: &HashedPassword,
    ) -> Result<UsuarioId, RepositoryError>;
}
