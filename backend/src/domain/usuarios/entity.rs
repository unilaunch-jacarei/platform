use super::value_objects::{Email, HashedPassword, Nome, UsuarioId};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Usuario {
    pub id: UsuarioId,
    pub nome: Nome,
    pub email: Email,
    pub password_hash: Option<HashedPassword>,
}

impl Usuario {
    pub fn new(
        id: UsuarioId,
        nome: Nome,
        email: Email,
        password_hash: Option<HashedPassword>,
    ) -> Self {
        Self {
            id,
            nome,
            email,
            password_hash,
        }
    }
}
