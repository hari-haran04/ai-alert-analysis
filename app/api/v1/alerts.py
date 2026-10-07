from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import rate_limiter, require_role
from app.repositories.memory_store import store
from app.schemas.alert import AlertIn
from app.schemas.analysis import AnalysisResponse
from app.services.alert_analyzer import AlertAnalyzer

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    dependencies=[Depends(rate_limiter), Depends(require_role("analyst", "admin"))],
)
async def analyze_alert(payload: AlertIn) -> AnalysisResponse:
    return await AlertAnalyzer().analyze(payload)


@router.get("/{alert_id}", dependencies=[Depends(require_role("analyst", "admin"))])
async def get_alert(alert_id: str) -> dict:
    alert = store.get_alert(alert_id)
    analysis = store.get_analysis(alert_id)
    if not alert and not analysis:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"alert": alert, "analysis": analysis}

