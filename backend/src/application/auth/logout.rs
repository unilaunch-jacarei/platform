use super::error::AuthAppError;
use super::ports::AuthRepository;
use crate::domain::auth::SessionId;
use std::sync::Arc;

pub struct LogoutUseCase {
    auth_repository: Arc<dyn AuthRepository>,
}

impl LogoutUseCase {
    pub fn new(auth_repository: Arc<dyn AuthRepository>) -> Self {
        Self { auth_repository }
    }

    pub async fn execute(&self, session_id_str: &str) -> Result<(), AuthAppError> {
        let session_id = SessionId::new(session_id_str)?;
        self.auth_repository.delete_session(&session_id).await?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::application::usuarios::ports::RepositoryError;
    use crate::domain::auth::ResetTokenHash;
    use crate::domain::usuarios::{Email, HashedPassword, Usuario, UsuarioId};
    use async_trait::async_trait;
    use std::sync::Mutex;

    struct FakeAuthRepository {
        deleted: Mutex<Vec<String>>,
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
            Ok(None)
        }
        async fn delete_session(&self, session_id: &SessionId) -> Result<(), RepositoryError> {
            self.deleted
                .lock()
                .unwrap()
                .push(session_id.as_str().to_string());
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
    async fn deletes_session_on_logout() {
        let repo = Arc::new(FakeAuthRepository {
            deleted: Mutex::new(Vec::new()),
        });
        let use_case = LogoutUseCase::new(repo.clone());

        let result = use_case.execute("active-session-id").await;
        assert!(result.is_ok());
        assert_eq!(repo.deleted.lock().unwrap().len(), 1);
        assert_eq!(repo.deleted.lock().unwrap()[0], "active-session-id");
    }
}
