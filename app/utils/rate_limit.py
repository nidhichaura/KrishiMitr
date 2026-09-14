"""Small in-memory rate limiter for the public demo API.

Use Redis or an API gateway when deploying more than one application instance.
"""
from collections import defaultdict, deque
from time import monotonic

from fastapi import HTTPException, Request, status

from app.config import settings

_requests: dict[str, deque[float]] = defaultdict(deque)


def enforce_api_rate_limit(request: Request) -> None:
    client = request.client.host if request.client else "unknown"
    now = monotonic()
    window = _requests[client]
    while window and now - window[0] >= 60:
        window.popleft()
    if len(window) >= settings.API_RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please wait a minute and try again.",
        )
    window.append(now)
