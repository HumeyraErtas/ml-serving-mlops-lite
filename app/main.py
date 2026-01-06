from __future__ import annotations

import time
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes import router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.middleware.request_id import RequestIdMiddleware
from app.monitoring.metrics import (
    metrics_router,
    REQUEST_COUNT,
    REQUEST_LATENCY_SECONDS,
    INFLIGHT_REQUESTS,
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        INFLIGHT_REQUESTS.inc()
        try:
            response = await call_next(request)
            return response
        finally:
            INFLIGHT_REQUESTS.dec()
            elapsed = time.perf_counter() - start
            path = request.url.path
            method = request.method
            status_code = getattr(locals().get("response", None), "status_code", 500)

            REQUEST_COUNT.labels(method=method, path=path, status=str(status_code)).inc()
            REQUEST_LATENCY_SECONDS.labels(method=method, path=path).observe(elapsed)


def create_app() -> FastAPI:
    configure_logging()
    log = get_logger(__name__)
    log.info("boot", service=settings.SERVICE_NAME, env=settings.ENV)

    app = FastAPI(
        title=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION,
        docs_url="/docs" if settings.ENABLE_DOCS else None,
        redoc_url="/redoc" if settings.ENABLE_DOCS else None,
    )

    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(MetricsMiddleware)

    app.include_router(router)
    app.include_router(metrics_router)

    @app.get("/healthz", response_class=PlainTextResponse)
    def healthz():
        return "ok"

    return app


app = create_app()
