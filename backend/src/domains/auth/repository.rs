use anyhow::{Context, Result};
use rand::RngCore;
use sqlx::PgPool;

pub struct LoginUser {
    pub id: i64,
    pub password_hash: Option<String>,
}

pub async fn find_user_by_email(pool: &PgPool, email: &str) -> Result<Option<LoginUser>> {
    sqlx::query_as!(
        LoginUser,
        r#"SELECT id, password_hash FROM usuarios WHERE email = $1"#,
        email
    )
    .fetch_optional(pool)
    .await
    .context("falha ao consultar credenciais")
}

pub async fn create_session(pool: &PgPool, user_id: i64) -> Result<String> {
    let mut bytes = [0_u8; 32];
    rand::rngs::OsRng.fill_bytes(&mut bytes);
    let session_id = hex::encode(bytes);

    sqlx::query!(
        r#"INSERT INTO sessoes (id, usuario_id, expires_at)
           VALUES ($1, $2, NOW() + INTERVAL '8 hours')"#,
        session_id,
        user_id
    )
    .execute(pool)
    .await
    .context("falha ao criar sessão")?;
    Ok(session_id)
}

pub async fn find_user_id_by_session(pool: &PgPool, session_id: &str) -> Result<Option<i64>> {
    let session = sqlx::query!(
        r#"WITH renewed AS (
               UPDATE sessoes
               SET expires_at = LEAST(
                   NOW() + INTERVAL '8 hours',
                   created_at + INTERVAL '24 hours'
               )
               WHERE id = $1
                 AND expires_at > NOW()
                 AND expires_at <= NOW() + INTERVAL '30 minutes'
               RETURNING usuario_id
           )
           SELECT usuario_id FROM renewed
           UNION ALL
           SELECT usuario_id FROM sessoes
           WHERE id = $1 AND expires_at > NOW()
           LIMIT 1"#,
        session_id
    )
    .fetch_optional(pool)
    .await
    .context("falha ao consultar sessão")?;
    Ok(session.and_then(|row| row.usuario_id))
}

pub async fn delete_session(pool: &PgPool, session_id: &str) -> Result<()> {
    sqlx::query!("DELETE FROM sessoes WHERE id = $1", session_id)
        .execute(pool)
        .await
        .context("falha ao encerrar sessão")?;
    Ok(())
}
