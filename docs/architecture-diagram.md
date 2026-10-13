# AI-Assisted Alert Analysis Architecture

```mermaid
flowchart LR
    user["Compliance analyst"]
    ui["Static analyst UI<br/>HTML, CSS, JavaScript"]
    postman["Postman or API client"]

    subgraph api["FastAPI application"]
        alerts["POST /api/v1/alerts/analyze"]
        getAlert["GET /api/v1/alerts/:alertId"]
        casesApi["Cases, feedback, models, rules APIs"]
        validation["Pydantic validation<br/>AlertIn, ThirdPartyIn, HitIn"]
    end

    subgraph orchestrator["Analysis orchestration"]
        analyzer["AlertAnalyzer"]
        matcher["AttributeMatcher"]
        rules["RuleEngine<br/>rules/matching_rules.yaml"]
        features["ScoringEngine<br/>feature builder"]
        ml["MLModelService<br/>XGBoost probability"]
        ranker["HitRanker"]
        cases["CaseRetrievalService<br/>top 3 similar cases"]
        risk["RiskEngine"]
        llm["LLM provider<br/>local grounded or OpenAI"]
        recommendations["RecommendationService"]
    end

    subgraph data["Data and model layer"]
        memory[("Prototype memory store")]
        model[("ml/models/entity_matcher.joblib")]
        metrics[("ml/metrics/entity_matcher_metrics.json")]
        seed["Seeded historical cases<br/>scripts/seed_data.py"]
        db[("Production target<br/>PostgreSQL + pgvector")]
    end

    subgraph output["Audit-ready response"]
        response["AnalysisResponse JSON"]
        classification["Classification<br/>TRUE_ALERT, FALSE_POSITIVE, INCONCLUSIVE"]
        evidence["Attribute evidence<br/>matches, mismatches, missing data"]
        ranked["Ranked hits<br/>match score"]
        historical["Historical evidence<br/>case similarity + matched fields"]
        audit["Audit metadata<br/>rule version, model version, input hash"]
    end

    user --> ui
    user --> postman
    ui --> alerts
    postman --> alerts
    alerts --> validation
    validation --> analyzer

    analyzer --> matcher
    matcher --> rules
    matcher --> features
    features --> ml
    rules --> ranker
    ml --> ranker
    ranker --> cases
    cases --> risk
    risk --> recommendations
    recommendations --> llm
    llm --> response

    seed --> memory
    analyzer --> memory
    memory --> getAlert
    memory --> cases
    ml --> model
    ml --> metrics
    db -. production persistence .- memory

    response --> classification
    response --> evidence
    response --> ranked
    response --> historical
    response --> audit
    response --> ui
    response --> postman
```

## Reading the Diagram

The main entry point is `POST /api/v1/alerts/analyze`. The API validates the alert payload, then `AlertAnalyzer` coordinates the full analysis pipeline.

The backend first compares the third party against each screening hit using `AttributeMatcher`. Those field-level results feed the rule engine and feature builder. The rule engine applies deterministic compliance logic, while `MLModelService` loads the trained XGBoost model and returns a match probability.

The hit ranker combines rule score, model probability, screening score, and historical similarity into a ranked hit list. Historical evidence is calculated by comparing the current third party against stored historical case third parties and returning the top three cases.

The LLM provider generates grounded reasoning text from already-computed evidence. It does not decide the final classification and does not override deterministic rules.

The output is an audit-ready JSON response with classification, confidence, risk level, ranked hits, attribute evidence, historical cases, reasoning, recommended actions, and audit metadata.
