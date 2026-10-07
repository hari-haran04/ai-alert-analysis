from __future__ import annotations

from app.schemas.case import HistoricalCaseIn
from app.services.case_retrieval import CaseRetrievalService


def seed() -> None:
    service = CaseRetrievalService()
    cases = [
        HistoricalCaseIn(
            caseId="CASE-001",
            alertId="ALT-1001",
            classification="TRUE_ALERT",
            analystDecision="TRUE_ALERT",
            summary="Gold Mayning 000 matched sanctions ownership record with registration and tax ID match.",
            attributes={"country": "Russia", "city": "Yakutsk"},
            reasoning=[
                "Name matched",
                "Registration number matched",
                "Tax ID matched",
            ],
        ),
        HistoricalCaseIn(
            caseId="CASE-002",
            alertId="ALT-1002",
            classification="FALSE_POSITIVE",
            analystDecision="FALSE_POSITIVE",
            summary="Michael Jordan alert closed due to DOB and passport mismatch.",
            attributes={"country": "USA", "city": "Chicago"},
            reasoning=["DOB mismatch", "Passport mismatch"],
        ),
        HistoricalCaseIn(
            caseId="CASE-003",
            alertId="ALT-1003",
            classification="INCONCLUSIVE",
            analystDecision="INCONCLUSIVE",
            summary="Organization name and country matched but identifiers were unavailable.",
            attributes={"country": "UAE"},
            reasoning=["Name partially matched", "Registration not available"],
        ),
    ]
    for case in cases:
        service.add_case(case)


if __name__ == "__main__":
    seed()
    print("Seeded historical cases")

