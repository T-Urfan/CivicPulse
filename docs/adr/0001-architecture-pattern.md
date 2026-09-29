# ADR 0001: 4-Layer Architecture Pattern

## Status
Accepted

## Context
The system needs to isolate concerns between the HTTP transport layer and core business logic. Combining routing and SQL operations makes testing difficult and leads to duplicated code.

## Decision
We implemented a strict 4-layer architecture:
1. **Routes**: HTTP-only logic, input validation, and status codes.
2. **Services**: Business rules, state machine orchestration, and rate limit orchestration.
3. **Repositories**: SQL/persistence access.
4. **Providers**: Outbound integrations (LLM, Cache).

## Consequences
- Testing is simplified through mockable interfaces.
- The HTTP layer cannot inadvertently perform complex database transactions.
- Future transitions (e.g., GraphQL instead of REST) will only require changing the routes layer.
