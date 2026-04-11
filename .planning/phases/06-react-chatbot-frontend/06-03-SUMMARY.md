---
phase: 06
plan: 06-03
plan_name: api-client-and-integration
subsystem: frontend
tags: [frontend, react, fetch, api-client, abort-controller, typescript]
requires:
  - 06-01 (scaffold + VITE_AI_SERVICE_URL env typing)
  - 06-02 (Chat.tsx shell + UIMessage shape + nearBottom scroll effect)
provides:
  - frontend/src/lib/types.ts (ChatRole, ChatMessage, ChatRequest, ChatSource, ChatResponse)
  - frontend/src/lib/api.ts (sendChat function + ChatApiError class)
  - Real /chat integration replacing Plan 06-02 stub
  - AbortController lifecycle (unmount + rapid-resend cancellation)
  - Client-side validation mirror of ai-service security.py (trim, 1–500 chars, 1–10 messages, last=user)
  - D-10 conversation history cap (slice(-10)) enforced client-side
  - CHAT-02 (functional typing indicator on real latency)
  - CHAT-05 (auto-greeting wired to real state)
affects:
  - frontend/src/pages/Chat.tsx (rewritten — stub handleSend replaced)
tech-stack:
  added: []
  patterns:
    - Native fetch + AbortController (no axios per D-05)
    - Custom typed error class (ChatApiError extends Error with optional status)
    - Type-only imports for verbatimModuleSyntax (Pitfall #11)
    - Client-side Pydantic validator mirror for friendlier UX vs server 422
    - useRef<AbortController | null> for in-flight request lifecycle
    - Byte-frozen type-to-Pydantic contract (lib/types.ts vs ai-service/main.py)
key-files:
  created:
    - frontend/src/lib/types.ts (26 lines)
    - frontend/src/lib/api.ts (85 lines)
  modified:
    - frontend/src/pages/Chat.tsx (106 lines, rewritten)
decisions:
  - D-03 Direct CORS — frontend reads VITE_AI_SERVICE_URL at build time, no proxy
  - D-05 Native fetch only, no axios
  - D-10 In-memory state, slice(-10) enforced before every send
  - Specific spec — tiny AbortController wrapper via useRef + unmount cleanup
metrics:
  tasks_completed: 2
  files_created: 2
  files_modified: 1
  total_new_lines: 217
  commits: 1
  build_status: green
  bundle_delta_js: +0.79kB_raw_+0.31kB_gzip
  duration_minutes: 6
---

# Phase 6 Plan 3: API Client and /chat Integration Summary

## One-liner

Replaced Plan 06-02's `setTimeout` stub with a real `sendChat()` fetch client backed by a byte-frozen `lib/types.ts` that mirrors `ai-service/main.py` Pydantic models, plus an `AbortController` lifecycle that cancels in-flight requests on unmount and on rapid re-send — conversation history is in-memory and sliced to the last 10 per D-10.

## File tree changes

```
frontend/src/
├── lib/                           (NEW directory)
│   ├── types.ts                   (26 lines) — ChatRole, ChatMessage, ChatRequest, ChatSource, ChatResponse
│   └── api.ts                     (85 lines) — sendChat() + ChatApiError class
└── pages/
    └── Chat.tsx                   (106 lines, rewritten from 92) — real sendChat flow + AbortController
```

Total: 2 new files, 1 rewrite, +111 net lines (158 insertions, 33 deletions per git stat).

## Contract verification — lib/types.ts vs ai-service/main.py

Source of truth: `ai-service/main.py` lines 159–196. The TypeScript types are byte-frozen against the Pydantic models:

| TypeScript (lib/types.ts)                                    | Python (ai-service/main.py L159–196)                                     | Match |
| ------------------------------------------------------------ | ------------------------------------------------------------------------ | ----- |
| `export type ChatRole = "user" \| "assistant"`               | `role: Literal["user", "assistant"]`                                     | YES   |
| `ChatMessage { role: ChatRole; content: string }`            | `class ChatMessage(BaseModel): role: Literal[...]; content: str`         | YES   |
| `ChatRequest { messages: ChatMessage[] }`                    | `class ChatRequest(BaseModel): messages: list[ChatMessage]`              | YES   |
| `ChatSource { chunk: string; relevance: number }`            | `sources: list[dict]` (each dict: `{chunk: str, relevance: float}`)      | YES   |
| `ChatResponse.answer: string`                                | `answer: str`                                                            | YES   |
| `ChatResponse.sources: ChatSource[]`                         | `sources: list[dict]`                                                    | YES   |
| `ChatResponse.model_used: string`                            | `model_used: str = "gemini-2.5-flash"`                                   | YES   |
| `ChatResponse.message_count: number`                         | `message_count: int`                                                     | YES   |

The Pydantic validators on `ChatRequest.messages` (1–10 items, last must be `role="user"`) and on `ChatMessage.content` (trim, non-empty, ≤500 chars) are replicated as early-return client-side guards in `sendChat()` so invalid requests never leave the browser. Server remains the final authority — a 422 still surfaces as a `ChatApiError(status: 422)` if the contract ever drifts.

## handleSend flow diagram (Chat.tsx)

```
text arrives from ChatInput
  │
  ├─ abortRef.current?.abort()            ← cancel any prior in-flight request
  ├─ new AbortController()                 ← create fresh controller
  ├─ nextMessages = [...messages, userMsg].slice(-10)   ← D-10 enforcement
  ├─ setMessages(nextMessages)             ← optimistic UI
  ├─ setIsLoading(true)                    ← typing indicator on
  │
  ├─ try: sendChat(nextMessages, controller.signal)
  │     └─ success: setMessages(prev => [...prev, { role: "assistant", content: response.answer }])
  │
  ├─ catch: DOMException("AbortError")    ← silent return, no UI
  │        ChatApiError                    ← console.error + ERROR_REPLY inline bubble
  │        other                           ← console.error + ERROR_REPLY inline bubble
  │
  └─ finally: setIsLoading(false)          ← typing indicator off
```

## AbortController lifecycle

Two triggers call `abortRef.current?.abort()`:

1. **Unmount cleanup** (`useEffect(() => { return () => abortRef.current?.abort(); }, [])`) — when the user clicks the back button or navigates away from `/chat`, any in-flight fetch is cancelled so React doesn't try to `setState` on an unmounted component.
2. **Rapid re-send** — if the user sends a second message while the first is still pending, the older controller is aborted before the new one replaces it. The aborted request throws `DOMException("AbortError")` in the catch block, which is silently swallowed (no inline error bubble) so rapid typing doesn't spam error messages.

Both triggers use the same `abortRef` so the "currently-pending" state is single-sourced.

## Requirement status

| Req ID  | Name                                     | Status   | Notes                                                                                                           |
| ------- | ---------------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------- |
| CHAT-02 | Polished chat design + typing indicator  | COMPLETE | Typing indicator is now driven by real network latency via `setIsLoading(true)` / `finally(false)` around fetch |
| CHAT-05 | Auto-greeting on first load              | COMPLETE | `useState([greeting])` seeds exactly one message on mount; CHAT-05 literal preserved verbatim                   |
| CHAT-04 | POST /chat endpoint w/ conversation hist | N/A      | Phase 4 deliverable — frontend is the client of it; integration contract verified via byte-frozen types        |

No other CHAT-0x requirements target Plan 06-03.

## Acceptance criteria evidence

All Task 1 and Task 2 acceptance grep commands pass. Representative evidence (run from `frontend/`):

```
grep -q 'export type ChatRole' src/lib/types.ts                                 PASS
grep -q '"user" | "assistant"' src/lib/types.ts                                 PASS
grep -q 'export interface ChatMessage' src/lib/types.ts                         PASS
grep -q 'export interface ChatRequest' src/lib/types.ts                         PASS
grep -q 'export interface ChatResponse' src/lib/types.ts                        PASS
grep -q 'model_used' src/lib/types.ts                                           PASS
grep -q 'import type' src/lib/api.ts                                            PASS
grep -q 'import.meta.env.VITE_AI_SERVICE_URL' src/lib/api.ts                    PASS
grep -q 'AbortSignal' src/lib/api.ts                                            PASS
grep -q 'export class ChatApiError' src/lib/api.ts                              PASS
grep -q 'method: "POST"' src/lib/api.ts                                         PASS
grep -q 'Content-Type' src/lib/api.ts                                           PASS
! grep -q 'credentials:' src/lib/api.ts                                         PASS
! grep -q 'axios' src/lib/api.ts                                                PASS
grep -q 'import { sendChat, ChatApiError }' src/pages/Chat.tsx                  PASS
grep -q 'import type { ChatMessage }' src/pages/Chat.tsx                        PASS
grep -q 'useRef<AbortController' src/pages/Chat.tsx                             PASS
grep -q 'abortRef.current?.abort()' src/pages/Chat.tsx                          PASS
grep -q '.slice(-10)' src/pages/Chat.tsx                                        PASS
grep -q 'controller.signal' src/pages/Chat.tsx                                  PASS
grep -q 'AbortError' src/pages/Chat.tsx                                         PASS
grep -q "Hi — I'm a bot trained on" src/pages/Chat.tsx                          PASS
! grep -q 'setTimeout' src/pages/Chat.tsx                                       PASS
! grep -q 'Stub reply' src/pages/Chat.tsx                                       PASS
! grep -q 'What languages do you know' src/pages/Chat.tsx                       PASS
! grep -R 'react-router-dom' src/                                               PASS
! grep -R 'h-screen' src/                                                       PASS
! grep -R ':8090' src/                                                          PASS
! grep -R 'import .*from .axios' src/                                           PASS
cd frontend && npm run build                                                    PASS (built in 502ms)
```

Build output after Task 2 commit:

```
dist/index.html                   0.45 kB │ gzip:  0.29 kB
dist/assets/index-BNRxXg4o.css   19.00 kB │ gzip:  4.42 kB
dist/assets/index-DSbHss2E.js   292.84 kB │ gzip: 93.04 kB
```

Delta vs Plan 06-02 build: JS grew from 292.05 kB → 292.84 kB (+0.79 kB raw / +0.31 kB gzip). Module count grew from 27 → 28 (new `lib/` barrel contributes one merged chunk through `Chat.tsx`).

## Deviations from plan

**None.** Plan 06-03 executed exactly as written. All three files (`lib/types.ts`, `lib/api.ts`, `pages/Chat.tsx`) are verbatim copies of the plan's code blocks — no Rule 1-3 auto-fixes triggered, no Rule 4 architectural questions raised. The plan-checker had already verified the snippets match `ai-service/main.py`, and copying them unchanged kept that guarantee intact.

## Pitfalls encountered

None tripped. Pre-emptively handled by the plan's code:

- **Pitfall #4 (Vite env vars are build-time):** `AI_URL` is read at module load; an explicit `if (!AI_URL)` guard throws `ChatApiError` with a friendly message if the env var was missing at build time. No runtime `process.env` access attempted.
- **Pitfall #10 (CORS credentials + wildcard):** `sendChat` does NOT pass `credentials: "include"`. `! grep -q 'credentials:' src/lib/api.ts` passes. Deployment-time CORS origin lock remains a DEFERRED-WORK item.
- **Pitfall #11 (verbatimModuleSyntax):** `api.ts` uses `import type { ChatMessage, ChatRequest, ChatResponse }` and `Chat.tsx` uses `import type { ChatMessage }` for the type-only consumption. `tsc -b` passed first try.
- **Pitfall #8 (auto-scroll):** `nearBottom` heuristic preserved verbatim from Plan 06-02 — `el.scrollHeight - el.scrollTop - el.clientHeight < 100`.
- **Pitfall #7 (100dvh):** Chat.tsx still uses `h-[100dvh]`. No `h-screen` anywhere in `src/`.

## Auth gates

None — no live network calls made during execution. The fetch target is still the placeholder Cloud Run URL from Plan 06-01's `.env.example`; real smoke testing is deferred to Plan 06-04's DEFERRED-WORK.md entry.

## Commits produced

| SHA      | Type | Message                                                      |
| -------- | ---- | ------------------------------------------------------------ |
| 42b7e83  | feat | feat(06-03): wire chat UI to ai-service /chat endpoint       |

Single atomic commit per the plan's Commit Protocol section (both Task 1 and Task 2 bundled because neither task ships usable code on its own — `api.ts` has no caller until `Chat.tsx` is rewritten, and the rewritten `Chat.tsx` wouldn't compile without `lib/api.ts`).

## Notes for Plan 06-04 executor (Docker + nginx)

Plan 06-04 packages the frontend into a multi-stage Docker image and writes `nginx.conf` + `cloudbuild.yaml` / `gcloud run deploy` scripts. Everything you need to know about the current file tree:

### What Plan 06-04's Dockerfile must COPY into the node:20-alpine build stage

```
frontend/
├── package.json                   (existing, from Plan 06-01)
├── package-lock.json              (existing, from Plan 06-01)
├── tsconfig.json                  (existing)
├── tsconfig.app.json              (existing — verbatimModuleSyntax: true)
├── tsconfig.node.json             (existing)
├── vite.config.ts                 (existing)
├── index.html                     (existing)
├── public/                        (existing Vite defaults)
└── src/
    ├── components/                (4 files from Plan 06-02 — unchanged by 06-03)
    │   ├── Header.tsx
    │   ├── MessageBubble.tsx
    │   ├── TypingIndicator.tsx
    │   └── ChatInput.tsx
    ├── lib/                       (NEW in 06-03 — must be COPYd)
    │   ├── types.ts
    │   └── api.ts
    ├── pages/
    │   ├── Landing.tsx            (unchanged since 06-02)
    │   └── Chat.tsx               (rewritten in 06-03)
    ├── index.css                  (unchanged)
    ├── main.tsx                   (unchanged)
    └── vite-env.d.ts              (unchanged — declares all 4 VITE_* env vars)
```

A `COPY frontend/ /app/` in the Dockerfile picks up the new `src/lib/` automatically — no special handling needed as long as `.dockerignore` doesn't accidentally exclude it. Double-check that `.dockerignore` only blocks `node_modules/`, `dist/`, `.env*`, and not `src/lib/` or `src/**`.

### No new dependencies added

Plan 06-03 uses only native browser APIs (`fetch`, `AbortController`, `DOMException`) and existing React types. `package.json` was NOT modified. `npm ci` in the Dockerfile stage will resolve the exact same lockfile Plan 06-01 produced.

### Build-time env var injection

`VITE_AI_SERVICE_URL` is inlined by Vite at build time (Pitfall #4). Plan 06-04's `docker build` command MUST pass it as a build-arg that gets written to `.env.local` (or exported into `ENV`) before `npm run build` runs. Suggested pattern:

```dockerfile
ARG VITE_AI_SERVICE_URL
ARG VITE_CANDIDATE_NAME
ARG VITE_CANDIDATE_TITLE
ARG VITE_CANDIDATE_EMAIL
RUN echo "VITE_AI_SERVICE_URL=$VITE_AI_SERVICE_URL" > .env.local \
 && echo "VITE_CANDIDATE_NAME=$VITE_CANDIDATE_NAME" >> .env.local \
 && echo "VITE_CANDIDATE_TITLE=$VITE_CANDIDATE_TITLE" >> .env.local \
 && echo "VITE_CANDIDATE_EMAIL=$VITE_CANDIDATE_EMAIL" >> .env.local \
 && npm run build
```

Without these build-args the bundle will contain `AI_URL = undefined` and `sendChat()` will throw `ChatApiError("VITE_AI_SERVICE_URL is not configured...")` on every send. The explicit guard in `api.ts` makes this fail loudly in the browser console instead of silently sending a request to `undefined/chat`.

### nginx.conf considerations

No server-side routing concerns from 06-03 — the SPA still has exactly two client routes (`/` and `/chat`) handled by React Router v7 client-side. `try_files $uri /index.html;` catches both. No new static assets, no new headers required. Gzip on the single ~293 kB JS bundle is still worth ~200 kB savings.

### Real smoke testing (DEFERRED-WORK)

Plan 06-04 should append to `DEFERRED-WORK.md`:

> **Phase 6 smoke test — live /chat round-trip** — After both ai-service and resume-chatbot are deployed to Cloud Run, manually: (1) open the deployed frontend, (2) send a chat message, (3) verify the response.answer renders as an assistant bubble, (4) verify rapid sends cancel prior requests (watch the network tab for `(canceled)` status), (5) verify that clicking the back button cancels an in-flight request (no stale setState warnings in the console).

This is the only way to verify the byte-frozen type contract at runtime — Plan 06-03 cannot do it because no live ai-service URL is available during scaffold-first execution.

### Negative grep acceptance tests still active in src/

Plan 06-04 will run all these again — if you add new code, don't trip them:

```
! grep -R 'react-router-dom' frontend/src/
! grep -R 'h-screen' frontend/src/
! grep -R 'react-icons|lucide-react|@heroicons' frontend/src/
! grep -R ':8090' frontend/src/
! grep -R 'import .*from .axios' frontend/src/
```

## Self-Check: PASSED

- [x] `frontend/src/lib/types.ts` FOUND
- [x] `frontend/src/lib/api.ts` FOUND
- [x] `frontend/src/pages/Chat.tsx` FOUND (rewritten)
- [x] Commit `42b7e83` FOUND in git log (`git log --oneline | grep 42b7e83` → `42b7e83 feat(06-03): wire chat UI to ai-service /chat endpoint`)
- [x] `cd frontend && npm run build` exits 0
- [x] All Task 1 `<acceptance>` grep commands pass
- [x] All Task 2 `<acceptance>` grep commands pass
- [x] Cross-plan negative greps pass (react-router-dom, h-screen, :8090, axios)
- [x] Contract byte-match verified against ai-service/main.py lines 159–196
