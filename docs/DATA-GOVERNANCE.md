# Data Governance and PII Handling

## Overview
CivicPulse handles municipal complaints, which frequently include Personally Identifiable Information (PII) such as phone numbers, exact addresses, and names.

## Risk Assessment
The primary risk vectors in the current architecture involve the **AI Triage Layer**. If an external third-party API (like Groq) is used as the active `TriageProvider`, unredacted citizen PII could be transmitted out of the operational network boundary, potentially violating privacy regulations.

## Mitigation and Sanitization Strategy (Proposed)
To mitigate these risks, the following data governance controls are proposed for the next iteration:

1. **Pre-Triage PII Sanitization (Regex / Local NLP)**:
   - Before `text` and `location` are sent to the `TriageProvider`, a dedicated sanitization service will strip phone numbers (using standard regex), names, and precise house numbers.
   - Example: "Water leak outside House 42, Block C, 0300-1234567" → "Water leak outside [REDACTED], Block C, [REDACTED]".
   - The sanitized payload is dispatched to the LLM, but the original payload is safely persisted to PostgreSQL.
   
2. **Local AI Exclusivity**:
   - For high-compliance environments, CivicPulse natively supports `OllamaTriage`, allowing a local model (e.g., Llama 3 8B) to run entirely within the cluster's network boundaries, guaranteeing zero external data egress.

3. **Data Retention**:
   - `reporter_contact` fields should be encrypted at rest.
   - Complaint data should be archived and scrubbed of PII after a 3-year statutory retention period.
