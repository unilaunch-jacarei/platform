use super::error::AuthAppError;
use super::ports::{
    AuthRepository, EmailMessage, EmailSenderPort, RateLimitOperation, RateLimiterPort,
    ResetTokenGenerator,
};
use crate::domain::auth::AuthDomainError;
use crate::domain::usuarios::Email;
use std::net::IpAddr;
use std::sync::Arc;
use std::time::Duration;

pub struct RequestPasswordResetCommand {
    pub email: String,
    pub ip: IpAddr,
}

pub struct RequestPasswordResetUseCase {
    auth_repository: Arc<dyn AuthRepository>,
    email_sender: Option<Arc<dyn EmailSenderPort>>,
    rate_limiter: Arc<dyn RateLimiterPort>,
    token_generator: Arc<dyn ResetTokenGenerator>,
    public_app_url: Arc<str>,
    email_logo_url: Option<Arc<str>>,
}

impl RequestPasswordResetUseCase {
    pub fn new(
        auth_repository: Arc<dyn AuthRepository>,
        email_sender: Option<Arc<dyn EmailSenderPort>>,
        rate_limiter: Arc<dyn RateLimiterPort>,
        token_generator: Arc<dyn ResetTokenGenerator>,
        public_app_url: Arc<str>,
        email_logo_url: Option<Arc<str>>,
    ) -> Self {
        Self {
            auth_repository,
            email_sender,
            rate_limiter,
            token_generator,
            public_app_url,
            email_logo_url,
        }
    }

    pub async fn execute(&self, cmd: RequestPasswordResetCommand) -> Result<(), AuthAppError> {
        let allowed = self
            .rate_limiter
            .is_allowed(
                cmd.ip,
                RateLimitOperation::ResetPassword,
                Duration::from_secs(60 * 60),
                3,
            )
            .await;

        if !allowed {
            return Err(AuthAppError::Domain(AuthDomainError::LimiteTentativasExcedido));
        }

        let Ok(email) = Email::new(cmd.email.clone()) else {
            // Silencioso se o e-mail não for válido para não vazar informações
            return Ok(());
        };

        if let Some(usuario) = self.auth_repository.find_user_by_email(&email).await? {
            let email_sender = self
                .email_sender
                .as_ref()
                .ok_or(AuthAppError::Domain(AuthDomainError::EmailNaoConfigurado))?;

            let (raw_token, token_hash) = self.token_generator.generate();
            self.auth_repository
                .create_password_reset(usuario.id, &token_hash)
                .await?;

            let reset_url = format!(
                "{}/reset-password?token={}",
                self.public_app_url.trim_end_matches('/'),
                raw_token.as_str()
            );

            let logo = self
                .email_logo_url
                .as_deref()
                .map(|url| {
                    format!(
                        r#"<img src="{url}" alt="UniLaunch" width="180" style="display:block;width:180px;max-width:100%;height:auto;margin:0 auto 24px;border:0;">"#
                    )
                })
                .unwrap_or_default();

            let message = EmailMessage {
                to: email.into_string(),
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
            };

            email_sender
                .send(message)
                .await
                .map_err(AuthAppError::Internal)?;
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::application::usuarios::ports::RepositoryError;
    use crate::domain::auth::{RawResetToken, ResetTokenHash, SessionId};
    use crate::domain::usuarios::{HashedPassword, Nome, Usuario, UsuarioId};
    use async_trait::async_trait;
    use std::sync::Mutex;

    struct FakeAuthRepository {
        user: Option<Usuario>,
        created_resets: Mutex<Vec<(UsuarioId, ResetTokenHash)>>,
    }

    #[async_trait]
    impl AuthRepository for FakeAuthRepository {
        async fn find_user_by_email(&self, email: &Email) -> Result<Option<Usuario>, RepositoryError> {
            Ok(self.user.clone().filter(|u| &u.email == email))
        }

        async fn create_session(&self, _user_id: UsuarioId, _session_id: &SessionId) -> Result<(), RepositoryError> {
            Ok(())
        }

        async fn find_user_id_by_session(&self, _session_id: &SessionId) -> Result<Option<UsuarioId>, RepositoryError> {
            Ok(None)
        }

        async fn delete_session(&self, _session_id: &SessionId) -> Result<(), RepositoryError> {
            Ok(())
        }

        async fn create_password_reset(&self, user_id: UsuarioId, token_hash: &ResetTokenHash) -> Result<(), RepositoryError> {
            self.created_resets.lock().unwrap().push((user_id, token_hash.clone()));
            Ok(())
        }

        async fn consume_password_reset(&self, _token_hash: &ResetTokenHash, _password_hash: &HashedPassword) -> Result<bool, RepositoryError> {
            Ok(true)
        }
    }

    #[derive(Default)]
    struct FakeEmailSender {
        sent_messages: Mutex<Vec<EmailMessage>>,
    }

    #[async_trait]
    impl EmailSenderPort for FakeEmailSender {
        async fn send(&self, message: EmailMessage) -> Result<String, String> {
            self.sent_messages.lock().unwrap().push(message);
            Ok("fake-msg-id".to_string())
        }
    }

    struct FakeRateLimiter {
        allowed: bool,
    }

    #[async_trait]
    impl RateLimiterPort for FakeRateLimiter {
        async fn is_allowed(&self, _ip: IpAddr, _op: RateLimitOperation, _window: Duration, _max: u32) -> bool {
            self.allowed
        }

        async fn reset(&self, _ip: IpAddr, _op: RateLimitOperation) {}
    }

    struct FakeTokenGenerator;

    impl ResetTokenGenerator for FakeTokenGenerator {
        fn generate(&self) -> (RawResetToken, ResetTokenHash) {
            (
                RawResetToken::new("raw-token-123").unwrap(),
                ResetTokenHash::new("hash-token-123"),
            )
        }

        fn hash_token(&self, raw: &RawResetToken) -> ResetTokenHash {
            ResetTokenHash::new(format!("hash_{}", raw.as_str()))
        }
    }

    fn test_ip() -> IpAddr {
        "127.0.0.1".parse().unwrap()
    }

    #[tokio::test]
    async fn sends_reset_email_when_user_exists() {
        let user = Usuario::new(
            UsuarioId::new(42),
            Nome::new("Beatriz").unwrap(),
            Email::new("beatriz@example.com").unwrap(),
            None,
        );
        let repo = Arc::new(FakeAuthRepository {
            user: Some(user),
            created_resets: Mutex::new(Vec::new()),
        });
        let email_sender = Arc::new(FakeEmailSender::default());
        let limiter = Arc::new(FakeRateLimiter { allowed: true });
        let token_gen = Arc::new(FakeTokenGenerator);

        let use_case = RequestPasswordResetUseCase::new(
            repo.clone(),
            Some(email_sender.clone()),
            limiter,
            token_gen,
            Arc::from("https://app.test"),
            Some(Arc::from("https://app.test/logo.png")),
        );

        let result = use_case
            .execute(RequestPasswordResetCommand {
                email: "beatriz@example.com".to_string(),
                ip: test_ip(),
            })
            .await;

        assert!(result.is_ok());
        assert_eq!(repo.created_resets.lock().unwrap().len(), 1);
        let sent = email_sender.sent_messages.lock().unwrap();
        assert_eq!(sent.len(), 1);
        assert_eq!(sent[0].to, "beatriz@example.com");
        assert!(sent[0].html.contains("https://app.test/reset-password?token=raw-token-123"));
    }

    #[tokio::test]
    async fn is_silent_when_user_does_not_exist() {
        let repo = Arc::new(FakeAuthRepository {
            user: None,
            created_resets: Mutex::new(Vec::new()),
        });
        let email_sender = Arc::new(FakeEmailSender::default());
        let limiter = Arc::new(FakeRateLimiter { allowed: true });
        let token_gen = Arc::new(FakeTokenGenerator);

        let use_case = RequestPasswordResetUseCase::new(
            repo.clone(),
            Some(email_sender.clone()),
            limiter,
            token_gen,
            Arc::from("https://app.test"),
            None,
        );

        let result = use_case
            .execute(RequestPasswordResetCommand {
                email: "inexistente@example.com".to_string(),
                ip: test_ip(),
            })
            .await;

        assert!(result.is_ok());
        assert_eq!(repo.created_resets.lock().unwrap().len(), 0);
        assert_eq!(email_sender.sent_messages.lock().unwrap().len(), 0);
    }
}

