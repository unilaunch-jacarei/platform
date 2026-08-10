use serde::{Deserialize, Serialize};

#[derive(Debug)]
pub struct UsuarioDb {
    pub id: i64,
    pub nome: String,
    pub email: String,
}

#[derive(Debug, Serialize)]
pub struct UsuarioResponse {
    pub id: i64,
    pub nome: String,
    pub email: String,
}

#[derive(Debug, Deserialize)]
pub struct CreateUsuarioRequest {
    pub nome: String,
    pub email: String,
    pub password: String,
}

impl From<UsuarioDb> for UsuarioResponse {
    fn from(usuario: UsuarioDb) -> Self {
        Self {
            id: usuario.id,
            nome: usuario.nome,
            email: usuario.email,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn converts_database_model_to_response_without_password_data() {
        let response = UsuarioResponse::from(UsuarioDb {
            id: 7,
            nome: "Ana".to_owned(),
            email: "ana@example.com".to_owned(),
        });
        assert_eq!(response.id, 7);
        assert_eq!(response.nome, "Ana");
        assert_eq!(response.email, "ana@example.com");
    }
}
