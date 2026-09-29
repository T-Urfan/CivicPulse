"""Triage factory and orchestration.

Implements retries, fallback logic, and provider selection based on environment.
"""

from __future__ import annotations

import logging

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from app.config import get_settings
from app.providers.triage.llm import LLMTriage
from app.providers.triage.ollama import OllamaTriage
from app.providers.triage.protocol import TriageProvider, TriageResult
from app.providers.triage.rule_based import RuleBasedTriage
from app.providers.triage.simulated import SimulatedTriage

logger = logging.getLogger(__name__)


def get_triage_provider() -> TriageProvider:
    """Factory to return the configured triage provider."""
    settings = get_settings()
    provider_name = settings.TRIAGE_PROVIDER.lower()

    if provider_name == "groq":
        return LLMTriage()
    elif provider_name == "ollama":
        return OllamaTriage()
    elif provider_name == "rules":
        return RuleBasedTriage()
    elif provider_name == "simulated":
        return SimulatedTriage()
    else:
        logger.warning(f"Unknown TRIAGE_PROVIDER '{provider_name}', falling back to rules")
        return RuleBasedTriage()


class TriageOrchestrator:
    """Orchestrates triage calls, handling retries and deterministic fallback."""

    def __init__(self, provider: TriageProvider) -> None:
        self.provider = provider
        self.fallback_provider = RuleBasedTriage()

    def _should_retry(self, exc: BaseException) -> bool:
        """Determine if an exception is retryable (timeout, 429, 5xx)."""
        if isinstance(exc, httpx.TimeoutException):
            return True
        if isinstance(exc, httpx.HTTPStatusError):
            status = exc.response.status_code
            if status == 429 or status >= 500:
                return True
        return False

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(2),  # Exactly one retry (initial + 1 retry)
        wait=wait_random_exponential(multiplier=1, max=10),
        reraise=True,
    )
    async def _call_provider_with_retry(self, text: str, location: str) -> TriageResult:
        """Call the provider with exactly one jittered retry on transient errors."""
        try:
            return await self.provider.triage(text, location)
        except Exception as e:
            if self._should_retry(e):
                logger.info(f"Retryable error from triage provider: {e}")
                raise
            # Non-retryable errors (e.g. 400, ValidationError from malformed output)
            # are re-raised immediately to bypass tenacity and trigger the outer fallback.
            raise e

    async def triage(self, complaint_id: str, text: str, location: str) -> TriageResult:
        """
        Attempt triage with the primary provider.
        If it fails (after retry), log exactly one WARNING and use the rule-based fallback.
        """
        try:
            return await self._call_provider_with_retry(text, location)
        except Exception as e:
            # Fallback triggered
            error_class = e.__class__.__name__

            # Exactly one WARNING per fallback with complaint id, provider, and error class
            logger.warning(
                f"Triage fallback triggered for complaint_id={complaint_id}: "
                f"provider={self.provider.name} failed with {error_class} ({e})"
            )

            # Fallback never intentionally fails
            return await self.fallback_provider.triage(text, location)
