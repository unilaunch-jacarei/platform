use super::dto::{CreateUsuarioRequest, UsuarioEnvelope};
use crate::adapters::inbound::http::error::ApiError;
use crate::adapters::inbound::http::state::AppState;
use crate::application::usuarios::CreateUsuarioCommand;
use crate::domain::usuarios::UsuarioId;
use axum::{
    extract::{Path, State},
    http::{Extensions, StatusCode},
    response::Json,
};

pub async fn create_usuario(
    State(state): State<AppState>,
    Json(input): Json<CreateUsuarioRequest>,
) -> Result<(StatusCode, Json<serde_json::Value>), ApiError> {
    let command = CreateUsuarioCommand {
        nome: input.nome,
        email: input.email,
        password: input.password,
    };

    let id = state.user_use_cases.create_usuario.execute(command).await?;

    Ok((
        StatusCode::CREATED,
        Json(serde_json::json!({ "id": id.value() })),
    ))
}

pub async fn get_usuario(
    State(state): State<AppState>,
    Path(id): Path<i64>,
    extensions: Extensions,
) -> Result<Json<UsuarioEnvelope>, ApiError> {
    let _user_id = extensions.get::<String>().cloned().unwrap_or_default();
    let usuario = state
        .user_use_cases
        .get_usuario
        .execute(UsuarioId::new(id))
        .await?;

    Ok(Json(UsuarioEnvelope {
        data: usuario.into(),
    }))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::adapters::outbound::rate_limiter::MemoryRateLimiter;
    use crate::adapters::outbound::security::CryptoTokenGenerator;
    use crate::application::auth::ports::PasswordHasher;
    use crate::application::usuarios::ports::{RepositoryError, UsuarioRepository};
    use crate::bootstrap::create_app_state;
    use crate::domain::auth::{ResetTokenHash, SessionId};
    use crate::domain::usuarios::{Email, HashedPassword, Nome, PlainPassword, Usuario};
    use async_trait::async_trait;
    use std::sync::Arc;

    struct FakeRepo {
        user: Option<Usuario>,
    }
    #[async_trait]
    impl UsuarioRepository for FakeRepo {
        async fn find_by_id(&self, id: UsuarioId) -> Result<Option<Usuario>, RepositoryError> {
            Ok(self.user.clone().filter(|u| u.id == id))
        }
        async fn create(
            &self,
            _n: &Nome,
            _e: &Email,
            _p: &HashedPassword,
        ) -> Result<UsuarioId, RepositoryError> {
            Ok(UsuarioId::new(1))
        }
    }

    struct DummyAuthRepo;
    #[async_trait]
    impl crate::application::auth::ports::AuthRepository for DummyAuthRepo {
        async fn find_user_by_email(&self, _e: &Email) -> Result<Option<Usuario>, RepositoryError> {
            Ok(None)
        }
        async fn create_session(
            &self,
            _u: UsuarioId,
            _s: &SessionId,
        ) -> Result<(), RepositoryError> {
            Ok(())
        }
        async fn find_user_id_by_session(
            &self,
            _s: &SessionId,
        ) -> Result<Option<UsuarioId>, RepositoryError> {
            Ok(None)
        }
        async fn delete_session(&self, _s: &SessionId) -> Result<(), RepositoryError> {
            Ok(())
        }
        async fn create_password_reset(
            &self,
            _u: UsuarioId,
            _t: &ResetTokenHash,
        ) -> Result<(), RepositoryError> {
            Ok(())
        }
        async fn consume_password_reset(
            &self,
            _t: &ResetTokenHash,
            _p: &HashedPassword,
        ) -> Result<bool, RepositoryError> {
            Ok(true)
        }
    }

    struct FakeHasher;
    impl PasswordHasher for FakeHasher {
        fn hash(&self, p: &PlainPassword) -> Result<HashedPassword, String> {
            Ok(HashedPassword::new(p.as_str()))
        }
        fn verify(&self, _p: &PlainPassword, _h: &HashedPassword) -> Result<bool, String> {
            Ok(true)
        }
    }

    fn test_app_state(user: Option<Usuario>) -> AppState {
        let user_repo = Arc::new(FakeRepo { user });
        let auth_repo = Arc::new(DummyAuthRepo);
        let hasher = Arc::new(FakeHasher);
        let crypto = Arc::new(CryptoTokenGenerator::new());
        let limiter = Arc::new(MemoryRateLimiter::new());

        create_app_state(
            user_repo,
            auth_repo,
            hasher,
            limiter,
            crypto.clone(),
            crypto,
            None,
            Arc::from("secret"),
            Arc::from("http://localhost"),
            None,
        )
    }

    #[tokio::test]
    async fn create_usuario_handler_success() {
        let state = test_app_state(None);
        let res = create_usuario(
            State(state),
            Json(CreateUsuarioRequest {
                nome: "Ana".into(),
                email: "ana@example.com".into(),
                password: "senha-segura".into(),
            }),
        )
        .await;

        assert!(res.is_ok());
        let (status, Json(body)) = res.unwrap();
        assert_eq!(status, StatusCode::CREATED);
        assert_eq!(body.get("id").unwrap().as_i64().unwrap(), 1);
    }

    #[tokio::test]
    async fn get_usuario_handler_success() {
        let user = Usuario::new(
            UsuarioId::new(1),
            Nome::new("Ana").unwrap(),
            Email::new("ana@example.com").unwrap(),
            None,
        );
        let state = test_app_state(Some(user));
        let res = get_usuario(State(state), Path(1), Extensions::new()).await;

        assert!(res.is_ok());
        let Json(envelope) = res.unwrap();
        assert_eq!(envelope.data.id, 1);
        assert_eq!(envelope.data.nome, "Ana");
    }
}
