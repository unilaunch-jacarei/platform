use super::dto::{ConfirmResetPasswordRequest, LoginRequest, LoginResponse, ResetPasswordRequest};
use crate::adapters::inbound::http::error::ApiError;
use crate::adapters::inbound::http::state::AppState;
use crate::application::auth::{
    ConfirmPasswordResetCommand, LoginCommand, RequestPasswordResetCommand,
};
use axum::{
    extract::{ConnectInfo, State},
    http::{Extensions, StatusCode},
    response::Json,
};
use std::net::SocketAddr;

pub async fn login(
    State(state): State<AppState>,
    ConnectInfo(address): ConnectInfo<SocketAddr>,
    Json(input): Json<LoginRequest>,
) -> Result<(StatusCode, Json<LoginResponse>), ApiError> {
    let command = LoginCommand {
        email: input.email,
        password: input.password,
        ip: address.ip(),
    };

    let result = state.auth_use_cases.login.execute(command).await?;

    Ok((
        StatusCode::CREATED,
        Json(LoginResponse {
            session_id: result.session_id.into_string(),
            user_id: result.user_id.value(),
        }),
    ))
}

pub async fn session(
    State(state): State<AppState>,
    extensions: Extensions,
) -> Result<Json<serde_json::Value>, ApiError> {
    let session_id = extensions
        .get::<String>()
        .ok_or_else(|| ApiError::Internal("sessão ausente".to_string()))?;

    let user_id = state.auth_use_cases.session.execute(session_id).await?;

    Ok(Json(serde_json::json!({ "user_id": user_id.value() })))
}

pub async fn logout(
    State(state): State<AppState>,
    extensions: Extensions,
) -> Result<StatusCode, ApiError> {
    let session_id = extensions
        .get::<String>()
        .ok_or_else(|| ApiError::Internal("sessão ausente".to_string()))?;

    state.auth_use_cases.logout.execute(session_id).await?;

    Ok(StatusCode::NO_CONTENT)
}

pub async fn reset_password(
    State(state): State<AppState>,
    ConnectInfo(address): ConnectInfo<SocketAddr>,
    Json(input): Json<ResetPasswordRequest>,
) -> Result<StatusCode, ApiError> {
    let command = RequestPasswordResetCommand {
        email: input.email,
        ip: address.ip(),
    };

    state.auth_use_cases.reset_password.execute(command).await?;

    Ok(StatusCode::NO_CONTENT)
}

pub async fn confirm_reset_password(
    State(state): State<AppState>,
    Json(input): Json<ConfirmResetPasswordRequest>,
) -> Result<StatusCode, ApiError> {
    if validate_confirm_reset_password(&input).is_err() {
        return Ok(StatusCode::BAD_REQUEST);
    }

    let command = ConfirmPasswordResetCommand {
        token: input.token,
        new_password: input.new_password,
    };

    state
        .auth_use_cases
        .confirm_reset_password
        .execute(command)
        .await?;

    Ok(StatusCode::NO_CONTENT)
}

fn validate_confirm_reset_password(input: &ConfirmResetPasswordRequest) -> anyhow::Result<()> {
    if input.token.trim().is_empty() {
        anyhow::bail!("token de recuperação ausente");
    }
    if input.new_password.len() < 8 {
        anyhow::bail!("senha deve possuir no mínimo 8 caracteres");
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::adapters::outbound::rate_limiter::MemoryRateLimiter;
    use crate::adapters::outbound::security::CryptoTokenGenerator;
    use crate::application::auth::ports::{AuthRepository, PasswordHasher};
    use crate::application::usuarios::ports::{RepositoryError, UsuarioRepository};
    use crate::bootstrap::create_app_state;
    use crate::domain::auth::{ResetTokenHash, SessionId};
    use crate::domain::usuarios::{Email, HashedPassword, Nome, PlainPassword, Usuario, UsuarioId};
    use async_trait::async_trait;
    use std::sync::Arc;

    struct DummyUserRepo;
    #[async_trait]
    impl UsuarioRepository for DummyUserRepo {
        async fn find_by_id(&self, _id: UsuarioId) -> Result<Option<Usuario>, RepositoryError> {
            Ok(None)
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

    struct FakeAuthRepo {
        user: Option<Usuario>,
    }
    #[async_trait]
    impl AuthRepository for FakeAuthRepo {
        async fn find_user_by_email(&self, _e: &Email) -> Result<Option<Usuario>, RepositoryError> {
            Ok(self.user.clone())
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
            Ok(Some(UsuarioId::new(1)))
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
        let user_repo = Arc::new(DummyUserRepo);
        let auth_repo = Arc::new(FakeAuthRepo { user });
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

    fn valid_confirm_input() -> ConfirmResetPasswordRequest {
        ConfirmResetPasswordRequest {
            token: "token-valido".to_owned(),
            new_password: "senha-segura".to_owned(),
        }
    }

    #[test]
    fn validates_password_reset_confirmation_input() {
        assert!(validate_confirm_reset_password(&valid_confirm_input()).is_ok());

        let mut input = valid_confirm_input();
        input.token = "  ".to_owned();
        assert!(validate_confirm_reset_password(&input).is_err());

        let mut input = valid_confirm_input();
        input.new_password = "1234567".to_owned();
        assert!(validate_confirm_reset_password(&input).is_err());
    }

    #[tokio::test]
    async fn login_handler_success() {
        let user = Usuario::new(
            UsuarioId::new(1),
            Nome::new("Ana").unwrap(),
            Email::new("ana@example.com").unwrap(),
            Some(HashedPassword::new("senha-segura")),
        );
        let state = test_app_state(Some(user));
        let addr = "127.0.0.1:3000".parse().unwrap();
        let res = login(
            State(state),
            ConnectInfo(addr),
            Json(LoginRequest {
                email: "ana@example.com".into(),
                password: "senha-segura".into(),
            }),
        )
        .await;

        assert!(res.is_ok());
        let (status, Json(body)) = res.unwrap();
        assert_eq!(status, StatusCode::CREATED);
        assert_eq!(body.user_id, 1);
    }

    #[tokio::test]
    async fn session_and_logout_handlers_success() {
        let state = test_app_state(None);
        let mut extensions = Extensions::new();
        extensions.insert("sess-123".to_string());

        let session_res = session(State(state.clone()), extensions.clone()).await;
        assert!(session_res.is_ok());
        let Json(val) = session_res.unwrap();
        assert_eq!(val.get("user_id").unwrap().as_i64().unwrap(), 1);

        let logout_res = logout(State(state), extensions).await;
        assert_eq!(logout_res.unwrap(), StatusCode::NO_CONTENT);
    }

    #[tokio::test]
    async fn reset_password_handlers_success() {
        let state = test_app_state(None);
        let addr = "127.0.0.1:3000".parse().unwrap();

        let reset_res = reset_password(
            State(state.clone()),
            ConnectInfo(addr),
            Json(ResetPasswordRequest {
                email: "ana@example.com".into(),
            }),
        )
        .await;
        assert_eq!(reset_res.unwrap(), StatusCode::NO_CONTENT);

        let confirm_res = confirm_reset_password(
            State(state),
            Json(ConfirmResetPasswordRequest {
                token: "token-123".into(),
                new_password: "nova-senha-123".into(),
            }),
        )
        .await;
        assert_eq!(confirm_res.unwrap(), StatusCode::NO_CONTENT);
    }
}
