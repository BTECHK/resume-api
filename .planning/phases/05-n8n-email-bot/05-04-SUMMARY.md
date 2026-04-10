---
phase: 05-n8n-email-bot
plan: 04
subsystem: n8n-monitoring-and-validation
tags: [gcp, monitoring, uptime-check, smoke-test, phase-gate, scaffold-first]
dependency-graph:
  requires:
    - "05-01 (n8n VM Terraform module)"
    - "05-02 (Gmail OAuth runbook)"
    - "05-03 (n8n workflow JSON, committed in 1ba4ea4)"
    - "ai-service/gcp-setup.sh (Phase 4 idempotent-script pattern)"
  provides:
    - "gcp/monitoring/n8n-uptime-check.sh (D-15 uptime check provisioning)"
    - "gcp/monitoring/README.md (usage + limitations)"
    - "n8n/docs/end-to-end-smoke-test.md (EMAIL-01..EMAIL-07 validation runbook)"
    - ".planning/phases/05-n8n-email-bot/05-PHASE-SUMMARY.md (pre-checkpoint skeleton)"
  affects:
    - "Phase 5 exit criteria (EMAIL-05 satisfied; EMAIL-01..EMAIL-04, EMAIL-06, EMAIL-07 pending live smoke test)"
    - "Phase 8 INT-01 end-to-end smoke tests will reuse this runbook as the manual baseline"
tech-stack:
  added:
    - "GCP Cloud Monitoring uptime check (free tier, TCP-22 liveness probe)"
    - "gcloud alpha monitoring channels (email notification channel)"
  patterns:
    - "Idempotent bash script: check-before-create for notification channel and uptime check (ai-service/gcp-setup.sh style)"
    - "Pre-checkpoint summary skeleton: write summary BEFORE the human checkpoint so durable artifact survives interruption; post-checkpoint task (3b) fills results table"
key-files:
  created:
    - "gcp/monitoring/n8n-uptime-check.sh"
    - "gcp/monitoring/README.md"
    - "n8n/docs/end-to-end-smoke-test.md"
    - ".planning/phases/05-n8n-email-bot/05-PHASE-SUMMARY.md"
    - ".planning/phases/05-n8n-email-bot/05-04-SUMMARY.md (this file)"
  modified:
    - "DEFERRED-WORK.md (appended Plan 05-04 Task 3 entry)"
decisions:
  - "TCP-22 uptime check chosen over HTTP /healthz because n8n port 5678 is not publicly reachable (D-09); HTTP probe would require an nginx reverse-proxy sidecar, out of Phase 5 scope"
  - "EMAIL-05 satisfied without the human checkpoint: commit 1ba4ea4 from Plan 05-03 already landed both email-bot.json and error-handler.json — the plan's Part C is a no-op as long as 1ba4ea4 is in git log"
  - "Phase summary skeleton pre-checked EMAIL-05 only; all other boxes stay [ ] until live smoke test results land (via Task 3b or manual edit when DEFERRED-WORK.md entry resolves)"
  - "Task 3b skipped (not deferred) — its sole purpose is to copy filled smoke-test results into the summary skeleton, which cannot happen without Task 3 having run first. When the operator eventually executes DEFERRED-WORK.md Plan 05-04 Task 3, Part E of that entry instructs them to perform the Task 3b edits manually"
metrics:
  duration: "~12 min"
  completed: "2026-04-10"
  tasks-completed: 2
  tasks-deferred: 1
  tasks-skipped: 1
requirements:
  - EMAIL-05 (verified — commit 1ba4ea4 proof)
---

# Phase 5 Plan 04: Smoke Test Runbook + Phase Summary Scaffold

**One-liner:** Authored the GCP Cloud Monitoring uptime check script (D-15), the end-to-end smoke test runbook covering EMAIL-01..EMAIL-07, and the pre-checkpoint Phase 5 summary skeleton — closing Phase 5's code/doc deliverables while deferring the live smoke test to `DEFERRED-WORK.md`.

## Status Overview

| Task   | Type                      | Status                                         |
| ------ | ------------------------- | ---------------------------------------------- |
| 1      | auto                      | COMPLETE — commit `c7957c0`                    |
| 2      | auto                      | COMPLETE — commit `2347168`                    |
| 3      | checkpoint:human-verify   | DEFERRED to `DEFERRED-WORK.md` — commit `6949b46` |
| 3b     | auto (post-checkpoint)    | SKIPPED (pending — cannot run without Task 3 data) |

## Tasks Completed

### Task 1 — Uptime check script + smoke test runbook (COMPLETE)

Created three files:

1. **`gcp/monitoring/n8n-uptime-check.sh`** (122 lines, `bash -n` clean) — Idempotent gcloud script that:
   - Validates `PROJECT_ID` and `ALERT_EMAIL` env vars
   - Enables `monitoring.googleapis.com`
   - Resolves the VM's external IP via `gcloud compute instances describe`
   - Creates (or reuses) an email notification channel via `gcloud alpha monitoring channels`
   - Creates (or reuses) a TCP-22 uptime check named `n8n-vm-uptime` with 5-minute period and 10-second timeout
   - Prints a final banner with VM, check, and channel details

   The script uses **TCP-22 liveness** (not HTTP `/healthz`) because n8n port 5678 is not publicly reachable per D-09. The script docstring explains both options (nginx sidecar for HTTP probe OR Ops Agent for process health) and calls out TCP-22 as the zero-extra-exposure fallback.

2. **`gcp/monitoring/README.md`** — Usage instructions covering the env var invocation, limitation notes (TCP ≠ HTTP health), manual Console fallback path, verification command (`gcloud monitoring uptime list-configs`), and tear-down commands.

3. **`n8n/docs/end-to-end-smoke-test.md`** (317 lines) — Operator runbook with:
   - **Prerequisites** checklist (terraform applied, OAuth published, workflow imported, ai-service live)
   - **Pre-flight checks** (VM active, swap 2G, container Up, `/healthz` 200, ai-service `/health` 200, `:8090` leak guard)
   - **Test 1 — Happy Path** (EMAIL-02, EMAIL-03): real email → 6-minute wait → AI reply with quote + signature + bot-replied label
   - **Test 2 — Filter Rejection** (D-13, Pitfall #6): self-loop OR empty-body rejection verified via n8n execution log
   - **Test 3 — Fallback Path** (EMAIL-04): AI_SERVICE_URL swap to unreachable host + restart + fallback template verification + restore
   - **Test 4 — VM Reboot** (EMAIL-06): `sudo reboot`, 90s wait, post-reboot email processed
   - **Test 5 — OAuth Token Persistence** (EMAIL-07): Day 0 recorded, Day +8 delayed verification
   - **Results Table** with placeholder rows
   - **Troubleshooting section** covering no-reply, fallback-on-happy-path, Pitfall #2 OOM, Pitfall #1 invalid_grant

   All runbook acceptance criteria grep checks (`swapon --show`, `systemctl is-active n8n`, `EMAIL-01`, `EMAIL-04`, `EMAIL-07`, `bot-replied`, fallback-case-insensitive) pass. File is 317 lines, well over the 100-line minimum.

**Verification:** All 18 plan acceptance grep checks + `bash -n` + file-existence checks pass. Commit: **`c7957c0`**.

### Task 2 — Phase summary skeleton (COMPLETE)

Created **`.planning/phases/05-n8n-email-bot/05-PHASE-SUMMARY.md`** (138 lines) with all fixed sections populated:

- **Header + status placeholder** ("Completed: `<date — filled in after smoke test>`") — intentionally literal placeholder for Task 3b to replace
- **Requirements Delivered table** — EMAIL-01..EMAIL-07 with status column. EMAIL-05 is pre-marked ✅ (commit `1ba4ea4` proof — see Key Insight below). All other rows are `[ ]` pending smoke test
- **Artifacts Produced** — full list across IaC, runtime config, workflows, runbooks, monitoring
- **Key Decisions Locked** — D-01 through D-16 with one-line outcome each
- **Pitfalls Avoided** — Pitfall #1..#7 each with mitigation summary
- **What's Still Manual (by design)** — enumerates the `DEFERRED-WORK.md` entries
- **Phase Exit Criteria** — EMAIL-01..EMAIL-07 checklist with EMAIL-05 pre-checked (`[x]`)
- **Smoke Test Results** — empty table except for EMAIL-05 row (pre-filled with date and commit hash)
- **Downstream Dependencies** — Phase 8 INT-01, Phase 8 SEC-04, Phase 5.5+ enhancement, Phase 6 independence

**Verification:** All 5 plan-level grep checks pass. File is 138 lines (≥50 minimum). Commit: **`2347168`** (required `git add -f` since `.planning/` is gitignored but previously-committed files in the tree are still tracked).

### Task 3 — DEFERRED to `DEFERRED-WORK.md`

The plan's Task 3 is `checkpoint:human-verify, blocking`. Under scaffold-first mode, instead of halting, a full entry was appended to `DEFERRED-WORK.md` directly after the existing Plan 05-03 Task 2 entry. The new entry contains:

- **Why deferred:** Phase 5 final gate requires (a) running VM, (b) Gmail OAuth Published, (c) ai-service live on Cloud Run, (d) real email round-trip, (e) live `sudo reboot`
- **Prerequisites** (6-item dependency chain across Phase 4, 5-01, 5-02, 5-03)
- **Part A — Execute smoke test runbook** (pre-flight + Tests 1-5 checklist)
- **Part B — Provision GCP uptime check** (script invocation + verification command)
- **Part C — EMAIL-05 status:** Explicitly noted as "already satisfied in commit `1ba4ea4`. No action needed." (see Key Insight below)
- **Part D — Fill Results Table** in `end-to-end-smoke-test.md` and commit
- **Part E — Update phase summary** (explicit instructions to replace the date placeholder, flip checkboxes, copy filled results into skeleton — effectively the manual version of the skipped Task 3b)
- Unchecked `[ ] Completed on: ____` tracking line

Commit: **`6949b46`**. The prior `Plan 05-02 Task 2` and `Plan 05-03 Task 2` entries in `DEFERRED-WORK.md` were preserved verbatim.

### Task 3b — SKIPPED (not deferred)

Task 3b's sole purpose is to copy filled-in smoke test results from `n8n/docs/end-to-end-smoke-test.md` into the phase summary skeleton's Smoke Test Results section and flip Exit Criteria boxes from `[ ]` to `[x]` for passed tests. This requires Task 3 to have already produced real data — which is impossible without executing the live smoke test.

Rather than create an empty "auto task ran but produced no changes" entry, Task 3b is **skipped entirely**. When the operator resolves the `DEFERRED-WORK.md` Plan 05-04 Task 3 entry, **Part E** of that entry contains the explicit edit instructions (replace date placeholder, flip boxes, copy results table) — this is effectively Task 3b re-parented to the deferred-work bundle. The phase summary skeleton will remain in its pre-checkpoint state until then.

## Key Insight: EMAIL-05 Satisfied Without the Checkpoint

The Plan 05-04 checkpoint's Part C instructed the operator to commit the workflow JSON files for EMAIL-05:

```bash
git add n8n/workflows/email-bot.json n8n/workflows/error-handler.json
git commit -m "feat(05): ..."
```

But those files are **already committed** in Plan 05-03's commit **`1ba4ea4`** (verified via `git show --stat 1ba4ea4`). The EMAIL-05 requirement is therefore satisfied right now, in the current `main` branch, without needing the live checkpoint.

This is reflected in:

- `05-PHASE-SUMMARY.md` Requirements Delivered table: EMAIL-05 = ✅ (with inline note citing `1ba4ea4`)
- `05-PHASE-SUMMARY.md` Phase Exit Criteria: EMAIL-05 = `[x]`
- `05-PHASE-SUMMARY.md` Smoke Test Results table: EMAIL-05 row pre-filled with date `2026-04-10` and commit hash
- `DEFERRED-WORK.md` Plan 05-04 Task 3 entry: Part C explicitly notes "Already satisfied in commit `1ba4ea4`. No action needed."

When verify-work eventually runs for Phase 5, it will find EMAIL-05 already green. The only boxes waiting on live validation are EMAIL-01..EMAIL-04, EMAIL-06, and EMAIL-07 — all of which require the deferred live stack.

## Decisions Made

1. **TCP-22 uptime check over HTTP `/healthz`** — n8n UI port 5678 is not publicly reachable (D-09). HTTP probing would require either an nginx reverse-proxy sidecar (firewall-limited to GCP uptime IPs) or the Google Ops Agent with process-health metrics. Both are explicitly out of Phase 5 scope per 05-CONTEXT.md deferred ideas. TCP-22 proves the VM is reachable at OS level, which combined with the existing systemd unit (`Restart=on-failure` + `After=docker.service`) gives a reasonable proxy for n8n liveness.

2. **Pre-checkpoint summary skeleton pattern** — The plan deliberately writes the phase summary skeleton in Task 2 (BEFORE the checkpoint) so there's a durable artifact even if the checkpoint is never resumed. Task 3b is the "finalize skeleton" companion that fills in Results Table rows after smoke test data exists. Under scaffold-first mode, Task 3b becomes Part E of the deferred-work entry — the same edits, performed by the operator when they resolve the deferred checkpoint.

3. **EMAIL-05 pre-checked in the skeleton** — Since commit `1ba4ea4` already satisfies EMAIL-05, pre-checking it in the skeleton is a statement of fact, not a premature victory lap. It saves the operator from having to re-verify git log during Part E of the deferred work.

4. **`git add -f` required for `05-PHASE-SUMMARY.md`** — `.planning/` is globally gitignored (line 38 of `.gitignore`), but older planning files are tracked because they were committed before that rule was added. New files in `.planning/` need explicit `-f` to be staged. Same workaround applied previously for 05-01..05-03 summaries — confirmed by inspecting prior Plan summaries in the repo.

## Deviations from Plan

**None in the code/doc deliverables.** Tasks 1 and 2 landed exactly as specified.

**Workflow deviations** (scaffold-first mode, not plan deviations):

1. **Task 3 deferred** — The plan expects a blocking human-verify checkpoint. Under scaffold-first mode, this is redirected to `DEFERRED-WORK.md` per the session's execution instructions.
2. **Task 3b skipped** — Cannot run auto because it depends on Task 3's runtime data. Its edits are re-parented into Part E of the deferred-work entry.

Neither of these reflects a defect in the plan. The plan was written expecting a live session; under scaffold-first mode the deferred-work mechanism is the intended escape hatch.

## Auth Gates

None encountered. Task 1 and Task 2 are pure file authoring + `bash -n` + grep verification — no network calls, no tool auth required.

## Files Changed

### Created (5)
- `gcp/monitoring/n8n-uptime-check.sh` (122 lines)
- `gcp/monitoring/README.md` (55 lines)
- `n8n/docs/end-to-end-smoke-test.md` (317 lines)
- `.planning/phases/05-n8n-email-bot/05-PHASE-SUMMARY.md` (138 lines)
- `.planning/phases/05-n8n-email-bot/05-04-SUMMARY.md` (this file)

### Modified (1)
- `DEFERRED-WORK.md` — appended Plan 05-04 Task 3 entry (preserved prior Plan 05-02 and 05-03 entries verbatim)

## Known Stubs

None in code. The phase summary skeleton contains the intentional `<date — filled in after smoke test>` placeholder and empty Results Table rows (except EMAIL-05). Both are part of the documented pre-checkpoint skeleton pattern and will be filled in via Part E of the deferred-work entry when the operator resolves the checkpoint. This is NOT a stub in the "broken rendering" sense — the file is complete as a skeleton.

## Commits

- `c7957c0` — `feat(05-04): add uptime check script and end-to-end smoke test runbook` (Task 1, 3 files)
- `2347168` — `docs(05-04): add Phase 5 summary skeleton` (Task 2, 1 file)
- `6949b46` — `docs(05-04): defer end-to-end smoke test checkpoint` (DEFERRED-WORK.md append)

All commits used `--no-verify` per scaffold-first session instructions.

## Next Steps

- **Phase 5 is complete in scaffold-first form.** All code, IaC, workflows, runbooks, and monitoring scripts are committed.
- Run `/gsd:verify-work 05` when ready — EMAIL-05 will verify green; EMAIL-01..EMAIL-04, EMAIL-06, EMAIL-07 will show as pending-live-validation, which verify-work should treat as acceptable for a scaffold-first phase.
- When the deferred live stack is in place (Phase 4 Cloud Run deploy, terraform apply, OAuth publish, workflow import), resolve the four `DEFERRED-WORK.md` Phase 5 entries in order:
  1. Plan 05-02 Task 2 (Gmail OAuth Publish)
  2. Plan 05-01 `terraform apply` (implicit in Plan 05-02/5-03 prerequisites)
  3. Plan 05-03 Task 2 (workflow import + dry-run)
  4. Plan 05-04 Task 3 (end-to-end smoke test + Part E summary update)
- **Phase 6 (React Chatbot Frontend)** is independent of Phase 5 and can proceed in parallel — both extend Phase 4.

## Self-Check: PASSED

**Files verified on disk:**
- FOUND: `gcp/monitoring/n8n-uptime-check.sh`
- FOUND: `gcp/monitoring/README.md`
- FOUND: `n8n/docs/end-to-end-smoke-test.md`
- FOUND: `.planning/phases/05-n8n-email-bot/05-PHASE-SUMMARY.md`
- FOUND: `DEFERRED-WORK.md` (with Plan 05-04 Task 3 entry appended, prior entries preserved)

**Commits verified in git log:**
- FOUND: `c7957c0` — `feat(05-04): add uptime check script and end-to-end smoke test runbook`
- FOUND: `2347168` — `docs(05-04): add Phase 5 summary skeleton`
- FOUND: `6949b46` — `docs(05-04): defer end-to-end smoke test checkpoint`

**Plan verification:** All Task 1 acceptance criteria (bash -n, grep patterns, file existence, wc -l ≥ 100) and all Task 2 acceptance criteria (file exists, grep EMAIL-01..EMAIL-07, grep Pitfall, grep Smoke Test Results, wc -l ≥ 50) pass.

**EMAIL-05 proof:** `git show --stat 1ba4ea4` confirms both `n8n/workflows/email-bot.json` and `n8n/workflows/error-handler.json` were created in that commit.
