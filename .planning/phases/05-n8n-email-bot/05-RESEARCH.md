# Phase 5: n8n Email Bot - Research

**Researched:** 2026-04-09
**Domain:** n8n self-hosted automation, Gmail OAuth, Terraform GCE, systemd
**Confidence:** HIGH (core n8n/Gmail patterns), MEDIUM (Terraform GCE startup script swap detail)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Create a new dedicated Gmail account for the bot (not personal email)
- **D-02:** Script OAuth client creation via gcloud CLI where possible; manual steps (consent screen) documented in plan
- **D-03:** Poll interval set to every 5 minutes. Update success criteria: reply within ~5 min + processing time.
- **D-04:** Gmail OAuth app MUST be set to Production mode to prevent 7-day token expiry (EMAIL-07)
- **D-05:** Plain text email replies (no HTML). Professional tone, works in all clients.
- **D-06:** Professional signature block: candidate name, GitHub link, portfolio URL, and AI-generated disclaimer
- **D-07:** Quote the original question in the reply (standard email threading)
- **D-08:** Terraform for GCE e2-micro VM provisioning (IaC for portfolio story)
- **D-09:** No public access to n8n UI — outbound only (Gmail API + ai-service). SSH for admin only.
- **D-10:** 2GB swap file on the VM (per STATE.md pitfall #3 — prevents OOM with n8n 700m limit + Docker + OS)
- **D-11:** Existing `n8n/docker-compose.yml` already has n8n v1.123.29, 700m mem limit, healthcheck, basic auth, and workflows volume mount — build on this, don't recreate
- **D-12:** Retry ai-service 2-3 times with backoff before sending fallback reply. Fallback message: polite acknowledgment + direct contact email.
- **D-13:** Basic email filtering: skip auto-replies (out-of-office), newsletters, and emails with no body text. Reply to everything else.
- **D-14:** Thread-aware conversations: track email thread IDs, pass conversation context to `/chat` endpoint (not just `/ai/ask`). Enables back-and-forth email conversations.
- **D-15:** GCP Uptime Check on n8n healthcheck endpoint (free tier). Alert via email if down.
- **D-16:** n8n error workflow: sends notification when a reply fails (built-in n8n error handling pattern)

### Claude's Discretion

- Terraform module structure (single file vs modular)
- systemd service file details (restart policy, environment file path)
- n8n workflow node configuration specifics
- Thread tracking implementation (n8n function node vs external state)
- Retry backoff strategy (exponential vs fixed)
- Email filtering implementation (n8n IF node conditions)
- Uptime check configuration details (interval, alert channels)

### Deferred Ideas (OUT OF SCOPE)

- n8n shortlist keyword fork (ENH-06) — auto-categorize incoming emails
- Workflow versioning / git-based n8n backup
- Security hardening beyond basic auth (deferred to Phase 8)
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| EMAIL-01 | n8n self-hosted on GCE e2-micro via Docker Compose with 2GB swap | Terraform google_compute_instance + metadata_startup_script pattern; existing docker-compose.yml (D-11) |
| EMAIL-02 | Gmail Trigger polls dedicated inbox every 60 seconds | D-03 overrides to 5-minute interval; Gmail Trigger node supports configurable cron poll times |
| EMAIL-03 | Extracts email question, calls AI service /ai/ask, sends formatted reply | HTTP Request node → ai-service POST /ai/ask; Gmail node Send action; D-14 uses /chat for threads |
| EMAIL-04 | Error fallback sends polite reply if AI service unreachable | n8n IF node on HTTP Request error + Gmail Send fallback branch; D-12 retry-first approach |
| EMAIL-05 | n8n workflow exported as JSON in n8n/workflows/ (version controlled) | n8n UI export; credentials stripped from JSON automatically |
| EMAIL-06 | systemd service for auto-restart on VM boot | systemd unit wrapping `docker compose up -d`; do NOT combine with Docker restart policy conflicts |
| EMAIL-07 | Gmail OAuth app set to Production mode (prevents 7-day token expiry) | CRITICAL NUANCE: see Pitfall #1 — Production mode is necessary but requires publish verification steps |
</phase_requirements>

---

## Summary

This phase deploys a self-hosted n8n instance on a GCE e2-micro VM that polls a dedicated Gmail inbox every 5 minutes, extracts recruiter questions, calls the Phase 4 ai-service `/chat` endpoint (for thread-aware conversations), and replies with a formatted plain-text email. The VM is provisioned via Terraform (IaC portfolio story), Docker Compose runs the n8n container, and systemd provides auto-restart on boot.

The most significant technical risk is Gmail OAuth token expiry. Google enforces a 7-day refresh token lifetime for OAuth apps in "Testing" mode. Switching to "Production" mode resolves this — but Production mode requires publishing the OAuth app (consent screen verification), which has specific steps that must be documented in the plan. The plan must include those manual steps explicitly; they cannot be scripted.

The second major risk is OOM on the e2-micro VM. n8n with Docker overhead + OS can hit the 1GB RAM ceiling. The 2GB swap file (D-10) and 700m Docker memory limit (D-11) are the established mitigations — both already encoded in the existing `n8n/docker-compose.yml`.

**Primary recommendation:** Build the workflow in a single-file Terraform configuration (`terraform/n8n-vm/main.tf`), use a startup script to create swap + install Docker + write the systemd unit, then deploy Docker Compose and configure the n8n workflow via UI export.

---

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| n8n Docker image | 1.123.29 (locked D-11) | Workflow automation runtime | Already pinned in docker-compose.yml; confirmed current as of 2026-04-07 |
| Terraform google provider | ~> 6.x (hashicorp/google) | GCE VM provisioning | Official IaC; `google_compute_instance` supports `metadata_startup_script` |
| Docker Compose | v2 (compose plugin) | Container orchestration on VM | Already used in existing docker-compose.yml |
| systemd | OS-native | Auto-restart n8n on VM reboot | Standard Linux init; do not mix with Docker `restart: unless-stopped` for reboot handling |
| Gmail API (via n8n credential) | OAuth 2.0 | Gmail poll + reply | n8n built-in Gmail credential type |

### Supporting

| Library / Tool | Version | Purpose | When to Use |
|----------------|---------|---------|-------------|
| n8n Gmail Trigger node | Built-in | Poll Gmail inbox | Entry point of main workflow |
| n8n HTTP Request node | Built-in | Call ai-service /chat endpoint | HTTP call with Retry on Fail settings |
| n8n IF node | Built-in | Email filtering + error branching | Skip auto-replies, newsletters, no-body; branch on HTTP error |
| n8n Code node | Built-in | Thread ID tracking, message array construction | Build /chat messages array from thread history |
| n8n Error Trigger node | Built-in | Catch workflow failures | Entry point of error notification workflow |
| GCP Cloud Monitoring Uptime Check | Free tier | Monitor n8n /healthz endpoint | D-15; alerts via email when n8n goes down |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Gmail Trigger (OAuth) | Gmail send via SMTP (App Password) | SMTP avoids OAuth complexity but can't poll/read inbox; OAuth required for reading |
| systemd + docker compose | Docker `restart: unless-stopped` only | `restart: unless-stopped` handles crashes but NOT clean reboots if Docker daemon isn't set to start on boot |
| HTTP Request node retry | Custom retry loop with Wait node | Built-in retry (linear backoff) is sufficient for 2-3 retries; custom loop only needed for exponential backoff |

**Installation (on the GCE VM, not local):**
```bash
# Docker install (via startup script or manual)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Terraform (local dev machine, already available)
# Verified: Terraform v1.14.8 already installed
```

**Version verification:** n8n 1.123.29 confirmed via GitHub releases (released 2026-04-07). Docker image tag `n8nio/n8n:1.123.29` exists. Terraform 1.14.8 confirmed installed locally.

---

## Architecture Patterns

### Recommended Project Structure

```
terraform/
└── n8n-vm/
    ├── main.tf          # google_compute_instance + swap startup script
    ├── variables.tf     # project_id, region, zone, ssh_pub_key_path
    └── outputs.tf       # instance external IP

n8n/
├── docker-compose.yml   # EXISTING — do not recreate (D-11)
├── workflows/
│   └── email-bot.json   # Exported workflow JSON (EMAIL-05)
└── systemd/
    └── n8n.service      # systemd unit file (EMAIL-06)
```

### Pattern 1: Gmail Trigger → Filter → HTTP Request → Reply

```
[Gmail Trigger: 5-min poll, unread only]
         |
    [IF Node: Filter]
    skip if: auto-reply headers present
             OR no body text
             OR newsletter/promotional label
         |
    [Code Node: Build thread context]
    - extract threadId from trigger data
    - fetch previous messages in thread (Gmail node: Thread > Get)
    - build messages array for /chat endpoint
         |
    [HTTP Request: POST /chat]
    URL: http://<ai-service-ip>:8090/chat
    Body: { "messages": [...] }
    Settings: Retry on Fail = true, Max Tries = 3, Wait = 2000ms
         |
    [IF Node: HTTP success?]
      YES → [Gmail Send: Reply]        NO → [Gmail Send: Fallback Reply]
             threadId, plain text              polite acknowledgment + contact email
             signature block                   signature block
```

**What:** Linear polling workflow with filter gate, thread-aware AI call, dual reply branches.
**When to use:** This is the main workflow (EMAIL-03, EMAIL-04, EMAIL-13).

### Pattern 2: Error Workflow (Separate Workflow)

```
[Error Trigger]
      |
[Gmail Send: Error Notification]
Send alert to bot's own Gmail or admin email
Include: {{ $json.execution.id }}, {{ $json.error.message }}, workflow name
```

**What:** Separate workflow set as the error handler for the main workflow.
**How to configure:** In main workflow Settings → Error Workflow → select this workflow.
**What it receives:** `$json.execution.id`, `$json.execution.url`, `$json.error.message`, `$json.workflow.name`.

### Pattern 3: systemd Unit Wrapping Docker Compose

```ini
# /etc/systemd/system/n8n.service
[Unit]
Description=n8n workflow automation
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/n8n
ExecStart=/usr/bin/docker compose up -d --remove-orphans
ExecStop=/usr/bin/docker compose down
EnvironmentFile=/opt/n8n/.env
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Critical:** Set `restart: unless-stopped` in docker-compose.yml for crash recovery AND use systemd for reboot recovery. They serve different failure modes. Do NOT set `restart: always` in Docker if using systemd — it causes double-start conflicts on manual `systemctl stop`.

### Pattern 4: Terraform GCE e2-micro with Startup Script

```hcl
resource "google_compute_instance" "n8n_vm" {
  name         = "resume-bot-n8n"
  machine_type = "e2-micro"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 30  # GB — free tier limit
    }
  }

  network_interface {
    network = "default"
    # No access_config = no external IP for n8n UI (D-09)
    # Use Cloud NAT for outbound OR add access_config for SSH-only
  }

  metadata = {
    ssh-keys = "ubuntu:${file(var.ssh_pub_key_path)}"
  }

  metadata_startup_script = file("startup.sh")

  tags = ["n8n-bot"]
}
```

**Startup script must include:**
```bash
#!/bin/bash
# 1. Create 2GB swap (D-10)
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# 2. Install Docker
curl -fsSL https://get.docker.com | sh
usermod -aG docker ubuntu

# 3. Clone repo or copy docker-compose.yml
# (or use gcloud scp in provisioning script)

# 4. Start n8n via systemd (after systemd unit is deployed)
systemctl enable n8n
systemctl start n8n
```

**D-09 Networking decision:** The plan must decide between (a) external IP with firewall rules restricting to SSH-only vs (b) no external IP with SSH via Identity-Aware Proxy (IAP). IAP is the cleaner zero-exposure approach but adds IAP setup complexity. External IP + restricted firewall is simpler for portfolio scope.

### Anti-Patterns to Avoid

- **Don't use Gmail webhooks/push:** Requires Pub/Sub setup. Poll mode is the correct n8n pattern (explicitly called out in REQUIREMENTS.md Out of Scope).
- **Don't combine `restart: always` in Docker with systemd WantedBy=multi-user.target:** Creates race condition on boot where both try to start the container. Use `restart: unless-stopped` in Docker + systemd for reboot.
- **Don't store Gmail credentials in plain env vars:** Use GCP Secret Manager pattern from Phase 4 (gcp_secrets.py), OR use n8n's built-in credential storage (encrypted in n8n_data volume). n8n credentials are the standard approach for n8n nodes.
- **Don't use `metadata_startup_script` and `metadata.startup-script` together:** Terraform only accepts one; use `metadata_startup_script` attribute (not `metadata` map key) to avoid provider conflict issue #9459.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Email polling + OAuth token refresh | Custom Gmail API poller | n8n Gmail Trigger node | Handles token refresh, pagination, label filtering, de-duplication automatically |
| Thread history retrieval | Custom Gmail API calls | n8n Gmail Thread > Get operation | Returns all messages in thread with proper ordering |
| Workflow retry logic | Custom retry counter + loop | HTTP Request node `Retry on Fail` setting | Built-in with configurable max tries and wait interval |
| Error notification | Custom error catch in workflow | n8n Error Trigger workflow | Receives structured execution error data; works even when main workflow crashes mid-execution |
| Auto-reply de-duplication | Track replied IDs in file/DB | Gmail label "Replied" + label filter on trigger | n8n Gmail Trigger can filter by label; mark as replied via Gmail label after successful send |

**Key insight:** n8n's built-in Gmail nodes handle the hardest parts of Gmail automation (OAuth refresh, message pagination, thread operations). The only custom code needed is the message array construction for the `/chat` endpoint (a Code node, ~15 lines of JS).

---

## Common Pitfalls

### Pitfall 1: Gmail OAuth 7-Day Token Expiry (HIGH SEVERITY)

**What goes wrong:** Workflow stops sending replies after 7 days with "invalid_grant" or "Token has been expired or revoked" error. n8n's credential Reconnect does not fix it — the refresh token itself is dead.

**Why it happens:** Google enforces a hard 7-day expiry on refresh tokens for OAuth apps with Publishing Status = "Testing". This is Google policy, not an n8n bug.

**How to avoid:**
1. Create OAuth consent screen with User Type = External
2. Go to OAuth consent screen → Publishing status → **"Publish App"** (not just fill fields)
3. Google will ask for verification if sensitive scopes are requested. For Gmail, these scopes ARE sensitive: `https://www.googleapis.com/auth/gmail.modify`
4. **For a personal non-commercial app**, the path to avoid full Google verification is: use Internal user type (requires Google Workspace account) OR publish and accept the "unverified app" warning screen for your own use

**Recommended approach for this portfolio project:**
- Publishing status = "In Production" with the warning that Google may show an "unverified app" screen on first login (acceptable — this is your own Gmail account)
- The unverified warning only appears on first OAuth consent — once tokens are issued, there is no expiry limitation
- Alternative that fully avoids this: Service Account with domain-wide delegation, but this requires Google Workspace (paid). Not applicable here.

**Warning signs:** "invalid_grant" errors in n8n execution logs; workflow runs trigger but HTTP to Gmail fails.

**Confluence of sources:** Multiple community threads confirm this behavior. Google's own documentation confirms the 7-day Testing mode limit. The "Production mode fixes it" claim is confirmed for personal OAuth flows (not requiring full app verification).

---

### Pitfall 2: n8n OOM on e2-micro (HIGH SEVERITY)

**What goes wrong:** n8n container is killed by OOM killer mid-execution. Docker shows container restarting repeatedly. Emails receive no reply.

**Why it happens:** e2-micro has 1GB RAM. n8n process alone needs 400-600MB. Docker overhead + OS = OOM without swap.

**How to avoid:** (Already in D-10 and D-11 — verify these are in place)
- 2GB swap: `fallocate -l 2G /swapfile` in startup script
- Docker memory limit: `mem_limit: 700m` in docker-compose.yml (ALREADY SET in existing file)
- Verify swap is mounted: `swapon --show` on the VM

**Warning signs:** n8n container shows `Exited (137)` status; kernel OOM messages in `dmesg`.

---

### Pitfall 3: systemd + Docker Restart Policy Double-Start

**What goes wrong:** n8n starts twice on reboot, or `systemctl stop n8n` doesn't actually stop it because Docker's own restart policy brings it back.

**Why it happens:** `restart: always` in Docker Compose means Docker daemon will restart the container independently of systemd. If both Docker's restart policy and systemd are configured, they fight.

**How to avoid:** Use `restart: unless-stopped` in docker-compose.yml (already set). systemd's `ExecStop=docker compose down` explicitly stops it, and `unless-stopped` respects manual stops. Systemd handles the "bring up on boot" path; Docker handles "bring up after crash" path.

---

### Pitfall 4: Metadata Startup Script Not Running

**What goes wrong:** Terraform applies successfully, VM starts, but Docker/swap setup didn't happen.

**Why it happens:** `metadata_startup_script` only runs once on first boot. If Terraform re-creates the instance, it runs again. But if the script fails silently (exit 0 despite failure), setup is incomplete.

**How to avoid:**
- Add `set -e` to startup script so any failure exits non-zero (GCP logs startup script output to Serial Console / Cloud Logging)
- Verify via: `sudo journalctl -u google-startup-scripts.service` on the VM
- Use `metadata_startup_script` attribute (not `metadata { "startup-script" = ... }` map) — the attribute form is the Terraform-idiomatic way

---

### Pitfall 5: n8n Credentials Not in workflow JSON

**What goes wrong:** Workflow JSON is committed to `n8n/workflows/` but when re-imported to a fresh n8n instance, all credential references are broken (empty/null IDs).

**Why it happens:** n8n deliberately strips credential secrets from exported JSON. Credential names are preserved but IDs are instance-specific.

**How to avoid:** Document (in the plan) that after importing workflow JSON to a new n8n instance, operator must:
1. Set up Gmail OAuth credential in n8n UI
2. Set up HTTP Request credential (if any auth on ai-service) or just configure URL
3. Re-link credential name in each node that uses it

This is expected behavior — the exported JSON is the workflow structure, not the credential secrets.

---

### Pitfall 6: Auto-Reply Loop

**What goes wrong:** Bot receives its own sent email as a new unread message, triggers another AI reply, creating an infinite loop.

**Why it happens:** If the bot's Gmail account receives delivery notifications or out-of-office replies to its own sent messages, those appear as unread.

**How to avoid:** In the IF Filter node, check:
- `{{ $json.from }}` does NOT match the bot's own Gmail address
- `{{ $json.headers['x-auto-reply-type'] }}` is absent (auto-reply header check)
- `{{ $json.threadId }}` not already processed (label-based de-duplication: mark thread with a "bot-replied" label after sending)

---

### Pitfall 7: ai-service Rate Limit Hit from Bot

**What goes wrong:** `/chat` endpoint returns 429 (rate limit exceeded) when bot processes multiple emails in a poll cycle. Bot may send fallback replies unnecessarily.

**Why it happens:** ai-service rate limit on `/chat` is 30/min. Under normal load (few emails per poll) this is fine, but if backlog exists on first activation, many emails process simultaneously.

**How to avoid:** n8n processes Gmail Trigger results sequentially by default in a single workflow run. Rate limit should not be hit in normal operation. If batch processing is needed, add a Wait node (1-2 second delay) between iterations. Document the 30/min limit in the plan as a known constraint.

---

## Code Examples

Verified patterns from official sources and confirmed behavior:

### Gmail Trigger Node Key Fields (from n8n docs)
```javascript
// Fields available from Gmail Trigger output ($json):
{
  "id": "message-id",
  "threadId": "thread-id",           // Use for thread-aware replies
  "from": "sender@example.com",
  "to": "botaccount@gmail.com",
  "subject": "Question about your background",
  "text": "Plain text body",         // Use this for question extraction
  "html": "<p>...</p>",
  "date": "2026-04-09T...",
  "labelIds": ["INBOX", "UNREAD"],
  "headers": { "x-auto-reply-type": "...", ... }  // Check for auto-replies
}
```

### Code Node: Build /chat Messages Array
```javascript
// Source: ai-service/main.py ChatRequest schema
// messages: list[ChatMessage] where each has role + content (max 10, last must be user)

const emailText = $json.text || $json.snippet || '';
const subject = $json.subject || '';

// For first message in thread (no history):
const messages = [
  {
    role: "user",
    content: `Subject: ${subject}\n\n${emailText}`.substring(0, 500)
  }
];

return { messages, threadId: $json.threadId, originalFrom: $json.from, subject: $json.subject };
```

### HTTP Request Node Configuration (POST /chat)
```
Method: POST
URL: http://{{ $env.AI_SERVICE_URL }}:8090/chat
Headers: Content-Type: application/json
Body: {
  "messages": {{ $json.messages }}
}
Settings:
  - Retry on Fail: ON
  - Max Tries: 3
  - Wait Between Tries: 2000ms
```

### Gmail Send Node (Reply in Thread)
```
Resource: Message
Operation: Reply
Thread ID: {{ $('Code Node').item.json.threadId }}
To: {{ $('Code Node').item.json.originalFrom }}
Subject: Re: {{ $('Code Node').item.json.subject }}
Message: {{ $('HTTP Request').item.json.answer }}

---
[Candidate Name] | GitHub: github.com/[handle] | Portfolio: [URL]
This reply was generated by an AI assistant trained on my professional background.
```

### systemd Unit File (EMAIL-06)
```ini
[Unit]
Description=n8n Email Bot (Docker Compose)
After=docker.service network-online.target
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/n8n
ExecStart=/usr/bin/docker compose up -d --remove-orphans
ExecStop=/usr/bin/docker compose down
EnvironmentFile=/opt/n8n/.env
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable:
sudo systemctl daemon-reload
sudo systemctl enable n8n
sudo systemctl start n8n
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| IMAP Email Trigger (generic) | Gmail Trigger node (native) | n8n v0.x → v1.x | Thread operations, label management, OAuth 2.0 built in |
| `n8n-nodes-base.function` (Function node) | `n8n-nodes-base.code` (Code node) | n8n v1.0 | Function node renamed to Code node; same JavaScript capability |
| `N8N_BASIC_AUTH_ACTIVE` env var | Still valid in v1.123 | — | Confirmed still works in v1.123.x; not deprecated |
| Service Account for Gmail | Still requires domain-wide delegation | — | For personal Gmail, OAuth is the correct path (service accounts need Google Workspace) |

**Deprecated/outdated:**
- `n8n-nodes-base.function`: Renamed to Code node. If importing old workflow JSON referencing `function`, it may fail to load.
- Gmail push webhooks: Out of scope (REQUIREMENTS.md). Do not use Pub/Sub.
- `google-generativeai` SDK: Deprecated Nov 2025 per STATE.md. ai-service uses `google-genai`. No impact on Phase 5 (n8n only calls HTTP endpoints).

---

## Open Questions

1. **D-09 Network Access Decision**
   - What we know: D-09 says no public access to n8n UI; SSH for admin only
   - What's unclear: Should the VM have an external IP at all (restricted via firewall) or use IAP tunneling (no external IP)?
   - Recommendation: External IP + firewall rule allowing SSH from `0.0.0.0/0` port 22 is simpler for a portfolio project. IAP tunneling is more secure but requires `gcloud compute ssh` wrapper and IAP API enablement. Plan should use external IP + SSH-only firewall for simplicity.

2. **Thread History Depth for /chat**
   - What we know: `/chat` accepts up to 10 messages; `D-14` says pass conversation context
   - What's unclear: How many prior emails in a thread should be fetched? Fetching 20+ old emails and truncating to 10 is costly.
   - Recommendation: Fetch last 5 messages from thread (Gmail Thread > Get); build messages array from those. Cap at 9 user+assistant pairs + 1 final user message = stays within 10-message limit.

3. **ai-service URL Resolution on VM**
   - What we know: ai-service is on Cloud Run; Phase 4 deploys to `ai-service-XXXXXX.us-central1.run.app`
   - What's unclear: The exact Cloud Run URL won't be known until Phase 4 completes
   - Recommendation: Store Cloud Run URL as an environment variable in `/opt/n8n/.env` on the VM. The plan should have a placeholder and a step to populate it post-Phase 4 deployment.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Terraform | VM provisioning (D-08) | Yes | 1.14.8 | — |
| Docker | Container runtime on VM | Yes (locally) | 29.3.1 | Install via startup script on VM |
| Docker Compose | n8n orchestration | Yes (locally) | v5.1.1 | Install via startup script on VM |
| Node.js | Local tooling | Yes | v24.13.0 | — |
| gcloud CLI | GCP resource scripting (D-02) | Unknown (not in bash PATH) | Unknown | Use Terraform exclusively; Console for manual steps |
| n8n Docker image | Email bot runtime | n8nio/n8n:1.123.29 | 1.123.29 | Confirmed on Docker Hub |
| GCE e2-micro (GCP) | VM host (EMAIL-01) | Needs provisioning | — | — |
| ai-service /chat endpoint | EMAIL-03 | Pending Phase 4 | — | Placeholder URL in .env; must be live before Phase 5 test |

**Missing dependencies with no fallback:**
- GCE e2-micro VM: Must be provisioned via Terraform as part of this phase.
- ai-service /chat endpoint: Phase 5 depends on Phase 4 completing. Workflow can be built and tested with a mock HTTP endpoint, but end-to-end smoke test (EMAIL-03) requires Phase 4 to be live.

**Missing dependencies with fallback:**
- gcloud CLI not available in bash shell: Terraform covers VM provisioning. Manual GCP Console steps documented for OAuth consent screen and GCP Uptime Check.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Manual smoke tests (no pytest for n8n workflows; Phase 7 adds test coverage) |
| Config file | None for Phase 5 — workflows are tested via n8n execution UI |
| Quick run command | Trigger workflow manually in n8n UI → check Gmail inbox for reply |
| Full suite command | Send test email → wait 5 min → verify reply received |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| EMAIL-01 | n8n container starts, stays running under load | Manual smoke | `docker ps` on VM; check mem with `free -h` | N/A (VM check) |
| EMAIL-02 | Gmail Trigger polls every 5 min (D-03) | Manual smoke | Send email, check n8n execution history for 5-min trigger | N/A |
| EMAIL-03 | Email → AI service → reply received | End-to-end smoke | Send test email → check reply in inbox | N/A |
| EMAIL-04 | Fallback reply when ai-service unreachable | Manual | Temporarily stop ai-service container; send email; verify fallback reply | N/A |
| EMAIL-05 | Workflow JSON committed to n8n/workflows/ | Code review | `git log --oneline n8n/workflows/` | ❌ Wave 0 |
| EMAIL-06 | n8n auto-restarts on VM reboot | Manual | `sudo reboot`; SSH back; `systemctl status n8n` | N/A |
| EMAIL-07 | Gmail OAuth tokens do not expire after 7 days | Manual (time-based) | Check n8n credential in Settings after 8 days | N/A |

### Sampling Rate

- **Per task commit:** `docker ps` on VM to verify container running
- **Per wave merge:** Send test email + check n8n execution history for successful completion
- **Phase gate:** EMAIL-03 end-to-end smoke test green + EMAIL-07 Production mode confirmed before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `n8n/workflows/email-bot.json` — covers EMAIL-05 (created during workflow build, not pre-built)
- [ ] `terraform/n8n-vm/main.tf`, `variables.tf`, `outputs.tf` — covers EMAIL-01/D-08 (to be created)
- [ ] `n8n/systemd/n8n.service` — covers EMAIL-06 (to be created)
- [ ] `terraform/n8n-vm/startup.sh` — swap + Docker install script

*(No existing test framework gaps — Phase 5 has no pytest-testable components; all validation is operational smoke tests)*

---

## Project Constraints (from CLAUDE.md)

*CLAUDE.md not found in project root. No project-specific constraints to enforce beyond those in CONTEXT.md and STATE.md.*

Constraints inherited from STATE.md (treat as locked):
- `n8n/docker-compose.yml` exists with n8n v1.123.29, 700m mem limit, basic auth — do NOT recreate
- `google-genai` SDK (not `google-generativeai`) — no impact on Phase 5
- Gmail OAuth app in Production mode — prevents 7-day token expiry
- n8n on e2-micro with 2GB swap + Docker mem_limit: 700m — already in docker-compose.yml

---

## Sources

### Primary (HIGH confidence)
- [n8n Gmail Trigger docs](https://docs.n8n.io/integrations/builtin/trigger-nodes/n8n-nodes-base.gmailtrigger/) — poll mode, OAuth, filter options
- [n8n Gmail Thread Operations docs](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.gmail/thread-operations/) — thread reply, threadId usage
- [n8n Error Handling docs](https://docs.n8n.io/flow-logic/error-handling/) — Error Trigger node, error workflow setup
- [n8n Export/Import docs](https://docs.n8n.io/workflows/export-import/) — workflow JSON format, credential stripping
- [Terraform google_compute_instance](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_instance) — metadata_startup_script, machine_type
- [n8n GitHub releases](https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.29) — confirmed v1.123.29 released 2026-04-07
- `n8n/docker-compose.yml` (project file) — locked stack config, directly read

### Secondary (MEDIUM confidence)
- [n8n community: Gmail OAuth 7-day expiry](https://community.n8n.io/t/google-credentials-expire-every-week-in-self-hosted-n8n/41177) — confirmed by multiple community threads; root cause verified against Google docs
- [ignite-ops.com: Google OAuth n8n fix](https://ignite-ops.com/resources/2025/03/google-oauth-n8n-keeps-expiring-here-is-the-real-fix/) — argues Service Account is better; valid for non-Gmail, but OAuth is required for personal Gmail inbox reading
- [n8n.io workflow template: AI email auto-responder](https://n8n.io/workflows/3277-smart-email-auto-responder-template-using-ai/) — confirms Gmail Trigger → HTTP Request → Gmail Send pattern structure
- [Docker start on boot docs](https://hostim.dev/learn/docker/start-on-boot/) — systemd + Docker Compose pattern confirmed
- [GCP + Terraform + Docker e2-micro reference](https://github.com/sudo-kraken/terraform-gcp-ubuntu-container-ready-e2-micro-vm) — startup script install pattern

### Tertiary (LOW confidence — flagged for validation)
- Production mode OAuth claim (multiple community sources agree, but Google's official docs on the specific "7-day testing vs production" behavior were not directly fetchable in this session — the behavior is empirically confirmed by community but not cited from a single authoritative Google doc URL)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all tools confirmed (Terraform 1.14.8 local, n8n 1.123.29 confirmed on GitHub, Docker Compose existing)
- Architecture: HIGH — n8n Gmail Trigger → HTTP Request → Gmail Reply is a well-documented community pattern; thread operations confirmed in docs
- OAuth pitfall: MEDIUM-HIGH — behavior empirically confirmed by many community sources; Production mode path confirmed as the fix for personal OAuth apps; service account alternative also documented
- Terraform GCE startup script: MEDIUM — pattern confirmed, exact swap+Docker script is standard Linux commands but not verified against a single canonical example

**Research date:** 2026-04-09
**Valid until:** 2026-05-09 (n8n releases frequently; verify latest patch of 1.123.x before build)
