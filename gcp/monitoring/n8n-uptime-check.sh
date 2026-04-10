#!/usr/bin/env bash
# Phase 5 Plan 04 Task 1 — GCP Cloud Monitoring uptime check for n8n VM
# Requirement: D-15 (GCP Uptime Check on n8n healthcheck, free tier)
#
# NOTE: n8n port 5678 is NOT publicly reachable by design (D-09).
# This uptime check therefore targets the VM's EXTERNAL IP on a
# SEPARATE exposed health endpoint. Options (document both):
#   A) Add a simple nginx container on port 80 that proxies /healthz
#      to n8n:5678/healthz, exposed via firewall rule to uptime check IPs only.
#   B) Use GCP VM "Process health" uptime check via the Monitoring agent.
#
# This script uses Option B (VM instance check on TCP port 22 SSH liveness)
# as a zero-extra-exposure fallback. For richer HTTP check, run with
# --mode=http after adding the nginx proxy (future work).

set -euo pipefail

# ──────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────
PROJECT_ID="${PROJECT_ID:-}"
INSTANCE_NAME="${INSTANCE_NAME:-resume-bot-n8n}"
ZONE="${ZONE:-us-central1-a}"
ALERT_EMAIL="${ALERT_EMAIL:-}"
CHECK_NAME="n8n-vm-uptime"
ALERT_POLICY_NAME="n8n-vm-down-alert"

# ──────────────────────────────────────────────────────────
# Validate inputs
# ──────────────────────────────────────────────────────────
if [ -z "$PROJECT_ID" ]; then
  echo "ERROR: PROJECT_ID env var required"
  echo "Usage: PROJECT_ID=my-project ALERT_EMAIL=me@example.com $0"
  exit 1
fi
if [ -z "$ALERT_EMAIL" ]; then
  echo "ERROR: ALERT_EMAIL env var required (recipient for uptime alerts)"
  exit 1
fi
if ! command -v gcloud >/dev/null 2>&1; then
  echo "ERROR: gcloud CLI not found"
  exit 1
fi

gcloud config set project "$PROJECT_ID" >/dev/null

# ──────────────────────────────────────────────────────────
# Enable Cloud Monitoring API (idempotent)
# ──────────────────────────────────────────────────────────
echo "[1/4] Enabling monitoring.googleapis.com..."
gcloud services enable monitoring.googleapis.com

# ──────────────────────────────────────────────────────────
# Resolve instance external IP
# ──────────────────────────────────────────────────────────
echo "[2/4] Resolving VM external IP for $INSTANCE_NAME in $ZONE..."
INSTANCE_IP=$(gcloud compute instances describe "$INSTANCE_NAME" \
  --zone="$ZONE" \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

if [ -z "$INSTANCE_IP" ]; then
  echo "ERROR: Could not resolve external IP for $INSTANCE_NAME"
  echo "Hint: Did Plan 01 terraform apply run successfully?"
  exit 1
fi
echo "  VM IP: $INSTANCE_IP"

# ──────────────────────────────────────────────────────────
# Create notification channel (email) — idempotent
# ──────────────────────────────────────────────────────────
echo "[3/4] Ensuring email notification channel for $ALERT_EMAIL..."
CHANNEL_ID=$(gcloud alpha monitoring channels list \
  --filter="type=email AND labels.email_address=$ALERT_EMAIL" \
  --format='value(name)' | head -n1)

if [ -z "$CHANNEL_ID" ]; then
  CHANNEL_ID=$(gcloud alpha monitoring channels create \
    --display-name="n8n Uptime Alert: $ALERT_EMAIL" \
    --type=email \
    --channel-labels="email_address=$ALERT_EMAIL" \
    --format='value(name)')
  echo "  Created channel: $CHANNEL_ID"
else
  echo "  Reusing existing channel: $CHANNEL_ID"
fi

# ──────────────────────────────────────────────────────────
# Create uptime check (TCP on SSH port 22 — proves VM is reachable)
# Idempotent: check if one with matching name already exists
# ──────────────────────────────────────────────────────────
echo "[4/4] Ensuring uptime check $CHECK_NAME targeting $INSTANCE_IP:22..."
EXISTING=$(gcloud monitoring uptime list-configs \
  --filter="displayName=$CHECK_NAME" \
  --format='value(name)' | head -n1)

if [ -z "$EXISTING" ]; then
  gcloud monitoring uptime create "$CHECK_NAME" \
    --resource-labels="host=$INSTANCE_IP" \
    --resource-type=uptime-url \
    --protocol=tcp \
    --port=22 \
    --period=5 \
    --timeout=10
  echo "  Created uptime check"
else
  echo "  Uptime check already exists: $EXISTING"
fi

cat <<EOF

────────────────────────────────────────────────────────────
Uptime check provisioned

VM:              $INSTANCE_NAME ($INSTANCE_IP)
Check:           $CHECK_NAME (TCP port 22)
Alert channel:   $CHANNEL_ID

NOTE: This is a TCP-level liveness check only. For HTTP-level
health monitoring of n8n itself, you must either:
  1. Add an nginx reverse-proxy sidecar exposing /healthz on 80, OR
  2. Install Ops Agent on the VM and use process-health metrics.

Free tier: 3 uptime checks, 1-min interval, email alerts included.
────────────────────────────────────────────────────────────
EOF
