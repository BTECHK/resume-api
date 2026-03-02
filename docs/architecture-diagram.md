# Resume API — Architecture Diagram

## System Overview

```mermaid
graph TB
    subgraph "GitHub"
        GH[GitHub Repository]
        GA[GitHub Actions]
    end

    subgraph "GCP - Networking"
        VPC[VPC Network]
        FW[Firewall Rules]
    end

    subgraph "GCP - Compute"
        CR[Cloud Run<br/>API Service]
        VM[e2-micro VM<br/>ETL + Traffic Sim]
    end

    subgraph "GCP - Data"
        BQ[BigQuery<br/>Analytics Warehouse]
        AR[Artifact Registry<br/>Docker Images]
    end

    subgraph "GCP - Security"
        IAM[IAM<br/>Service Accounts]
        SM[Secret Manager<br/>API Keys]
    end

    subgraph "AI Layer"
        CH[Chroma<br/>Vector DB]
        GEM[Gemini API<br/>AI Generation]
    end

    subgraph "External"
        USER[Users / Recruiters]
    end

    USER -->|HTTPS| CR
    CR -->|Analytics queries| BQ
    CR -->|Similarity search| CH
    CR -->|RAG generation| GEM
    CH -->|Relevant chunks| CR

    GH -->|Push triggers| GA
    GA -->|terraform apply| VPC
    GA -->|docker push| AR
    AR -->|Deploy image| CR

    VM -->|ETL sync| BQ
    VM -->|Traffic sim| CR

    VPC --> CR
    VPC --> VM
    FW --> VPC

    IAM -->|Least privilege| CR
    IAM -->|Least privilege| VM
    SM -->|GOOGLE_API_KEY| CR
```

## Data Flow: AI Resume Q&A

```mermaid
sequenceDiagram
    participant U as User
    participant CR as Cloud Run API
    participant CH as Chroma VectorDB
    participant GEM as Gemini API
    participant BQ as BigQuery

    U->>CR: POST /ai/ask {"question": "What databases has the candidate used?"}
    CR->>CH: Similarity search (query embedding)
    CH-->>CR: Top 3 relevant resume chunks
    CR->>GEM: System prompt + context chunks + question
    GEM-->>CR: Generated answer with citations
    CR-->>U: {"answer": "...", "sources": [...], "model": "gemini-2.5-flash"}

    Note over CR,BQ: Request logged via middleware
    CR->>BQ: Log request metrics (async ETL)
```

## Data Flow: Analytics Pipeline

```mermaid
sequenceDiagram
    participant R as Recruiter
    participant API as FastAPI (Cloud Run)
    participant MW as Logging Middleware
    participant SQ as SQLite (Operational)
    participant ETL as ETL Scheduler (VM)
    participant BQ as BigQuery (Analytical)

    R->>API: GET /resume/skills?keyword=sql
    API->>MW: Capture request metadata
    MW->>SQ: Write log row (domain, endpoint, skill, latency, status)
    API-->>R: {"technical_development": ["SQL..."]}

    Note over ETL,BQ: Scheduled batch sync
    ETL->>SQ: Read new rows since last sync
    ETL->>BQ: Batch insert to recruiter_queries table
    Note over BQ: Now queryable at scale (500K+ rows)
```

## CI/CD Pipeline

```mermaid
flowchart LR
    subgraph "CI Pipeline (Every Push/PR)"
        A[Push / PR] --> B[Ruff Lint]
        B --> C[Bandit SAST]
        C --> D[pip-audit SCA]
        D --> E[pytest]
        E --> F{All Pass?}
    end

    subgraph "CD Pipeline (Main Branch Only)"
        F -->|Yes + main| G[Terraform Plan]
        G --> H[Terraform Apply]
        H --> I[Docker Build]
        I --> J[Push to Artifact Registry]
        J --> K[Deploy to Cloud Run]
    end

    F -->|No| L[❌ Build Fails]
    F -->|Yes + PR| M[✅ PR Checks Pass]
```

## Security Layers

```mermaid
graph TB
    subgraph "Layer 1: Code Quality"
        A1[Pydantic Input Validation]
        A2[Type Hints + mypy]
        A3[Ruff Linting]
    end

    subgraph "Layer 2: Application Security"
        B1[Rate Limiting<br/>100 req/min per IP]
        B2[Security Headers<br/>X-Content-Type-Options, X-Frame-Options, etc.]
        B3[CORS Restriction<br/>Explicit origin allowlist]
        B4[Error Sanitization<br/>No stack traces in production]
    end

    subgraph "Layer 3: Infrastructure Security"
        C1[VPC Firewall<br/>Allow only 22, 80, 443]
        C2[IAM Least Privilege<br/>Scoped service accounts]
        C3[Secret Manager<br/>No secrets in code]
        C4[Non-root Containers<br/>Minimal base images]
    end

    subgraph "Layer 4: CI/CD Security Gates"
        D1[SAST — Bandit<br/>Python code analysis]
        D2[SCA — pip-audit<br/>Dependency vulnerabilities]
        D3[Container Scan — Trivy<br/>Image CVEs]
        D4[IaC Scan — Trivy<br/>Terraform misconfigurations]
        D5[Secret Detection<br/>detect-secrets pre-commit]
    end
```

## Component Responsibilities

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| Cloud Run | API hosting, auto-scaling, HTTPS termination | FastAPI, Docker, Uvicorn |
| e2-micro VM | ETL scheduler, traffic simulation (Locust) | Docker Compose, APScheduler |
| BigQuery | Analytics warehouse, scale queries (500K+ rows) | SQL (3-tier progression) |
| Artifact Registry | Docker image storage and versioning | Docker |
| Chroma | Vector similarity search for RAG | ChromaDB, HuggingFace embeddings |
| Gemini 2.5 Flash | AI text generation for resume Q&A | LangChain, Google AI |
| GitHub Actions | CI/CD automation (lint → scan → test → deploy) | YAML workflows |
| Terraform | Infrastructure as Code for all GCP resources | HCL modules |
| SQLite | Operational database for real-time analytics | Built-in Python |
| Secret Manager | Secure storage for API keys and credentials | GCP |

## Technology Stack Summary

```
Frontend / Client:  curl, Postman, Swagger UI (/docs)
API Framework:      FastAPI + Uvicorn (Python 3.11)
Databases:          SQLite (operational) + BigQuery (analytical) + Chroma (vector)
AI:                 Gemini 2.5 Flash + LangChain + HuggingFace all-MiniLM-L6-v2
Infrastructure:     Terraform (GCS remote state, modular HCL)
CI/CD:              GitHub Actions (CI: lint/scan/test, CD: build/deploy)
Security:           Bandit, pip-audit, Trivy, detect-secrets, OWASP alignment
Hosting:            Cloud Run (API) + e2-micro VM (ETL/traffic)
Container:          Docker + Artifact Registry
Cost:               $0.00/month (GCP Always Free + GitHub free tier)
```
