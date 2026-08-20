use anyhow::{Context, Result};
use std::{env, net::SocketAddr, sync::Arc};

#[derive(Debug, Clone)]
pub struct AppConfig {
    pub database_url: String,
    pub internal_secret: Arc<str>,
    pub public_app_url: Arc<str>,
    pub email_logo_url: Option<Arc<str>>,
    pub bind_addr: SocketAddr,
}

impl AppConfig {
    pub fn from_env() -> Result<Self> {
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

        Ok(Self {
            database_url,
            internal_secret,
            public_app_url,
            email_logo_url,
            bind_addr,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_config_from_env_or_defaults() {
        unsafe {
            env::set_var("DATABASE_URL", "postgres://localhost/test_db");
            env::set_var("INTERNAL_SECRET", "super-secret");
        }

        let config = AppConfig::from_env();
        assert!(config.is_ok());
        let c = config.unwrap();
        assert_eq!(c.database_url, "postgres://localhost/test_db");
        assert_eq!(c.internal_secret.as_ref(), "super-secret");
        assert_eq!(c.public_app_url.as_ref(), "http://localhost:5173");
        assert_eq!(c.bind_addr.to_string(), "0.0.0.0:3000");
    }
}

