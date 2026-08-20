use crate::application::auth::ports::{ResetTokenGenerator, SessionIdGenerator};
use crate::domain::auth::{RawResetToken, ResetTokenHash, SessionId};
use rand::RngCore;
use sha2::{Digest, Sha256};

#[derive(Default, Clone)]
pub struct CryptoTokenGenerator;

impl CryptoTokenGenerator {
    pub fn new() -> Self {
        Self
    }
}

impl ResetTokenGenerator for CryptoTokenGenerator {
    fn generate(&self) -> (RawResetToken, ResetTokenHash) {
        let mut token_bytes = [0_u8; 32];
        rand::rngs::OsRng.fill_bytes(&mut token_bytes);
        let raw = hex::encode(token_bytes);
        let hash = hex::encode(Sha256::digest(raw.as_bytes()));
        (
            RawResetToken::new(raw).expect("generated valid token"),
            ResetTokenHash::new(hash),
        )
    }

    fn hash_token(&self, raw: &RawResetToken) -> ResetTokenHash {
        let hash = hex::encode(Sha256::digest(raw.as_str().as_bytes()));
        ResetTokenHash::new(hash)
    }
}

impl SessionIdGenerator for CryptoTokenGenerator {
    fn generate(&self) -> SessionId {
        let mut bytes = [0_u8; 32];
        rand::rngs::OsRng.fill_bytes(&mut bytes);
        SessionId::new(hex::encode(bytes)).expect("generated valid session id")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn generates_valid_reset_tokens_and_hashes() {
        let generator = CryptoTokenGenerator::new();
        let (raw, hash) = ResetTokenGenerator::generate(&generator);

        assert_eq!(raw.as_str().len(), 64);
        assert_eq!(hash.as_str().len(), 64);

        let recomputed = generator.hash_token(&raw);
        assert_eq!(hash.as_str(), recomputed.as_str());
    }

    #[test]
    fn generates_unique_session_ids() {
        let generator = CryptoTokenGenerator::new();
        let id1 = SessionIdGenerator::generate(&generator);
        let id2 = SessionIdGenerator::generate(&generator);

        assert_eq!(id1.as_str().len(), 64);
        assert_ne!(id1.as_str(), id2.as_str());
    }
}


