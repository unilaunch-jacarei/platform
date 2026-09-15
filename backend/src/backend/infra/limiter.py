import ipaddress

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from backend.config import get_settings


def get_client_address(request: Request) -> str:
    """Uses the client IP forwarded by the private BFF when it is valid."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        candidate = forwarded.split(",", 1)[0].strip()
        try:
            ipaddress.ip_address(candidate)
            return candidate
        except ValueError:
            pass
    return get_remote_address(request)


limiter = Limiter(
    key_func=get_client_address,
    default_limits=["120/minute"],
    storage_uri=get_settings().rate_limit_storage_uri,
)
