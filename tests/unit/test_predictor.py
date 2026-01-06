from __future__ import annotations

from app.services.model_loader import ModelRegistry
from app.services.predictor import Predictor


def test_predictor_not_ready_initially(tmp_path):
    registry = ModelRegistry(base_dir=str(tmp_path))
    p = Predictor(registry=registry)
    assert p.is_ready is False


def test_predictor_load_missing_raises(tmp_path):
    registry = ModelRegistry(base_dir=str(tmp_path))
    p = Predictor(registry=registry)

    try:
        p.load("1.0.0")
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        assert True
