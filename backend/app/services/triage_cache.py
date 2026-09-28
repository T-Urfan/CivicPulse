"""Triage result cache implementation."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Optional

from redis.asyncio import Redis

from app.providers.triage.protocol import TriageResult

logger = logging.getLogger(__name__)


class TriageCache:
    """Content-hash based cache for triage results to avoid duplicate LLM inferences."""

    def __init__(self, redis: Redis) -> None:
        self.redis = redis
        self.ttl_seconds = 24 * 60 * 60  # 24 hours

    def _generate_key(self, text: str, location: str) -> str:
        """Generate a SHA-256 content hash of the input including location."""
        # Using canonical representation to prevent cross-location contamination
        canonical = f"loc:{location.strip().lower()}|txt:{text.strip().lower()}"
        content_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return f"triage_cache:{content_hash}"

    async def get(self, text: str, location: str) -> Optional[TriageResult]:
        """Fetch a cached triage result if it exists."""
        key = self._generate_key(text, location)
        raw = await self.redis.get(key)
        
        # Track hit rate in a separate Redis counter (hit/miss)
        if raw:
            await self.redis.incr("metrics:triage_cache:hits")
            try:
                data = json.loads(raw)
                return TriageResult(**data)
            except Exception as e:
                logger.warning(f"Failed to parse cached triage result: {e}")
                return None
        else:
            await self.redis.incr("metrics:triage_cache:misses")
            return None

    async def set(self, text: str, location: str, result: TriageResult) -> None:
        """Cache a successful triage result."""
        key = self._generate_key(text, location)
        # Store as JSON string
        await self.redis.set(key, result.model_dump_json(), ex=self.ttl_seconds)
