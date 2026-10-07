from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Callable
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, Header, HTTPException, Request

from app.core.config import Settings, get_settings


RequestId = Annotated[str | None, Header(alias="X-Request-ID")]
ApiKey = Annotated[str | None, Header(alias="X-API-Key")]
RoleHeader = Annotated[str | None, Header(alias="X-Role")]

_rate_window: dict[str, deque[float]] = defaultdict(deque)


async def request_context_middleware(request: Request, call_next: Callable):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


def require_api_key(
    api_key: ApiKey = None, settings: Settings = Depends(get_settings)
) -> None:
    if not settings.auth_enabled:
        return
    if api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


def require_role(*allowed_roles: str):
    def dependency(
        role: RoleHeader = "analyst",
        _: None = Depends(require_api_key),
    ) -> None:
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient role")

    return dependency


def rate_limiter(
    request: Request, settings: Settings = Depends(get_settings)
) -> None:
    client = request.client.host if request.client else "unknown"
    now = time.monotonic()
    calls = _rate_window[client]
    while calls and now - calls[0] > 60:
        calls.popleft()
    if len(calls) >= settings.rate_limit_per_minute:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    calls.append(now)

