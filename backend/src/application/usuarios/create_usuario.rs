use super::error::UsuarioAppError;
use super::ports::UsuarioRepository;
use crate::application::auth::ports::PasswordHasher;
use crate::domain::usuarios::{Email, Nome, PlainPassword, UsuarioId};
use std::sync::Arc;

pub struct CreateUsuarioCommand {
    pub nome: String,
    pub email: String,
    pub password: String,
}

pub struct CreateUsuarioUseCase {
    repository: Arc<dyn UsuarioRepository>,
    password_hasher: Arc<dyn PasswordHasher>,
}

impl CreateUsuarioUseCase {
    pub fn new(
        repository: Arc<dyn UsuarioRepository>,
        password_hasher: Arc<dyn PasswordHasher>,
    ) -> Self {
        Self {
            repository,
            password_hasher,
        }
    }

    pub async fn execute(&self, cmd: CreateUsuarioCommand) -> Result<UsuarioId, UsuarioAppError> {
        let nome = Nome::new(cmd.nome)?;
        let email = Email::new(cmd.email)?;
        let plain_password = PlainPassword::new(cmd.password)?;

        let password_hash = self
            .password_hasher
            .hash(&plain_password)
            .map_err(UsuarioAppError::Internal)?;

        let id = self
            .repository
            .create(&nome, &email, &password_hash)
            .await?;

        Ok(id)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::application::usuarios::ports::RepositoryError;
    use crate::domain::usuarios::{HashedPassword, Usuario, UsuarioDomainError};
    use async_trait::async_trait;
    use std::sync::Mutex;

    struct FakeUsuarioRepository {
        created_count: Mutex<i64>,
    }

    impl FakeUsuarioRepository {
        fn new() -> Self {
            Self {
                created_count: Mutex::new(0),
            }
        }
    }

    #[async_trait]
    impl UsuarioRepository for FakeUsuarioRepository {
        async fn find_by_id(&self, _id: UsuarioId) -> Result<Option<Usuario>, RepositoryError> {
            Ok(None)
        }

        async fn create(
            &self,
            _nome: &Nome,
            _email: &Email,
            _password_hash: &HashedPassword,
        ) -> Result<UsuarioId, RepositoryError> {
            let mut lock = self.created_count.lock().unwrap();
            *lock += 1;
            Ok(UsuarioId::new(*lock))
        }
    }

    struct FakePasswordHasher;

    impl PasswordHasher for FakePasswordHasher {
        fn hash(&self, password: &PlainPassword) -> Result<HashedPassword, String> {
            Ok(HashedPassword::new(format!("hashed_{}", password.as_str())))
        }

        fn verify(&self, password: &PlainPassword, hashed: &HashedPassword) -> Result<bool, String> {
            Ok(hashed.as_str() == format!("hashed_{}", password.as_str()))
        }
    }

    #[tokio::test]
    async fn successfully_creates_user_without_database() {
        let repo = Arc::new(FakeUsuarioRepository::new());
        let hasher = Arc::new(FakePasswordHasher);
        let use_case = CreateUsuarioUseCase::new(repo.clone(), hasher);

        let result = use_case
            .execute(CreateUsuarioCommand {
                nome: "Maria Silva".to_string(),
                email: "maria@example.com".to_string(),
                password: "senha-segura-123".to_string(),
            })
            .await;

        assert!(result.is_ok());
        assert_eq!(result.unwrap().value(), 1);
        assert_eq!(*repo.created_count.lock().unwrap(), 1);
    }

    #[tokio::test]
    async fn fails_when_email_is_invalid_without_hitting_repository() {
        let repo = Arc::new(FakeUsuarioRepository::new());
        let hasher = Arc::new(FakePasswordHasher);
        let use_case = CreateUsuarioUseCase::new(repo.clone(), hasher);

        let result = use_case
            .execute(CreateUsuarioCommand {
                nome: "Maria Silva".to_string(),
                email: "email-invalido".to_string(),
                password: "senha-segura-123".to_string(),
            })
            .await;

        assert!(matches!(
            result,
            Err(UsuarioAppError::Domain(UsuarioDomainError::EmailInvalido(_)))
        ));
        assert_eq!(*repo.created_count.lock().unwrap(), 0);
    }

    #[tokio::test]
    async fn fails_when_password_is_too_short() {
        let repo = Arc::new(FakeUsuarioRepository::new());
        let hasher = Arc::new(FakePasswordHasher);
        let use_case = CreateUsuarioUseCase::new(repo.clone(), hasher);

        let result = use_case
            .execute(CreateUsuarioCommand {
                nome: "Maria Silva".to_string(),
                email: "maria@example.com".to_string(),
                password: "123".to_string(),
            })
            .await;

        assert!(matches!(
            result,
            Err(UsuarioAppError::Domain(UsuarioDomainError::SenhaCurta))
        ));
        assert_eq!(*repo.created_count.lock().unwrap(), 0);
    }
}

