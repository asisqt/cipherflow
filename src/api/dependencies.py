"""
FastAPI dependency injection — authentication and shared resources.
All route handlers receive these via Depends().
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from jose import JWTError

from src.core.security_utils import create_access_token, decode_access_token, hash_password, verify_password
from src.core.config import get_settings, Settings

# ── Bearer token scheme ───────────────────────────────────────────────────────
_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(_bearer)],
) -> dict:
    """
    Validate the Bearer JWT from the Authorization header.
    Raises 401 if missing, expired, or invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(credentials.credentials)
        return {"sub": payload["sub"]}
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Settings shortcut ─────────────────────────────────────────────────────────
def get_app_settings() -> Settings:
    return get_settings()


# ── Demo user store (replace with DB in production) ──────────────────────────
_DEMO_USERS_RAW: dict[str, str] = {
    "admin": "cipherflow-secret",
    "demo":  "demo1234",
}
_DEMO_USERS: dict[str, str] = {}

def _get_user_store() -> dict[str, str]:
    global _DEMO_USERS
    if not _DEMO_USERS:
        _DEMO_USERS = {u: hash_password(p) for u, p in _DEMO_USERS_RAW.items()}
    return _DEMO_USERS


def authenticate_user(username: str, password: str) -> str | None:
    """
    Verify credentials against the user store.
    Returns the username on success, None on failure.
    """
    hashed = _get_user_store().get(username)
    if hashed and verify_password(password, hashed):
        return username
    return None


def issue_token(username: str) -> dict:
    """Issue a signed JWT for a verified user."""
    token = create_access_token(subject=username)
    return {"access_token": token, "token_type": "bearer"}


# ── Type alias for DI in route handlers ───────────────────────────────────────
CurrentUser = Annotated[dict, Depends(get_current_user)]
