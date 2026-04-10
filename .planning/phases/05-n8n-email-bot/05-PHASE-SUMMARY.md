# Phase 5 — n8n Email Bot — Summary

**Completed:** `<date — filled in after smoke test>`

Self-hosted n8n email bot on GCE e2-micro. Polls a dedicated Gmail inbox every 5 minutes, filters junk, calls the Phase 4 ai-service `/chat` endpoint with thread-aware conversation context, and sends either an AI-generated reply or a polite fallback. Infrastructure provisioned via Terraform (IaC), orchestrated via Docker Compose + systemd, and monitored via a GCP Cloud Monitoring TCP uptime check on port 22.

Phase 5 was executed in **scaffold-first mode**: all code, IaC, workflows, runbooks, and monitoring scripts landed in the repo and passed static verification. Live execution (terraform apply, Gmail OAuth Publish, workflow import, end-to-end smoke test) is tracked in `DEFERRED-WORK.md` and will run once the deployed VM + Cloud Run ai-service + Gmail OAuth are all live simultaneously.

---

## Requirements Delivered

| ID        | Requirement                                                                 | Status | Notes                                                                                   |
| --------- | --------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------- |
| EMAIL-01  | n8n self-hosted on GCE e2-micro via Docker Compose with 2GB swap            | [ ]    | IaC ready (`terraform/n8n-vm/`); live validation pending (Test 1 pre-flight)            |
| EMAIL-02  | Gmail Trigger polls dedicated inbox every 5 minutes (D-03 override of 60s)  | [ ]    | Workflow JSON encodes 5-min interval; live validation pending (Test 1)                  |
| EMAIL-03  | Extracts email question, calls ai-service `/chat`, sends formatted reply   | [ ]    | D-14 override: uses `/chat` (not `/ai/ask`). Live validation pending (Test 1)           |
| EMAIL-04  | Error fallback sends polite reply if ai-service unreachable                 | [ ]    | `continueErrorOutput` branch wired; live validation pending (Test 3)                    |
| EMAIL-05  | n8n workflow exported as JSON in `n8n/workflows/` (version controlled)      | ✅     | Satisfied by commit `1ba4ea4` (Plan 05-03) — both `email-bot.json` and `error-handler.json` committed |
| EMAIL-06  | systemd service for auto-restart on VM boot                                 | [ ]    | `n8n/systemd/n8n.service` ready; live validation pending (Test 4)                       |
| EMAIL-07  | Gmail OAuth app in Production mode (prevents 7-day token expiry)            | [ ]    | Runbook ready (`n8n/docs/gmail-oauth-setup.md`); requires Day 0 + Day +8 validation     |

**Delayed verification:** EMAIL-07 requires an 8-day wait between Day 0 (first successful token use) and Day +8 (re-run Test 1 to prove the refresh token did not expire). Recorded dates will land in the Smoke Test Results section below.

---

## Artifacts Produced

### Infrastructure as Code
- `terraform/n8n-vm/main.tf` — `google_compute_instance` (e2-micro, Ubuntu 22.04, 30GB disk) + `google_compute_firewall` (SSH-only, port 22; NO port 5678 per D-09)
- `terraform/n8n-vm/variables.tf` — `project_id`, `region`, `zone`, `ssh_pub_key_path`, `instance_name`, `machine_type`, `disk_size_gb`
- `terraform/n8n-vm/outputs.tf` — `instance_ip`, `instance_name`, `ssh_command`
- `terraform/n8n-vm/startup.sh` — boot script: 2GB swap + `vm.swappiness=10`, Docker + Compose v2 install, `/opt/n8n/` prep, systemd unit inline deployment (byte-identical to `n8n/systemd/n8n.service`)
- `terraform/n8n-vm/README.md` + `.gitignore`

### Runtime configuration
- `n8n/systemd/n8n.service` — `Type=oneshot` + `RemainAfterExit=yes`, `Restart=on-failure` (NOT `always` — Pitfall #3), `TimeoutStartSec=300`
- `n8n/.env.example` — template with `N8N_USER`, `N8N_PASSWORD`, `AI_SERVICE_URL` (Cloud Run HTTPS, no `:8090`), `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `BOT_GMAIL_ADDRESS`, `CANDIDATE_*` signature vars

### n8n workflows (EMAIL-05 — committed in `1ba4ea4`)
- `n8n/workflows/email-bot.json` — 7-node main workflow (Gmail Trigger → Filter → Code → HTTP Request → AI Reply / Fallback Reply → Mark as Replied)
- `n8n/workflows/error-handler.json` — 2-node error handler (Error Trigger → Gmail Send Error Notification)

### Operator runbooks
- `n8n/docs/gmail-oauth-setup.md` — 9-step Gmail OAuth setup (creating dedicated Gmail, enabling Gmail API, OAuth consent screen, publishing app — critical for EMAIL-07)
- `n8n/docs/oauth-consent-screen-config.md` — Reference table with exact field values and D-02 exception note
- `n8n/docs/workflow-build-guide.md` — Node-by-node walkthrough tying each node back to D-03..D-16
- `n8n/docs/workflow-import-runbook.md` — 10-step post-import runbook (SSH tunnel, Gmail label creation, OAuth2 credential, credential re-linking per Pitfall #5, workflow activation)
- `n8n/docs/end-to-end-smoke-test.md` — EMAIL-01..EMAIL-07 validation runbook (Pre-flight + Tests 1-5)

### Monitoring (D-15)
- `gcp/monitoring/n8n-uptime-check.sh` — idempotent gcloud script provisioning TCP-22 uptime check + email notification channel
- `gcp/monitoring/README.md` — usage, limitations (TCP vs HTTP monitoring), Console fallback, tear-down

---

## Key Decisions Locked

- **D-01** — Dedicated Gmail account for the bot (not personal email). Runbook `n8n/docs/gmail-oauth-setup.md` Step 1 directs operator through creation.
- **D-02** — Script OAuth client creation via gcloud where possible. **Exception:** `gcloud iap oauth-clients` only creates IAP clients, not general-purpose Web Application OAuth 2.0 clients. The GCP Console is the only supported path for that specific step — documented in both the runbook and `oauth-consent-screen-config.md`.
- **D-03** — Poll interval = 5 minutes (not 60 seconds). Workflow JSON encodes `{ mode: "everyX", value: 5, unit: "minutes" }`.
- **D-04** — Gmail OAuth app MUST be Production mode (EMAIL-07, Pitfall #1). Runbook Step 7 marked as critical.
- **D-05** — Plain text replies, no HTML (D-05). Reply bodies use plain string concatenation.
- **D-06** — Professional signature: `CANDIDATE_NAME`, `CANDIDATE_GITHUB`, `CANDIDATE_PORTFOLIO` + AI disclaimer.
- **D-07** — Quote original question in the reply (standard email threading). Reply template uses `>` prefix on quoted lines.
- **D-08** — Terraform for VM provisioning. `terraform/n8n-vm/` module with single-file layout.
- **D-09** — No public n8n UI. Firewall opens port 22 only (zero matches on `5678` in `main.tf`). UI access via SSH port-forward only.
- **D-10** — 2GB swap file (`fallocate -l 2G /swapfile`) in startup.sh. Idempotent; tuned with `vm.swappiness=10`.
- **D-11** — Built on existing `n8n/docker-compose.yml` (not recreated). systemd unit `WorkingDirectory=/opt/n8n` preserves the relative `./workflows` volume mount.
- **D-12** — HTTP Request node: `Retry on Fail` ON, `Max Tries = 3`, `Wait Between Tries = 2000 ms`, `onError: continueErrorOutput` → fallback branch.
- **D-13** — Filter node rejects: self-loop (`from == BOT_GMAIL_ADDRESS`), `x-auto-reply-type` header present, `auto-submitted != no`, empty body, `CATEGORY_PROMOTIONS`, `CATEGORY_UPDATES`.
- **D-14** — **Override of EMAIL-03 text:** use `/chat` (not `/ai/ask`) for thread-aware multi-turn conversations. REQUIREMENTS.md §EMAIL-03 predates the Phase 5 context session. Single-message MVP now; thread history fetching deferred to Phase 5.5+.
- **D-15** — GCP Cloud Monitoring uptime check, free tier. Provisioned via `gcp/monitoring/n8n-uptime-check.sh` (TCP-22).
- **D-16** — n8n error workflow (`error-handler.json`) registered as main workflow's Error Workflow via Settings → Error Workflow.

---

## Pitfalls Avoided

1. **Pitfall #1 — Gmail OAuth 7-day token expiry (HIGH SEVERITY)** — Mitigated by Production mode step in `gmail-oauth-setup.md` (Step 7). Full EMAIL-07 validation requires an 8-day wait (Test 5).
2. **Pitfall #2 — e2-micro OOM** — Mitigated by 2GB swap (`startup.sh`) + Docker `mem_limit: 700m` (existing `docker-compose.yml`). Pre-flight check includes `swapon --show` and `docker stats` verification.
3. **Pitfall #3 — systemd + Docker restart policy double-start** — Mitigated by `Restart=on-failure` in unit (NOT `always`) + `restart: unless-stopped` in compose. systemd handles boot recovery; compose handles crash recovery. No overlap.
4. **Pitfall #4 — Startup script silent failure** — Mitigated by `set -euxo pipefail` in `startup.sh`. Verify via `sudo journalctl -u google-startup-scripts.service` on the VM.
5. **Pitfall #5 — Credential stripping on workflow import** — Mitigated by placeholder `REPLACE_AFTER_IMPORT` credential IDs on all 4 Gmail nodes + explicit re-linking step in `workflow-import-runbook.md` Step 7.
6. **Pitfall #6 — Auto-reply loop** — Mitigated by Filter node self-loop guard (`from != BOT_GMAIL_ADDRESS`) + `x-auto-reply-type` header check + `bot-replied` label exclusion on Gmail Trigger.
7. **Pitfall #7 — ai-service rate limit (429)** — Documented as known constraint (30/min on `/chat`). Normal operation stays well under limit; Wait node between iterations documented as mitigation for large backlogs.

---

## What's Still Manual (by design)

These are intentionally manual (not scripted) and are either deferred in `DEFERRED-WORK.md` or part of normal operator workflow:

- `terraform apply` — user runs once after Plan 01 files exist (`DEFERRED-WORK.md` Plan 05-01)
- GCP Console OAuth consent screen steps (Plan 02) — Google does not expose via CLI; D-02 exception documented (`DEFERRED-WORK.md` Plan 05-02 Task 2)
- `scp` of `docker-compose.yml` + `workflows/` to `/opt/n8n/` on the VM — post-`terraform apply` step in `terraform/n8n-vm/README.md`
- Gmail OAuth credential re-linking on workflow import (Pitfall #5) — covered in `workflow-import-runbook.md` Step 7 (`DEFERRED-WORK.md` Plan 05-03 Task 2)
- End-to-end smoke test — Plan 04 Task 3 (`DEFERRED-WORK.md` Plan 05-04 Task 3)
- Uptime check provisioning — requires a live deployed VM (part of Plan 05-04 Task 3 deferred entry)

---

## Phase Exit Criteria (filled post-checkpoint by Task 3b)

- [ ] EMAIL-01 — n8n on e2-micro + 2GB swap (pre-flight Test, Test 1)
- [ ] EMAIL-02 — Gmail Trigger 5-min poll (Test 1)
- [ ] EMAIL-03 — Email → `/chat` → reply (Test 1)
- [ ] EMAIL-04 — Fallback reply on ai-service unreachable (Test 3)
- [x] EMAIL-05 — Workflow JSON committed to `n8n/workflows/` (commit `1ba4ea4`, verified via `git log --oneline n8n/workflows/`)
- [ ] EMAIL-06 — systemd auto-restart on VM boot (Test 4)
- [ ] EMAIL-07 — OAuth Production mode (Day 0 verified via Test 1; Day +8 persistence verification pending via Test 5)

EMAIL-05 is the only box pre-checked in the skeleton: the workflow JSON commit `1ba4ea4` (from Plan 05-03) satisfies it without needing the live smoke test. All other boxes flip to `[x]` via Task 3b once the operator executes the smoke test runbook.

---

## Smoke Test Results

**Status:** Results Table below is empty — pending execution of the end-to-end smoke test (Plan 04 Task 3, currently in `DEFERRED-WORK.md`). Task 3b will copy filled-in results from `n8n/docs/end-to-end-smoke-test.md` once the operator completes the runbook.

| Test                                | Requirement(s)     | Date | Result |
| ----------------------------------- | ------------------ | ---- | ------ |
| Pre-flight: VM/swap/container       | EMAIL-01, EMAIL-06 | ____ | [ ]    |
| 1 Happy path                        | EMAIL-02, EMAIL-03 | ____ | [ ]    |
| 2 Filter rejection                  | D-13, Pitfall #6   | ____ | [ ]    |
| 3 Fallback path                     | EMAIL-04           | ____ | [ ]    |
| 4 VM reboot                         | EMAIL-06           | ____ | [ ]    |
| 5 8-day token (Day 0 → Day +8)      | EMAIL-07           | ____ | [ ] (delayed)  |
| Workflow JSON committed             | EMAIL-05           | 2026-04-10 | [x] (`1ba4ea4`) |

---

## Downstream Dependencies

- **Phase 8** end-to-end smoke tests will re-run the email → ai-service → reply loop via CI (INT-01). The smoke test runbook in this phase is the manual baseline; Phase 8 automates the parts that can be automated.
- **Phase 8** container hardening may add a non-root n8n user and pinned image digests (SEC-04) — deferred per `05-CONTEXT.md`. Current Phase 5 delivery relies on the upstream `n8nio/n8n:1.123.29` image as-is.
- **Phase 5.5+ enhancement:** Gmail thread history fetching in the Code node — single-message MVP now, up to 9 prior user/assistant messages later. ai-service already supports up to 10 messages per `/chat` request; this is a pure code-node change, no other workflow edits required.
- **Phase 6 (React Chatbot Frontend)** does NOT depend on Phase 5 — both extend Phase 4 in parallel.
