# Phase 5: n8n Email Bot

**Status:** Scaffold Complete 🟡 — terraform apply + n8n workflow import deferred
**Goal:** A recruiter emails a dedicated inbox and gets an AI-generated reply within ~5 minutes via a self-hosted n8n workflow.

## Architecture
![email bot diagram](../diagrams/phase-05.png)
<!-- diagram file: docs/diagrams/phase-05.drawio -->
*Gmail inbox → n8n Gmail Trigger (5-min poll) on e2-micro VM → filter → POST ai-service `/chat` → Gmail reply; fallback reply when ai-service is unreachable.*

## What was built
- Terraform for GCE e2-micro VM with 2GB swap, Docker, systemd unit for n8n — [`.planning/phases/05-n8n-email-bot/`](../../.planning/phases/05-n8n-email-bot/)
- Gmail OAuth Production-mode runbook + `.env.example` (avoids 7-day token expiry)
- n8n workflow JSON design: Gmail Trigger → filter → `/chat` → reply + fallback + error handler
- GCP uptime check + end-to-end smoke test plan

## Key decisions
| Decision | Rationale | Reference |
|---|---|---|
| n8n on e2-micro, not Cloud Run | Persistent polling + OAuth state; always-on free tier | [ADR-0005](../adrs/0005-n8n-e2-micro.md) |
| 2GB swap on the VM | Keep Docker + n8n inside e2-micro memory budget | [ADR-0005](../adrs/0005-n8n-e2-micro.md) |
| 5-min Gmail poll (not 60s) | Quota headroom; accepted tradeoff vs original target | ROADMAP D-03 |
| Fallback reply path | Never leave recruiter with silence or a stack trace | [ROADMAP.md](../../.planning/ROADMAP.md) |

## What I learned
- Gmail OAuth in Testing mode revokes tokens every 7 days — moving to Production mode was mandatory for a truly unattended bot.
- The e2-micro memory ceiling is the real constraint; swap is not optional once n8n + Docker run together.

## Links
- Source: [`.planning/phases/05-n8n-email-bot/`](../../.planning/phases/05-n8n-email-bot/)
- Related ADR: [ADR-0005](../adrs/0005-n8n-e2-micro.md)
- Next: [Phase 6](./06-react-frontend.md)
