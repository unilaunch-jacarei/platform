use crate::domain::usuarios::{Email, HashedPassword, Nome, Usuario, UsuarioId};

#[derive(Debug)]
pub struct PostgresUserModel {
    pub id: i64,
    pub nome: String,
    pub email: String,
    pub password_hash: Option<String>,
}

impl PostgresUserModel {
    pub fn try_into_domain(self) -> Result<Usuario, String> {
        let nome = Nome::new(self.nome).map_err(|e| e.to_string())?;
        let email = Email::new(self.email).map_err(|e| e.to_string())?;
        let password_hash = self.password_hash.map(HashedPassword::new);

        Ok(Usuario::new(
            UsuarioId::new(self.id),
            nome,
            email,
            password_hash,
        ))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn converts_valid_postgres_model_to_domain_entity() {
        let model = PostgresUserModel {
            id: 1,
            nome: "Lucas".to_string(),
            email: "lucas@example.com".to_string(),
            password_hash: Some("hashed-password-123".to_string()),
        };

        let domain = model.try_into_domain();
        assert!(domain.is_ok());
        let user = domain.unwrap();
        assert_eq!(user.id.value(), 1);
        assert_eq!(user.nome.as_str(), "Lucas");
        assert_eq!(user.email.as_str(), "lucas@example.com");
        assert_eq!(user.password_hash.unwrap().as_str(), "hashed-password-123");
    }

    #[test]
    fn fails_when_postgres_model_has_corrupt_email() {
        let model = PostgresUserModel {
            id: 1,
            nome: "Lucas".to_string(),
            email: "invalid-email".to_string(),
            password_hash: None,
        };

        assert!(model.try_into_domain().is_err());
    }
}
