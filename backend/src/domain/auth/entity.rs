use super::value_objects::SessionId;
use crate::domain::usuarios::UsuarioId;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Session {
    pub id: SessionId,
    pub user_id: UsuarioId,
}

impl Session {
    pub fn new(id: SessionId, user_id: UsuarioId) -> Self {
        Self { id, user_id }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn creates_session_entity() {
        let session = Session::new(SessionId::new("sess-123").unwrap(), UsuarioId::new(1));
        assert_eq!(session.id.as_str(), "sess-123");
        assert_eq!(session.user_id.value(), 1);
    }
}
