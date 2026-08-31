import time

import pytest
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient

from backend.error import UnauthorizedError
from backend.infra.hmac import HmacAuthMiddleware, verify_hmac_signature
from backend.infra.password import hash_password, verify_password
from backend.infra.security import CurrentUserId, get_current_user_id


def test_password_hash_and_verify():
    pwd = "MinhaSenhaSuperForte123"
    hashed = hash_password(pwd)
    assert hashed.startswith("$argon2")

    # Correct password
    assert verify_password(pwd, hashed) is True

    # Wrong password
    assert verify_password("SenhaErrada", hashed) is False

    # Empty inputs
    assert verify_password("", hashed) is False
    assert verify_password(pwd, "") is False

    with pytest.raises(ValueError):
        hash_password("")


def test_hmac_signature_verification():
    secret = "secret-chave-123"
    path = "/api/v1/usuarios/1"
    user_id = "user_abc"
    now = int(time.time())

    import hashlib
    import hmac

    payload = f"{now}:{path}:{user_id}".encode()
    signature = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    # Valid
    assert verify_hmac_signature(path, user_id, now, signature, secret, now=now) is True

    # Expired timestamp (> 30s)
    assert verify_hmac_signature(path, user_id, now - 35, signature, secret, now=now) is False

    # Invalid signature
    assert verify_hmac_signature(path, user_id, now, "invalidsig", secret, now=now) is False


@pytest.mark.asyncio
async def test_hmac_middleware_and_security_dependency():
    app = FastAPI()
    app.add_middleware(HmacAuthMiddleware)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/protected")
    async def protected_endpoint(user_id: CurrentUserId):
        return {"user_id": user_id}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Exempt path succeeds
        h_res = await client.get("/health")
        assert h_res.status_code == 200

        # Missing headers fails with 401
        res1 = await client.get("/protected")
        assert res1.status_code == 401

        # Invalid timestamp fails with 401
        res2 = await client.get(
            "/protected",
            headers={
                "x-user-id": "123",
                "x-timestamp": "invalid_int",
                "x-signature": "some_sig",
            },
        )
        assert res2.status_code == 401

        # Valid HMAC request
        now = int(time.time())
        secret = "change-me-in-production"
        path = "/protected"
        user_id = "user_456"

        import hashlib
        import hmac

        payload = f"{now}:{path}:{user_id}".encode()
        sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

        res3 = await client.get(
            "/protected",
            headers={
                "x-user-id": user_id,
                "x-timestamp": str(now),
                "x-signature": sig,
            },
        )
        assert res3.status_code == 200
        assert res3.json()["user_id"] == "user_456"


@pytest.mark.asyncio
async def test_get_current_user_id_fallback():
    # Direct header fallback
    req = Request({"type": "http", "headers": [(b"x-user-id", b"direct_user_789")]})
    uid = await get_current_user_id(req)
    assert uid == "direct_user_789"

    # Missing header raises UnauthorizedError
    empty_req = Request({"type": "http", "headers": []})
    with pytest.raises(UnauthorizedError):
        await get_current_user_id(empty_req)
