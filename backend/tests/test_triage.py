"""Tests for triage AI layer and deterministic fallbacks."""

import pytest
from httpx import TimeoutException

from app.models import Category
from app.providers.triage.factory import TriageOrchestrator
from app.providers.triage.simulated import SimulatedTriage


@pytest.mark.asyncio
async def test_simulated_triage_fallback_on_injection():
    """Test that prompt injection or explicit failure triggers rule fallback."""
    provider = SimulatedTriage()
    orchestrator = TriageOrchestrator(provider)

    # Simulated provider is configured to raise an error if "inject_failure" is in text
    result = await orchestrator.triage(
        complaint_id="test-123",
        text="This is a test with inject_failure to force a fallback.",
        location="Test Location"
    )

    # Because it fell back to rules, triaged_by should be rules:fallback
    assert result.triaged_by == "rules:fallback"
    # And since the text didn't contain "water" or other rule keywords, it defaults to other
    assert result.category == Category.OTHER


@pytest.mark.asyncio
async def test_simulated_triage_malformed_output():
    """Test that malformed output (ValueError) is caught and triggers fallback."""
    provider = SimulatedTriage()
    orchestrator = TriageOrchestrator(provider)

    # Simulated provider raises ValueError on "inject_malformed"
    result = await orchestrator.triage(
        complaint_id="test-456",
        text="A normal complaint with inject_malformed",
        location="Test Location"
    )

    assert result.triaged_by == "rules:fallback"
