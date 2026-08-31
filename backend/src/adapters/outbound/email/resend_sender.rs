use crate::application::auth::ports::{EmailMessage, EmailSenderPort};
use async_trait::async_trait;
use reqwest::Client;
use serde::{Deserialize, Serialize};

const RESEND_API_URL: &str = "https://api.resend.com/emails";

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

    pub fn from_env() -> Result<Self, String> {
        let api_key = std::env::var("RESEND_API_KEY")
            .map_err(|_| "RESEND_API_KEY não configurada".to_string())?;
        let from =
            std::env::var("MAIL_FROM").map_err(|_| "MAIL_FROM não configurado".to_string())?;

        if api_key.trim().is_empty() || from.trim().is_empty() {
            return Err("RESEND_API_KEY e MAIL_FROM não podem ser vazios".to_string());
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
impl EmailSenderPort for ResendEmailSender {
    async fn send(&self, message: EmailMessage) -> Result<String, String> {
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
            .map_err(|e| format!("falha ao comunicar com o Resend: {e}"))?;

        let status = response.status();
        let body = response
            .text()
            .await
            .map_err(|e| format!("falha ao ler resposta do Resend: {e}"))?;

        if !status.is_success() {
            return Err(format!("Resend retornou HTTP {status}: {body}"));
        }

        let parsed = serde_json::from_str::<ResendResponse>(&body)
            .map_err(|e| format!("resposta inválida recebida do Resend: {e}"))?;

        Ok(parsed.id)
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
