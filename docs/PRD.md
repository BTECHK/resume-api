# Resume API — Product Requirements Document

**Version:** 1.0  
**Author:** [Your Name]
**Date:** February 2025  
**Status:** Draft  
**Project Type:** Portfolio / Self-Study Project

---

## 1. Overview

### 1.1 Problem Statement

Technical consulting roles in ad tech require practitioners to demonstrate hands-on proficiency in API design, SQL at scale, Linux deployment, and Python — but most consultants' day-to-day work involves architecture and stakeholder management, not greenfield builds. There is a gap between "I understand these concepts" and "here is a live system I designed and deployed end-to-end."

### 1.2 Opportunity

The ad tech ecosystem increasingly relies on integrations between REST APIs, cloud-hosted analytical databases (BigQuery), and containerized deployment. A portfolio project that demonstrates all of these — with a data model that mirrors digital advertising reporting patterns — provides a tangible artifact that showcases full-stack technical depth alongside domain awareness.

### 1.3 Solution Summary

Build and deploy a REST API on Google Cloud infrastructure that serves structured resume data and tracks analytics on who queries the resume. The system is designed as a **recruiter analytics pipeline**: the API ingests recruiter interactions via request logging middleware, stores them in SQLite for real-time operational analytics, and feeds that data into BigQuery for large-scale analytical queries. The data model intentionally mirrors Google Ads reporting patterns (advertiser → campaign → keyword → performance metrics), and the dual-database architecture mirrors how enterprise ad tech clients use operational stores alongside BigQuery analytical warehouses connected by ETL pipelines.

In this version, the ETL layer between SQLite and BigQuery is simulated — a data generation script produces realistic data matching the middleware schema, and `bq load` CLI uploads it to BigQuery. Future iterations would add automated ETL (Cloud Functions), mock API load testing to generate organic traffic, and streaming ingestion. The entire project runs on Google's free tier and is documented in a public GitHub repo.

### 1.4 Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Primary: All 9 API endpoints return valid JSON | 9/9 passing | curl tests against live Cloud Run URL |
| Primary: BigQuery 3-tier SQL demos execute successfully | 3/3 queries run | BigQuery console screenshots with bytes scanned |
| Secondary: README communicates design decisions clearly | Peer review (self-assess) | Can a technical reader understand the architecture in <2 min? |
| Secondary: Swagger/OpenAPI docs auto-generated | Docs accessible at /docs | Browser test |
| Guardrail: Total cost remains $0.00 | $0.00 | GCP billing dashboard — budget alert set at $1 |
| Guardrail: Build time under 12 hours total | ≤12 hrs | Time tracking |

---

## 2. Target Users

### 2.1 Primary User Persona

**Name:** The Technical Reader
**Segment:** Engineer, architect, or technical lead exploring ad tech portfolio projects

**Jobs to be Done:**

| Job Type | Job Statement | Priority |
|----------|---------------|----------|
| Functional | Understand how a REST API can be designed and deployed end-to-end on Google Cloud | P0 |
| Functional | See SQL proficiency demonstrated across naive, optimized, and scale-aware query patterns | P0 |
| Functional | Learn how web tech integrates with the digital advertising ecosystem | P0 |
| Emotional | Feel inspired to build a similar portfolio project or apply these patterns | P1 |

### 2.2 Secondary User Persona

**Name:** The Builder (Self)
**Segment:** Self-study practitioner

**Jobs to be Done:**

| Job Type | Job Statement | Priority |
|----------|---------------|----------|
| Functional | Practice end-to-end technical skills: API design, Linux deployment, SQL optimization, Python | P0 |
| Functional | Have a live artifact that demonstrates these skills publicly | P0 |
| Emotional | Build confidence through hands-on execution | P1 |

### 2.3 Anti-Personas (Who This Is NOT For)

- **End users / general public** — This is not a production application; it's a learning project
- **Non-technical visitors looking for an actual resume site** — The API serves data, not a pretty frontend
- **Anyone expecting enterprise-grade security** — Authentication, encryption at rest, etc. are discussed in the README but not implemented (portfolio scope)

---

## 3. User Stories & Requirements

### 3.1 Epic Overview

| Epic | Description | Priority |
|------|-------------|----------|
| Epic 1: REST API Design | Build 9 endpoints with proper resource modeling, query params, status codes | P0 |
| Epic 2: Data Generation & Database Setup | Generate 10K rows (SQLite) + 500K rows (BigQuery) with realistic schema | P0 |
| Epic 3: SQL Query Progression | Write and document 3 tiers of SQL from naive to optimized | P0 |
| Epic 4: Linux Deployment | Dockerize and deploy via CLI on Cloud Run | P0 |
| Epic 5: Documentation | README with design decisions, trade-offs, ecosystem connections | P0 |
| Epic 6: Ad Tech Data Model | Schema mirrors digital advertising reporting patterns | P1 |

### 3.2 Detailed User Stories

**Epic 1: REST API Design**

| ID | User Story | Acceptance Criteria | Priority |
|----|------------|---------------------|----------|
| US-001 | As a technical reader, I want to hit GET /resume and receive structured JSON so I can see proper resource modeling | - Returns 200 with valid JSON | P0 |
| | | - JSON has sections: summary, experience, skills, education, certifications | |
| US-002 | As a technical reader, I want to hit GET /resume/experience?company=deloitte so I can see query parameter filtering works | - Filters results to Deloitte entries only | P0 |
| | | - Returns 200 with filtered array | |
| US-003 | As a technical reader, I want to see GET /resume/skills?category=databases return grouped skills | - Groups by category | P0 |
| | | - Returns count metadata | |
| US-004 | As a technical reader, I want to see GET /analytics/top-domains use a Python dictionary frequency map | - Code comments show dict-based approach AND Counter approach | P0 |
| | | - Response includes method and complexity info | |
| US-005 | As a technical reader, I want to see the auto-generated /docs page | - Swagger UI loads at /docs | P1 |
| | | - All endpoints documented with schemas | |

**Epic 2: Data Generation**

| ID | User Story | Acceptance Criteria | Priority |
|----|------------|---------------------|----------|
| US-006 | As a builder, I want to generate 10K rows of realistic analytics data into SQLite | - Uses Faker library | P0 |
| | | - Weighted distribution on http_status | |
| | | - Completes in <10 seconds | |
| US-007 | As a builder, I want to generate 500K rows as CSV for BigQuery upload | - CSV generated with same schema | P0 |
| | | - Progress printed every 100K rows | |

**Epic 3: SQL Query Progression**

| ID | User Story | Acceptance Criteria | Priority |
|----|------------|---------------------|----------|
| US-008 | As a technical reader, I want to see a naive full-table-scan query with documented bytes processed | - Query runs in BigQuery console | P0 |
| | | - Screenshot shows bytes scanned | |
| US-009 | As a technical reader, I want to see an optimized query using CTEs, window functions, SAFE_DIVIDE | - Uses CTE, RANK(), SAFE_DIVIDE, COUNTIF | P0 |
| | | - Shows bytes improvement vs Tier 1 | |
| US-010 | As a technical reader, I want to see partitioned + clustered table with dramatic scan reduction | - Table partitioned by DATE(timestamp) | P0 |
| | | - Clustered by recruiter_domain, endpoint_hit | |
| | | - Bytes scanned drops significantly | |

**Epic 4: Linux Deployment**

| ID | User Story | Acceptance Criteria | Priority |
|----|------------|---------------------|----------|
| US-011 | As a builder, I want to deploy via Docker + gcloud CLI so I can demonstrate Linux/CLI proficiency | - Dockerfile builds successfully | P0 |
| | | - `gcloud run deploy` succeeds | |
| | | - Public URL returns 200 | |
| US-012 | As a builder, I want screenshots of key Linux commands executed during development | - ps, ss, top, kill, grep, curl all captured | P1 |

**Epic 5: Documentation**

| ID | User Story | Acceptance Criteria | Priority |
|----|------------|---------------------|----------|
| US-013 | As a technical reader, I want to read the README and understand the full architecture in under 2 minutes | - Architecture diagram present | P0 |
| | | - Design decisions explained with trade-offs | |
| | | - Ad tech ecosystem mapping included | |

### 3.3 Feature Requirements Matrix (MoSCoW)

| Feature | Story | Must Have | Should Have | Nice to Have | Won't Have (v1) |
|---------|-------|-----------|-------------|--------------|-----------------|
| 9 REST endpoints | US-001–005 | X | | | |
| Pydantic response models | US-001 | X | | | |
| SQLite 10K row dataset | US-006 | X | | | |
| BigQuery 500K row dataset | US-007 | X | | | |
| 3-tier SQL progression | US-008–010 | X | | | |
| Docker + Cloud Run deploy | US-011 | X | | | |
| README with design decisions | US-013 | X | | | |
| Swagger /docs page | US-005 | | X | | |
| Linux command screenshots | US-012 | | X | | |
| Request logging middleware | — | | X | | |
| Rate limit headers | — | | | X | |
| Scale benchmark (10K→500K→5M) | FR-014 | X | | | |
| CROSS JOIN 5M table generation | FR-015 | | X | | |
| Frontend UI | — | | | | X |
| Authentication/OAuth | — | | | | X |
| CI/CD pipeline | — | | | | X |
| Custom domain name | — | | | | X |
| Automated ETL (SQLite → BigQuery) | — | | | | X |
| Mock API load testing (Locust/wrk) | — | | | | X |
| Streaming ingestion (Pub/Sub + Dataflow) | — | | | | X |

---

## 4. Functional Requirements

### 4.1 Core Functionality

**API Server**

| Req ID | Requirement | Rationale | Priority |
|--------|-------------|-----------|----------|
| FR-001 | FastAPI app with 9 GET endpoints returning JSON | Demonstrates REST resource modeling and API design | P0 |
| FR-002 | Pydantic models for all request/response schemas | Shows type safety awareness; mirrors production API design | P0 |
| FR-003 | CORS middleware enabled | Required for any browser-based API consumer | P0 |
| FR-004 | /analytics/top-domains uses dict frequency map + Counter | Demonstrates Python data structure proficiency | P0 |
| FR-005 | Request logging middleware (timestamp, endpoint, response_time_ms) | Demonstrates observability awareness | P1 |
| FR-006 | Rate limiting headers on all responses | Shows API gateway awareness without over-engineering | P2 |

**Data Layer**

| Req ID | Requirement | Rationale | Priority |
|--------|-------------|-----------|----------|
| FR-007 | SQLite database with 10K rows of analytics data | Operational DB for API-served queries | P0 |
| FR-008 | BigQuery dataset with 500K rows, same schema | Analytical DB for scale demonstrations | P0 |
| FR-009 | Faker-generated data with realistic distributions | Weighted status codes, realistic domains, 90-day range | P0 |
| FR-010 | Data schema mirrors digital advertising reporting patterns | Demonstrates domain knowledge and practical data modeling | P1 |

**SQL Demonstrations**

| Req ID | Requirement | Rationale | Priority |
|--------|-------------|-----------|----------|
| FR-011 | Tier 1: Naive GROUP BY query with documented bytes processed | Baseline for comparison | P0 |
| FR-012 | Tier 2: CTE + Window Function + SAFE_DIVIDE query | Production-quality SQL pattern | P0 |
| FR-013 | Tier 3: Partitioned + clustered table with scan reduction | Scale-aware optimization | P0 |
| FR-014 | Scale benchmark progression (10K → 500K → 5M rows) with 3 scripts comparing Python dict/Counter, SQLite, and BigQuery at each scale | Shows "when to use each" decision framework — demonstrates that tool selection changes as data volume grows | P0 |
| FR-015 | CROSS JOIN table generation (500K → 5M rows inside BigQuery) | Demonstrates SQL-native data generation at scale without ETL pipeline | P1 |

### 4.2 Primary User Flow

```
Step 1: Reader opens GitHub repo
  → Sees: README with architecture diagram and design decisions
  → Action: Reads for 1-2 minutes, understands the system

Step 2: Clicks live Cloud Run URL
  → Sees: JSON health check response
  → Action: Navigates to /docs for Swagger UI

Step 3: Tests /resume/experience?company=deloitte
  → Sees: Filtered JSON response with work experience
  → Action: Observes proper REST design, query params, status codes

Step 4: Reads "Data Pipeline: End-to-End Flow" section
  → Sees: Clear narrative — API ingests recruiter hits → SQLite → (ETL) → BigQuery
  → Action: Understands the system as a pipeline, not disconnected components
  → Notes: ETL is explicitly marked as simulated, with future iterations documented

Step 5: Scrolls to SQL Query Progression in README
  → Sees: 3 tiers with screenshots showing bytes scanned decreasing
  → Action: Understands BigQuery partitioning/clustering optimization

Step 6: Reads "Digital Marketing Ecosystem Connection" section
  → Sees: Mapping of project patterns to ad tech workflows
  → Action: Understands how project patterns map to real-world ad tech systems
```

### 4.3 Edge Cases & Error Handling

| Scenario | Expected Behavior | Priority |
|----------|-------------------|----------|
| Invalid query param (e.g., `?limit=-5`) | Return 400 with descriptive error message | P1 |
| Request for non-existent resume section (e.g., `/resume/hobbies`) | Return 404 with available sections listed | P1 |
| BigQuery connection failure (if BQ endpoint added) | Return 503 with fallback message; don't crash the API | P2 |
| Empty query result (e.g., `?company=nonexistent`) | Return 200 with empty array, not 404 | P1 |

---

## 5. Non-Functional Requirements

### 5.1 Performance

| Requirement | Target | Measurement |
|-------------|--------|-------------|
| API response time (resume endpoints) | < 100ms | FastAPI middleware logging |
| API response time (analytics endpoints) | < 500ms | FastAPI middleware logging |
| Data generation (500K rows) | < 120 seconds | Script timing output |
| Cold start (Cloud Run) | < 5 seconds | First request after idle |

### 5.2 Scalability

*This is a portfolio project, so scalability is discussed rather than required:*

- Cloud Run auto-scales from 0 to N instances (capped at 1 for free tier)
- BigQuery handles petabyte-scale queries natively
- README documents "what breaks at 10x/100x/1000x" for architectural awareness

### 5.3 Security

*Production security is out of scope, but the README should discuss:*

- API key authentication (mentioned, not implemented)
- Service account least-privilege for BigQuery access
- HTTPS enforced by Cloud Run by default
- `.gitignore` includes all credential files
- No PII in sample data (all Faker-generated)

---

## 6. Technical Considerations

### 6.1 Architecture Overview

```
Firebase Studio (Dev) → Docker Container → Cloud Run (Prod)
                                              ├── FastAPI app (9 endpoints)
                                              ├── Request logging middleware
                                              ├── SQLite (embedded, operational)
                                              │     ↓  (future: ETL batch sync)
                                              │     ↓  (current: simulated via generate_data.py + bq load)
                                              └── BigQuery (analytical warehouse)
```

**Data pipeline flow:** Recruiter hits API → middleware logs request metadata → SQLite stores for real-time analytics → (ETL) → BigQuery enables analysis at 500K–5M+ row scale. The ETL layer is simulated in v1; future iterations add automated sync and load testing.

### 6.2 Integration Requirements

| System | Integration Type | Purpose |
|--------|------------------|---------|
| BigQuery | Python client library (`google-cloud-bigquery`) | Analytical queries on 500K+ rows |
| Cloud Run | Docker deployment via `gcloud` CLI | Production hosting |
| GitHub | Git push | Source control + portfolio visibility |

### 6.3 Data Requirements

| Data Entity | Source | Storage | Retention |
|-------------|--------|---------|-----------|
| Resume content | Hardcoded Python dict | In-memory (FastAPI) | Permanent (in code) |
| Analytics (10K rows) | Faker-generated | SQLite file (analytics.db) | Life of project |
| Analytics (500K rows) | Faker-generated CSV | BigQuery table | Life of project |

### 6.4 Technical Constraints

- **No billing overages:** Budget alert at $1, max 1 Cloud Run instance, BigQuery free tier (1TB queries/month)
- **Firebase Studio ephemeral environment:** Work must be committed to Git regularly; workspace may reset
- **AI-assisted development:** Gemini generates implementation code; the author designs architecture, reviews, and validates
- **Time constraint:** Must be buildable in ≤12 hours across 1-2 sessions

---

## 7. UX/UI Requirements

*This project is API-only with no custom frontend. The "UX" is:*

| Interface | Purpose | Key Elements | Priority |
|-----------|---------|--------------|----------|
| FastAPI Swagger UI (/docs) | Interactive API documentation | Try-it-out buttons, schema display | P1 |
| GitHub README | Primary interface for technical readers | Architecture diagram, design decisions, screenshots | P0 |
| curl / terminal output | Demonstration of working endpoints | JSON responses with proper formatting | P0 |

---

## 8. Pricing & Monetization

*Not applicable — this is a free portfolio project, not a commercial product.*

*For reference, the infrastructure cost model:*

| Service | Free Tier Allowance | Projected Usage | Cost |
|---------|-------------------|-----------------|------|
| Cloud Run | 2M requests/month | ~100 requests | $0.00 |
| BigQuery Queries | 1 TB/month | ~2 GB | $0.00 |
| BigQuery Storage | 10 GB | ~500 MB | $0.00 |
| Artifact Registry | 500 MB | ~200 MB | $0.00 |
| Cloud Build | 120 min/day | ~5 min | $0.00 |
| **Total** | | | **$0.00** |

---

## 9. Go-to-Market

*Not a commercial launch. Distribution channels:*

| Channel | Purpose | Priority |
|---------|---------|----------|
| GitHub public repo | Portfolio visibility; shareable link | P0 |
| LinkedIn project section | *Optional — professional visibility* | P2 |

---

## 10. Success Criteria & KPIs

### 10.1 Activation Metric

- **Activation Event:** All 9 endpoints return valid JSON from the live Cloud Run URL
- **Target:** 100% pass rate

### 10.2 North Star Metric

**The builder can articulate design decisions for any component in under 60 seconds.**

### 10.3 Supporting Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| All endpoints return valid JSON | 9/9 | curl tests |
| All 3 SQL tiers execute in BigQuery | 3/3 | BigQuery console |
| README readable in <2 minutes | Yes | Self-timed read-through |
| Total cost | $0.00 | GCP billing console |
| Build time | ≤12 hours | Time tracking |

---

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Accidental cloud charges | Low | High (financial) | $1 budget alert, max-instances=1, delete resources when done |
| Firebase Studio workspace resets mid-build | Medium | Medium | Commit to GitHub every 30 minutes |
| Cloud Run deployment fails | Medium | Low (can demo locally) | Test Docker locally first; have screenshots as backup |
| BigQuery free trial expires | Low | Medium | BigQuery Sandbox (no billing) works for queries |
| Project takes longer than 12 hours | Medium | Medium | Cut list: Skip Cloud Run → Skip Tier 3 SQL → NEVER skip README |
| Gemini generates incorrect code | Medium | Low | Review all generated code; test every endpoint manually |

---

## 12. Timeline & Milestones

| Phase | Milestone | Target Duration | Dependencies |
|-------|-----------|-----------------|--------------|
| Phase 0 | GCP account + billing safeguards configured | 30 min | Google account |
| Phase 1 | Firebase Studio workspace running with dependencies | 15 min | Phase 0 |
| Phase 2 | All 9 API endpoints working locally | 2-3 hrs | Phase 1 |
| Phase 3 | BigQuery dataset loaded, 3 SQL tiers documented, scale benchmarks (10K→500K→5M) run with screenshots | 2-3 hrs | Phase 0 (BigQuery API enabled) |
| Phase 4 | Docker build + Cloud Run deploy successful | 1-2 hrs | Phase 2 |
| Phase 5 | README complete with screenshots, pushed to GitHub | 2-3 hrs | Phases 2-4 |
| Phase 6 | All screenshots captured and organized | 30 min | Phases 2-5 |
| **Total** | **Project complete** | **8-12 hrs** | |

---

## 13. Open Questions

| Question | Owner | Status |
|----------|-------|--------|
| Should the API connect to BigQuery directly, or keep BQ as a separate demo? | Author | **Decided:** BQ stays as a separate demo — benchmark scripts compare approaches outside the API |
| Should there be a `/analytics/compare` endpoint that queries both SQLite and BQ? | Author | **Decided:** No — the scale benchmark scripts (benchmark_small/medium/large.py) serve this comparison purpose more effectively than an API endpoint |
| Should Tier 3 scale to 50M rows using CROSS JOIN? | Author | **Decided:** Scale to 5M rows via CROSS JOIN (500K × 10). 5M is sufficient to demonstrate partition pruning and the Python→BigQuery crossover. See Steps 3.7-3.8 in the implementation guide |
| Should the ETL pipeline (SQLite → BigQuery) be fully implemented in v1? | Author | **Decided:** No — simulate via `generate_data.py` + `bq load`. The ETL infrastructure (Cloud Functions, scheduling) adds complexity without demonstrating additional SQL/API skills. Future iterations (v2) add automated ETL; v3 adds load testing to generate organic data through the full pipeline. |

---

## 14. Appendices

### 14.1 References

- Domain context: Technical solutions work in ad tech / data engineering
- Study resources: API design, Linux, Python, SQL guides
- Firebase Studio research: Billing vs. no-billing comparison and implementation plans

### 14.2 Skills Demonstrated

| Skill Area | How Demonstrated |
|-----------|-----------------|
| REST API Design | 9 endpoints with resource modeling, query params, status codes, Swagger docs |
| Linux Proficiency | Full CLI development and deployment with ps, ss, grep, kill, docker, gcloud |
| Python Data Structures | Dictionary frequency map + Counter, both implemented in /analytics/top-domains |
| BigQuery / SQL | 3-tier progression: naive → CTE/window functions → partitioned/clustered. Scale benchmarks at 10K, 500K, and 5M rows comparing Python, SQLite, and BigQuery |
| Data Engineering | CROSS JOIN for SQL-native test data generation (500K → 5M). Benchmark framework measuring time, memory, and bytes scanned across tools and scales |
| Ad Tech Domain | Data model mirrors advertising reporting patterns (advertiser, campaign, keyword) |
| Cloud Deployment | Docker containerization → Cloud Run serverless hosting |
| Documentation | Comprehensive README with architecture, design decisions, trade-offs |
