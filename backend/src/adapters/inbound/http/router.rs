use super::middleware::verify_internal_request;
use super::state::AppState;
use super::{auth, usuarios};
use axum::{Router, routing::get};
use tower_http::trace::TraceLayer;

pub fn build_http_router(state: AppState) -> Router {
    let api_routes = Router::new()
        .merge(auth::router())
        .merge(usuarios::router())
        .layer(axum::middleware::from_fn_with_state(
            state.clone(),
            verify_internal_request,
        ));

    Router::new()
        .route("/health", get(|| async { "ok" }))
        .merge(api_routes)
        .with_state(state)
        .layer(TraceLayer::new_for_http())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::adapters::outbound::rate_limiter::MemoryRateLimiter;
    use crate::adapters::outbound::security::CryptoTokenGenerator;
    use crate::application::auth::ports::{AuthRepository, PasswordHasher};
    use crate::application::usuarios::ports::{RepositoryError, UsuarioRepository};
    use crate::bootstrap::create_app_state;
    use crate::domain::auth::{ResetTokenHash, SessionId};
    use crate::domain::usuarios::{Email, HashedPassword, Nome, PlainPassword, Usuario, UsuarioId};
    use async_trait::async_trait;
    use std::sync::Arc;

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
    fn builds_complete_http_router() {
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
