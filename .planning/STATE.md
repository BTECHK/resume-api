---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: Core Resume API
status: Phase 05 scaffold-complete (live validation deferred); Phase 06 planned (4 plans, PASS_WITH_NOTES, ready for execute-phase)
stopped_at: "Completed Plan 06-02 (landing + chat UI, Apple HIG). Next: /gsd:execute-phase 6 continues with Plan 06-03 (API client wiring)."
last_updated: "2026-04-11T16:09:30.889Z"
progress:
  total_phases: 5
  completed_phases: 2
  total_plans: 27
  completed_plans: 14
---

# Project State

## Current Position

Phase: 06 (react-chatbot-frontend) — PLANNED, ready for `/gsd:execute-phase 6`
Phase 05 (n8n-email-bot) — SCAFFOLD-COMPLETE, live validation deferred to DEFERRED-WORK.md
Plans remaining in Phase 6: 4 of 4 (all written, plan-checked PASS_WITH_NOTES)

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
- [Phase 06]: Plan 06-02: Apple HIG components (Header, MessageBubble, TypingIndicator, ChatInput) built with inline SVG only (zero icon libs), tokens consumed from index.css @theme via Tailwind arbitrary-value utilities
- [Phase 06]: Plan 06-02: Chat.tsx seeded with hardcoded 3-message array (greeting + sample user/bot) + stub handleSend with 600ms fake reply — Plan 06-03 will rip these out and wire real /chat POST to ai-service

## Session Continuity

**Last session:** 2026-04-11T16:09:19.591Z
**Stopped at:** Completed Plan 06-02 (landing + chat UI, Apple HIG). Next: /gsd:execute-phase 6 continues with Plan 06-03 (API client wiring).

**Artifacts produced this session:**

- `.planning/phases/06-react-chatbot-frontend/06-CONTEXT.md` (200 lines, D-01..D-13 locked)
- `.planning/phases/06-react-chatbot-frontend/06-RESEARCH.md` (1565 lines, 8 tracks, code snippets)
- `.planning/phases/06-react-chatbot-frontend/06-01-PLAN.md` (459 lines — Vite/React/TS/Tailwind scaffold)
- `.planning/phases/06-react-chatbot-frontend/06-02-PLAN.md` (642 lines — Landing + Chat UI + Apple HIG)
- `.planning/phases/06-react-chatbot-frontend/06-03-PLAN.md` (431 lines — API client + `/chat` integration)
- `.planning/phases/06-react-chatbot-frontend/06-04-PLAN.md` (731 lines — Dockerfile + nginx + deploy.sh + DEFERRED-WORK entries)

All planning artifacts are on disk in the gitignored `.planning/` tree. Nothing is committed (matches prior phase convention — only SUMMARY files are force-tracked).

**To resume — primary action:**

```
/gsd:execute-phase 6
```

Use scaffold-first mode. Plans run sequentially (06-01 → 06-02 → 06-03 → 06-04), no parallel waves possible (each plan touches files the next builds on).

**To resume — deferred work order (when live GCP stack is ready):**

1. Phase 4 04-04 Task 2 — run `gcp-setup.sh` (blocks everything else)
2. Deploy ai-service to Cloud Run (Phase 8 CI/CD, can be done manually earlier)
3. Phase 5 05-01 — `cd terraform/n8n-vm && terraform init && terraform apply`
4. Phase 5 05-02 Task 2 — Gmail OAuth Publish to Production (per `n8n/docs/gmail-oauth-setup.md`)
5. Phase 5 05-03 Task 2 — n8n workflow import + credential re-link (per `n8n/docs/workflow-import-runbook.md`)
6. Phase 5 05-04 Task 3 — end-to-end smoke test + uptime check + Phase Summary Part E
7. (After Phase 6 execution) Phase 6 deferred Tasks A-E — Docker build, push, Cloud Run deploy, ALLOWED_ORIGINS swap, smoke test

**Next decision needed:** None. Just run `/gsd:execute-phase 6` to continue, or tackle deferred work live.

### Phase 06 Decisions (locked in 06-CONTEXT.md)

- D-01: React Router v7 data router (`react-router` package, NOT `react-router-dom` — Pitfall #1)
- D-02: Apple Human Interface aesthetic — system font stack, generous whitespace, glass/blur headers, `rounded-2xl`, warm off-white `#fafaf9`
- D-03: Direct CORS to ai-service Cloud Run URL (no reverse proxy, no same-origin StaticFiles mount)
- D-04: Scaffold-first mode (same as Phase 5) — defer `docker build` + `gcloud run deploy` + CORS origin swap to DEFERRED-WORK.md
- D-05: React 19.2 + Vite 8.0 + TypeScript 6 + Tailwind v4.2 (CSS-first `@import "tailwindcss"` + `@theme` in `index.css`, NO `tailwind.config.ts`)
- D-06: Cloud Run service name `resume-chatbot`, region `us-central1`, port 8080
- D-07: Multi-stage Dockerfile — `node:20-alpine` build → `nginx:1.27-alpine` serve (digest pinning deferred to Phase 8)
- D-08: Landing hero + 2 CTAs (Chat → `/chat` Link, Email → native `mailto:`)
- D-09: Chat screen = header + scrollable message list + typing indicator + bottom textarea (Enter to send, 500 char client cap mirrors SEC-03)
- D-10: In-memory conversation state (`useState`), last 10 messages, NO localStorage persistence
- D-11: Zero analytics / zero cookies / zero third-party scripts
- D-12: New top-level `frontend/` directory (parallel to `ai-service/`)
- D-13: No unit tests in Phase 6 — only `npm run build` smoke gate; Phase 7 handles testing per TEST-01..TEST-04
- Dockerfile non-root fix (Pitfall #5): BOTH halves required — `chown /tmp/nginx.pid` in Dockerfile AND `pid /tmp/nginx.pid;` directive in nginx.conf. Plan 06-04 enforces both via grep-strict acceptance.
- Auto dark mode via `prefers-color-scheme` — included (zero JS cost via Tailwind v4 `dark:` variant default)
- `nginx:1.27-alpine` kept per D-07 lock (not bumped to 1.28 despite research suggestion — bump in Phase 8 hardening)
- Dependency chain strictly sequential: 06-01 → 06-02 → 06-03 → 06-04 (no parallelism possible; 06-03 overwrites Chat.tsx which 06-02 creates; 06-04 COPYs full frontend tree)

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
- Plan 05-04: TCP-22 uptime check chosen over HTTP `/healthz` — n8n port 5678 is not publicly reachable per D-09; HTTP probing would require an nginx reverse-proxy sidecar or Ops Agent, both out of Phase 5 scope.
- Plan 05-04: Phase summary skeleton written BEFORE the human checkpoint (Task 2) so a durable artifact exists even if the checkpoint is interrupted; Task 3b is the "finalize skeleton" companion that fills in Results Table post-smoke-test.
- Plan 05-04: EMAIL-05 already satisfied by commit `1ba4ea4` (Plan 05-03 committed both workflow JSON files); the plan's Task 3 Part C is a no-op. Phase summary pre-marks EMAIL-05 ✅ with commit hash as proof.
- Plan 05-04: Task 3b (auto post-checkpoint) SKIPPED (not deferred) — its edits cannot run without Task 3 data. Instructions re-parented to Part E of the DEFERRED-WORK.md Plan 05-04 Task 3 entry.

---
*State updated: 2026-04-09 after completing plan 04-02*
