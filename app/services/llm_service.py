from __future__ import annotations

import httpx

from app.core.config import get_settings
from app.schemas.common import Classification


class LLMProvider:
    async def generate_analysis(self, evidence: dict) -> dict:
        raise NotImplementedError


class LocalGroundedLLMProvider(LLMProvider):
    async def generate_analysis(self, evidence: dict) -> dict:
        best_hit = evidence.get("bestHit") or {}
        classification = evidence.get("classification")
        attribute_analysis = evidence.get("attributeAnalysis", {})
        mismatches = [
            item["evidence"]
            for item in attribute_analysis.values()
            if item.get("result") == "MISMATCH"
        ]
        matches = [
            item["evidence"]
            for item in attribute_analysis.values()
            if item.get("result") in {"MATCH", "PARTIAL_MATCH"}
        ]
        if classification == Classification.TRUE_ALERT:
            summary = (
                f"AI-assisted assessment recommends TRUE_ALERT for {best_hit.get('hitId')} "
                "based on strong identity evidence."
            )
        elif classification == Classification.FALSE_POSITIVE:
            summary = (
                f"AI-assisted assessment recommends FALSE_POSITIVE for {best_hit.get('hitId')} "
                "because stronger identity attributes contradict the match."
            )
        else:
            summary = (
                f"AI-assisted assessment is INCONCLUSIVE for {best_hit.get('hitId')} "
                "because available evidence is insufficient or mixed."
            )
        reasoning = [*matches[:6], *mismatches[:6]]
        if not reasoning:
            reasoning = ["No sufficient attribute evidence was available."]
        return {
            "summary": summary,
            "reasoning": reasoning,
            "keyEvidence": matches[:5],
            "riskExplanation": evidence.get("riskExplanation", ""),
            "recommendedActions": evidence.get("recommendedActions", []),
        }


class OpenAILLMProvider(LLMProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate_analysis(self, evidence: dict) -> dict:
        if not self.settings.openai_api_key:
            return await LocalGroundedLLMProvider().generate_analysis(evidence)
        prompt = {
            "instruction": (
                "Only use evidence provided in the input. Never create missing attributes. "
                "Do not override deterministic compliance rules. Return concise JSON with "
                "summary, reasoning, keyEvidence, riskExplanation, recommendedActions."
            ),
            "evidence": evidence,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
                json={
                    "model": self.settings.llm_model,
                    "input": [{"role": "user", "content": str(prompt)}],
                },
            )
            response.raise_for_status()
        text = response.json().get("output_text", "")
        return {
            "summary": text[:500],
            "reasoning": evidence.get("reasoning", []),
            "keyEvidence": [],
            "riskExplanation": "",
            "recommendedActions": evidence.get("recommendedActions", []),
        }


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    if settings.llm_provider in {"openai", "azure_openai"}:
        return OpenAILLMProvider()
    return LocalGroundedLLMProvider()

