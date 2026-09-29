# CivicPulse RUNBOOK

## 1. Deployment Process
### Standard Update
1. Merge PR to `main` to trigger the `.github/workflows/cd.yml` workflow.
2. The pipeline will build the image, push to GHCR, and apply the Kubernetes manifests to production using the new immutable SHA.
3. Run `kubectl rollout status deployment/backend -n civicpulse` to verify.

## 2. Rollback Procedure
If a bad deployment goes live:
1. Revert the commit in GitHub or trigger a manual rollback.
2. Imperative quick rollback: 
   ```bash
   kubectl rollout undo deployment/backend -n civicpulse
   ```
3. Declarative rollback: Re-apply the previous production overlay kustomization pointing to the last known good SHA.

## 3. Retrieving Logs
- Backend Logs: `kubectl logs -l app=backend -n civicpulse --tail=100 -f`
- Postgres Logs: `kubectl logs -l app=postgres -n civicpulse -f`

## 4. Triage Failure Recovery
If the primary AI provider (e.g. Groq) fails entirely:
1. The system automatically falls back to `rules`. No immediate action is strictly required.
2. To switch providers manually:
   - Edit `k8s/base/config.yaml` and set `TRIAGE_PROVIDER` to `ollama` or `rules`.
   - Apply changes: `kubectl apply -k k8s/overlays/prod`
   - Restart pods: `kubectl rollout restart deployment/backend -n civicpulse`
