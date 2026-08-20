use super::error::UsuarioAppError;
use super::ports::UsuarioRepository;
use crate::domain::usuarios::{Usuario, UsuarioId};
use std::sync::Arc;

pub struct GetUsuarioUseCase {
    repository: Arc<dyn UsuarioRepository>,
}

impl GetUsuarioUseCase {
    pub fn new(repository: Arc<dyn UsuarioRepository>) -> Self {
        Self { repository }
    }

    pub async fn execute(&self, id: UsuarioId) -> Result<Usuario, UsuarioAppError> {
        let usuario = self
            .repository
            .find_by_id(id)
            .await?
            .ok_or(UsuarioAppError::UsuarioNaoEncontrado(id.value()))?;

        Ok(usuario)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::application::usuarios::ports::RepositoryError;
    use crate::domain::usuarios::{Email, HashedPassword, Nome};
    use async_trait::async_trait;

    struct FakeUsuarioRepository {
        existing_user: Option<Usuario>,
    }

    #[async_trait]
    impl UsuarioRepository for FakeUsuarioRepository {
        async fn find_by_id(&self, id: UsuarioId) -> Result<Option<Usuario>, RepositoryError> {
            Ok(self.existing_user.clone().filter(|u| u.id == id))
        }

        async fn create(
            &self,
            _nome: &Nome,
            _email: &Email,
            _password_hash: &HashedPassword,
        ) -> Result<UsuarioId, RepositoryError> {
            Ok(UsuarioId::new(1))
        }
    }

    #[tokio::test]
    async fn returns_user_when_found() {
        let user = Usuario::new(
            UsuarioId::new(42),
            Nome::new("João").unwrap(),
            Email::new("joao@example.com").unwrap(),
            None,
        );
        let repo = Arc::new(FakeUsuarioRepository {
            existing_user: Some(user),
        });
        let use_case = GetUsuarioUseCase::new(repo);

        let result = use_case.execute(UsuarioId::new(42)).await;
        assert!(result.is_ok());
        let found = result.unwrap();
        assert_eq!(found.id.value(), 42);
        assert_eq!(found.nome.as_str(), "João");
    }

    #[tokio::test]
    async fn returns_not_found_when_user_does_not_exist() {
        let repo = Arc::new(FakeUsuarioRepository {
            existing_user: None,
        });
        let use_case = GetUsuarioUseCase::new(repo);

        let result = use_case.execute(UsuarioId::new(99)).await;
        assert!(matches!(
            result,
            Err(UsuarioAppError::UsuarioNaoEncontrado(99))
        ));
    }
}

