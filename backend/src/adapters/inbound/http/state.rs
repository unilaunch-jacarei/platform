use crate::application::auth::{
    ConfirmPasswordResetUseCase, LoginUseCase, LogoutUseCase, RequestPasswordResetUseCase,
    ValidateSessionUseCase,
};
use crate::application::usuarios::{CreateUsuarioUseCase, GetUsuarioUseCase};
use std::sync::Arc;

#[derive(Clone)]
pub struct UserUseCases {
    pub create_usuario: Arc<CreateUsuarioUseCase>,
    pub get_usuario: Arc<GetUsuarioUseCase>,
}

#[derive(Clone)]
pub struct AuthUseCases {
    pub login: Arc<LoginUseCase>,
    pub session: Arc<ValidateSessionUseCase>,
    pub logout: Arc<LogoutUseCase>,
    pub reset_password: Arc<RequestPasswordResetUseCase>,
    pub confirm_reset_password: Arc<ConfirmPasswordResetUseCase>,
}

#[derive(Clone)]
pub struct AppState {
    pub user_use_cases: UserUseCases,
    pub auth_use_cases: AuthUseCases,
    pub internal_secret: Arc<str>,
}
