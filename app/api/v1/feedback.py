from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends

from app.core.security import require_role
from app.repositories.memory_store import store
from app.schemas.feedback import FeedbackIn, FeedbackOut

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackOut, dependencies=[Depends(require_role("analyst", "admin"))])
async def create_feedback(payload: FeedbackIn) -> FeedbackOut:
    feedback_id = f"FDB-{uuid4().hex[:12].upper()}"
    data = payload.model_dump(by_alias=True, mode="json")
    data["feedbackId"] = feedback_id
    store.save_feedback(feedback_id, data)
    return FeedbackOut(**data)

