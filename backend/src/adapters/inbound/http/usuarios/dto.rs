use crate::domain::usuarios::Usuario;
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize)]
pub struct CreateUsuarioRequest {
    pub nome: String,
    pub email: String,
    pub password: String,
}

#[derive(Debug, Serialize)]
pub struct UsuarioResponse {
    pub id: i64,
    pub nome: String,
    pub email: String,
}

#[derive(Debug, Serialize)]
pub struct UsuarioEnvelope {
    pub data: UsuarioResponse,
}

impl From<Usuario> for UsuarioResponse {
    fn from(u: Usuario) -> Self {
        Self {
            id: u.id.value(),
            nome: u.nome.into_string(),
            email: u.email.into_string(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::domain::usuarios::{Email, Nome, UsuarioId};

    #[test]
    fn converts_domain_user_to_response() {
        let user = Usuario::new(
            UsuarioId::new(7),
            Nome::new("Ana").unwrap(),
            Email::new("ana@example.com").unwrap(),
            None,
        );
        let response = UsuarioResponse::from(user);
        assert_eq!(response.id, 7);
        assert_eq!(response.nome, "Ana");
        assert_eq!(response.email, "ana@example.com");
    }
}
