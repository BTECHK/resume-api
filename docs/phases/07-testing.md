# Phase 7: Differentiators + Testing

**Status:** Done ✅ — 61 local + 25 CI-gated tests (2026-04-11)
**Goal:** Add interview-impressive capabilities (two-tier RAG, architecture self-awareness, unanswered-question logging) and put an 80%-target test suite behind them.

## Architecture
![testing diagram](../diagrams/phase-07.png)
<!-- diagram file: docs/diagrams/phase-07.drawio -->
*ai-service retrieves from two Chroma collections (Tier 1 facts, Tier 2 patterns/ADRs); weak matches are appended to a JSONL unanswered log; pytest suites cover unit, integration, and endpoint-level security with a 70% coverage gate.*

## What was built
- Two-tier RAG retrieval: Tier 1 resume facts kept separate from Tier 2 interview patterns and embedded ADR content
- Architecture self-awareness: ADR content embedded into the corpus so the bot can explain its own design
- JSONL unanswered-question logging for weak-match queries — feeds future KB improvements
- 86 total tests across unit / integration / endpoint security — [`ai-service/tests/`](../../ai-service/tests/)
- 70% coverage gate enforced in CI (pytest-cov) — [`ai-service/pytest.ini`](../../ai-service/pytest.ini)
- Security tests: prompt-injection detection, rate-limit triggering, oversized-input rejection (422)

## Key decisions
| Decision | Rationale | Reference |
|---|---|---|
| Two Chroma collections, not one | Prevents interview-pattern text from contaminating factual answers | [ADR-0010](../adrs/0010-two-tier-rag.md) |
| JSONL file log, not DB, for unanswered | Zero infra; trivial to review; append-only friendly | [ADR-0011](../adrs/0011-jsonl-unanswered-logging.md) |
| 70% gate (not 80%) | Pragmatic — matches what's actually meaningful to test vs vanity coverage | [pytest.ini](../../ai-service/pytest.ini) |
| Split 61 local + 25 CI-gated | CI-gated tests need GCP creds / network | [ai-service/tests/](../../ai-service/tests/) |

## What I learned
- Mixing tiers in a single collection caused Tier 2 prose to bleed into Tier 1 answers — splitting collections was the clean fix.
- "Unanswered" is a more useful signal than raw query logs — the bot's weak-match threshold is the product, not just a tuning knob.
- Aiming for 80% coverage produced low-value tests; capping at 70% and investing in endpoint-level security tests was a better use of time.

## Links
- Source: [`ai-service/tests/`](../../ai-service/tests/), [`ai-service/unanswered.py`](../../ai-service/unanswered.py)
- Related ADRs: [ADR-0010](../adrs/0010-two-tier-rag.md), [ADR-0011](../adrs/0011-jsonl-unanswered-logging.md)
- Next: [Phase 8](./08-cicd-hardening.md)
