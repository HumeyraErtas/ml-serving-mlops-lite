from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import joblib


class ModelRegistry:
    """
    Basit 'model registry' yaklaşımı:
    models/<version>/
      - model.joblib
      - meta.json
    """

    def __init__(self, base_dir: str = "models"):
        self.base_dir = Path(base_dir)

    def _version_dir(self, version: str) -> Path:
        return self.base_dir / version

    def load(self, version: str) -> Tuple[Any, Dict[str, Any]]:
        vdir = self._version_dir(version)
        model_path = vdir / "model.joblib"
        meta_path = vdir / "meta.json"

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        if not meta_path.exists():
            raise FileNotFoundError(f"Model metadata not found: {meta_path}")

        model = joblib.load(model_path)
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        return model, meta
