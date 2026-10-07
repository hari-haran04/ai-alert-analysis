from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import require_role
from app.repositories.memory_store import store
from app.schemas.case import HistoricalCaseIn
from app.services.case_retrieval import CaseRetrievalService

router = APIRouter(prefix="/cases", tags=["cases"])
service = CaseRetrievalService()


@router.post("", dependencies=[Depends(require_role("analyst", "admin"))])
async def create_case(payload: HistoricalCaseIn) -> dict:
    return service.add_case(payload)


@router.get("/similar/{alert_id}", dependencies=[Depends(require_role("analyst", "admin"))])
async def similar_cases(alert_id: str) -> dict:
    alert = store.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"cases": service.similar_cases(service.alert_text(alert), top_k=5)}


@router.get("/{case_id}", dependencies=[Depends(require_role("analyst", "admin"))])
async def get_case(case_id: str) -> dict:
    case = service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

