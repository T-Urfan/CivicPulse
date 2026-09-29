# ADR 0002: Data Governance and PII Redaction

## Status
Accepted

## Context
Citizens submit free-text complaints that may contain Personal Identifiable Information (PII) such as phone numbers or explicit addresses. Sending unredacted text to external LLMs (Groq, Ollama) poses a significant privacy risk.

## Decision
We enforce a strict data governance boundary. 
- LLM prompts instruct the model to anonymize its summary output.
- Log masking ensures PII does not leak into operational stdout logs.
- The database stores contact info in a dedicated field, which is not sent to the triage LLM.

## Consequences
- Improved compliance with privacy requirements.
- Slightly higher processing overhead for prompt instructions.
