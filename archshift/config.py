"""Environment-backed ArchShift settings."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="ARCHSHIFT_", extra="ignore")

    arm_host: str | None = None
    x86_host: str | None = None
    anthropic_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="ANTHROPIC_API_KEY",
    )


@lru_cache
def get_settings() -> Settings:
    """Load and cache settings for the current process."""

    return Settings()
