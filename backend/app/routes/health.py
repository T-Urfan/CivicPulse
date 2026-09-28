"""Operational health and metrics routes."""

import time

from fastapi import APIRouter, Depends, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.database import get_db_session
from app.providers.redis import get_redis_dependency

router = APIRouter(tags=["operational"])

# Simple counter for metrics as requested
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests")


@router.get("/health")
async def health_probe() -> dict:
    """Liveness probe. Must not touch PostgreSQL or Redis."""
    REQUEST_COUNT.inc()
    return {"status": "alive"}


@router.get("/ready")
async def readiness_probe(
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_dependency),
) -> dict:
    """Readiness probe. Checks PostgreSQL and Redis reachability."""
    REQUEST_COUNT.inc()
    
    try:
        await session.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database check failed: {e}")

    try:
        await redis.ping()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis check failed: {e}")

    return {"status": "ready"}


@router.get("/metrics")
async def metrics_endpoint() -> Response:
    """Prometheus metrics exposition format."""
    REQUEST_COUNT.inc()
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
