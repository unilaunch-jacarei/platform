use super::{
    models::{CreateUsuarioRequest, UsuarioResponse},
    repository,
};
use crate::{AppState, error::AppError};
use axum::{
    extract::{Path, State},
    http::{Extensions, StatusCode},
    response::Json,
};
use serde::Serialize;

#[derive(Serialize)]
pub struct UsuarioEnvelope {
    pub data: UsuarioResponse,
}

pub async fn create_usuario(
    State(state): State<AppState>,
    Json(input): Json<CreateUsuarioRequest>,
) -> Result<(StatusCode, Json<serde_json::Value>), AppError> {
    validate_create_usuario(&input)?;
    let id = repository::create(&state.db, &input.nome, &input.email, &input.password).await?;
    Ok((StatusCode::CREATED, Json(serde_json::json!({ "id": id }))))
}

pub async fn get_usuario(
    State(state): State<AppState>,
    Path(id): Path<i64>,
    extensions: Extensions,
) -> Result<Json<UsuarioEnvelope>, AppError> {
    let user_id = extensions.get::<String>().cloned().unwrap_or_default();
    let usuario = repository::find_by_id(&state.db, id)
        .await
        .map_err(|error| anyhow::anyhow!(error).context(format!("usuário autenticado {user_id}")))?
        .ok_or_else(|| anyhow::anyhow!("usuário {id} não encontrado"))?;
    Ok(Json(UsuarioEnvelope {
        data: usuario.into(),
    }))
}

fn validate_create_usuario(input: &CreateUsuarioRequest) -> anyhow::Result<()> {
    if input.nome.trim().is_empty() || input.email.trim().is_empty() || input.password.is_empty() {
        anyhow::bail!("nome, email e senha são obrigatórios");
    }
    if input.password.chars().count() < 8 {
        anyhow::bail!("senha deve possuir no mínimo 8 caracteres");
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn valid_input() -> CreateUsuarioRequest {
        CreateUsuarioRequest {
            nome: "Ana".to_owned(),
            email: "ana@example.com".to_owned(),
            password: "senha-segura".to_owned(),
        }
    }

    #[test]
    fn accepts_valid_registration() {
        assert!(validate_create_usuario(&valid_input()).is_ok());
    }

    #[test]
    fn rejects_missing_registration_fields() {
        let mut input = valid_input();
        input.nome = "  ".to_owned();
        assert!(validate_create_usuario(&input).is_err());
        input = valid_input();
        input.email.clear();
        assert!(validate_create_usuario(&input).is_err());
        input = valid_input();
        input.password.clear();
        assert!(validate_create_usuario(&input).is_err());
    }

    #[test]
    fn rejects_short_passwords() {
        let mut input = valid_input();
        input.password = "1234567".to_owned();
        assert!(validate_create_usuario(&input).is_err());
    }
}
