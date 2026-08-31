use super::config::AppConfig;
use crate::adapters::inbound::http::{AppState, AuthUseCases, UserUseCases, build_http_router};
use crate::adapters::outbound::email::ResendEmailSender;
use crate::adapters::outbound::persistence::postgres::{
    PostgresAuthRepository, PostgresUsuarioRepository,
};
use crate::adapters::outbound::rate_limiter::MemoryRateLimiter;
use crate::adapters::outbound::security::{Argon2PasswordHasher, CryptoTokenGenerator};
use crate::application::auth::ports::{
    AuthRepository, EmailSenderPort, PasswordHasher, RateLimiterPort, ResetTokenGenerator,
    SessionIdGenerator,
};
use crate::application::auth::{
    ConfirmPasswordResetUseCase, LoginUseCase, LogoutUseCase, RequestPasswordResetUseCase,
    ValidateSessionUseCase,
};
use crate::application::usuarios::ports::UsuarioRepository;
use crate::application::usuarios::{CreateUsuarioUseCase, GetUsuarioUseCase};
use anyhow::{Context, Result};
use axum::Router;
use sqlx::postgres::PgPoolOptions;
use std::sync::Arc;
use tracing::warn;

pub struct ApplicationContainer {
    pub router: Router,
    pub config: AppConfig,
}

#[allow(clippy::too_many_arguments)]
pub fn create_app_state(
    usuario_repo: Arc<dyn UsuarioRepository>,
    auth_repo: Arc<dyn AuthRepository>,
    password_hasher: Arc<dyn PasswordHasher>,
    rate_limiter: Arc<dyn RateLimiterPort>,
    token_generator: Arc<dyn ResetTokenGenerator>,
    session_generator: Arc<dyn SessionIdGenerator>,
    email_sender: Option<Arc<dyn EmailSenderPort>>,
    internal_secret: Arc<str>,
    public_app_url: Arc<str>,
    email_logo_url: Option<Arc<str>>,
) -> AppState {
    let create_usuario = Arc::new(CreateUsuarioUseCase::new(
        usuario_repo.clone(),
        password_hasher.clone(),
    ));
    let get_usuario = Arc::new(GetUsuarioUseCase::new(usuario_repo.clone()));

    let login = Arc::new(LoginUseCase::new(
        auth_repo.clone(),
        password_hasher.clone(),
        rate_limiter.clone(),
        session_generator.clone(),
    ));
    let session = Arc::new(ValidateSessionUseCase::new(auth_repo.clone()));
    let logout = Arc::new(LogoutUseCase::new(auth_repo.clone()));
    let reset_password = Arc::new(RequestPasswordResetUseCase::new(
        auth_repo.clone(),
        email_sender,
        rate_limiter.clone(),
        token_generator.clone(),
        public_app_url,
        email_logo_url,
    ));
    let confirm_reset_password = Arc::new(ConfirmPasswordResetUseCase::new(
        auth_repo.clone(),
        password_hasher.clone(),
        token_generator.clone(),
    ));

    AppState {
        user_use_cases: UserUseCases {
            create_usuario,
            get_usuario,
        },
        auth_use_cases: AuthUseCases {
            login,
            session,
            logout,
            reset_password,
            confirm_reset_password,
        },
        internal_secret,
    }
}

pub async fn build_app(config: AppConfig) -> Result<ApplicationContainer> {
    let pool = PgPoolOptions::new()
        .max_connections(20)
        .connect(&config.database_url)
        .await
        .context("falha ao conectar ao PostgreSQL")?;

    sqlx::migrate!("./migrations")
        .run(&pool)
        .await
        .context("falha ao executar migrations")?;

    let usuario_repo = Arc::new(PostgresUsuarioRepository::new(pool.clone()));
    let auth_repo = Arc::new(PostgresAuthRepository::new(pool.clone()));
    let password_hasher = Arc::new(Argon2PasswordHasher::new());
    let crypto_generator = Arc::new(CryptoTokenGenerator::new());
    let rate_limiter = Arc::new(MemoryRateLimiter::new());

    let email_sender: Option<Arc<dyn EmailSenderPort>> = match ResendEmailSender::from_env() {
        Ok(sender) => Some(Arc::new(sender)),
        Err(error) => {
            warn!(
                %error,
                "Resend não configurado; recuperação de senha ficará indisponível"
            );
            None
        }
    };

    let state = create_app_state(
        usuario_repo,
        auth_repo,
        password_hasher,
        rate_limiter,
        crypto_generator.clone(),
        crypto_generator,
        email_sender,
        config.internal_secret.clone(),
        config.public_app_url.clone(),
        config.email_logo_url.clone(),
    );

    let router = build_http_router(state);

    Ok(ApplicationContainer { router, config })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::application::usuarios::ports::RepositoryError;
    use crate::domain::auth::{ResetTokenHash, SessionId};
    use crate::domain::usuarios::{Email, HashedPassword, Nome, PlainPassword, Usuario, UsuarioId};
    use async_trait::async_trait;

    struct DummyUserRepo;
    #[async_trait]
    impl UsuarioRepository for DummyUserRepo {
        async fn find_by_id(&self, _id: UsuarioId) -> Result<Option<Usuario>, RepositoryError> {
            Ok(None)
        }
        async fn create(
            &self,
            _n: &Nome,
            _e: &Email,
            _p: &HashedPassword,
        ) -> Result<UsuarioId, RepositoryError> {
            Ok(UsuarioId::new(1))
        }
    }

    struct DummyAuthRepo;
    #[async_trait]
    impl AuthRepository for DummyAuthRepo {
        async fn find_user_by_email(&self, _e: &Email) -> Result<Option<Usuario>, RepositoryError> {
            Ok(None)
        }
        async fn create_session(
            &self,
            _u: UsuarioId,
            _s: &SessionId,
        ) -> Result<(), RepositoryError> {
            Ok(())
        }
        async fn find_user_id_by_session(
            &self,
            _s: &SessionId,
        ) -> Result<Option<UsuarioId>, RepositoryError> {
            Ok(None)
        }
        async fn delete_session(&self, _s: &SessionId) -> Result<(), RepositoryError> {
            Ok(())
        }
        async fn create_password_reset(
            &self,
            _u: UsuarioId,
            _t: &ResetTokenHash,
        ) -> Result<(), RepositoryError> {
            Ok(())
        }
        async fn consume_password_reset(
            &self,
            _t: &ResetTokenHash,
            _p: &HashedPassword,
        ) -> Result<bool, RepositoryError> {
            Ok(true)
        }
    }

    struct DummyHasher;
    impl PasswordHasher for DummyHasher {
        fn hash(&self, _p: &PlainPassword) -> Result<HashedPassword, String> {
            Ok(HashedPassword::new("hash"))
        }
        fn verify(&self, _p: &PlainPassword, _h: &HashedPassword) -> Result<bool, String> {
            Ok(true)
        }
    }

    #[test]
    fn creates_valid_app_state_and_router() {
        let user_repo = Arc::new(DummyUserRepo);
        let auth_repo = Arc::new(DummyAuthRepo);
        let hasher = Arc::new(DummyHasher);
        let crypto = Arc::new(CryptoTokenGenerator::new());
        let limiter = Arc::new(MemoryRateLimiter::new());

        let state = create_app_state(
            user_repo,
            auth_repo,
            hasher,
            limiter,
            crypto.clone(),
            crypto,
            None,
            Arc::from("secret"),
            Arc::from("http://localhost"),
            None,
        );

        let _router = build_http_router(state);
    }
}
