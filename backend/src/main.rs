use anyhow::{Context, Result};
use backend::bootstrap::{AppConfig, build_app};
use std::net::SocketAddr;
use tracing::info;

#[tokio::main]
async fn main() -> Result<()> {
    dotenvy::dotenv().ok();
    let log_level = std::env::var("LOG_LEVEL")
        .or_else(|_| std::env::var("RUST_LOG"))
        .unwrap_or_else(|_| "info".to_string());
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| tracing_subscriber::EnvFilter::new(log_level)),
        )
        .init();

    let config = AppConfig::from_env()?;
    let bind_addr = config.bind_addr;
    let app = build_app(config).await?;

    let listener = tokio::net::TcpListener::bind(bind_addr)
        .await
        .context("falha ao abrir listener HTTP")?;

    info!(%bind_addr, "backend iniciado");

    axum::serve(
        listener,
        app.router.into_make_service_with_connect_info::<SocketAddr>(),
    )
    .await
    .context("servidor HTTP encerrado com erro")?;

    Ok(())
}
