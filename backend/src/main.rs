use anyhow::{Context, Result};
use backend::{
    AppState, build_app,
    infra::{email::ResendEmailSender, rate_limiter::RateLimiter},
};
use sqlx::postgres::PgPoolOptions;
use std::{env, net::SocketAddr, sync::Arc};
use tracing::{info, warn};

#[tokio::main]
async fn main() -> Result<()> {
    dotenvy::dotenv().ok();
    tracing_subscriber::fmt::init();

    let database_url = env::var("DATABASE_URL").context("DATABASE_URL não configurada")?;
    let internal_secret = env::var("INTERNAL_SECRET")
        .context("INTERNAL_SECRET não configurada")?
        .into();
    let public_app_url = env::var("PUBLIC_APP_URL")
        .unwrap_or_else(|_| "http://localhost:5173".to_owned())
        .into();
    let email_logo_url = env::var("EMAIL_LOGO_URL").ok().map(Arc::from);
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
        rate_limiter: Arc::new(RateLimiter::new()),
        email_sender: match ResendEmailSender::from_env() {
            Ok(sender) => Some(Arc::new(sender)),
            Err(error) => {
                warn!(
                    ?error,
                    "Resend não configurado; recuperação de senha ficará indisponível"
                );
                None
            }
        },
        public_app_url,
        email_logo_url,
    };
    let app = build_app(state);

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
