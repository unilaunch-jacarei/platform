import hashlib
import hmac
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from backend.config import get_settings


def verify_hmac_signature(
    path: str,
    user_id: str,
    timestamp: int,
    signature_hex: str,
    secret: str,
    now: int | None = None,
) -> bool:
    """Valida a assinatura HMAC-SHA256 e o desvio de relógio (máximo 30 segundos)."""
    if now is None:
        now = int(time.time())

    if abs(now - timestamp) > 30:
        return False

    payload = f"{timestamp}:{path}:{user_id}".encode()
    key = secret.encode("utf-8")
    expected_signature = hmac.new(key, payload, hashlib.sha256).hexdigest()

    return hmac.compare_digest(expected_signature.lower(), signature_hex.lower())


class HmacAuthMiddleware(BaseHTTPMiddleware):
    """Middleware que valida a assinatura HMAC do BFF para requisições no backend."""

    def __init__(self, app, exempt_paths: set[str] | None = None):
        super().__init__(app)
        self.exempt_paths = exempt_paths or {"/health", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Permite acesso sem assinatura a endpoints públicos e de documentação
        if (
            request.url.path in self.exempt_paths
            or request.url.path.startswith("/docs")
            or request.url.path.startswith("/openapi")
        ):
            return await call_next(request)

        user_id = request.headers.get("x-user-id")
        timestamp_header = request.headers.get("x-timestamp")
        signature = request.headers.get("x-signature")

        if not user_id or not timestamp_header or not signature:
            return JSONResponse(
                status_code=401,
                content={"error": "Não autorizado: cabeçalhos de autenticação ausentes"},
            )

        try:
            timestamp = int(timestamp_header)
        except ValueError:
            return JSONResponse(
                status_code=401,
                content={"error": "Não autorizado: timestamp inválido"},
            )

        settings = get_settings()
        if not verify_hmac_signature(
            path=request.url.path,
            user_id=user_id,
            timestamp=timestamp,
            signature_hex=signature,
            secret=settings.internal_secret,
        ):
            return JSONResponse(
                status_code=401,
                content={"error": "Não autorizado: assinatura inválida ou expirada"},
            )

        request.state.user_id = user_id
        return await call_next(request)
