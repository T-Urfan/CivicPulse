"""Local LLM triage provider using Ollama."""

from __future__ import annotations

import json
import logging

import httpx

from app.config import get_settings
from app.providers.triage.protocol import TriageProvider, TriageResult

logger = logging.getLogger(__name__)


class OllamaTriage(TriageProvider):
    """Local LLM provider using Ollama."""

    def __init__(self) -> None:
        self.settings = get_settings()
        # Default to a ~1B param instruct model for local speed, e.g. qwen:0.5b or llama3.2:1b
        self.model = "llama3.2:1b"
        self.api_url = "http://ollama:11434/api/generate"

    @property
    def name(self) -> str:
        return "llm:ollama"

    async def triage(self, text: str, location: str) -> TriageResult:
        """Call local Ollama to triage the complaint."""
        system_prompt = (
            "You are an expert municipal complaint triage assistant.\n"
            "Analyze the complaint and return a JSON object exactly matching this schema:\n"
            "{\n"
            '  "category": "water" | "electricity" | "sanitation" | '
            '"roads" | "streetlights" | "other",\n'
            '  "priority": "high" | "normal" | "low",\n'
            '  "summary": "One line summary (max 140 chars)",\n'
            '  "confidence": 0.0 to 1.0\n'
            "}\n"
            "Output ONLY valid JSON. No prose."
        )

        prompt = f"{system_prompt}\n\nLocation: {location}\nComplaint: {text}"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }

        # 10 second timeout as required by the assignment
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(self.api_url, json=payload)
                response.raise_for_status()
                data = response.json()
                raw_content = data["response"]

                parsed = json.loads(raw_content)

                return TriageResult(
                    category=parsed.get("category"),
                    priority=parsed.get("priority"),
                    summary=parsed.get("summary"),
                    confidence=parsed.get("confidence", 1.0),
                    triaged_by=self.name,
                )
            except httpx.RequestError as e:
                # Map connection errors to something catchable for fallback
                raise RuntimeError(f"Ollama connection error: {e}") from e
