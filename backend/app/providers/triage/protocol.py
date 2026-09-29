"""Triage protocol and models."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, Field

from app.models import Category, Priority


class TriageResult(BaseModel):
    """Structured output expected from a triage provider."""

    category: Category = Field(description="The assigned category of the complaint.")
    priority: Priority = Field(description="The determined priority level.")
    summary: str = Field(
        max_length=140,
        description="A one-line summary of the complaint.",
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Provider's confidence score between 0.0 and 1.0.",
    )
    triaged_by: str = Field(
        default="",
        description="The identity of the provider that produced this result.",
    )


class TriageProvider(Protocol):
    """Protocol defining the interface for complaint triage."""

    @property
    def name(self) -> str:
        """The identifier of the provider."""
        ...

    async def triage(self, text: str, location: str) -> TriageResult:
        """Triage the complaint text and return a structured result."""
        ...
