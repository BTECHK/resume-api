#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# GCP Infrastructure Setup for ai-service
#
# Run these commands manually after reviewing. Each section is
# idempotent — safe to re-run.
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - GCP project created with billing enabled
#   - Artifact Registry API enabled
#   - Secret Manager API enabled
#
# Usage:
#   export GCP_PROJECT_ID=your-project-id
#   bash ai-service/gcp-setup.sh
# ──────────────────────────────────────────────────────────────

set -euo pipefail

# ── Configuration ──────────────────────────────────────────────
# Override any of these via env vars before running the script.
PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID env var}"
: "${REGION:=us-central1}"
: "${AR_REPO:=resume-api}"
: "${SERVICE_ACCOUNT:=resume-ai-service}"

echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# ── 1. Enable required APIs ───────────────────────────────────
echo ""
echo "=== API ENABLEMENT ==="
echo "Enabling APIs..."
gcloud services enable \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  --project="$PROJECT_ID"

# ── 2. Secret Manager: Create gemini-api-key secret (SEC-05) ──
# The actual key value must be provided interactively.
# Get your key from: https://aistudio.google.com/apikey
echo ""
echo "=== SECRET MANAGER SETUP (SEC-05) ==="
echo "Creating secret 'gemini-api-key'..."

if gcloud secrets describe gemini-api-key --project="$PROJECT_ID" 2>/dev/null; then
  echo "Secret 'gemini-api-key' already exists — skipping creation"
else
  echo "Enter your Gemini API key (from https://aistudio.google.com/apikey):"
  read -rs GEMINI_KEY
  echo -n "$GEMINI_KEY" | gcloud secrets create gemini-api-key \
    --data-file=- \
    --replication-policy="automatic" \
    --project="$PROJECT_ID"
  echo "Secret created successfully"
fi

# ── 3. IAM: Grant Cloud Run service account secret access ──────
echo ""
echo "=== IAM SETUP ==="
# Create a dedicated service account for the AI service (least-privilege principle)
SA_EMAIL="${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com"

# Create service account if it doesn't exist
if gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT_ID" 2>/dev/null; then
  echo "Service account $SA_EMAIL already exists — skipping creation"
else
  gcloud iam service-accounts create "$SERVICE_ACCOUNT" \
    --display-name="Resume AI Service" \
    --project="$PROJECT_ID"
  echo "Service account created: $SA_EMAIL"
fi

# Grant Secret Manager access (secretAccessor role — read-only, least privilege)
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor" \
  --project="$PROJECT_ID"
echo "Granted roles/secretmanager.secretAccessor to $SA_EMAIL"

# ── 4. Artifact Registry: Create repo + pruning policy (SEC-09) ─
echo ""
echo "=== ARTIFACT REGISTRY SETUP (SEC-09) ==="

# Create repository if it doesn't exist
if gcloud artifacts repositories describe "$AR_REPO" \
  --location="$REGION" \
  --project="$PROJECT_ID" 2>/dev/null; then
  echo "Repository $AR_REPO already exists — skipping creation"
else
  gcloud artifacts repositories create "$AR_REPO" \
    --repository-format=docker \
    --location="$REGION" \
    --description="Resume API container images" \
    --project="$PROJECT_ID"
fi
echo "Repository: ${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}"

# Set cleanup policy — keep only the 10 most recent versions per tag.
# This prevents unbounded storage growth (SEC-09).
# Policy: delete images older than 30 days, but always keep the 10 most recent.
cat > /tmp/ar-cleanup-policy.json << 'POLICY'
[
  {
    "name": "keep-recent-10",
    "action": {"type": "Delete"},
    "condition": {
      "tagState": "any",
      "olderThan": "2592000s"
    },
    "mostRecentVersions": {
      "keepCount": 10
    }
  }
]
POLICY

# Note: set-cleanup-policies may require gcloud beta in some versions
gcloud artifacts repositories set-cleanup-policies "$AR_REPO" \
  --location="$REGION" \
  --policy=/tmp/ar-cleanup-policy.json \
  --project="$PROJECT_ID" 2>/dev/null || \
  echo "WARNING: Cleanup policy not applied. May require 'gcloud beta artifacts' — run manually if needed."

rm -f /tmp/ar-cleanup-policy.json
echo "Artifact Registry configured with keep-10-versions cleanup policy"

# ── 5. Billing Alert at $1 (SEC-08) ──────────────────────────
echo ""
echo "=== BILLING ALERT SETUP (SEC-08) ==="
echo ""
echo "OPTION A — GCP Console (recommended, most reliable):"
echo "  1. Go to: https://console.cloud.google.com/billing/budgets"
echo "  2. Click 'Create Budget'"
echo "  3. Set budget amount to \$1.00 USD"
echo "  4. Set alert thresholds at 50%, 90%, 100%"
echo "  5. Enable email notifications to your billing admin address"
echo ""
echo "OPTION B — gcloud CLI (requires billing account ID):"
echo "  # First: find your billing account ID"
echo "  BILLING_ACCOUNT=\$(gcloud billing projects describe $PROJECT_ID --format='value(billingAccountName)' | cut -d/ -f2)"
echo "  echo \"Billing account: \$BILLING_ACCOUNT\""
echo ""
echo "  # Then: create the budget (run these commands manually)"
echo "  gcloud billing budgets create \\"
echo "    --billing-account=\$BILLING_ACCOUNT \\"
echo "    --display-name='Resume API \$1 Alert' \\"
echo "    --budget-amount=1.00USD \\"
echo "    --threshold-rule=percent=0.5 \\"
echo "    --threshold-rule=percent=0.9 \\"
echo "    --threshold-rule=percent=1.0 \\"
echo "    --filter-projects=projects/$PROJECT_ID"
echo ""
echo "NOTE: Budget alerts are advisory — they do NOT automatically stop services."
echo "      For hard spend limits, consider setting a Cloud Run max-instances=1 and"
echo "      Artifact Registry cleanup policy (already configured above)."

# ── Done ──────────────────────────────────────────────────────
echo ""
echo "=== SETUP COMPLETE ==="
echo ""
echo "Verification commands:"
echo "  # Confirm secret exists:"
echo "  gcloud secrets versions access latest --secret=gemini-api-key --project=$PROJECT_ID"
echo ""
echo "  # Confirm IAM binding:"
echo "  gcloud secrets get-iam-policy gemini-api-key --project=$PROJECT_ID"
echo ""
echo "  # Confirm Artifact Registry repo:"
echo "  gcloud artifacts repositories list --location=$REGION --project=$PROJECT_ID"
echo ""
echo "Next steps:"
echo "  1. Create billing budget via Console at https://console.cloud.google.com/billing/budgets"
echo "  2. Deploy ai-service to Cloud Run with --service-account=$SA_EMAIL"
echo "  3. Pass GCP_PROJECT_ID as Cloud Run env var for Secret Manager access"
