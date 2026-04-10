# Workflow Build Guide — Email Bot (Phase 5)

This guide describes the workflow structure in human-readable form. The
authoritative definition is `n8n/workflows/email-bot.json`. Use this guide when
modifying nodes in the n8n UI or when teaching a new maintainer what each node
does and why.

---

> **CRITICAL — Endpoint override and port rules (read this first).**
>
> - The HTTP Request node calls **`/chat`** per **D-14**, NOT `/ai/ask` as
>   REQUIREMENTS.md §EMAIL-03 originally said. D-14 overrides the older text to
>   enable thread-aware multi-turn conversations. If you see `/ai/ask` anywhere
>   in this workflow, it is wrong — change it to `/chat`.
> - `AI_SERVICE_URL` is the **raw Cloud Run HTTPS URL** (e.g.
>   `https://ai-service-abc123-uc.a.run.app`). Do **NOT** append `:8090` — that
>   port only applies to the local docker-compose dev environment where
>   ai-service listens on 8090. Cloud Run terminates HTTPS on 443 implicitly.
> - The HTTP Request node URL is exactly `={{ $env.AI_SERVICE_URL }}/chat`.

---

## Workflow Overview

The main workflow (`Email Bot — Phase 5`) has seven nodes in a polling
pipeline with two parallel reply branches. A separate `email-bot-error-handler`
workflow catches unhandled execution errors and notifies the operator.

```
Gmail Trigger (5 min poll)
      |
Filter: Skip Auto-Replies and Junk
      |
Build Chat Messages (Code)
      |
HTTP Request: ai-service /chat
      |\
      | \___(on error)___> Gmail Send: Fallback Reply ___
      |                                                  \
      `___(on success)___> Gmail Send: AI Reply __________>  Label: Mark as Replied
```

---

## Node-by-Node Walkthrough

### 1. Gmail Trigger
- **Type:** `n8n-nodes-base.gmailTrigger` (v1.2)
- **Poll interval:** Every 5 minutes (`mode: everyX`, `value: 5`, `unit: minutes`)
- **Filters:** `INBOX`, `UNREAD`, Gmail search query `-label:bot-replied -label:auto-replied`
- **Credential:** `Gmail Bot Account` (Gmail OAuth2, re-linked per import runbook)
- **Why 5 min (D-03):** see "Why the 5-minute poll interval" below.

### 2. Filter: Skip Auto-Replies and Junk
- **Type:** `n8n-nodes-base.if` (v2.2)
- **Conditions (ALL must be true to continue; any false stops the item):**
  - `from` does not contain `BOT_GMAIL_ADDRESS` (Pitfall #6 — self-loop guard)
  - `headers['x-auto-reply-type']` is empty (vacation / OOO autoresponders)
  - `headers['auto-submitted']` equals `no` (RFC 3834 auto-reply marker)
  - `text` is not empty (D-13 — skip empty-body emails)
  - `labelIds` does not contain `CATEGORY_PROMOTIONS` (D-13 — skip newsletters)
  - `labelIds` does not contain `CATEGORY_UPDATES` (D-13)
- **Why:** Prevents infinite reply loops, skips junk, implements D-13.

### 3. Build Chat Messages
- **Type:** `n8n-nodes-base.code` (v2, JavaScript)
- **Job:** Construct the `messages` array required by ai-service `ChatRequest`.
- **Key logic:**
  - Truncates `Subject: ... \n\n body` to 500 chars (ai-service SEC-03 limit).
  - Emits exactly one `{ role: 'user', content: ... }` message (MVP single-turn).
  - Passes through `threadId`, `originalFrom`, `subject`, `messageId`,
    `originalText` for downstream reply nodes.
- **Future (Phase 5.5+):** Fetch prior thread messages via Gmail Thread > Get
  and prepend them (still capped at 10 total, last role must be `user`).

### 4. HTTP Request: ai-service /chat
- **Type:** `n8n-nodes-base.httpRequest` (v4.2)
- **Method:** POST
- **URL:** `={{ $env.AI_SERVICE_URL }}/chat`
  - Endpoint is `/chat` per **D-14** (NOT `/ai/ask`).
  - No `:8090` port suffix — Cloud Run 443 implicit.
- **Body (JSON):** `{{ JSON.stringify({ messages: $json.messages }) }}`
- **Retry:** `maxTries: 3`, `waitBetweenTries: 2000` ms (D-12)
- **On Error:** `continueErrorOutput` — creates a second output pin that
  feeds the Fallback Reply branch when all retries fail.

### 5. Gmail Send: AI Reply
- **Type:** `n8n-nodes-base.gmail` (v2.1)
- **Operation:** `reply` (uses `messageId` to reply in-thread — D-14 threading)
- **Message body format (D-05 plain text, D-06 signature, D-07 quote):**
  1. AI answer from the HTTP Request response
  2. Horizontal rule
  3. Quoted original email (`> On DATE, FROM wrote:` + quoted body)
  4. Signature block with `CANDIDATE_NAME`, GitHub URL, portfolio URL
  5. AI disclaimer line
- **Credential:** `Gmail Bot Account`

### 6. Gmail Send: Fallback Reply
- **Type:** `n8n-nodes-base.gmail` (v2.1)
- **Operation:** `reply` to the same `messageId`
- **Trigger:** Only runs when HTTP Request error pin fires after 3 retries
- **Body:** Polite apology + direct `CANDIDATE_CONTACT_EMAIL` + signature
- **Why:** Implements D-12 / EMAIL-04 — the recruiter always gets a reply even
  if ai-service is down.

### 7. Label: Mark as Replied
- **Type:** `n8n-nodes-base.gmail` (v2.1)
- **Operation:** `addLabels` with `["bot-replied"]`
- **Purpose:** De-duplication — the Gmail Trigger query excludes
  `label:bot-replied`, so marking replied emails prevents double-replies on the
  next poll cycle.
- **Precondition:** The `bot-replied` label must exist in the bot Gmail account
  (operator creates it manually in the Gmail web UI — see import runbook).

---

## Why the 5-minute poll interval

**Decision:** D-03 — "Poll interval set to every 5 minutes (not 60 seconds).
User accepts longer reply time (~5 min + processing)."

Reasoning:
- Lower Gmail API quota consumption — the bot runs on a free-tier e2-micro
  and the portfolio budget is $0/month.
- Simpler execution scheduling — avoids overlapping poll cycles.
- Acceptable UX for a portfolio project where recruiters do not expect
  instant replies. Faster polling is a future enhancement if ever needed.

---

## Why quote the original question

**Decision:** D-07 — "Quote the original question in the reply (standard email
threading)."

This matches standard email etiquette and gives the recipient context in the
reply body itself (not just the threaded view). The Gmail Send: AI Reply node
builds the quoted block from `$('Build Chat Messages').item.json.originalText`
with `\n` replaced by `\n> ` to produce proper quote formatting.

---

## Why the fallback reply exists

**Decisions:** D-12 and requirement EMAIL-04.

If ai-service is unreachable (container crashed, Cloud Run cold start timeout,
network partition), the HTTP Request node exhausts 3 retries (2s apart) then
emits on its error output pin. The Fallback Reply node sends a polite
acknowledgment with the candidate's direct contact email so the recruiter is
never left without a response.

This branch is wired via `onError: continueErrorOutput` on the HTTP Request
node — n8n creates a second output pin that only fires on unrecoverable error.

---

## Error Handler Workflow

**Decision:** D-16 — "n8n error workflow: sends notification when a reply
fails (built-in n8n error handling pattern)."

The main workflow's `settings.errorWorkflow` is set to `email-bot-error-handler`
in the JSON, but n8n regenerates internal workflow IDs on import so this link
must be re-established manually after first import. See
`workflow-import-runbook.md` step 10.

The `email-bot-error-handler` workflow has two nodes:

1. **Error Trigger** — catches all unhandled execution failures from the main
   workflow.
2. **Gmail Send: Error Notification** — emails `CANDIDATE_CONTACT_EMAIL` with
   the workflow name, execution ID, execution URL, and error message.

To register it after import:
1. Open the main workflow (`Email Bot — Phase 5`).
2. Click **Settings** (top-right gear icon).
3. Under **Error Workflow**, select `email-bot-error-handler`.
4. Save.

---

## Environment Variables Referenced

The workflow reads the following env vars at execution time (populated from
`/opt/n8n/.env` on the VM — see `n8n/.env.example`):

| Variable | Used By | Purpose |
|----------|---------|---------|
| `AI_SERVICE_URL` | HTTP Request node | Cloud Run URL of ai-service (no port) |
| `BOT_GMAIL_ADDRESS` | Filter node | Self-loop guard (Pitfall #6) |
| `CANDIDATE_NAME` | Reply + Fallback nodes | D-06 signature block |
| `CANDIDATE_GITHUB` | Reply + Fallback nodes | D-06 signature block |
| `CANDIDATE_PORTFOLIO` | Reply + Fallback nodes | D-06 signature block |
| `CANDIDATE_CONTACT_EMAIL` | Fallback + Error Handler | D-12 direct contact |

---

## Related Files

- `n8n/workflows/email-bot.json` — the authoritative workflow definition
- `n8n/workflows/error-handler.json` — the error notification workflow
- `n8n/docs/workflow-import-runbook.md` — post-import operator steps
- `n8n/.env.example` — env var template for `/opt/n8n/.env`
- `ai-service/main.py` — `/chat` endpoint contract (ChatRequest/ChatResponse)
