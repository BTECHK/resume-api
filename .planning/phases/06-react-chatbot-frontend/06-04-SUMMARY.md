---
phase: 06
plan: 06-04
plan_name: dockerfile-nginx-deploy-deferred
subsystem: frontend
tags: [frontend, docker, nginx, cloud-run, deploy, scaffold-first, deferred-work]
requires:
  - 06-01 (frontend scaffold + package.json + vite.config.ts + .env.example)
  - 06-02 (UI components — Vite build produces dist/)
  - 06-03 (lib/api.ts + Chat.tsx integrated — bundle includes real fetch client)
provides:
  - frontend/Dockerfile (69 lines — multi-stage node:20-alpine -> nginx:1.27-alpine)
  - frontend/nginx.conf (91 lines — non-root, port 8080, SPA fallback, gzip, cache-control)
  - frontend/.dockerignore (21 lines — excludes node_modules/dist/.env/.git/docs)
  - frontend/deploy.sh (88 lines — gcloud run deploy resume-chatbot --source . --set-build-env-vars)
  - DEFERRED-WORK.md Phase 6 section (5 sub-entries, tasks A-E with acceptance + commands)
  - CHAT-06 partial satisfaction (artifacts authored; live deploy deferred to DEFERRED-WORK.md)
affects:
  - DEFERRED-WORK.md (appended 213 lines; Phase 5 entries UNCHANGED)
tech-stack:
  added:
    - nginx:1.27-alpine (runtime base image)
    - node:20-alpine (build stage base image)
  patterns:
    - Multi-stage Docker build (thin runtime image, Vite dist is ~313 kB uncompressed)
    - Non-root nginx hardening (Pitfall #5 — BOTH halves: Dockerfile chown + nginx.conf /tmp paths)
    - Build-time env injection via ARG + ENV + Vite inlining (Pitfall #4)
    - Location block ordering (/assets/ before / — Pitfall #6)
    - `--source .` Cloud Build deploy with `--set-build-env-vars` (Open Q5 decision)
    - Scaffold-first execution: author artifacts, defer live infra (D-04)
key-files:
  created:
    - frontend/Dockerfile (69 lines)
    - frontend/nginx.conf (91 lines)
    - frontend/.dockerignore (21 lines)
    - frontend/deploy.sh (88 lines, git mode 100755)
  modified:
    - DEFERRED-WORK.md (+213 lines; Phase 6 section appended)
decisions:
  - D-04 Scaffold-first — no docker build, no gcloud run deploy, no image push
  - D-06 Cloud Run service name resume-chatbot, region us-central1, port 8080
  - D-07 Multi-stage Dockerfile node:20-alpine -> nginx:1.27-alpine, non-root
  - D-11 No analytics / telemetry in nginx.conf
  - Open Q1 resolved — use nginx:1.27-alpine (D-07 verbatim); 1.28 bump deferred to Phase 8
  - Open Q5 resolved — --set-build-env-vars inline (not --build-env-vars-file); cleaner one-liner
metrics:
  tasks_completed: 3
  files_created: 4
  files_modified: 1
  total_new_lines: 482
  commits: 1
  build_status: green
  checkbox_count_before: 3
  checkbox_count_after: 8
  duration_minutes: 8
---

# Phase 6 Plan 4: Dockerfile + nginx + Cloud Run Deploy Script + Deferred Work Summary

## One-liner

Authored the complete container-and-deploy toolchain for `resume-chatbot` — multi-stage Dockerfile with non-root nginx hardening, SPA-aware `nginx.conf` on port 8080 with ordered `/assets/` cache + `/` fallback, a `gcloud run deploy --source .` shell script that refuses `PLACEHOLDER`, and a five-task "Phase 6 — Deferred Manual Steps" section appended to `DEFERRED-WORK.md` that guides future-self through the chicken-and-egg CORS deployment (build → push → deploy frontend → capture URL → update ai-service `ALLOWED_ORIGINS` → smoke test). Scaffold-first per D-04: zero `docker build`, zero `gcloud` calls.

## File tree changes

```
frontend/
├── Dockerfile         (NEW, 69 lines) — multi-stage node:20-alpine -> nginx:1.27-alpine, non-root hardened
├── nginx.conf         (NEW, 91 lines) — listen 8080, SPA fallback, gzip, cache-control, /healthz
├── .dockerignore      (NEW, 21 lines) — excludes node_modules/dist/.env/.git/docs
└── deploy.sh          (NEW, 88 lines, git mode 100755) — gcloud run deploy with PLACEHOLDER guard

DEFERRED-WORK.md       (+213 lines) — Phase 6 section appended after Phase 5 (unchanged)
```

Total: 4 new files, 1 modified (append-only), +482 net lines on disk.

## Task completion

| Task | What                                              | Status | Acceptance |
| ---- | ------------------------------------------------- | ------ | ---------- |
| 1    | frontend/Dockerfile + nginx.conf + .dockerignore  | DONE   | all greps pass |
| 2    | frontend/deploy.sh (authored, git +x)             | DONE   | all greps pass; `bash -n` clean; git mode 100755 |
| 3    | DEFERRED-WORK.md append Phase 6 (tasks A-E)       | DONE   | 8 checkboxes total; Phase 5 intact; Pitfall #10 surfaced |

## Pitfall verification

### Pitfall #5 (HIGH — non-root nginx) — BOTH halves verified

**Half 1 — Dockerfile runtime stage:**
```dockerfile
RUN touch /tmp/nginx.pid && \
    chown -R nginx:nginx /var/cache/nginx /var/log/nginx /tmp/nginx.pid /usr/share/nginx/html && \
    chmod -R g=u /var/cache/nginx /var/log/nginx /tmp/nginx.pid
USER nginx
```
- `touch /tmp/nginx.pid` — grep PASS
- `chown -R nginx:nginx` — grep PASS
- `USER nginx` — grep PASS (at line 62, after chown)

**Half 2 — nginx.conf:**
- Top-level `pid /tmp/nginx.pid;` — grep PASS
- `client_body_temp_path /tmp/client_temp;` — grep PASS
- `proxy_temp_path /tmp/proxy_temp;` — present
- `fastcgi_temp_path /tmp/fastcgi_temp;` — present
- `uwsgi_temp_path /tmp/uwsgi_temp;` — present
- `scgi_temp_path /tmp/scgi_temp;` — present

All five temp paths point to `/tmp/` (nginx user has write access). Without ANY of these, the container would crash on first request with `[emerg] permission denied` on the missing temp directory.

### Pitfall #6 (location ordering) — verified via line-number comparison

```
frontend/nginx.conf:65: location /assets/ {
frontend/nginx.conf:87: location / {
```
`/assets/` at line 65 precedes `/ {` at line 87 — the `65 < 87` test passes. Nginx's longest-prefix match means `/assets/index-BrdlCSo2.css` hits the assets block (more specific) instead of falling through to the SPA catch-all with `Content-Type: text/html`.

### Pitfall #4 (HIGH — Vite env vars are build-time)

Dockerfile build stage:
```dockerfile
ARG VITE_AI_SERVICE_URL
ARG VITE_CANDIDATE_NAME
ARG VITE_CANDIDATE_TITLE
ARG VITE_CANDIDATE_EMAIL
ENV VITE_AI_SERVICE_URL=${VITE_AI_SERVICE_URL}
ENV VITE_CANDIDATE_NAME=${VITE_CANDIDATE_NAME}
ENV VITE_CANDIDATE_TITLE=${VITE_CANDIDATE_TITLE}
ENV VITE_CANDIDATE_EMAIL=${VITE_CANDIDATE_EMAIL}
RUN npm run build
```

Vite reads `VITE_*` vars from the process environment at build time and inlines them into the bundle. `ENV` (not `.env.local`) is the cleanest path because it avoids writing a temp file inside the image layer. `deploy.sh` passes these values via `--set-build-env-vars` to Cloud Build, which pipes them into the Dockerfile `ARG`s. If any of the four vars is missing at build time, the bundle ships with `AI_URL = undefined` and Plan 06-03's explicit `if (!AI_URL) throw new ChatApiError(...)` guard fires loudly in the browser console on the first chat send — NOT a silent 404 to `undefined/chat`.

### Pitfall #9 (Vite base /)

`nginx.conf` has `root /usr/share/nginx/html;` and the SPA fallback is `try_files $uri $uri/ /index.html;` — both assume root-serving, which matches `vite.config.ts`'s default `base: '/'`. If a future deploy moves the app to a subpath (e.g. `/chatbot/`), BOTH files must change in lockstep. Noted in the nginx.conf header comment as a forward-compatibility reminder.

### Pitfall #10 (CORS credentials + wildcard)

Not directly addressed in Plan 06-04's frontend artifacts — this is a RUNTIME concern on the ai-service side. But the plan surfaces it in two places:
1. `DEFERRED-WORK.md` Task D explicitly references Pitfall #10 as the reason the task exists — ai-service's `CORSMiddleware(allow_credentials=True)` forbids wildcard origins, so `ALLOWED_ORIGINS=*` silently breaks preflight.
2. `DEFERRED-WORK.md` Task E includes a six-row CORS debugging runbook table keyed to the actual browser DevTools error messages (`net::ERR_FAILED`, "must not be the wildcard", etc.), with the fix for each symptom.

This is the classic chicken-and-egg: frontend needs ai-service URL (Task B) and ai-service needs frontend URL (Task D). The DEFERRED-WORK entries document the exact order: `deploy ai-service` → `capture URL` → `put in frontend/.env.local` → `deploy frontend via deploy.sh` → `capture frontend URL` → `gcloud run services update ai-service --update-env-vars ALLOWED_ORIGINS=$FRONTEND_URL` → `smoke test`.

## Chicken-and-egg CORS resolution order (for future-self)

```
1. [Phase 4 Plan 04-03/04-04 deferred] Deploy ai-service to Cloud Run
2. [DEFERRED-WORK Task B] Capture ai-service URL -> frontend/.env.local (VITE_AI_SERVICE_URL)
3. [DEFERRED-WORK Task A, optional] Local smoke build: docker build --build-arg VITE_* -t resume-chatbot:local .
4. [DEFERRED-WORK Task C] Run frontend/deploy.sh -> gcloud run deploy resume-chatbot --source . --set-build-env-vars VITE_*=...
5. [DEFERRED-WORK Task C output] Capture deployed frontend URL
6. [DEFERRED-WORK Task D] gcloud run services update ai-service --update-env-vars ALLOWED_ORIGINS=<frontend-url>
7. [DEFERRED-WORK Task E] Open frontend in browser, send test message, verify response bubble + DevTools Network tab shows Access-Control-Allow-Origin: <frontend-url> (NOT *)
```

## Requirement status

| Req ID  | Name                                                 | Status           | Notes                                                                                                       |
| ------- | ---------------------------------------------------- | ---------------- | ----------------------------------------------------------------------------------------------------------- |
| CHAT-06 | Multi-stage Dockerfile + nginx serve + Cloud Run     | PARTIAL          | All artifacts authored: Dockerfile + nginx.conf + deploy.sh committed. Live deploy tracked in DEFERRED-WORK |

CHAT-06 flips to COMPLETE once DEFERRED-WORK.md Tasks A-E are executed. Until then, it is "scaffold-complete" — the code path exists and compiles; only the runtime instantiation is missing.

## Acceptance criteria evidence

Representative excerpts from the verification run (all passed):

```
PASS: frontend/Dockerfile exists
PASS: FROM node:20-alpine / FROM nginx:1.27-alpine
PASS: AS build / AS runtime
PASS: ARG VITE_AI_SERVICE_URL
PASS: touch /tmp/nginx.pid / chown -R nginx:nginx / USER nginx
PASS: EXPOSE 8080 / STOPSIGNAL SIGQUIT

PASS: nginx.conf: pid /tmp/nginx.pid
PASS: listen 8080 default_server
PASS: try_files SPA fallback
PASS: client_body_temp_path /tmp/client_temp
PASS: gzip on / immutable cache header / /healthz endpoint
PASS: Pitfall #6 - /assets/ (line 65) ordered before / { (line 87)

PASS: .dockerignore contains node_modules / dist / .env

PASS: deploy.sh bash -n clean syntax
PASS: gcloud run deploy "$SERVICE" / --source . / --region "$REGION"
PASS: --port 8080 / --memory 256Mi / --allow-unauthenticated / --set-build-env-vars
PASS: PLACEHOLDER guard / SERVICE:=resume-chatbot / REGION:=us-central1
PASS: no --build-env-vars-file (using inline form per Open Q5)
PASS: git mode 100755

PASS: DEFERRED-WORK.md: ## Phase 6 header present
PASS: Task A / B / C / D / E all present
PASS: checkbox count 8 (3 Phase 5 + 5 Phase 6)
PASS: Phase 5 section intact (11 "Plan 05-" references preserved)
PASS: Pitfall #10 referenced

PASS: cd frontend && npm run build -> built in 511ms
dist/index.html                   0.45 kB │ gzip:  0.29 kB
dist/assets/index-BrdlCSo2.css   19.03 kB │ gzip:  4.43 kB
dist/assets/index-DYflcqSk.js   292.84 kB │ gzip: 93.04 kB

PASS: negative greps (no react-router-dom, h-screen, :8090, axios, icon libs in src/)
```

Bundle size is unchanged from Plan 06-03 (as expected — no source code was modified in Plan 06-04, only container/deploy scaffold).

## Deviations from plan

**None.** Plan 06-04 executed exactly as written. All four new files are verbatim copies of the plan's code blocks. DEFERRED-WORK.md Phase 6 section was appended verbatim from the plan's content block. No Rule 1-3 auto-fixes triggered, no Rule 4 architectural questions raised.

## Auth gates

None — scaffold-first execution mode. No `docker`, `gcloud`, or network operations attempted.

## Commits produced

| SHA     | Type | Message                                                                 |
| ------- | ---- | ----------------------------------------------------------------------- |
| e979c0c | feat | feat(06-04): dockerfile + nginx + cloud run deploy script (scaffold-first) |

Single atomic commit per the plan's Commit Protocol. 5 files changed, 482 insertions. `frontend/deploy.sh` created with mode `100755` in the git index.

## DEFERRED-WORK.md diff summary

- Before: 118 lines, 3 checkboxes (all Phase 5)
- After: 331 lines, 8 checkboxes (3 Phase 5 + 5 Phase 6)
- Net addition: +213 lines
- Phase 5 section: zero modifications (verified — `grep -c "Plan 05-" DEFERRED-WORK.md` still returns 11)

New checkboxes added (Phase 6):
1. Plan 06-04 Task A — Build/push Docker image
2. Plan 06-04 Task B — Populate frontend/.env.local with real VITE_* values
3. Plan 06-04 Task C — Deploy frontend to Cloud Run via deploy.sh
4. Plan 06-04 Task D — Update ai-service ALLOWED_ORIGINS (chicken-and-egg CORS resolution)
5. Plan 06-04 Task E — End-to-end smoke test (6-step browser runbook + CORS debugging table)

## Notes for Phase 6 verifier / future operator

### For the phase verifier

1. **Scaffold-first is INTENTIONAL, not incomplete.** CHAT-06 is correctly marked PARTIAL — do not flag it as a failure. The expected state is "artifacts authored, live deploy deferred". Verify by checking that DEFERRED-WORK.md has Task A-E, then flip CHAT-06 to COMPLETE only after an operator ticks all 5 checkboxes.

2. **Both halves of Pitfall #5 must be present or the container crashes.** If a future plan regenerates `nginx.conf` without the top-level `pid /tmp/nginx.pid;` directive OR without the five `*_temp_path /tmp/...` directives, the phase is broken. Same for Dockerfile: removing `touch /tmp/nginx.pid && chown` before `USER nginx` also breaks it.

3. **Pitfall #6 ordering is enforced by grep line-number test.** The verifier can re-run:
   ```bash
   test $(grep -n 'location /assets/' frontend/nginx.conf | head -1 | cut -d: -f1) -lt $(grep -n 'location / {' frontend/nginx.conf | head -1 | cut -d: -f1)
   ```
   If this fails, missing assets fall through to `index.html` with the wrong Content-Type.

4. **`git ls-files --stage frontend/deploy.sh` must show 100755.** Windows filesystems don't track the exec bit, so Git is the source of truth. On Linux/macOS checkouts, this mode is what actually makes `bash deploy.sh` work without an explicit interpreter.

5. **`npm run build` is the final gate for the whole plan.** If the plan ever bundles in additional files or changes the Dockerfile's `COPY . .` scope, re-run `cd frontend && npm run build` to confirm nothing breaks.

### For the future operator (running DEFERRED-WORK.md Tasks A-E)

1. **Order matters absolutely.** Task B depends on the ai-service URL (Phase 4 deferred deploy). Task C depends on B. Task D depends on C (the frontend URL doesn't exist until C runs). Task E depends on A-D. Skipping any step breaks the chain.

2. **`VITE_AI_SERVICE_URL` format is strict.** `https://ai-service-XXXX-uc.a.run.app` — NO trailing slash, NO port, NO path. The frontend (`lib/api.ts`) appends `/chat` automatically; a trailing slash would produce `.../run.app//chat` (double slash, 404).

3. **`ALLOWED_ORIGINS` MUST be the exact frontend URL — never `*`.** Pitfall #10: ai-service runs `CORSMiddleware(allow_credentials=True)`, and the CORS spec forbids wildcard origins with credentials. Setting `ALLOWED_ORIGINS=*` silently breaks preflight — the browser rejects the response and the user sees "Sorry, I couldn't reach the AI" with no clear Cloud Run logs explaining why. The Task E CORS debugging table in DEFERRED-WORK.md covers this exact symptom.

4. **Cloud Run cold-start latency may exceed Plan 06-03's 30s timeout on the first message.** The `sendChat()` fetch has no explicit timeout, but the browser may abort after ~120s. If the smoke test in Task E times out on the first message, retry — subsequent requests hit a warm instance and respond in <3s.

5. **The deploy.sh PLACEHOLDER guard is a feature, not a bug.** If Task C errors with `ERROR: VITE_AI_SERVICE_URL is still set to the PLACEHOLDER value`, re-read Task B and actually populate `.env.local` with the real ai-service URL.

### Phase 6 status after this plan

All four plans in Phase 6 are complete:
- 06-01: scaffold + env typing (COMPLETE)
- 06-02: UI components (COMPLETE)
- 06-03: API client + Chat.tsx integration (COMPLETE)
- 06-04: Dockerfile + nginx + deploy.sh + DEFERRED-WORK (COMPLETE — this plan)

Phase 6 is ready for phase-level verification. The only remaining work is runtime (live deploy) which is tracked in DEFERRED-WORK.md and bound by Phase 4's ai-service deploy also being deferred.

## Self-Check: PASSED

- [x] `frontend/Dockerfile` FOUND (69 lines)
- [x] `frontend/nginx.conf` FOUND (91 lines)
- [x] `frontend/.dockerignore` FOUND (21 lines)
- [x] `frontend/deploy.sh` FOUND (88 lines, git mode 100755)
- [x] `DEFERRED-WORK.md` modified (+213 lines, Phase 6 section present)
- [x] Commit `e979c0c` FOUND in git log (`git log --oneline | grep e979c0c`)
- [x] `cd frontend && npm run build` exits 0
- [x] All Task 1 `<acceptance>` grep commands pass
- [x] All Task 2 `<acceptance>` grep commands pass
- [x] All Task 3 `<acceptance>` grep commands pass (8 checkboxes, Phase 5 intact)
- [x] Cross-plan negative greps pass (react-router-dom, h-screen, :8090, axios, icon libs)
- [x] Both halves of Pitfall #5 verified (Dockerfile chown + nginx.conf /tmp paths)
- [x] Pitfall #6 line-number ordering verified (65 < 87)
- [x] Pitfall #4 build-time env injection verified (ARG + ENV + RUN npm run build)
