use super::repository;
use crate::{AppState, error::AppError, infra::password::verify_password};
use axum::{
    Router,
    extract::{ConnectInfo, State},
    http::{Extensions, StatusCode},
    response::Json,
    routing::{delete, post},
};
use serde::{Deserialize, Serialize};
use std::{
    net::SocketAddr,
    time::{Duration, Instant},
};

#[derive(Debug, Deserialize)]
pub struct LoginRequest {
    pub email: String,
    pub password: String,
}

#[derive(Debug, Serialize)]
pub struct LoginResponse {
    pub session_id: String,
    pub user_id: i64,
}

pub fn router() -> Router<AppState> {
    Router::new()
        .route("/api/v1/auth/login", post(login))
        .route("/api/v1/auth/session", post(session))
        .route("/api/v1/auth/logout", delete(logout))
}

pub async fn login(
    State(state): State<AppState>,
    ConnectInfo(address): ConnectInfo<SocketAddr>,
    Json(input): Json<LoginRequest>,
) -> Result<(StatusCode, Json<LoginResponse>), AppError> {
    if !allow_login_attempt(&state, address.ip()).await {
        return Err(anyhow::anyhow!("limite de tentativas excedido").into());
    }

    let user = repository::find_user_by_email(&state.db, &input.email)
        .await?
        .ok_or_else(|| anyhow::anyhow!("credenciais inválidas"))?;
    let Some(password_hash) = user.password_hash else {
        return Err(anyhow::anyhow!("credenciais inválidas").into());
    };
    if !verify_password(&input.password, &password_hash)? {
        return Err(anyhow::anyhow!("credenciais inválidas").into());
    }

    state.login_attempts.lock().await.remove(&address.ip());
    let session_id = repository::create_session(&state.db, user.id).await?;
    Ok((
        StatusCode::CREATED,
        Json(LoginResponse {
            session_id,
            user_id: user.id,
        }),
    ))
}

async fn allow_login_attempt(state: &AppState, ip: std::net::IpAddr) -> bool {
    const WINDOW: Duration = Duration::from_secs(60);
    const MAX_ATTEMPTS: u32 = 5;
    let now = Instant::now();
    let mut attempts = state.login_attempts.lock().await;
    let window = attempts.entry(ip).or_default();

    if window
        .started_at
        .is_none_or(|started| now.duration_since(started) >= WINDOW)
    {
        window.started_at = Some(now);
        window.count = 0;
    }

    if window.count >= MAX_ATTEMPTS {
        return false;
    }
    window.count += 1;
    true
}

pub async fn session(
    State(state): State<AppState>,
    extensions: Extensions,
) -> Result<Json<serde_json::Value>, AppError> {
    let session_id = extensions
        .get::<String>()
        .ok_or_else(|| anyhow::anyhow!("sessão ausente"))?;
    let user_id = repository::find_user_id_by_session(&state.db, session_id)
        .await?
        .ok_or_else(|| anyhow::anyhow!("sessão inválida ou expirada"))?;
    Ok(Json(serde_json::json!({ "user_id": user_id })))
}

pub async fn logout(
    State(state): State<AppState>,
    extensions: Extensions,
) -> Result<StatusCode, AppError> {
    let session_id = extensions
        .get::<String>()
        .ok_or_else(|| anyhow::anyhow!("sessão ausente"))?;
    repository::delete_session(&state.db, session_id).await?;
    Ok(StatusCode::NO_CONTENT)
}
