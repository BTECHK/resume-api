# Phase 6: React Chatbot Frontend

**Status:** In Progress 🟡 — local works, Cloud Run deploy + CORS swap pending
**Goal:** A polished recruiter-facing chat UI that talks to the ai-service `/chat` endpoint and renders well on mobile.

## Architecture
![react frontend diagram](../diagrams/phase-06.png)
<!-- diagram file: docs/diagrams/phase-06.drawio -->
*Browser loads Vite-built React SPA served by nginx on Cloud Run; SPA calls ai-service `/chat` directly over CORS-locked HTTPS.*

## What was built
- React 19 + Vite 8 + Tailwind v4 SPA with streaming-style chat UI — [`frontend/`](../../frontend/)
- Landing page with two CTAs: "Email My Resume" (mailto) and "Chat With My Resume"
- Multi-stage Dockerfile: Node build → nginx:1.27-alpine serve (non-root) — [`frontend/Dockerfile`](../../frontend/Dockerfile)
- Cloud Run deploy script — [`frontend/deploy.sh`](../../frontend/deploy.sh)
- Mobile-responsive layout (landing, chat bubbles, header, input)

## Key decisions
| Decision | Rationale | Reference |
|---|---|---|
| React 19 + Vite 8 + Tailwind v4 | Modern, fast HMR, utility-first styling | [ADR-0006](../adrs/0006-react-vite-tailwind.md) |
| nginx static container, not Node server | Smaller image, no runtime JS server needed | [frontend/Dockerfile](../../frontend/Dockerfile) |
| Direct CORS to ai-service (no proxy) | Simplicity; one less hop for a personal-scale site | [ADR-0012](../adrs/0012-direct-cors.md) |
| Cloud Run for the SPA too | Same deploy primitive as the API; scales to zero | [ADR-0006](../adrs/0006-react-vite-tailwind.md) |

## What I learned
- Tailwind v4 config surface changed enough from v3 that copying old configs wasted time; starting from the v4 docs was faster.
- Direct CORS is fine when you control both origins, but means any CORS mistake is visible to recruiters — the deploy ritual has to include a CORS smoke check.

## Links
- Source: [`frontend/`](../../frontend/)
- Related ADRs: [ADR-0006](../adrs/0006-react-vite-tailwind.md), [ADR-0012](../adrs/0012-direct-cors.md)
- Next: [Phase 7](./07-testing.md)
