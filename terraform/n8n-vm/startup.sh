#!/bin/bash
# Phase 5 Plan 01 Task 2 — GCE VM startup script
# Creates swap (D-10), installs Docker, deploys n8n as systemd service (EMAIL-06)
# Logs: sudo journalctl -u google-startup-scripts.service

set -euxo pipefail

# ──────────────────────────────────────────────────────────
# 1. Create 2GB swap file (D-10, Pitfall #2 OOM prevention)
# ──────────────────────────────────────────────────────────
if ! swapon --show | grep -q /swapfile; then
  fallocate -l 2G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# Tune swappiness (prefer RAM, use swap as overflow only)
echo 'vm.swappiness=10' > /etc/sysctl.d/99-swappiness.conf
sysctl -p /etc/sysctl.d/99-swappiness.conf

# ──────────────────────────────────────────────────────────
# 2. Install Docker + Compose plugin v2
# ──────────────────────────────────────────────────────────
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
  usermod -aG docker ubuntu
  systemctl enable docker
  systemctl start docker
fi

# Verify compose plugin v2
docker compose version || { echo "docker compose plugin v2 missing"; exit 1; }

# ──────────────────────────────────────────────────────────
# 3. Prepare /opt/n8n directory for docker-compose.yml and workflows/
# ──────────────────────────────────────────────────────────
mkdir -p /opt/n8n/workflows
chown -R ubuntu:ubuntu /opt/n8n

# Placeholder .env — operator MUST edit with real N8N_PASSWORD after first SSH
if [ ! -f /opt/n8n/.env ]; then
  cat > /opt/n8n/.env <<'EOF'
# PLACEHOLDER — operator must edit after first SSH
# See .planning/phases/05-n8n-email-bot/05-01-PLAN.md
N8N_USER=admin
N8N_PASSWORD=CHANGE_ME_BEFORE_FIRST_START
AI_SERVICE_URL=https://ai-service-PLACEHOLDER-uc.a.run.app
EOF
  chmod 600 /opt/n8n/.env
  chown ubuntu:ubuntu /opt/n8n/.env
fi

# ──────────────────────────────────────────────────────────
# 4. Install systemd unit (EMAIL-06)
# Unit file is fetched from the repo after operator scps it;
# for bootstrap we write it inline so reboot works even before first scp.
# IMPORTANT: this heredoc MUST match n8n/systemd/n8n.service byte-for-byte
# (including the Documentation= line). Acceptance criteria enforces this.
# ──────────────────────────────────────────────────────────
cat > /etc/systemd/system/n8n.service <<'UNIT'
[Unit]
Description=n8n Email Bot (Docker Compose) - Phase 5 EMAIL-06
Documentation=https://github.com/[repo]/blob/main/.planning/phases/05-n8n-email-bot/05-01-PLAN.md
After=docker.service network-online.target
Requires=docker.service
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/n8n
EnvironmentFile=/opt/n8n/.env
ExecStart=/usr/bin/docker compose up -d --remove-orphans
ExecStop=/usr/bin/docker compose down
ExecReload=/usr/bin/docker compose restart
Restart=on-failure
RestartSec=10
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable n8n.service

# Do NOT launch the n8n unit yet — /opt/n8n/docker-compose.yml does not
# exist until the operator scps it. Launching here would fail and mark the
# unit as failed. The operator starts the unit manually after copying the
# compose file — see terraform/n8n-vm/README.md for the exact post-apply
# steps (scp docker-compose.yml, edit /opt/n8n/.env, then start the unit).

echo "Startup script completed successfully at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
