from __future__ import annotations


class HitRanker:
    def rank(self, hit_evidence: list[dict]) -> list[dict]:
        ranked = []
        for evidence in hit_evidence:
            screening_component = (evidence.get("screeningScore") or 0.0) / 100
            score = (
                evidence["ruleScore"] * 0.42
                + evidence["modelProbability"] * 0.32
                + screening_component * 0.16
                + evidence.get("historicalSimilarity", 0.0) * 0.1
            )
            if evidence.get("criticalMismatches"):
                score *= 0.25
            elif evidence.get("highMismatches"):
                score *= 0.55
            evidence = dict(evidence)
            evidence["matchScore"] = round(max(0.0, min(1.0, score)), 4)
            ranked.append(evidence)
        ranked.sort(key=lambda item: item["matchScore"], reverse=True)
        for idx, item in enumerate(ranked, start=1):
            item["rank"] = idx
        return ranked

