use super::error::AuthAppError;
use super::ports::{AuthRepository, PasswordHasher, RateLimitOperation, RateLimiterPort, SessionIdGenerator};
use crate::domain::auth::{AuthDomainError, SessionId};
use crate::domain::usuarios::{Email, PlainPassword, UsuarioId};
use std::net::IpAddr;
use std::sync::Arc;
use std::time::Duration;

pub struct LoginCommand {
    pub email: String,
    pub password: String,
    pub ip: IpAddr,
}

pub struct LoginResult {
    pub session_id: SessionId,
    pub user_id: UsuarioId,
}

pub struct LoginUseCase {
    auth_repository: Arc<dyn AuthRepository>,
    password_hasher: Arc<dyn PasswordHasher>,
    rate_limiter: Arc<dyn RateLimiterPort>,
    session_generator: Arc<dyn SessionIdGenerator>,
}

impl LoginUseCase {
    pub fn new(
        auth_repository: Arc<dyn AuthRepository>,
        password_hasher: Arc<dyn PasswordHasher>,
        rate_limiter: Arc<dyn RateLimiterPort>,
        session_generator: Arc<dyn SessionIdGenerator>,
    ) -> Self {
        Self {
            auth_repository,
            password_hasher,
            rate_limiter,
            session_generator,
        }
    }

    pub async fn execute(&self, cmd: LoginCommand) -> Result<LoginResult, AuthAppError> {
        let allowed = self
            .rate_limiter
            .is_allowed(
                cmd.ip,
                RateLimitOperation::Login,
                Duration::from_secs(60 * 60),
                5,
            )
            .await;

        if !allowed {
            return Err(AuthAppError::Domain(AuthDomainError::LimiteTentativasExcedido));
        }

        let email = Email::new(cmd.email)?;
        let plain_password = PlainPassword::new(cmd.password)?;

        let user = self
            .auth_repository
            .find_user_by_email(&email)
            .await?
            .ok_or(AuthAppError::Domain(AuthDomainError::CredenciaisInvalidas))?;

        let Some(ref password_hash) = user.password_hash else {
            return Err(AuthAppError::Domain(AuthDomainError::CredenciaisInvalidas));
        };

        let password_valid = self
            .password_hasher
            .verify(&plain_password, password_hash)
            .map_err(AuthAppError::Internal)?;

        if !password_valid {
            return Err(AuthAppError::Domain(AuthDomainError::CredenciaisInvalidas));
        }

        self.rate_limiter.reset(cmd.ip, RateLimitOperation::Login).await;

        let session_id = self.session_generator.generate();
        self.auth_repository
            .create_session(user.id, &session_id)
            .await?;

        Ok(LoginResult {
            session_id,
            user_id: user.id,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::application::usuarios::ports::RepositoryError;
    use crate::domain::auth::{ResetTokenHash, SessionId};
    use crate::domain::usuarios::{HashedPassword, Nome, Usuario};
    use async_trait::async_trait;
    use std::sync::Mutex;

    struct FakeAuthRepository {
        user: Option<Usuario>,
        sessions: Mutex<Vec<(UsuarioId, SessionId)>>,
    }

    #[async_trait]
    impl AuthRepository for FakeAuthRepository {
        async fn find_user_by_email(&self, email: &Email) -> Result<Option<Usuario>, RepositoryError> {
            Ok(self.user.clone().filter(|u| &u.email == email))
        }

        async fn create_session(
            &self,
            user_id: UsuarioId,
            session_id: &SessionId,
        ) -> Result<(), RepositoryError> {
            self.sessions.lock().unwrap().push((user_id, session_id.clone()));
            Ok(())
        }

        async fn find_user_id_by_session(&self, _session_id: &SessionId) -> Result<Option<UsuarioId>, RepositoryError> {
            Ok(None)
        }

        async fn delete_session(&self, _session_id: &SessionId) -> Result<(), RepositoryError> {
            Ok(())
        }

        async fn create_password_reset(&self, _user_id: UsuarioId, _token_hash: &ResetTokenHash) -> Result<(), RepositoryError> {
            Ok(())
        }

        async fn consume_password_reset(&self, _token_hash: &ResetTokenHash, _password_hash: &HashedPassword) -> Result<bool, RepositoryError> {
            Ok(true)
        }
    }

    struct FakePasswordHasher;

    impl PasswordHasher for FakePasswordHasher {
        fn hash(&self, password: &PlainPassword) -> Result<HashedPassword, String> {
            Ok(HashedPassword::new(format!("hash_{}", password.as_str())))
        }

        fn verify(&self, password: &PlainPassword, hashed: &HashedPassword) -> Result<bool, String> {
            Ok(hashed.as_str() == format!("hash_{}", password.as_str()))
        }
    }

    struct FakeRateLimiter {
        allowed: bool,
    }

    #[async_trait]
    impl RateLimiterPort for FakeRateLimiter {
        async fn is_allowed(&self, _ip: IpAddr, _op: RateLimitOperation, _window: Duration, _max: u32) -> bool {
            self.allowed
        }

        async fn reset(&self, _ip: IpAddr, _op: RateLimitOperation) {}
    }

    struct FakeSessionGenerator;

    impl SessionIdGenerator for FakeSessionGenerator {
        fn generate(&self) -> SessionId {
            SessionId::new("mocked-session-id-12345").unwrap()
        }
    }

    fn test_ip() -> IpAddr {
        "127.0.0.1".parse().unwrap()
    }

    #[tokio::test]
    async fn logs_in_successfully_with_valid_credentials() {
        let user = Usuario::new(
            UsuarioId::new(10),
            Nome::new("Carlos").unwrap(),
            Email::new("carlos@example.com").unwrap(),
            Some(HashedPassword::new("hash_senha-correta")),
        );

        let repo = Arc::new(FakeAuthRepository {
            user: Some(user),
            sessions: Mutex::new(Vec::new()),
        });
        let hasher = Arc::new(FakePasswordHasher);
        let limiter = Arc::new(FakeRateLimiter { allowed: true });
        let generator = Arc::new(FakeSessionGenerator);

        let use_case = LoginUseCase::new(repo.clone(), hasher, limiter, generator);

        let result = use_case
            .execute(LoginCommand {
                email: "carlos@example.com".to_string(),
                password: "senha-correta".to_string(),
                ip: test_ip(),
            })
            .await;

        assert!(result.is_ok());
        let res = result.unwrap();
        assert_eq!(res.user_id.value(), 10);
        assert_eq!(res.session_id.as_str(), "mocked-session-id-12345");
        assert_eq!(repo.sessions.lock().unwrap().len(), 1);
    }

    #[tokio::test]
    async fn rejects_invalid_password() {
        let user = Usuario::new(
            UsuarioId::new(10),
            Nome::new("Carlos").unwrap(),
            Email::new("carlos@example.com").unwrap(),
            Some(HashedPassword::new("hash_senha-correta")),
        );

        let repo = Arc::new(FakeAuthRepository {
            user: Some(user),
            sessions: Mutex::new(Vec::new()),
        });
        let hasher = Arc::new(FakePasswordHasher);
        let limiter = Arc::new(FakeRateLimiter { allowed: true });
        let generator = Arc::new(FakeSessionGenerator);

        let use_case = LoginUseCase::new(repo, hasher, limiter, generator);

        let result = use_case
            .execute(LoginCommand {
                email: "carlos@example.com".to_string(),
                password: "senha-errada".to_string(),
                ip: test_ip(),
            })
            .await;

        assert!(matches!(
            result,
            Err(AuthAppError::Domain(AuthDomainError::CredenciaisInvalidas))
        ));
    }

    #[tokio::test]
    async fn blocks_when_rate_limit_exceeded() {
        let repo = Arc::new(FakeAuthRepository {
            user: None,
            sessions: Mutex::new(Vec::new()),
        });
        let hasher = Arc::new(FakePasswordHasher);
        let limiter = Arc::new(FakeRateLimiter { allowed: false });
        let generator = Arc::new(FakeSessionGenerator);

        let use_case = LoginUseCase::new(repo, hasher, limiter, generator);

        let result = use_case
            .execute(LoginCommand {
                email: "carlos@example.com".to_string(),
                password: "senha-correta".to_string(),
                ip: test_ip(),
            })
            .await;

        assert!(matches!(
            result,
            Err(AuthAppError::Domain(AuthDomainError::LimiteTentativasExcedido))
        ));
    }
}

