import logging
import time
import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from backend.config import get_settings
from backend.database import close_db
from backend.domains.leads.routes import leads_router, public_leads_router
from backend.domains.usuarios.routes import auth_router, users_router
from backend.error import register_exception_handlers
from backend.infra.limiter import limiter

request_logger = logging.getLogger("backend.request")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Cleanup database connection pool
    await close_db()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="UniLaunch Platform Backend API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Attach Rate Limiter to app state
    app.state.limiter = limiter

    # Rate Limiter Middleware
    app.add_middleware(SlowAPIMiddleware)

    @app.middleware("http")
    async def request_tracing(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID")
        if not request_id or len(request_id) > 128:
            request_id = str(uuid.uuid4())

        started_at = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        response.headers["X-Request-ID"] = request_id
        request_logger.info(
            "request_completed request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        return response

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.public_app_url, "http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Exception Handlers
    register_exception_handlers(app)

    # Health Check
    @app.get("/health", tags=["health"])
    async def health():
        return {"status": "ok"}

    # Include Routers with /api/v1 prefix
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(public_leads_router, prefix="/api/v1")
    app.include_router(leads_router, prefix="/api/v1")

    return app


app = create_app()


def start():
    settings = get_settings()
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )


if __name__ == "__main__":
    start()
