import pytest
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient
from limits import parse
from slowapi.errors import RateLimitExceeded
from slowapi.wrappers import Limit

from backend.error import (
    AppException,
    BadRequestError,
    ConflictError,
    NotFoundError,
    UnauthorizedError,
    register_exception_handlers,
)


def test_exception_classes():
    nf = NotFoundError(message="Not found", details={"id": 1})
    assert nf.status_code == 404
    assert nf.code == "not_found"

    un = UnauthorizedError(message="Unauthorized")
    assert un.status_code == 401
    assert un.code == "unauthorized"

    br = BadRequestError(message="Bad request")
    assert br.status_code == 400
    assert br.code == "bad_request"

    cf = ConflictError(message="Conflict")
    assert cf.status_code == 409
    assert cf.code == "conflict"


@pytest.mark.asyncio
async def test_exception_handlers():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/app-error")
    async def raise_app_error():
        raise BadRequestError(message="Erro customizado", details={"campo": "email"})

    @app.get("/server-error")
    async def raise_server_error():
        raise AppException(message="Falha interna grave", status_code=500, code="server_fail")

    @app.get("/rate-limit-error")
    async def raise_rate_limit(request: Request):
        limit = Limit(parse("10/minute"), lambda: "key", None, False, None, None, None, 1, False)
        raise RateLimitExceeded(limit)

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Custom 400 error
        res1 = await client.get("/app-error")
        assert res1.status_code == 400
        assert res1.json()["error"] == "Erro customizado"
        assert res1.json()["details"] == {"campo": "email"}

        # Custom 500 error
        res2 = await client.get("/server-error")
        assert res2.status_code == 500
        assert res2.json()["error"] == "Falha interna grave"

        # Rate limit 429 error
        res3 = await client.get("/rate-limit-error")
        assert res3.status_code == 429
        assert res3.json()["code"] == "rate_limit_exceeded"

    # Test generic unhandled exception handler directly
    handler = app.exception_handlers[Exception]
    req = Request({"type": "http", "method": "GET", "path": "/"})
    res = await handler(req, RuntimeError("Erro inesperado"))
    assert res.status_code == 500
    import json

    data = json.loads(res.body.decode("utf-8"))
    assert data == {"error": "Erro interno da aplicação", "code": "internal_error"}
