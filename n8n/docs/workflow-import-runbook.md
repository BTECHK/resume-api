# Importing email-bot.json and error-handler.json to n8n

This runbook walks the operator through importing the Phase 5 workflow JSON
files to a running n8n instance on the GCE VM, re-linking credentials
(Pitfall #5), and running a manual dry-run execution.

**When to follow this:** After Plan 05-01 (`terraform apply`) and Plan 05-02
(Gmail OAuth setup) are both complete and the VM is running. Also after any
time the workflow JSON is re-exported from n8n and re-imported.

**Estimated time:** ~15 minutes (including OAuth credential setup).

---

## Prerequisites

Before starting:

- [ ] `terraform apply` succeeded in `terraform/n8n-vm/` and the VM is running
- [ ] `/opt/n8n/.env` on the VM has real values for every variable in
      `n8n/.env.example` (especially `AI_SERVICE_URL`, `N8N_USER`,
      `N8N_PASSWORD`, Gmail OAuth credentials, and all `CANDIDATE_*` vars)
- [ ] `sudo systemctl is-active n8n` on the VM reports `active`
- [ ] Phase 4 ai-service is deployed to Cloud Run and the URL is accessible
      (`curl https://ai-service-xxx-uc.a.run.app/health` returns 200)

---

## Step 1: SSH tunnel to the n8n UI

The n8n UI is bound to localhost on the VM (D-09 — no public exposure). Open
an SSH tunnel from your laptop:

```bash
ssh -L 5678:localhost:5678 ubuntu@$(cd terraform/n8n-vm && terraform output -raw instance_ip)
```

Leave this shell open. Verify n8n is running on the VM:

```bash
sudo systemctl is-active n8n   # expect: active
docker ps --filter name=n8n    # expect: container up
```

## Step 2: Log in to n8n

Open `http://localhost:5678` in your local browser. Log in with the values you
set in `/opt/n8n/.env`:

- Username: `N8N_USER`
- Password: `N8N_PASSWORD`

## Step 3: Create the `bot-replied` Gmail label

The "Label: Mark as Replied" node references a Gmail label called
`bot-replied`. This label must exist in the **bot** Gmail account (not your
personal Gmail).

1. Open [https://mail.google.com](https://mail.google.com) and sign in as the
   bot Gmail account (`BOT_GMAIL_ADDRESS`).
2. Left sidebar → **More** → **Create new label**.
3. Name: `bot-replied` (exact, case-sensitive).
4. Save.

This must be done via the Gmail web UI, not via n8n — n8n's Gmail node can
add existing labels but cannot create them without extra API scopes.

## Step 4: Create the Gmail OAuth2 credential in n8n

In the n8n UI:

1. Left sidebar → **Credentials** → **Add Credential**.
2. Search for **Gmail OAuth2 API** and select it.
3. Paste `GOOGLE_OAUTH_CLIENT_ID` into Client ID.
4. Paste `GOOGLE_OAUTH_CLIENT_SECRET` into Client Secret.
5. Click **Connect my account**.
6. A Google OAuth popup opens — sign in with the **bot** Gmail account.
7. If you see "Google hasn't verified this app" (unverified app warning):
   click **Advanced** → **Go to Resume Bot Phase 5 (unsafe)**. This is
   one-time; once tokens are issued, the warning does not reappear. (This is
   expected per Pitfall #1 and D-04.)
8. Accept the requested scopes.
9. Back in n8n, name the credential exactly: `Gmail Bot Account`
10. Save.

## Step 5: Import the error handler workflow first

Import order matters: the main workflow references the error handler by name,
so the error handler must exist first.

1. Left sidebar → **Workflows** → **Import from File**.
2. Select `n8n/workflows/error-handler.json` from your local checkout.
3. Open the imported workflow (`email-bot-error-handler`).
4. Click on the **Gmail Send: Error Notification** node.
5. Under **Credentials to connect with**, select `Gmail Bot Account` (Pitfall #5).
6. Save the workflow (Ctrl+S).

## Step 6: Import the main workflow

1. **Workflows** → **Import from File**.
2. Select `n8n/workflows/email-bot.json`.
3. The main workflow (`Email Bot — Phase 5`) opens in the canvas.
4. Do **NOT** activate it yet (toggle stays off).
5. Save the workflow (Ctrl+S).

## Step 7: Re-link the Gmail OAuth2 credential on every Gmail node (Pitfall #5)

n8n strips credential IDs on export. The imported JSON has placeholder
`REPLACE_AFTER_IMPORT` IDs that must be replaced manually.

In the main workflow, open each of these four nodes and select
`Gmail Bot Account` from the credential dropdown:

1. **Gmail Trigger**
2. **Gmail Send: AI Reply**
3. **Gmail Send: Fallback Reply**
4. **Label: Mark as Replied**

Save after each change. All four must show a green checkmark next to the
credential name.

## Step 8: Register the error workflow in Main Workflow settings

The main workflow's JSON references `email-bot-error-handler` by name in
`settings.errorWorkflow`, but n8n does not auto-link across import. Do this
manually:

1. Open `Email Bot — Phase 5`.
2. Top-right → **Settings** (gear icon).
3. Scroll to **Error Workflow**.
4. Select `email-bot-error-handler` from the dropdown.
5. Save.

## Step 9: Manual dry-run execution

With the workflow still **INACTIVE**:

1. Click on the **Gmail Trigger** node in the canvas.
2. Click **Execute Workflow** (or the play button on the node).
3. n8n runs a one-shot Gmail poll.
4. Watch the execution progress:
   - Gmail Trigger should run green (even if 0 unread items — this is fine).
   - If there are any unread emails matching the filter, the downstream nodes
     will execute; otherwise they remain grey (no items to process).
   - No nodes should turn red.

If the Gmail Trigger returns 0 items because the inbox is empty, that is a
**successful dry run** — it proves OAuth works and the trigger is configured
correctly.

## Step 10: Leave the workflow INACTIVE

Do NOT toggle the activation switch. Activation is Plan 05-04's smoke test.

---

## Troubleshooting

### "Credential ID invalid" / "No credential selected"
Step 7 was skipped. Open each Gmail node and re-select `Gmail Bot Account`.

### Workflow runs but no reply arrives
- Check `/opt/n8n/.env` on the VM: `CANDIDATE_NAME`, `CANDIDATE_GITHUB`,
  `CANDIDATE_PORTFOLIO`, `CANDIDATE_CONTACT_EMAIL` must all be populated.
- After editing `/opt/n8n/.env`, restart n8n on the VM:
  `sudo systemctl restart n8n` (env vars are loaded at container start).

### HTTP 429 from ai-service
Pitfall #7 — the `/chat` endpoint is rate-limited to 30 requests per minute
per IP. If the bot processes a large backlog on first activation, it can hit
this limit. Add a `Wait` node (1-2 second delay) between `Build Chat Messages`
and `HTTP Request: ai-service /chat` if this becomes a problem in practice.

### HTTP 404 on `/chat`
Verify `AI_SERVICE_URL` in `/opt/n8n/.env` does **NOT** include `:8090`.
Cloud Run exposes HTTPS on 443 implicitly — the `:8090` port only applies to
the local docker-compose dev environment. The URL should look like
`https://ai-service-abc123-uc.a.run.app` with no port suffix.

Also confirm the endpoint is `/chat` (D-14), not `/ai/ask`. Older
REQUIREMENTS.md text mentions `/ai/ask` but D-14 overrides it.

### "invalid_grant" / "Token has been expired or revoked"
Pitfall #1 — the OAuth app is still in Testing mode (7-day token expiry).
Run the `n8n/docs/gmail-oauth-setup.md` runbook and verify Publishing status
is **In production**, not **Testing**. Then re-create the credential in n8n.

### Gmail Trigger fails with 403 / insufficient scope
The OAuth consent screen is missing required scopes. The app must request:
- `https://www.googleapis.com/auth/gmail.modify` (read + modify labels)
- `https://www.googleapis.com/auth/gmail.send` (send replies)

See `n8n/docs/oauth-consent-screen-config.md`.

### n8n container exits with code 137
OOM kill (Pitfall #2). Verify the 2GB swap file is mounted on the VM:
`swapon --show` should list `/swapfile`. If not, re-run the swap setup
commands from `terraform/n8n-vm/startup.sh`.

---

## Post-Import Checklist

After completing all steps, verify:

- [ ] `email-bot-error-handler` workflow imported, 2 nodes visible
- [ ] `Email Bot — Phase 5` workflow imported, 7 nodes visible
- [ ] `Gmail Bot Account` credential exists and has a green checkmark
- [ ] All 4 Gmail nodes in the main workflow show `Gmail Bot Account` selected
- [ ] The Gmail Send node in the error handler workflow also shows
      `Gmail Bot Account` selected
- [ ] Main workflow → Settings → Error Workflow shows `email-bot-error-handler`
- [ ] `bot-replied` label exists in the bot Gmail account
- [ ] Manual Gmail Trigger execution completed without red/error state
- [ ] Main workflow is still **INACTIVE** (activation toggle off)

Once all boxes are checked, this plan's checkpoint is satisfied. Activation
happens in Plan 05-04 as part of the end-to-end smoke test.
