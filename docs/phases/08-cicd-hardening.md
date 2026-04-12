# Phase 8: CI/CD Full Pipeline + Container Hardening

**Status:** In Progress 🟡 — WIF provider + first end-to-end CI run deferred
**Goal:** Every push to main runs lint → scan → test → build → deploy for ai-service and frontend independently, with no long-lived GCP keys and hardened containers.

## Architecture
![cicd hardening diagram](../diagrams/phase-08.png)
<!-- diagram file: docs/diagrams/phase-08.drawio -->
*GitHub push → Actions workflow exchanges an OIDC token with GCP Workload Identity Federation → short-lived credentials → Artifact Registry push → Cloud Run deploy (ai-service and/or frontend) → smoke tests.*

## What was built
- Full GitHub Actions pipeline (lint → SAST → SCA → test → container scan → build → deploy) — [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)
- Workload Identity Federation config for GitHub → GCP auth (no JSON keys in repo/secrets)
- Container hardening: non-root USER, digest-pinned base images across ai-service and frontend Dockerfiles
- PR path runs lint + test + scan but does NOT deploy; main path deploys independently per changed service
- End-to-end smoke tests for email → ai-service → reply, chatbot → ai-service → response, and resume → RAG → generation

## Key decisions
| Decision | Rationale | Reference |
|---|---|---|
| Workload Identity Federation | No long-lived service account keys; auditable short-lived tokens | [ci.yml](../../.github/workflows/ci.yml) |
| Digest-pinned base images | Supply-chain integrity; reproducible builds | Dockerfiles |
| Path-filtered deploys | Avoid redeploying the frontend when only ai-service changes | [ci.yml](../../.github/workflows/ci.yml) |
| Non-root USER in all containers | Defense-in-depth; Cloud Run best practice | ai-service + frontend Dockerfiles |

## What I learned
- Setting up WIF correctly is fiddly (provider, pool, attribute mapping, SA impersonation binding) — a single typo surfaces as opaque auth errors, which is why the first live CI run is deferred until the provider is verified.
- Digest pinning is easy to add but creates a small maintenance tax — needs a periodic refresh, ideally via Dependabot or Renovate.
- Splitting PR vs main behavior was the single biggest CI quality win — reviewers see fast feedback without production side effects.

## Links
- Source: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml), [`ai-service/Dockerfile`](../../ai-service/Dockerfile), [`frontend/Dockerfile`](../../frontend/Dockerfile)
- Previous: [Phase 7](./07-testing.md)
