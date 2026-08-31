import argon2
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

_hasher = argon2.PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
    type=argon2.Type.ID,
)


def hash_password(password: str) -> str:
    """Gera um hash Argon2id com salt aleatório. O salt fica embutido no resultado."""
    if not password:
        raise ValueError("senha não pode ser vazia")
    return _hasher.hash(password)


def verify_password(password: str, encoded_hash: str) -> bool:
    """Verifica se a senha em texto plano corresponde ao hash Argon2id."""
    if not password or not encoded_hash:
        return False
    try:
        return _hasher.verify(encoded_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False
