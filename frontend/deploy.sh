#!/usr/bin/env bash
# frontend/deploy.sh — build and deploy the resume-chatbot service to Cloud Run.
#
# Phase 6 — see .planning/phases/06-react-chatbot-frontend/06-04-PLAN.md
#
# NOT run during Phase 6 scaffold. Executed manually per
# DEFERRED-WORK.md "Phase 6 — Deferred Manual Steps" Task C.
#
# Prerequisites (all tracked in DEFERRED-WORK.md):
#   1. ai-service already deployed to Cloud Run (Phase 4 deferred — Task A)
#   2. gcloud CLI authenticated with owner/editor on the project
#   3. frontend/.env.local populated with real VITE_* values (Task B)
#   4. PROJECT_ID environment variable exported

set -euo pipefail

# ----------------------------------------------------------
# Config
# ----------------------------------------------------------
: "${PROJECT_ID:?PROJECT_ID env var is required (export PROJECT_ID=your-gcp-project)}"
: "${REGION:=us-central1}"
: "${SERVICE:=resume-chatbot}"

# ----------------------------------------------------------
# Load .env.local so build args are correct
# ----------------------------------------------------------
if [[ ! -f .env.local ]]; then
  echo "ERROR: frontend/.env.local not found." >&2
  echo "Copy .env.example to .env.local and fill in real values before running this script." >&2
  echo "  cp .env.example .env.local" >&2
  echo "  \$EDITOR .env.local" >&2
  exit 1
fi

# shellcheck disable=SC1091
set -a
source .env.local
set +a

: "${VITE_AI_SERVICE_URL:?VITE_AI_SERVICE_URL must be set in .env.local}"
: "${VITE_CANDIDATE_NAME:?VITE_CANDIDATE_NAME must be set in .env.local}"
: "${VITE_CANDIDATE_TITLE:?VITE_CANDIDATE_TITLE must be set in .env.local}"
: "${VITE_CANDIDATE_EMAIL:?VITE_CANDIDATE_EMAIL must be set in .env.local}"

# Refuse to deploy with the placeholder URL
if [[ "$VITE_AI_SERVICE_URL" == *"PLACEHOLDER"* ]]; then
  echo "ERROR: VITE_AI_SERVICE_URL is still set to the PLACEHOLDER value." >&2
  echo "Update frontend/.env.local with the real ai-service Cloud Run URL first." >&2
  echo "See DEFERRED-WORK.md Phase 6 Task B for the exact procedure." >&2
  exit 1
fi

echo "Deploying $SERVICE to $REGION in project $PROJECT_ID"
echo "  ai-service URL: $VITE_AI_SERVICE_URL"
echo "  candidate:      $VITE_CANDIDATE_NAME — $VITE_CANDIDATE_TITLE"

# ----------------------------------------------------------
# Deploy via Cloud Build (--source .)
# Build-time vars are passed via --set-build-env-vars (RESEARCH Open Q5).
# ----------------------------------------------------------
gcloud run deploy "$SERVICE" \
  --source . \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 256Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3 \
  --concurrency 80 \
  --timeout 60 \
  --project "$PROJECT_ID" \
  --set-build-env-vars "VITE_AI_SERVICE_URL=${VITE_AI_SERVICE_URL},VITE_CANDIDATE_NAME=${VITE_CANDIDATE_NAME},VITE_CANDIDATE_TITLE=${VITE_CANDIDATE_TITLE},VITE_CANDIDATE_EMAIL=${VITE_CANDIDATE_EMAIL}"

# ----------------------------------------------------------
# Print the deployed URL
# ----------------------------------------------------------
echo ""
echo "Deploy complete. Service URL:"
gcloud run services describe "$SERVICE" \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --format='value(status.url)'

echo ""
echo "NEXT: Update ai-service ALLOWED_ORIGINS to the URL above and redeploy ai-service."
echo "      See DEFERRED-WORK.md Phase 6 Task D."
