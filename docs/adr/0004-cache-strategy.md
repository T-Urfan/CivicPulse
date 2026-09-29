# ADR 0004: Redis Read-Through Caching

## Status
Accepted

## Context
Aggregate statistics (`/api/stats`) require full table scans and GROUP BY operations which are expensive. High read traffic could easily overwhelm the database.

## Decision
We implemented a Redis read-through cache for stats with a 30-second TTL. The application sets an `X-Cache: HIT` or `X-Cache: MISS` header. The cache is actively invalidated on any write operation (new complaint, status update).

## Consequences
- Significant reduction in database load for read-heavy workloads.
- Cache invalidation guarantees strong consistency for users.
