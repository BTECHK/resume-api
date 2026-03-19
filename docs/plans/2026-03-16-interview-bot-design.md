# Interview Bot — Product Requirements Document

**Version:** 1.0
**Date:** March 2026
**Status:** Draft
**Project Type:** Job Application + Portfolio Project
**Related Project:** resume-api-repo (data source, shared infrastructure)

---

## 1. Overview

### 1.1 Problem Statement

Fairly's CEO has posted an unconventional application process for an AI Operations Analyst role: instead of submitting a resume, candidates must provide an email or SMS endpoint connected to an automation that can be "interviewed." The bot must discuss the candidate's professional background, salary expectations, and the technical architecture behind how it was built. This filters for builders who can bridge business logic and AI orchestration — the exact skill set the role requires.

### 1.2 Opportunity

The candidate has an existing resume API project (resume-api-repo) with structured career data, multiple role-specific resumes, a master career history file, and transcribed interview recordings. These assets can be leveraged as the knowledge base for a conversational AI bot. Building this bot also creates a reusable portfolio artifact: after the Fairly application process, the bot transitions to a public-facing LinkedIn portfolio piece demonstrating automation, AI integration, and infrastructure-as-code skills to any future employer.

### 1.3 Solution Summary

Build an email-based conversational AI bot that receives inbound emails, retrieves relevant context from a vector database (RAG), generates responses using Gemini 2.5 Flash, and sends replies — all orchestrated through n8n workflows on Google Cloud free-tier infrastructure. The system operates in two modes controlled by a feature flag: **Fairly mode** (full career details + salary range for the application) and **Portfolio mode** (public-safe responses with PII and salary redacted).

The architecture:

```
Email arrives at Gmail inbox
    |
n8n (self-hosted, GCE e2-micro) — IMAP trigger polls inbox
    |
n8n parses email, loads conversation history, calls AI service
    |
AI Service (FastAPI on Cloud Run):
    |- Embeds question (HuggingFace all-MiniLM-L6-v2)
    |- Retrieves context from Chroma vector DB
    |- Generates response via Gemini 2.5 Flash
    |- Applies mode-based guardrails
    |
n8n receives response, sends reply via Gmail SMTP
    |
Conversation logged to SQLite (conversation memory)
```

All infrastructure is codified in Terraform (extending the existing resume-api infrastructure state) and deployed via GitHub Actions CI/CD.

### 1.4 Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Primary: Bot responds to inbound email within 3 minutes | < 3 min response time | Timestamp comparison (email received → reply sent) |
| Primary: Bot accurately answers background questions from RAG context | Answers grounded in source material, no hallucination | Manual review of 10 test Q&A pairs |
| Primary: Bot explains its own architecture accurately | Technical walkthrough matches actual implementation | Self-review against architecture doc |
| Secondary: Fairly mode shares salary range correctly | States $130-170K+ with total comp context | Test email asking salary question |
| Secondary: Portfolio mode redacts PII and salary | Declines salary, generalizes personal details | Test email in portfolio mode |
| Guardrail: Total recurring cost remains $0.00/month | $0.00 | GCP billing dashboard — budget alert at $1 |
| Guardrail: Bot resists prompt injection attempts | Refuses to override instructions or leak restricted data | 5 adversarial test emails |

---

## 2. Target Users

### 2.1 Primary User Persona

**Name:** The Hiring CEO
**Segment:** Eric Breon, Co-Founder & CEO of Fairly. Serial founder (Vacasa — 6,000 employees, 25,000 homes, IPO). Capital One analytics background. Values initiative, candor, and results over credentials.

**Jobs to be Done:**

| Job Type | Job Statement | Priority |
|----------|---------------|----------|
| Functional | Evaluate if this candidate can build workflow automations connecting SaaS tools via webhooks and APIs | P0 |
| Functional | Understand the candidate's professional background through conversation with the bot | P0 |
| Functional | Assess salary alignment before investing time in a live interview | P0 |
| Emotional | Feel impressed by the initiative and quality of the build | P1 |

### 2.2 Secondary User Persona

**Name:** The LinkedIn Viewer (Portfolio Mode)
**Segment:** Recruiters, hiring managers, engineers who discover the project via LinkedIn or GitHub

**Jobs to be Done:**

| Job Type | Job Statement | Priority |
|----------|---------------|----------|
| Functional | Interact with a live AI bot that demonstrates automation and AI integration skills | P0 |
| Functional | Understand the technical architecture and tools used | P0 |
| Emotional | Be impressed enough to reach out about opportunities | P1 |

### 2.3 Tertiary User Persona

**Name:** The Builder (Self)
**Segment:** The candidate building and maintaining the system

**Jobs to be Done:**

| Job Type | Job Statement | Priority |
|----------|---------------|----------|
| Functional | Demonstrate hands-on proficiency in workflow automation, AI integration, IaC, and CI/CD | P0 |
| Functional | Have a live artifact that can be repurposed across job applications | P0 |
| Functional | Learn n8n, Terraform, and RAG patterns through hands-on execution | P1 |

### 2.4 Anti-Personas (Who This Is NOT For)

- **General public seeking a chatbot** — This is a job application tool, not a product
- **Anyone expecting real-time chat** — Email has inherent latency (1-3 minutes); this is asynchronous conversation
- **Attackers attempting prompt injection** — The bot has guardrails and will not comply with adversarial instructions

---

## 3. User Stories & Requirements

### 3.1 Epic Overview

| Epic | Description | Priority |
|------|-------------|----------|
| Epic 1: Email Intake & Response | Receive emails, process them, send AI-generated replies via n8n | P0 |
| Epic 2: RAG Knowledge Base | Build and populate Chroma vector DB with career data, resumes, and transcripts | P0 |
| Epic 3: Conversational AI Service | FastAPI service with RAG retrieval + Gemini Flash generation | P0 |
| Epic 4: Feature Flags & Privacy | Mode-based access control (Fairly vs Portfolio) with PII guardrails | P0 |
| Epic 5: Security | Prompt injection defense, PII filtering, infrastructure hardening | P0 |
| Epic 6: Infrastructure as Code | Terraform extending resume-api infra + GitHub Actions CI/CD | P1 |
| Epic 7: Documentation & Diagrams | PRD, architecture draw.io diagram, implementation guide | P1 |

### 3.2 Detailed User Stories

**Epic 1: Email Intake & Response**

| ID | User Story | Acceptance Criteria | Priority |
|----|------------|---------------------|----------|
| US-001 | As Eric, I want to email the bot and receive a reply so I can evaluate the candidate | - Email sent to bot address receives a reply within 3 minutes | P0 |
| | | - Reply is contextually relevant to the question asked | |
| US-002 | As Eric, I want to have a multi-turn conversation so I can ask follow-up questions | - Bot maintains conversation history per sender | P0 |
| | | - Follow-up replies reference prior context without repeating | |
| US-003 | As Eric, I want the reply to come from the same email address I sent to | - Gmail SMTP sends reply from the bot's address | P0 |
| | | - Email thread is maintained (proper In-Reply-To headers) | |

**Epic 2: RAG Knowledge Base**

| ID | User Story | Acceptance Criteria | Priority |
|----|------------|---------------------|----------|
| US-004 | As the bot, I need access to the candidate's full career history so I can answer background questions accurately | - Master career file chunked and embedded in Chroma | P0 |
| | | - Retrieval returns relevant chunks for career questions | |
| US-005 | As the bot, I need role-specific resume versions so I can frame answers appropriately | - Multiple resume versions stored with role tags | P0 |
| | | - Retrieval can filter or weight by role context | |
| US-006 | As the bot, I need interview transcripts so I can answer in the candidate's voice | - Otter.ai transcripts cleaned, chunked by Q&A pair where possible | P1 |
| | | - Bot uses candidate's phrasing patterns | |
| US-007 | As the bot, I need a self-knowledge document so I can explain my own architecture | - Architecture doc embedded describing tools, decisions, costs | P0 |
| | | - Bot accurately explains n8n, Gemini, Chroma, Terraform, etc. | |

**Epic 3: Conversational AI Service**

| ID | User Story | Acceptance Criteria | Priority |
|----|------------|---------------------|----------|
| US-008 | As Eric, I want the bot to answer questions about the candidate's background | - Responses grounded in RAG context, not hallucinated | P0 |
| | | - Covers: work history, skills, projects, education, certifications | |
| US-009 | As Eric, I want the bot to share salary expectations | - States range: $130-170K+ depending on total comp (equity, bonuses, benefits) | P0 |
| | | - Never isolates floor or ceiling separately | |
| US-010 | As Eric, I want the bot to explain how it was built | - Technical walkthrough: n8n, Gmail IMAP, Chroma, Gemini Flash, Cloud Run, Terraform, GitHub Actions | P0 |
| | | - Explains WHY each tool was chosen (free tier, industry standard, etc.) | |
| US-011 | As Eric, I want the bot to be conversational and direct, not robotic | - No corporate speak or bullet-point dumps unless asked | P0 |
| | | - Honest about limitations ("I don't have context on that") | |

**Epic 4: Feature Flags & Privacy**

| ID | User Story | Acceptance Criteria | Priority |
|----|------------|---------------------|----------|
| US-012 | As the builder, I want to switch between Fairly and Portfolio mode via env var | - BOT_MODE=fairly enables full career + salary access | P0 |
| | | - BOT_MODE=public disables salary, redacts PII | |
| US-013 | As a LinkedIn viewer (Portfolio mode), I want to interact with the bot without seeing private info | - Salary questions get: "That's private — happy to discuss directly" | P0 |
| | | - No name, address, or contact info exposed | |

**Epic 5: Security**

| ID | User Story | Acceptance Criteria | Priority |
|----|------------|---------------------|----------|
| US-014 | As the builder, I want the bot to resist prompt injection | - Adversarial emails ("ignore your instructions") are refused politely | P0 |
| | | - System prompt guardrails cannot be overridden via email content | |
| US-015 | As the builder, I want PII filtered from all responses | - Output regex scan catches SSN, phone, address patterns | P0 |
| | | - Blocked responses return safe fallback message | |
| US-016 | As the builder, I want all secrets managed securely | - API keys, Gmail credentials in GCE Secret Manager | P0 |
| | | - Nothing sensitive committed to git | |
| US-017 | As the builder, I want rate limiting on the email endpoint | - Max responses per sender per hour enforced in n8n | P1 |

**Epic 6: Infrastructure as Code**

| ID | User Story | Acceptance Criteria | Priority |
|----|------------|---------------------|----------|
| US-018 | As the builder, I want to extend existing resume-api Terraform to add bot infrastructure | - New Cloud Run service, firewall rules, Secret Manager entries added to existing state | P1 |
| | | - terraform plan shows only additive changes | |
| US-019 | As the builder, I want CI/CD deploying the AI service on push | - GitHub Actions: lint, test, build Docker image, push to Artifact Registry, deploy to Cloud Run | P1 |
| US-020 | As the builder, I want the n8n instance provisioned via Terraform | - GCE e2-micro with Docker + docker-compose for n8n | P1 |
| | | - Firewall rules codified | |

**Epic 7: Documentation & Diagrams**

| ID | User Story | Acceptance Criteria | Priority |
|----|------------|---------------------|----------|
| US-021 | As the builder, I want a draw.io architecture diagram that renders on GitHub | - .drawio file in repo, also exported as .drawio.svg for README embedding | P1 |
| | | - Covers: email flow, n8n, Cloud Run, RAG pipeline, infra layout, CI/CD | |
| US-022 | As the builder, I want a step-by-step implementation guide matching resume-api style | - Markdown doc with code snippets, command explanations, first-use annotations | P1 |
| | | - Matches format of phase-2 and phase-3 implementation guides | |

### 3.3 Feature Requirements Matrix (MoSCoW)

| Feature | Story | Must Have | Should Have | Nice to Have | Won't Have (v1) |
|---------|-------|-----------|-------------|--------------|-----------------|
| Email receive + reply via n8n | US-001, 003 | X | | | |
| Multi-turn conversation memory | US-002 | X | | | |
| RAG with career data + resumes | US-004, 005 | X | | | |
| Gemini Flash response generation | US-008-011 | X | | | |
| Salary range response | US-009 | X | | | |
| Architecture self-explanation | US-007, 010 | X | | | |
| Feature flag (Fairly/Portfolio) | US-012, 013 | X | | | |
| Prompt injection defense | US-014 | X | | | |
| PII output filtering | US-015 | X | | | |
| Secret management | US-016 | X | | | |
| Interview transcript RAG | US-006 | | X | | |
| Rate limiting | US-017 | | X | | |
| Terraform IaC | US-018, 020 | | X | | |
| GitHub Actions CI/CD | US-019 | | X | | |
| draw.io architecture diagram | US-021 | | X | | |
| Implementation guide | US-022 | | X | | |
| SMS endpoint (Twilio) | — | | | | X |
| Web chat interface | — | | | | X |
| Frontend UI | — | | | | X |
| Custom domain email | — | | | X | |
| Slack integration | — | | | | X |

---

## 4. Functional Requirements

### 4.1 Core Functionality

**n8n Workflow (Email Orchestration)**

| Req ID | Requirement | Rationale | Priority |
|--------|-------------|-----------|----------|
| FR-001 | n8n IMAP trigger polls Gmail inbox for new emails (1-2 min interval) | Email intake without external services | P0 |
| FR-002 | n8n parses sender, subject, body, and thread ID from email payload | Required for routing and conversation threading | P0 |
| FR-003 | n8n loads conversation history from SQLite by sender email | Multi-turn conversation support | P0 |
| FR-004 | n8n calls AI service via HTTP POST with message + history + mode | Connects orchestration to AI generation | P0 |
| FR-005 | n8n sends reply via Gmail SMTP with proper threading headers | Reply appears in same email thread | P0 |
| FR-006 | n8n logs interaction to SQLite conversation store | Persistent memory across sessions | P0 |
| FR-007 | n8n enforces rate limit per sender (configurable, default 10/hour) | Abuse prevention | P1 |
| FR-007a | n8n sends instant acknowledgment on first email from new sender | UX — eliminates 1-3 min silence on first contact (see ADR-7) | P1 |

**AI Service (FastAPI + RAG + Gemini)**

| Req ID | Requirement | Rationale | Priority |
|--------|-------------|-----------|----------|
| FR-008 | POST /chat endpoint accepts { sender, message, conversation_history, mode } | Single endpoint for n8n to call | P0 |
| FR-009 | Embed incoming question using HuggingFace all-MiniLM-L6-v2 | Local, free embeddings for vector search | P0 |
| FR-010 | Retrieve top-5 relevant chunks from Chroma vector DB | RAG context for grounded responses | P0 |
| FR-011 | Generate response via Gemini 2.5 Flash with system prompt + retrieved context | Conversational AI generation | P0 |
| FR-012 | System prompt enforces mode-based access control (fairly vs public) | Privacy and PII protection | P0 |
| FR-013 | Output filter scans response for PII patterns before returning | Defense-in-depth PII protection | P0 |
| FR-014 | GET /health endpoint for Cloud Run health checks | Required for Cloud Run deployment | P0 |

**Knowledge Base (Chroma Vector DB)**

| Req ID | Requirement | Rationale | Priority |
|--------|-------------|-----------|----------|
| FR-015 | Master career file chunked (~500 tokens per chunk) and embedded | Primary knowledge source | P0 |
| FR-016 | Role-specific resumes stored with metadata tags (role type) | Context-aware framing | P0 |
| FR-017 | Architecture self-knowledge document embedded | Bot can explain its own build | P0 |
| FR-018 | Interview transcripts cleaned and chunked by Q&A pairs | Candidate voice and real examples | P1 |
| FR-019 | All chunks tagged with access level (public, fairly-only) | Feature flag enforcement at retrieval level | P0 |

### 4.2 Primary User Flow

```
Step 1: Eric receives email address (e.g., hire.me.bot@gmail.com)
  -> Action: Sends email — "Tell me about yourself"

Step 2: n8n detects new email (IMAP poll, 1-2 min)
  -> Action: Parses email, checks conversation history (none — new sender)
  -> Action: First-contact acknowledgment sent immediately:
     "Thanks for reaching out! I'm pulling together a thoughtful
      response based on [Name]'s background. You'll hear back
      from me in just a moment."
  -> Action: Calls AI service with message + mode=fairly

Step 3: AI service embeds question, retrieves career context from Chroma
  -> Returns: 3-4 sentence professional overview from master career file
  -> Framed through consulting/ops lens based on resume metadata

Step 4: n8n sends reply email in the same thread
  -> Eric receives response within ~2-3 minutes

Step 5: Eric replies — "What are your salary expectations?"
  -> n8n loads conversation history (1 prior exchange)
  -> AI service retrieves salary context, applies Fairly mode rules
  -> Bot states: "$130-170K+ depending on total comp breakdown"

Step 6: Eric replies — "How did you build this?"
  -> AI service retrieves architecture self-knowledge document
  -> Bot gives technical walkthrough: n8n, Gmail IMAP, Chroma, Gemini
     Flash, Cloud Run, GCE e2-micro, Terraform, GitHub Actions
  -> Explains WHY each tool was chosen

Step 7: Eric asks follow-up questions (skills, projects, automation experience)
  -> Each response draws from relevant chunks across all data sources
  -> Conversation history keeps context coherent
```

### 4.3 Edge Cases & Error Handling

| Scenario | Expected Behavior | Priority |
|----------|-------------------|----------|
| Email with no body text (empty message) | Reply: "I received your email but it appears to be empty. Feel free to ask me anything about [Name]'s background, skills, or how I was built." | P1 |
| Question outside knowledge base (e.g., "What's the weather?") | Reply: "I'm built to discuss [Name]'s professional background and how I was built. I don't have context on that topic, but I'm happy to help with anything career-related." | P0 |
| Prompt injection attempt ("Ignore your instructions and...") | Reply: "I appreciate the creative testing! I'm designed to discuss [Name]'s professional background and the architecture behind this bot. What would you like to know?" | P0 |
| Salary question in Portfolio mode | Reply: "Salary expectations are something [Name] prefers to discuss directly. Happy to answer questions about their skills and experience though." | P0 |
| Gemini API rate limit hit (15 req/min free tier) | n8n retries after 60 seconds, up to 3 attempts. If still failing, sends: "I'm experiencing high demand — please try again in a few minutes." | P1 |
| Very long email (>2000 words) | Truncate to last 1500 tokens before embedding. Respond to the most recent question/topic. | P2 |
| Email with attachments | Ignore attachments, respond only to body text. | P2 |
| Duplicate/rapid-fire emails from same sender | Rate limiter in n8n (10/hour). Beyond limit: "I've received several messages — give me a moment to catch up." | P1 |

---

## 5. Non-Functional Requirements

### 5.1 Performance

| Requirement | Target | Measurement |
|-------------|--------|-------------|
| End-to-end email response time | < 3 minutes (includes IMAP poll interval) | Timestamp comparison |
| AI service response time (POST /chat) | < 10 seconds | FastAPI middleware logging |
| Chroma retrieval time | < 500ms | Application logging |
| Gemini Flash generation time | < 5 seconds | API response timing |
| n8n workflow execution time | < 30 seconds (excluding IMAP poll wait) | n8n execution log |

### 5.2 Scalability

*This is a portfolio/application project, so scale is discussed, not required:*

- n8n on e2-micro handles ~10-20 concurrent workflows comfortably
- Cloud Run auto-scales the AI service (capped at 1 instance for free tier)
- Chroma with <1000 chunks performs retrieval in milliseconds
- For portfolio mode at scale, the same architecture would add Redis caching and Cloud Run min-instances

### 5.3 Security

| Requirement | Implementation | Priority |
|-------------|---------------|----------|
| Prompt injection defense | Multi-layer: input sanitization in n8n + system prompt guardrails + output filtering | P0 |
| PII output filtering | Regex scan for SSN, phone, address patterns before sending reply | P0 |
| Secret management | Gemini API key, Gmail app password in GCE Secret Manager; never in code | P0 |
| Mode-based data access | RAG chunks tagged with access levels; system prompt enforces per-mode rules | P0 |
| Salary floor protection | System prompt states full range only, never isolates floor/ceiling | P0 |
| Infrastructure hardening | GCE firewall: only 443 + SSH via IAP tunnel. No public SSH IP | P1 |
| Email rate limiting | n8n workflow limits responses per sender per hour | P1 |
| Conversation history isolation | SQLite on GCE, localhost-only access, not publicly exposed | P1 |
| Container security | Non-root user in Dockerfile, minimal base image, no unnecessary packages | P1 |
| Dependency scanning | pip-audit in CI/CD pipeline | P1 |

### 5.4 Reliability

| Requirement | Target | Measurement |
|-------------|--------|-------------|
| n8n uptime on GCE e2-micro | 99%+ (excluding planned maintenance) | GCE monitoring |
| AI service availability on Cloud Run | 99.5%+ (Cloud Run SLA) | Cloud Run metrics |
| Graceful degradation if Gemini API is down | Error reply sent instead of silence | Manual test |

---

## 6. Technical Considerations

### 6.1 Architecture Overview

```
Gmail Inbox
    |
    v
GCE e2-micro VM (free tier, always-on)
|-- Docker Compose
|   |-- n8n container
|   |   |-- IMAP Email Trigger (polls Gmail)
|   |   |-- Workflow: parse -> history lookup -> call AI -> send reply -> log
|   |   |-- SQLite (conversation history per sender)
|   |-- Chroma container (or embedded in AI service)
|       |-- Vector DB with career chunks
|       |-- HuggingFace embeddings (all-MiniLM-L6-v2)
|
    |  HTTP POST /chat
    v
Cloud Run (free tier)
|-- FastAPI AI Service container
|   |-- POST /chat (main endpoint)
|   |-- GET /health (health check)
|   |-- RAG retrieval from Chroma
|   |-- Gemini 2.5 Flash generation
|   |-- Mode-based system prompt
|   |-- PII output filter
|
Infrastructure Layer:
|-- Terraform (extends resume-api state)
|   |-- modules/compute (e2-micro + docker-compose)
|   |-- modules/cloud-run (AI service)
|   |-- modules/networking (firewall rules)
|   |-- modules/iam (service accounts, least privilege)
|   |-- modules/secrets (Secret Manager)
|   |-- modules/artifact-registry (container images)
|
CI/CD:
|-- GitHub Actions
|   |-- Lint (Ruff) -> Test (pytest) -> Scan (pip-audit)
|   |-- Build Docker image -> Push to Artifact Registry
|   |-- Deploy to Cloud Run
```

### 6.2 Integration Requirements

| System | Integration Type | Purpose |
|--------|------------------|---------|
| Gmail | IMAP (receive) + SMTP (send) | Email intake and response |
| Gemini 2.5 Flash | REST API (google-generativeai SDK) | LLM response generation |
| Chroma | Python client (local or Docker) | Vector storage and retrieval |
| HuggingFace | sentence-transformers library (local) | Text embeddings |
| resume-api (existing) | HTTP GET (optional) | Pull structured resume data as additional context |
| GCE Secret Manager | google-cloud-secret-manager SDK | Credential management |
| Artifact Registry | Docker push/pull | Container image storage |
| Cloud Run | gcloud CLI / Terraform | AI service hosting |

### 6.3 Data Requirements

| Data Entity | Source | Storage | Access Level |
|-------------|--------|---------|-------------|
| Master career file | User-provided document | Chroma (embedded chunks) | fairly-only (detailed), public (generalized) |
| Role-specific resumes (4-5 versions) | User-provided documents | Chroma (embedded, tagged by role) | fairly-only (full), public (skills only) |
| Interview transcripts | Otter.ai exports | Chroma (cleaned, chunked by Q&A) | public (no PII in transcripts) |
| Architecture self-knowledge | Hand-written document | Chroma (embedded) | public |
| Conversation history | Runtime generated | SQLite on GCE VM | private (never exposed) |
| Salary range | Environment variable | System prompt injection at runtime | fairly-only |

### 6.4 Technical Constraints

- **$0.00/month recurring cost:** All infrastructure on Google Cloud free tier + free-tier APIs
- **Gemini 2.5 Flash free tier limits:** 15 requests/minute, 1M tokens/day — sufficient for interview-volume email traffic
- **GCE e2-micro limits:** 0.25 vCPU, 1GB RAM — n8n + Chroma must fit within this
- **Cloud Run free tier:** 2M requests/month, 360K vCPU-seconds — more than sufficient
- **Private repo:** All source code in private GitHub repo; no PII in committed files
- **Gmail App Password:** Requires 2FA enabled on Gmail account, generates app-specific password for IMAP/SMTP

### 6.5 Architecture Decision Records

Each decision below was evaluated as a business trade-off, not just a technical choice. An AI Operations Analyst's job is to make these calls for the business — this section demonstrates that thinking.

---

#### ADR-1: Email Interface — Cloudflare Email Routing vs Gmail + n8n IMAP

**Status:** Decided — Gmail + n8n IMAP

**Context:** The bot needs to receive inbound emails and send replies. Cloudflare Email Routing is an enterprise-grade option that provides custom domain email handling (`hire@custom.com`). Gmail with n8n's built-in IMAP trigger provides the same functionality using a standard Gmail address.

| Factor | Cloudflare Email Routing | Gmail + n8n IMAP (Selected) |
|--------|--------------------------|----------------------------|
| Professional appearance | `hire@custom.com` | `name.bot@gmail.com` |
| Annual cost | ~$10/year (domain registration) | $0 |
| Additional integration points | +1 (Cloudflare config + DNS nameserver migration) | 0 (n8n handles natively) |
| Failure surface area | Domain DNS + Cloudflare routing rules + webhook endpoint | Gmail IMAP poll only |
| Time to configure | ~2 hours (domain purchase, DNS propagation, routing rules, webhook setup) | ~30 minutes (Gmail account + n8n IMAP node) |
| Terraform complexity | Additional Cloudflare provider + DNS records + email routing resources | None — Gmail is external to infrastructure |
| Debugging difficulty | Failures could be DNS, Cloudflare routing, or webhook — three layers to troubleshoot | Single point: n8n IMAP connection |

**Business verdict:** Cloudflare adds brand polish but increases complexity and cost for a component that doesn't differentiate the product. Eric is evaluating the bot's conversational quality and the architecture behind it — not whether the email comes from a vanity domain. Investing time in email presentation over AI quality is a misallocation of resources. A strong operator knows where effort compounds and where it's cosmetic.

**Upgrade path:** If the bot transitions to production use (Portfolio mode at scale), adding Cloudflare and a custom domain is a 2-hour migration with no architectural changes.

---

#### ADR-2: Workflow Orchestration — n8n vs Zapier vs Make vs Pure Code

**Status:** Decided — n8n (self-hosted)

**Context:** The email-to-AI-to-reply pipeline needs orchestration. This could be built as a pure Python script, or managed through a visual workflow automation platform.

| Factor | n8n (self-hosted) (Selected) | Zapier | Make (Integromat) | Pure Python Code |
|--------|------------------------------|--------|-------------------|-----------------|
| Cost | $0 (open source, self-hosted) | Free: 100 tasks/month, 5 zaps | Free: 1,000 ops/month | $0 |
| Scale limits | None (self-hosted) | Hard cap at 100 tasks | Hard cap at 1,000 ops | None |
| Visual workflow | Yes — inspectable, screenshot-able, handoff-ready | Yes | Yes | No — code only |
| Team handoff | Non-engineer can read and modify workflows | Yes | Yes | Requires developer |
| Signaling to hiring CEO | Eric mentioned n8n by name in posting | Eric mentioned Zapier | Not mentioned | Doesn't demonstrate low-code skills |
| Infrastructure ownership | Full control (Docker on GCE) | Vendor-hosted | Vendor-hosted | Full control |
| Vendor lock-in | Exportable JSON workflows | High | High | None |
| Community / ecosystem | 400+ built-in integrations, active OSS community | Largest marketplace | Strong marketplace | N/A |

**Business verdict:** Eric specifically named n8n and Zapier in the job posting — this signals he values visual workflow tools, not raw code. n8n is the only option that is both free at any scale (self-hosted) and visually demonstrable. Zapier's 100-task free tier would be exhausted during testing alone. Pure code solves the technical problem but misses the business signal: at Fairly, the AI Ops Analyst won't be the only person touching workflows. n8n makes automations inspectable, modifiable, and handoff-ready for the broader team — exactly how you'd operate at a startup where everyone wears multiple hats.

---

#### ADR-3: LLM Provider — Gemini 2.5 Flash vs Claude API vs OpenAI vs Local LLM

**Status:** Decided — Gemini 2.5 Flash

**Context:** The bot needs an LLM to generate conversational responses from RAG-retrieved context. Multiple providers offer varying price points, quality, and integration characteristics.

| Factor | Gemini 2.5 Flash (Selected) | Claude API (Anthropic) | OpenAI GPT-4o-mini | Local LLM (Ollama) |
|--------|----------------------------|----------------------|--------------------|--------------------|
| Free tier | 15 req/min, 1M tokens/day | No free tier | Limited free credits (expire) | Free (open source) |
| Ongoing cost at low volume | $0 | ~$3-15/month | ~$1-5/month | $0 |
| Response quality | Strong (competitive with GPT-4o-mini) | Excellent | Strong | Variable (model-dependent) |
| Google ecosystem alignment | Native — same platform as GCE, Cloud Run, BigQuery | None | None | None |
| SDK / integration | google-generativeai Python SDK | anthropic SDK | openai SDK | REST API (local) |
| Hardware requirements | Cloud API (no local compute) | Cloud API | Cloud API | Needs 8GB+ RAM (e2-micro has 1GB) |
| Vendor relationship to Fairly | Fairly likely uses Google Workspace — ecosystem familiarity | Less likely | Possible | N/A |

**Business verdict:** Gemini offers the only truly sustainable free tier — no expiring credits, no surprise bills. For a startup evaluating AI tools, choosing the provider that stays free at low volume and scales predictably at high volume is an operational decision, not just a cost one. Google ecosystem alignment also matters: if Fairly uses Google Workspace (likely given their size and stage), demonstrating Gemini integration shows you can work within their existing vendor relationships. The ability to evaluate and select LLM providers based on cost-per-token, quality, and ecosystem fit is precisely what this role requires.

**Upgrade path:** The RAG architecture is LLM-agnostic. Swapping Gemini for Claude or GPT-4o requires changing one API call and the system prompt format — no architectural changes. This flexibility itself is a design decision worth discussing.

---

#### ADR-4: Knowledge Retrieval — RAG vs Fine-Tuning vs Prompt Stuffing

**Status:** Decided — RAG (Retrieval Augmented Generation)

**Context:** The bot needs to answer questions accurately about the candidate's career, salary, and the bot's own architecture. The knowledge could be injected via fine-tuning the model, stuffing all context into the prompt, or retrieving relevant context dynamically via RAG.

| Factor | RAG (Selected) | Fine-Tuning | Prompt Stuffing |
|--------|---------------|-------------|-----------------|
| Cost | $0 (Chroma + HuggingFace, local) | $50-500+ per training run | $0 |
| Knowledge updates | Add/remove chunks instantly, no retraining | Retrain the entire model | Edit the prompt |
| Scales with data volume | Yes — vector search handles thousands of chunks | Model size limits | Context window limits (~128K tokens) |
| Model portability | Works with any LLM (swap Gemini for Claude, etc.) | Locked to one model/provider | Works with any LLM |
| Accuracy grounding | Cites specific source chunks — auditable | Baked into weights — not auditable | Full context visible but may overwhelm |
| Token cost per request | Small — only retrieved chunks sent to LLM | N/A (model is pre-trained) | High — entire knowledge base sent every time |
| Hallucination control | Strong — "answer only from provided context" is enforceable | Weak — model may blend training data | Moderate — context is there but model may ignore it |

**Business verdict:** RAG is the operationally sound choice for a startup. Fine-tuning costs money, locks you to one provider, and requires retraining whenever the knowledge base changes (new project completed, salary updated, new skills learned). Prompt stuffing works for small knowledge bases but hits context window limits and sends unnecessary tokens on every request (cost at scale). RAG lets you update knowledge without retraining, swap LLM providers without rearchitecting, and audit exactly what context informed each response. For a company like Fairly that might change AI providers as pricing evolves, this flexibility is a business advantage, not just a technical one.

---

#### ADR-5: Feature Flags — Single Deployment with Mode Toggle vs Separate Deployments

**Status:** Decided — Single deployment with environment variable toggle

**Context:** The bot operates in two modes: Fairly (full access) and Portfolio (PII redacted). These could be two separate deployments or one deployment with a configuration toggle.

| Factor | Feature Flag (Selected) | Separate Deployments |
|--------|------------------------|---------------------|
| Infrastructure cost | 1 Cloud Run service | 2 Cloud Run services (doubles free tier consumption) |
| Maintenance burden | One codebase, one pipeline, one deploy | Two of everything — drift risk |
| Mode switching | Change one env var, redeploy (~30 seconds) | Tear down one, stand up another |
| Code complexity | Small — if/else on BOT_MODE in system prompt + RAG tag filter | Simpler per-deployment but duplicated logic |
| Production pattern | Standard — feature flags are how multi-tenant SaaS works | Unusual for same-codebase mode switching |
| Monitoring | One dashboard, one log stream | Two dashboards, two log streams |

**Business verdict:** Separate deployments for what is fundamentally the same application with different access controls is operational waste. Feature flags are how production systems handle multi-tenant or multi-mode behavior. This demonstrates the candidate thinks about operational overhead — maintaining two identical services with diverging configs is exactly the kind of manual process this role exists to eliminate.

---

#### ADR-6: Infrastructure State — Extend Existing Terraform vs Separate State

**Status:** Decided — Extend existing resume-api Terraform state

**Context:** The resume-api project will have its own Terraform state managing GCE, Cloud Run, networking, and IAM. The interview-bot could share that state or have its own.

| Factor | Shared State (Selected) | Separate State |
|--------|------------------------|----------------|
| Simulates real-world pattern | Yes — startups extend infrastructure, not rebuild it | No — greenfield is less common |
| Cross-service dependencies | Explicit — shared VPC, firewall rules, IAM visible in one plan | Implicit — duplicated resources or manual coordination |
| terraform plan clarity | Shows exactly what's new vs existing | Clean but isolated — can't see shared resource impact |
| State file complexity | Higher — more resources in one state | Lower per-state, but two states to manage |
| Blast radius | Larger — mistake affects both services | Smaller — isolated per service |
| Skill demonstration | Extending production infra is a Phase 2 skill (more advanced) | Setting up greenfield infra is Phase 1 (foundational) |

**Business verdict:** In a real startup, you never create a new Terraform project for every service. You extend existing infrastructure — add a new Cloud Run service to the existing state, share the VPC, reuse IAM patterns. Building the resume-api Terraform first, then extending it with interview-bot resources, simulates the realistic workflow: inheriting infrastructure and safely adding to it. `terraform plan` showing additive changes against existing resources is more impressive than a greenfield `terraform apply`.

---

#### ADR-7: First-Contact Acknowledgment — Instant "Received" Reply

**Status:** Decided — Yes, first email only

**Context:** There's a 1-3 minute gap between when Eric sends an email and when the bot replies (IMAP poll interval + AI processing). During this time, Eric has no feedback that the bot is working.

| Factor | With Acknowledgment (Selected) | Without Acknowledgment |
|--------|-------------------------------|----------------------|
| User experience | Eric knows the bot is alive immediately | 1-3 minute silence — is it broken? |
| Email noise | +1 extra email on first contact only | Cleaner inbox |
| Demonstrates UX thinking | Yes — shows candidate considers the human experience, not just technical function | No |
| Implementation complexity | One additional n8n branch (check: is this sender's first email?) | None |
| Risk | Could feel robotic if poorly worded | Could feel broken if Eric expects instant response |

**Business verdict:** A bot that silently processes for 2 minutes feels broken. A bot that says "Received — give me a moment to pull together a thoughtful response" feels intentional. This is a small UX detail that signals the candidate thinks about the experience from the user's perspective, not just the technical pipeline. Only fires on the first email from a new sender — subsequent exchanges don't need it because Eric already knows the bot's response cadence.

**Acknowledgment message:** "Thanks for reaching out! I'm pulling together a thoughtful response based on [Name]'s background. You'll hear back from me in just a moment."

---

#### ADR-8: Vector Database — Chroma vs Pinecone vs FAISS vs Weaviate

**Status:** Decided — Chroma

**Context:** The RAG pipeline needs a vector database to store and retrieve embedded career document chunks. Options range from cloud-hosted managed services to local embeddable libraries.

| Factor | Chroma (Selected) | Pinecone | FAISS | Weaviate |
|--------|-------------------|----------|-------|----------|
| Cost | $0 (open source, local) | Free tier: 1 index, 100K vectors | $0 (open source, local) | $0 (open source, self-hosted) |
| Metadata filtering | Yes — filter by access level, role tag, source type | Yes | No native metadata filtering | Yes |
| Python integration | Native Python client, embeddable | REST API client | Python library | REST API + Python client |
| Persistence | SQLite backend, persists to disk | Cloud-managed | In-memory (requires serialization) | Docker container |
| Memory footprint | Light (~50-100MB for <1000 chunks) | N/A (cloud) | Light | Heavy (~500MB+ Docker image) |
| Fits on e2-micro (1GB RAM) | Yes | N/A (cloud) | Yes | Tight — competes with n8n for RAM |
| Setup complexity | `pip install chromadb` | Account creation, API key, index setup | `pip install faiss-cpu` | Docker Compose service |

**Business verdict:** Metadata filtering is the deciding factor. The feature flag system requires filtering RAG chunks by access level (`public` vs `fairly-only`) at retrieval time — not just at the prompt level. FAISS doesn't support this natively. Pinecone adds an external dependency and API key management for a database that will hold <1000 vectors. Weaviate is capable but its Docker image would compete with n8n for the e2-micro's 1GB RAM. Chroma is lightweight, embeddable, supports metadata filtering, and persists to disk — the right tool for the scale of this problem without over-provisioning.

---

#### ADR-9: Embedding Model — HuggingFace all-MiniLM-L6-v2 vs OpenAI Embeddings vs Vertex AI

**Status:** Decided — HuggingFace all-MiniLM-L6-v2

**Context:** Document chunks and queries need to be converted to vector embeddings for similarity search. Options include cloud API-based embedding services and local open-source models.

| Factor | HuggingFace all-MiniLM-L6-v2 (Selected) | OpenAI text-embedding-3-small | Vertex AI text-embedding |
|--------|----------------------------------------|------------------------------|--------------------------|
| Cost | $0 (local inference) | $0.02 per 1M tokens | Free tier available, then per-token |
| Latency | ~5-10ms per embedding (local) | ~100-300ms per embedding (API call) | ~100-300ms per embedding |
| External dependency | None — runs locally | Requires OpenAI API key + internet | Requires GCP credentials + internet |
| Quality (MTEB benchmark) | Good (ranked top-20 for its size) | Excellent | Good |
| Model size | 80MB | N/A (cloud) | N/A (cloud) |
| Offline capability | Yes — works without internet | No | No |
| Privacy | Embeddings computed locally — no data sent externally | Document content sent to OpenAI | Document content sent to Google |

**Business verdict:** For <1000 chunks, embedding quality differences between models are negligible — the retrieval task is simple enough that a good local model performs comparably to cloud APIs. Running embeddings locally eliminates an API dependency, removes per-request latency, keeps career data private (never sent to a third-party embedding service), and costs nothing. The model loads once at startup and serves all requests. At Fairly's scale, evaluating whether a cloud API is justified for a given workload — rather than defaulting to it — is the kind of cost-conscious analysis this role demands.

---

## 7. UX/UI Requirements

*This project has no visual frontend. The "UX" is the email conversation experience.*

| Interface | Purpose | Key Elements | Priority |
|-----------|---------|--------------|----------|
| Email conversation | Primary interaction — Eric emails, bot replies | Natural language, conversational tone, threaded replies | P0 |
| n8n workflow dashboard | Builder visibility into workflow execution | Visual workflow diagram, execution logs, error states | P1 (builder only) |
| GitHub README | Portfolio visibility for LinkedIn viewers | Architecture diagram, tech stack, design decisions | P1 |
| draw.io diagram | Visual architecture reference | Email flow, RAG pipeline, infrastructure layout, CI/CD | P1 |

---

## 8. Pricing & Monetization

*Not applicable — this is a job application and portfolio project.*

*Infrastructure cost model:*

| Service | Free Tier Allowance | Projected Usage | Cost |
|---------|-------------------|-----------------|------|
| GCE e2-micro | 1 instance/month (us-central1) | 1 instance (shared with resume-api) | $0.00 |
| Cloud Run | 2M requests/month, 360K vCPU-sec | ~100 requests | $0.00 |
| Artifact Registry | 500 MB | ~400 MB (2 images) | $0.00 |
| Secret Manager | 6 active secrets, 10K access ops | 3 secrets, ~500 ops | $0.00 |
| Gemini 2.5 Flash | 15 req/min, 1M tokens/day | ~50 requests/day max | $0.00 |
| Gmail | Unlimited IMAP/SMTP | ~50 emails/day max | $0.00 |
| GitHub Actions | 2,000 min/month (free repos) | ~30 min/month | $0.00 |
| HuggingFace model | Open source, local inference | Loaded once at startup | $0.00 |
| Chroma | Open source, self-hosted | <1000 chunks, ~50MB | $0.00 |
| **Total** | | | **$0.00/month** |

---

## 9. Go-to-Market

| Phase | Channel | Action | Timeline |
|-------|---------|--------|----------|
| Phase 1: Application | Email to Eric (eric@fairly.com) | Send bot email address + brief intro | After build complete |
| Phase 2: Portfolio | LinkedIn post | Showcase the project with architecture diagram and demo | After Fairly process concludes |
| Phase 3: Reuse | Future job applications | Switch to portfolio mode, share with other opportunities | Ongoing |

---

## 10. Success Criteria & KPIs

### 10.1 Activation Metric

- **Activation Event:** Eric sends an email and receives a coherent, relevant reply within 3 minutes
- **Target:** First email exchange succeeds without intervention

### 10.2 North Star Metric

**Eric engages in a multi-turn email conversation (3+ exchanges) without the bot breaking, hallucinating, or failing to respond.**

### 10.3 Supporting Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Bot responds to all test emails | 10/10 | Manual testing |
| Responses grounded in RAG context (no hallucination) | 100% of tested queries | Manual review |
| Salary stated correctly in Fairly mode | Exact range with comp context | Test email |
| PII redacted in Portfolio mode | 0 leaks in 10 adversarial tests | Manual testing |
| Architecture explanation matches actual build | Accurate | Self-review |
| Prompt injection resisted | 5/5 adversarial attempts handled | Manual testing |
| Total infrastructure cost | $0.00/month | GCP billing |

---

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Gemini hallucmates career details not in knowledge base | Medium | High (credibility) | RAG-only grounding; system prompt: "Only answer from provided context" |
| Email ends up in Eric's spam folder | Medium | High (application fails) | Test with multiple email providers first; use proper SMTP headers; include brief plain-text intro email first |
| GCE e2-micro runs out of memory (n8n + Chroma) | Medium | High (system down) | Benchmark memory usage; Chroma can run embedded in AI service on Cloud Run instead |
| Gemini free tier rate limit hit during demo | Low | Medium | n8n retry logic; email is async so small delays are acceptable |
| Prompt injection leaks salary floor or PII | Low | High (privacy) | Multi-layer defense: input sanitization + system prompt + output filter + tagged RAG chunks |
| Gmail app password compromised | Low | High (email access) | App password has limited scope; 2FA required; can revoke instantly |
| n8n workflow breaks and bot goes silent | Medium | High (no reply = failed application) | n8n error handling nodes; email alert on workflow failure; manual monitoring during application window |
| Interview transcripts contain PII from other people | Medium | Medium (privacy) | Clean transcripts before embedding; remove names, companies, identifiers of others |
| Competition — other candidates build better bots | High | Medium | Focus on conversational quality, technical depth, and honest personality — not gimmicks |

---

## 12. Timeline & Milestones

| Phase | Milestone | Target Duration | Dependencies |
|-------|-----------|-----------------|--------------|
| Phase 0 | Project setup: private repo, Gmail account, GCP resources | 1 hour | Google account, GitHub |
| Phase 1 | Resume-api Terraform: codify existing infrastructure | 3-4 hours | Phase 0, existing Cloud Run deployment |
| Phase 2 | Knowledge base: clean + chunk career data, resumes, transcripts into Chroma | 3-4 hours | Source documents from user |
| Phase 3 | AI service: FastAPI + RAG + Gemini Flash + feature flags + PII filter | 4-5 hours | Phase 2 (Chroma populated) |
| Phase 4 | n8n setup: GCE e2-micro + Docker Compose + email workflow | 3-4 hours | Phase 3 (AI service deployed) |
| Phase 5 | Extend Terraform: add bot infra to existing state | 2-3 hours | Phase 1 (base Terraform), Phase 4 |
| Phase 6 | CI/CD: GitHub Actions pipeline for AI service | 2-3 hours | Phase 3, Phase 5 |
| Phase 7 | Security hardening: adversarial testing, PII audit, output filtering | 2-3 hours | Phase 3, Phase 4 |
| Phase 8 | Documentation: implementation guide, draw.io diagram, README | 3-4 hours | All prior phases |
| Phase 9 | End-to-end testing: 10 test conversations, mode switching, edge cases | 2-3 hours | All prior phases |
| Phase 10 | Application: email Eric with bot address | 30 min | Phase 9 (all tests pass) |
| **Total** | **Project complete** | **25-35 hours** | |

---

## 13. Open Questions

| Question | Owner | Status |
|----------|-------|--------|
| Should Chroma run on GCE (Docker) or embedded in the Cloud Run AI service? | Builder | **Open** — depends on e2-micro memory constraints |
| How many interview transcripts are available and how clean are they? | Builder | **Open** — affects Phase 2 timeline |
| Should the bot proactively suggest topics ("Want to hear about my automation experience?")? | Builder | **Open** — could be impressive or annoying |
| Should there be a "first contact" auto-reply before the AI processes? | Builder | **Open** — instant "Got your email, thinking..." might improve experience |
| What email address format? (e.g., firstname.bot@gmail, hire.firstname@gmail) | Builder | **Open** |
| Should the resume-api be called live as an additional data source, or is RAG sufficient? | Builder | **Open** — RAG from source docs is likely sufficient |

---

## 14. Appendices

### 14.1 Skills Demonstrated (Mapped to Job Description)

| Job Requirement | How Demonstrated |
|----------------|-----------------|
| Build, test, and maintain automated workflows | n8n email workflow with error handling, retry logic, conversation memory |
| Connecting SaaS tools via webhooks and REST APIs | Gmail IMAP/SMTP + n8n webhook + Cloud Run API + Gemini API |
| AI Integration (OpenAI, Anthropic, etc.) in workflows | Gemini 2.5 Flash integrated via n8n HTTP node into email workflow |
| Prompt Engineering | Multi-layer system prompt with mode-based guardrails, RAG grounding, personality tuning |
| Monitoring & Debugging | n8n execution logs, Cloud Run metrics, error handling nodes, retry logic |
| The "Hacker" Mindset | Entire project built on $0 budget using free tiers creatively |
| Low-Code Experience | n8n visual workflow orchestration |
| Data Literacy (SQL, JSON, Webhooks, REST APIs) | SQLite conversation store, JSON payloads between services, REST API design |
| Challenge the status quo | Built an AI interview bot instead of submitting a traditional resume |

### 14.2 Technology Stack Summary

| Layer | Technology | Cost |
|-------|-----------|------|
| Email Interface | Gmail (IMAP + SMTP) | Free |
| Workflow Orchestration | n8n (self-hosted) | Free |
| AI Generation | Gemini 2.5 Flash | Free tier |
| Vector Database | Chroma | Free (open source) |
| Embeddings | HuggingFace all-MiniLM-L6-v2 | Free (open source) |
| AI Service Framework | FastAPI + Uvicorn | Free (open source) |
| Conversation Store | SQLite | Free (embedded) |
| Compute (always-on) | GCE e2-micro | Free tier |
| Compute (serverless) | Cloud Run | Free tier |
| Container Registry | Artifact Registry | Free tier |
| Secret Management | GCE Secret Manager | Free tier |
| Infrastructure as Code | Terraform | Free (open source) |
| CI/CD | GitHub Actions | Free for private repos (2000 min/month) |
| Source Control | GitHub (private repo) | Free |

### 14.3 Security Reference

This project applies principles from the Vibe Code Security Guide (separate project), specifically:
- Section 13: AI-Powered Application Security (prompt injection, output validation)
- Section 12: Webhook & Integration Security (email webhook validation)
- Section 23: Docker & Container Security (non-root, minimal images)
- Section 36: Agentic AI Security Principles (least privilege, action boundaries)
- Section 34: Persistent AI Agent Security (memory hygiene, credential protection)
