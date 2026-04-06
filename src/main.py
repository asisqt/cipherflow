"""
CipherFlow — Secure Cloud-Native Data Processing Pipeline
Entry point: uvicorn src.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.api.routes import router
from src.core.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"[CipherFlow] Starting — env={settings.app_env} build={settings.build_tag}")
    yield
    # Shutdown
    print("[CipherFlow] Shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A secure cloud-native data processing pipeline with JWT auth, "
        "Fernet encryption, and a full CI/CD delivery workflow."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ─────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.app_env == "production":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

# ── Routes ─────────────────────────────────────────────────────────────────────
app.include_router(router, prefix=settings.api_prefix)


# Root redirect to docs
@app.get("/", include_in_schema=False)
async def root():
    return {"message": "CipherFlow API", "docs": "/docs", "health": "/api/v1/health"}
