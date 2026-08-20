use crate::application::auth::AuthAppError;
use crate::application::usuarios::UsuarioAppError;
use crate::domain::auth::AuthDomainError;
use crate::domain::usuarios::UsuarioDomainError;
use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
};

#[derive(Debug)]
pub enum ApiError {
    BadRequest(String),
    Unauthorized(String),
    NotFound(String),
    UnprocessableEntity(String),
    Internal(String),
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        match self {
            Self::BadRequest(msg) => {
                tracing::warn!(error = %msg, "bad request");
                StatusCode::BAD_REQUEST.into_response()
            }
            Self::Unauthorized(msg) => {
                tracing::warn!(error = %msg, "unauthorized");
                StatusCode::UNAUTHORIZED.into_response()
            }
            Self::NotFound(msg) => {
                tracing::warn!(error = %msg, "not found");
                StatusCode::NOT_FOUND.into_response()
            }
            Self::UnprocessableEntity(msg) => {
                tracing::warn!(error = %msg, "unprocessable entity");
                StatusCode::UNPROCESSABLE_ENTITY.into_response()
            }
            Self::Internal(msg) => {
                tracing::error!(error = %msg, "internal server error");
                StatusCode::INTERNAL_SERVER_ERROR.into_response()
            }
        }
    }
}

impl From<UsuarioDomainError> for ApiError {
    fn from(err: UsuarioDomainError) -> Self {
        match err {
            UsuarioDomainError::CamposObrigatorios
            | UsuarioDomainError::SenhaCurta
            | UsuarioDomainError::NomeVazio => Self::BadRequest(err.to_string()),
            UsuarioDomainError::EmailInvalido(_) => Self::UnprocessableEntity(err.to_string()),
        }
    }
}

impl From<UsuarioAppError> for ApiError {
    fn from(err: UsuarioAppError) -> Self {
        match err {
            UsuarioAppError::Domain(d) => d.into(),
            UsuarioAppError::UsuarioNaoEncontrado(id) => {
                Self::Internal(format!("usuário {id} não encontrado"))
            }
            UsuarioAppError::Repository(e) => Self::Internal(e.to_string()),
            UsuarioAppError::Internal(msg) => Self::Internal(msg),
        }
    }
}

impl From<AuthDomainError> for ApiError {
    fn from(err: AuthDomainError) -> Self {
        match err {
            AuthDomainError::TokenRecuperacaoInvalido => Self::Unauthorized(err.to_string()),
            AuthDomainError::TokenRecuperacaoAusente | AuthDomainError::SenhaInvalida(_) => {
                Self::BadRequest(err.to_string())
            }
            AuthDomainError::CredenciaisInvalidas
            | AuthDomainError::SessaoAusente
            | AuthDomainError::SessaoInvalidaOuExpirada
            | AuthDomainError::LimiteTentativasExcedido
            | AuthDomainError::EmailNaoConfigurado => Self::Internal(err.to_string()),
        }
    }
}

impl From<AuthAppError> for ApiError {
    fn from(err: AuthAppError) -> Self {
        match err {
            AuthAppError::Domain(d) => d.into(),
            AuthAppError::UsuarioDomain(d) => d.into(),
            AuthAppError::Repository(e) => Self::Internal(e.to_string()),
            AuthAppError::Internal(msg) => Self::Internal(msg),
        }
    }
}

impl From<anyhow::Error> for ApiError {
    fn from(err: anyhow::Error) -> Self {
        Self::Internal(err.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::application::usuarios::ports::RepositoryError;

    #[test]
    fn hides_internal_error_from_http_client() {
        let response = ApiError::Internal("database password must stay private".to_string()).into_response();
        assert_eq!(response.status(), StatusCode::INTERNAL_SERVER_ERROR);
    }

    #[test]
    fn maps_all_api_errors_to_status_codes() {
        assert_eq!(ApiError::BadRequest("msg".into()).into_response().status(), StatusCode::BAD_REQUEST);
        assert_eq!(ApiError::Unauthorized("msg".into()).into_response().status(), StatusCode::UNAUTHORIZED);
        assert_eq!(ApiError::NotFound("msg".into()).into_response().status(), StatusCode::NOT_FOUND);
        assert_eq!(ApiError::UnprocessableEntity("msg".into()).into_response().status(), StatusCode::UNPROCESSABLE_ENTITY);
        assert_eq!(ApiError::Internal("msg".into()).into_response().status(), StatusCode::INTERNAL_SERVER_ERROR);
    }

    #[test]
    fn converts_domain_and_app_errors() {
        let err: ApiError = UsuarioDomainError::SenhaCurta.into();
        assert_eq!(err.into_response().status(), StatusCode::BAD_REQUEST);

        let err: ApiError = UsuarioDomainError::EmailInvalido("a".into()).into();
        assert_eq!(err.into_response().status(), StatusCode::UNPROCESSABLE_ENTITY);

        let err: ApiError = UsuarioAppError::UsuarioNaoEncontrado(1).into();
        assert_eq!(err.into_response().status(), StatusCode::INTERNAL_SERVER_ERROR);

        let err: ApiError = UsuarioAppError::Repository(RepositoryError::Database("db".into())).into();
        assert_eq!(err.into_response().status(), StatusCode::INTERNAL_SERVER_ERROR);

        let err: ApiError = AuthDomainError::TokenRecuperacaoInvalido.into();
        assert_eq!(err.into_response().status(), StatusCode::UNAUTHORIZED);

        let err: ApiError = AuthDomainError::TokenRecuperacaoAusente.into();
        assert_eq!(err.into_response().status(), StatusCode::BAD_REQUEST);

        let err: ApiError = AuthDomainError::CredenciaisInvalidas.into();
        assert_eq!(err.into_response().status(), StatusCode::INTERNAL_SERVER_ERROR);

        let err: ApiError = AuthAppError::Internal("err".into()).into();
        assert_eq!(err.into_response().status(), StatusCode::INTERNAL_SERVER_ERROR);

        let err: ApiError = anyhow::anyhow!("generic").into();
        assert_eq!(err.into_response().status(), StatusCode::INTERNAL_SERVER_ERROR);
    }
}

