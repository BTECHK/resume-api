# Phase 1: Core API + Analytics

**Status:** Done ✅ — shipped in milestone v1.0 (2026-03-02)
**Goal:** Ship a production-grade REST API serving structured resume data with analytics tracking, deployed on Cloud Run.

## Architecture
![core api diagram](../diagrams/phase-01.png)
<!-- diagram file: docs/diagrams/phase-01.drawio -->
*Recruiter/client hits FastAPI on Cloud Run; middleware logs each request to SQLite (operational) while a simulated ETL feeds BigQuery for analytical queries.*

## What was built
- 9 REST endpoints (resume + analytics) — [`api/main.py`](../../api/main.py)
- SQLite operational store (~10K rows) for real-time analytics — [`api/`](../../api/)
- BigQuery analytical warehouse (500K–5M rows) for scale SQL — [`scripts/generate_data.py`](../../scripts/generate_data.py)
- Three-tier SQL progression: naive → CTE + window functions → partitioned + clustered
- Scale benchmarks at 10K / 500K / 5M rows comparing Python dict, SQLite, BigQuery
- Docker container + Cloud Run deployment — [`Dockerfile`](../../Dockerfile)

## Key decisions
| Decision | Rationale | Reference |
|---|---|---|
| FastAPI over Flask/Django | Auto-generated OpenAPI docs; async support | [README](../../README.md) |
| SQLite + BigQuery split | Operational vs analytical workloads; mirrors ad-tech patterns | [README](../../README.md) |
| Cloud Run, not GCE | Scales to zero; free tier friendly; Docker-native | [README](../../README.md) |
| Simulated ETL (generate_data.py + bq load) | Keeps focus on API + SQL skills without pipeline infra | [README](../../README.md) |
| Multi-endpoint resource model | Mirrors Google Ads API resource design | [README](../../README.md) |

## What I learned
- The Python/SQLite/BigQuery crossover is real and measurable — Python dict streaming timed out at 60s on 5M rows while BigQuery finished in ~1s.
- Partitioning + clustering on a 5M-row table cut bytes scanned by 45%, the difference between a $5 query and $0.05 at ad-tech scale.
- FastAPI's auto-generated `/docs` endpoint removed a whole class of doc-drift problems — the schema is the docs.

## Screenshots
- ![SQL Tier 1 naive](../screenshots/step-3.4-sql-tier1-naive-query.png)
- ![SQL Tier 2 CTE + window](../screenshots/step-3.4-sql-tier2-optimized-ctes-window-functions.png)
- ![SQL Tier 3 partitioned + clustered](../screenshots/step-3.4-sql-tier3-partitioned-clustered.png)
- ![Benchmark 10K](../screenshots/step-3.5-benchmark-small-10k.png)
- ![Benchmark 500K](../screenshots/step-3.6-benchmark-medium-500k.png)
- ![Benchmark 5M](../screenshots/step-3.8-benchmark-large-5m.png)

## Links
- Source: [`api/main.py`](../../api/main.py)
- Full walkthrough: [docs/implementation-guide.md](../implementation-guide.md)
- Next: [Phase 2](./02-data-pipeline.md)
