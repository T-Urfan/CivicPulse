"""Deterministic keyword-based fallback triage provider."""

from __future__ import annotations

import logging

from app.models import Category, Priority
from app.providers.triage.protocol import TriageProvider, TriageResult

logger = logging.getLogger(__name__)


class RuleBasedTriage(TriageProvider):
    """Deterministic fallback provider that never intentionally fails."""

    @property
    def name(self) -> str:
        return "rules:fallback"

    async def triage(self, text: str, location: str) -> TriageResult:
        """Apply simple keyword matching to triage the complaint."""
        text_lower = text.lower()

        # Simple category rules
        if any(word in text_lower for word in ["water", "pipe", "leak", "sewerage", "gutter"]):
            category = Category.water
        elif any(word in text_lower for word in ["electricity", "power", "light", "wire", "transformer", "voltage"]):
            category = Category.electricity
        elif any(word in text_lower for word in ["garbage", "trash", "kachra", "smell", "clean", "sweep"]):
            category = Category.sanitation
        elif any(word in text_lower for word in ["road", "street", "pothole", "broken", "asphalt"]):
            category = Category.roads
        else:
            category = Category.other

        # Simple priority rules
        if any(word in text_lower for word in ["blast", "spark", "burn", "die", "dead", "bite", "severe", "high"]):
            priority = Priority.high
        elif any(word in text_lower for word in ["slow", "speed breaker", "money", "fee"]):
            priority = Priority.low
        else:
            priority = Priority.normal

        # Construct a simple summary
        summary = text[:137] + "..." if len(text) > 137 else text

        return TriageResult(
            category=category,
            priority=priority,
            summary=summary,
            confidence=1.0,
            triaged_by=self.name,
        )
