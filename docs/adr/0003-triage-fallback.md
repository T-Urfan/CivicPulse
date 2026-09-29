# ADR 0003: Deterministic Triage Fallback

## Status
Accepted

## Context
AI providers (Groq, Ollama) can experience timeouts, rate limits, or return malformed JSON due to prompt injection or hallucination. The system must remain highly available.

## Decision
We implemented a `TriageOrchestrator` that wraps AI providers. If an LLM call fails (timeout, JSON parsing error, prompt injection), it automatically falls back to a deterministic `RuleBasedTriage` provider (`rules:fallback`).

## Consequences
- The system guarantees a response even if AI fails.
- Fallback results may be less accurate (often categorizing as "other" if keywords don't match), but they prevent the system from crashing.
