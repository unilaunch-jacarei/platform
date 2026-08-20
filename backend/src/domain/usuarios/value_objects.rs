use super::error::UsuarioDomainError;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct UsuarioId(pub i64);

impl UsuarioId {
    pub fn new(id: i64) -> Self {
        Self(id)
    }

    pub fn value(&self) -> i64 {
        self.0
    }
}

impl From<i64> for UsuarioId {
    fn from(id: i64) -> Self {
        Self(id)
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Nome(String);

impl Nome {
    pub fn new(raw: impl Into<String>) -> Result<Self, UsuarioDomainError> {
        let raw = raw.into();
        let trimmed = raw.trim();
        if trimmed.is_empty() {
            return Err(UsuarioDomainError::NomeVazio);
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
pub struct Email(String);

impl Email {
    pub fn new(raw: impl Into<String>) -> Result<Self, UsuarioDomainError> {
        let raw = raw.into();
        let trimmed = raw.trim().to_lowercase();
        if trimmed.is_empty() || !trimmed.contains('@') {
            return Err(UsuarioDomainError::EmailInvalido(trimmed));
        }
        Ok(Self(trimmed))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }

    pub fn into_string(self) -> String {
        self.0
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PlainPassword(String);

impl PlainPassword {
    pub fn new(raw: impl Into<String>) -> Result<Self, UsuarioDomainError> {
        let raw = raw.into();
        if raw.is_empty() {
            return Err(UsuarioDomainError::CamposObrigatorios);
        }
        if raw.chars().count() < 8 {
            return Err(UsuarioDomainError::SenhaCurta);
        }
        Ok(Self(raw))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }

    pub fn into_string(self) -> String {
        self.0
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct HashedPassword(String);

impl HashedPassword {
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
    fn validates_email() {
        assert!(Email::new("test@example.com").is_ok());
        assert!(Email::new("invalid-email").is_err());
        assert!(Email::new("").is_err());
    }

    #[test]
    fn validates_password() {
        assert!(PlainPassword::new("12345678").is_ok());
        assert_eq!(
            PlainPassword::new("1234567").unwrap_err(),
            UsuarioDomainError::SenhaCurta
        );
    }
}
