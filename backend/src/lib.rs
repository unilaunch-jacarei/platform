pub mod domains;
pub mod error;
pub mod infra;

use axum::{Router, routing::get};
use std::sync::Arc;
use tower_http::trace::TraceLayer;

use crate::infra::{email::EmailSender, rate_limiter::RateLimiter};

#[derive(Clone)]
pub struct AppState {
    pub db: sqlx::PgPool,
    pub internal_secret: Arc<str>,
    pub rate_limiter: Arc<RateLimiter>,
    pub email_sender: Option<Arc<dyn EmailSender>>,
    pub public_app_url: Arc<str>,
    pub email_logo_url: Option<Arc<str>>,
}

pub fn build_app(state: AppState) -> Router {
    Router::new()
        .route("/health", get(|| async { "ok" }))
        .merge(domains::auth::routes::router())
        .merge(domains::usuarios::routes::router())
        .with_state(state.clone())
        .layer(axum::middleware::from_fn_with_state(
            state,
            infra::hmac::verify_internal_request,
        ))
        .layer(TraceLayer::new_for_http())
}
