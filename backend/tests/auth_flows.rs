use anyhow::Result;
use async_trait::async_trait;
use axum::{
    Json,
    extract::{ConnectInfo, State},
    http::StatusCode,
};
use backend::{
    AppState,
    domains::{
        auth::{
            handlers::{
                ConfirmResetPasswordRequest, LoginRequest, ResetPasswordRequest,
                confirm_reset_password, login, reset_password,
            },
            repository as auth_repository,
        },
        usuarios::repository as usuarios_repository,
    },
    infra::{
        email::{EmailMessage, EmailSender},
        rate_limiter::RateLimiter,
    },
};
use sqlx::{PgPool, postgres::PgPoolOptions};
use std::{
    env,
    net::{IpAddr, Ipv4Addr, SocketAddr},
    sync::Arc,
    time::{SystemTime, UNIX_EPOCH},
};
use tokio::sync::Mutex;

#[derive(Clone, Default)]
struct MockEmailSender {
    messages: Arc<Mutex<Vec<EmailMessage>>>,
}

#[async_trait]
impl EmailSender for MockEmailSender {
    async fn send(&self, message: EmailMessage) -> Result<String> {
        self.messages.lock().await.push(message);
        Ok("email-test-id".to_owned())
    }
}

async fn test_pool() -> PgPool {
    dotenvy::dotenv().ok();
    let database_url = env::var("DATABASE_URL")
        .expect("DATABASE_URL deve apontar para um PostgreSQL de teste/desenvolvimento");
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&database_url)
        .await
        .expect("falha ao conectar ao PostgreSQL de teste");

    sqlx::migrate!("./migrations")
        .run(&pool)
        .await
        .expect("falha ao executar migrations de teste");
    pool
}

fn test_state(pool: PgPool, email_sender: Option<Arc<dyn EmailSender>>) -> AppState {
    AppState {
        db: pool,
        internal_secret: Arc::from("test-secret"),
        rate_limiter: Arc::new(RateLimiter::new()),
        email_sender,
        public_app_url: Arc::from("http://localhost:5173"),
        email_logo_url: Some(Arc::from("https://example.com/logo.png")),
    }
}

fn address(octet: u8) -> SocketAddr {
    SocketAddr::new(IpAddr::V4(Ipv4Addr::new(127, 0, 0, octet)), 30_000)
}

fn unique_email(prefix: &str) -> String {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    format!("{prefix}-{nanos}@example.com")
}

fn extract_reset_token(html: &str) -> String {
    let marker = "/reset-password?token=";
    html.split(marker)
        .nth(1)
        .and_then(|tail| tail.split('"').next())
        .expect("email deve conter link de recuperação")
        .to_owned()
}

#[tokio::test]
#[ignore = "requer DATABASE_URL apontando para PostgreSQL de teste/desenvolvimento"]
async fn login_creates_a_server_side_session() {
    let pool = test_pool().await;
    let email = unique_email("login");
    let user_id = usuarios_repository::create(&pool, "Login Test", &email, "senha-antiga-segura")
        .await
        .unwrap();
    let state = test_state(pool.clone(), None);

    let (status, Json(response)) = login(
        State(state),
        ConnectInfo(address(10)),
        Json(LoginRequest {
            email,
            password: "senha-antiga-segura".to_owned(),
        }),
    )
    .await
    .unwrap();

    assert_eq!(status, StatusCode::CREATED);
    assert_eq!(response.user_id, user_id);
    assert_eq!(response.session_id.len(), 64);
    assert_eq!(
        auth_repository::find_user_id_by_session(&pool, &response.session_id)
            .await
            .unwrap(),
        Some(user_id)
    );
}

#[tokio::test]
#[ignore = "requer DATABASE_URL apontando para PostgreSQL de teste/desenvolvimento"]
async fn password_reset_is_silent_for_unknown_email() {
    let pool = test_pool().await;
    let sender = MockEmailSender::default();
    let state = test_state(pool, Some(Arc::new(sender.clone())));

    let status = reset_password(
        State(state),
        ConnectInfo(address(11)),
        Json(ResetPasswordRequest {
            email: unique_email("unknown"),
        }),
    )
    .await
    .unwrap();

    assert_eq!(status, StatusCode::NO_CONTENT);
    assert!(sender.messages.lock().await.is_empty());
}

#[tokio::test]
#[ignore = "requer DATABASE_URL apontando para PostgreSQL de teste/desenvolvimento"]
async fn password_reset_token_is_single_use_and_invalidates_old_sessions() {
    let pool = test_pool().await;
    let email = unique_email("reset");
    let user_id = usuarios_repository::create(&pool, "Reset Test", &email, "senha-antiga-segura")
        .await
        .unwrap();
    let old_session_id = auth_repository::create_session(&pool, user_id)
        .await
        .unwrap();
    let sender = MockEmailSender::default();
    let state = test_state(pool.clone(), Some(Arc::new(sender.clone())));

    let status = reset_password(
        State(state.clone()),
        ConnectInfo(address(12)),
        Json(ResetPasswordRequest {
            email: email.clone(),
        }),
    )
    .await
    .unwrap();
    assert_eq!(status, StatusCode::NO_CONTENT);

    let messages = sender.messages.lock().await;
    assert_eq!(messages.len(), 1);
    assert_eq!(messages[0].to, email);
    assert!(messages[0].html.contains("https://example.com/logo.png"));
    let token = extract_reset_token(&messages[0].html);
    drop(messages);

    let status = confirm_reset_password(
        State(state.clone()),
        Json(ConfirmResetPasswordRequest {
            token: token.clone(),
            new_password: "nova-senha-segura".to_owned(),
        }),
    )
    .await
    .unwrap();
    assert_eq!(status, StatusCode::NO_CONTENT);

    assert_eq!(
        auth_repository::find_user_id_by_session(&pool, &old_session_id)
            .await
            .unwrap(),
        None
    );

    let (status, Json(response)) = login(
        State(state.clone()),
        ConnectInfo(address(13)),
        Json(LoginRequest {
            email,
            password: "nova-senha-segura".to_owned(),
        }),
    )
    .await
    .unwrap();
    assert_eq!(status, StatusCode::CREATED);
    assert_eq!(response.user_id, user_id);

    let status = confirm_reset_password(
        State(state),
        Json(ConfirmResetPasswordRequest {
            token,
            new_password: "outra-senha-segura".to_owned(),
        }),
    )
    .await
    .unwrap();
    assert_eq!(status, StatusCode::UNAUTHORIZED);
}
