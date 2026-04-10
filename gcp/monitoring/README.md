# GCP Monitoring — n8n VM Uptime Check

Purpose: Phase 5 free-tier uptime monitoring for the n8n email bot VM per decision D-15.

## What this provisions

The script `n8n-uptime-check.sh` creates (idempotently):

1. A Cloud Monitoring **email notification channel** pointed at `$ALERT_EMAIL`
2. A Cloud Monitoring **uptime check** (`n8n-vm-uptime`) that performs a TCP
   liveness probe against the n8n VM on SSH port 22

Cloud Monitoring API (`monitoring.googleapis.com`) is auto-enabled on first run.

## Usage

```bash
PROJECT_ID=your-project ALERT_EMAIL=you@example.com \
  bash gcp/monitoring/n8n-uptime-check.sh
```

Optional overrides:

- `INSTANCE_NAME` (default: `resume-bot-n8n`) — must match `terraform/n8n-vm/variables.tf`
- `ZONE` (default: `us-central1-a`)

## Limitation: TCP vs HTTP health

This check proves the **VM is reachable on port 22**. It does NOT prove that:

- The n8n container is actually running (`docker ps`)
- The n8n process is responding on `http://localhost:5678/healthz`
- The Gmail Trigger is authenticated and polling

Container-level monitoring requires one of:

1. An **nginx reverse-proxy sidecar** exposing `/healthz` on port 80, with a firewall
   rule allowing only GCP uptime-check IP ranges. This lets the uptime check probe
   HTTP.
2. Install the **Google Ops Agent** on the VM and use process-health metrics against
   the `resume-bot-n8n` Docker container.

Both of these are **out of Phase 5 scope** (documented in `.planning/phases/05-n8n-email-bot/05-CONTEXT.md` deferred ideas). The TCP-22 check is the minimum-viable free-tier option.

## Manual Console path (fallback)

If the script fails or gcloud CLI is unavailable:

1. Console → **Monitoring** → **Uptime checks** → **Create Uptime Check**
2. Target type: **URL**; Host: `<VM external IP>`; Protocol: **TCP**; Port: `22`
3. Check interval: 5 minutes; Timeout: 10 seconds
4. Notifications: select/create an email channel with `$ALERT_EMAIL`
5. Name: `n8n-vm-uptime`; Save

## How to verify

```bash
gcloud monitoring uptime list-configs --project=$PROJECT_ID \
  --filter="displayName=n8n-vm-uptime"
```

Must return a non-empty result after the script runs successfully.

## How to tear down

```bash
gcloud monitoring uptime delete n8n-vm-uptime --project=$PROJECT_ID
gcloud alpha monitoring channels delete <channel-id> --project=$PROJECT_ID
```

## Related files

- `terraform/n8n-vm/` — provisions the VM this check monitors
- `n8n/docker-compose.yml` — defines the `/healthz` endpoint (internal only per D-09)
- `n8n/docs/end-to-end-smoke-test.md` — Pre-flight check also uses `curl http://localhost:5678/healthz` from inside the VM
