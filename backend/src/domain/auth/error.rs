use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum AuthDomainError {
    CredenciaisInvalidas,
    TokenRecuperacaoInvalido,
    TokenRecuperacaoAusente,
    SenhaInvalida(String),
    SessaoAusente,
    SessaoInvalidaOuExpirada,
    LimiteTentativasExcedido,
    EmailNaoConfigurado,
}

impl fmt::Display for AuthDomainError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::CredenciaisInvalidas => write!(f, "credenciais inválidas"),
            Self::TokenRecuperacaoInvalido => {
                write!(f, "token de recuperação inválido ou expirado")
            }
            Self::TokenRecuperacaoAusente => write!(f, "token de recuperação ausente"),
            Self::SenhaInvalida(msg) => write!(f, "senha inválida: {msg}"),
            Self::SessaoAusente => write!(f, "sessão ausente"),
            Self::SessaoInvalidaOuExpirada => write!(f, "sessão inválida ou expirada"),
            Self::LimiteTentativasExcedido => write!(f, "limite de tentativas excedido"),
            Self::EmailNaoConfigurado => write!(f, "serviço de e-mail não configurado"),
        }
    }
}

impl std::error::Error for AuthDomainError {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn formats_auth_domain_errors() {
        assert_eq!(
            AuthDomainError::CredenciaisInvalidas.to_string(),
            "credenciais inválidas"
        );
        assert_eq!(
            AuthDomainError::TokenRecuperacaoInvalido.to_string(),
            "token de recuperação inválido ou expirado"
        );
        assert_eq!(
            AuthDomainError::TokenRecuperacaoAusente.to_string(),
            "token de recuperação ausente"
        );
        assert_eq!(
            AuthDomainError::SenhaInvalida("curta".to_string()).to_string(),
            "senha inválida: curta"
        );
        assert_eq!(AuthDomainError::SessaoAusente.to_string(), "sessão ausente");
        assert_eq!(
            AuthDomainError::SessaoInvalidaOuExpirada.to_string(),
            "sessão inválida ou expirada"
        );
        assert_eq!(
            AuthDomainError::LimiteTentativasExcedido.to_string(),
            "limite de tentativas excedido"
        );
        assert_eq!(
            AuthDomainError::EmailNaoConfigurado.to_string(),
            "serviço de e-mail não configurado"
        );
    }
}
