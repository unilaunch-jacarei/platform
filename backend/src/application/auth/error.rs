use crate::application::usuarios::ports::RepositoryError;
use crate::domain::auth::AuthDomainError;
use crate::domain::usuarios::UsuarioDomainError;
use std::fmt;

#[derive(Debug)]
pub enum AuthAppError {
    Domain(AuthDomainError),
    UsuarioDomain(UsuarioDomainError),
    Repository(RepositoryError),
    Internal(String),
}

impl fmt::Display for AuthAppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Domain(err) => write!(f, "{err}"),
            Self::UsuarioDomain(err) => write!(f, "{err}"),
            Self::Repository(err) => write!(f, "{err}"),
            Self::Internal(msg) => write!(f, "erro interno: {msg}"),
        }
    }
}

impl std::error::Error for AuthAppError {}

impl From<AuthDomainError> for AuthAppError {
    fn from(err: AuthDomainError) -> Self {
        Self::Domain(err)
    }
}

impl From<UsuarioDomainError> for AuthAppError {
    fn from(err: UsuarioDomainError) -> Self {
        Self::UsuarioDomain(err)
    }
}

impl From<RepositoryError> for AuthAppError {
    fn from(err: RepositoryError) -> Self {
        Self::Repository(err)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn formats_auth_app_errors() {
        assert_eq!(
            AuthAppError::from(AuthDomainError::CredenciaisInvalidas).to_string(),
            "credenciais inválidas"
        );
        assert_eq!(
            AuthAppError::from(UsuarioDomainError::SenhaCurta).to_string(),
            "senha deve possuir no mínimo 8 caracteres"
        );
        assert_eq!(
            AuthAppError::from(RepositoryError::NotFound).to_string(),
            "registro não encontrado"
        );
        assert_eq!(
            AuthAppError::Internal("erro".into()).to_string(),
            "erro interno: erro"
        );
    }
}
