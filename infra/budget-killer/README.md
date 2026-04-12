# Budget Killer

Cloud Function that listens on a Pub/Sub topic fed by a GCP Budget and **disables
billing on the target project** when spend meets or exceeds the budget amount.

## Deployment sequence

All commands below assume:

- `PROJECT_ID=resume-bot-493100`
- `REGION=us-central1`
- `TOPIC=resume-bot-budget-alerts`
- `SA=budget-killer`

### 1. Enable APIs

```bash
gcloud services enable \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  eventarc.googleapis.com \
  run.googleapis.com \
  cloudbilling.googleapis.com \
  --project=$PROJECT_ID
```

### 2. Create dedicated service account

```bash
gcloud iam service-accounts create $SA \
  --display-name="Budget Killer" \
  --project=$PROJECT_ID
```

### 3. Grant Billing Account Administrator on the billing account

Find the billing account ID:

```bash
gcloud billing accounts list
```

Then:

```bash
BILLING_ACCOUNT_ID=<paste from above>
gcloud billing accounts add-iam-policy-binding $BILLING_ACCOUNT_ID \
  --member="serviceAccount:${SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/billing.admin"
```

### 4. Deploy the function

From inside `infra/budget-killer/`:

```bash
gcloud functions deploy stop-billing \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=stop_billing \
  --trigger-topic=$TOPIC \
  --service-account="${SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --set-env-vars="TARGET_PROJECT_ID=$PROJECT_ID" \
  --project=$PROJECT_ID
```

### 5. Dry-run test (SAFE — publishes a cost < budget)

```bash
gcloud pubsub topics publish $TOPIC \
  --message='{"budgetDisplayName":"dry-run","costAmount":0.01,"budgetAmount":10.0,"currencyCode":"USD"}' \
  --project=$PROJECT_ID

# Wait ~15s, then check logs:
gcloud functions logs read stop-billing --gen2 --region=$REGION --project=$PROJECT_ID
```

Expected log line: `Under budget — no action.`

### 6. Live test (DESTRUCTIVE — actually disables billing)

Only run this if you want to verify the kill switch works and are prepared to
re-link billing afterward.

```bash
gcloud pubsub topics publish $TOPIC \
  --message='{"budgetDisplayName":"kill-test","costAmount":99.99,"budgetAmount":10.0,"currencyCode":"USD"}' \
  --project=$PROJECT_ID
```

Verify billing was disabled:

```bash
gcloud billing projects describe $PROJECT_ID
# billingEnabled should be false
```

### Re-enable billing after a kill

```bash
gcloud billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT_ID
```
