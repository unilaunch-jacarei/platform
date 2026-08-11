use super::handlers;
use crate::AppState;
use axum::{
    Router,
    routing::{delete, post},
};

/// Apenas registra os endpoints HTTP; regras de negócio ficam em `handlers`.
pub fn router() -> Router<AppState> {
    Router::new()
        .route("/api/v1/auth/login", post(handlers::login))
        .route(
            "/api/v1/auth/password-reset",
            post(handlers::reset_password),
        )
        .route(
            "/api/v1/auth/password-reset/confirm",
            post(handlers::confirm_reset_password),
        )
        .route("/api/v1/auth/session", post(handlers::session))
        .route("/api/v1/auth/logout", delete(handlers::logout))
}
