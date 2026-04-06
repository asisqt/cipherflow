"""
CipherFlow API Routes
----------------------
POST /auth/token          — issue JWT
GET  /health              — liveness probe
GET  /ready               — readiness probe
POST /process             — process a data payload (auth required)
POST /process/encrypted   — process and encrypt output (auth required)
GET  /info                — build and runtime info (auth required)
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.api.dependencies import CurrentUser, authenticate_user, issue_token
from src.core.config import get_settings
from src.services.data_processor import ProcessingResult, process_payload

router = APIRouter()
settings = get_settings()


# ── Schemas ───────────────────────────────────────────────────────────────────

class TokenRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PayloadRequest(BaseModel):
    payload_id: str = Field(..., min_length=1, description="Unique ID for this payload")
    source:     str = Field(..., min_length=1, description="Origin system identifier")
    data:       dict = Field(..., description="Arbitrary data object to process")
    metadata:   dict | None = Field(default=None, description="Optional context metadata")


class ProcessResponse(BaseModel):
    status:       str
    record_id:    str
    checksum:     str
    processed:    dict
    warnings:     list[str]
    encrypted:    bool
    processed_at: str


# ── Auth ──────────────────────────────────────────────────────────────────────

@router.post(
    "/auth/token",
    response_model=TokenResponse,
    summary="Issue JWT access token",
    tags=["auth"],
)
async def login(body: TokenRequest):
    user = authenticate_user(body.username, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return issue_token(user)


# ── Health ────────────────────────────────────────────────────────────────────

@router.get("/health", tags=["ops"], summary="Liveness probe")
async def health():
    return {"status": "ok", "service": "cipherflow", "build": settings.build_tag}


@router.get("/ready", tags=["ops"], summary="Readiness probe")
async def ready():
    # Add real dependency checks here (DB ping, cache reachability, etc.)
    return {"ready": True}


# ── Processing ────────────────────────────────────────────────────────────────

@router.post(
    "/process",
    response_model=ProcessResponse,
    summary="Process a data payload",
    tags=["pipeline"],
)
async def process(body: PayloadRequest, _user: CurrentUser):
    raw = body.model_dump(exclude_none=True)
    result: ProcessingResult = process_payload(raw, encrypt=False)

    if result.status.value == "failed":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": result.warnings},
        )

    return ProcessResponse(
        status=result.status.value,
        record_id=result.record_id,
        checksum=result.checksum,
        processed=result.processed,
        warnings=result.warnings,
        encrypted=result.encrypted,
        processed_at=result.processed_at,
    )


@router.post(
    "/process/encrypted",
    response_model=ProcessResponse,
    summary="Process and encrypt output with Fernet",
    tags=["pipeline"],
)
async def process_encrypted(body: PayloadRequest, _user: CurrentUser):
    raw = body.model_dump(exclude_none=True)
    result: ProcessingResult = process_payload(raw, encrypt=True)

    if result.status.value == "failed":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": result.warnings},
        )

    return ProcessResponse(
        status=result.status.value,
        record_id=result.record_id,
        checksum=result.checksum,
        processed=result.processed,
        warnings=result.warnings,
        encrypted=result.encrypted,
        processed_at=result.processed_at,
    )


# ── Info ──────────────────────────────────────────────────────────────────────

@router.get("/info", tags=["ops"], summary="Build and runtime information")
async def info(_user: CurrentUser):
    return {
        "app":     settings.app_name,
        "version": settings.app_version,
        "env":     settings.app_env,
        "build":   settings.build_tag,
        "commit":  settings.build_commit,
    }
