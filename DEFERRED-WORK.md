# Deferred Work — Manual Steps Pending

Items scaffolded in code but awaiting live credentials, GCP Console clicks, or deployed services. Each entry has exact commands/UI steps. Resolve when ready, then tick the checkbox and commit.

## Phase 5 — Deferred Manual Steps

### Plan 05-02 Task 2: Execute Gmail OAuth setup

**Why deferred:** Scaffold-first session. User will do GCP Console clicks + Gmail account creation manually later. Runbook landed in `n8n/docs/gmail-oauth-setup.md`.

**Steps to complete later:**
1. Open `n8n/docs/gmail-oauth-setup.md` and follow all 9 steps
2. Publishing status MUST read "In production" at the end (Pitfall #1 — Testing mode = 7-day token death)
3. Save client_id, client_secret, BOT_GMAIL_ADDRESS into `/opt/n8n/.env` on the VM (not the repo)
4. Verify per <how-to-verify> checks in `.planning/phases/05-n8n-email-bot/05-02-PLAN.md`:
   - Gmail account exists and is reachable (send test email from personal Gmail)
   - `gcloud services list --enabled --filter="gmail.googleapis.com" --project=$PROJECT_ID` shows gmail.googleapis.com
   - GCP Console → OAuth consent screen: User type = External, App name = "Resume Bot Phase 5", scopes include gmail.modify AND gmail.send
   - GCP Console → Credentials: "n8n Gmail Client" (Web application) exists
   - GCP Console → OAuth consent screen: Publishing status = "In production" (NOT "Testing")
   - client_id, client_secret, BOT_GMAIL_ADDRESS pasted into /opt/n8n/.env on VM

**Depends on:** Plan 05-01 `terraform apply` (need VM IP for OAuth redirect URI) — also deferred.

**Files with placeholders waiting on this:**
- `n8n/.env.example` — `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `BOT_GMAIL_ADDRESS` all `REPLACE_*`

**[ ] Completed on: ____**

### Plan 05-03 Task 2: Import workflow JSON to live n8n and dry-run

**Why deferred:** Scaffold-first session. n8n UI import, OAuth credential re-linking (Pitfall #5), and Gmail Trigger manual execution all require a running n8n instance on the deployed VM — which is also deferred (depends on Plan 05-01 terraform apply). No automated equivalent exists for n8n 1.123.29.

**Prerequisites (must complete in order):**
1. Plan 05-01 Task deferred: `terraform apply` the VM
2. Plan 05-02 Task 2 deferred: Gmail OAuth Published + credentials in `/opt/n8n/.env`
3. ai-service deployed to Cloud Run (Phase 8 deliverable — currently deferred)

**Steps to complete later (from `n8n/docs/workflow-import-runbook.md`):**
1. SSH tunnel: `ssh -L 5678:localhost:5678 ubuntu@$(cd terraform/n8n-vm && terraform output -raw instance_ip)`
2. Verify: `sudo systemctl is-active n8n` → `active`
3. Double-check `/opt/n8n/.env` has real values — especially `AI_SERVICE_URL` must be the Cloud Run URL with NO `:8090` suffix
4. Log into http://localhost:5678, create Gmail label "bot-replied" in the bot Gmail web UI
5. Create Gmail OAuth2 credential in n8n named "Gmail Bot Account"
6. Import `n8n/workflows/error-handler.json` first, save it
7. Import `n8n/workflows/email-bot.json`, save but DO NOT activate
8. Re-link "Gmail Bot Account" credential on all 4 Gmail nodes (Pitfall #5)
9. Set Main Workflow → Settings → Error Workflow → `email-bot-error-handler`
10. Manually execute Gmail Trigger — confirm no red/error nodes
11. Leave workflow INACTIVE (activation is Plan 05-04 smoke test)

**Files with placeholders waiting on this:**
- `n8n/workflows/email-bot.json` — `credentials.gmailOAuth2.id = "REPLACE_AFTER_IMPORT"` on Gmail nodes
- `n8n/workflows/error-handler.json` — same placeholder

**Acceptance criteria to verify later:**
- 7 nodes visible in email-bot canvas
- 2 nodes in error-handler canvas
- Gmail OAuth2 credential "Gmail Bot Account" linked to all 4 Gmail nodes
- Workflow Settings → Error Workflow = email-bot-error-handler
- Manual Gmail Trigger execution succeeds (0 items is OK if inbox is empty)

**[ ] Completed on: ____**
