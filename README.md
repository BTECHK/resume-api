# Resume API

[![CI](https://github.com/BTECHK/resume-api/actions/workflows/ci.yml/badge.svg)](https://github.com/BTECHK/resume-api/actions)

A recruiter-facing resume platform: REST API, RAG-powered chat, and email bot, all deployed on Google Cloud with Terraform + GitHub Actions. Three interaction surfaces (curl, email, chat) share one FastAPI + Chroma + Gemini backend.

**Live:** https://resume-api-711025857117.us-central1.run.app — [API docs](https://resume-api-711025857117.us-central1.run.app/docs)

---

## At a glance

![Architecture](docs/diagrams/architecture.png)
*Dual-database FastAPI on Cloud Run (SQLite for serving, BigQuery for analytics) with a separate RAG ai-service powering the email bot and React chatbot.*

| Layer | Tech |
|---|---|
| API | Python 3.11, FastAPI, SQLite, BigQuery |
| AI | Chroma (ephemeral), paraphrase-MiniLM-L3-v2 (baked-in), Gemini 2.5 Flash, slowapi |
| Frontend | React 19, Vite 8, Tailwind v4, react-router 7 |
| Infra | Terraform, GitHub Actions (WIF), Cloud Run, BigQuery, Secret Manager, Artifact Registry |

---

## What's built

| Phase | Status | Goal | Deep dive |
|---|---|---|---|
| 1 — Core API + Analytics | Done ✅ | 9 REST endpoints, SQLite + BigQuery dual store, 3-tier SQL progression | [docs/phases/01-core-api.md](docs/phases/01-core-api.md) |
| 2 — Data Pipeline | Done ✅ | Request-logging middleware, Locust traffic simulation, SQLite→BigQuery ETL | [docs/phases/02-data-pipeline.md](docs/phases/02-data-pipeline.md) |
| 3 — IaC + CI/CD + AI scaffolding | Done ✅ | Terraform modules w/ GCS remote state, lint→SAST→SCA→test→build pipeline, RAG scaffolding | [docs/phases/03-iac-cicd-ai.md](docs/phases/03-iac-cicd-ai.md) |
| 7 — Testing | Done ✅ | 86 tests (unit + integration + endpoint security), 70% coverage gate | [docs/phases/07-testing.md](docs/phases/07-testing.md) |
| 4 — RAG service | In progress 🟡 | ai-service live on Cloud Run, hardening in flight | [docs/phases/04-rag-service.md](docs/phases/04-rag-service.md) |
| 5 — n8n email bot | In progress 🟡 | e2-micro VM + n8n workflow, Terraform apply pending | [docs/phases/05-email-bot.md](docs/phases/05-email-bot.md) |
| 6 — React frontend | In progress 🟡 | Streaming chat UI on Cloud Run behind nginx:1.27-alpine | [docs/phases/06-react-frontend.md](docs/phases/06-react-frontend.md) |
| 8 — CI/CD hardening | In progress 🟡 | Workload Identity Federation, full push-to-main pipeline | [docs/phases/08-cicd-hardening.md](docs/phases/08-cicd-hardening.md) |
| Observability | Next ⬜ | Cloud Logging dashboards, SLO tracking |  |
| Cost alerts | Next ⬜ | Validate billing budgets across all services |  |
| Load testing | Next ⬜ | Locust against full live stack |  |

---

## Key decisions & learnings

- **3-tier SQL progression (naive → CTEs+windows → partitioned/clustered)** — makes the crossover between Python, SQLite, and BigQuery concrete. At 5M rows, partitioning cut bytes scanned 45%. See benchmarks in [docs/phases/01-core-api.md](docs/phases/01-core-api.md).
- **Two-tier RAG retrieval** — resume facts and interview/architecture patterns live in separate Chroma collections, queried independently then merged. Keeps factual answers from being diluted by meta content. [ADR-0010](docs/adrs/0010-two-tier-rag.md).
- **Separate ai-service from the resume API** — RAG deps (torch, sentence-transformers, chromadb) would have bloated the resume API container from ~150MB to ~2GB. Isolating them keeps cold starts fast on the public API. [ADR-0004](docs/adrs/0004-separate-ai-service.md).
- **Baked-in MiniLM-L3-v2 embeddings (33MB)** — no external embedding API, no network hop per query, no extra cost, deterministic cold starts. [ADR-0001](docs/adrs/0001-embedding-model.md).
- **Regex-based prompt injection detection + response sanitization** — 20+ patterns block the common jailbreak vectors before the Gemini call; output is re-scanned for leaked system prompt fragments. [ADR-0008](docs/adrs/0008-regex-injection-detection.md).
- **IP rate limiting via slowapi** — per-IP caps on `/chat` keep Gemini spend bounded under abuse. [ADR-0007](docs/adrs/0007-slowapi-rate-limiting.md).
- **Secrets in Secret Manager with least-privilege service accounts** — no keys in env files, no keys in Terraform state, IAM scoped per-secret per-service. [ADR-0009](docs/adrs/0009-secret-manager.md).
- **Direct CORS from chatbot to ai-service** — no API gateway in front; simpler deploy topology, one CORS allowlist, one trust boundary. [ADR-0012](docs/adrs/0012-direct-cors.md).

---

## Security posture

Aligned to OWASP API Security Top 10 (2023). Full write-up in [docs/security.md](docs/security.md).

| OWASP item | Control | Code ref |
|---|---|---|
| API8 Injection | Regex prompt-injection filter + response sanitization | [ai-service/security.py](ai-service/security.py) |
| API2 Broken auth | Public by design (portfolio); no user auth surface | [ai-service/main.py](ai-service/main.py) |
| API8 Secrets | Google Secret Manager, per-service SA | [infra/modules/secrets](infra/) |
| API4 Resource abuse | slowapi per-IP rate limits on `/chat` | [ai-service/main.py](ai-service/main.py) |
| API8 Supply chain | Trivy + Bandit + pip-audit in CI on every push | [.github/workflows/ci.yml](.github/workflows/ci.yml) |
| Container hardening | nginx:1.27-alpine non-root, digest-pinnable, CPU-only Torch | [ai-service/Dockerfile](ai-service/Dockerfile) |

---

## Running locally

```bash
git clone https://github.com/BTECHK/resume-api.git
cd resume-api
pip install -r requirements.txt
python scripts/generate_data.py
cd api && uvicorn main:app --reload --port 8000
# Docs: http://localhost:8000/docs
```

For the RAG service, frontend dev server, and the full GCP deployment walkthrough (Terraform, WIF, Cloud Run, Secret Manager), see [docs/deploy/gcp-walkthrough.md](docs/deploy/gcp-walkthrough.md).

---

## Roadmap

**Done**
- Core API, analytics pipeline, dual-database architecture
- Terraform modules + GitHub Actions CI
- Test suite with coverage gate

**In progress**
- AI service, email bot, React chatbot live on Cloud Run
- Full WIF-based push-to-main pipeline

**Next**
- Cloud Logging dashboards + SLO tracking
- Cost alert validation
- Load testing against live stack

---

## Repo structure

```
resume-api-repo/
  api/                 FastAPI app (resume + analytics endpoints)
  ai-service/          RAG service (FastAPI + Chroma + Gemini)
  frontend/            React 19 + Vite + Tailwind chatbot
  infra/               Terraform modules (Cloud Run, BQ, IAM, Secrets)
  scripts/             Data generation + ETL helpers
  tests/               Unit, integration, endpoint security
  docs/
    adrs/              12 architecture decision records
    phases/            Per-phase deep-dives
    diagrams/          Architecture diagrams
    deploy/            GCP walkthrough
  .github/workflows/   CI pipeline
```

---

## License & attribution

Portfolio project, educational use. Built with Firebase Studio + Gemini AI-assisted development. Data model inspired by digital advertising reporting patterns (Google Ads API resource conventions).
