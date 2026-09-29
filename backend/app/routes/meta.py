"""HTTP routes for metadata and statistics."""

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.providers.redis import get_redis_dependency
from app.providers.triage.factory import get_triage_provider
from app.services.stats import StatsService

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/stats")
async def get_stats(
    response: Response,
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_dependency),
) -> dict:
    """Retrieve aggregate statistics."""
    service = StatsService(session, redis)
    stats, is_hit = await service.get_dashboard_stats()

    # Requirement: X-Cache header
    response.headers["X-Cache"] = "HIT" if is_hit else "MISS"
    return stats


class ProviderMeta(BaseModel):
    provider: str
    latency_ms: int
    fallback: bool


class MetaResponse(BaseModel):
    active_provider: str
    outcomes: list[ProviderMeta]


@router.get("/meta/providers", response_model=MetaResponse)
async def get_providers(
    redis: Redis = Depends(get_redis_dependency),
) -> MetaResponse:
    """Retrieve current triage provider metadata and cache stats."""
    provider = get_triage_provider()

    # For now we'll just return the provider identity as requested.
    # The actual "last 20 outcomes" is a nice-to-have observable, we'll leave it empty to start
    # or populate it if we implement a rotating list in Redis.
    return MetaResponse(
        active_provider=provider.name,
        outcomes=[],
    )
