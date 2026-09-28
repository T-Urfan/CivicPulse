"""CivicPulse Backend - FastAPI Application Entry Point."""

from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncGenerator  # noqa: TCH003 — used at runtime by asynccontextmanager
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

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
    # Resource initialization will be added in later phases (P02-P05)
    yield
    # Graceful shutdown: close DB/Redis/client pools
    logger.info("civicpulse shutting down")


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

    # Health endpoint — liveness only, no DB/Redis dependency
    @app.get("/health", tags=["operational"])
    async def health() -> dict[str, str]:
        """Liveness probe. Must not touch PostgreSQL or Redis."""
        return {"status": "alive"}

    # Routes will be registered in later phases (P05)

    return app


app = create_app()
