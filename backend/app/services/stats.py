"""Statistics service for dashboard aggregates and cache metrics."""

from __future__ import annotations

from typing import Any

from redis.asyncio import Redis
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.models import DBComplaint
from app.services.stats_cache import StatsCache


class StatsService:
    """Service to aggregate complaint stats and report metrics."""

    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self.session = session
        self.redis = redis
        self.stats_cache = StatsCache(redis)

    async def _compute_db_stats(self) -> dict[str, Any]:
        """Compute live aggregates from the database."""
        # Aggregate by category
        cat_stmt = select(DBComplaint.category, func.count(DBComplaint.id)).group_by(DBComplaint.category)
        cat_result = await self.session.execute(cat_stmt)
        by_category = {row[0]: row[1] for row in cat_result.all()}

        # Aggregate by priority
        pri_stmt = select(DBComplaint.priority, func.count(DBComplaint.id)).group_by(DBComplaint.priority)
        pri_result = await self.session.execute(pri_stmt)
        by_priority = {row[0]: row[1] for row in pri_result.all()}

        return {
            "by_category": by_category,
            "by_priority": by_priority,
        }

    async def get_dashboard_stats(self) -> tuple[dict[str, Any], bool]:
        """
        Fetch dashboard stats, utilizing the read-through cache.
        Returns a tuple of (stats_dict, is_cache_hit).
        """
        cached_stats, is_hit = await self.stats_cache.get_stats()
        if is_hit and cached_stats is not None:
            return cached_stats, True

        # Cache miss, compute from DB
        live_stats = await self._compute_db_stats()

        # Populate cache
        await self.stats_cache.set_stats(live_stats)

        return live_stats, False

    async def invalidate_stats(self) -> None:
        """Invalidate the stats cache when new data is persisted."""
        await self.stats_cache.invalidate()

    async def get_triage_cache_metrics(self) -> dict[str, int]:
        """Fetch the triage cache hit/miss counters."""
        hits = await self.redis.get("metrics:triage_cache:hits") or b"0"
        misses = await self.redis.get("metrics:triage_cache:misses") or b"0"
        return {
            "hits": int(hits),
            "misses": int(misses),
        }
