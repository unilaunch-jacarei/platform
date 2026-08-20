use async_trait::async_trait;
use axum::{
    Json,
    extract::{ConnectInfo, State},
    http::StatusCode,
};
use backend::{
    AppState,
    adapters::{
        inbound::http::auth::{
            dto::{ConfirmResetPasswordRequest, LoginRequest, ResetPasswordRequest},
            handlers::{confirm_reset_password, login, reset_password},
        },
        outbound::{
            persistence::postgres::{PostgresAuthRepository, PostgresUsuarioRepository},
            rate_limiter::MemoryRateLimiter,
            security::{Argon2PasswordHasher, CryptoTokenGenerator},
        },
    },
    application::{
        auth::ports::{AuthRepository, EmailMessage, EmailSenderPort, PasswordHasher, SessionIdGenerator},
        usuarios::ports::UsuarioRepository,
    },
    bootstrap::create_app_state,
    domain::usuarios::{Email, Nome, PlainPassword},
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
impl EmailSenderPort for MockEmailSender {
    async fn send(&self, message: EmailMessage) -> Result<String, String> {
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

fn test_state(pool: PgPool, email_sender: Option<Arc<dyn EmailSenderPort>>) -> AppState {
    let usuario_repo = Arc::new(PostgresUsuarioRepository::new(pool.clone()));
    let auth_repo = Arc::new(PostgresAuthRepository::new(pool));
    let password_hasher = Arc::new(Argon2PasswordHasher::new());
    let crypto_generator = Arc::new(CryptoTokenGenerator::new());
    let rate_limiter = Arc::new(MemoryRateLimiter::new());

    create_app_state(
        usuario_repo,
        auth_repo,
        password_hasher,
        rate_limiter,
        crypto_generator.clone(),
        crypto_generator,
        email_sender,
        Arc::from("test-secret"),
        Arc::from("http://localhost:5173"),
        Some(Arc::from("https://example.com/logo.png")),
    )
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
    let usuario_repo = PostgresUsuarioRepository::new(pool.clone());
    let auth_repo = PostgresAuthRepository::new(pool.clone());
    let password_hasher = Argon2PasswordHasher::new();

    let email = unique_email("login");
    let hashed_pw = password_hasher
        .hash(&PlainPassword::new("senha-antiga-segura").unwrap())
        .unwrap();

    let user_id = usuario_repo
        .create(
            &Nome::new("Login Test").unwrap(),
            &Email::new(&email).unwrap(),
            &hashed_pw,
        )
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
    assert_eq!(response.user_id, user_id.value());
    assert_eq!(response.session_id.len(), 64);
    assert_eq!(
        auth_repo
            .find_user_id_by_session(&backend::domain::auth::SessionId::new(&response.session_id).unwrap())
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
    let usuario_repo = PostgresUsuarioRepository::new(pool.clone());
    let auth_repo = PostgresAuthRepository::new(pool.clone());
    let password_hasher = Argon2PasswordHasher::new();
    let crypto_generator = CryptoTokenGenerator::new();

    let email = unique_email("reset");
    let hashed_pw = password_hasher
        .hash(&PlainPassword::new("senha-antiga-segura").unwrap())
        .unwrap();

    let user_id = usuario_repo
        .create(
            &Nome::new("Reset Test").unwrap(),
            &Email::new(&email).unwrap(),
            &hashed_pw,
        )
        .await
        .unwrap();

    let old_session_id = crypto_generator.generate();
    auth_repo
        .create_session(user_id, &old_session_id)
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
        auth_repo
            .find_user_id_by_session(&old_session_id)
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
    assert_eq!(response.user_id, user_id.value());

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
