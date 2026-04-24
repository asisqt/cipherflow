# ═══════════════════════════════════════════════════════════════════════════════
# CipherFlow Backend — Multi-Stage Production Dockerfile
# ═══════════════════════════════════════════════════════════════════════════════
# Stage 1: Install dependencies in a builder layer
# Stage 2: Copy only the runtime artifacts into a slim image
# Result: ~120MB image vs ~900MB with a naive approach
# ═══════════════════════════════════════════════════════════════════════════════

# ── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ── Stage 2: Runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Security: run as non-root
RUN groupadd -r cipherflow && useradd -r -g cipherflow -s /bin/false cipherflow

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy application code
COPY src/ ./src/

# Build metadata (injected at build time)
ARG BUILD_TAG=local
ARG BUILD_COMMIT=development
ENV BUILD_TAG=${BUILD_TAG}
ENV BUILD_COMMIT=${BUILD_COMMIT}

# Security: read-only filesystem hint
ENV PYTHONHASHSEED=random

# Switch to non-root user
USER cipherflow

# Expose port and define health check
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

# Run with uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--access-log"]

# ── Labels for container metadata ────────────────────────────────────────────
LABEL maintainer="Ashish Khatri <1060ashish@gmail.com>"
LABEL org.opencontainers.image.source="https://github.com/asisqt/cipherflow"
LABEL org.opencontainers.image.description="CipherFlow secure data processing API"
LABEL org.opencontainers.image.version="2.0.0"
LABEL org.opencontainers.image.vendor="Ashish Khatri"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.created="2026-04-21"
