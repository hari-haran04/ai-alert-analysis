from __future__ import annotations

from copy import deepcopy


class MemoryStore:
    """Small repository used by the prototype and tests.

    SQLAlchemy models and migrations are included for production persistence; this store
    keeps local demos fast and dependency-light.
    """

    def __init__(self) -> None:
        self.alerts: dict[str, dict] = {}
        self.analyses: dict[str, dict] = {}
        self.cases: dict[str, dict] = {}
        self.feedback: dict[str, dict] = {}

    def save_alert(self, alert_id: str, payload: dict) -> None:
        self.alerts[alert_id] = deepcopy(payload)

    def get_alert(self, alert_id: str) -> dict | None:
        alert = self.alerts.get(alert_id)
        return deepcopy(alert) if alert else None

    def save_analysis(self, alert_id: str, payload: dict) -> None:
        self.analyses[alert_id] = deepcopy(payload)

    def get_analysis(self, alert_id: str) -> dict | None:
        analysis = self.analyses.get(alert_id)
        return deepcopy(analysis) if analysis else None

    def save_case(self, case_id: str, payload: dict) -> None:
        self.cases[case_id] = deepcopy(payload)

    def get_case(self, case_id: str) -> dict | None:
        case = self.cases.get(case_id)
        return deepcopy(case) if case else None

    def list_cases(self) -> list[dict]:
        return [deepcopy(case) for case in self.cases.values()]

    def save_feedback(self, feedback_id: str, payload: dict) -> None:
        self.feedback[feedback_id] = deepcopy(payload)


store = MemoryStore()

