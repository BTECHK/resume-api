# Gmail OAuth Setup for Phase 5 Email Bot

This runbook covers EMAIL-07 (Gmail OAuth in Production mode). **CRITICAL**: If you skip the "Publish App" step, the refresh token will expire after 7 days and the bot will stop sending replies. This is Google policy, not an n8n bug.

The 7-day expiry only affects OAuth apps with Publishing status = "Testing". Publishing the app (even as an unverified app for personal use) removes this limit. This runbook walks through every Console click plus the gcloud CLI steps that D-02 prefers.

## Prerequisites

- GCP project from Phase 4 (same `project_id` used in `terraform/n8n-vm` variables)
- Ability to create a new Gmail account (personal, not through the candidate's primary inbox)
- n8n VM provisioned by Plan 05-01 so you know the VM external IP for the OAuth redirect URI — run `terraform -chdir=terraform/n8n-vm output instance_ip` to retrieve it
- gcloud CLI installed and authenticated: `gcloud auth login && gcloud config set project $PROJECT_ID`

Reference sibling docs: `n8n/docs/oauth-consent-screen-config.md` (field values) and `n8n/.env.example` (template for `/opt/n8n/.env` on the VM).

## Step 1 — Create Dedicated Gmail Account (D-01)

1. Open https://accounts.google.com/signup in an incognito window (so you don't contaminate your personal Google session).
2. Suggested handle: `resume-bot-[your-handle]@gmail.com`.
3. Record the address and password in a secure password manager.
4. Do NOT use your personal Gmail — D-01 locks this decision.
5. Enable 2FA on the bot account to satisfy Google's security expectations for "unverified app" OAuth.

## Step 2 — Enable Gmail API in GCP Project

Preferred (D-02 — scripted CLI path):

```bash
gcloud services enable gmail.googleapis.com --project=$PROJECT_ID
gcloud services list --enabled --filter="gmail.googleapis.com" --project=$PROJECT_ID
```

Alternative (GCP Console): APIs & Services → Library → Gmail API → Enable.

## Step 3 — Configure OAuth Consent Screen

Console → APIs & Services → OAuth consent screen. Use these values (also captured in `oauth-consent-screen-config.md`):

- User Type: **External** (Internal requires Google Workspace)
- App name: `Resume Bot Phase 5`
- User support email: your personal email
- Developer contact: your personal email
- Authorized domains: leave empty (no domain for personal use)
- App logo / home page / privacy / terms: leave empty

Click "Save and continue".

## Step 4 — Add Gmail Scopes

On the Scopes page click "Add or Remove Scopes" and add:

- `https://www.googleapis.com/auth/gmail.modify` — read inbox, label, mark as read
- `https://www.googleapis.com/auth/gmail.send` — send replies

These are "Sensitive scopes" — Google displays a warning. Proceed. Do NOT add `gmail.readonly` or `gmail.metadata`: `gmail.modify` supersedes both, and stacking scopes only slows the consent flow.

## Step 5 — Add Test Users (Temporary)

Add the dedicated bot Gmail address from Step 1 as a Test User. This lets you exercise the OAuth flow before the app is published. You will still publish later — this step just makes the pre-publish testing path work.

## Step 6 — Create OAuth 2.0 Client ID

**D-02 compliance note:** D-02 says "script OAuth client creation via gcloud CLI where possible". For Web Application OAuth 2.0 clients, THIS IS THE DOCUMENTED EXCEPTION: `gcloud iap oauth-clients create` only creates IAP (Identity-Aware Proxy) clients, not general-purpose Web Application clients needed by n8n's Gmail node. There is no gcloud command for creating `type=Web application` OAuth 2.0 clients as of GCP SDK ~480.x. The GCP Console is therefore the only supported path for this specific step — this is a KNOWN limitation, not a D-02 violation. All other steps in this runbook (Gmail API enablement in Step 2, project configuration) DO use gcloud per D-02.

1. Console → APIs & Services → Credentials → Create Credentials → OAuth client ID
2. Application type: **Web application**
3. Name: `n8n Gmail Client`
4. Authorized redirect URIs: `https://<N8N_VM_EXTERNAL_IP>:5678/rest/oauth2-credential/callback`
   - Use the `instance_ip` output from `terraform -chdir=terraform/n8n-vm output`
   - If you don't have a domain, the IP-based URI is acceptable for personal use
5. Create → download the JSON or copy the `client_id` + `client_secret` to a secure temporary location.

## Step 7 — **PUBLISH THE APP** (EMAIL-07, Pitfall #1)

**CRITICAL STEP — DO NOT SKIP.** This is the step that eliminates the 7-day refresh token expiry.

1. Console → APIs & Services → OAuth consent screen
2. Publishing status: **Testing → Publish App**
3. Confirm in the dialog ("PUBLISH").
4. Publishing status MUST now read: **"In production"**.
5. Google will show an "unverified app" warning on first OAuth consent — this is expected for a personal non-commercial app. Click "Advanced" → "Go to Resume Bot Phase 5 (unsafe)" to proceed. This warning only appears once per user.
6. After publishing, refresh tokens will no longer expire after 7 days. This is the entire reason for Pitfall #1 and D-04.

If Publishing status still reads "Testing" after this step, redo it before continuing — otherwise the bot will silently fail in ~7 days.

## Step 8 — Populate `/opt/n8n/.env` on the VM

1. SSH to the VM using the `ssh_command` output from `terraform -chdir=terraform/n8n-vm output`.
2. Edit `/opt/n8n/.env` based on the template at `n8n/.env.example` in the repo.
3. Paste `client_id` and `client_secret` into `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`.
4. Set `BOT_GMAIL_ADDRESS` to the dedicated Gmail from Step 1.
5. Set `CANDIDATE_*` values per D-06 / D-12.
6. Save, then `sudo systemctl restart n8n`.

## Step 9 — Verify in n8n UI

1. SSH port forward: `ssh -L 5678:localhost:5678 ubuntu@<VM_IP>`
2. Open `http://localhost:5678`, log in with `N8N_USER` / `N8N_PASSWORD`.
3. n8n → Credentials → Add Credential → Gmail OAuth2 API.
4. Paste `client_id` + `client_secret` → "Connect my account".
5. Sign in with the dedicated bot Gmail (NOT your personal Gmail).
6. Accept the unverified app warning (one-time).
7. Confirm the credential saves successfully.

## Verification (time-based)

- **Immediately after setup:** send a test email to the bot Gmail; confirm it appears in the n8n Gmail Trigger test run.
- **8 days later:** re-run a workflow manually; confirm it still sends. This is the only way to empirically prove the 7-day token death no longer applies — EMAIL-07 verified.

## Troubleshooting

- `"invalid_grant"` error → consent screen is still in Testing mode; re-check Step 7 and confirm Publishing status = "In production".
- `"unverified app"` warning loop → this is expected once per user the first time they consent; click through Advanced → Go to app. It does not repeat.
- Token not refreshing → delete the n8n credential and recreate from scratch after confirming Step 7.
- Redirect URI mismatch → verify the exact `https://<N8N_VM_EXTERNAL_IP>:5678/rest/oauth2-credential/callback` matches the value stored under the OAuth 2.0 Client ID in Console.
