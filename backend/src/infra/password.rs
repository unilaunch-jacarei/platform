use anyhow::Result;
use argon2::{
    Argon2,
    password_hash::{PasswordHash, PasswordHasher, PasswordVerifier, SaltString, rand_core::OsRng},
};

/// Gera um hash Argon2id com salt aleatório. O salt fica embutido no resultado.
pub fn hash_password(password: &str) -> Result<String> {
    if password.is_empty() {
        anyhow::bail!("senha não pode ser vazia");
    }

    let salt = SaltString::generate(&mut OsRng);
    Argon2::default()
        .hash_password(password.as_bytes(), &salt)
        .map(|hash| hash.to_string())
        .map_err(|error| anyhow::anyhow!("falha ao gerar hash da senha: {error}"))
}

pub fn verify_password(password: &str, encoded_hash: &str) -> Result<bool> {
    let parsed_hash = PasswordHash::new(encoded_hash)
        .map_err(|error| anyhow::anyhow!("hash de senha inválido: {error}"))?;
    Ok(Argon2::default()
        .verify_password(password.as_bytes(), &parsed_hash)
        .is_ok())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hashes_and_verifies_without_storing_plaintext() {
        let hash = hash_password("uma-senha-segura").unwrap();
        assert_ne!(hash, "uma-senha-segura");
        assert!(hash.starts_with("$argon2id$"));
        assert!(verify_password("uma-senha-segura", &hash).unwrap());
        assert!(!verify_password("senha-incorreta", &hash).unwrap());
    }

    #[test]
    fn generates_unique_salts_and_rejects_invalid_inputs() {
        let first = hash_password("mesma-senha").unwrap();
        let second = hash_password("mesma-senha").unwrap();
        assert_ne!(first, second);
        assert!(hash_password("").is_err());
        assert!(verify_password("senha", "hash-invalido").is_err());
    }
}
