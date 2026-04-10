---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: Core Resume API
status: Executing Phase 05
stopped_at: Completed 05-03-PLAN.md Task 1 (n8n workflow JSON + build guide + import runbook); Task 2 deferred to DEFERRED-WORK.md per scaffold-first
last_updated: "2026-04-10T22:15:00.000Z"
progress:
  total_phases: 4
  completed_phases: 1
  total_plans: 23
  completed_plans: 8
---

# Project State

## Current Position

Phase: 05 (n8n-email-bot) — EXECUTING
Plan: 4 of 4 (05-01, 05-02, 05-03 complete — 05-03 Task 2 deferred)

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

**Last session:** 2026-04-10T22:15:00Z
**Stopped at:** Completed 05-03-PLAN.md Task 1 (n8n workflow JSON `email-bot.json` + `error-handler.json`, build guide, import runbook). Plan 05-03 Task 2 (n8n UI import + credential re-link + dry-run) deferred to DEFERRED-WORK.md per scaffold-first mode.

**To resume:** Next plan is 05-04 (smoke tests + phase summary). When ready for manual live work, resolve DEFERRED-WORK.md entries in order: (1) Plan 05-01 `terraform apply`, (2) Plan 05-02 Task 2 OAuth runbook, (3) Plan 05-03 Task 2 workflow import runbook (`n8n/docs/workflow-import-runbook.md`).

**Next decision needed:** None — scaffold-first mode continues.

### Phase 05 Decisions

- Plan 05-01: Terraform module uses ephemeral external IP on e2-micro (not IAP tunnel) for operator SSH — D-09 network access simplified for portfolio scope; firewall opens port 22 only.
- Plan 05-01: cloud-platform service account scope on the VM enables future Secret Manager access for Gmail OAuth secrets without re-provisioning.
- Plan 05-01: startup.sh enables n8n.service but deliberately does NOT start it — operator must scp docker-compose.yml + edit /opt/n8n/.env first, otherwise the unit would fail and be marked failed on first boot.
- Plan 05-01: systemd unit uses Type=oneshot + RemainAfterExit=yes + Restart=on-failure (NOT Restart=always) to avoid double-start conflict with compose restart:unless-stopped (Pitfall #3).
- Plan 05-01: Inline systemd unit heredoc in startup.sh is byte-for-byte identical to the committed n8n/systemd/n8n.service — single source of truth for the unit file, verified via diff.
- Plan 05-02: Task 2 human-action checkpoint (Gmail OAuth GCP Console clicks) deferred to DEFERRED-WORK.md per scaffold-first session. Runbook, reference table, and .env template all in place.
- Plan 05-02: D-02 exception documented — Web Application OAuth 2.0 clients require GCP Console (gcloud iap oauth-clients only creates IAP clients).
- Plan 05-03: D-14 `/chat` endpoint override honored throughout workflow JSON, build guide, and import runbook — REQUIREMENTS.md §EMAIL-03 text ("/ai/ask") predates the Phase 5 context session and is superseded for thread-aware conversations.
- Plan 05-03: AI_SERVICE_URL has no `:8090` port suffix — RESEARCH.md code examples show `:8090` for local docker-compose only; Cloud Run terminates HTTPS on 443 implicitly. Both workflow JSON and docs explicitly warn against copying the dev example.
- Plan 05-03: Single-message `/chat` MVP — Code node emits one `{role:'user',content}` per email. Thread history fetching (Gmail Thread > Get) deferred to Phase 5.5+ as a pure code-node enhancement; ai-service already supports up to 10-message history.
- Plan 05-03: All Gmail node credential IDs use `REPLACE_AFTER_IMPORT` placeholder (Pitfall #5). Import runbook Step 7 walks operator through re-linking `Gmail Bot Account` on all 4 Gmail nodes.
- Plan 05-03: Task 2 human-verify checkpoint (live n8n import + dry-run) deferred to DEFERRED-WORK.md per scaffold-first session. Depends on Plan 05-01 VM + Plan 05-02 OAuth + Phase 4 ai-service deployment.

---
*State updated: 2026-04-09 after completing plan 04-02*
