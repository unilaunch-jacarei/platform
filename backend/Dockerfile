# syntax=docker/dockerfile:1.7

# 1. Builder Stage with UV
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Copy dependency specifications first for Docker layer caching
COPY backend/pyproject.toml backend/uv.lock ./

# Install dependencies into virtualenv without building the project itself yet
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy application source code
COPY backend/src ./src
COPY backend/README.md ./

# Sync project package itself into the virtual environment
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# 2. Final Runtime Stage (Slim & Non-Root)
FROM python:3.12-slim-bookworm AS runtime

ARG APP_VERSION=unknown
LABEL org.opencontainers.image.title="UniLaunch Platform Backend" \
      org.opencontainers.image.description="FastAPI Backend for UniLaunch Platform" \
      org.opencontainers.image.version=$APP_VERSION

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production

# Create non-root system user for security
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Copy only the compiled virtual environment and code from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/src /app/src

USER appuser

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
