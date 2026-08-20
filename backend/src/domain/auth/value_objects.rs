use super::error::AuthDomainError;

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct SessionId(String);

impl SessionId {
    pub fn new(id: impl Into<String>) -> Result<Self, AuthDomainError> {
        let s = id.into();
        let trimmed = s.trim();
        if trimmed.is_empty() {
            return Err(AuthDomainError::SessaoAusente);
        }
        Ok(Self(trimmed.to_string()))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }

    pub fn into_string(self) -> String {
        self.0
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RawResetToken(String);

impl RawResetToken {
    pub fn new(token: impl Into<String>) -> Result<Self, AuthDomainError> {
        let t = token.into();
        let trimmed = t.trim();
        if trimmed.is_empty() {
            return Err(AuthDomainError::TokenRecuperacaoAusente);
        }
        Ok(Self(trimmed.to_string()))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }

    pub fn into_string(self) -> String {
        self.0
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ResetTokenHash(String);

impl ResetTokenHash {
    pub fn new(hash: impl Into<String>) -> Self {
        Self(hash.into())
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }

    pub fn into_string(self) -> String {
        self.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn validates_session_id() {
        assert!(SessionId::new("valid-session-123").is_ok());
        assert_eq!(
            SessionId::new("   ").unwrap_err(),
            AuthDomainError::SessaoAusente
        );
        let s = SessionId::new("my-session").unwrap();
        assert_eq!(s.as_str(), "my-session");
        assert_eq!(s.into_string(), "my-session");
    }

    #[test]
    fn validates_raw_reset_token() {
        assert!(RawResetToken::new("token-123").is_ok());
        assert_eq!(
            RawResetToken::new("").unwrap_err(),
            AuthDomainError::TokenRecuperacaoAusente
        );
        let t = RawResetToken::new("raw-token").unwrap();
        assert_eq!(t.as_str(), "raw-token");
        assert_eq!(t.into_string(), "raw-token");
    }

    #[test]
    fn creates_reset_token_hash() {
        let hash = ResetTokenHash::new("hash-value");
        assert_eq!(hash.as_str(), "hash-value");
        assert_eq!(hash.into_string(), "hash-value");
    }
}

