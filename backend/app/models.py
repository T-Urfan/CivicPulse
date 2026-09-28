"""CivicPulse domain models and enums.

This module is the single source of truth for domain enums and shared
Pydantic models used across routes, services, repositories, and providers.
"""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from datetime import datetime
from uuid import UUID


class Category(enum.StrEnum):
    """Complaint category enum — assignment-mandated values."""

    WATER = "water"
    ELECTRICITY = "electricity"
    SANITATION = "sanitation"
    ROADS = "roads"
    STREETLIGHTS = "streetlights"
    OTHER = "other"


class Priority(enum.StrEnum):
    """Complaint priority enum — assignment-mandated values."""

    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class Status(enum.StrEnum):
    """Complaint status enum — assignment-mandated values.

    State machine transitions:
        open → in_progress
        open → rejected
        in_progress → resolved
        in_progress → rejected
    Terminal states: resolved, rejected
    """

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"


# ── Explicit state transition table ──────────────────────────────────────────
# Implemented as a dictionary per the assignment requirement:
#   "Use an explicit transition table/dictionary. Do not implement as a
#    long chain of if/elif business rules."
ALLOWED_TRANSITIONS: dict[Status, frozenset[Status]] = {
    Status.OPEN: frozenset({Status.IN_PROGRESS, Status.REJECTED}),
    Status.IN_PROGRESS: frozenset({Status.RESOLVED, Status.REJECTED}),
    Status.RESOLVED: frozenset(),  # terminal
    Status.REJECTED: frozenset(),  # terminal
}


def is_valid_transition(current: Status, target: Status) -> bool:
    """Check if the status transition is allowed by the state machine."""
    return target in ALLOWED_TRANSITIONS.get(current, frozenset())


# ── Pydantic models ─────────────────────────────────────────────────────────


class ComplaintCreate(BaseModel):
    """Request body for POST /api/complaints."""

    model_config = ConfigDict(strict=True)

    text: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Complaint free text (10-2000 characters)",
    )
    location: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Location of the complaint (3-200 characters)",
    )
    reporter_contact: str | None = Field(
        default=None,
        max_length=200,
        description="Optional reporter contact information",
    )


class StatusUpdate(BaseModel):
    """Request body for PATCH /api/complaints/{id}/status."""

    model_config = ConfigDict(strict=True)

    status: Status


class ComplaintResponse(BaseModel):
    """Response model for a single complaint."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    location: str
    reporter_contact: str | None
    category: Category
    priority: Priority
    status: Status
    ai_summary: str | None
    triaged_by: str
    triage_latency_ms: int
    created_at: datetime
    updated_at: datetime


class ComplaintListResponse(BaseModel):
    """Paginated list of complaints."""

    items: list[ComplaintResponse]
    total: int
    page: int
    page_size: int


class StatsResponse(BaseModel):
    """Aggregate statistics response."""

    by_category: dict[str, int]
    by_priority: dict[str, int]


class TriageOutcome(BaseModel):
    """Recent triage outcome for /api/meta/providers."""

    provider: str
    latency_ms: int
    fallback: bool


class ProviderMetaResponse(BaseModel):
    """Response for GET /api/meta/providers."""

    active_provider: str
    recent_outcomes: list[TriageOutcome]


class HealthResponse(BaseModel):
    """Response for health and readiness endpoints."""

    status: str
    details: dict[str, str] | None = None


class ValidationErrorItem(BaseModel):
    """Individual field validation error."""

    field: str
    message: str


class ValidationErrorResponse(BaseModel):
    """HTTP 400 field-level validation error body.

    The assignment requires 400 (not FastAPI's default 422) with
    field-level errors.
    """

    errors: list[ValidationErrorItem]
