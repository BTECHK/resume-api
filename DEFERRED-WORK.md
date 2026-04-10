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

### Plan 05-04 Task 3: Execute end-to-end smoke test + provision uptime check

**Why deferred:** Scaffold-first session. This is the final Phase 5 phase gate — requires (a) a running deployed VM, (b) Gmail OAuth Published with live credentials, (c) ai-service `/chat` live on Cloud Run, (d) sending real emails and waiting for real AI replies, (e) a live `sudo reboot` of the VM. None of the live infrastructure exists yet.

**Prerequisites (must ALL be resolved first):**
1. Phase 4 04-04 Task 2: `gcp-setup.sh` executed, gemini-api-key in Secret Manager
2. ai-service deployed to Cloud Run (currently Phase 8 deliverable — deferred)
3. Plan 05-01 Task deferred: `terraform apply` — VM provisioned
4. Plan 05-02 Task 2 deferred: Gmail OAuth Published, creds in /opt/n8n/.env
5. Plan 05-03 Task 2 deferred: n8n workflow imported, credentials re-linked
6. `/opt/n8n/.env` on VM populated with real AI_SERVICE_URL (Cloud Run URL, NO :8090)

**Part A — Execute the smoke test runbook**

Follow `n8n/docs/end-to-end-smoke-test.md` from top to bottom. Minimum passing checks:
- [ ] Pre-flight: VM active, swap 2G, container Up, n8n /healthz 200, ai-service /health 200
- [ ] Test 1 — Happy Path: real email receives AI reply with quote + signature within 6 min
- [ ] Test 2 — Filter rejection: at least one junk case (self-loop or empty body) confirmed skipped
- [ ] Test 3 — Fallback path: with AI_SERVICE_URL unreachable, fallback reply delivered
- [ ] Test 4 — VM reboot: `sudo reboot`, wait 90s, `systemctl is-active n8n` = active, new email processed
- [ ] Test 5 — Record day-0 date for 8-day OAuth persistence check (run later)

**Part B — Provision GCP uptime check**

```bash
PROJECT_ID=<your-project> ALERT_EMAIL=<your-email> \
  bash gcp/monitoring/n8n-uptime-check.sh
```
Verify:
```bash
gcloud monitoring uptime list-configs --project=$PROJECT_ID \
  --filter="displayName=n8n-vm-uptime"
```
must return non-empty.

**Part C — EMAIL-05 status:** Already satisfied in commit `1ba4ea4` (n8n/workflows/email-bot.json + error-handler.json committed in plan 05-03). No action needed.

**Part D — Fill Results Table**

Edit `n8n/docs/end-to-end-smoke-test.md` and fill dates/results for Tests 1-4. Commit:
```bash
git add n8n/docs/end-to-end-smoke-test.md
git commit -m "docs(05): record smoke test results"
```

**Part E — Update phase summary**

Edit `.planning/phases/05-n8n-email-bot/05-PHASE-SUMMARY.md`:
- Replace "Completed: <date — filled in after smoke test>" with real date
- Flip [ ] → ✅ in Requirements Delivered table for EMAIL-01..EMAIL-06 (EMAIL-07 stays pending until day +8)
- Flip [ ] → [x] in Phase Exit Criteria for passed tests
- Copy filled Results Table from end-to-end-smoke-test.md into the Smoke Test Results section

**[ ] Completed on: ____**
