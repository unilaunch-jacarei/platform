use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum UsuarioDomainError {
    CamposObrigatorios,
    SenhaCurta,
    EmailInvalido(String),
    NomeVazio,
}

impl fmt::Display for UsuarioDomainError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::CamposObrigatorios => write!(f, "nome, email e senha são obrigatórios"),
            Self::SenhaCurta => write!(f, "senha deve possuir no mínimo 8 caracteres"),
            Self::EmailInvalido(email) => write!(f, "email inválido: {email}"),
            Self::NomeVazio => write!(f, "nome não pode ser vazio"),
        }
    }
}

impl std::error::Error for UsuarioDomainError {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn formats_errors_correctly() {
        assert_eq!(
            UsuarioDomainError::CamposObrigatorios.to_string(),
            "nome, email e senha são obrigatórios"
        );
        assert_eq!(
            UsuarioDomainError::SenhaCurta.to_string(),
            "senha deve possuir no mínimo 8 caracteres"
        );
        assert_eq!(
            UsuarioDomainError::EmailInvalido("bad".to_string()).to_string(),
            "email inválido: bad"
        );
        assert_eq!(
            UsuarioDomainError::NomeVazio.to_string(),
            "nome não pode ser vazio"
        );
    }
}

