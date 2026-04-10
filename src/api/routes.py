"""
CipherFlow API Routes
======================
Defines all HTTP endpoints for the CipherFlow secure data processing API.
Endpoints are grouped by function: authentication, processing, and health.
"""

import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.api.dependencies import get_current_user
from src.core.config import get_settings
from src.core.security_utils import authenticate_user, create_access_token
from src.services.data_processor import process_payload

settings = get_settings()
_start_time = time.time()


# ── Request/Response Schemas ─────────────────────────────────────────────────

class AuthRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class ProcessRequest(BaseModel):
    id: str = Field(..., min_length=1, description="Record identifier")
    data: dict[str, Any] = Field(..., description="Payload data to process")


class PipelineStageResponse(BaseModel):
    name: str
    status: str
    duration_ms: float


class ProcessResponse(BaseModel):
    status: str
    record_id: str
    processed_data: dict[str, Any] | None = None
    encrypted_blob: str | None = None
    is_encrypted: bool = False
    checksum: str
    processed_at: str
    warnings: list[str] = []
    pipeline: list[PipelineStageResponse] = []


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "cipherflow"
    version: str = settings.APP_VERSION
    uptime_seconds: float
    build: str = settings.BUILD_TAG
    timestamp: str


class InfoResponse(BaseModel):
    service: str
    version: str
    build_tag: str
    build_commit: str
    environment: str
    endpoints: dict[str, str]


# ── Router ───────────────────────────────────────────────────────────────────

router = APIRouter()


# ── Authentication ───────────────────────────────────────────────────────────

@router.post(
    "/auth/token",
    response_model=AuthResponse,
    tags=["Authentication"],
    summary="Obtain a JWT access token",
    description="Authenticate with username/password credentials to receive a Bearer token.",
)
async def login(body: AuthRequest):
    user = authenticate_user(body.username, body.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(subject=user)
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
    )


# ── Data Processing ──────────────────────────────────────────────────────────

@router.post(
    "/process",
    response_model=ProcessResponse,
    tags=["Processing"],
    summary="Process a data payload",
    description="Run a payload through the 4-stage pipeline: validate → normalize → redact → checksum.",
)
async def process_data(
    body: ProcessRequest,
    current_user: str = Depends(get_current_user),
):
    result = process_payload(body.model_dump(), encrypt=False)

    if result.status == "failed":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": result.errors, "warnings": result.warnings},
        )

    return ProcessResponse(
        status=result.status,
        record_id=result.record_id,
        processed_data=result.processed_data,
        is_encrypted=False,
        checksum=result.checksum,
        processed_at=result.processed_at,
        warnings=result.warnings,
        pipeline=[
            PipelineStageResponse(name=s.name, status=s.status, duration_ms=s.duration_ms)
            for s in result.pipeline
        ],
    )


@router.post(
    "/process/encrypted",
    response_model=ProcessResponse,
    tags=["Processing"],
    summary="Process and encrypt a data payload",
    description="Run a payload through all 5 stages including Fernet encryption.",
)
async def process_data_encrypted(
    body: ProcessRequest,
    current_user: str = Depends(get_current_user),
):
    result = process_payload(body.model_dump(), encrypt=True)

    if result.status == "failed":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": result.errors, "warnings": result.warnings},
        )

    return ProcessResponse(
        status=result.status,
        record_id=result.record_id,
        encrypted_blob=result.encrypted_blob,
        is_encrypted=True,
        checksum=result.checksum,
        processed_at=result.processed_at,
        warnings=result.warnings,
        pipeline=[
            PipelineStageResponse(name=s.name, status=s.status, duration_ms=s.duration_ms)
            for s in result.pipeline
        ],
    )


# ── Health & Info ────────────────────────────────────────────────────────────

@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="API health check",
)
async def health_check():
    from datetime import datetime, timezone

    return HealthResponse(
        status="ok",
        service="cipherflow",
        version=settings.APP_VERSION,
        uptime_seconds=round(time.time() - _start_time, 2),
        build=settings.BUILD_TAG,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get(
    "/ready",
    tags=["Health"],
    summary="Kubernetes readiness probe",
)
async def readiness():
    return {"status": "ready"}


@router.get(
    "/info",
    response_model=InfoResponse,
    tags=["Health"],
    summary="Build and deployment info",
)
async def build_info(current_user: str = Depends(get_current_user)):
    return InfoResponse(
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        build_tag=settings.BUILD_TAG,
        build_commit=settings.BUILD_COMMIT,
        environment=settings.ENVIRONMENT,
        endpoints={
            "auth": "/api/v1/auth/token",
            "process": "/api/v1/process",
            "process_encrypted": "/api/v1/process/encrypted",
            "health": "/api/v1/health",
            "docs": "/docs",
        },
    )
