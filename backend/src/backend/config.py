from functools import lru_cache

from pydantic import Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    environment: str = Field(
        default="development",
        validation_alias="ENVIRONMENT",
    )

    # Database
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/platform",
        validation_alias="DATABASE_URL",
    )

    # HMAC Internal communication secret (between BFF and Backend)
    internal_secret: str = Field(
        default="change-me-in-production",
        validation_alias="INTERNAL_SECRET",
    )

    # JWT and Auth Settings
    jwt_secret: str = Field(
        default="platform-dev-super-secret-jwt-key-32chars!",
        validation_alias="JWT_SECRET",
    )
    jwt_lifetime_seconds: int = Field(
        default=60 * 60 * 24 * 7,  # 7 days
        validation_alias="JWT_LIFETIME_SECONDS",
    )

    # HTTP server binding
    bind_addr: str = Field(
        default="0.0.0.0:3000",
        validation_alias="BIND_ADDR",
    )

    # Public URLs
    public_app_url: str = Field(
        default="http://localhost:5173",
        validation_alias="PUBLIC_APP_URL",
    )

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.environment.lower() == "production":
            if len(self.jwt_secret) < 32 or "dev" in self.jwt_secret.lower():
                msg = (
                    "Em produção, JWT_SECRET deve possuir no mínimo 32 caracteres seguros "
                    "e não utilizar o valor padrão!"
                )
                raise ValueError(msg)
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def async_database_url(self) -> str:
        """Ensures SQLAlchemy 2.0 uses async psycopg driver for Postgres."""
        url = self.database_url
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://") :]
        if url.startswith("postgresql://") and not url.startswith("postgresql+"):
            return "postgresql+psycopg://" + url[len("postgresql://") :]
        return url

    @property
    def host(self) -> str:
        if ":" in self.bind_addr:
            return self.bind_addr.rsplit(":", 1)[0]
        return self.bind_addr

    @property
    def port(self) -> int:
        if ":" in self.bind_addr:
            try:
                return int(self.bind_addr.rsplit(":", 1)[1])
            except ValueError:
                return 3000
        return 3000


@lru_cache
def get_settings() -> Settings:
    return Settings()
