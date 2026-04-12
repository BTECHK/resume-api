# Phase 2: End-to-End Data Pipeline

**Status:** Done ✅ — shipped in milestone v1.0
**Goal:** Move from a one-shot API demo to a persistently hosted service with realistic traffic and enriched request telemetry.

## Architecture
![data pipeline diagram](../diagrams/phase-02.png)
<!-- diagram file: docs/diagrams/phase-02.drawio -->
*Docker Compose on an e2-micro VM runs the API under systemd; Locust drives traffic, enhanced middleware logs to SQLite, and APScheduler batch-syncs rows to BigQuery.*

## What was built
- Docker Compose + systemd persistent hosting on a GCE e2-micro VM
- Enhanced request logging middleware with funnel-style fields (recruiter_domain, endpoint_hit, skill_searched, response_time_ms, http_status)
- Locust traffic simulation — 200K-row burst test against the live endpoint
- APScheduler-driven ETL job (SQLite → BigQuery) so the warehouse is fed automatically
- BigQuery analytics queries running against ~500K real pipeline-produced rows

## Key decisions
| Decision | Rationale | Reference |
|---|---|---|
| e2-micro + Docker Compose (not Cloud Run) | Always-on free-tier host for scheduler + persistent SQLite | [phase-2-approach.md](../phase-2-approach.md) |
| APScheduler in-process | No extra infra; good enough for batch ETL | [phase-2-implementation-guide.md](../phase-2-implementation-guide.md) |
| Locust over k6/wrk | Python-native, matches the rest of the stack | [phase-2-implementation-guide.md](../phase-2-implementation-guide.md) |
| Enrich middleware, not endpoints | Central capture point, no per-route duplication | [phase-2-implementation-guide.md](../phase-2-implementation-guide.md) |

## What I learned
- e2-micro is tight on memory — ran into OOM risk once n8n entered the picture later (Phase 5), which is why a 2GB swap file became standard.
- In-process APScheduler is fine until you need multi-instance deployment; at that point a managed scheduler or Cloud Scheduler pushes past it.
- Initially logged to stdout only; switched to structured SQLite writes when analytics endpoints needed to query the same data.

## Links
- Source: [`api/main.py`](../../api/main.py)
- Full walkthrough: [docs/phase-2-implementation-guide.md](../phase-2-implementation-guide.md)
- Design doc: [docs/phase-2-approach.md](../phase-2-approach.md)
- Next: [Phase 3](./03-iac-cicd-ai.md)
