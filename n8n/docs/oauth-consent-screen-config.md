# OAuth Consent Screen Configuration Reference

Exact field values for Phase 5 Gmail OAuth setup. Used as input to
`gmail-oauth-setup.md` Step 3.

| Field | Value |
|-------|-------|
| User Type | External |
| App name | Resume Bot Phase 5 |
| User support email | [operator's personal email] |
| App logo | (leave empty) |
| Application home page | (leave empty) |
| Authorized domains | (leave empty — no domain for personal use) |
| Developer contact | [operator's personal email] |
| Publishing status | **In production** (after Step 7 of runbook) |

## Scopes

| Scope | Purpose | Sensitive? |
|-------|---------|-----------|
| `https://www.googleapis.com/auth/gmail.modify` | Read inbox, mark as read, apply labels | Yes |
| `https://www.googleapis.com/auth/gmail.send` | Send reply emails | Yes |

Do NOT add `gmail.readonly` or `gmail.metadata` — `gmail.modify` supersedes both.

## OAuth Client ID

| Field | Value |
|-------|-------|
| Type | Web application |
| Name | n8n Gmail Client |
| Authorized redirect URI | `https://<N8N_VM_IP>:5678/rest/oauth2-credential/callback` |

Replace `<N8N_VM_IP>` with the `instance_ip` output from `terraform -chdir=terraform/n8n-vm output`.

## D-02 Compliance Note

D-02 prefers gcloud CLI for OAuth client creation. However, `gcloud iap oauth-clients`
only supports Identity-Aware Proxy clients, not general-purpose `type=Web application`
OAuth 2.0 clients. The GCP Console is the only supported path for this step — this is
the documented D-02 exception. All other project/API setup in the runbook DOES use gcloud.
