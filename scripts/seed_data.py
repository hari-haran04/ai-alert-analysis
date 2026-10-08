from __future__ import annotations

from app.schemas.case import HistoricalCaseIn
from app.services.case_retrieval import CaseRetrievalService


def seed() -> None:
    service = CaseRetrievalService()
    cases = [
        HistoricalCaseIn(
            caseId="CASE-001",
            alertId="ALT-HIST-1001",
            classification="TRUE_ALERT",
            analystDecision="TRUE_ALERT",
            summary="Gold Mayning 000 matched sanctions ownership record with registration and tax ID match.",
            attributes={
                "thirdParty": {
                    "name": "Gold Mayning 000",
                    "country": "Russia",
                    "city": "Yakutsk",
                    "registrationNumber": "1201400007291",
                    "taxId": "1435353596",
                },
                "bestHit": {
                    "name": "Gold Mayning 000",
                    "country": "Russia",
                    "city": "Yakutsk",
                    "listType": "US_50PLUS",
                    "source": "KHARON",
                },
                "attributeAnalysis": {
                    "name": "MATCH",
                    "country": "MATCH",
                    "city": "MATCH",
                    "registrationNumber": "MATCH",
                    "taxId": "MATCH",
                },
            },
            reasoning=[
                "Name matched",
                "Registration number matched",
                "Tax ID matched",
            ],
        ),
        HistoricalCaseIn(
            caseId="CASE-002",
            alertId="ALT-HIST-1002",
            classification="FALSE_POSITIVE",
            analystDecision="FALSE_POSITIVE",
            summary="Michael Jordan alert closed due to DOB and passport mismatch.",
            attributes={
                "thirdParty": {
                    "name": "Michael Jordan",
                    "country": "USA",
                    "city": "Chicago",
                    "dateOfBirth": "1985-06-20",
                    "passportNumberMasked": "P123****5678",
                },
                "bestHit": {
                    "name": "Michael B Jordan",
                    "country": "USA",
                    "city": "New York",
                    "dateOfBirth": "1960-01-01",
                    "passportNumberMasked": "P999****9999",
                    "listType": "WATCHLIST",
                    "source": "FIRCO",
                },
                "attributeAnalysis": {
                    "name": "PARTIAL_MATCH",
                    "country": "MATCH",
                    "city": "MISMATCH",
                    "dateOfBirth": "MISMATCH",
                    "passportNumber": "MISMATCH",
                },
            },
            reasoning=[
                "Name partially matched",
                "Country matched",
                "City mismatch",
                "DOB mismatch",
                "Passport mismatch",
            ],
        ),
        HistoricalCaseIn(
            caseId="CASE-003",
            alertId="ALT-HIST-1003",
            classification="INCONCLUSIVE",
            analystDecision="INCONCLUSIVE",
            summary="Organization name and country matched but identifiers were unavailable.",
            attributes={
                "thirdParty": {
                    "name": "ABC Trading Ltd",
                    "country": "UAE",
                    "city": "Dubai",
                },
                "bestHit": {
                    "name": "ABC Trading Limited",
                    "country": "UAE",
                    "city": "Dubai",
                    "listType": "WATCHLIST",
                },
                "attributeAnalysis": {
                    "name": "MATCH",
                    "country": "MATCH",
                    "city": "MATCH",
                    "registrationNumber": "NOT_AVAILABLE",
                    "taxId": "NOT_AVAILABLE",
                },
            },
            reasoning=[
                "Name matched through company suffix normalization",
                "Registration not available",
                "Tax ID not available",
            ],
        ),
        HistoricalCaseIn(
            caseId="CASE-004",
            alertId="ALT-HIST-1004",
            classification="FALSE_POSITIVE",
            analystDecision="FALSE_POSITIVE",
            summary="John Smith watchlist alert closed because passport and date of birth contradicted the name match.",
            attributes={
                "thirdParty": {
                    "name": "John Smith",
                    "country": "USA",
                    "city": "Boston",
                    "dateOfBirth": "1990-02-11",
                    "passportNumberMasked": "P555****1111",
                },
                "bestHit": {
                    "name": "John Smyth",
                    "country": "USA",
                    "city": "Miami",
                    "dateOfBirth": "1972-09-03",
                    "passportNumberMasked": "P777****2222",
                    "listType": "WATCHLIST",
                },
                "attributeAnalysis": {
                    "name": "PARTIAL_MATCH",
                    "country": "MATCH",
                    "city": "MISMATCH",
                    "dateOfBirth": "MISMATCH",
                    "passportNumber": "MISMATCH",
                },
            },
            reasoning=[
                "Name partially matched",
                "DOB mismatch",
                "Passport mismatch",
                "Closed as false positive",
            ],
        ),
        HistoricalCaseIn(
            caseId="CASE-005",
            alertId="ALT-HIST-1005",
            classification="TRUE_ALERT",
            analystDecision="TRUE_ALERT",
            summary="Sakha Gold AO matched entity record by organization name, Russia country, and registration number.",
            attributes={
                "thirdParty": {
                    "name": "Sakha Gold AO",
                    "country": "Russia",
                    "city": "Aldan",
                    "registrationNumber": "7743001111",
                },
                "bestHit": {
                    "name": "Sakha Gold Joint Stock Company",
                    "country": "Russia",
                    "city": "Aldan",
                    "listType": "US_50PLUS",
                },
                "attributeAnalysis": {
                    "name": "PARTIAL_MATCH",
                    "country": "MATCH",
                    "city": "MATCH",
                    "registrationNumber": "MATCH",
                },
            },
            reasoning=[
                "Organization suffix normalized",
                "Country matched",
                "City matched",
                "Registration number matched",
            ],
        ),
        HistoricalCaseIn(
            caseId="CASE-006",
            alertId="ALT-HIST-1006",
            classification="FALSE_POSITIVE",
            analystDecision="FALSE_POSITIVE",
            summary="Volga Energy alert closed because the tax ID and registration number belonged to a different company.",
            attributes={
                "thirdParty": {
                    "name": "Volga Energy LLC",
                    "country": "Russia",
                    "registrationNumber": "5500123000",
                    "taxId": "7700550011",
                },
                "bestHit": {
                    "name": "Volga Energy Limited",
                    "country": "Russia",
                    "registrationNumber": "9900990099",
                    "taxId": "1111222233",
                    "listType": "SANCTIONS",
                },
                "attributeAnalysis": {
                    "name": "PARTIAL_MATCH",
                    "country": "MATCH",
                    "registrationNumber": "MISMATCH",
                    "taxId": "MISMATCH",
                },
            },
            reasoning=[
                "Name partially matched",
                "Tax ID mismatch",
                "Registration number mismatch",
                "Closed as false positive",
            ],
        ),
        HistoricalCaseIn(
            caseId="CASE-007",
            alertId="ALT-HIST-1007",
            classification="INCONCLUSIVE",
            analystDecision="INCONCLUSIVE",
            summary="Maria Garcia PEP alert required additional information because only name and country matched.",
            attributes={
                "thirdParty": {
                    "name": "Maria Garcia",
                    "country": "Mexico",
                    "city": "Monterrey",
                },
                "bestHit": {
                    "name": "Maria Garcia",
                    "country": "Mexico",
                    "listType": "PEP",
                },
                "attributeAnalysis": {
                    "name": "MATCH",
                    "country": "MATCH",
                    "city": "NOT_AVAILABLE",
                    "dateOfBirth": "NOT_AVAILABLE",
                    "passportNumber": "NOT_AVAILABLE",
                },
            },
            reasoning=[
                "Name matched",
                "Country matched",
                "Critical identifiers not available",
                "Requested additional information",
            ],
        ),
        HistoricalCaseIn(
            caseId="CASE-008",
            alertId="ALT-HIST-1008",
            classification="TRUE_ALERT",
            analystDecision="TRUE_ALERT",
            summary="North River Metals matched sanctions entity through exact tax ID, registration number, and address similarity.",
            attributes={
                "thirdParty": {
                    "name": "North River Metals Ltd",
                    "country": "United Kingdom",
                    "city": "London",
                    "registrationNumber": "UK445566",
                    "taxId": "GB998877",
                    "address": "10 Dock Road London",
                },
                "bestHit": {
                    "name": "North River Metals Limited",
                    "country": "United Kingdom",
                    "city": "London",
                    "registrationNumber": "UK445566",
                    "taxId": "GB998877",
                    "address": "10 Dock Rd London",
                    "listType": "UK_SANCTIONS",
                },
                "attributeAnalysis": {
                    "name": "MATCH",
                    "country": "MATCH",
                    "city": "MATCH",
                    "registrationNumber": "MATCH",
                    "taxId": "MATCH",
                    "address": "PARTIAL_MATCH",
                },
            },
            reasoning=[
                "Name matched",
                "Registration number matched",
                "Tax ID matched",
                "Address partially matched",
            ],
        ),
    ]
    for case in cases:
        service.add_case(case)


if __name__ == "__main__":
    seed()
    print("Seeded historical cases")

