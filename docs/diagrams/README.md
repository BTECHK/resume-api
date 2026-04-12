# Diagrams

These are draw.io source files (plain XML) for architecture and per-phase diagrams.

## Editing and exporting

Open in https://app.diagrams.net or the VS Code "Draw.io Integration" extension. Export to PNG via File -> Export as -> PNG, save next to the `.drawio` with the same basename.

## Files

| File | Depicts |
| --- | --- |
| `architecture.drawio` | Main README system diagram: GitHub -> Actions -> Artifact Registry -> Cloud Run services, data stores, and externals |
| `phase-01.drawio` | Core API + Analytics with 3 SQL optimization tiers |
| `phase-02.drawio` | Data Pipeline on e2-micro VM: SQLite, APScheduler ETL, BigQuery, Locust |
| `phase-03.drawio` | IaC (Terraform) + GitHub Actions CI/CD pipeline |
| `phase-04.drawio` | RAG core service: ai-service, security middleware, Chroma, Gemini, Secret Manager |
| `phase-05.drawio` | Email bot: Gmail + n8n + ai-service with fallback path |
| `phase-06.drawio` | React frontend on Cloud Run (nginx) calling ai-service |
| `phase-07.drawio` | Testing pyramid with 70% coverage gate and 61 local + 25 CI split |
| `phase-08.drawio` | CI/CD hardening: OIDC + WIF, short-lived creds, container security + Trivy gate |
