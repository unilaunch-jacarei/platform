use super::error::AuthAppError;
use super::ports::AuthRepository;
use crate::domain::auth::{AuthDomainError, SessionId};
use crate::domain::usuarios::UsuarioId;
use std::sync::Arc;

pub struct ValidateSessionUseCase {
    auth_repository: Arc<dyn AuthRepository>,
}

impl ValidateSessionUseCase {
    pub fn new(auth_repository: Arc<dyn AuthRepository>) -> Self {
        Self { auth_repository }
    }

    pub async fn execute(&self, session_id_str: &str) -> Result<UsuarioId, AuthAppError> {
        let session_id = SessionId::new(session_id_str)?;
        let user_id = self
            .auth_repository
            .find_user_id_by_session(&session_id)
            .await?
            .ok_or(AuthAppError::Domain(
                AuthDomainError::SessaoInvalidaOuExpirada,
            ))?;

        Ok(user_id)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::application::usuarios::ports::RepositoryError;
    use crate::domain::auth::ResetTokenHash;
    use crate::domain::usuarios::{Email, HashedPassword, Usuario};
    use async_trait::async_trait;

    struct FakeAuthRepository {
        user_id: Option<UsuarioId>,
    }

    #[async_trait]
    impl AuthRepository for FakeAuthRepository {
        async fn find_user_by_email(
            &self,
            _email: &Email,
        ) -> Result<Option<Usuario>, RepositoryError> {
            Ok(None)
        }
        async fn create_session(
            &self,
            _user_id: UsuarioId,
            _session_id: &SessionId,
        ) -> Result<(), RepositoryError> {
            Ok(())
        }
        async fn find_user_id_by_session(
            &self,
            _session_id: &SessionId,
        ) -> Result<Option<UsuarioId>, RepositoryError> {
            Ok(self.user_id)
        }
        async fn delete_session(&self, _session_id: &SessionId) -> Result<(), RepositoryError> {
            Ok(())
        }
        async fn create_password_reset(
            &self,
            _user_id: UsuarioId,
            _token_hash: &ResetTokenHash,
        ) -> Result<(), RepositoryError> {
            Ok(())
        }
        async fn consume_password_reset(
            &self,
            _token_hash: &ResetTokenHash,
            _password_hash: &HashedPassword,
        ) -> Result<bool, RepositoryError> {
            Ok(true)
        }
    }

    #[tokio::test]
    async fn validates_active_session() {
        let repo = Arc::new(FakeAuthRepository {
            user_id: Some(UsuarioId::new(42)),
        });
        let use_case = ValidateSessionUseCase::new(repo);

        let result = use_case.execute("valid-session-123").await;
        assert!(result.is_ok());
        assert_eq!(result.unwrap().value(), 42);
    }

    #[tokio::test]
    async fn fails_when_session_expired() {
        let repo = Arc::new(FakeAuthRepository { user_id: None });
        let use_case = ValidateSessionUseCase::new(repo);

        let result = use_case.execute("expired-session").await;
        assert!(matches!(
            result,
            Err(AuthAppError::Domain(
                AuthDomainError::SessaoInvalidaOuExpirada
            ))
        ));
    }
}
