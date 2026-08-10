mod domains;
mod error;
mod infra;

use anyhow::{Context, Result};
use axum::{Router, routing::get};
use sqlx::postgres::PgPoolOptions;
use std::{
    collections::HashMap,
    env,
    net::{IpAddr, SocketAddr},
    sync::Arc,
    time::Instant,
};
use tokio::sync::Mutex;
use tower_http::trace::TraceLayer;
use tracing::info;

#[derive(Clone)]
pub struct AppState {
    pub db: sqlx::PgPool,
    pub internal_secret: Arc<str>,
    pub login_attempts: Arc<Mutex<HashMap<IpAddr, LoginAttemptWindow>>>,
}

#[derive(Default)]
pub struct LoginAttemptWindow {
    pub started_at: Option<Instant>,
    pub count: u32,
}

#[tokio::main]
async fn main() -> Result<()> {
    dotenvy::dotenv().ok();
    tracing_subscriber::fmt::init();

    let database_url = env::var("DATABASE_URL").context("DATABASE_URL não configurada")?;
    let internal_secret = env::var("INTERNAL_SECRET")
        .context("INTERNAL_SECRET não configurada")?
        .into();
    let bind_addr: SocketAddr = env::var("BIND_ADDR")
        .unwrap_or_else(|_| "0.0.0.0:3000".to_owned())
        .parse()
        .context("BIND_ADDR inválido")?;

    let db = PgPoolOptions::new()
        .max_connections(20)
        .connect(&database_url)
        .await
        .context("falha ao conectar ao PostgreSQL")?;
    sqlx::migrate!("./migrations")
        .run(&db)
        .await
        .context("falha ao executar migrations")?;

    let state = AppState {
        db,
        internal_secret,
        login_attempts: Arc::new(Mutex::new(HashMap::new())),
    };
    let app = Router::new()
        .route("/health", get(|| async { "ok" }))
        .merge(domains::auth::routes::router())
        .merge(domains::usuarios::routes::router())
        .with_state(state.clone())
        .layer(axum::middleware::from_fn_with_state(
            state,
            infra::hmac::verify_internal_request,
        ))
        .layer(TraceLayer::new_for_http());

    let listener = tokio::net::TcpListener::bind(bind_addr)
        .await
        .context("falha ao abrir listener HTTP")?;
    info!(%bind_addr, "backend iniciado");
    axum::serve(
        listener,
        app.into_make_service_with_connect_info::<SocketAddr>(),
    )
    .await
    .context("servidor HTTP encerrado com erro")?;
    Ok(())
}
