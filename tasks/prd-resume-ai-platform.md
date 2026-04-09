# PRD: Resume AI Platform

## Introduction

Evolve the existing Resume API from a basic REST endpoint into an AI-powered career knowledge platform. The platform adds two new capabilities on top of the working Phase 1 API: (1) an email bot that answers recruiter inquiries via Gmail using n8n workflow automation, and (2) a polished web chatbot where recruiters can interactively ask questions about the candidate's background.

The system uses a two-tier RAG architecture: resume experience as the factual ground truth (Tier 1), and pre-scrubbed "mock interview" Q&A as style/framing patterns (Tier 2). All resume data is anonymized using consulting-style descriptors — no real names, no company names, certifications and skills preserved.

This is a portfolio project demonstrating the progression from basic API → email bot → interactive chatbot, running entirely on GCP free tier ($0/month).

## Goals

- Deploy an AI service (FastAPI + Gemini 2.5 Flash + Chroma RAG) that answers resume and architecture questions grounded in anonymized candidate data
- Deploy an n8n email bot on a GCE e2-micro VM that automatically responds to recruiter emails via a dedicated Gmail address
- Deploy a polished, recruiter-facing chat UI on Cloud Run where visitors can ask questions about the candidate
- Implement comprehensive security: rate limiting, prompt injection detection + logging + rate reduction, container hardening, cost protection
- Maintain $0/month GCP free tier budget throughout
- Demonstrate engineering progression via README narrative + Architecture Decision Records (ADRs)
- Enable the bot to explain its own architecture at decision-level depth ("Why Chroma over Pinecone?", "Why separate services?")
- All resume data follows the anonymization guidelines (ANONYMIZATION_GUIDE.md) — auditable and enforced

## User Stories

### US-001: AI Service — RAG Engine Setup
**Description:** As a developer, I need a FastAPI service that ingests anonymized resume data into a Chroma vector database so that questions can be answered with grounded context.

**Acceptance Criteria:**
- [ ] FastAPI app with `POST /ai/ask` endpoint accepting `{"question": "string"}` and returning `{"answer": "string", "sources": ["string"]}`
- [ ] Resume data chunked and embedded using `all-MiniLM-L6-v2` (local, no API key)
- [ ] Chroma vector store with cosine similarity search
- [ ] Chunks tagged with metadata: `source: "resume"` or `source: "mock_interview"`
- [ ] Resume data follows ANONYMIZATION_GUIDE.md — no real names or company names
- [ ] Returns top-3 relevant chunks as context to Gemini
- [ ] Typecheck/lint passes

### US-002: AI Service — Gemini Integration
**Description:** As a developer, I need the AI service to call Gemini 2.5 Flash to generate answers grounded in retrieved resume context.

**Acceptance Criteria:**
- [ ] Uses `google-generativeai` SDK (free tier: 15 RPM, 1M tokens/day)
- [ ] System prompt instructs Gemini to ground answers in Tier 1 (resume) facts, use Tier 2 (mock interview) patterns for framing only
- [ ] Handles unanswerable questions with polite redirect ("I don't have that information")
- [ ] Logs unanswered questions to a file for future knowledge base improvement
- [ ] Salary/availability/sensitive questions redirected to direct contact
- [ ] Response time under 5 seconds for typical questions
- [ ] Typecheck/lint passes

### US-003: AI Service — Architecture Self-Awareness
**Description:** As a recruiter, I want to ask the bot "Why did you build it this way?" and get decision-level explanations so I can evaluate the candidate's engineering judgment.

**Acceptance Criteria:**
- [ ] Curated architecture FAQ document embedded in RAG alongside resume data
- [ ] Bot can explain: why separate services, why Chroma, why n8n, why GCP free tier, why anonymization approach
- [ ] README.md and ADR documents auto-ingested into the knowledge base
- [ ] Answers reference specific design tradeoffs, not just "because it's popular"
- [ ] Typecheck/lint passes

### US-004: AI Service — Two-Tier RAG Retrieval
**Description:** As a developer, I need the RAG system to weight resume experience higher than mock interview patterns so answers are always factually grounded.

**Acceptance Criteria:**
- [ ] Chroma metadata filtering: `source` field on every chunk
- [ ] Query retrieves top-3 resume chunks (Tier 1) + top-2 mock interview chunks (Tier 2)
- [ ] System prompt explicitly instructs: "Ground in resume facts. Use interview patterns for framing only. Never reference interview contexts."
- [ ] Mock interview documents labeled as "mock interviews" in all code and docs (no reference to real interviews)
- [ ] Typecheck/lint passes

### US-005: AI Service — Security Hardening
**Description:** As a developer, I need the AI service to be protected against abuse, prompt injection, and cost overruns.

**Acceptance Criteria:**
- [ ] IP-based rate limiting: 10 requests/minute for `/ai/ask`, 30 requests/minute for `/chat`
- [ ] Prompt injection detection: pattern matching for common injection phrases ("ignore your instructions", "system prompt", "pretend you are")
- [ ] Detected injections: logged to file, response deflected ("I can only answer questions about the candidate's resume"), IP rate limit temporarily reduced
- [ ] Input validation via Pydantic: max question length (500 chars), required fields
- [ ] Container runs as non-root user
- [ ] No secrets baked into Docker image — all via environment variables or Secret Manager
- [ ] CORS locked to specific origins (chatbot frontend URL)
- [ ] Error responses do not leak internal details (stack traces, file paths)
- [ ] Typecheck/lint passes

### US-006: AI Service — Containerization and Cloud Run Deployment
**Description:** As a developer, I need the AI service containerized and deployed to Cloud Run so it scales to zero and stays within free tier.

**Acceptance Criteria:**
- [ ] Dockerfile: Python 3.11-slim, multi-stage build, non-root user, pinned base image
- [ ] `.dockerignore` excludes `.env`, `*.key`, `.git`, `chroma_db/`, `__pycache__/`
- [ ] Cloud Run config: min instances 0, max instances 1, 512MB memory, 1 vCPU
- [ ] Health check endpoint: `GET /health`
- [ ] Environment variables: `GOOGLE_API_KEY`, `CHROMA_PERSIST_DIR`, `ALLOWED_ORIGINS`
- [ ] Startup: auto-ingests resume data if Chroma DB is empty
- [ ] Typecheck/lint passes

### US-007: Email Bot — n8n Workflow
**Description:** As a recruiter, I want to email a dedicated address with a question about the candidate and receive an AI-generated response so I can evaluate the candidate without scheduling a call.

**Acceptance Criteria:**
- [ ] n8n self-hosted on GCE e2-micro VM via Docker Compose
- [ ] Gmail Trigger node polls dedicated Gmail inbox (new address: to be created)
- [ ] Extracts email subject + body as the question
- [ ] Calls AI service `POST /ai/ask` with the extracted question
- [ ] Sends reply via Gmail Send node using EMAIL_SYSTEM_PROMPT formatting
- [ ] Error fallback: if AI service unreachable, sends "Thank you for your inquiry. I'll get back to you shortly."
- [ ] n8n workflow exported as JSON in `n8n/workflows/resume-email-bot.json` (version controlled)
- [ ] Best-effort response time (no SLA)

### US-008: Email Bot — n8n Infrastructure
**Description:** As a developer, I need the n8n instance running reliably on a GCE e2-micro VM with auto-restart.

**Acceptance Criteria:**
- [ ] Docker Compose: n8n container with SQLite persistence, port 5678
- [ ] systemd service for auto-start on VM boot
- [ ] Gmail OAuth2 credentials stored in GCP Secret Manager (not in code)
- [ ] n8n admin UI accessible only via SSH tunnel (not exposed to internet)
- [ ] Firewall rules: only port 22 (SSH) open, n8n port blocked from public
- [ ] VM uses the GCP always-free e2-micro tier
- [ ] Typecheck/lint passes (for any scripts)

### US-009: Chatbot Frontend — React Chat UI
**Description:** As a recruiter, I want to visit a web page and ask questions about the candidate in a chat interface so I can quickly evaluate their background.

**Acceptance Criteria:**
- [ ] React + Vite + TypeScript + Tailwind CSS
- [ ] Professional, polished design appropriate for recruiter audience
- [ ] Chat message bubbles (user on right, bot on left)
- [ ] Text input with send button, supports Enter key to send
- [ ] Typing indicator while waiting for AI response
- [ ] Header with candidate title (anonymized) and brief intro text
- [ ] Mobile responsive
- [ ] No suggested questions, no conversation export — Q&A only
- [ ] First bot message: auto-greeting introducing itself
- [ ] Verify in browser

### US-010: Chatbot Frontend — API Integration
**Description:** As a developer, I need the chatbot frontend to communicate with the AI service securely.

**Acceptance Criteria:**
- [ ] `POST /chat` endpoint on AI service — accepts `{"message": "string", "history": []}` and returns `{"reply": "string"}`
- [ ] Conversation history maintained in frontend state (not persisted server-side)
- [ ] History sent with each request for multi-turn context (last 10 messages)
- [ ] Error handling: network failures show "Connection issue — please try again" message
- [ ] Loading state prevents duplicate submissions
- [ ] Typecheck/lint passes

### US-011: Chatbot Frontend — Containerization and Deployment
**Description:** As a developer, I need the chatbot frontend containerized and deployed to Cloud Run.

**Acceptance Criteria:**
- [ ] Multi-stage Dockerfile: Node build stage → Nginx serve stage
- [ ] Nginx config serves static files + proxies `/api/*` to AI service
- [ ] Cloud Run deployment: min instances 0, max instances 1
- [ ] Cloud Run URL serves the chatbot (no custom domain required)
- [ ] HTTPS enforced (Cloud Run provides this by default)
- [ ] Typecheck/lint passes

### US-012: CI/CD — GitHub Actions Pipeline
**Description:** As a developer, I need automated CI/CD so that pushes to main auto-deploy to Cloud Run.

**Acceptance Criteria:**
- [ ] GitHub Actions workflow: lint (ruff) → security scan (bandit, pip-audit) → test (pytest) → build Docker → push to Artifact Registry → deploy to Cloud Run
- [ ] Separate jobs for ai-service and frontend (only rebuild what changed)
- [ ] GCP Workload Identity Federation for keyless auth (no service account key in GitHub)
- [ ] Deployment only triggers on push to `main`
- [ ] PR checks run lint + test + security scan without deploying
- [ ] Typecheck/lint passes

### US-013: Testing — Comprehensive Test Suite
**Description:** As a developer, I need automated tests covering unit, integration, and security scenarios.

**Acceptance Criteria:**
- [ ] Unit tests: RAG retrieval returns relevant chunks, prompt formatting, anonymization verification
- [ ] Integration tests: `/ai/ask` endpoint returns grounded answers, `/chat` endpoint handles conversation history
- [ ] Security tests: prompt injection attempts are detected and logged, rate limiting triggers at threshold, oversized inputs rejected
- [ ] Test fixtures with anonymized sample data (no real PII)
- [ ] pytest with coverage report (target: 80%+ on ai-service)
- [ ] All tests pass in CI pipeline

### US-014: Documentation — Progression Narrative and ADRs
**Description:** As an engineer reviewing this repo, I want to understand the project's evolution and design decisions so I can evaluate the candidate's engineering maturity.

**Acceptance Criteria:**
- [ ] README.md updated with progression narrative: "Version 1: REST API → Version 2: Email Bot → Version 3: Chatbot"
- [ ] ADR directory (`docs/adr/`) with decision records for: separate services vs monolith, Chroma vs Pinecone, n8n vs Cloud Functions, anonymization approach, two-tier RAG design, GCP free tier constraints
- [ ] ADRs follow standard format: Title, Status, Context, Decision, Consequences
- [ ] ADRs generated from conversation + dedicated architecture interview session
- [ ] Architecture diagram updated to reflect new services

### US-015: Data Ingestion — Mock Interview Q&A
**Description:** As a developer, I need a process to ingest pre-scrubbed mock interview documents into the RAG knowledge base.

**Acceptance Criteria:**
- [ ] `ai-service/ingest.py` script that reads markdown files from `ai-service/resume_corpus/`
- [ ] Supports two document types: `resume` (Tier 1) and `mock_interview` (Tier 2)
- [ ] Documents in `resume_corpus/` are pre-scrubbed by the candidate (no automated scrubbing of interview data)
- [ ] All ingested documents labeled as "mock interviews" — never reference real interview contexts
- [ ] Chunks tagged with `source` metadata for tiered retrieval
- [ ] Idempotent: re-running doesn't duplicate data
- [ ] `resume_corpus/` directory included in `.gitignore` if it contains any sensitive drafts
- [ ] A `resume_corpus/examples/` directory with anonymized sample documents is committed

## Functional Requirements

- FR-1: AI service exposes `POST /ai/ask` accepting a question string and returning a grounded answer with source references
- FR-2: AI service exposes `POST /chat` accepting a message + conversation history and returning a contextual reply
- FR-3: AI service exposes `GET /health` returning service status
- FR-4: RAG engine uses two-tier retrieval: Tier 1 (resume, always retrieved) and Tier 2 (mock interviews, supplementary)
- FR-5: All resume data in the codebase follows ANONYMIZATION_GUIDE.md — enforced via CI checks
- FR-6: Gemini 2.5 Flash generates all responses via `google-generativeai` SDK free tier
- FR-7: Unanswered questions are logged to a file with timestamp and question text
- FR-8: Prompt injection attempts are detected, logged, and trigger temporary rate limit reduction for the source IP
- FR-9: n8n email bot polls Gmail inbox, extracts questions, calls AI service, sends formatted reply
- FR-10: n8n admin UI is only accessible via SSH tunnel — not exposed publicly
- FR-11: Chatbot frontend sends conversation history (last 10 messages) with each request for multi-turn context
- FR-12: GitHub Actions CI/CD deploys ai-service and frontend to Cloud Run on push to main
- FR-13: All containers run as non-root users with pinned base images
- FR-14: Rate limiting enforced: 10 req/min on `/ai/ask`, 30 req/min on `/chat`
- FR-15: Error responses never leak internal details (stack traces, file paths, env vars)

## Non-Goals (Out of Scope)

- **Phase 2 data pipeline:** ETL, Locust traffic simulation, APScheduler — removed from this project, will be a separate portfolio project
- **Custom domain:** Chatbot lives at Cloud Run URL; no DNS setup
- **Suggested questions or conversation export** in the chatbot UI
- **Real-time streaming responses:** Gemini responses are returned as complete text, not streamed
- **User authentication:** The chatbot and email bot are public-facing with no login
- **Resume PDF download:** No downloadable resume from the chatbot
- **Contact form / interview scheduling:** The bot redirects to direct contact, doesn't collect recruiter info
- **Automated interview document scrubbing:** The candidate pre-scrubs all mock interview documents manually before ingestion
- **Production SLA:** Best-effort response times, no uptime guarantees
- **Analytics dashboard:** No BigQuery analytics pipeline (removed with Phase 2)
- **Multiple language support:** English only

## Design Considerations

- **Chatbot UI:** Polished, recruiter-facing. Professional color scheme, clean typography, message bubbles. Not a tech demo — this represents the candidate to hiring managers.
- **Anonymization:** Consulting-style descriptors throughout. "A Big Four consulting firm" not "Deloitte." All data files must pass the ANONYMIZATION_GUIDE.md audit checklist.
- **Progression narrative:** The README should tell a story: basic API → email bot → chatbot. Each evolution accompanied by an ADR explaining the decision.
- **Mobile responsive:** Recruiters may view on phones during commute.

## Technical Considerations

- **GCP Free Tier Constraints:**
  - Cloud Run: 2M requests/month, 360K vCPU-seconds, 180K GiB-seconds
  - GCE e2-micro: 1 instance in us-central1/us-east1/us-west1
  - Artifact Registry: 500MB storage
  - Gemini API: 15 RPM, 1M tokens/day via `google-generativeai` SDK
- **Embedding model:** `all-MiniLM-L6-v2` runs locally in the container (~100MB). No external API call needed.
- **Chroma persistence:** Stored on container filesystem. Cloud Run containers are ephemeral — Chroma re-ingests on cold start from bundled resume data files. This is acceptable given small corpus size (<1MB).
- **Memory budget:** Cloud Run container at 512MB must fit: Python runtime (~50MB) + FastAPI (~20MB) + sentence-transformers model (~100MB) + Chroma (~50MB) + overhead. Tight but feasible.
- **n8n on e2-micro:** 1GB RAM. n8n uses ~300MB. Leaves headroom for OS + Docker overhead. No AI processing on this VM — all RAG/Gemini calls go to Cloud Run.
- **GitHub Actions → Cloud Run:** Use Workload Identity Federation (no service account key stored in GitHub Secrets). Requires one-time GCP Console setup.
- **Existing Phase 1 API:** Left untouched. Separate service, separate deployment. Shared repo only.

## Success Metrics

- AI service answers resume questions with grounded, accurate responses (manual spot-check of 10 questions)
- Email bot responds to test emails within 5 minutes (best effort)
- Chatbot frontend loads in under 3 seconds on mobile
- Prompt injection attempts are detected and logged (test with 5 known injection patterns)
- Rate limiting triggers correctly at threshold (test with automated requests)
- All tests pass in CI with 80%+ coverage on ai-service
- Total GCP bill: $0.00/month
- A stranger visiting the repo can understand the project's progression from README alone

## Open Questions

1. **Gmail address:** What should the dedicated bot email address be? (e.g., `resume-bot-portfolio@gmail.com`)
2. **Mock interview documents:** When will the initial batch of pre-scrubbed documents be ready for ingestion?
3. **Architecture interview session:** When should we schedule the dedicated session to generate ADR content?
4. **Cloud Run cold start:** Embedding model loading may cause 10-15 second cold starts. Is this acceptable, or should we keep 1 minimum instance (costs ~$5/month)?
5. **n8n version:** Pin to a specific version or use `latest`? (Recommend pinning for reproducibility)
