from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "CipherFlow"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = False

    # Security
    secret_key: str = "change-me-in-production-min-32-chars!!"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    encryption_key: str = "change-me-32-bytes-fernet-key!!!!"

    # API
    api_prefix: str = "/api/v1"
    allowed_hosts: list[str] = ["*"]
    rate_limit_per_minute: int = 60

    # Build info (injected by CI pipeline)
    build_tag: str = "local"
    build_commit: str = "none"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Cached settings — loaded once, reused everywhere."""
    return Settings()
