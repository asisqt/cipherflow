"""
CipherFlow Configuration Module
================================
Centralized environment variable management using Pydantic Settings.
All secrets and configuration are loaded from environment variables
with sensible defaults for local development.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── Application ──────────────────────────────────────────────────────
    APP_NAME: str = "CipherFlow"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # ── Security ─────────────────────────────────────────────────────────
    SECRET_KEY: str = "cipherflow-jwt-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 3600

    # ── Encryption ───────────────────────────────────────────────────────
    ENCRYPTION_KEY: str = "Y2lwaGVyZmxvdy1mZXJuZXQta2V5LTMyYg=="

    # ── CORS ─────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://64.225.84.36",
        "*",
    ]

    # ── Build Info ───────────────────────────────────────────────────────
    BUILD_TAG: str = "local"
    BUILD_COMMIT: str = "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — loaded once per process."""
    return Settings()
