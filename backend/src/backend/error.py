import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger("backend")


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str = "Erro interno da aplicação",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str = "internal_error",
        details: Any | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details


class NotFoundError(AppException):
    def __init__(self, message: str = "Recurso não encontrado", details: Any | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            code="not_found",
            details=details,
        )


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Não autorizado", details: Any | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="unauthorized",
            details=details,
        )


class BadRequestError(AppException):
    def __init__(self, message: str = "Requisição inválida", details: Any | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            code="bad_request",
            details=details,
        )


class ConflictError(AppException):
    def __init__(self, message: str = "Conflito de dados", details: Any | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            code="conflict",
            details=details,
        )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error("Erro interno da aplicação: %s", exc.message, exc_info=True)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "code": exc.code,
                **({"details": exc.details} if exc.details else {}),
            },
        )

    from slowapi.errors import RateLimitExceeded

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Muitas requisições. Por favor, tente novamente em alguns instantes.",
                "code": "rate_limit_exceeded",
                "detail": str(exc.detail),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Exceção não tratada na requisição: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Erro interno da aplicação", "code": "internal_error"},
        )
