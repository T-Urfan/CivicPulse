"""Redis connection management."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.config import get_settings

logger = logging.getLogger(__name__)

# Global Redis instance, initialized lazily or explicitly
_redis_client: Redis | None = None


async def get_redis() -> Redis:
    """Get or initialize the global Redis client."""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        logger.info(f"Connecting to Redis at {settings.REDIS_URL}")
        _redis_client = Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def close_redis() -> None:
    """Close the global Redis client connection."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()  # type: ignore
        _redis_client = None


async def get_redis_dependency() -> AsyncGenerator[Redis, None]:
    """FastAPI dependency to yield the Redis client."""
    client = await get_redis()
    yield client
