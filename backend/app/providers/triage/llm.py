"""Hosted LLM triage provider using Groq API."""

from __future__ import annotations

import json
import logging

import httpx

from app.config import get_settings
from app.providers.triage.protocol import TriageProvider, TriageResult

logger = logging.getLogger(__name__)


class LLMTriage(TriageProvider):
    """Hosted LLM provider using Groq."""

    def __init__(self) -> None:
        self.settings = get_settings()
        # Default to llama3-8b-8192 or whatever is the free tier Groq model
        self.model = "llama3-8b-8192"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    @property
    def name(self) -> str:
        return "llm:groq"

    async def triage(self, text: str, location: str) -> TriageResult:
        """Call Groq API to triage the complaint."""
        if not self.settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required for LLMTriage")

        system_prompt = (
            "You are an expert municipal complaint triage assistant.\n"
            "Analyze the complaint and return a JSON object exactly matching this schema:\n"
            "{\n"
            '  "category": "water" | "electricity" | "sanitation" | "roads" | "streetlights" | "other",\n'
            '  "priority": "high" | "normal" | "low",\n'
            '  "summary": "One line summary (max 140 chars)",\n'
            '  "confidence": 0.0 to 1.0\n'
            "}\n"
            "Do not include any prose, markdown formatting, or code fences."
        )

        user_prompt = f"Location: {location}\nComplaint: {text}"

        headers = {
            "Authorization": f"Bearer {self.settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        }

        # 10 second timeout as required by the assignment
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            raw_content = data["choices"][0]["message"]["content"]
            
            # Pydantic validation handles malformed JSON and schema mismatches
            parsed = json.loads(raw_content)
            
            return TriageResult(
                category=parsed.get("category"),
                priority=parsed.get("priority"),
                summary=parsed.get("summary"),
                confidence=parsed.get("confidence", 1.0),
                triaged_by=self.name,
            )
