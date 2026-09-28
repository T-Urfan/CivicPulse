# CivicPulse - Implementation Status Ledger

> Internal engineering ledger. Updated after each implementation phase.
> This file tracks actual progress against the master XML specification.

## Current Phase: P00 — Forensics and Assignment Mapping

### Repository Baseline

| Property           | Value                                        |
|--------------------|----------------------------------------------|
| Repository         | T-Urfan/CivicPulse                           |
| Remote URL         | https://github.com/T-Urfan/CivicPulse.git   |
| Initial branch     | main                                         |
| Working branches   | dev, feature/project-bootstrap               |
| Git identity       | T-Urfan (configured)                         |
| GitHub CLI auth    | ✓ Authenticated (HTTPS, keyring)             |
| Initial commit     | 22e2e69 (Add files via upload)               |

### Phase P00 Deliverables

- [x] Repository inspected and baseline documented
- [x] Master XML read completely (964 lines)
- [x] Verification report read completely (388 lines)
- [x] Branch strategy established (main → dev → feature/*)
- [x] `.gitignore` created (covers Python, Node, .env, IDE, Docker, K8s)
- [x] `.env.example` created with safe placeholders
- [x] Repository skeleton directories created
- [x] `docs/IMPLEMENTATION-STATUS.md` created (this file)
- [ ] First legitimate commit made on feature branch

### Phase P00 Gate Checklist

- [x] Git clean/understood
- [x] Checklist covers all contract/rubric/deduction/evidence requirements
- [x] No secrets in repository
- [x] .env is gitignored
- [x] Branch strategy follows assignment requirements

---

## Requirement Checklist (Assignment-Derived)

### A — Collaboration and Version Control (15 marks)

| ID  | Requirement                                                       | Status       |
|-----|-------------------------------------------------------------------|--------------|
| A1  | main protected, no direct push, PR required, CI required, ≥1 approval | NOT STARTED  |
| A2  | dev + feature branches; no direct work on main                    | IN PROGRESS  |
| A3  | ≥5 merged PRs, each linked to Issue, substantive partner review   | NOT STARTED  |
| A4  | ≥35 commits, conventional prefixes, neither partner below 35%     | NOT STARTED  |
| A5  | One deliberate real-code merge conflict with evidence              | NOT STARTED  |

### B — Frontend (18 marks)

| ID  | Requirement                                                       | Status       |
|-----|-------------------------------------------------------------------|--------------|
| B1  | Submit view: validation/loading/category/priority/summary/provider | NOT STARTED  |
| B2  | Dashboard: pagination/filters/status transitions/server 409       | NOT STARTED  |
| B3  | Stats aggregates + X-Cache state                                  | NOT STARTED  |
| B4  | Runtime config: no baked API URL; one image works across envs     | NOT STARTED  |
| B5  | ≥5 meaningful frontend tests                                      | NOT STARTED  |

### C — Backend (25 marks)

| ID  | Requirement                                                       | Status       |
|-----|-------------------------------------------------------------------|--------------|
| C1  | All contract endpoints, correct status codes, field-level errors  | NOT STARTED  |
| C2  | Four-layer separation, no SQL outside repos, no business in routes | NOT STARTED  |
| C3  | Explicit state transition table, invalid transitions 409          | NOT STARTED  |
| C4  | health/readiness distinction; health does not touch DB            | NOT STARTED  |
| C5  | JSON stdout logging with propagated request_id                    | NOT STARTED  |
| C6  | SIGTERM drains in-flight work before exit                         | NOT STARTED  |
| C7  | ≥14 deterministic backend tests, coverage ≥65%                    | NOT STARTED  |

### D — Data Layer (12 marks)

| ID  | Requirement                                                       | Status       |
|-----|-------------------------------------------------------------------|--------------|
| D1  | Alembic migrations; no startup DDL                                | NOT STARTED  |
| D2  | Complete schema including triaged_by, ai_summary, etc.            | NOT STARTED  |
| D3  | Two indexes with named-query justification                        | NOT STARTED  |
| D4  | Idempotent ≥30 realistic complaints; second run changes nothing   | NOT STARTED  |

### E — Cache Layer (10 marks)

| ID  | Requirement                                                       | Status       |
|-----|-------------------------------------------------------------------|--------------|
| E1  | Stats read-through cache, 30s TTL, X-Cache                       | NOT STARTED  |
| E2  | Cache invalidated on write                                        | NOT STARTED  |
| E3  | Distributed Redis rate limiter, 429 + Retry-After                 | NOT STARTED  |
| E4  | Redis AOF on named volume with justification                      | NOT STARTED  |

### F — AI Layer (25 marks)

| ID  | Requirement                                                       | Status       |
|-----|-------------------------------------------------------------------|--------------|
| F1  | TriageProvider interface + ≥3 working implementations by env      | NOT STARTED  |
| F2  | Structured output + Pydantic validation; malformed output rejected | NOT STARTED  |
| F3  | 10s timeout, one jittered retry, fallback to rules, triaged_by    | NOT STARTED  |
| F4  | Content-hash caching + measured hit rate                          | NOT STARTED  |
| F5  | Prompt injection guardrail + injection test                       | NOT STARTED  |
| F6  | Triage latency persisted and surfaced through provider metadata   | NOT STARTED  |
| F7  | PII/data-governance ADR                                           | NOT STARTED  |

### G — Docker and Compose (15 marks)

| ID  | Requirement                                                       | Status       |
|-----|-------------------------------------------------------------------|--------------|
| G1  | Multi-stage images, pinned bases, non-root, exec CMD, cache order | NOT STARTED  |
| G2  | Per-context .dockerignore + before/after context sizes            | NOT STARTED  |
| G3  | Two networks with internal=true, frontend cannot reach DB         | NOT STARTED  |
| G4  | Three named volumes justified, dev bind mount only in dev         | NOT STARTED  |
| G5  | Healthchecks all services + service_healthy dependencies          | NOT STARTED  |
| G6  | Prod compose: image ${IMAGE_TAG}, no build, no DB/cache ports     | NOT STARTED  |

### H — Kubernetes (20 marks)

| ID  | Requirement                                                       | Status       |
|-----|-------------------------------------------------------------------|--------------|
| H1  | Namespace, deployments, Postgres StatefulSet+PVC, ClusterIP, Ingress | NOT STARTED |
| H2  | ConfigMap/Secret separation; placeholders only in committed manifests | NOT STARTED |
| H3  | startup/liveness/readiness semantics correct                      | NOT STARTED  |
| H4  | requests/limits every container                                   | NOT STARTED  |
| H5  | HPA v2 tuned + hpa -w output + replicas-vs-load chart            | NOT STARTED  |
| H6  | VPA Off, recommendations committed, requests updated, conflict    | NOT STARTED  |

### I — CI/CD (20 marks)

| ID  | Requirement                                                       | Status       |
|-----|-------------------------------------------------------------------|--------------|
| I1  | ci.yml lint/type/test on every PR; required checks                | NOT STARTED  |
| I2  | Compose integration smoke job with real request path              | NOT STARTED  |
| I3  | Trivy + kubeconform in CI                                         | NOT STARTED  |
| I4  | cd.yml needs gating; GHCR images tagged by SHA                    | NOT STARTED  |
| I5  | Ephemeral K8s deploy waits for rollout and smoke-tests Ingress    | NOT STARTED  |
| I6  | GitHub Secrets + scoped token + least privilege permissions        | NOT STARTED  |
| I7  | Red pipeline blocked merge then green                             | NOT STARTED  |

### J — Documentation, Portfolio, Reflection (15 marks)

| ID  | Requirement                                                       | Status       |
|-----|-------------------------------------------------------------------|--------------|
| J1  | README: problem/badges/Mermaid/one-command/API/screenshots        | NOT STARTED  |
| J2  | Four ADRs                                                         | NOT STARTED  |
| J3  | RUNBOOK: deploy/rollback/logs/triage failure                      | NOT STARTED  |
| J4  | ≤5 minute demo, both partners, required scenarios                 | NOT STARTED  |
| J5  | ENGINEERING-NOTES answers all eight questions with file/line refs  | NOT STARTED  |

### Automatic Deduction Prevention

| ID   | Deduction | Guard                                                 | Status  |
|------|-----------|-------------------------------------------------------|---------|
| D01  | -20       | No .env/key/token/password in git history             | ✓ SAFE  |
| D02  | -15       | No LLM API key in committed K8s manifests             | ✓ SAFE  |
| D03  | -8        | No unpinned base image                                | PENDING |
| D04  | -8        | No localhost service-to-service in Docker/K8s          | PENDING |
| D05  | -8        | Frontend cannot reach database                        | PENDING |
| D06  | -8        | No published DB/Redis port in production              | PENDING |
| D07  | -8        | No publishing/deploying job without needs gating      | PENDING |
| D08  | -8        | Never deploy :latest                                  | PENDING |
| D09  | -8        | PostgreSQL is StatefulSet with PVC                    | PENDING |
| D10  | -5        | No direct commits pushed to main                      | ✓ SAFE  |
| D11  | -5        | README quickstart works from clean clone              | PENDING |

### Known Assignment Inconsistencies (from master XML)

| ID     | Description                                                        |
|--------|--------------------------------------------------------------------|
| AMB-01 | Page 1: Duration = 2 Weeks vs §5.1: ~35-45 hours over four weeks   |
| AMB-02 | Rubric says "ten endpoints" but API contract lists nine             |
| AMB-03 | Provider section specifies four but rubric requires ≥3              |
| AMB-04 | "Done" prose mentions signed images; Cosign is bonus                |

### Marks Discrepancy

Rubric section headings sum to **175** but assignment states **150** as total.
All 56 rubric items preserved; discrepancy recorded per master XML instruction.

---

## Phase History

### P00 — Forensics and Assignment Mapping
- **Date**: 2026-09-28
- **Status**: COMPLETE
- **Actions**: Repository inspected, master files read, branch strategy established, skeleton created
- **Gate**: PASSED
