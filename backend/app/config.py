"""CivicPulse backend configuration using Pydantic Settings.

All configuration is sourced from environment variables.
No secrets are hardcoded. The .env file is gitignored.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Environment variable names match the field names (case-insensitive).
    A .env file at the backend working directory is loaded automatically
    by Pydantic Settings if present.
    """

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://civicpulse:civicpulse@postgres:5432/civicpulse"

    # ── Redis ────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://redis:6379/0"

    # ── Triage provider ──────────────────────────────────────────────────────
    TRIAGE_PROVIDER: str = "rules"

    # ── Hosted LLM (Groq) ───────────────────────────────────────────────────
    GROQ_API_KEY: str = ""

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000"

    # ── Rate limiting ────────────────────────────────────────────────────────
    RATE_LIMIT_REQUESTS: int = 20
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ── Ollama ───────────────────────────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://ollama:11434"

    # ── Stats cache ──────────────────────────────────────────────────────────
    STATS_CACHE_TTL_SECONDS: int = 30

    # ── Triage cache ─────────────────────────────────────────────────────────
    TRIAGE_CACHE_TTL_SECONDS: int = 86400  # 24 hours

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [o.strip() for o in self.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached singleton settings instance."""
    return Settings()
