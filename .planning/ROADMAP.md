# Resume API Portfolio — Project Roadmap

## Milestone v1.0: Core Resume API (Complete)

Phases 1–3 shipped. REST API with 9 endpoints, SQLite operational DB, BigQuery analytical DB, 3-tier SQL progression, scale benchmarks, Docker + Cloud Run deployment, Docker Compose + systemd, request logging middleware, comprehensive documentation.

---

## Milestone v2.0: Resume AI Platform (Active)

**Started:** 2026-04-08
**Goal:** Evolve from static REST API into AI-powered career knowledge platform with email bot, RAG database, and recruiter-facing chatbot.

## Phases

- [x] **Phase 4: RAG Core Service** — AI service on Cloud Run with Chroma vector store, Gemini generation, and full security middleware (scaffold-complete, live deploy deferred)
- [x] **Phase 5: n8n Email Bot** — Self-hosted email bot on GCE e2-micro with Gmail OAuth, swap, and workflow version control (scaffold-complete, terraform apply + n8n import deferred)
- [x] **Phase 6: React Chatbot Frontend** — Polished recruiter-facing chat UI on Cloud Run with mobile-responsive design (scaffold-complete, Cloud Run deploy + CORS swap deferred)
- [x] **Phase 7: Differentiators + Testing** — Two-tier RAG, architecture self-awareness, unanswered question logging, and full pytest suite (61 local + 25 CI-gated tests)
- [x] **Phase 8: CI/CD + Final Hardening** — GitHub Actions pipeline, Workload Identity Federation, container hardening, smoke tests, and documentation (scaffold-complete, WIF provider + first CI run deferred)

## Phase Details

### Phase 4: RAG Core Service
**Goal**: Recruiters can ask questions via POST /ai/ask and receive grounded, accurate answers powered by Gemini and Chroma — with full security middleware active
**Depends on**: Phase 1 (existing Cloud Run API untouched; new ai-service deployed independently)
**Requirements**: RAG-01, RAG-02, RAG-03, RAG-04, RAG-08, SEC-01, SEC-02, SEC-03, SEC-05, SEC-06, SEC-07, SEC-08, SEC-09, CHAT-04
**Success Criteria** (what must be TRUE):
  1. POST /ai/ask returns a grounded answer with source references within the Cloud Run cold start window
  2. POST /chat accepts a conversation history of up to 10 messages and returns a contextually coherent response
  3. A request exceeding 10 req/min from the same IP receives a 429 response
  4. A prompt containing known injection patterns is detected, logged, and rate-reduced without leaking internal details
  5. GCP Secret Manager holds all credentials; no secrets appear in code, images, or environment variables committed to the repo
**Plans:** 1/5 plans executed

Plans:
- [x] 04-00-PLAN.md — Test infrastructure (pytest.ini, conftest.py, test stubs)
- [ ] 04-01-PLAN.md — Fix rag.py bugs, anonymize data files, create secrets.py
- [x] 04-02-PLAN.md — Create security.py (injection detection, response sanitization)
- [ ] 04-03-PLAN.md — Create main.py (FastAPI app with /ai/ask, /chat, /health)
- [ ] 04-04-PLAN.md — GCP infrastructure setup (Secret Manager, billing alert, Artifact Registry pruning)

**UI hint**: no

### Phase 5: n8n Email Bot
**Goal**: An email sent to the dedicated recruiter inbox triggers an automated, AI-powered reply within ~5 min poll + processing time (per CONTEXT.md D-03 — user accepted 5-minute interval over original 60s target for quota headroom)
**Depends on**: Phase 4 (ai-service /chat endpoint must be live — D-14 uses /chat for thread-aware conversations)
**Requirements**: EMAIL-01, EMAIL-02, EMAIL-03, EMAIL-04, EMAIL-05, EMAIL-06, EMAIL-07
**Success Criteria** (what must be TRUE):
  1. n8n container starts successfully on the e2-micro VM with 2GB swap and does not OOM under normal load
  2. An email sent to the dedicated inbox receives an AI-generated reply within ~5 minutes + processing time (per D-03)
  3. When ai-service is unreachable, the sender receives a polite fallback reply — not silence or an error trace
  4. The n8n workflow JSON is committed to n8n/workflows/ and the VM auto-restarts n8n on reboot via systemd
  5. Gmail OAuth app is in Production mode and tokens do not expire after 7 days
**Plans:** 4 plans

Plans:
- [x] 05-01-PLAN.md — Terraform GCE e2-micro VM with 2GB swap, Docker, systemd unit (EMAIL-01, EMAIL-06)
- [x] 05-02-PLAN.md — Gmail OAuth Production mode runbook + .env.example (EMAIL-07)
- [ ] 05-03-PLAN.md — n8n workflow JSON: Gmail Trigger → filter → /chat → reply + fallback + error handler (EMAIL-02, EMAIL-03, EMAIL-04)
- [ ] 05-04-PLAN.md — GCP uptime check, end-to-end smoke test, workflow commit, phase summary (EMAIL-05)

### Phase 6: React Chatbot Frontend
**Goal**: Recruiters can open a polished web UI and have a natural language conversation about the candidate's background from any device
**Depends on**: Phase 4 (ai-service /chat endpoint must be live with CORS configured)
**Requirements**: CHAT-01, CHAT-02, CHAT-03, CHAT-05, CHAT-06, CHAT-07, CHAT-08
**Success Criteria** (what must be TRUE):
  1. Landing page loads with two CTAs: "Email My Resume" (opens native mailto) and "Chat With My Resume" (navigates to chat). Apple-style minimal design.
  2. The chatbot loads, displays an auto-greeting, and accepts a typed question without any setup by the recruiter
  3. The chat UI renders correctly on a mobile phone screen — landing page, chat bubbles, header, and input are all usable
  4. The frontend is deployed to Cloud Run via a multi-stage Docker build (Node build → Nginx serve) and is publicly reachable
  5. The candidate's professional title appears in the header, and the overall visual design is polished enough to share in a job application
**Plans**: TBD
**UI hint**: yes

### Phase 7: Differentiators + Testing
**Goal**: The AI service demonstrates interview-impressive capabilities — two-tier retrieval, architecture self-awareness, unanswered question logging — and has an 80%+ tested codebase
**Depends on**: Phase 4 (base RAG service), Phase 6 (frontend needed for /chat integration tests)
**Requirements**: RAG-05, RAG-06, RAG-07, TEST-01, TEST-02, TEST-03, TEST-04
**Success Criteria** (what must be TRUE):
  1. A question about mock interview style returns an answer that draws from the Tier 2 collection without contaminating Tier 1 factual answers
  2. A question asking how the system works returns an answer that accurately describes architecture decisions from embedded ADR content
  3. A question the bot cannot answer is written to the unanswered questions log file for future knowledge base improvement
  4. pytest runs successfully and reports 80%+ coverage on ai-service code
  5. Security tests confirm prompt injection is detected, rate limiting triggers at the configured threshold, and oversized inputs are rejected with a 422
**Plans**: TBD

### Phase 8: CI/CD + Final Hardening
**Goal**: Every push to main triggers an automated pipeline that lints, tests, scans, builds, and deploys — and the project is fully documented with a progression narrative
**Depends on**: Phase 4, Phase 5, Phase 6, Phase 7 (all services must exist to be deployed by the pipeline)
**Requirements**: CICD-01, CICD-02, CICD-03, CICD-04, SEC-04, INT-01, INT-02, INT-03, INT-04, DOC-01, DOC-02, DOC-03
**Success Criteria** (what must be TRUE):
  1. A push to main triggers the full pipeline (lint → scan → test → build → deploy) and deploys ai-service and frontend independently based on which changed
  2. A PR opened against main runs lint, test, and security scan but does NOT deploy — reviewable in the GitHub Actions tab
  3. All containers run as non-root with pinned base image digests; no container runs as root in production
  4. End-to-end smoke tests pass in CI: email → AI service → reply, chatbot → AI service → response, resume data → RAG ingestion → retrieval → generation
  5. The README tells the progression story (V1: REST API → V2: Email Bot → V3: Chatbot), and the ADR directory contains decision records for all major architecture choices
**Plans**: TBD

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 4. RAG Core Service | 5/5 | Scaffold-complete (live deploy deferred) | 2026-04-10 |
| 5. n8n Email Bot | 4/4 | Scaffold-complete (terraform apply + import deferred) | 2026-04-10 |
| 6. React Chatbot Frontend | 4/4 | Scaffold-complete (Cloud Run deploy + CORS swap deferred) | 2026-04-11 |
| 7. Differentiators + Testing | 4/4 | Complete (61 local + 25 CI-gated tests) | 2026-04-11 |
| 8. CI/CD + Final Hardening | 4/4 | Scaffold-complete (WIF provider + first CI run deferred) | 2026-04-11 |

---

## Coverage

**v2.0 requirements: 45 total across 8 categories**

| Requirement | Phase |
|-------------|-------|
| RAG-01 | Phase 4 |
| RAG-02 | Phase 4 |
| RAG-03 | Phase 4 |
| RAG-04 | Phase 4 |
| RAG-05 | Phase 7 |
| RAG-06 | Phase 7 |
| RAG-07 | Phase 7 |
| RAG-08 | Phase 4 |
| EMAIL-01 | Phase 5 |
| EMAIL-02 | Phase 5 |
| EMAIL-03 | Phase 5 |
| EMAIL-04 | Phase 5 |
| EMAIL-05 | Phase 5 |
| EMAIL-06 | Phase 5 |
| EMAIL-07 | Phase 5 |
| CHAT-01 | Phase 6 |
| CHAT-02 | Phase 6 |
| CHAT-03 | Phase 6 |
| CHAT-04 | Phase 4 |
| CHAT-05 | Phase 6 |
| CHAT-06 | Phase 6 |
| CHAT-07 | Phase 6 |
| CHAT-08 | Phase 6 |
| SEC-01 | Phase 4 |
| SEC-02 | Phase 4 |
| SEC-03 | Phase 4 |
| SEC-04 | Phase 8 |
| SEC-05 | Phase 4 |
| SEC-06 | Phase 4 |
| SEC-07 | Phase 4 |
| SEC-08 | Phase 4 |
| SEC-09 | Phase 4 |
| CICD-01 | Phase 8 |
| CICD-02 | Phase 8 |
| CICD-03 | Phase 8 |
| CICD-04 | Phase 8 |
| TEST-01 | Phase 7 |
| TEST-02 | Phase 7 |
| TEST-03 | Phase 7 |
| TEST-04 | Phase 7 |
| INT-01 | Phase 8 |
| INT-02 | Phase 8 |
| INT-03 | Phase 8 |
| INT-04 | Phase 8 |
| DOC-01 | Phase 8 |
| DOC-02 | Phase 8 |
| DOC-03 | Phase 8 |

**Mapped: 47/47 ✓**

---
*Roadmap created: 2026-04-08 for milestone v2.0*
*v1.0 phases (1–3) complete. v2.0 phases (4–8) active.*
