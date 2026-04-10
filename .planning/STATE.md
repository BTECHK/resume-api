---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: Core Resume API
status: Executing Phase 05
stopped_at: Completed 05-02 Task 1 (runbook scaffold); Task 2 GCP Console human-action deferred to DEFERRED-WORK.md
last_updated: "2026-04-10T21:35:00.000Z"
progress:
  total_phases: 4
  completed_phases: 1
  total_plans: 23
  completed_plans: 7
---

# Project State

## Current Position

Phase: 05 (n8n-email-bot) — EXECUTING
Plan: 1 of 4

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-08)

**Core value:** Recruiters can ask natural language questions about the candidate's background and get grounded, accurate answers — via email or chat.
**Current focus:** Phase 05 — n8n-email-bot

## Progress Bar

```
v2.0: [Phase 4] [Phase 5] [Phase 6] [Phase 7] [Phase 8]
       ------     ------    ------    ------    ------
       Active     Queued    Queued    Queued    Queued
```

## Performance Metrics

- Requirements defined: 45 (v2.0)
- Requirements mapped: 45/45 (100%)
- Phases planned: 0/5
- Plans written: 0

## Accumulated Context

### From Phase 1 (v1.0)

- 9 REST endpoints deployed on Cloud Run (live at resume-api-711025857117.us-central1.run.app)
- SQLite operational database (10K rows)
- Docker containerization + Cloud Run deployment working
- Request logging middleware with funnel tracking
- Docker Compose + systemd for persistent hosting set up

### Key Workflow Change (v2.0)

- **Old:** Claude writes guides, user builds by hand (learning project)
- **New:** Vibe coding — Claude writes code directly (portfolio project, speed priority)
- Phase 2 (ETL/Locust) dropped entirely — moved to separate portfolio project

### Files Already Created (pre-GSD, during v2.0 scoping)

- `ai-service/resume_data.py` — Structured resume content for RAG (needs anonymization pass)
- `ai-service/prompts.py` — System prompts for Gemini (email, chat, general)
- `ai-service/rag.py` — Chroma + embeddings logic (needs review/update)
- `ANONYMIZATION_GUIDE.md` — Anonymization rules and audit checklist
- `tasks/prd-resume-ai-platform.md` — Full PRD with 15 user stories

### Architecture Decisions Locked (v2.0)

- Separate `ai-service/` service — Phase 1 API untouched
- paraphrase-MiniLM-L3-v2 (33MB) — NOT all-MiniLM-L6-v2 (420MB) — critical for cold start
- google-genai SDK — NOT google-generativeai (deprecated Nov 2025)
- Chroma in-memory, re-ingests on cold start from bundled data files
- n8n on e2-micro with 2GB swap and Docker mem_limit: 700m
- Gmail OAuth app in Production mode — prevents 7-day token expiry
- GCP Workload Identity Federation with numeric repo ID (keyless CI/CD auth)

### Critical Pitfalls to Watch (from research)

1. Cold start timeout — 33MB model baked into image, lazy init
2. Gmail OAuth 7-day expiry — must set app to Production mode in Phase 5
3. n8n OOM on e2-micro — 2GB swap + Docker mem_limit: 700m required
4. CORS not configured before frontend — must be live by Phase 4 completion
5. Artifact Registry overage — pruning policy in Phase 8

### Phase Dependency Chain

```
Phase 4 (ai-service live) → Phase 5 (email bot) in parallel with Phase 6 (frontend)
                          → Phase 7 (differentiators extend Phase 4)
All 4 above → Phase 8 (CI/CD wires everything, smoke tests verify end-to-end)
```

## Decisions

### Phase 04

- `pythonpath=.` in pytest.ini mirrors uvicorn runtime so test imports match production (04-00)
- Test stubs for rag/security/main assert module structure only; full behavioral tests deferred to Phase 7 (04-00)
- FLAG_DURATION_SECONDS=300 (5 min): less punishing for false positives than research-recommended 15 min (04-02)
- secrets.py renamed to gcp_secrets.py to fix stdlib shadow conflict — Plan 03 must import from gcp_secrets (04-02)
- RESPONSE_SCRUB_PATTERNS reimplements PII regex independently from scrub.py (belt-and-suspenders D-08/D-10) (04-02)
- Dedicated service account 'resume-ai-service' (not default compute SA) for least-privilege secretAccessor access (04-04)
- Billing budget documented as Console + gcloud CLI paths — Console is more reliable for billing APIs (04-04)

## Session Continuity

**Last session:** 2026-04-10T21:35:00Z
**Stopped at:** Completed 05-02-PLAN.md Task 1 (a5a6b25). Task 2 (GCP Console human-action) deferred to DEFERRED-WORK.md per scaffold-first mode.

**To resume:** When ready for manual GCP work, open DEFERRED-WORK.md and follow the "Plan 05-02 Task 2" entry (runs `n8n/docs/gmail-oauth-setup.md` end-to-end). Meanwhile, Plan 05-03 (n8n workflow) can proceed since it consumes the .env template, not the live secrets.

**Next decision needed:** None — scaffold-first mode continues.

### Phase 05 Decisions

- Plan 05-02: Task 2 human-action checkpoint (Gmail OAuth GCP Console clicks) deferred to DEFERRED-WORK.md per scaffold-first session. Runbook, reference table, and .env template all in place.
- Plan 05-02: D-02 exception documented — Web Application OAuth 2.0 clients require GCP Console (gcloud iap oauth-clients only creates IAP clients).

---
*State updated: 2026-04-09 after completing plan 04-02*
