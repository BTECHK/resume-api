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
