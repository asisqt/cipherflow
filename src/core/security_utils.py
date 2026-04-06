from datetime import datetime, timedelta, timezone
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import get_settings

settings = get_settings()

# ── Password hashing ──────────────────────────────────────────────────────────
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


# ── JWT tokens ────────────────────────────────────────────────────────────────
def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT with an expiry claim."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": str(subject), "exp": expire, "iat": datetime.now(timezone.utc)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT.
    Raises JWTError if the token is expired, tampered, or malformed.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("sub") is None:
            raise JWTError("Token missing subject claim")
        return payload
    except JWTError:
        raise


# ── Symmetric encryption (Fernet / AES-128-CBC) ───────────────────────────────
def _get_fernet() -> Fernet:
    """
    Derive a valid Fernet key from the configured encryption_key.
    Fernet requires exactly 32 url-safe base64 bytes — we pad/truncate here
    so the app starts cleanly even with a raw string key in development.
    """
    import base64
    raw = settings.encryption_key.encode()[:32].ljust(32, b"=")
    key = base64.urlsafe_b64encode(raw)
    return Fernet(key)


def encrypt_payload(data: str) -> str:
    """Encrypt a plaintext string. Returns a url-safe base64 token."""
    return _get_fernet().encrypt(data.encode()).decode()


def decrypt_payload(token: str) -> str:
    """
    Decrypt a Fernet token back to plaintext.
    Raises cryptography.fernet.InvalidToken on tampered or expired ciphertext.
    """
    try:
        return _get_fernet().decrypt(token.encode()).decode()
    except InvalidToken:
        raise ValueError("Payload decryption failed — token invalid or tampered")


def mask_sensitive(value: str, visible_chars: int = 4) -> str:
    """Return a partially masked string safe for logging (e.g. API keys)."""
    if len(value) <= visible_chars:
        return "*" * len(value)
    return value[:visible_chars] + "*" * (len(value) - visible_chars)
