from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.v1 import alerts, cases, feedback, health, models, rules
from app.core.config import get_settings
from app.core.exceptions import AppError, app_error_handler
from app.core.logging import configure_logging
from app.core.security import request_context_middleware
from scripts.seed_data import seed


settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "AI-assisted analyst copilot for sanctions and embargo screening investigations. "
        "The API provides recommendations and supporting evidence; final compliance "
        "decisions remain with human analysts."
    ),
)

app.middleware("http")(request_context_middleware)
app.add_exception_handler(AppError, app_error_handler)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "INVALID_ALERT",
                "message": "The alert payload is invalid",
                "requestId": request_id,
                "details": exc.errors(),
            }
        },
    )


for router in [
    health.router,
    alerts.router,
    cases.router,
    feedback.router,
    models.router,
    rules.router,
]:
    app.include_router(router, prefix=settings.api_v1_prefix if router is not health.router else "")


@app.on_event("startup")
async def seed_demo_cases() -> None:
    seed()

