"""
CipherFlow Environment Profiles
==================================
Pre-configured settings for development, staging, and production.
Validates that critical security settings are not using defaults
in production environments.
"""

from typing import Any


PROFILES: dict[str, dict[str, Any]] = {
    "development": {
        "debug": True,
        "log_level": "DEBUG",
        "cors_origins": ["*"],
        "workers": 1,
        "reload": True,
    },
    "staging": {
        "debug": False,
        "log_level": "INFO",
        "cors_origins": ["https://staging.cipherflow.dev"],
        "workers": 2,
        "reload": False,
    },
    "production": {
        "debug": False,
        "log_level": "WARNING",
        "cors_origins": ["https://cipherflow.dev"],
        "workers": 4,
        "reload": False,
    },
}

DEFAULT_SECRETS = {
    "cipherflow-jwt-secret-key-change-in-production-2024",
    "change-me-in-production-min-32-chars!!",
    "supersecretkey",
}


def get_profile(environment: str) -> dict[str, Any]:
    """Return configuration profile for the given environment."""
    return PROFILES.get(environment, PROFILES["development"])


def validate_production_config(secret_key: str, environment: str) -> list[str]:
    """Check for insecure defaults in production. Returns list of warnings."""
    warnings = []
    if environment == "production":
        if secret_key in DEFAULT_SECRETS:
            warnings.append("CRITICAL: Using default SECRET_KEY in production")
        if len(secret_key) < 32:
            warnings.append("WARNING: SECRET_KEY should be at least 32 characters")
    return warnings
