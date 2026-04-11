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

## Phase 6 — Deferred Manual Steps

### Plan 06-04 Task A: Build and push the frontend Docker image to Artifact Registry

**Why deferred:** Scaffold-first session per D-04. The Dockerfile is committed but no image has been built or pushed. This step requires `gcloud` authenticated against the GCP project, an existing Artifact Registry repo (provisioned by Phase 4 Plan 04-04 Task 2), and a tagged build. Cold-start of the container needs to be verified <500ms before Task C deploys it.

**Prerequisites:**
1. Phase 4 Plan 04-04 Task 2 completed: `cloud-run-source-deploy` Artifact Registry repo exists in `us-central1` (auto-created on first `gcloud run deploy --source .`, but can be pre-provisioned)
2. `gcloud auth login` completed
3. `gcloud config set project $PROJECT_ID` completed
4. Docker Desktop (or compatible) running locally — only needed if you want to do a smoke build before Task C; otherwise Cloud Build does it
5. `frontend/.env.local` populated with real values (see Task B)

**Steps to complete later:**

```bash
# Optional: smoke-test the Dockerfile builds locally first
cd frontend
docker build \
  --build-arg VITE_AI_SERVICE_URL="https://ai-service-XXXX-uc.a.run.app" \
  --build-arg VITE_CANDIDATE_NAME="Your Name" \
  --build-arg VITE_CANDIDATE_TITLE="Software Engineer" \
  --build-arg VITE_CANDIDATE_EMAIL="hello@example.com" \
  -t resume-chatbot:local .

# Verify image size (should be <50MB total per D-07 target)
docker images resume-chatbot:local --format '{{.Size}}'

# Optional: smoke-test locally
docker run --rm -p 8080:8080 resume-chatbot:local
# In another terminal: curl http://localhost:8080/healthz  → expect "ok"
# Then: curl -I http://localhost:8080/  → expect 200 with Cache-Control: no-cache
# Stop with Ctrl+C
cd ..
```

If the local smoke build passes, proceed to Task C — `gcloud run deploy --source .` will rebuild via Cloud Build automatically (no manual push required). If you want to push the local image to AR explicitly:

```bash
docker tag resume-chatbot:local us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/resume-chatbot:latest
gcloud auth configure-docker us-central1-docker.pkg.dev
docker push us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/resume-chatbot:latest
```

**Acceptance:**
- Image size <50MB
- `curl http://localhost:8080/healthz` returns `ok`
- `curl http://localhost:8080/chat` returns a 200 with `index.html` (SPA fallback works)
- `curl http://localhost:8080/assets/<some-hashed-file>.js` returns 200 with `Cache-Control: public, max-age=31536000, immutable`

**[ ] Completed on: ____**

---

### Plan 06-04 Task B: Populate frontend/.env.local with real VITE_* values

**Why deferred:** `frontend/.env.local` is gitignored by design (contains environment-specific URLs, not secrets but not committable). Operator must create it once ai-service is live.

**Prerequisites:**
1. Phase 4 ai-service deployed to Cloud Run — its Cloud Run URL must be known. Get it via:
   ```bash
   gcloud run services describe ai-service --region us-central1 --format='value(status.url)'
   ```

**Steps to complete later:**

```bash
cd frontend
cp .env.example .env.local

# Edit .env.local and replace the four placeholder values:
#   VITE_AI_SERVICE_URL=https://ai-service-XXXX-uc.a.run.app  (NO trailing slash, NO :8090)
#   VITE_CANDIDATE_NAME=<your real name>
#   VITE_CANDIDATE_TITLE=<your real title>
#   VITE_CANDIDATE_EMAIL=<your real email>

# Verify .env.local is gitignored (must NOT show up in git status)
git status .env.local
# Expected: empty output (file is ignored)
```

**CRITICAL:** `VITE_AI_SERVICE_URL` must be the **HTTPS Cloud Run URL with no trailing slash, no port, no path**. Example: `https://ai-service-abc123-uc.a.run.app`. The frontend appends `/chat` automatically.

**[ ] Completed on: ____**

---

### Plan 06-04 Task C: Deploy frontend to Cloud Run via deploy.sh

**Why deferred:** Requires Tasks A + B done, gcloud authenticated, and a real ai-service URL in `.env.local`.

**Prerequisites:**
1. Task A done (or skipped — `gcloud run deploy --source .` will trigger Cloud Build to rebuild from scratch)
2. Task B done — `.env.local` populated
3. `PROJECT_ID` env var exported
4. `gcloud auth login` and `gcloud config set project $PROJECT_ID` done
5. The Cloud Build API and Cloud Run API are enabled in the project (`gcloud services enable cloudbuild.googleapis.com run.googleapis.com`)

**Steps to complete later:**

```bash
cd frontend
export PROJECT_ID=<your-gcp-project>
bash deploy.sh
```

The script will:
1. Validate `.env.local` exists and has all four VITE_* vars
2. Refuse to run if `VITE_AI_SERVICE_URL` still contains `PLACEHOLDER`
3. Run `gcloud run deploy resume-chatbot --source . --set-build-env-vars ...` which uploads the source dir, runs Cloud Build with the Dockerfile, and deploys the resulting image
4. Print the deployed Cloud Run service URL at the end — **save this URL for Task D**

**Acceptance:**
- `gcloud run services describe resume-chatbot --region us-central1 --format='value(status.url)'` returns a non-empty URL
- The URL responds to `curl -I` with HTTP 200 and `Server: nginx`
- `curl https://<service-url>/healthz` returns `ok`
- Hard-refresh on `https://<service-url>/chat` renders the chat screen (SPA fallback works in production)

**[ ] Completed on: ____**

---

### Plan 06-04 Task D: Update ai-service ALLOWED_ORIGINS to the new frontend Cloud Run URL and redeploy ai-service

**Why deferred:** This is the chicken-and-egg CORS resolution (RESEARCH Track 5). The frontend needs the ai-service URL (Task B) and ai-service needs the frontend URL (this task). Cannot be done before Task C completes.

**Why this matters (Pitfall #10 — HIGH):** Phase 4 ai-service `main.py` configures `CORSMiddleware` with `allow_credentials=True`. The CORS spec forbids wildcard `*` origins when credentials are enabled, so `ALLOWED_ORIGINS=*` will silently fail in the browser. The fix is to set `ALLOWED_ORIGINS` to the EXACT frontend Cloud Run URL — including `https://`, no trailing slash.

**Prerequisites:**
1. Task C completed — frontend Cloud Run URL is known
2. ai-service is deployed and reachable
3. `gcloud` authenticated against the project

**Steps to complete later:**

```bash
# Get the frontend URL from Task C (or re-fetch it):
FRONTEND_URL=$(gcloud run services describe resume-chatbot --region us-central1 --format='value(status.url)')
echo "Frontend URL: $FRONTEND_URL"

# Redeploy ai-service with the updated ALLOWED_ORIGINS env var.
# Replace SERVICE with the actual ai-service Cloud Run service name.
gcloud run services update ai-service \
  --region us-central1 \
  --update-env-vars "ALLOWED_ORIGINS=$FRONTEND_URL"

# Verify the env var is set:
gcloud run services describe ai-service --region us-central1 \
  --format='value(spec.template.spec.containers[0].env)'
```

**CRITICAL formatting rules:**
- The URL must start with `https://`
- NO trailing slash
- NO path
- Comma-separated if you want multiple origins (e.g. dev + prod): `https://resume-chatbot-xxxx.run.app,http://localhost:5173`
- Do NOT use `*` — it will silently break preflight (Pitfall #10)

**Acceptance:**
- `curl -i -X OPTIONS https://<ai-service-url>/chat -H "Origin: $FRONTEND_URL" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: content-type"` returns 200 with `Access-Control-Allow-Origin: <FRONTEND_URL>` (NOT `*`)

**[ ] Completed on: ____**

---

### Plan 06-04 Task E: End-to-end smoke test (frontend → ai-service)

**Why deferred:** Requires Tasks A through D done. Covers INT-02 partial (frontend → ai-service integration). Real-traffic verification — cannot be automated in scaffold mode.

**Prerequisites:**
1. Tasks A, B, C, D all completed
2. ai-service `/chat` is reachable and answering questions
3. A quiet 5 minutes to actually use the chatbot

**Steps to complete later:**

1. Open the frontend Cloud Run URL in a browser (Chrome recommended for DevTools clarity)
2. **Landing page check (CHAT-07):**
   - Verify `<h1>` shows your real `VITE_CANDIDATE_NAME`
   - Verify `<h2>` shows your real `VITE_CANDIDATE_TITLE`
   - Click "Email My Resume" → confirm OS opens default mail client with `Resume inquiry from <name>` subject
   - Click browser back, then click "Chat With My Resume" → confirm navigation to `/chat`
3. **Chat screen check (CHAT-02, CHAT-05):**
   - Auto-greeting bubble appears immediately on page load
   - Type a real question (e.g. "What languages do you know?") and press Enter
   - Typing indicator (3 dots) appears
   - Bot reply appears within ~3 seconds (longer on first cold-start, up to 30s)
4. **Network tab check (CORS verification):**
   - Open DevTools → Network tab
   - Send another message
   - Find the `OPTIONS /chat` preflight request → should be 200 with `Access-Control-Allow-Origin: <frontend-url>`
   - Find the `POST /chat` request → should be 200 with the JSON response
5. **Mobile responsive check (CHAT-03):**
   - DevTools → Device Toolbar (Ctrl+Shift+M) → iPhone 14 Pro
   - Reload — verify hero, CTAs stack vertically, header still glass-blur, chat input pinned to bottom, no horizontal scroll
6. **Hard-refresh deep link check (CHAT-08):**
   - Navigate to the chat screen
   - Hit Ctrl+Shift+R (hard refresh) directly on `/chat`
   - Verify the chat screen still renders (proves nginx SPA fallback `try_files` works)

**Common failure modes (CORS debugging runbook from RESEARCH Track 5):**

| Symptom in browser DevTools | Likely cause | Fix |
|----------------------------|--------------|-----|
| `Access to fetch ... blocked by CORS policy: No 'Access-Control-Allow-Origin'` | ai-service not running, or URL mismatch | Verify `VITE_AI_SERVICE_URL` matches deployed ai-service URL exactly |
| `the value of the 'Access-Control-Allow-Origin' header ... must not be the wildcard '*' when credentials mode is 'include'` | `ALLOWED_ORIGINS=*` on ai-service | Re-do Task D with the exact frontend URL (no `*`) — Pitfall #10 |
| `Request header field content-type is not allowed by Access-Control-Allow-Headers` | ai-service CORSMiddleware misconfigured | Verify `allow_headers=["*"]` in `ai-service/main.py` line 113-119 (already correct in Phase 4) |
| `CORS preflight did not succeed` (`net::ERR_FAILED`) | ai-service returning 500 on OPTIONS, or unreachable | `curl -i -X OPTIONS <ai-service-url>/chat -H "Origin: ..." -H "Access-Control-Request-Method: POST"` — should be 200 |
| Frontend loads but "Sorry, I couldn't reach the AI" | Network failure (cold start timeout, or wrong URL) | Check Cloud Run logs for ai-service; bump `--timeout` on ai-service deploy if cold-start exceeds 30s |
| 422 Unprocessable Entity from `/chat` | Frontend message shape doesn't match Pydantic | Verify `frontend/src/lib/types.ts` matches `ai-service/main.py` lines 159–196 byte-for-byte |

**[ ] Completed on: ____**

---

## Phase 7 — Deferred Manual Steps

### Full test suite run

**Why deferred:** Local Python env lacks `chromadb`, `sentence-transformers`, `slowapi`, `google-genai`. 25 of 86 tests are guarded via `pytest.importorskip` and skip cleanly.

**Steps to complete later:**
1. `cd ai-service && pip install -r requirements.txt`
2. `pytest`
3. Expect: 86 passed, coverage >= 70% across modules

**[ ] Completed on: ____**

### Coverage gate promotion

**Why deferred:** `--cov-fail-under=70` lives in the CI workflow (`.github/workflows/ci.yml` job `test-ai`) rather than `ai-service/pytest.ini`. Local runs without ML deps would otherwise always fail the threshold.

**Steps to complete later (optional):**
1. Once local env reliably has all deps, edit `ai-service/pytest.ini` and append `--cov-fail-under=70` to `addopts`
2. Remove the duplicate `--cov-fail-under=70` from `.github/workflows/ci.yml`

**[ ] Completed on: ____**

---

## Phase 8 — Deferred Manual Steps

### CICD-03: Workload Identity Federation provider creation

**Why deferred:** Requires `gcp-setup.sh` from Phase 4 to have run (billing + project exists) and requires GitHub repo settings access.

**Steps to complete later:**
1. Get numeric repo ID: `gh api repos/BTECHK/resume-api-repo --jq .id`
2. Run in GCP:
   ```bash
   PROJECT_ID=<your-project-id>
   PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
   gcloud iam workload-identity-pools create "github-pool" \
     --project="$PROJECT_ID" --location="global" --display-name="GitHub Pool"
   gcloud iam workload-identity-pools providers create-oidc "github-provider" \
     --project="$PROJECT_ID" --location="global" \
     --workload-identity-pool="github-pool" \
     --display-name="GitHub provider" \
     --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_id=assertion.repository_id" \
     --attribute-condition="assertion.repository_id == '<NUMERIC_REPO_ID>'" \
     --issuer-uri="https://token.actions.githubusercontent.com"
   gcloud iam service-accounts create cicd-runner --project=$PROJECT_ID
   gcloud iam service-accounts add-iam-policy-binding \
     cicd-runner@$PROJECT_ID.iam.gserviceaccount.com \
     --project=$PROJECT_ID \
     --role=roles/iam.workloadIdentityUser \
     --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/BTECHK/resume-api-repo"
   ```
3. Grant the cicd-runner SA Cloud Run Admin, Artifact Registry Writer, IAM Service Account User roles
4. Set GitHub repo secrets:
   - `GCP_PROJECT_ID`
   - `GCP_WIF_PROVIDER` = `projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider`
   - `GCP_SERVICE_ACCOUNT` = `cicd-runner@$PROJECT_ID.iam.gserviceaccount.com`
   - `ALLOWED_ORIGINS` = the frontend Cloud Run URL
   - `VITE_AI_SERVICE_URL` = the ai-service Cloud Run URL

**[ ] Completed on: ____**

### First CI run

**Why deferred:** No commits pushed to a configured remote yet and the WIF provider doesn't exist.

**Steps to complete later:**
1. Ensure all 5 GitHub secrets above are set
2. Push to `main`: `git push origin main`
3. Watch the run at https://github.com/BTECHK/resume-api-repo/actions
4. Expect: path-filtered jobs for any changed paths, deploy only if `main`

**[ ] Completed on: ____**

### SEC-04: Base image digest pinning

**Why deferred:** Digests change weekly; pinning now would block builds by next week.

**Steps to complete later (per Dockerfile):**
```bash
docker pull python:3.11-slim
docker inspect --format='{{index .RepoDigests 0}}' python:3.11-slim
docker pull node:20-alpine
docker inspect --format='{{index .RepoDigests 0}}' node:20-alpine
docker pull nginx:1.27-alpine
docker inspect --format='{{index .RepoDigests 0}}' nginx:1.27-alpine
```
Then replace each `FROM python:3.11-slim` with `FROM python@sha256:<digest>` in `ai-service/Dockerfile`, same for `frontend/Dockerfile`. Commit with a monthly cadence.

**[ ] Completed on: ____**

### INT-01..04: Smoke tests against live services

**Why deferred:** Scripts are authored but require live Cloud Run URLs + (for email) n8n VM + Gmail OAuth.

**Steps to complete later:**
```bash
export AI_SERVICE_URL=https://ai-service-xxxxx.run.app
python scripts/smoke/smoke_ai_ask.py
python scripts/smoke/smoke_chat.py

# Runs in-process against real Chroma:
pip install -r ai-service/requirements.txt
python scripts/smoke/smoke_rag_ingest.py

# Requires n8n webhook URL (after Phase 5 manual steps):
export N8N_WEBHOOK_URL=https://n8n.example.com/webhook/email-test
python scripts/smoke/smoke_email.py
```

**[ ] Completed on: ____**
