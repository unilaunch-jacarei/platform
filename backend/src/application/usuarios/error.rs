use crate::application::usuarios::ports::RepositoryError;
use crate::domain::usuarios::UsuarioDomainError;
use std::fmt;

#[derive(Debug)]
pub enum UsuarioAppError {
    Domain(UsuarioDomainError),
    Repository(RepositoryError),
    UsuarioNaoEncontrado(i64),
    Internal(String),
}

impl fmt::Display for UsuarioAppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Domain(err) => write!(f, "{err}"),
            Self::Repository(err) => write!(f, "{err}"),
            Self::UsuarioNaoEncontrado(id) => write!(f, "usuário {id} não encontrado"),
            Self::Internal(msg) => write!(f, "erro interno: {msg}"),
        }
    }
}

impl std::error::Error for UsuarioAppError {}

impl From<UsuarioDomainError> for UsuarioAppError {
    fn from(err: UsuarioDomainError) -> Self {
        Self::Domain(err)
    }
}

impl From<RepositoryError> for UsuarioAppError {
    fn from(err: RepositoryError) -> Self {
        Self::Repository(err)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn formats_usuario_app_errors() {
        assert_eq!(
            UsuarioAppError::from(UsuarioDomainError::NomeVazio).to_string(),
            "nome não pode ser vazio"
        );
        assert_eq!(
            UsuarioAppError::from(RepositoryError::NotFound).to_string(),
            "registro não encontrado"
        );
        assert_eq!(
            UsuarioAppError::UsuarioNaoEncontrado(5).to_string(),
            "usuário 5 não encontrado"
        );
        assert_eq!(
            UsuarioAppError::Internal("falha".into()).to_string(),
            "erro interno: falha"
        );
    }
}
