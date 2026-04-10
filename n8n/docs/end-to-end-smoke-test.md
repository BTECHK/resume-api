# Phase 5 End-to-End Smoke Test

This runbook validates every Phase 5 requirement (EMAIL-01..EMAIL-07) end-to-end. Run after Plans 01-03 are executed and Plan 04 Task 1 is complete.

The runbook is designed so a first-time operator can follow it top-to-bottom without cross-referencing the plan files. Every step prints a concrete command or describes a concrete GUI observation. Fill in the Results Table at the bottom as you go.

## Prerequisites

- [ ] `terraform/n8n-vm/` applied successfully — VM `resume-bot-n8n` is running
- [ ] Plan 02 complete: Gmail OAuth consent screen shows Publishing status = **In production**, `client_id`/`client_secret` pasted into `/opt/n8n/.env` on the VM
- [ ] Plan 03 complete: `n8n/workflows/email-bot.json` + `error-handler.json` imported to live n8n, Gmail OAuth2 credential re-linked on all 4 Gmail nodes, Error Workflow registered in Settings
- [ ] ai-service `/chat` endpoint is live and reachable (Phase 4 deployed to Cloud Run). `AI_SERVICE_URL` in `/opt/n8n/.env` is the Cloud Run HTTPS URL with **no `:8090` suffix**
- [ ] You have access to two email accounts: your **personal Gmail** (to send test emails from) and the **dedicated bot Gmail** (the bot's inbox)

---

## Pre-Flight Checks

Run these **before** sending any test email. If any fails, stop and fix it before proceeding.

SSH to the VM:

```bash
ssh ubuntu@$(cd terraform/n8n-vm && terraform output -raw instance_ip)
```

From inside the VM:

```bash
# EMAIL-06 — systemd unit active
sudo systemctl is-active n8n
# Expected: active

# EMAIL-01 / D-10 — 2GB swap created and mounted
free -h | grep -i swap
# Expected: Swap total >= 2.0G

swapon --show
# Expected: /swapfile  file  2G  ...

# EMAIL-01 — n8n container running
docker ps --filter "name=resume-bot-n8n" --format "{{.Names}}\t{{.Status}}"
# Expected: resume-bot-n8n    Up N minutes (healthy)

# n8n internal healthcheck responds
curl -sf http://localhost:5678/healthz && echo OK
# Expected: OK

# Docker container memory pressure sanity (Pitfall #2)
docker stats --no-stream resume-bot-n8n --format "{{.Name}} {{.MemUsage}} {{.MemPerc}}"
# Expected: MemPerc < 90% (700m limit; sustained > 90% = investigate OOM risk)
```

From your local workstation:

```bash
# Phase 4 ai-service up
curl -sf "$AI_SERVICE_URL/health" && echo OK
# Expected: OK

# Double-check AI_SERVICE_URL has no :8090 port leak
grep -E "AI_SERVICE_URL=" <<<"$(ssh ubuntu@<VM_IP> 'sudo cat /opt/n8n/.env | grep AI_SERVICE_URL')" | grep -v ":8090" && echo "URL has no :8090 (correct)"
```

All six pre-flight lines must be green. Record the result in the Results Table row **"Pre-flight"**.

---

## Test 1 — Happy Path (EMAIL-02, EMAIL-03)

Validates the core email → AI → reply loop. This is the **primary EMAIL-03 verification**.

1. SSH tunnel to n8n UI:
   ```bash
   ssh -L 5678:localhost:5678 ubuntu@<VM_IP>
   ```
2. Open `http://localhost:5678`, log in with `N8N_USER` / `N8N_PASSWORD`
3. Workflows → **email-bot** → toggle **ACTIVE** (top-right) — the workflow starts polling immediately
4. From your personal email, send an email to `BOT_GMAIL_ADDRESS`:
   - **Subject:** `Test: background question`
   - **Body:** `Can you tell me about your recent work on Cloud Run?`
5. Wait up to **6 minutes** (5-min poll interval per D-03 + up to 60 s for ai-service `/chat` call + Gmail send)
6. Check your personal Gmail **Inbox** (not Sent) for the AI reply

Verification checklist — all boxes must be checked:

- [ ] Reply received within 6 minutes of sending
- [ ] Reply body starts with an AI-generated answer (NOT the fallback "Thank you for your message..." template)
- [ ] Reply contains the quoted original question (D-07, lines starting with `>`)
- [ ] Reply contains signature block with `CANDIDATE_NAME`, GitHub, portfolio (D-06)
- [ ] Reply is plain text and renders correctly in Gmail (D-05 — no HTML tags visible)
- [ ] Reply subject is `Re: Test: background question` (thread-aware reply)
- [ ] n8n UI → Executions → most recent row shows all nodes green, no red error states
- [ ] In the bot Gmail web UI, the original email now has the **bot-replied** label applied (confirms the "Label: Mark as Replied" node ran)

If any box fails, see the Troubleshooting section at the bottom. Do NOT proceed to Test 2 until Test 1 is green.

Record date + result in Results Table row **"Test 1 Happy path"**.

---

## Test 2 — Filter Rejection (D-13, Pitfall #6)

Validates the IF filter node skips auto-replies, newsletters, and self-loops. Pick **at least one** of the following cases:

**Option A — Self-loop guard (Pitfall #6):**

1. Log in to the **bot Gmail** account in a separate browser
2. From the bot Gmail, compose a new email to itself (the bot Gmail address)
3. Subject: `Self-send test`; Body: `hello`
4. Send
5. Wait 6 minutes
6. Verify: n8n Executions shows the Gmail Trigger fired, but the Filter node output = **0 items passed** (the self-loop guard caught it via `from == BOT_GMAIL_ADDRESS`)
7. Verify: your personal Inbox does NOT receive a reply to this self-email

**Option B — Empty body (D-13):**

1. From your personal Gmail, send an email to the bot with:
   - Subject: `Empty body test`
   - Body: (leave completely blank)
2. Wait 6 minutes
3. Verify: n8n Executions shows the Filter node rejected the item (0 items passed)
4. Verify: personal Gmail does NOT receive a reply

**Verification checklist:**

- [ ] At least one junk case (self-loop or empty body) was rejected by the Filter node
- [ ] n8n Execution log shows Filter node output count = 0 for that case
- [ ] No reply was sent

Record date + result in Results Table row **"Test 2 Filter rejection"**.

---

## Test 3 — Fallback Path (EMAIL-04)

Validates the polite fallback reply when ai-service is unreachable (D-12).

1. SSH to the VM
2. **Backup** the current `.env`:
   ```bash
   sudo cp /opt/n8n/.env /opt/n8n/.env.backup
   ```
3. Edit `/opt/n8n/.env` and change `AI_SERVICE_URL` to an unreachable host:
   ```
   AI_SERVICE_URL=http://127.0.0.1:9999
   ```
4. Restart n8n:
   ```bash
   sudo systemctl restart n8n
   ```
5. Wait 20 seconds for the container to come up:
   ```bash
   sudo systemctl is-active n8n   # Expected: active
   docker ps | grep resume-bot-n8n
   ```
6. From your personal Gmail, send a test email:
   - Subject: `Fallback test`
   - Body: `This should trigger the fallback reply.`
7. Wait up to 6 minutes
8. Verify your personal Inbox for the reply

Verification checklist:

- [ ] Reply received within 6 minutes
- [ ] Reply body matches the fallback template: starts with `Thank you for your message! I'm unable to provide an AI-generated reply right now...`
- [ ] Reply contains `CANDIDATE_CONTACT_EMAIL` value
- [ ] Reply contains signature block (D-06)
- [ ] n8n Execution log shows HTTP Request node exhausted 3 retries and fell through the `continueErrorOutput` branch to Gmail Send: Fallback Reply

**RESTORE step — do NOT skip:**

```bash
sudo cp /opt/n8n/.env.backup /opt/n8n/.env
sudo systemctl restart n8n
sudo systemctl is-active n8n   # Expected: active
```

Verify the restore worked by sending one more normal test email and confirming Test 1 passes again. Then delete the backup:

```bash
sudo rm /opt/n8n/.env.backup
```

Record date + result in Results Table row **"Test 3 Fallback path"**.

---

## Test 4 — VM Reboot (EMAIL-06)

Validates systemd auto-restart on VM boot.

1. SSH to the VM
2. Record the current uptime:
   ```bash
   uptime
   ```
3. Reboot:
   ```bash
   sudo reboot
   ```
4. Your SSH session will drop. **Wait 90 seconds** (e2-micro boot + Docker start + n8n image load).
5. Re-SSH to the VM
6. Verify:
   ```bash
   sudo systemctl is-active n8n
   # Expected: active

   docker ps --filter "name=resume-bot-n8n" --format "{{.Status}}"
   # Expected: Up N seconds

   swapon --show
   # Expected: /swapfile 2G (survived reboot via /etc/fstab entry)

   curl -sf http://localhost:5678/healthz && echo OK
   # Expected: OK
   ```
7. From your personal Gmail, send one more test email
8. Wait 6 minutes; confirm it is processed and replied to (proves Gmail Trigger resumed polling after reboot)

Verification checklist:

- [ ] `systemctl is-active n8n` prints `active` after reboot (EMAIL-06)
- [ ] resume-bot-n8n container is Up
- [ ] Swap is still mounted (survived reboot)
- [ ] `/healthz` returns 200
- [ ] Post-reboot test email gets a reply within 6 minutes

Record date + result in Results Table row **"Test 4 VM reboot"**.

---

## Test 5 — OAuth Token Persistence (EMAIL-07) [DELAYED]

This test cannot be run immediately — it validates the Production-mode fix from Plan 02 against Google's 7-day refresh-token expiry (Pitfall #1).

**Day 0 (today):**

- Record today's date: `__________`
- Confirm Test 1 passed (proves tokens work right now)

**Day +8 (eight days later):**

1. Do NOT touch the n8n credential between Day 0 and Day +8
2. Re-run Test 1 (send a real email from personal Gmail to bot)
3. Wait 6 minutes
4. If you receive an AI reply → **EMAIL-07 verified** (Production mode held the token)
5. If you see `invalid_grant` or `Token has been expired or revoked` in n8n execution logs → re-check Publishing status per `n8n/docs/gmail-oauth-setup.md` Step 7. The consent screen must read **"In production"**, not "Testing".

Record both dates + result in Results Table row **"Test 5 8-day token"**.

---

## Results Table (fill in as you go)

| Test                                | Requirement(s)     | Date | Result |
| ----------------------------------- | ------------------ | ---- | ------ |
| Pre-flight: VM/swap/container       | EMAIL-01, EMAIL-06 | ____ | [ ]    |
| 1 Happy path                        | EMAIL-02, EMAIL-03 | ____ | [ ]    |
| 2 Filter rejection                  | D-13, Pitfall #6   | ____ | [ ]    |
| 3 Fallback path                     | EMAIL-04           | ____ | [ ]    |
| 4 VM reboot                         | EMAIL-06           | ____ | [ ]    |
| 5 8-day token (Day 0 recorded)      | EMAIL-07           | ____ | [ ] (run on day +8) |
| Workflow JSON committed             | EMAIL-05           | ____ | [ ] (git log n8n/workflows/) |

After filling this in, commit the runbook update:

```bash
git add n8n/docs/end-to-end-smoke-test.md
git commit -m "docs(05): record smoke test results"
```

---

## Troubleshooting

**Test 1 — no reply received after 10 minutes:**

- Check n8n Executions. If no executions appear, the Gmail Trigger is not polling — verify it says "Active" top-right and that the Gmail OAuth2 credential is linked (Pitfall #5).
- If executions appear but all red on HTTP Request: check `AI_SERVICE_URL` in `/opt/n8n/.env`. Common mistake: `:8090` port suffix leaked in from local docker-compose dev. Remove it — Cloud Run HTTPS is on implicit 443.
- Rate limit (429) from ai-service: Pitfall #7. Only an issue with large backlogs; rare in normal operation.

**Test 1 — reply received but it's the fallback template:**

- The HTTP Request node exhausted retries and fell through to fallback. Means `/chat` is unreachable OR returning errors. Check `curl -sf "$AI_SERVICE_URL/chat" -X POST -H 'Content-Type: application/json' -d '{"messages":[{"role":"user","content":"hi"}]}'` from the VM.

**Test 3 — fallback reply NOT received (error silent):**

- Check n8n Executions. If the HTTP Request node shows `continueErrorOutput` was not triggered, the retry config may be wrong — verify `maxTries: 3` and `onError: continueErrorOutput` in the node settings.

**Test 4 — n8n not active after reboot:**

- Check `sudo journalctl -u n8n.service -n 50` — likely `/opt/n8n/.env` is missing or Docker daemon hadn't started yet. Check `After=docker.service network-online.target` is in the unit file.
- If Docker daemon isn't running: `sudo systemctl enable docker && sudo systemctl start docker && sudo systemctl start n8n`

**Test 5 — `invalid_grant` on day +8:**

- Publishing status reverted or was never set to "In production". Re-do `n8n/docs/gmail-oauth-setup.md` Step 7. Delete the n8n credential and recreate it after publishing.

**n8n container in Exited (137) state:**

- Pitfall #2 OOM. Verify `swapon --show` shows 2G. Check `dmesg | grep -i oom` for OOM kills. If swap is missing, re-run `startup.sh` manually.

**Gmail OAuth "unverified app" warning blocking credential setup:**

- Expected on first connection. Click **Advanced** → `Go to Resume Bot Phase 5 (unsafe)` → continue. Appears only once per user.

---

## Related references

- `n8n/docs/gmail-oauth-setup.md` — OAuth setup runbook (Plan 02)
- `n8n/docs/workflow-import-runbook.md` — Workflow import + credential re-linking (Plan 03)
- `n8n/docs/workflow-build-guide.md` — Node-by-node walkthrough
- `gcp/monitoring/n8n-uptime-check.sh` — Uptime check provisioning (D-15)
- `.planning/phases/05-n8n-email-bot/05-CONTEXT.md` — Decisions D-01..D-16
- `.planning/phases/05-n8n-email-bot/05-RESEARCH.md` — Full pitfall descriptions
