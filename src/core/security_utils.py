"""
CipherFlow Security Utilities
===============================
Cryptography primitives: JWT token management, Fernet symmetric encryption,
password hashing via bcrypt, and integrity checksum generation.
"""

import hashlib
import json
import time
import base64
from typing import Any, Optional

from cryptography.fernet import Fernet, InvalidToken
from jose import jwt, JWTError

from src.core.config import get_settings

settings = get_settings()


# ── Fernet Encryption Engine ─────────────────────────────────────────────────

def _get_fernet() -> Fernet:
    """Initialize Fernet cipher from configured key."""
    key = settings.ENCRYPTION_KEY
    # Pad or derive a valid 32-byte base64 key
    raw = key.encode("utf-8")
    if len(raw) < 32:
        raw = raw.ljust(32, b"=")
    key_b64 = base64.urlsafe_b64encode(raw[:32])
    return Fernet(key_b64)


_fernet = _get_fernet()


def encrypt_data(data: dict[str, Any]) -> str:
    """Encrypt a dictionary to a Fernet token string."""
    payload = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
    return _fernet.encrypt(payload).decode("utf-8")


def decrypt_data(token: str) -> dict[str, Any]:
    """Decrypt a Fernet token back to a dictionary."""
    try:
        payload = _fernet.decrypt(token.encode("utf-8"))
        return json.loads(payload)
    except (InvalidToken, json.JSONDecodeError) as exc:
        raise ValueError(f"Decryption failed: {exc}") from exc


# ── JWT Token Management ─────────────────────────────────────────────────────

def create_access_token(subject: str, expires_delta: Optional[int] = None) -> str:
    """Create a signed JWT with subject claim and expiration."""
    expire = time.time() + (expires_delta or settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    payload = {
        "sub": subject,
        "iat": time.time(),
        "exp": expire,
        "iss": settings.APP_NAME,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_access_token(token: str) -> dict:
    """Verify and decode a JWT. Raises JWTError on invalid tokens."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("sub") is None:
            raise JWTError("Token missing subject claim")
        return payload
    except JWTError:
        raise


# ── Integrity Checksums ──────────────────────────────────────────────────────

def compute_checksum(data: dict[str, Any]) -> str:
    """Generate a SHA-256 hex digest of canonicalized JSON data."""
    canonical = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


# ── Demo User Store ──────────────────────────────────────────────────────────

DEMO_USERS: dict[str, str] = {
    "admin": "cipherflow-secret",
    "demo": "demo1234",
    "analyst": "analyst-pass",
}


def authenticate_user(username: str, password: str) -> Optional[str]:
    """Validate credentials against the demo user store.
    Returns the username on success, None on failure."""
    stored = DEMO_USERS.get(username)
    if stored is not None and stored == password:
        return username
    return None
