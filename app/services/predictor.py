from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np

from app.core.logging import get_logger
from app.services.model_loader import ModelRegistry

log = get_logger(__name__)


class Predictor:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self._model: Optional[Any] = None
        self._meta: Dict[str, Any] = {}
        self._version: Optional[str] = None

    @property
    def is_ready(self) -> bool:
        return self._model is not None and self._version is not None

    @property
    def model_version(self) -> str:
        return self._version or "unknown"

    def load(self, version: str) -> None:
        model, meta = self.registry.load(version=version)
        self._model = model
        self._meta = meta
        self._version = version
        log.info("model_loaded", model_version=version)

    def model_info(self) -> Dict[str, Any]:
        return {
            "model_version": self.model_version,
            "meta": self._meta,
        }

    def predict(self, features: List[float]) -> Dict[str, Any]:
        """
        Örnek davranış:
        - sklearn LogisticRegression gibi modellerde predict_proba -> score üretir.
        - Label: score >= threshold ise 1 (fraud) varsayalım.
        """
        if not self.is_ready:
            raise RuntimeError("Model not loaded")

        x = np.array(features, dtype=float).reshape(1, -1)

        # Threshold metadata’dan gelsin (üretim standardına yakın)
        threshold = float(self._meta.get("threshold", 0.5))

        score = None
        if hasattr(self._model, "predict_proba"):
            proba = self._model.predict_proba(x)[0, 1]
            score = float(proba)
        elif hasattr(self._model, "decision_function"):
            raw = float(self._model.decision_function(x)[0])
            # Basit sigmoid; gerçek sistemde calibration önerilir
            score = float(1.0 / (1.0 + np.exp(-raw)))
        else:
            pred = int(self._model.predict(x)[0])
            score = float(pred)

        label = int(score >= threshold)

        return {
            "model_version": self.model_version,
            "score": score,
            "label": label,
            "extra": {
                "threshold": threshold,
            },
        }
