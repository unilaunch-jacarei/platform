use super::handlers;
use crate::AppState;
use axum::{
    Router,
    routing::{get, post},
};

/// Apenas registra os endpoints HTTP do domínio de usuários.
pub fn router() -> Router<AppState> {
    Router::new()
        .route("/api/v1/usuarios", post(handlers::create_usuario))
        .route("/api/v1/usuarios/{id}", get(handlers::get_usuario))
}
