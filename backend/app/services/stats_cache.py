"""Statistics read-through cache implementation."""

from __future__ import annotations

import json
from typing import Any, Optional

from redis.asyncio import Redis


class StatsCache:
    """Read-through cache for dashboard statistics."""

    STATS_KEY = "stats:aggregate"
    TTL_SECONDS = 30

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get_stats(self) -> tuple[Optional[dict[str, Any]], bool]:
        """Attempt to fetch stats. Returns (data, is_hit)."""
        raw = await self.redis.get(self.STATS_KEY)
        if raw:
            return json.loads(raw), True
        return None, False

    async def set_stats(self, stats: dict[str, Any]) -> None:
        """Cache stats output."""
        await self.redis.set(self.STATS_KEY, json.dumps(stats), ex=self.TTL_SECONDS)

    async def invalidate(self) -> None:
        """Invalidate the stats cache completely (e.g. on new complaint submission)."""
        await self.redis.delete(self.STATS_KEY)
