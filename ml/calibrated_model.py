from __future__ import annotations

import numpy as np


class ProbabilityCalibratedModel:
    """Wrap a classifier with a probability calibrator.

    This avoids sklearn/XGBoost tag incompatibilities in newer Colab runtimes
    while still saving a model with a standard ``predict_proba`` interface.
    """

    def __init__(self, base_model, calibrator) -> None:
        self.base_model = base_model
        self.calibrator = calibrator

    def predict_proba(self, x_rows):
        raw_probabilities = self.base_model.predict_proba(x_rows)[:, 1]
        calibrated = self.calibrator.predict(raw_probabilities)
        calibrated = np.clip(calibrated, 0.0, 1.0)
        return np.column_stack([1.0 - calibrated, calibrated])

