"""HTTP routes for complaints management."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.models import (
    ALLOWED_TRANSITIONS,
    ComplaintCreate,
    ComplaintResponse,
    Status,
)
from app.providers.redis import get_redis_dependency
from app.providers.triage.factory import TriageOrchestrator, get_triage_provider
from app.repositories.complaint import SQLAlchemyComplaintRepository
from app.services.rate_limiter import DistributedRateLimiter, RateLimitExceededError
from app.services.stats import StatsService

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    request: Request,
    complaint_in: ComplaintCreate,
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_dependency),
) -> ComplaintResponse:
    """Submit, triage, and persist a new complaint."""
    # Rate Limiting
    client_ip = request.client.host if request.client else "127.0.0.1"
    rate_limiter = DistributedRateLimiter(redis)
    try:
        await rate_limiter.check_rate_limit(endpoint="POST /api/complaints", client_ip=client_ip)
    except RateLimitExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
            headers={"Retry-After": str(exc.retry_after)},
        ) from exc

    # Triage Phase
    provider = get_triage_provider()
    orchestrator = TriageOrchestrator(provider)

    # We generate a temporary ID to pass for logging
    temp_id = str(uuid.uuid4())
    triage_result = await orchestrator.triage(
        complaint_id=temp_id,
        text=complaint_in.text,
        location=complaint_in.location
    )

    # Persistence Phase
    repo = SQLAlchemyComplaintRepository(session)
    data = complaint_in.model_dump()
    data["category"] = triage_result.category.value
    data["priority"] = triage_result.priority.value
    data["ai_summary"] = triage_result.summary
    data["triaged_by"] = triage_result.triaged_by
    # Latency tracking omitted for simplicity but would normally be passed here

    complaint = await repo.create(data)

    # Invalidate Stats Cache
    stats_service = StatsService(session, redis)
    await stats_service.invalidate_stats()

    return complaint


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(
    complaint_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
) -> ComplaintResponse:
    """Fetch a single complaint."""
    repo = SQLAlchemyComplaintRepository(session)
    complaint = await repo.get_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


class PaginatedComplaints(BaseModel):
    items: list[ComplaintResponse]
    total: int
    page: int
    page_size: int


@router.get("", response_model=PaginatedComplaints)
async def list_complaints(
    category: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 50,
    session: AsyncSession = Depends(get_db_session),
) -> PaginatedComplaints:
    """List complaints with filters and pagination."""
    if page_size > 100:
        page_size = 100

    repo = SQLAlchemyComplaintRepository(session)
    items, total = await repo.list_complaints(
        category=category, priority=priority, status=status, page=page, page_size=page_size
    )

    return PaginatedComplaints(items=items, total=total, page=page, page_size=page_size)


class StatusUpdate(BaseModel):
    status: Status


@router.patch("/{complaint_id}/status", response_model=ComplaintResponse)
async def update_complaint_status(
    complaint_id: uuid.UUID,
    status_update: StatusUpdate,
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_dependency),
) -> ComplaintResponse:
    """Update a complaint's status enforcing the state machine."""
    repo = SQLAlchemyComplaintRepository(session)
    complaint = await repo.get_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    current_status = complaint.status
    target_status = status_update.status

    allowed = ALLOWED_TRANSITIONS.get(current_status, [])  # type: ignore
    if target_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Invalid transition from {current_status} to {target_status}",
        )

    # In a real app we'd update the DB. We didn't add a repository update method yet!
    # Let's update using SQLAlchemy directly.
    from sqlalchemy import update

    from app.repositories.models import DBComplaint

    stmt = (
        update(DBComplaint)
        .where(DBComplaint.id == complaint_id)
        .values(status=target_status.value)
    )
    await session.execute(stmt)
    await session.commit()

    # Refetch
    updated_complaint = await repo.get_by_id(complaint_id)

    # Invalidate stats
    stats_service = StatsService(session, redis)
    await stats_service.invalidate_stats()

    return updated_complaint  # type: ignore
