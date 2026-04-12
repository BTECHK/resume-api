# Phase 3: IaC + CI/CD + AI Scaffolding + Security

**Status:** Done ✅ — shipped in milestone v1.0
**Goal:** Wrap the API in Terraform-managed infrastructure, an automated GitHub Actions pipeline, an initial AI RAG feature, and OWASP-aligned security tooling.

## Architecture
![iac cicd ai diagram](../diagrams/phase-03.png)
<!-- diagram file: docs/diagrams/phase-03.drawio -->
*GitHub push triggers Actions (lint → scan → test → build → deploy); Terraform modules provision VPC, IAM, Cloud Run, BigQuery, and Artifact Registry; a first-pass RAG feature sits behind /ai/ask.*

## What was built
- Terraform modules for VPC, IAM, Cloud Run, VM, BigQuery, Artifact Registry with GCS remote state — [`infra/terraform/`](../../infra/terraform/)
- GitHub Actions CI pipeline: Ruff → Bandit → pip-audit → pytest → Trivy → Docker build → deploy — [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)
- First-pass AI endpoints (`/ai/ask`, `/ai/skills/match`) using HuggingFace embeddings + Chroma + Gemini 2.5 Flash
- Security headers middleware + rate-limit headers; Trivy/Bandit/pip-audit scanning in CI
- Threat model + OWASP API Security Top 10 mapping — [`SECURITY.md`](../../SECURITY.md)

## Key decisions
| Decision | Rationale | Reference |
|---|---|---|
| Terraform modules + GCS remote state | Reproducible infra; shareable state across pipeline | [phase-3-implementation-guide.md](../phase-3-implementation-guide.md) |
| Ruff over flake8 + isort | Single fast tool, fewer config files | [.github/workflows/ci.yml](../../.github/workflows/ci.yml) |
| Gemini 2.5 Flash, not Pro | Cost + latency tradeoff for short grounded answers | [ADR-0003](../adrs/0003-gemini-25-flash.md) |
| RAG scaffolded inside main API | Phase 3 scope; split to dedicated service in Phase 4 | [ADR-0004](../adrs/0004-separate-ai-service.md) |

## What I learned
- Running four scanners (Ruff, Bandit, pip-audit, Trivy) adds ~2 min to CI but catches distinct classes of issues — worth the cost.
- Putting AI in the main API was the fastest path to "works" but made the image big and coupled embeddings startup to the resume endpoints — which is why Phase 4 splits it out.
- Terraform remote state in GCS unblocks CI deploys cleanly; local state would have been a dead end for GitHub Actions.

## Links
- Source: [`infra/terraform/`](../../infra/terraform/), [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)
- Full walkthrough: [docs/phase-3-implementation-guide.md](../phase-3-implementation-guide.md)
- Security: [SECURITY.md](../../SECURITY.md)
- Next: [Phase 4](./04-rag-service.md)
