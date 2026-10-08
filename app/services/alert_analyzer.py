from __future__ import annotations

from app.core.config import get_settings
from app.repositories.memory_store import store
from app.schemas.alert import AlertIn, HitIn
from app.schemas.analysis import (
    AnalysisResponse,
    AuditInfo,
    BestHit,
    HistoricalEvidence,
    ModelAnalysis,
    RankedHit,
)
from app.schemas.common import Classification
from app.services.attribute_matcher import AttributeMatcher
from app.services.case_retrieval import CaseRetrievalService
from app.services.hit_ranker import HitRanker
from app.services.llm_service import get_llm_provider
from app.services.ml_service import MLModelService
from app.services.recommendation_service import RecommendationService
from app.services.risk_engine import RiskEngine
from app.services.rule_engine import RuleEngine
from app.services.scoring_engine import ScoringEngine
from app.utils.hashing import stable_input_hash


class AlertAnalyzer:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.rule_engine = RuleEngine()
        self.attribute_matcher = AttributeMatcher(weights=self.rule_engine.weights)
        self.scoring_engine = ScoringEngine()
        self.ml_service = MLModelService()
        self.hit_ranker = HitRanker()
        self.risk_engine = RiskEngine()
        self.case_retrieval = CaseRetrievalService()
        self.recommendations = RecommendationService()
        self.llm = get_llm_provider()

    async def analyze(self, alert: AlertIn) -> AnalysisResponse:
        alert_payload = alert.model_dump(by_alias=True, mode="json")
        input_hash = stable_input_hash(alert_payload)
        hit_evidence: list[dict] = []
        for hit in alert.hits:
            attributes = self.attribute_matcher.compare_all(alert.third_party, hit)
            rule_result = self.rule_engine.evaluate(attributes)
            features = self.scoring_engine.build_features(
                attributes, hit.score, hit.level, hit.list_type, hit.source
            )
            model_probability = self.ml_service.predict_probability(features)
            classification = self._combine_classification(rule_result, model_probability)
            hit_evidence.append(
                {
                    "hitId": hit.hit_id,
                    "name": hit.name,
                    "screeningScore": hit.score,
                    "screeningLevel": hit.level,
                    "listType": hit.list_type,
                    "source": hit.source,
                    "attributes": attributes,
                    "features": features,
                    "ruleResult": rule_result,
                    "ruleScore": rule_result["ruleScore"],
                    "modelProbability": round(model_probability, 4),
                    "classification": classification,
                    "criticalMismatches": rule_result["criticalMismatches"],
                    "highMismatches": rule_result["highMismatches"],
                    "historicalSimilarity": 0.0,
                }
            )

        ranked = self.hit_ranker.rank(hit_evidence)
        best = ranked[0]
        historical_cases = self.case_retrieval.similar_cases(
            self.case_retrieval.analysis_text(alert_payload, best["attributes"]),
            top_k=5,
        )
        historical_similarity = historical_cases[0]["similarity"] if historical_cases else 0.0
        best["historicalSimilarity"] = historical_similarity
        risk_level = self.risk_engine.calculate(best, self.rule_engine.config)
        classification = best["classification"]
        data_quality = self._data_quality(best["attributes"])
        confidence = self.scoring_engine.confidence(
            rule_score=best["ruleScore"],
            model_probability=best["modelProbability"],
            data_quality=data_quality,
            historical_similarity=historical_similarity,
            has_override=bool(best["ruleResult"].get("override")),
        )
        if classification == Classification.FALSE_POSITIVE and (
            best["criticalMismatches"] or len(best["highMismatches"]) >= 2
        ):
            confidence = max(confidence, 88)
        actions = self.recommendations.actions(classification, risk_level)

        llm_payload = {
            "thirdParty": alert.third_party.model_dump(by_alias=True, mode="json"),
            "bestHit": self._best_hit_dict(self._hit_from_best(best)).model_dump(
                by_alias=True, mode="json"
            ),
            "attributeAnalysis": {
                key: value.model_dump(mode="json") for key, value in best["attributes"].items()
            },
            "ruleAnalysis": best["ruleResult"],
            "mlPrediction": {
                "prediction": self._ml_prediction(best["modelProbability"]),
                "probability": best["modelProbability"],
            },
            "historicalCases": historical_cases,
            "classification": classification,
            "recommendedActions": actions,
            "riskExplanation": f"Risk is {risk_level} based on list/screening level and identity evidence.",
        }
        llm_result = await self.llm.generate_analysis(llm_payload)

        response = AnalysisResponse(
            alertId=alert.alert_id,
            classification=classification,
            confidence=confidence,
            riskLevel=risk_level,
            bestHit=self._best_hit_dict(self._hit_from_best(best)),
            rankedHits=[
                RankedHit(
                    hitId=item["hitId"],
                    rank=item["rank"],
                    matchScore=item["matchScore"],
                    classification=item["classification"],
                )
                for item in ranked
            ],
            attributeAnalysis=best["attributes"],
            modelAnalysis=ModelAnalysis(
                modelVersion=str(self.ml_service.metadata.get("modelVersion", "1.0.0")),
                prediction=self._ml_prediction(best["modelProbability"]),
                probability=best["modelProbability"],
            ),
            historicalEvidence=HistoricalEvidence(
                similarCasesFound=len(historical_cases),
                cases=historical_cases,
            ),
            reasoning=llm_result.get("reasoning") or [],
            recommendedActions=llm_result.get("recommendedActions") or actions,
            summary=llm_result.get("summary"),
            audit=AuditInfo(
                ruleVersion=self.rule_engine.version,
                modelVersion=str(self.ml_service.metadata.get("modelVersion", "1.0.0")),
                inputHash=input_hash,
                analystReviewRequired=True,
            ),
        )
        store.save_alert(alert.alert_id, alert_payload)
        store.save_analysis(alert.alert_id, response.model_dump(by_alias=True, mode="json"))
        return response

    @staticmethod
    def _combine_classification(rule_result: dict, model_probability: float) -> Classification:
        rule_classification = rule_result["classification"]
        if rule_result.get("override"):
            return Classification.FALSE_POSITIVE
        if rule_classification == Classification.TRUE_ALERT and model_probability >= 0.65:
            return Classification.TRUE_ALERT
        if rule_classification == Classification.FALSE_POSITIVE and model_probability <= 0.55:
            return Classification.FALSE_POSITIVE
        if model_probability >= 0.9 and rule_result["ruleScore"] >= 0.8:
            return Classification.TRUE_ALERT
        if model_probability <= 0.2 and rule_result["ruleScore"] <= 0.35:
            return Classification.FALSE_POSITIVE
        return Classification.INCONCLUSIVE

    @staticmethod
    def _ml_prediction(probability: float) -> str:
        return "TRUE_POSITIVE" if probability >= 0.5 else "FALSE_POSITIVE"

    @staticmethod
    def _data_quality(attributes: dict) -> float:
        total = len(attributes) or 1
        available = sum(1 for value in attributes.values() if value.result != "NOT_AVAILABLE")
        return available / total

    @staticmethod
    def _hit_from_best(best: dict) -> HitIn:
        return HitIn(
            hitId=best["hitId"],
            name=best["name"],
            score=best.get("screeningScore"),
            level=best.get("screeningLevel"),
            listType=best.get("listType"),
            source=best.get("source"),
        )

    @staticmethod
    def _best_hit_dict(hit: HitIn) -> BestHit:
        return BestHit(
            hitId=hit.hit_id,
            name=hit.name,
            screeningScore=hit.score,
            screeningLevel=hit.level,
            listType=hit.list_type,
            source=hit.source,
        )

