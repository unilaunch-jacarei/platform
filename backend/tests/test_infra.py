import hashlib
import hmac

from fastapi import Request

from backend.config import get_settings
from backend.infra.limiter import get_client_address


def _request(client_ip: bytes | None, signature: bytes | None) -> Request:
    headers = []
    if client_ip is not None:
        headers.append((b"x-client-ip", client_ip))
    if signature is not None:
        headers.append((b"x-client-ip-signature", signature))
    return Request({"type": "http", "headers": headers, "client": ("127.0.0.1", 1234)})


def test_client_address_rejects_invalid_forwarded_ip():
    request = _request(b"not-an-ip", b"invalid")
    assert get_client_address(request) == "127.0.0.1"


def test_client_address_accepts_signed_forwarded_ip():
    secret = get_settings().internal_secret
    client_ip = "203.0.113.10"
    signature = hmac.new(secret.encode(), client_ip.encode(), hashlib.sha256).hexdigest()

    request = _request(client_ip.encode(), signature.encode())

    assert get_client_address(request) == client_ip
