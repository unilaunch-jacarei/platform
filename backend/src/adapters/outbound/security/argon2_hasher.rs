use crate::application::auth::ports::PasswordHasher;
use crate::domain::usuarios::{HashedPassword, PlainPassword};
use argon2::{
    Argon2,
    password_hash::{
        PasswordHash, PasswordHasher as _, PasswordVerifier, SaltString, rand_core::OsRng,
    },
};

#[derive(Default, Clone)]
pub struct Argon2PasswordHasher;

impl Argon2PasswordHasher {
    pub fn new() -> Self {
        Self
    }
}

impl PasswordHasher for Argon2PasswordHasher {
    fn hash(&self, password: &PlainPassword) -> Result<HashedPassword, String> {
        let salt = SaltString::generate(&mut OsRng);
        Argon2::default()
            .hash_password(password.as_str().as_bytes(), &salt)
            .map(|hash| HashedPassword::new(hash.to_string()))
            .map_err(|error| format!("falha ao gerar hash da senha: {error}"))
    }

    fn verify(&self, password: &PlainPassword, hashed: &HashedPassword) -> Result<bool, String> {
        let parsed_hash = PasswordHash::new(hashed.as_str())
            .map_err(|error| format!("hash de senha inválido: {error}"))?;
        Ok(Argon2::default()
            .verify_password(password.as_str().as_bytes(), &parsed_hash)
            .is_ok())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hashes_and_verifies_without_storing_plaintext() {
        let hasher = Argon2PasswordHasher::new();
        let plain = PlainPassword::new("uma-senha-segura").unwrap();
        let wrong = PlainPassword::new("senha-incorreta").unwrap();
        let hash = hasher.hash(&plain).unwrap();

        assert_ne!(hash.as_str(), "uma-senha-segura");
        assert!(hash.as_str().starts_with("$argon2id$"));
        assert!(hasher.verify(&plain, &hash).unwrap());
        assert!(!hasher.verify(&wrong, &hash).unwrap());
    }

    #[test]
    fn generates_unique_salts() {
        let hasher = Argon2PasswordHasher::new();
        let plain = PlainPassword::new("mesma-senha").unwrap();
        let first = hasher.hash(&plain).unwrap();
        let second = hasher.hash(&plain).unwrap();
        assert_ne!(first.as_str(), second.as_str());
    }
}
