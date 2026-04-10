# n8n VM Terraform Module

Provisions the GCE e2-micro VM that hosts the n8n email bot for Phase 5 (EMAIL-01, EMAIL-06). All infrastructure is defined as code so the host is reproducible from this commit.

## What it builds

- `google_compute_instance.n8n_vm` — e2-micro Ubuntu 22.04 LTS VM named `resume-bot-n8n`
- `google_compute_firewall.allow_ssh` — SSH-only (port 22) firewall rule
- Boot-time `startup.sh` that creates a 2GB swap file (D-10), installs Docker + Compose plugin v2, and installs the `n8n.service` systemd unit (EMAIL-06)

The n8n UI (port 5678) is **NOT** publicly reachable by design (D-09). SSH in and use `localhost:5678` via SSH port forward if UI access is needed:

```bash
ssh -L 5678:localhost:5678 ubuntu@<VM_IP>
```

## Usage

```bash
cd terraform/n8n-vm
terraform init
terraform apply \
  -var="project_id=YOUR_PROJECT_ID" \
  -var="ssh_pub_key_path=$HOME/.ssh/id_ed25519.pub"
```

Outputs: `instance_ip`, `instance_name`, `ssh_command`.

## Post-apply manual steps

After `terraform apply` completes, the VM exists and the systemd unit is enabled — but n8n cannot start yet because the compose file and env file are not on the VM. Run these from the repo root:

1. **Copy compose file + workflows to the VM:**
   ```bash
   IP=$(terraform -chdir=terraform/n8n-vm output -raw instance_ip)
   scp n8n/docker-compose.yml ubuntu@$IP:/opt/n8n/
   scp -r n8n/workflows ubuntu@$IP:/opt/n8n/
   ```

2. **Edit `/opt/n8n/.env` on the VM** (a placeholder was created by `startup.sh`):
   ```bash
   ssh ubuntu@$IP
   sudo nano /opt/n8n/.env
   # Set N8N_PASSWORD to a real password
   # Set AI_SERVICE_URL to the Cloud Run HTTPS URL from Phase 4
   ```

3. **Start n8n via systemd:**
   ```bash
   sudo systemctl start n8n
   sudo systemctl status n8n
   ```

## Design notes

- **No port 5678 firewall rule** (D-09) — n8n UI is admin-only via SSH tunnel.
- **2GB swap** (D-10) — prevents OOM on e2-micro under n8n + Docker + OS load.
- **systemd `Type=oneshot` + `RemainAfterExit=yes`** — canonical pattern for wrapping `docker compose up -d`.
- **`Restart=on-failure`** (not `always`) — avoids conflict with Docker Compose's `restart: unless-stopped` (Pitfall #3).
