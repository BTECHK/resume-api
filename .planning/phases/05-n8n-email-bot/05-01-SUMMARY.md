---
phase: 05-n8n-email-bot
plan: 01
subsystem: n8n-vm-infrastructure
tags: [terraform, gcp, gce, systemd, docker, n8n, iac]
requirements:
  satisfied: [EMAIL-01, EMAIL-06]
dependency-graph:
  requires:
    - n8n/docker-compose.yml (existing, D-11 — not modified)
  provides:
    - terraform/n8n-vm (IaC module for n8n host)
    - n8n/systemd/n8n.service (unit file, EMAIL-06)
  affects:
    - Plan 05-03 (n8n workflow JSON lands in n8n/workflows/ which is scp'd to /opt/n8n/ on the VM)
    - Plan 05-04 (smoke test runs against the VM provisioned by this module)
tech-stack:
  added:
    - Terraform ~> 6.0 google provider (hashicorp/google v6.50.0)
    - Ubuntu 22.04 LTS boot image (ubuntu-os-cloud/ubuntu-2204-lts)
    - Docker + Compose plugin v2 (installed by startup.sh on first boot)
  patterns:
    - Terraform metadata_startup_script for boot-time provisioning (Pattern 4, Pitfall #4)
    - systemd Type=oneshot + RemainAfterExit=yes wrapping docker compose up -d (Pattern 3)
    - Idempotent bash startup script (set -euxo pipefail, guards around swap/Docker/env)
key-files:
  created:
    - terraform/n8n-vm/main.tf
    - terraform/n8n-vm/variables.tf
    - terraform/n8n-vm/outputs.tf
    - terraform/n8n-vm/startup.sh
    - terraform/n8n-vm/.gitignore
    - terraform/n8n-vm/README.md
    - n8n/systemd/n8n.service
  modified: []
decisions:
  - "Ephemeral external IP + SSH-only firewall (not IAP tunnel) — simpler for portfolio scope"
  - "cloud-platform SA scope on VM enables future Secret Manager access without reprovisioning"
  - "startup.sh enables but does NOT start n8n.service — operator must scp docker-compose.yml first"
  - "Inline heredoc in startup.sh is byte-identical to n8n/systemd/n8n.service (single source of truth)"
  - "Restart=on-failure (NOT always) to avoid conflict with compose restart:unless-stopped (Pitfall #3)"
metrics:
  duration: ~15 minutes
  tasks-completed: 2
  files-created: 7
  commits: 2
  completed: "2026-04-10"
---

# Phase 5 Plan 01: n8n VM Infrastructure Summary

**One-liner:** Terraform module provisioning a GCE e2-micro VM with 2GB swap, Docker, and a systemd unit that boots n8n from the existing `n8n/docker-compose.yml`, with SSH-only firewall (no public n8n UI) — satisfies EMAIL-01 and EMAIL-06.

## What Was Built

### Terraform module (`terraform/n8n-vm/`)

| File            | Purpose                                                                                                |
| --------------- | ------------------------------------------------------------------------------------------------------ |
| `main.tf`       | `google_compute_instance.n8n_vm` (e2-micro, Ubuntu 22.04, 30GB pd-standard) + `google_compute_firewall.allow_ssh` (port 22 only). `metadata_startup_script = file("${path.module}/startup.sh")`. cloud-platform SA scope for future Secret Manager access. |
| `variables.tf`  | `project_id`, `region` (default us-central1), `zone` (default us-central1-a), `ssh_pub_key_path`, `ssh_user` (default ubuntu), `instance_name` (default resume-bot-n8n), `machine_type` (default e2-micro), `disk_size_gb` (default 30). |
| `outputs.tf`    | `instance_ip`, `instance_name`, `ssh_command` (ready-to-run).                                          |
| `startup.sh`    | Boot-time script: creates 2GB swap (D-10), installs Docker + Compose plugin v2, prepares `/opt/n8n/` and placeholder `.env`, installs systemd unit inline, enables (not starts) the unit. |
| `.gitignore`    | Excludes `.terraform/`, lock file, tfstate, tfvars — keeps `example.tfvars` allowed.                   |
| `README.md`     | Usage + post-apply manual steps (scp compose file, edit .env, start unit).                             |

### systemd unit (`n8n/systemd/n8n.service`)

- `Type=oneshot` + `RemainAfterExit=yes` — canonical pattern for wrapping `docker compose up -d`
- `After=docker.service network-online.target`, `Requires=docker.service`
- `WorkingDirectory=/opt/n8n`, `EnvironmentFile=/opt/n8n/.env`
- `ExecStart=/usr/bin/docker compose up -d --remove-orphans`
- `Restart=on-failure` (NOT `always`) to avoid Pitfall #3 conflict with compose `restart: unless-stopped`
- `TimeoutStartSec=300` — first pull of `n8nio/n8n:1.123.29` on e2-micro can take 2–3 minutes

The inline heredoc that `startup.sh` writes to `/etc/systemd/system/n8n.service` on the VM is **byte-for-byte identical** to the standalone `n8n/systemd/n8n.service` (verified via `diff`, 21 lines each). Single source of truth — if the file changes, both must change together.

## Post-Apply User Workflow

This plan produces IaC only. `terraform apply` is a user setup step. Once the user decides to provision:

```bash
# 1. One-time local auth (from repo root)
gcloud auth application-default login

# 2. Provision the VM
cd terraform/n8n-vm
terraform init
terraform apply \
  -var="project_id=YOUR_PROJECT_ID" \
  -var="ssh_pub_key_path=$HOME/.ssh/id_ed25519.pub"

# 3. Capture VM IP
IP=$(terraform output -raw instance_ip)
cd ../..

# 4. Copy compose file + workflows
scp n8n/docker-compose.yml ubuntu@$IP:/opt/n8n/
scp -r n8n/workflows ubuntu@$IP:/opt/n8n/

# 5. Edit placeholder .env on the VM
ssh ubuntu@$IP
sudo nano /opt/n8n/.env
# Set real N8N_PASSWORD and AI_SERVICE_URL (Cloud Run HTTPS URL from Phase 4)

# 6. Launch the unit
sudo systemctl start n8n
sudo systemctl status n8n
```

For UI access (admin only, D-09), SSH port-forward:

```bash
ssh -L 5678:localhost:5678 ubuntu@$IP
# Then open http://localhost:5678 in your local browser
```

## Critical Design Choices

1. **`Type=oneshot` + `RemainAfterExit=yes`** — The canonical systemd pattern for `docker compose up -d`. Without `RemainAfterExit`, systemd would mark the service inactive the moment compose returns (detached containers running). Combined with `After=docker.service` + `Requires=docker.service`, this guarantees n8n starts on reboot.

2. **No port 5678 firewall rule (D-09)** — The n8n web UI is intentionally unreachable from the public internet. The only opened port is 22 (SSH). UI access is via SSH port-forward, documented in both `README.md` and `systemd unit's` comment trail. `grep "5678" main.tf` returns zero matches — this is enforced.

3. **2GB swap (D-10, Pitfall #2)** — `fallocate -l 2G /swapfile` + `vm.swappiness=10` tuning in `/etc/sysctl.d/99-swappiness.conf`. Prevents OOM on the 1GB e2-micro under n8n + Docker + OS load. Swap creation is idempotent (`if ! swapon --show | grep -q /swapfile`) so re-running the startup script is safe.

4. **`Restart=on-failure` (NOT `always`)** — Compose already has `restart: unless-stopped` which handles crash recovery; systemd handles boot recovery. Using `Restart=always` in systemd would fight compose's policy on manual `systemctl stop`, causing double-start races (Pitfall #3).

5. **startup.sh enables but does NOT start the unit** — The unit has `EnvironmentFile=/opt/n8n/.env` and `WorkingDirectory=/opt/n8n`, but neither the compose file nor a real `.env` exist on the VM at first boot. Launching the unit there would fail-start and leave it in a failed state. The operator runs `systemctl start` manually after copying the compose file and editing `.env`.

6. **cloud-platform SA scope** — Foresight for Plan 05-03/04 where the n8n workflow may need to pull Gmail OAuth secrets from Secret Manager. Adding the scope now avoids re-provisioning the VM later.

## Verification

All six plan-level verification commands pass:

```bash
terraform -chdir=terraform/n8n-vm fmt -check       # OK
terraform -chdir=terraform/n8n-vm init -backend=false   # OK (google v6.50.0 installed)
terraform -chdir=terraform/n8n-vm validate         # "Success! The configuration is valid."
bash -n terraform/n8n-vm/startup.sh                # OK (valid bash syntax, 95 lines)
! grep -q "Restart=always" n8n/systemd/n8n.service # OK (no match)
! grep -q "5678" terraform/n8n-vm/main.tf          # OK (no match)
grep -q "Documentation=" n8n/systemd/n8n.service   # OK
grep -q "Documentation=" terraform/n8n-vm/startup.sh  # OK
```

And a direct diff of the heredoc vs the standalone unit file:

```
diff <(awk '/<<.UNIT./{flag=1; next} /^UNIT$/{flag=0} flag' terraform/n8n-vm/startup.sh) n8n/systemd/n8n.service
# → no output (byte-identical, 21 lines each)
```

Note: `terraform apply` was NOT executed — scaffold-first mode. The `terraform init` pulled `hashicorp/google v6.50.0` locally but `.terraform/` and `.terraform.lock.hcl` are gitignored.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed "5678" mentions from main.tf comments**
- **Found during:** Task 1 verification
- **Issue:** Initial draft of `main.tf` had two comment lines referencing "port 5678" for documentation clarity. The plan's acceptance criterion explicitly requires `grep "5678" terraform/n8n-vm/main.tf returns NO matches` (strict grep, not "no allow rule").
- **Fix:** Reworded both comments to reference "the n8n UI" and "the n8n UI port" instead of the literal number.
- **Files modified:** `terraform/n8n-vm/main.tf`
- **Commit:** `b8637af` (Task 1 commit; fix was made before commit)

**2. [Rule 1 - Bug] Removed "systemctl start n8n" phrase from startup.sh comment**
- **Found during:** Task 2 verification
- **Issue:** A documentation comment in `startup.sh` suggested the operator run `sudo systemctl start n8n` after scp'ing the compose file. The plan's acceptance criterion requires `grep "systemctl start n8n" terraform/n8n-vm/startup.sh returns NO match` to guarantee startup.sh never launches the unit itself (even by accident).
- **Fix:** Reworded the comment to point operators to `README.md` for the exact post-apply commands instead of inlining the systemctl command in the script.
- **Files modified:** `terraform/n8n-vm/startup.sh`
- **Commit:** Captured in `2e90f8d` (see parallel-execution note below)

### Parallel Execution Note

This plan was executed in parallel with Plan 05-02 under a single branch, using `--no-verify` on each commit. A race condition occurred during the Task 2 commit: the parallel `05-02` executor's final `git add`/`commit` picked up my staged `startup.sh` + `n8n/systemd/n8n.service` before my own Task 2 commit executed. As a result:

- **Task 1** (`terraform/n8n-vm/main.tf`, `variables.tf`, `outputs.tf`, `.gitignore`, `README.md`, stub `startup.sh`) landed in its dedicated commit: **`b8637af`** — correctly attributed to Plan 05-01.
- **Task 2** (`terraform/n8n-vm/startup.sh` full content + `n8n/systemd/n8n.service`) landed in commit **`2e90f8d`** — attributed in the commit message to `docs(05-02)` but the file diffs are the Plan 05-01 Task 2 payload.

The files on disk and in HEAD are correct and byte-identical to the plan specification. The attribution is cosmetic only. Future parallel plan executions should either serialize the final commit or use git worktrees to eliminate index races.

### Deferred Items

**Terraform CLI execution deferred to user setup**
- Plan explicitly states: "Plan 01 does NOT actually run `terraform apply` — that is a user setup step"
- Scaffold-first mode: all IaC files landed, local `terraform validate` is green, but no cloud resources were provisioned this session.
- User must run `gcloud auth application-default login` + `terraform apply` when ready to bring the VM live.

## Known Stubs

None. `startup.sh` uses a placeholder `/opt/n8n/.env` on the VM (with `N8N_PASSWORD=CHANGE_ME_BEFORE_FIRST_START` and `AI_SERVICE_URL=https://ai-service-PLACEHOLDER-uc.a.run.app`), but this is intentional — the operator edits it after first SSH, and the unit is deliberately not started by the startup script to prevent a fail-start before real values are in place. This is documented in `README.md` post-apply steps and in STATE.md Phase 05 Decisions.

## Next Steps

- **Plan 05-03:** Build the n8n workflow JSON (Gmail Trigger → filter → /chat → reply + fallback + error handler). Exported workflow JSON lands in `n8n/workflows/`, which is scp'd into `/opt/n8n/workflows/` on the VM by the operator.
- **Plan 05-04:** GCP Uptime Check, end-to-end smoke test, final phase summary.
- **User (when ready for live cloud):** Run `terraform apply` from `terraform/n8n-vm/` with `project_id` and `ssh_pub_key_path` vars, then follow the post-apply steps in `README.md`.

## Self-Check: PASSED

**Files verified on disk:**
- FOUND: `terraform/n8n-vm/main.tf`
- FOUND: `terraform/n8n-vm/variables.tf`
- FOUND: `terraform/n8n-vm/outputs.tf`
- FOUND: `terraform/n8n-vm/startup.sh` (95 lines, full content)
- FOUND: `terraform/n8n-vm/.gitignore`
- FOUND: `terraform/n8n-vm/README.md`
- FOUND: `n8n/systemd/n8n.service`

**Commits verified in git log:**
- FOUND: `b8637af` — `feat(05-01): add Terraform module for n8n GCE e2-micro VM`
- FOUND: `2e90f8d` — captured Task 2 payload (`startup.sh` full + `n8n/systemd/n8n.service`) during parallel 05-02 executor commit race

**Plan verification:** All 8 plan-level checks pass (terraform fmt, init, validate, bash -n, no Restart=always, no 5678, Documentation= in both files).
