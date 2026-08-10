use super::models::UsuarioDb;
use crate::infra::password::hash_password;
use anyhow::{Context, Result};
use sqlx::PgPool;

pub async fn find_by_id(pool: &PgPool, id: i64) -> Result<Option<UsuarioDb>> {
    sqlx::query_as!(
        UsuarioDb,
        r#"SELECT id, nome, email FROM usuarios WHERE id = $1"#,
        id
    )
    .fetch_optional(pool)
    .await
    .context("falha ao consultar usuário")
}

pub async fn create(pool: &PgPool, nome: &str, email: &str, password: &str) -> Result<i64> {
    let password_hash = hash_password(password)?;
    let result = sqlx::query!(
        r#"INSERT INTO usuarios (nome, email, password_hash)
           VALUES ($1, $2, $3)
           RETURNING id"#,
        nome,
        email,
        password_hash
    )
    .fetch_one(pool)
    .await
    .context("falha ao criar usuário")?;
    Ok(result.id)
}
