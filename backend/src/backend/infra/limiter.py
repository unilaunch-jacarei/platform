import hashlib
import hmac
import ipaddress

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from backend.config import get_settings


def get_client_address(request: Request) -> str:
    """Uses a client IP only when its value was signed by the BFF."""
    candidate = request.headers.get("X-Client-IP", "").strip()
    signature = request.headers.get("X-Client-IP-Signature", "")
    if candidate and signature:
        try:
            ipaddress.ip_address(candidate)
        except ValueError:
            pass
        else:
            secret = get_settings().internal_secret.encode()
            expected = hmac.new(secret, candidate.encode(), hashlib.sha256).hexdigest()
            if hmac.compare_digest(signature, expected):
                return candidate
    return get_remote_address(request)


limiter = Limiter(
    key_func=get_client_address,
    default_limits=["120/minute"],
    storage_uri=get_settings().rate_limit_storage_uri,
)
