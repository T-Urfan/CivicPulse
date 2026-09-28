"""Simulated CI triage provider with failure injection."""

from __future__ import annotations

from app.config import get_settings
from app.models import Category, Priority
from app.providers.triage.protocol import TriageProvider, TriageResult


class SimulatedTriage(TriageProvider):
    """Deterministic provider for CI that can inject failures based on input."""

    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def name(self) -> str:
        return "ci-simulated"

    async def triage(self, text: str, location: str) -> TriageResult:
        """Return a simulated result or inject a failure."""
        text_lower = text.lower()

        # Inject failure if the magic keyword is present
        if "inject_failure" in text_lower:
            raise RuntimeError("Injected CI failure")

        if "inject_malformed" in text_lower:
            # We raise a ValueError to simulate a validation failure (400 level, non-retryable)
            # The test seam requires injecting malformed JSON, we simulate the parse failure here.
            raise ValueError("Malformed model response")

        # In CI, we use a semantic identity from the assignment (e.g. llm:groq)
        # to ensure the database enum is satisfied without adding llm:simulated to the DB enum.
        return TriageResult(
            category=Category.WATER if "water" in text_lower else Category.OTHER,
            priority=Priority.HIGH if "high" in text_lower else Priority.NORMAL,
            summary="Simulated summary",
            confidence=0.9,
            triaged_by="llm:groq"  # semantic identity
        )
