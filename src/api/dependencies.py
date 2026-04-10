"""
CipherFlow API Dependencies
=============================
FastAPI dependency injection for authentication, authorization,
and request context. The Bearer token scheme extracts and validates
JWTs on every protected endpoint.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.security_utils import verify_access_token
from jose import JWTError

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> str:
    """Extract and validate the Bearer token from the Authorization header.
    Returns the authenticated username (the 'sub' claim).
    Raises 401 if the token is missing, expired, or tampered with.
    """
    token = credentials.credentials
    try:
        payload = verify_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token: missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )
