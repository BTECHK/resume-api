---
phase: 05-n8n-email-bot
plan: 03
subsystem: n8n-workflow
tags: [n8n, gmail, workflow, ai-service, scaffold-first]
dependency-graph:
  requires:
    - "05-01 (n8n VM Terraform module)"
    - "05-02 (Gmail OAuth runbook scaffold)"
    - "ai-service /chat endpoint (Phase 4)"
  provides:
    - "n8n/workflows/email-bot.json (EMAIL-02, EMAIL-03, EMAIL-04 scaffold)"
    - "n8n/workflows/error-handler.json (D-16)"
    - "workflow build guide + import runbook"
  affects:
    - "ai-service integration surface (calls POST /chat)"
    - "n8n/.env runtime env var contract"
tech-stack:
  added:
    - "n8n v1.123.29 workflow JSON format (nodes, connections, settings)"
  patterns:
    - "Gmail Trigger → Filter → Code → HTTP Request → dual Gmail Send branches"
    - "continueErrorOutput fallback branch (D-12, EMAIL-04)"
    - "Error Trigger workflow as main workflow's errorWorkflow (D-16)"
key-files:
  created:
    - "n8n/workflows/email-bot.json"
    - "n8n/workflows/error-handler.json"
    - "n8n/docs/workflow-build-guide.md"
    - "n8n/docs/workflow-import-runbook.md"
  modified:
    - "DEFERRED-WORK.md (appended Plan 05-03 Task 2 entry)"
decisions:
  - "D-14 override: use /chat endpoint (not /ai/ask) for thread-aware conversations"
  - "AI_SERVICE_URL is raw Cloud Run HTTPS URL — no :8090 port suffix"
  - "Single-message MVP; thread history fetching deferred to Phase 5.5+"
  - "Placeholder credential IDs REPLACE_AFTER_IMPORT on all Gmail nodes (Pitfall #5)"
  - "Filter node uses AND-combinator with 6 conditions (self-loop, auto-reply, auto-submitted, body-empty, promotions, updates)"
metrics:
  duration: "~30 min"
  completed: "2026-04-10"
  tasks-completed: 1
  tasks-deferred: 1
---

# Phase 5 Plan 03: n8n Email Bot Workflow Summary

**One-liner:** Authored the 7-node n8n Gmail → /chat → reply workflow JSON (plus 2-node error handler, build guide, and import runbook) honoring D-14 endpoint override and Cloud Run portless URL convention.

## Status

- **Task 1 (auto):** COMPLETE — workflow JSON + docs committed in `1ba4ea4`
- **Task 2 (checkpoint:human-verify):** DEFERRED to `DEFERRED-WORK.md` per scaffold-first session

## What Was Built

### Workflow Structure

**`n8n/workflows/email-bot.json`** — main email-bot workflow (7 nodes, INACTIVE):

| # | Node | Type | Encodes |
|---|------|------|---------|
| 1 | Gmail Trigger | `gmailTrigger` v1.2 | D-03 (5-min poll), INBOX+UNREAD filter, `-label:bot-replied` dedup |
| 2 | Filter: Skip Auto-Replies and Junk | `if` v2.2 | Pitfall #6 self-loop guard, D-13 (skip autoreplies/newsletters/empty bodies) |
| 3 | Build Chat Messages | `code` v2 (JS) | Constructs `{ messages: [{role:'user', content}] }`, truncates to 500 chars (ai-service SEC-03) |
| 4 | HTTP Request: ai-service /chat | `httpRequest` v4.2 | D-14 (/chat endpoint), D-12 (3 retries × 2s), `continueErrorOutput` for fallback branch |
| 5 | Gmail Send: AI Reply | `gmail` v2.1 | D-05 (plain text), D-06 (signature), D-07 (quoted original) |
| 6 | Gmail Send: Fallback Reply | `gmail` v2.1 | D-12 / EMAIL-04 polite apology + direct contact email |
| 7 | Label: Mark as Replied | `gmail` v2.1 | Dedup via `bot-replied` label; matches Gmail Trigger exclusion filter |

**`n8n/workflows/error-handler.json`** — separate error workflow (2 nodes, D-16):

| # | Node | Type | Purpose |
|---|------|------|---------|
| 1 | Error Trigger | `errorTrigger` v1 | Catches unhandled execution failures from main workflow |
| 2 | Gmail Send: Error Notification | `gmail` v2.1 | Emails `CANDIDATE_CONTACT_EMAIL` with workflow name, execution ID, URL, error |

Main workflow `settings.errorWorkflow = "email-bot-error-handler"` — operator must re-link this via UI after import (n8n does not auto-link by name).

### Documentation

- **`n8n/docs/workflow-build-guide.md`** (206 lines) — node-by-node walkthrough, decision traceability (D-03..D-16), env var reference table, prominent callout box reinforcing the D-14 `/chat` override and the no-`:8090` rule.
- **`n8n/docs/workflow-import-runbook.md`** (218 lines) — 10-step post-import runbook including SSH tunnel, Gmail label creation, OAuth2 credential setup, import order (error handler first), Pitfall #5 credential re-linking on all 4 Gmail nodes, error workflow registration, manual dry-run, and troubleshooting (404 on /chat, 429 rate limit, invalid_grant, OOM 137).

## Decisions Made

1. **D-14 /chat override honored throughout.** REQUIREMENTS.md §EMAIL-03 says "/ai/ask", but D-14 supersedes that text for thread-aware conversations. Every HTTP Request reference, build-guide mention, and runbook troubleshooting entry uses `/chat`. Acceptance check `! grep -q "/ai/ask" n8n/workflows/email-bot.json` passes (0 matches).

2. **AI_SERVICE_URL has no port suffix.** RESEARCH.md Code Examples show `http://ai-service:8090/chat` because those are local docker-compose examples. In Phase 5 the VM calls the Cloud Run HTTPS URL on implicit 443. The HTTP Request node URL is exactly `={{ $env.AI_SERVICE_URL }}/chat`. Acceptance check `! grep -q ":8090" n8n/workflows/email-bot.json` passes (0 matches). Build guide and import runbook both include prominent warnings.

3. **Single-message MVP for /chat.** The Code node emits exactly one `{ role: 'user', content: ... }` message per email. Thread history fetching (Gmail Thread > Get + message array construction) is deferred to Phase 5.5+ as a future enhancement. The ai-service contract allows up to 10 messages with last-must-be-user; the MVP stays comfortably within that.

4. **Placeholder credential IDs + Pitfall #5 runbook step.** All 4 Gmail nodes in the main workflow and the 1 Gmail node in the error handler use `credentials.gmailOAuth2.id = "REPLACE_AFTER_IMPORT"`. Step 7 of the import runbook explicitly walks the operator through re-selecting `Gmail Bot Account` on each node — this is expected n8n behavior on JSON export.

5. **Filter node uses loose typing + AND combinator** with 6 conditions: self-loop guard, `x-auto-reply-type` empty, `auto-submitted` equals `no`, body not empty, not in CATEGORY_PROMOTIONS, not in CATEGORY_UPDATES. `labelIds` comparisons are done by joining the array to a CSV string and checking `notContains` since n8n IF v2.2 does not have a native array-contains operator without additional configuration.

## Env Vars Required at Runtime

Populated from `/opt/n8n/.env` on the VM (template: `n8n/.env.example`):

| Variable | Consumer |
|----------|----------|
| `AI_SERVICE_URL` | HTTP Request node (Cloud Run URL, no port) |
| `BOT_GMAIL_ADDRESS` | Filter node (self-loop guard) |
| `CANDIDATE_NAME` | AI Reply + Fallback Reply signature |
| `CANDIDATE_GITHUB` | AI Reply + Fallback Reply signature |
| `CANDIDATE_PORTFOLIO` | AI Reply + Fallback Reply signature |
| `CANDIDATE_CONTACT_EMAIL` | Fallback Reply body + Error Handler recipient |

Plus n8n-native: `N8N_USER`, `N8N_PASSWORD` (UI basic auth), and Gmail OAuth creds (`GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`) consumed by the n8n credential system, not the workflow JSON.

## Known Phase 5.5+ Enhancement

**Thread history fetching** — the Code node currently builds a single-message array. A future enhancement can insert a Gmail `thread.get` call before Build Chat Messages, iterate prior messages to construct a user/assistant conversation history (capped at 9 pairs + 1 final user message), and pass the full context to `/chat`. The ai-service `/chat` endpoint already supports up to 10 messages (CHAT-04 / D-06 on the ai-service side). Adding this later is a code-node-only change; no other workflow edits needed.

## Deviations from Plan

**None.** Plan executed exactly as written. The plan's `<action>` block and override warnings were followed byte-for-byte:
- D-14 `/chat` override honored
- No `:8090` port suffix anywhere
- 7 nodes in the main workflow, exact names matching the connections object
- Position coordinates on the left-to-right grid (x = 250, 470, 690, 910, 1130, 1350; y = 300 main line with 220/500 for the reply branches)
- All required env var references present

## Task 2 DEFERRED to DEFERRED-WORK.md

**Task 2 (checkpoint:human-verify, blocking)** — Import workflow JSON to running n8n and verify it executes without errors — **DEFERRED**.

Per scaffold-first session mode, this checkpoint is **not** halted on. Instead, a full entry was appended to `DEFERRED-WORK.md` under the existing "Phase 5 — Deferred Manual Steps" section (after the Plan 05-02 Task 2 entry). The entry contains:

- Why deferred (requires running n8n on deployed VM; depends on Plan 05-01 `terraform apply` + Plan 05-02 OAuth + Phase 4 ai-service deployment)
- All 11 steps from the plan's `<how-to-verify>` block
- Prerequisite ordering
- Files with placeholders waiting (`REPLACE_AFTER_IMPORT` credential IDs on both JSON files)
- Acceptance criteria to verify on resolution
- Unchecked `[ ] Completed on: ____` checkbox

The deferred-work entry is a verbatim copy of the `<how-to-verify>` checklist, so when the operator is ready to resolve it, they can follow DEFERRED-WORK.md without re-reading the plan.

## Auth Gates

None encountered during Task 1 (pure file authoring — no network, no tools requiring auth).

## Files Changed

### Created (4)
- `n8n/workflows/email-bot.json` (302 lines, valid JSON, 7 nodes)
- `n8n/workflows/error-handler.json` (62 lines, valid JSON, 2 nodes)
- `n8n/docs/workflow-build-guide.md` (206 lines)
- `n8n/docs/workflow-import-runbook.md` (218 lines)

### Modified (1)
- `DEFERRED-WORK.md` — appended Plan 05-03 Task 2 entry (preserved existing Plan 05-02 Task 2 entry exactly)

## Verification Results

All automated acceptance criteria in the plan passed:

```
python -c "import json; json.load(open('n8n/workflows/email-bot.json'))"      → VALID JSON
python -c "import json; json.load(open('n8n/workflows/error-handler.json'))"  → VALID JSON
grep "gmailTrigger" n8n/workflows/email-bot.json                              → 1 match
grep "n8n-nodes-base.if" n8n/workflows/email-bot.json                         → 1 match
grep "n8n-nodes-base.code" n8n/workflows/email-bot.json                       → 1 match
grep "n8n-nodes-base.httpRequest" n8n/workflows/email-bot.json                → 1 match
grep -c "n8n-nodes-base.gmail\"" n8n/workflows/email-bot.json                 → 3 (AI Reply + Fallback + Label)
grep "AI_SERVICE_URL" n8n/workflows/email-bot.json                            → 1 match
grep "/chat" n8n/workflows/email-bot.json                                     → 6 matches
! grep "/ai/ask" n8n/workflows/email-bot.json                                 → 0 matches (D-14 override enforced)
! grep ":8090" n8n/workflows/email-bot.json                                   → 0 matches (no port suffix leak)
grep "\"unit\": \"minutes\"" n8n/workflows/email-bot.json                     → 1 match (D-03)
grep "\"value\": 5" n8n/workflows/email-bot.json                              → 1 match
grep "maxTries" n8n/workflows/email-bot.json                                  → 1 match (D-12)
grep "BOT_GMAIL_ADDRESS" n8n/workflows/email-bot.json                         → 1 match (Pitfall #6)
grep "x-auto-reply-type" n8n/workflows/email-bot.json                         → 1 match
grep "CANDIDATE_CONTACT_EMAIL" n8n/workflows/email-bot.json                   → 1 match
grep "CANDIDATE_NAME" n8n/workflows/email-bot.json                            → 2 matches
grep "errorWorkflow" n8n/workflows/email-bot.json                             → 1 match (D-16)
grep "errorTrigger" n8n/workflows/error-handler.json                          → 1 match
grep "CANDIDATE_CONTACT_EMAIL" n8n/workflows/error-handler.json               → 1 match
grep "Gmail Trigger" n8n/docs/workflow-build-guide.md                         → 3 matches
grep "D-14" n8n/docs/workflow-build-guide.md                                  → 4 matches
grep "credentials" n8n/docs/workflow-import-runbook.md                        → 2 matches
grep "bot-replied" n8n/docs/workflow-import-runbook.md                        → 4 matches
wc -l workflow-build-guide.md                                                 → 206 (>= 50)
wc -l workflow-import-runbook.md                                              → 218 (>= 30)
```

## Commits

- `1ba4ea4` — `feat(05-03): author n8n email-bot workflow JSON and docs` (4 files, +797 lines)
- (pending) — `docs(05-03): defer n8n workflow import checkpoint` (DEFERRED-WORK.md + SUMMARY.md + STATE.md)

## Next Steps

- **Plan 05-04** — smoke tests + phase summary (final Phase 5 plan)
- **When VM is live:** Resolve Plan 05-03 Task 2 entry in DEFERRED-WORK.md by following `n8n/docs/workflow-import-runbook.md`

## Self-Check: PASSED

- All 4 created files exist on disk (verified via filesystem check)
- SUMMARY.md exists at `.planning/phases/05-n8n-email-bot/05-03-SUMMARY.md`
- DEFERRED-WORK.md exists with both Plan 05-02 Task 2 (preserved) and Plan 05-03 Task 2 (appended) entries
- Commit `1ba4ea4` confirmed in `git log`
- All automated acceptance grep checks passed (see Verification Results section)
