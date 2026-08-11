use anyhow::Error;
use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
};

#[derive(Debug)]
pub struct AppError(pub Error);

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        tracing::error!(error = ?self.0, "erro interno da aplicação");
        StatusCode::INTERNAL_SERVER_ERROR.into_response()
    }
}

impl From<Error> for AppError {
    fn from(error: Error) -> Self {
        Self(error)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hides_internal_error_from_http_client() {
        let response =
            AppError(anyhow::anyhow!("database password must stay private")).into_response();
        assert_eq!(response.status(), StatusCode::INTERNAL_SERVER_ERROR);
    }
}
