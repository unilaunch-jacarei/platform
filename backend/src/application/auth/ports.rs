use crate::application::usuarios::ports::RepositoryError;
use crate::domain::auth::{RawResetToken, ResetTokenHash, SessionId};
use crate::domain::usuarios::{Email, HashedPassword, PlainPassword, Usuario, UsuarioId};
use async_trait::async_trait;
use std::net::IpAddr;
use std::time::Duration;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum RateLimitOperation {
    Login,
    ResetPassword,
    Register,
}

#[async_trait]
pub trait RateLimiterPort: Send + Sync {
    async fn is_allowed(
        &self,
        ip: IpAddr,
        operation: RateLimitOperation,
        window: Duration,
        max_attempts: u32,
    ) -> bool;
    async fn reset(&self, ip: IpAddr, operation: RateLimitOperation);
}

pub trait PasswordHasher: Send + Sync {
    fn hash(&self, password: &PlainPassword) -> Result<HashedPassword, String>;
    fn verify(&self, password: &PlainPassword, hashed: &HashedPassword) -> Result<bool, String>;
}

#[derive(Debug, Clone)]
pub struct EmailMessage {
    pub to: String,
    pub subject: String,
    pub html: String,
    pub text: Option<String>,
}

#[async_trait]
pub trait EmailSenderPort: Send + Sync {
    async fn send(&self, message: EmailMessage) -> Result<String, String>;
}

pub trait ResetTokenGenerator: Send + Sync {
    fn generate(&self) -> (RawResetToken, ResetTokenHash);
    fn hash_token(&self, raw: &RawResetToken) -> ResetTokenHash;
}

pub trait SessionIdGenerator: Send + Sync {
    fn generate(&self) -> SessionId;
}

#[async_trait]
pub trait AuthRepository: Send + Sync {
    async fn find_user_by_email(&self, email: &Email) -> Result<Option<Usuario>, RepositoryError>;
    async fn create_session(&self, user_id: UsuarioId, session_id: &SessionId) -> Result<(), RepositoryError>;
    async fn find_user_id_by_session(&self, session_id: &SessionId) -> Result<Option<UsuarioId>, RepositoryError>;
    async fn delete_session(&self, session_id: &SessionId) -> Result<(), RepositoryError>;
    async fn create_password_reset(
        &self,
        user_id: UsuarioId,
        token_hash: &ResetTokenHash,
    ) -> Result<(), RepositoryError>;
    async fn consume_password_reset(
        &self,
        token_hash: &ResetTokenHash,
        password_hash: &HashedPassword,
    ) -> Result<bool, RepositoryError>;
}
