# CivicPulse Master Prompt - Verification Report

Generated after a full review of the supplied 26-page CivicPulse assignment PDF.

## 1. Source inspection

- Source: `CS4032 - Software Construction and Design - Assignment 01 - CivicPulse`
- Pages: 26
- PDF inspection: 26 pages, no encryption, no forms, no attachments.
- Rendering: all 26 pages rendered to PNG and visually scanned as a contact sheet; rubric/notes/deduction/viva pages 19-24 were also inspected at full page scale because they contain the highest-risk grading details.
- Text basis: the parsed assignment text was cross-checked against the rendered pages for tables and rubric items.
- Source-alignment validator: each of the 56 rubric entries in the XML was compared against the assignment PDF vocabulary; all 56 exceeded the semantic token-overlap threshold used by the validator.

## 2. XML integrity and structure

| Check | Result |
|---|---|
| XML well-formed | PASS |
| Root element present | PASS |
| Implementation phases | 14 |
| Planned meaningful commits | 42 |
| Planned PRs | 8 |
| Rubric sections A-J | 10/10 |
| Printed rubric line items represented | 56/56 |
| Automatic deductions represented | 11/11 |
| Final quality gates | 23 |
| Repository layout entries represented | 32 |
| Mandatory documentation families represented | PASS |
| Mandatory evidence families represented | PASS |

The XML was parsed with an XML parser and checked with structural assertions. A second semantic-anchor pass verified the presence of representative requirements spanning the frontend, API, state machine, data layer, Redis, AI, Docker, Compose, Kubernetes, HPA/VPA, CI/CD, documentation, deductions, evidence, commits, PRs, and viva.

## 3. Rubric coverage

The master prompt contains a dedicated rubric matrix with one XML item for every printed rubric bullet.

| Section | Printed marks | Rubric items represented |
|---|---:|---:|
| A - Collaboration and version control | 15 | 5/5 |
| B - Frontend | 18 | 5/5 |
| C - Backend | 25 | 7/7 |
| D - Data layer | 12 | 4/4 |
| E - Cache layer | 10 | 4/4 |
| F - AI layer | 25 | 7/7 |
| G - Docker and Compose | 15 | 6/6 |
| H - Kubernetes | 20 | 6/6 |
| I - CI/CD | 20 | 7/7 |
| J - Documentation, portfolio and reflection | 15 | 5/5 |
| **Total of printed section headings** | **175** | **56/56** |

### Important source inconsistency discovered

The assignment says `150 marks`, but the printed section headings and line-item marks add up to **175**. The master prompt does not silently choose a subset. It preserves every printed rubric item and explicitly records the arithmetic discrepancy for the student to raise/confirm with the instructor.

## 4. Assignment contract coverage

### Problem and system behavior

Covered:
- free-text municipal complaint intake
- validation
- replaceable triage
- category/priority/summary
- durable persistence
- live operations dashboard
- aggregate statistics
- five local cooperating services
- one-command clean-clone startup
- second command for local Kubernetes
- CI deployment path and rollback

### Frontend

Covered:
- React 18 + Vite + TypeScript
- nginx multi-stage serving
- submit view
- loading state
- category/priority/summary/provider rendering
- paginated/filterable dashboard
- server 409 message surfacing
- stats + X-Cache
- runtime configuration without baked absolute API URL
- OpenAPI-checked typed client
- error boundary
- CORS with configurable origins
- no frontend secrets
- >=5 meaningful component tests

### Backend

Covered:
- FastAPI + Pydantic v2
- routes/services/repositories/providers separation
- no SQL outside repositories
- no business rules in routes
- complete contract endpoints listed by the assignment
- field-level HTTP 400 validation body
- pagination/filter rules
- explicit status transition table
- health/readiness separation
- request ID propagation
- JSON stdout logging
- fallback warning semantics
- SIGTERM/graceful shutdown
- Prometheus `/metrics`

### Data

Covered:
- PostgreSQL 16
- Alembic-only schema management
- exact required complaint columns
- database-level text length enforcement
- required enum values
- UTC timestamptz
- two required indexes
- index/query justification
- >=30 realistic Urdu-influenced English seed complaints
- idempotent seed
- Compose persistence
- Kubernetes persistence through StatefulSet/PVC

### Redis

Covered:
- Redis 7
- stats read-through cache
- 30-second TTL
- X-Cache HIT/MISS
- write invalidation
- content-hash triage cache
- 24-hour triage cache TTL
- measured cache hit rate
- distributed IP-based rate limiter
- Redis-backed rather than process-local limiter
- 429 + Retry-After
- Redis AOF + named volume
- written justification for cache persistence

### AI

Covered:
- TriageResult schema
- TriageProvider protocol
- hosted LLM path
- Ollama path
- deterministic rules path
- deterministic simulated CI path
- TRIAGE_PROVIDER factory selection
- structured output request
- Pydantic validation
- malformed-output rejection
- 10-second call timeout
- exactly one retry with jitter for timeout/429/5xx only
- no retry on 400
- rules fallback
- `rules:fallback`
- content-hash caching
- cache hit-rate measurement
- API-key secrecy
- prompt-injection guardrail and test
- `triage_latency_ms`
- provider metadata surface
- PII/data-governance ADR
- live verification of current provider limits/policy

### Docker and Compose

Covered:
- two custom multi-stage images
- required base families
- non-root
- exec-form CMD
- Docker HEALTHCHECK
- dependency-before-source cache order
- frontend final image without Node/node_modules/source
- frontend size measurement
- per-context `.dockerignore`
- before/after build-context measurements
- edge/internal networks
- internal network with `internal: true`
- frontend cannot reach database
- three named volumes
- development bind mount only in dev
- healthchecks + `service_healthy`
- `.env` / `.env.example` / `.gitignore`
- pinned image tags
- `unless-stopped`
- resource limits
- production image-based Compose file
- `${IMAGE_TAG}`
- no production DB/cache ports

### Kubernetes

Covered:
- kind/k3d
- namespace `civicpulse`
- Kustomize base + dev/prod overlays
- backend Deployment >=2 replicas
- frontend Deployment >=2 replicas
- PostgreSQL StatefulSet
- PostgreSQL PVC through volumeClaimTemplates
- Redis Deployment + PVC
- four ClusterIP services
- Ingress `/` -> frontend, `/api` -> backend
- ConfigMap/Secret separation
- placeholder-only committed Secret manifest values
- three probes with correct semantics
- resource requests/limits on every container
- backend HPA v2
- HPA 2-10 replicas
- CPU 60%
- scale-down stabilization 300s
- scale-up stabilization 0s
- metrics-server
- k6/hey load generation
- `kubectl get hpa -w`
- replicas-vs-load chart
- measured HPA lag
- VPA Off/recommender mode
- Target/Lower Bound/Upper Bound evidence
- request adjustment and retest
- HPA/VPA conflict explanation
- backend PDB minAvailable 1
- rolling-update controls
- preStop + termination grace
- Postgres pod deletion persistence test

### CI/CD

Covered:
- `ci.yml` PR-to-main and push-to-dev
- backend ruff/mypy
- frontend eslint/tsc
- backend pytest + >=65% coverage on app/
- simulated provider in CI
- frontend Vitest >=5
- build without push in CI
- Trivy HIGH/CRITICAL gate with pinned/fixed scanner reference
- kubeconform validation
- Compose integration path with MISS -> HIT assertion
- `cd.yml` on push to main
- full test gate
- GHCR
- SHA tags
- `latest` may be pushed but never deployed
- Syft SBOM
- captured digest output
- ephemeral Kubernetes cluster
- rollout wait
- Ingress smoke test
- HPA print
- `release.yml` on `v*`
- semver tags
- release notes
- GitHub Secrets
- scoped credentials
- least-privilege permissions
- pinned Actions
- red-pipeline/blocked-merge/green evidence
- two rollback mechanisms

### Documentation and evidence

Covered:
- README requirements
- four ADRs
- RUNBOOK
- TRIAGE.md
- ENGINEERING-NOTES.md with eight repository-specific questions
- AI-USAGE.md
- evidence directory
- <=5 minute demo plan with both partners
- submission artifact checklist
- `scripts/check_submission.py`

## 5. Collaboration requirements

The master prompt deliberately plans **42 meaningful commits**, exceeding the assignment minimum of 35. The suggested ownership alternates across the two partners, targeting roughly 21 commits each and therefore providing a large safety margin over the 35% floor.

It also plans **8 PRs**, each tied to an Issue and requiring substantive partner review. The prompt explicitly treats the actual partner review and branch-protection screenshots as human/account evidence and forbids fabrication.

A real-code merge conflict is explicitly planned and must include conflict/resolution/merge evidence plus the required 2-4 sentence explanation.

## 6. Automatic-deduction coverage

All 11 printed deduction triggers are explicitly represented in the master prompt, including:

- secrets in git history
- LLM key in Kubernetes manifests
- unpinned images
- localhost service-to-service communication
- frontend-to-database reachability
- production DB/cache ports
- missing `needs:` gating
- deploying `:latest`
- PostgreSQL as Deployment without PVC
- direct main commits
- broken clean-clone README quickstart

The XML also includes a static submission-checker specification aimed at catching these mechanical failures before submission.

## 7. Engineering-note coverage

All eight questions in §5.2 are represented, including:

1. laptop vs CI differences and exact lines freezing them
2. CI/CD maturity ladder position
3. exact build-once-deploy-many line
4. correctness for probabilistic LLMs and deterministic CI
5. measured HPA lag
6. VPA Off and HPA/VPA conflict
7. outbound hosted-LLM networking with `internal: true`
8. one real >1-hour failure, wrong initial belief, and diagnostic command/log

The prompt requires actual repository line references and explicitly rejects generic answers.

## 8. Evidence integrity

The master prompt contains a strong non-fabrication rule. It distinguishes:

- code/configuration the agent can implement and test
- external provider information that must be checked live
- GitHub branch protection and partner reviews
- workflow runs and GHCR artifacts
- screenshots/video
- HPA/VPA measurements

The agent is instructed to leave only true external/human blockers open and to provide exact capture instructions rather than inventing successful evidence.

## 9. Important implementation ambiguities handled explicitly

### 9.1 Printed marks vs total

Preserved all rubric items while documenting the 175-vs-150 arithmetic discrepancy.

### 9.2 Nine visible API endpoints vs rubric wording of ten

Implements all explicitly listed application endpoints and does not invent a tenth business endpoint solely from the typo/inconsistency.

### 9.3 Four providers vs rubric minimum of three

Plans all four named providers, including the deterministic simulated CI provider.

### 9.4 Simulated provider vs `triaged_by` enum

The assignment's persisted enum does not include `llm:simulated`. The master prompt therefore keeps the runtime/observability identity of the simulated provider separate and requires a documented semantic identity from the assignment's persisted enum for CI-only persisted test data, rather than silently widening the required enum.

### 9.5 Hosted LLM vs internal Docker network

The prompt explicitly preserves backend outbound access by placing the backend on the external-capable edge network plus the internal network, while keeping PostgreSQL and Redis internal-only. Ollama is allowed onto the external-capable side only as needed for model bootstrap, without publishing its port.

## 10. What this verification does NOT prove

This verification proves the **master prompt is structurally and semantically aligned with the supplied assignment statement**. It does not prove that a future Claude execution will produce a perfect repository without actually running that execution.

In particular, the following still require real-world execution/evidence:

- GitHub branch protection configuration
- actual partner approvals/review comments
- actual commit distribution between both humans
- actual provider free-tier limits/policies at execution time
- real GHCR images and workflow runs
- real HPA/VPA measurements
- screenshots and demo video
- the team's actual >1-hour failure narrative
- the student's individual viva performance

## 11. Final validation conclusion

**Master prompt XML integrity: PASS.**

**Printed rubric-line coverage: 56/56.**

**Automatic-deduction coverage: 11/11.**

**Implementation phases: 14.**

**Commit plan: 42.**

**PR plan: 8.**

**Final quality gates: 23.**

The XML is designed as a repository-agent master prompt rather than a generic coding prompt. It explicitly separates implementation, verification, collaboration, evidence, documentation, and viva requirements so that a future implementation agent is less likely to satisfy the application behavior while missing the grading contract.
