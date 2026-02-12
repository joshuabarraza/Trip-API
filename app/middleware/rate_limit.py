from starlette.requests import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings


def rate_limit_key_func(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()

    return get_remote_address(request)


limiter = Limiter(
    key_func = rate_limit_key_func,
    default_limits = [f"{settings.rate_limit_per_minute}/minute"]
)
