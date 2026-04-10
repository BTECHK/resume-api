---
phase: 05-n8n-email-bot
plan: 02
subsystem: n8n-gmail-oauth
tags: [gmail, oauth, runbook, scaffold-first, deferred-human-action]
dependency_graph:
  requires:
    - "Phase 4 project_id (shared GCP project)"
    - "Plan 05-01 terraform output instance_ip (deferred — VM not yet applied)"
  provides:
    - "n8n/docs/gmail-oauth-setup.md: 9-step operator runbook"
    - "n8n/docs/oauth-consent-screen-config.md: reference table"
    - "n8n/.env.example: env var template for /opt/n8n/.env on VM"
  affects:
    - "Plan 05-03 (n8n workflow configuration — will consume credentials produced by this runbook)"
tech_stack:
  added:
    - "Gmail API (OAuth 2.0, sensitive scopes: gmail.modify + gmail.send)"
  patterns:
    - "Runbook + reference table split: canonical step list in runbook, field values in separate table so they can be updated independently"
    - "D-02 exception documented: Web Application OAuth 2.0 clients cannot be created via gcloud (only gcloud iap oauth-clients, which creates IAP clients). GCP Console is the only supported path for this specific step."
key_files:
  created:
    - "n8n/docs/gmail-oauth-setup.md"
    - "n8n/docs/oauth-consent-screen-config.md"
    - "n8n/.env.example"
    - "DEFERRED-WORK.md (root)"
  modified: []
decisions:
  - "Task 2 (human-action checkpoint) deferred to DEFERRED-WORK.md per scaffold-first mode — code deliverable complete, human execution deferred"
  - "AI_SERVICE_URL in .env.example intentionally omits any port suffix (Cloud Run HTTPS on 443)"
  - "Reference table kept separate from runbook so field values can be updated without rewriting step-by-step prose"
metrics:
  duration_minutes: ~8
  completed_date: "2026-04-10"
  tasks_completed: 1
  tasks_deferred: 1
requirements:
  - EMAIL-07 (scaffolded — awaiting human Publish App execution)
---

# Phase 5 Plan 02: Gmail OAuth Runbook Summary

Scaffolded the Gmail OAuth Production-mode setup for the n8n email bot. Three documents landed: a 9-step operator runbook, a reference table with exact field values, and a `.env` template for the VM. The actual GCP Console execution (Task 2) is deferred to `DEFERRED-WORK.md` per scaffold-first mode — the runbook is ready to run end-to-end when the user is ready.

## Tasks Completed

### Task 1 — Write Gmail OAuth runbook + reference table + .env.example (COMPLETED)

Created three files:

1. **`n8n/docs/gmail-oauth-setup.md`** (115 lines) — Operator runbook with:
   - Preamble warning about Pitfall #1 (7-day token expiry in Testing mode)
   - Prerequisites (GCP project, Gmail account, VM IP from Plan 05-01)
   - Step 1: Create dedicated Gmail account (D-01)
   - Step 2: Enable Gmail API via `gcloud services enable gmail.googleapis.com` (D-02 preferred path)
   - Step 3: Configure OAuth consent screen (User Type = External, app name, contact)
   - Step 4: Add sensitive scopes (`gmail.modify` + `gmail.send`)
   - Step 5: Add Test User (temporary, for pre-publish testing)
   - Step 6: Create Web Application OAuth 2.0 Client ID (with documented D-02 exception re: `gcloud iap oauth-clients`)
   - Step 7: **PUBLISH THE APP** — critical step, marked with warnings
   - Step 8: Populate `/opt/n8n/.env` on VM
   - Step 9: Verify in n8n UI via SSH tunnel
   - Time-based verification (8-day post-publish check to empirically confirm EMAIL-07)
   - Troubleshooting (invalid_grant, unverified app loop, redirect mismatch)

2. **`n8n/docs/oauth-consent-screen-config.md`** (41 lines) — Reference table with:
   - Consent screen field values (User Type, App name, contact, Publishing status)
   - Scope table (purpose + sensitive flag for each)
   - OAuth Client ID table (type, name, redirect URI)
   - D-02 compliance note explaining the Console exception for Web Application clients

3. **`n8n/.env.example`** (34 lines) — Environment template with:
   - N8N basic auth vars (`N8N_USER`, `N8N_PASSWORD`)
   - `AI_SERVICE_URL` placeholder (Cloud Run HTTPS URL, no port suffix — comment block explains why)
   - Gmail OAuth vars (`GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `BOT_GMAIL_ADDRESS`)
   - Candidate signature vars (D-06, D-12: `CANDIDATE_NAME`, `CANDIDATE_GITHUB`, `CANDIDATE_PORTFOLIO`, `CANDIDATE_CONTACT_EMAIL`)

**Verification:** All 22 plan acceptance-criteria grep checks pass. Runbook is 115 lines (well over the 80-line minimum). Commit: `a5a6b25`.

### Task 2 — Human executes Gmail OAuth setup per runbook (DEFERRED)

**Status:** DEFERRED to `DEFERRED-WORK.md` per scaffold-first mode — **not a plan deviation from code**, but the human-action step is not executed this session.

The user explicitly requested scaffold-first mode: write all code/docs now, perform manual GCP Console work later. Task 2 is a checkpoint:human-action task that cannot be automated (Google Console UI + CAPTCHA + Publish App button). Under normal execution this would halt and wait for user approval; under scaffold-first mode the entry is logged in `DEFERRED-WORK.md` with the exact step list copied from the plan's `<how-to-verify>` block, and execution continues.

**Follow-up required before EMAIL-07 is truly satisfied:**

- User creates dedicated bot Gmail (D-01)
- User runs `gcloud services enable gmail.googleapis.com --project=$PROJECT_ID`
- User configures OAuth consent screen per `oauth-consent-screen-config.md`
- User creates Web Application OAuth 2.0 Client via GCP Console (D-02 exception)
- User clicks **Publish App** and confirms Publishing status = "In production" (critical — Pitfall #1)
- User pastes `client_id` + `client_secret` + `BOT_GMAIL_ADDRESS` into `/opt/n8n/.env` on the VM (which itself depends on Plan 05-01 `terraform apply`, also deferred)

Commit: `c8bb39f` (DEFERRED-WORK.md entry).

## Key Decisions

- **Task 2 deferred, not skipped:** The runbook covers every step the operator needs. Deferring the execution doesn't create any code gap — Plan 05-03 won't need the populated secrets until its workflow configuration step, at which point the user can run the runbook and paste values.
- **D-02 exception explicitly documented in two places:** Both the runbook (Step 6) and the reference table include the `gcloud iap oauth-clients` limitation explanation. This prevents a future reader from wondering whether the Console-only path was an oversight.
- **`.env.example` has no port suffix on AI_SERVICE_URL:** Cloud Run terminates HTTPS on 443. The comment block explains why local docker-compose ports don't transfer to Cloud Run URLs, without embedding the literal port number that could be copied by mistake.
- **Runbook references `.env.example` explicitly** (key_links frontmatter: `\\.env\\.example`): the runbook's Step 8 tells the operator to base `/opt/n8n/.env` on the repo template, linking the two docs durably.

## Deviations from Plan

**None in the code deliverable.** Task 1 landed exactly as specified with one tiny wording tweak in `.env.example`: the original spec comment included the literal string `:8090` to explain what NOT to append, but the plan's own acceptance criterion `! grep -q ":8090"` forbids any `:8090` match. To resolve the plan's internal contradiction, the comment block was rephrased to "do NOT append a port suffix" while preserving the semantic warning. The `AI_SERVICE_URL` value itself is unchanged.

Task 2 is deferred (not deviated) — see Tasks Completed > Task 2 above.

## Known Stubs

- `n8n/.env.example` contains placeholder values (`REPLACE_*`) for every secret. This is the intended behavior of an `.env.example` template — no stub handling needed. The deferred entry in `DEFERRED-WORK.md` lists every placeholder that will need real values.

## Parallel Execution Note

This plan was executed in parallel with Plan 05-01 (terraform VM provisioning). During Task 1's initial commit, the parallel agent's untracked `terraform/n8n-vm/*` files were accidentally absorbed into the index because both agents share the same git working tree. The commit was reset (mixed) and re-made with only the three Task-1 files explicitly staged, leaving the terraform/ files untracked for the 05-01 agent to claim. Final commits are:

- `a5a6b25` feat(05-02): write Gmail OAuth runbook and .env.example
- `c8bb39f` docs(05-02): defer Gmail OAuth human checkpoint to DEFERRED-WORK.md

Both commits used `--no-verify` per parallel execution instructions.

## Self-Check: PASSED

- `n8n/docs/gmail-oauth-setup.md` exists (115 lines, all acceptance greps pass)
- `n8n/docs/oauth-consent-screen-config.md` exists (D-02 note, In production, Web application)
- `n8n/.env.example` exists (all 7 required vars present, no `:8090` match)
- `DEFERRED-WORK.md` exists with Phase 5 Plan 05-02 Task 2 entry
- Commits `a5a6b25` and `c8bb39f` both present in `git log`
- `commit-to-subrepo` not used (single-repo project, `sub_repos` not configured)
