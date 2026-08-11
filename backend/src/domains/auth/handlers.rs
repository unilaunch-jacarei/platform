use super::repository;
use crate::{
    AppState,
    error::AppError,
    infra::{email::EmailMessage, password::verify_password, rate_limiter::RateLimitOperation},
};
use anyhow::{Context, anyhow};
use axum::{
    extract::{ConnectInfo, State},
    http::{Extensions, StatusCode},
    response::Json,
};
use rand::RngCore;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{net::SocketAddr, time::Duration};

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

#[derive(Debug, Deserialize)]
pub struct ResetPasswordRequest {
    pub email: String,
}

#[derive(Debug, Deserialize)]
pub struct ConfirmResetPasswordRequest {
    pub token: String,
    pub new_password: String,
}

pub async fn login(
    State(state): State<AppState>,
    ConnectInfo(address): ConnectInfo<SocketAddr>,
    Json(input): Json<LoginRequest>,
) -> Result<(StatusCode, Json<LoginResponse>), AppError> {
    if !state
        .rate_limiter
        .is_allowed(
            address.ip().clone(),
            RateLimitOperation::Login,
            Duration::from_mins(60),
            5,
        )
        .await
    {
        return Err(anyhow!("limite de tentativas excedido").into());
    }

    let user = repository::find_user_by_email(&state.db, &input.email)
        .await?
        .ok_or_else(|| anyhow!("credenciais inválidas"))?;
    let Some(password_hash) = user.password_hash else {
        return Err(anyhow!("credenciais inválidas").into());
    };
    if !verify_password(&input.password, &password_hash)? {
        return Err(anyhow!("credenciais inválidas").into());
    }

    state
        .rate_limiter
        .reset(address.ip().clone(), RateLimitOperation::Login)
        .await;

    let session_id = repository::create_session(&state.db, user.id).await?;
    Ok((
        StatusCode::CREATED,
        Json(LoginResponse {
            session_id,
            user_id: user.id,
        }),
    ))
}

pub async fn session(
    State(state): State<AppState>,
    extensions: Extensions,
) -> Result<Json<serde_json::Value>, AppError> {
    let session_id = extensions
        .get::<String>()
        .ok_or_else(|| anyhow!("sessão ausente"))?;
    let user_id = repository::find_user_id_by_session(&state.db, session_id)
        .await?
        .ok_or_else(|| anyhow!("sessão inválida ou expirada"))?;
    Ok(Json(serde_json::json!({ "user_id": user_id })))
}

pub async fn logout(
    State(state): State<AppState>,
    extensions: Extensions,
) -> Result<StatusCode, AppError> {
    let session_id = extensions
        .get::<String>()
        .ok_or_else(|| anyhow!("sessão ausente"))?;
    repository::delete_session(&state.db, session_id).await?;
    Ok(StatusCode::NO_CONTENT)
}

pub async fn confirm_reset_password(
    State(state): State<AppState>,
    Json(input): Json<ConfirmResetPasswordRequest>,
) -> Result<StatusCode, AppError> {
    if validate_confirm_reset_password(&input).is_err() {
        return Ok(StatusCode::BAD_REQUEST);
    }

    let token_hash = hex::encode(Sha256::digest(input.token.as_bytes()));
    let password_hash = crate::infra::password::hash_password(&input.new_password)?;
    let consumed =
        repository::consume_password_reset(&state.db, &token_hash, &password_hash).await?;

    if consumed {
        Ok(StatusCode::NO_CONTENT)
    } else {
        Ok(StatusCode::UNAUTHORIZED)
    }
}

pub async fn reset_password(
    State(state): State<AppState>,
    ConnectInfo(address): ConnectInfo<SocketAddr>,
    Json(input): Json<ResetPasswordRequest>,
) -> Result<StatusCode, AppError> {
    if !state
        .rate_limiter
        .is_allowed(
            address.ip(),
            RateLimitOperation::ResetPassword,
            Duration::from_mins(60),
            3,
        )
        .await
    {
        return Err(anyhow!("limite de solicitações excedido").into());
    }

    if let Some(usuario) = repository::find_user_by_email(&state.db, &input.email).await? {
        let email_sender = state
            .email_sender
            .as_ref()
            .ok_or_else(|| anyhow!("serviço de e-mail não configurado"))?;
        let mut token_bytes = [0_u8; 32];
        rand::rngs::OsRng.fill_bytes(&mut token_bytes);
        let raw_token = hex::encode(token_bytes);
        let token_hash = hex::encode(Sha256::digest(raw_token.as_bytes()));

        repository::create_password_reset(&state.db, usuario.id, token_hash).await?;

        let reset_url = format!(
            "{}/reset-password?token={raw_token}",
            state.public_app_url.trim_end_matches('/')
        );
        let logo = state
            .email_logo_url
            .as_deref()
            .map(|url| {
                format!(
                    r#"<img src="{url}" alt="UniLaunch" width="180" style="display:block;width:180px;max-width:100%;height:auto;margin:0 auto 24px;border:0;">"#
                )
            })
            .unwrap_or_default();
        email_sender
            .send(EmailMessage {
                to: input.email,
                subject: "Recuperação de senha — UniLaunch".to_owned(),
                html: format!(
                    r##"<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Recuperação de senha</title>
  </head>
  <body style="margin:0;background:#f4f7fb;color:#172033;font-family:Arial,Helvetica,sans-serif;">
    <div style="display:none;max-height:0;overflow:hidden;opacity:0;">
      Crie uma nova senha para acessar sua conta UniLaunch.
    </div>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:#f4f7fb;">
      <tr>
        <td align="center" style="padding:40px 16px;">
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width:560px;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 8px 30px rgba(23,32,51,.08);">
            <tr>
              <td style="height:6px;background:#2563eb;font-size:0;line-height:0;">&nbsp;</td>
            </tr>
            <tr>
              <td style="padding:40px 40px 16px;text-align:center;">
                {logo}
                <div style="font-size:24px;font-weight:700;letter-spacing:-.3px;color:#172033;">Recuperação de senha</div>
              </td>
            </tr>
            <tr>
              <td style="padding:8px 40px 40px;font-size:16px;line-height:1.65;color:#526078;">
                <p style="margin:0 0 18px;">Olá,</p>
                <p style="margin:0 0 24px;">Recebemos uma solicitação para redefinir a senha da sua conta no UniLaunch.</p>
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                  <tr>
                    <td align="center" style="padding:8px 0 28px;">
                      <a href="{reset_url}" style="display:inline-block;background:#2563eb;color:#ffffff;text-decoration:none;font-size:16px;font-weight:700;border-radius:9px;padding:14px 28px;">Redefinir minha senha</a>
                    </td>
                  </tr>
                </table>
                <p style="margin:0 0 12px;font-size:14px;">Este link expira em <strong>1 hora</strong> e pode ser usado uma única vez.</p>
                <p style="margin:0;font-size:14px;">Se você não solicitou essa alteração, ignore este e-mail. Sua senha permanecerá a mesma.</p>
                <hr style="border:0;border-top:1px solid #e7ebf2;margin:28px 0 20px;">
                <p style="margin:0;font-size:12px;line-height:1.6;color:#8994a8;">Se o botão não funcionar, copie e cole este endereço no navegador:<br><span style="word-break:break-all;color:#2563eb;">{reset_url}</span></p>
              </td>
            </tr>
          </table>
          <p style="margin:22px 0 0;font-size:12px;color:#8994a8;text-align:center;">© UniLaunch Platform</p>
        </td>
      </tr>
    </table>
  </body>
</html>"##
                ),
                text: Some(format!(
                    "Olá,\n\n\
                     Recebemos uma solicitação para redefinir sua senha no UniLaunch.\n\n\
                     Redefina sua senha pelo link:\n{reset_url}\n\n\
                     Este link expira em 1 hora e pode ser usado uma única vez.\n\n\
                     Se você não solicitou essa alteração, ignore este e-mail."
                )),
            })
            .await
            .context("falha ao enviar e-mail de recuperação")?;
    }

    Ok(StatusCode::NO_CONTENT)
}

fn validate_confirm_reset_password(input: &ConfirmResetPasswordRequest) -> anyhow::Result<()> {
    if input.token.trim().is_empty() {
        anyhow::bail!("token de recuperação ausente");
    }
    if input.new_password.len() < 8 {
        anyhow::bail!("senha deve possuir no mínimo 8 caracteres");
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn valid_confirm_input() -> ConfirmResetPasswordRequest {
        ConfirmResetPasswordRequest {
            token: "token-valido".to_owned(),
            new_password: "senha-segura".to_owned(),
        }
    }

    #[test]
    fn validates_password_reset_confirmation_input() {
        assert!(validate_confirm_reset_password(&valid_confirm_input()).is_ok());

        let mut input = valid_confirm_input();
        input.token = "  ".to_owned();
        assert!(validate_confirm_reset_password(&input).is_err());

        let mut input = valid_confirm_input();
        input.new_password = "1234567".to_owned();
        assert!(validate_confirm_reset_password(&input).is_err());
    }
}
