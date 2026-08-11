use anyhow::{Context, Result, bail};
use async_trait::async_trait;
use reqwest::Client;
use serde::{Deserialize, Serialize};

const RESEND_API_URL: &str = "https://api.resend.com/emails";

#[derive(Debug, Clone)]
pub struct EmailMessage {
    pub to: String,
    pub subject: String,
    pub html: String,
    pub text: Option<String>,
}

#[async_trait]
pub trait EmailSender: Send + Sync {
    async fn send(&self, message: EmailMessage) -> Result<String>;
}

#[derive(Clone)]
pub struct ResendEmailSender {
    client: Client,
    api_key: String,
    from: String,
}

impl ResendEmailSender {
    pub fn new(client: Client, api_key: String, from: String) -> Self {
        Self {
            client,
            api_key,
            from,
        }
    }

    pub fn from_env() -> Result<Self> {
        let api_key = std::env::var("RESEND_API_KEY").context("RESEND_API_KEY não configurada")?;
        let from = std::env::var("MAIL_FROM").context("MAIL_FROM não configurado")?;

        if api_key.trim().is_empty() || from.trim().is_empty() {
            bail!("RESEND_API_KEY e MAIL_FROM não podem ser vazios");
        }

        Ok(Self::new(Client::new(), api_key, from))
    }
}

#[derive(Debug, Serialize)]
struct ResendRequest<'a> {
    from: &'a str,
    to: [&'a str; 1],
    subject: &'a str,
    html: &'a str,
    #[serde(skip_serializing_if = "Option::is_none")]
    text: Option<&'a str>,
}

#[derive(Debug, Deserialize)]
struct ResendResponse {
    id: String,
}

#[async_trait]
impl EmailSender for ResendEmailSender {
    async fn send(&self, message: EmailMessage) -> Result<String> {
        let request = ResendRequest {
            from: &self.from,
            to: [&message.to],
            subject: &message.subject,
            html: &message.html,
            text: message.text.as_deref(),
        };

        let response = self
            .client
            .post(RESEND_API_URL)
            .bearer_auth(&self.api_key)
            .json(&request)
            .send()
            .await
            .context("falha ao comunicar com o Resend")?;

        let status = response.status();
        let body = response
            .text()
            .await
            .context("falha ao ler resposta do Resend")?;

        if !status.is_success() {
            bail!("Resend retornou HTTP {status}: {body}");
        }

        serde_json::from_str::<ResendResponse>(&body)
            .context("resposta inválida recebida do Resend")
            .map(|response| response.id)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn serializes_resend_payload_with_optional_text() {
        let request = ResendRequest {
            from: "UniLaunch <noreply@stackvize.org>",
            to: ["ana@example.com"],
            subject: "Recuperação de senha",
            html: "<strong>Olá</strong>",
            text: Some("Olá"),
        };

        assert_eq!(
            serde_json::to_value(request).unwrap(),
            json!({
                "from": "UniLaunch <noreply@stackvize.org>",
                "to": ["ana@example.com"],
                "subject": "Recuperação de senha",
                "html": "<strong>Olá</strong>",
                "text": "Olá"
            })
        );
    }

    #[test]
    fn omits_text_when_plain_version_is_absent() {
        let request = ResendRequest {
            from: "UniLaunch <noreply@stackvize.org>",
            to: ["ana@example.com"],
            subject: "Recuperação de senha",
            html: "<strong>Olá</strong>",
            text: None,
        };

        let value = serde_json::to_value(request).unwrap();
        assert!(value.get("text").is_none());
    }
}
