"""CivicPulse Backend - FastAPI Application Entry Point."""

from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncGenerator  # noqa: TC003 — used at runtime by asynccontextmanager
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pythonjsonlogger import jsonlogger

from app.config import get_settings
from app.database import engine
from app.providers.redis import close_redis
from app.routes import complaints, health, meta

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

def setup_logging() -> None:
    """Configure structured JSON logging."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    log_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

setup_logging()
logger = logging.getLogger("civicpulse")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle.

    On startup: initialize DB pool, Redis pool, provider factory.
    On shutdown: drain in-flight work, close pools gracefully.
    """
    settings = get_settings()
    logger.info(
        "civicpulse starting",
        extra={"triage_provider": settings.TRIAGE_PROVIDER},
    )
    yield
    # Graceful shutdown: close DB/Redis/client pools
    logger.info("civicpulse shutting down")
    await close_redis()
    await engine.dispose()


def create_app() -> FastAPI:
    """Application factory for CivicPulse backend."""
    settings = get_settings()

    app = FastAPI(
        title="CivicPulse API",
        description="Municipal Complaint Triage System",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware with configurable origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Cache", "X-Request-ID"],
    )

    @app.middleware("http")
    async def request_id_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Propagate or generate X-Request-ID for tracing."""
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Return 400 instead of default 422 for field validation errors."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.errors(), "body": exc.body},
        )

    # Register routers
    app.include_router(health.router)
    app.include_router(meta.router)
    app.include_router(complaints.router)

    return app


app = create_app()
