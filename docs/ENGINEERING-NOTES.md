# ENGINEERING NOTES

**Q1: How did you prevent prompt injection?**
- **A1**: See `backend/app/providers/triage/simulated.py` and `backend/app/providers/triage/factory.py`. We sanitize inputs by enforcing strict Pydantic JSON schemas on output, and we have fallback mechanics that catch `ValueError` or JSON parsing errors if the LLM gets hijacked and returns garbage. Additionally, ADR-0002 details our data governance guardrails.

**Q2: Where does the pipeline sit on the course CI/CD maturity ladder?**
- **A2**: It sits at Level 3 (Continuous Delivery). It builds and pushes containers to GHCR tagged with immutable commit SHAs, generates SBOMs, and performs ephemeral deployments via `k3d` in `.github/workflows/cd.yml`. The next rung would be true Continuous Deployment (Level 4) directly to a live cluster (e.g. ArgoCD GitOps).

**Q3: How does the read-through cache invalidate?**
- **A3**: See `backend/app/services/stats_cache.py` and `backend/app/routes/complaints.py`. We call `stats_service.invalidate_stats()` whenever a `POST` or `PATCH` request alters complaint state.

**Q4: How does the system handle database outages?**
- **A4**: See `backend/app/routes/health.py`. The `/health` liveness probe remains active even if Postgres dies, meaning Kubernetes won't kill the pod prematurely. The `/ready` probe will fail, stopping traffic routing until Postgres recovers.

**Q5: How is PII handled?**
- **A5**: See `DATA-GOVERNANCE.md`. The contact info is partitioned into a separate column and never appended to the LLM prompt.

**Q6: Why FastAPI and not Flask?**
- **A6**: FastAPI provides automatic OpenAPI documentation generation and strongly typed request/response validation via Pydantic, enabling faster, safer contract integration with the frontend TypeScript types.

**Q7: How did we ensure idempotent seeding?**
- **A7**: See `backend/scripts/seed.py`. We use a `SELECT` check or `ON CONFLICT DO NOTHING` approach in SQLAlchemy before inserting the complaint fixtures, ensuring a second run alters nothing.

**Q8: Why is Kubernetes VPA turned off?**
- **A8**: VPA is set to `Off` (Recommendation Only) to prevent it from evicting and restarting pods mid-request. It generates recommendations that we manually review and commit to Git.
