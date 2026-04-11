"""
Architecture Decision Record content for RAG-06 (architecture self-awareness).

This module exposes concise, factual statements about the system's architecture
so the bot can answer questions like "How is this system built?" or "Why Gemini?"
from grounded context rather than hallucinating.

Content is authored directly (not scraped from docs/plans/) to guarantee
anonymization and accuracy. Each entry is a self-contained mini-ADR.
"""

ADR_CONTENT: list[dict] = [
    {
        "decision": "Chose paraphrase-MiniLM-L3-v2 as the embedding model",
        "phase": 4,
        "content": (
            "The ai-service uses paraphrase-MiniLM-L3-v2 (33MB) as its sentence embedding model. "
            "We chose this over the more common all-MiniLM-L6-v2 (420MB) specifically to minimize "
            "Cloud Run cold start time. The 33MB model is baked into the Docker image at build time "
            "and loads into memory in under 1 second on a cold container."
        ),
    },
    {
        "decision": "Chose Chroma with ephemeral in-memory client",
        "phase": 4,
        "content": (
            "The ai-service uses Chroma as its vector database in ephemeral (in-memory) mode. "
            "On every cold start, it re-ingests the bundled resume data from resume_data.py into "
            "a fresh collection. This avoids persistent-volume complexity on Cloud Run and "
            "keeps the service stateless — any instance can serve any request without session "
            "affinity."
        ),
    },
    {
        "decision": "Chose Gemini 2.5 Flash via google-genai SDK",
        "phase": 4,
        "content": (
            "Answer generation uses Gemini 2.5 Flash accessed via the google-genai Python SDK "
            "(not the older google-generativeai package, which was deprecated in November 2025). "
            "Gemini 2.5 Flash was chosen for its free tier, sub-second latency on short prompts, "
            "and strong instruction-following for RAG-style grounded answers."
        ),
    },
    {
        "decision": "Chose separate ai-service on Cloud Run, decoupled from Phase 1 REST API",
        "phase": 4,
        "content": (
            "The AI-powered endpoints (/ai/ask, /chat) live in a new ai-service deployed as a "
            "separate Cloud Run service, not bolted onto the existing Phase 1 resume-api service. "
            "This keeps the original REST API untouched, allows independent scaling, and prevents "
            "embedding model cold-start time from affecting the simpler REST endpoints."
        ),
    },
    {
        "decision": "Chose n8n self-hosted on e2-micro for the email bot",
        "phase": 5,
        "content": (
            "The email-to-AI bot runs on a self-hosted n8n instance on a GCE e2-micro (1 vCPU, "
            "1GB RAM) with a 2GB swap file, Docker mem_limit of 700MB, and systemd auto-restart. "
            "Gmail OAuth is in Production mode (not Test) to prevent the 7-day token expiry that "
            "would otherwise require weekly manual re-auth. Polling interval is 5 minutes."
        ),
    },
    {
        "decision": "Chose React 19 + Vite 8 + Tailwind v4 for the chatbot frontend",
        "phase": 6,
        "content": (
            "The recruiter-facing chatbot is a React 19.2 + Vite 8.0 + TypeScript + Tailwind v4.2 "
            "single-page app, deployed as a multi-stage Docker image (Node build stage, Nginx "
            "serve stage) on Cloud Run. It calls the ai-service /chat endpoint directly via CORS; "
            "there is no reverse proxy or same-origin mount. Design follows Apple Human Interface "
            "guidelines — system font stack, generous whitespace, rounded-2xl cards."
        ),
    },
    {
        "decision": "Chose IP-based rate limiting via slowapi",
        "phase": 4,
        "content": (
            "Rate limiting uses slowapi, configured at 10 requests/minute on /ai/ask and "
            "30 requests/minute on /chat. Flagged IPs (those that trigger prompt injection "
            "detection) get additional dynamic reduction for 5 minutes. This prevents abuse "
            "while keeping the latency overhead negligible for normal users."
        ),
    },
    {
        "decision": "Chose regex-based prompt injection detection with canned deflection",
        "phase": 4,
        "content": (
            "Prompt injection detection uses a list of compiled regex patterns covering known "
            "attack phrases (ignore previous instructions, DAN mode, jailbreak, etc.). When a "
            "pattern matches, the service returns a canned deflection message with HTTP 429 "
            "so the attacker sees a generic rate-limit error rather than a security detection. "
            "The detected IP is also flagged for 5 minutes of increased scrutiny."
        ),
    },
    {
        "decision": "Chose GCP Secret Manager for all runtime secrets",
        "phase": 4,
        "content": (
            "The Gemini API key and any other runtime secrets live in GCP Secret Manager. The "
            "ai-service fetches them at startup via google-cloud-secret-manager and caches them "
            "in memory. No secrets appear in the Docker image, environment variables committed "
            "to the repo, or CI/CD configs."
        ),
    },
    {
        "decision": "Chose two-tier RAG retrieval for interview-impressive differentiation",
        "phase": 7,
        "content": (
            "The RAG layer uses two separate Chroma collections: tier 1 is the resume factual "
            "corpus (always retrieved) and tier 2 is a small corpus of anonymized mock interview "
            "Q&A patterns (retrieved only for behavioral/interview questions). A keyword router "
            "decides when to include tier 2 based on the question's intent. This prevents "
            "factual contamination while still letting the bot answer behavioral questions "
            "with realistic style."
        ),
    },
    {
        "decision": "Chose file-based JSONL logging for unanswered questions",
        "phase": 7,
        "content": (
            "Questions the bot cannot confidently answer (confidence below 0.3) are appended "
            "as JSONL lines to /tmp/unanswered_questions.jsonl on the Cloud Run instance. "
            "This is ephemeral but visible through Cloud Logging tail for offline analysis, "
            "driving future knowledge-base improvements."
        ),
    },
    {
        "decision": "Chose direct CORS from chatbot to ai-service (no reverse proxy)",
        "phase": 6,
        "content": (
            "The React chatbot calls the ai-service Cloud Run URL directly via CORS rather than "
            "through a reverse proxy on the frontend's Nginx. The ai-service has ALLOWED_ORIGINS "
            "locked to the chatbot's Cloud Run URL. This keeps the deployment simpler at the "
            "cost of a chicken-and-egg CORS update after initial deploy (handled in DEFERRED-WORK.md)."
        ),
    },
]


def get_adr_content_as_text() -> str:
    """Render the ADR corpus as a single string for chunked ingestion."""
    parts = []
    for item in ADR_CONTENT:
        parts.append(
            f"ARCHITECTURE DECISION — {item['decision']}\n"
            f"Phase: {item.get('phase', 'n/a')}\n"
            f"{item['content']}\n"
        )
    return "\n---\n".join(parts)
