"""Repository interface and implementation for Complaints."""

from __future__ import annotations

import uuid
from typing import Protocol

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category, ComplaintResponse, Priority, Status
from app.repositories.models import DBComplaint


class ComplaintRepository(Protocol):
    """Protocol defining the data access contract for complaints."""

    async def create(self, complaint_data: dict[str, object]) -> ComplaintResponse:
        """Create and return a new complaint."""
        ...

    async def get_by_id(self, complaint_id: uuid.UUID) -> ComplaintResponse | None:
        """Fetch a single complaint by ID."""
        ...

    async def list_complaints(
        self,
        category: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[ComplaintResponse], int]:
        """Fetch a paginated list of complaints with optional filters and total count."""
        ...


class SQLAlchemyComplaintRepository:
    """PostgreSQL implementation of the ComplaintRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_domain(self, db_obj: DBComplaint) -> ComplaintResponse:
        """Map the ORM object to the domain response model."""
        return ComplaintResponse(
            id=db_obj.id,
            text=db_obj.text,
            location=db_obj.location,
            reporter_contact=db_obj.reporter_contact,
            category=Category(db_obj.category),
            priority=Priority(db_obj.priority),
            status=Status(db_obj.status),
            ai_summary=db_obj.ai_summary,
            triaged_by=db_obj.triaged_by,
            triage_latency_ms=db_obj.triage_latency_ms,
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at,
        )

    async def create(self, complaint_data: dict[str, object]) -> ComplaintResponse:
        """Create a new complaint and return the domain model."""
        db_complaint = DBComplaint(**complaint_data)
        self.session.add(db_complaint)
        await self.session.commit()
        await self.session.refresh(db_complaint)
        return self._to_domain(db_complaint)

    async def get_by_id(self, complaint_id: uuid.UUID) -> ComplaintResponse | None:
        """Fetch a complaint by ID."""
        stmt = select(DBComplaint).where(DBComplaint.id == complaint_id)
        result = await self.session.execute(stmt)
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            return None
        return self._to_domain(db_obj)

    async def list_complaints(
        self,
        category: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[ComplaintResponse], int]:
        """Fetch paginated complaints with filters."""
        stmt = select(DBComplaint)
        count_stmt = select(func.count()).select_from(DBComplaint)

        # Apply filters
        if category:
            stmt = stmt.where(DBComplaint.category == category)
            count_stmt = count_stmt.where(DBComplaint.category == category)
        if priority:
            stmt = stmt.where(DBComplaint.priority == priority)
            count_stmt = count_stmt.where(DBComplaint.priority == priority)
        if status:
            stmt = stmt.where(DBComplaint.status == status)
            count_stmt = count_stmt.where(DBComplaint.status == status)

        # Pagination
        limit = min(page_size, 100)  # Max page size enforced here or in routes
        offset = (max(page, 1) - 1) * limit

        # Order chronologically descending
        stmt = stmt.order_by(DBComplaint.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        # Execute queries concurrently if desired, but sequential is fine
        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        items_result = await self.session.execute(stmt)
        items = items_result.scalars().all()

        return [self._to_domain(item) for item in items], total_count
