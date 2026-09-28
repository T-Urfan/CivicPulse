"""Distributed IP-based rate limiter using Redis."""

from __future__ import annotations

import time

from redis.asyncio import Redis

# Lua script for a fixed-window rate limiter.
# Keys: [rate_limit_key]
# Args: [limit, window_seconds]
# Returns: 1 if allowed, 0 if rate limited
FIXED_WINDOW_LUA = """
local current = redis.call("INCR", KEYS[1])
if current == 1 then
    redis.call("EXPIRE", KEYS[1], ARGV[2])
end
if current > tonumber(ARGV[1]) then
    return 0
end
return 1
"""


class RateLimitExceeded(Exception):
    """Exception raised when the client exceeds the rate limit."""
    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds.")


class DistributedRateLimiter:
    """Redis-backed distributed rate limiter using fixed window algorithm."""

    def __init__(
        self,
        redis: Redis,
        limit: int = 10,
        window_seconds: int = 60,
    ) -> None:
        self.redis = redis
        self.limit = limit
        self.window_seconds = window_seconds

    def _generate_key(self, endpoint: str, client_ip: str) -> str:
        """Generate a fixed-window key for the specific IP and endpoint."""
        current_window = int(time.time() / self.window_seconds)
        return f"ratelimit:{endpoint}:{client_ip}:{current_window}"

    async def check_rate_limit(self, endpoint: str, client_ip: str) -> None:
        """
        Check if the client IP is allowed to make a request to the endpoint.
        Raises RateLimitExceeded if the limit is breached.
        """
        key = self._generate_key(endpoint, client_ip)

        # We load the script directly or use eval. eval is simpler for a short script.
        allowed = await self.redis.eval(
            FIXED_WINDOW_LUA,
            1,           # Number of keys
            key,         # KEYS[1]
            self.limit,  # ARGV[1]
            self.window_seconds  # ARGV[2]
        )

        if not allowed:
            # Calculate time remaining in the current window for Retry-After
            current_time = int(time.time())
            window_end = ((current_time // self.window_seconds) + 1) * self.window_seconds
            retry_after = max(1, window_end - current_time)
            raise RateLimitExceeded(retry_after=retry_after)
