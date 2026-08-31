use super::error::AuthAppError;
use super::ports::{AuthRepository, PasswordHasher, ResetTokenGenerator};
use crate::domain::auth::{AuthDomainError, RawResetToken};
use crate::domain::usuarios::PlainPassword;
use std::sync::Arc;

pub struct ConfirmPasswordResetCommand {
    pub token: String,
    pub new_password: String,
}

pub struct ConfirmPasswordResetUseCase {
    auth_repository: Arc<dyn AuthRepository>,
    password_hasher: Arc<dyn PasswordHasher>,
    token_generator: Arc<dyn ResetTokenGenerator>,
}

impl ConfirmPasswordResetUseCase {
    pub fn new(
        auth_repository: Arc<dyn AuthRepository>,
        password_hasher: Arc<dyn PasswordHasher>,
        token_generator: Arc<dyn ResetTokenGenerator>,
    ) -> Self {
        Self {
            auth_repository,
            password_hasher,
            token_generator,
        }
    }

    pub async fn execute(&self, cmd: ConfirmPasswordResetCommand) -> Result<(), AuthAppError> {
        let raw_token = RawResetToken::new(cmd.token)?;
        let plain_password = PlainPassword::new(cmd.new_password)?;

        let token_hash = self.token_generator.hash_token(&raw_token);
        let password_hash = self
            .password_hasher
            .hash(&plain_password)
            .map_err(AuthAppError::Internal)?;

        let consumed = self
            .auth_repository
            .consume_password_reset(&token_hash, &password_hash)
            .await?;

        if !consumed {
            return Err(AuthAppError::Domain(
                AuthDomainError::TokenRecuperacaoInvalido,
            ));
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::application::usuarios::ports::RepositoryError;
    use crate::domain::auth::{ResetTokenHash, SessionId};
    use crate::domain::usuarios::{Email, HashedPassword, Usuario, UsuarioId};
    use async_trait::async_trait;

    struct FakeAuthRepository {
        consume_success: bool,
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
            Ok(self.consume_success)
        }
    }

    struct FakePasswordHasher;

    impl PasswordHasher for FakePasswordHasher {
        fn hash(&self, password: &PlainPassword) -> Result<HashedPassword, String> {
            Ok(HashedPassword::new(format!("hash_{}", password.as_str())))
        }

        fn verify(
            &self,
            password: &PlainPassword,
            hashed: &HashedPassword,
        ) -> Result<bool, String> {
            Ok(hashed.as_str() == format!("hash_{}", password.as_str()))
        }
    }

    struct FakeTokenGenerator;

    impl ResetTokenGenerator for FakeTokenGenerator {
        fn generate(&self) -> (RawResetToken, ResetTokenHash) {
            (
                RawResetToken::new("raw").unwrap(),
                ResetTokenHash::new("hash"),
            )
        }

        fn hash_token(&self, raw: &RawResetToken) -> ResetTokenHash {
            ResetTokenHash::new(format!("hash_{}", raw.as_str()))
        }
    }

    #[tokio::test]
    async fn confirms_password_reset_successfully() {
        let repo = Arc::new(FakeAuthRepository {
            consume_success: true,
        });
        let hasher = Arc::new(FakePasswordHasher);
        let token_gen = Arc::new(FakeTokenGenerator);

        let use_case = ConfirmPasswordResetUseCase::new(repo, hasher, token_gen);

        let result = use_case
            .execute(ConfirmPasswordResetCommand {
                token: "token-valido-123".to_string(),
                new_password: "nova-senha-segura".to_string(),
            })
            .await;

        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn fails_when_token_is_invalid_or_expired() {
        let repo = Arc::new(FakeAuthRepository {
            consume_success: false,
        });
        let hasher = Arc::new(FakePasswordHasher);
        let token_gen = Arc::new(FakeTokenGenerator);

        let use_case = ConfirmPasswordResetUseCase::new(repo, hasher, token_gen);

        let result = use_case
            .execute(ConfirmPasswordResetCommand {
                token: "token-invalido".to_string(),
                new_password: "nova-senha-segura".to_string(),
            })
            .await;

        assert!(matches!(
            result,
            Err(AuthAppError::Domain(
                AuthDomainError::TokenRecuperacaoInvalido
            ))
        ));
    }
}
