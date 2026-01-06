from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.services.model_loader import ModelRegistry
from app.services.predictor import Predictor

router = APIRouter()
log = get_logger(__name__)

registry = ModelRegistry(base_dir=settings.MODEL_DIR)
predictor = Predictor(registry=registry)


class PredictRequest(BaseModel):
    # Basit örnek: sayısal feature vektörü
    features: List[float] = Field(..., min_length=1)


class PredictResponse(BaseModel):
    model_version: str
    score: float
    label: int
    extra: Dict[str, Any] = {}


@router.on_event("startup")
def _startup():
    # Uygulama kalkarken modeli yükle
    predictor.load(version=settings.MODEL_VERSION)
    log.info("startup_loaded_model", model_version=predictor.model_version)


@router.get("/readyz")
def readyz():
    if not predictor.is_ready:
        raise HTTPException(status_code=503, detail="model_not_ready")
    return {"status": "ready", "model_version": predictor.model_version}


@router.get("/model-info")
def model_info():
    if not predictor.is_ready:
        raise HTTPException(status_code=503, detail="model_not_ready")
    return predictor.model_info()


@router.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest, request: Request):
    if not predictor.is_ready:
        raise HTTPException(status_code=503, detail="model_not_ready")

    # RequestId middleware header olarak ekliyor; log’ta da kullanabilirsiniz
    request_id: Optional[str] = getattr(request.state, "request_id", None)

    result = predictor.predict(req.features)

    log.info(
        "predict",
        request_id=request_id,
        model_version=result["model_version"],
        label=result["label"],
        score=result["score"],
    )
    return result


@router.post("/reload")
def reload_model():
    """
    Opsiyonel: küçük servislerde deploy sonrası hızlı reload.
    Prod’da genelde canary/blue-green ile çözülür; burada 'lite' örnek.
    """
    predictor.load(version=settings.MODEL_VERSION)
    return {"status": "reloaded", "model_version": predictor.model_version}
