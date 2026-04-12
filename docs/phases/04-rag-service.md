# Phase 4: RAG Core Service

**Status:** In Progress 🟡 — deployed on default compute SA; dedicated service account fix in flight
**Goal:** A standalone FastAPI `ai-service` on Cloud Run that answers recruiter questions over the resume via Chroma + Gemini, with full security middleware.

## Architecture
![rag service diagram](../diagrams/phase-04.png)
<!-- diagram file: docs/diagrams/phase-04.drawio -->
*Client → Cloud Run ai-service → injection detection + rate limit → Chroma (ephemeral, in-memory) → Gemini 2.5 Flash → sanitized response; secrets pulled from GCP Secret Manager at startup.*

## What was built
- FastAPI app with `/ai/ask`, `/chat`, `/health` endpoints — [`ai-service/main.py`](../../ai-service/main.py)
- Chroma ephemeral in-memory vector store, MiniLM embeddings baked into the image — [`ai-service/rag.py`](../../ai-service/rag.py)
- Regex-based prompt injection detection + response sanitization — [`ai-service/security.py`](../../ai-service/security.py)
- slowapi IP-based rate limiting (10 req/min on `/ai/ask`, `/chat`)
- Secret Manager integration loads Gemini API key at startup — [`ai-service/gcp_secrets.py`](../../ai-service/gcp_secrets.py)
- Dedicated Dockerfile with CPU-only PyTorch and non-blocking startup — [`ai-service/Dockerfile`](../../ai-service/Dockerfile)

## Key decisions
| Decision | Rationale | Reference |
|---|---|---|
| paraphrase-MiniLM-L3-v2 (33MB) | Fits in Cloud Run image; good enough for short-corpus RAG | [ADR-0001](../adrs/0001-embedding-model.md) |
| Chroma ephemeral, not persistent | Corpus is tiny; rebuild on cold start beats managing disk | [ADR-0002](../adrs/0002-chroma-ephemeral.md) |
| Separate ai-service, not bolt-on | Decouples image size and cold-start from main API | [ADR-0004](../adrs/0004-separate-ai-service.md) |
| slowapi IP-based limiting | No external store needed; Cloud Run friendly | [ADR-0007](../adrs/0007-slowapi-rate-limiting.md) |
| Regex injection detection | Fast, transparent, no extra ML model | [ADR-0008](../adrs/0008-regex-injection-detection.md) |
| Secret Manager for all secrets | No keys in images, env, or git | [ADR-0009](../adrs/0009-secret-manager.md) |

## What I learned
- Baking the 33MB MiniLM model into the image traded image size for cold-start determinism — preferable to first-request downloads.
- Initial CPU PyTorch image was >2GB; switching to the CPU-only wheel dropped it substantially (see commit 94e88be).
- Startup was blocking on model load; moved to non-blocking lifespan init (commit d2caf16) to fix Cloud Run port-readiness timeouts.

## Links
- Source: [`ai-service/main.py`](../../ai-service/main.py), [`ai-service/security.py`](../../ai-service/security.py), [`ai-service/rag.py`](../../ai-service/rag.py)
- Related ADRs: [0007](../adrs/0007-slowapi-rate-limiting.md), [0008](../adrs/0008-regex-injection-detection.md), [0009](../adrs/0009-secret-manager.md), [0010](../adrs/0010-two-tier-rag.md), [0012](../adrs/0012-direct-cors.md)
- Next: [Phase 5](./05-email-bot.md)
