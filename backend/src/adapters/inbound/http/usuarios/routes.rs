use super::handlers;
use crate::adapters::inbound::http::state::AppState;
use axum::{
    Router,
    routing::{get, post},
};

pub fn router() -> Router<AppState> {
    Router::new()
        .route("/api/v1/usuarios", post(handlers::create_usuario))
        .route("/api/v1/usuarios/{id}", get(handlers::get_usuario))
}
