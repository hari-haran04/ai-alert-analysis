from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security import require_role
from app.schemas.rule import RuleConfig
from app.services.rule_engine import RuleEngine

router = APIRouter(prefix="/rules", tags=["rules"])


@router.get("", dependencies=[Depends(require_role("analyst", "admin"))])
async def get_rules() -> dict:
    engine = RuleEngine()
    return engine.config


@router.put("", response_model=RuleConfig, dependencies=[Depends(require_role("admin"))])
async def put_rules(payload: RuleConfig) -> RuleConfig:
    engine = RuleEngine()
    return RuleConfig(**engine.update_config(payload.model_dump(mode="json")))

