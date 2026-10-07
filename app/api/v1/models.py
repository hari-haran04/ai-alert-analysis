from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security import require_role
from app.services.ml_service import MLModelService

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", dependencies=[Depends(require_role("analyst", "admin"))])
async def list_models() -> dict:
    service = MLModelService()
    return {"models": [service.metadata_response()]}

