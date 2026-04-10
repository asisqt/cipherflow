"""
CipherFlow — Secure Data Processing Pipeline
==============================================
A production-grade FastAPI application demonstrating enterprise patterns:
JWT authentication, Fernet encryption, data redaction, CORS, health probes,
and a five-stage processing pipeline with per-stage timing metrics.

Architecture:
    src/core/       → Configuration and security primitives
    src/api/        → HTTP routes, schemas, dependency injection
    src/services/   → Business logic (data processing pipeline)
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.api.routes import router as api_router

settings = get_settings()

_start_time: float = 0.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler — runs on startup and shutdown."""
    global _start_time
    _start_time = time.time()
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    print(f"   Environment : {settings.ENVIRONMENT}")
    print(f"   Build tag   : {settings.BUILD_TAG}")
    print(f"   CORS origins: {settings.CORS_ORIGINS}")
    yield
    print(f"🛑 {settings.APP_NAME} shutting down.")


# ── Application Factory ──────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Secure data processing pipeline with JWT authentication, "
        "Fernet encryption, data redaction, and integrity checksums. "
        "Built as a DevOps portfolio piece demonstrating CI/CD, Docker, "
        "Kubernetes, and Terraform."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ───────────────────────────────────────────────────────────────────

app.include_router(api_router, prefix="/api/v1")


# ── Root Endpoint ────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"{settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health",
    }
