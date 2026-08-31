import pytest
from pydantic import ValidationError

from backend.config import Settings, get_settings


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)
    settings = Settings(_env_file=None)
    assert settings.environment == "development"
    assert settings.port == 3000
    assert settings.host == "0.0.0.0"
    assert settings.jwt_lifetime_seconds > 0


def test_settings_custom_bind_addr():
    settings = Settings(_env_file=None, BIND_ADDR="127.0.0.1:8080")
    assert settings.host == "127.0.0.1"
    assert settings.port == 8080

    settings_no_port = Settings(_env_file=None, BIND_ADDR="127.0.0.1")
    assert settings_no_port.host == "127.0.0.1"
    assert settings_no_port.port == 3000

    settings_invalid_port = Settings(_env_file=None, BIND_ADDR="0.0.0.0:invalid")
    assert settings_invalid_port.port == 3000


def test_async_database_url_conversions():
    s1 = Settings(_env_file=None, DATABASE_URL="postgres://user:pass@localhost:5432/db")
    assert s1.async_database_url == "postgresql+psycopg://user:pass@localhost:5432/db"

    s2 = Settings(_env_file=None, DATABASE_URL="postgresql://user:pass@localhost:5432/db")
    assert s2.async_database_url == "postgresql+psycopg://user:pass@localhost:5432/db"

    s3 = Settings(_env_file=None, DATABASE_URL="sqlite+aiosqlite:///test.db")
    assert s3.async_database_url == "sqlite+aiosqlite:///test.db"


def test_production_secret_validation():
    # Production with dev secret must fail
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            ENVIRONMENT="production",
            JWT_SECRET="platform-dev-super-secret-jwt-key-32chars!",
        )

    # Production with short secret must fail
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            ENVIRONMENT="production",
            JWT_SECRET="short-secret-key",
        )

    # Production with strong valid secret must succeed
    valid_settings = Settings(
        _env_file=None,
        ENVIRONMENT="production",
        JWT_SECRET="super-strong-production-entropy-key-64-bytes-long-random-string!",
    )
    assert valid_settings.environment == "production"


def test_get_settings():
    s = get_settings()
    assert isinstance(s, Settings)
