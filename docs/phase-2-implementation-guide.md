# Resume API — Phase 2 Implementation Guide
## Transform a Static Demo into a Live End-to-End Data Pipeline

**Goal:** Take the Phase 1 REST API (9 endpoints on Cloud Run) and build a complete data pipeline around it — persistent hosting, live traffic simulation, automated ETL, and BigQuery analytics — all on GCP free tier.
**Total Cost:** $0.00 (Google Cloud Always Free tier)
**Primary Tool:** Firebase Studio with Gemini AI-assisted development
**Prerequisite:** Phase 1 complete (API deployed on Cloud Run, BigQuery dataset with 500K rows)

---

## WHAT YOU'RE BUILDING

Phase 1 was a static demo — fake data, manual uploads, ephemeral hosting. Phase 2 makes the pipeline real:

| Component | Phase 1 (Static) | Phase 2 (Live Pipeline) |
|-----------|------------------|------------------------|
| Hosting | Cloud Run (ephemeral, scales to zero) | e2-micro VM (persistent, always on) |
| Traffic | No real traffic | Locust simulator generating realistic recruiter hits |
| Data Collection | Simulated via `generate_data.py` | Live middleware capturing every request |
| ETL | Manual `bq load` from CSV | Automated APScheduler syncing SQLite → BigQuery every 6 hours |
| Analytics | Queries on static 500K rows | Queries on live, growing data from real pipeline |
| Containers | Single Dockerfile | Docker Compose orchestrating 2 services on VM |
| Traffic Source | None | Cloud Shell running Locust → hits VM over the internet |

```
Phase 1:                          Phase 2:
[generate_data.py]                [Cloud Shell: Locust]
       │                                 │ (real internet traffic)
       ▼                                 ▼
[SQLite] + [CSV]                  [e2-micro VM: FastAPI + Middleware]
       │                                 │
  [manual bq load]                [SQLite (live logs)]
       │                                 │
       ▼                            [APScheduler ETL]
  [BigQuery]                             │
                                         ▼
                                    [BigQuery]
                                         │
                                         ▼
                                  [Analytics Queries]
```

**The end result:** A split architecture where traffic originates from Cloud Shell, crosses the real internet to hit your API on a free VM, gets captured by middleware, syncs to BigQuery via ETL, and becomes queryable — the same operational → analytical pipeline pattern used in ad tech consulting. Traffic actually travels over the network, just like real recruiter visits.

---

## ARCHITECTURE OVERVIEW

```
┌──────────────────────────────────────────────────┐
│  GCP Cloud Shell (Free)                           │
│                                                    │
│  ┌──────────────────────┐                         │
│  │  Locust               │                         │
│  │  3 simulated users    │                         │
│  │  Weighted tasks       │                         │
│  └──────────┬───────────┘                         │
└─────────────┼─────────────────────────────────────┘
              │ real internet traffic
              │ (HTTP to VM external IP)
              ▼
┌──────────────────────────────────────────────────────────────┐
│  GCP e2-micro VM (Always Free — 2 vCPU, 1 GB RAM)           │
│                                                               │
│  ┌─────────────────┐                                         │
│  │  API Container   │  Port 8080 (public)                    │
│  │  (FastAPI)       │  Receives real network traffic          │
│  │  + Middleware     │  Captures IP, User-Agent, Referer      │
│  └────────┬─────────┘                                         │
│           │ logs every request                                │
│  ┌────────▼─────────┐                                         │
│  │  SQLite           │  ./data/queries.db                     │
│  │  synced_to_bq     │  Tracks what's been sent to BigQuery   │
│  │  tracking         │                                         │
│  └────────┬─────────┘                                         │
│           │                                                    │
│  ┌────────▼──────────────┐                                    │
│  │  ETL Container         │                                    │
│  │  (APScheduler)         │                                    │
│  │  Every 6 hours:        │                                    │
│  │  SQLite → BigQuery     │                                    │
│  └────────┬──────────────┘                                    │
│           │                                                    │
│  systemd: auto-start on boot                                  │
│  fail2ban: SSH protection                                     │
└───────────┼────────────────────────────────────────────────────┘
            │
   ┌────────▼────────────────┐
   │  BigQuery               │
   │  resume_analytics       │
   │  (Analytical Warehouse) │
   │  Growing dataset        │
   └─────────────────────────┘
```

> **Why separate machines?** If Locust runs on the same VM as the API, traffic never leaves the machine — it's just localhost-to-localhost. By running Locust from Cloud Shell, requests travel over the real internet. The middleware captures real external IPs, realistic latency, and actual network behavior. This is how production traffic works.

---

## WHERE AM I? — LOCATION GUIDE (Phase 2 Additions)

Phase 2 adds a new environment — the e2-micro VM. Watch for these tags:

| Tag | Where | What It Looks Like |
|-----|-------|-------------------|
| 📍 **GCP Console** | Google Cloud Console in your browser | `console.cloud.google.com` — clicking buttons, enabling APIs |
| 📍 **Firebase Terminal** | Terminal panel inside Firebase Studio | Black terminal at the bottom of the IDE — bash commands |
| 📍 **Firebase Editor** | Code editor inside Firebase Studio | The file tabs at the top — editing .py files |
| 📍 **VM Terminal** | SSH session into your e2-micro VM | `gcloud compute ssh` or browser-based SSH from GCP Console |
| 📍 **Cloud Shell** | GCP's free browser-based terminal | `console.cloud.google.com` → click the `>_` icon top-right. Pre-authenticated, no setup needed |
| 📍 **BigQuery Console** | BigQuery UI in your browser | `console.cloud.google.com/bigquery` — running SQL queries |
| 📍 **Your Browser** | Your actual browser | Visiting deployed URLs, testing endpoints |

> **New in Phase 2:** Most development still happens in Firebase Studio. Deployment and verification happen on the VM. Traffic simulation runs from Cloud Shell — a separate machine so traffic travels over the real internet to reach your API.

---

## PRE-FLIGHT CHECKLIST

📍 **Firebase Terminal**

Before starting Phase 2, verify your Phase 1 infrastructure is intact:

```bash
# 1. Check your Cloud Run service is still deployed
gcloud run services describe resume-api --region=us-central1 --format="value(status.url)"
# Expected: https://resume-api-xxxxx-uc.a.run.app

# 2. Verify the API responds
curl -s "$(gcloud run services describe resume-api --region=us-central1 --format='value(status.url)')/" | python3 -m json.tool
# Expected: {"status": "healthy", ...}

# 3. Check BigQuery dataset exists
bq ls
# Expected: resume_analytics listed

# 4. Verify BigQuery has data
bq query --use_legacy_sql=false 'SELECT COUNT(*) as rows FROM resume_analytics.recruiter_queries'
# Expected: 500000

# 5. Verify your GCP project
gcloud config get-value project
# Expected: resume-api-portfolio
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `gcloud run services describe` | Shows details about a deployed Cloud Run service |
| `--format="value(status.url)"` | Extracts just the URL from the service description |
| `bq ls` | Lists all BigQuery datasets in the current project |
| `bq query` | Runs a SQL query in BigQuery from the terminal |

</em></sub>

> **If Cloud Run is down:** That's fine — Phase 2 replaces Cloud Run with persistent VM hosting. You just need the code in your repo and BigQuery data intact.

> **If BigQuery is empty:** Re-upload from Phase 1:
> ```bash
> uv run -- python scripts/generate_data.py
> bq load --source_format=CSV --autodetect --skip_leading_rows=1 \
>   resume_analytics.recruiter_queries data/recruiter_queries.csv
> ```

---

## PHASE 6: QUICK START — RESTARTING PHASE 1 (15 minutes)

> 📍 **Firebase Editor** — updating existing documentation
>
> Before building new infrastructure, add a Quick Start section to your Phase 1 guide so anyone (including future-you) can restart the existing deployment fast.

### Step 6.1 — Append Quick Start to Implementation Guide
📍 **Firebase Editor** — open `docs/implementation-guide.md`

Scroll to the end of the guide (before the CLEANUP section if present). Add this new section:

```markdown
---

## QUICK START: RESTARTING PHASE 1

> Returning to the project after time away? Use these commands to verify and restart
> your Phase 1 infrastructure without re-reading the full guide.

### Check Service Status
📍 **Firebase Terminal**

```bash
# Is the Cloud Run service still deployed?
gcloud run services describe resume-api --region=us-central1 --format="value(status.url)"

# Does it respond?
BASE_URL=$(gcloud run services describe resume-api --region=us-central1 --format='value(status.url)')
curl -s "$BASE_URL/" | python3 -m json.tool
```

### If Service Is Down — Redeploy
📍 **Firebase Terminal**

```bash
# Re-authenticate if needed
gcloud auth list
# If your account doesn't have a * next to it:
gcloud auth login

# Set project
gcloud config set project resume-api-portfolio

# Regenerate requirements.txt (in case pyproject.toml changed)
uv pip compile pyproject.toml -o requirements.txt

# Deploy
gcloud run deploy resume-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 256Mi \
  --max-instances 1
```

### Verify All 9 Endpoints
📍 **Firebase Terminal**

```bash
BASE_URL=$(gcloud run services describe resume-api --region=us-central1 --format='value(status.url)')

curl -s "$BASE_URL/" | python3 -m json.tool
curl -s "$BASE_URL/resume" | python3 -m json.tool
curl -s "$BASE_URL/resume/experience" | python3 -m json.tool
curl -s "$BASE_URL/resume/skills" | python3 -m json.tool
curl -s "$BASE_URL/resume/education" | python3 -m json.tool
curl -s "$BASE_URL/resume/certifications" | python3 -m json.tool
curl -s "$BASE_URL/analytics/queries?limit=3" | python3 -m json.tool
curl -s "$BASE_URL/analytics/top-domains?n=5" | python3 -m json.tool
curl -s "$BASE_URL/analytics/performance" | python3 -m json.tool
```

### Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| "Service not found" | Wrong region or service deleted | Check: `gcloud run services list` — deploy again if missing |
| "Permission denied" | Auth token expired | Run: `gcloud auth login` |
| "Build failed" | Code issue or missing requirements.txt | Check: `docker build .` locally, verify `requirements.txt` exists |
| "502 Bad Gateway" | Container crashing on startup | Check: `gcloud run services logs read resume-api --region=us-central1` |
| BigQuery returns 0 rows | Dataset deleted or wrong project | Check: `bq ls` then re-upload CSV if needed |
```

### Step 6.2 — Git Commit
📍 **Firebase Terminal**

```bash
git add "docs/implementation-guide.md"
git commit -m "Add Quick Start restart section to Phase 1 guide"
```

---

## PHASE 7: PERSISTENT HOSTING — DOCKER COMPOSE ON e2-micro (1-2 hours)

> Phase 1 used Cloud Run — serverless, scales to zero, but ephemeral. You can't run a traffic simulator or scheduled ETL on something that shuts down when idle. Phase 2 needs a persistent VM.
>
> 📍 **Phase 7 switches between Firebase Studio (code) and GCP Console (VM creation).**

### Step 7.1 — Create e2-micro VM Instance
📍 **GCP Console → Compute Engine**

1. Go to: `https://console.cloud.google.com/compute/instances`
2. If prompted to enable the Compute Engine API, click **Enable** (takes 1-2 minutes)
3. Click **"Create Instance"**
4. Configure:

| Setting | Value | Why |
|---------|-------|-----|
| Name | `resume-api-vm` | Descriptive, matches project |
| Region | `us-central1` | Free tier eligible |
| Zone | `us-central1-a` | Any zone in region works |
| Machine type | `e2-micro` | **Always Free** (2 vCPU burst, 1 GB RAM) |
| Boot disk | Debian 12 (Bookworm), 30 GB standard | Free tier: 30 GB standard persistent disk |
| Firewall | Check both: "Allow HTTP" and "Allow HTTPS" | Lets traffic reach port 8080 |

5. Click **"Create"**

> **What is e2-micro?** It's Google Cloud's smallest (and free) VM. You get 2 shared vCPUs that can burst and 1 GB of RAM. It's enough for 3 lightweight Docker containers. The "Always Free" tier gives you 1 e2-micro per billing account (not per project) in select US regions.

> **Cost check:** e2-micro in us-central1 = $0.00/month. 30 GB standard disk = $0.00/month. Both covered by Always Free tier. Verify at: `https://cloud.google.com/free/docs/free-cloud-features#compute`

### Step 7.2 — Configure Firewall for Port 8080
📍 **GCP Console → VPC Network → Firewall**

The default HTTP rule only opens port 80. Your API runs on 8080.

1. Go to: `https://console.cloud.google.com/networking/firewalls`
2. Click **"Create Firewall Rule"**
3. Configure:

| Setting | Value |
|---------|-------|
| Name | `allow-api-8080` |
| Direction | Ingress |
| Targets | All instances in the network |
| Source IP ranges | `0.0.0.0/0` |
| Protocols and ports | TCP: `8080` |

4. Click **"Create"**

<sub><em style="color: #999; font-size: 0.65em;">

💡 Why port 8080?

Your FastAPI app listens on port 8080 (matching the Cloud Run convention from Phase 1). The default "Allow HTTP" firewall rule only opens port 80. Without this rule, external traffic can't reach your API.

</em></sub>

### Step 7.3 — SSH into the VM and Install Docker
📍 **VM Terminal** (SSH into your new VM)

**Connect via browser SSH:**
1. Go to: `https://console.cloud.google.com/compute/instances`
2. Click **"SSH"** next to `resume-api-vm`
3. A terminal window opens in your browser — you're now on the VM

**Or connect via gcloud (from Firebase Terminal):**
```bash
gcloud compute ssh resume-api-vm --zone=us-central1-a
```

**Install Docker and Docker Compose:**
📍 **VM Terminal**

```bash
# Update package list
sudo apt-get update

# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to the docker group (so you don't need sudo for every docker command)
sudo usermod -aG docker $USER

# Apply group change (or log out and back in)
newgrp docker

# Verify
docker --version
docker compose version
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `sudo apt-get update` | Refreshes the list of available packages from Debian repositories |
| `sudo apt-get install -y` | Installs packages. `-y` = auto-confirm (don't ask yes/no) |
| `curl -fsSL` | Downloads a file silently. `-f` = fail on error, `-s` = silent, `-S` = show errors, `-L` = follow redirects |
| `gpg --dearmor` | Converts a GPG key to binary format (required by apt) |
| `sudo tee` | Writes to a file that requires root permissions |
| `sudo usermod -aG docker $USER` | Adds your user to the `docker` group so you can run docker without sudo |
| `newgrp docker` | Activates the group change without logging out |

</em></sub>

**Verify Docker works:**

```bash
docker run hello-world
```

You should see "Hello from Docker!" — confirming the installation works.

### Step 7.4 — Clone Your Repository on the VM
📍 **VM Terminal**

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/resume-api.git
cd resume-api

# Verify the code is there
ls -la api/ data/ sql/
```

> **Replace `YOUR_USERNAME`** with your actual GitHub username. If the repo is private, you'll need to set up a personal access token or SSH key.

### Step 7.5 — Create docker-compose.yml
📍 **Firebase Studio → Gemini Chat** (generate the file, then push to GitHub, then pull on VM)

> **Workflow note:** You write and test code in Firebase Studio, push to GitHub, then pull on the VM. This keeps Firebase Studio as your development environment and the VM as your deployment target.

**PROMPT TO COPY (paste into Gemini):**

```
Read docs/gemini-context.md first. Then create docker-compose.yml at the repo root.

This is a Phase 2 addition. Do NOT modify any existing Phase 1 files.

Create docker-compose.yml with a SINGLE service for now (we add more services later):

services:
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_PATH=/app/data/queries.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

IMPORTANT:
- Only the api service for now. Traffic simulator and ETL are added in later phases.
- Volume mount ./data:/app/data maps the host's data directory into the container
- restart: unless-stopped means the container auto-restarts if it crashes
- The healthcheck uses curl to verify the API is responding

Do NOT add version: '3.8' at the top — it's deprecated in modern Docker Compose.
Add comments explaining each section.
```

**After Gemini generates the file, verify:**

```bash
grep -n 'services:' docker-compose.yml
grep -n 'api:' docker-compose.yml
grep -n '8080:8080' docker-compose.yml
grep -n 'healthcheck' docker-compose.yml
grep -n 'restart' docker-compose.yml
```

Each grep should print at least one line. If any prints nothing, tell Gemini what's missing.

### Step 7.6 — Create API Dockerfile (Multi-Stage Build)
📍 **Firebase Studio → Gemini Chat**

**PROMPT TO COPY:**

```
Read docs/gemini-context.md first. Create api/Dockerfile — this is SEPARATE from the root
Dockerfile (which is for Cloud Run). This new Dockerfile is for Docker Compose.

Use a multi-stage build:

Stage 1 (builder):
- FROM python:3.11-slim AS builder
- Create virtual environment at /opt/venv
- Copy requirements.txt and pip install into the venv

Stage 2 (runtime):
- FROM python:3.11-slim
- Copy the venv from builder stage
- Install curl (needed for healthcheck)
- Copy application code
- Create non-root user "appuser" for security
- Run as appuser
- CMD: uvicorn main:app --host 0.0.0.0 --port 8080

IMPORTANT:
- This Dockerfile is in api/ directory, so COPY . . copies from api/ context
- The CMD uses main:app (not api.main:app) because the build context is already api/
- Install curl with: apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
- Non-root user: useradd -m appuser && chown -R appuser:appuser /app

Also create api/requirements.txt with ONLY the API dependencies (not the data generation
or BigQuery packages — those go in other containers):
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0

Do NOT modify the root-level Dockerfile or requirements.txt.
Add comments explaining the multi-stage build and why it reduces image size.
```

**Verify:**

```bash
grep -n 'FROM python:3.11-slim' api/Dockerfile
# Expected: 2 lines (builder stage + runtime stage)

grep -n 'appuser' api/Dockerfile
# Expected: at least 1 line (non-root user)

cat api/requirements.txt
# Expected: fastapi, uvicorn, pydantic (3 packages)
```

> **Why multi-stage?** The builder stage installs all the build tools needed for pip (gcc, headers, etc.). The runtime stage only copies the finished virtual environment — no build tools, smaller image. This typically saves 20-30% image size.

> **Why a separate Dockerfile?** The root Dockerfile (Phase 1) copies the entire project and is designed for Cloud Run's build system. The api/Dockerfile is optimized for Docker Compose — it only includes the API code, uses a non-root user, and has a healthcheck. Different deployment targets need different container configurations.

### Step 7.7 — Create .env.example and systemd Service
📍 **Firebase Studio → Gemini Chat**

**PROMPT TO COPY:**

```
Read docs/gemini-context.md first. Create two files:

1. .env.example at repo root — template showing all environment variables for Phase 2:

# === API Configuration ===
DATABASE_PATH=/app/data/queries.db

# === BigQuery Configuration (Phase 2.5 — ETL) ===
# Uncomment when setting up ETL pipeline
# GCP_PROJECT_ID=your-project-id
# BIGQUERY_DATASET=resume_api_analytics
# BIGQUERY_TABLE=api_queries
# GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account-key.json

# === Traffic Simulator Configuration (Phase 2.4) ===
# Uncomment when setting up traffic simulation
# TARGET_HOST=http://api:8080
# LOCUST_USERS=3
# LOCUST_SPAWN_RATE=1

2. systemd/resume-api.service — auto-start Docker Compose on VM boot:

[Unit]
Description=Resume API Data Pipeline
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/YOUR_USERNAME/resume-api
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target

Add comments explaining each section in both files.
Also create the systemd/ directory if it doesn't exist: mkdir -p systemd
```

> **What is systemd?** It's Linux's service manager — the thing that starts services when the machine boots. Without this, your Docker containers would stop running whenever the VM restarts. The service file tells systemd: "after Docker is ready, run `docker compose up -d` to start all containers."

> **YOUR_USERNAME placeholder:** You'll replace this with your actual VM username when deploying. The default on GCP is usually your Google account username (the part before @gmail.com).

### Step 7.8 — Update .gitignore
📍 **Firebase Editor**

Add these lines to your `.gitignore`:

```
# Phase 2 additions
.env
credentials/
*.json
!.env.example
```

> **Why?** `.env` contains real configuration values (project IDs, paths). `credentials/` will hold your BigQuery service account key. Neither should be in Git. The `!.env.example` line means "but DO track the template file."

### Step 7.9 — Test Docker Compose Locally
📍 **Firebase Terminal** (if Docker is available) or 📍 **VM Terminal**

```bash
# Build and start
docker compose up --build -d

# Check status
docker compose ps
# Expected: api service running, status "Up" or "healthy"

# Test the API
curl http://localhost:8080/
# Expected: {"status": "healthy", ...}

curl http://localhost:8080/resume | python3 -m json.tool
# Expected: Full resume JSON

# Check logs
docker compose logs api
# Expected: Uvicorn startup messages, no errors

# Stop
docker compose down
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `docker compose up` | `--build -d` | Builds images and starts containers. `--build` = rebuild even if image exists. `-d` = detached (background) |
| `docker compose ps` | | Shows running containers and their status |
| `docker compose logs` | `api` | Shows logs from the api container |
| `docker compose down` | | Stops and removes all containers |

</em></sub>

### Step 7.10 — Git Commit and Push
📍 **Firebase Terminal**

```bash
git add docker-compose.yml api/Dockerfile api/requirements.txt
git add systemd/resume-api.service .env.example .gitignore
git commit -m "Add Docker Compose infrastructure for persistent hosting"
git push
```

### Step 7.11 — Deploy to VM
📍 **VM Terminal** (SSH into your e2-micro)

```bash
cd ~/resume-api
git pull origin main

# Create the data directory (for SQLite volume mount)
mkdir -p data

# Build and start
docker compose up --build -d

# Verify
docker compose ps
curl http://localhost:8080/

# Get the VM's external IP
curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google"
```

**Test from your browser:**

📍 **Your Browser**

```
http://YOUR_VM_EXTERNAL_IP:8080/
http://YOUR_VM_EXTERNAL_IP:8080/docs
http://YOUR_VM_EXTERNAL_IP:8080/resume
```

> **If the browser can't connect:** Check the firewall rule from Step 7.2. Go to GCP Console → VPC Network → Firewall and verify `allow-api-8080` exists with TCP port 8080 open to `0.0.0.0/0`.

### Step 7.12 — Set Up Auto-Start with systemd
📍 **VM Terminal**

```bash
# Copy service file
sudo cp systemd/resume-api.service /etc/systemd/system/

# Edit to replace YOUR_USERNAME with your actual username
sudo nano /etc/systemd/system/resume-api.service
# Change WorkingDirectory to: /home/YOUR_ACTUAL_USERNAME/resume-api

# Reload systemd, enable and start
sudo systemctl daemon-reload
sudo systemctl enable resume-api
sudo systemctl start resume-api

# Verify it's running
sudo systemctl status resume-api
docker compose ps
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `sudo cp` | Copies a file with root privileges (needed for /etc/systemd/) |
| `sudo nano` | Opens a text editor with root privileges |
| `sudo systemctl daemon-reload` | Tells systemd to re-read service files (required after changes) |
| `sudo systemctl enable` | Marks a service to start automatically on boot |
| `sudo systemctl start` | Starts the service immediately |
| `sudo systemctl status` | Shows whether the service is running |

</em></sub>

**Test auto-start by rebooting the VM:**

```bash
sudo reboot
```

Wait 1-2 minutes, then SSH back in and verify:

```bash
docker compose ps
curl http://localhost:8080/
```

If the API responds after reboot, auto-start is working.

---

## PHASE 8: MIDDLEWARE & FUNNEL TRACKING — LIVE REQUEST LOGGING (1-2 hours)

> Phase 1's middleware logged basic request info. Phase 2 enhances it to capture comprehensive recruiter funnel data — every request is tagged with a session ID, campaign, traffic source, funnel stage, device type, and geo region. Non-blocking, so API latency stays under 50ms.
>
> This phase also adds 2 new POST endpoints that complete the recruiter interaction funnel: shortlisting and requesting contact. These are the "conversion events" that make the pipeline analytically interesting.
>
> 📍 **All development in Firebase Studio. Deploy to VM via git push/pull.**

### Step 8.1 — Prompt for Gemini: Enhanced Logging Middleware
📍 **Firebase Studio → Gemini Chat**

> Before pasting this prompt, run the state check:
> ```bash
> head -20 api/main.py api/database.py
> ```
> Paste the output at the top of your prompt.

**PROMPT TO COPY:**

```
Read docs/gemini-context.md first. I need to enhance the request logging system for Phase 2.
This captures live recruiter funnel data that will be synced to BigQuery by an ETL pipeline.

OVERVIEW: The middleware captures every API request and tags it with recruiter session
context (sent via custom headers by our traffic simulator). This creates an analytics
dataset that tracks the full recruiter journey: impression → engagement → contact.

Create api/middleware/logging.py with a LoggingMiddleware class:

CRITICAL TECHNICAL DETAIL:
Use starlette.background.BackgroundTask attached to response.background — NOT
BaseHTTPMiddleware with BackgroundTasks. There is a known incompatibility where
BackgroundTasks inside BaseHTTPMiddleware lose context. The correct pattern is:

from starlette.background import BackgroundTask

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)

        log_data = {
            "timestamp": time.time(),
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "recruiter_domain": self._extract_domain(request),
            "user_agent": request.headers.get("user-agent", ""),
            "client_ip": request.client.host if request.client else "",
            "status_code": response.status_code,
            "response_time_ms": round((time.time() - start_time) * 1000, 2),
            # Funnel tracking — captured from custom headers sent by traffic simulator
            "session_id": request.headers.get("x-session-id"),
            "search_campaign": request.headers.get("x-search-campaign"),
            "traffic_source": request.headers.get("x-traffic-source"),
            "funnel_stage": request.headers.get("x-funnel-stage"),
            "device_type": request.headers.get("x-device-type"),
            "geo_region": request.headers.get("x-geo-region"),
        }

        # Non-blocking write — response returns immediately
        response.background = BackgroundTask(log_request_to_db, log_data)
        return response

    def _extract_domain(self, request):
        # Extract domain from Referer header, or use "direct" if none
        referer = request.headers.get("referer", "")
        if referer:
            from urllib.parse import urlparse
            return urlparse(referer).netloc or "direct"
        return "direct"

Also update api/database.py to add:
1. An init_db() function that creates the queries table:

CREATE TABLE IF NOT EXISTS queries (
    query_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    method TEXT NOT NULL DEFAULT 'GET',
    path TEXT NOT NULL,
    query_params TEXT,
    recruiter_domain TEXT DEFAULT 'direct',
    user_agent TEXT,
    client_ip TEXT,
    status_code INTEGER DEFAULT 200,
    response_time_ms REAL,
    synced_to_bq INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    -- Funnel tracking columns (populated by traffic simulator headers)
    session_id TEXT,
    search_campaign TEXT,
    traffic_source TEXT,
    funnel_stage TEXT,
    device_type TEXT,
    geo_region TEXT
);
-- Existing indexes
CREATE INDEX IF NOT EXISTS idx_queries_synced ON queries(synced_to_bq);
CREATE INDEX IF NOT EXISTS idx_queries_timestamp ON queries(timestamp);
CREATE INDEX IF NOT EXISTS idx_queries_domain ON queries(recruiter_domain);
-- Funnel indexes (for analytical queries)
CREATE INDEX IF NOT EXISTS idx_queries_session ON queries(session_id);
CREATE INDEX IF NOT EXISTS idx_queries_campaign ON queries(search_campaign);
CREATE INDEX IF NOT EXISTS idx_queries_funnel ON queries(funnel_stage);

2. A log_request_to_db(data) function that inserts a row (all 18 columns).
3. A get_db_connection() function that returns a sqlite3 connection to data/queries.db

The synced_to_bq column is critical — the ETL pipeline uses it to track
which rows have been sent to BigQuery. Default 0 = not synced.

The 6 funnel columns (session_id through geo_region) are nullable — when
someone hits the API directly (not through the traffic simulator), these
will be NULL. The middleware captures them if present, ignores if not.

Also update api/main.py to:
1. Import and add the new middleware
2. Call init_db() at startup using @app.on_event("startup")
3. Update CORS to allow POST method: allow_methods=["GET", "POST"]
4. Do NOT modify any existing GET endpoints

IMPORTANT:
- The queries table is SEPARATE from api_queries (which is Phase 1 static data)
- The new middleware captures LIVE request data with funnel context
- Non-blocking writes: response returns before the database write completes
- Keep all existing Phase 1 code unchanged
```

**After Gemini generates the code, verify:**

```bash
# Check middleware file exists
ls -la api/middleware/logging.py

# Check it uses BackgroundTask (not BackgroundTasks)
grep -n 'BackgroundTask' api/middleware/logging.py
# Expected: import from starlette.background

# Check database has new functions
grep -n 'def init_db' api/database.py
grep -n 'def log_request' api/database.py
grep -n 'synced_to_bq' api/database.py

# Check funnel columns exist in schema
grep -n 'session_id' api/database.py
grep -n 'search_campaign' api/database.py
grep -n 'funnel_stage' api/database.py
# Expected: each appears in CREATE TABLE

# Check main.py has new middleware
grep -n 'LoggingMiddleware' api/main.py
grep -n 'init_db' api/main.py

# Check CORS allows POST
grep -n 'allow_methods' api/main.py
# Expected: ["GET", "POST"]
```

Also create the `__init__.py` for the middleware package:

```bash
touch api/middleware/__init__.py
```

### Step 8.2 — Prompt for Gemini: Recruiter Funnel Endpoints
📍 **Firebase Studio → Gemini Chat**

These two POST endpoints complete the recruiter interaction funnel. They represent the "conversion" actions — when a recruiter goes beyond browsing and takes action on a candidate.

> **The funnel pattern:**
> - **Impression**: Recruiter views resume (`GET /resume`) — everyone does this
> - **Engagement**: Recruiter explores details (`GET /resume/experience`, `/skills`, etc.) — ~55% do this
> - **Contact**: Recruiter takes action (`POST /resume/shortlist` or `/resume/contact`) — ~15% do this
>
> This is the same impression → engagement → conversion pattern used in ad campaign measurement. The endpoints exist to generate trackable "conversion events" in the pipeline.

**PROMPT TO COPY:**

```
Read docs/gemini-context.md first. Add 2 new POST endpoints and their Pydantic models.

Add to api/models.py:

class ContactRequest(BaseModel):
    """Recruiter requests contact with candidate."""
    recruiter_email: str
    company: str
    message: str
    role: str

class ShortlistRequest(BaseModel):
    """Recruiter adds candidate to a shortlist."""
    list_name: str
    priority: str  # "high", "medium", "low"

class ActionResponse(BaseModel):
    """Response for recruiter action endpoints."""
    status: str
    message: str
    confirmation_id: Optional[str] = None

Add to api/main.py (after existing /resume/* endpoints):

@app.post("/resume/contact", response_model=ActionResponse)
def request_contact(request_data: ContactRequest):
    """Recruiter requests an interview or sends a message.

    This is a portfolio demo — no actual message is sent.
    The request is logged by middleware for pipeline analytics.
    """
    import uuid
    return ActionResponse(
        status="received",
        confirmation_id=f"conf_{uuid.uuid4().hex[:8]}",
        message="Contact request logged. This is a portfolio demo — no actual message is sent."
    )

@app.post("/resume/shortlist", response_model=ActionResponse)
def shortlist_candidate(request_data: ShortlistRequest):
    """Recruiter saves candidate to a shortlist.

    This is a portfolio demo — no actual list is maintained.
    The request is logged by middleware for pipeline analytics.
    """
    return ActionResponse(
        status="shortlisted",
        message="Candidate added to shortlist. This is a portfolio demo."
    )

Also update the health endpoint's endpoint list to include the 2 new endpoints.

IMPORTANT:
- These endpoints do NOT persist data — they return static confirmations
- Their ONLY purpose is to generate log entries that the middleware captures
- The middleware logs these as funnel_stage="contact" events (the traffic simulator sends this header)
- The POST body is validated by Pydantic but otherwise discarded
- Do NOT modify any existing endpoints
```

**Verify:**

```bash
grep -n 'ContactRequest' api/models.py
grep -n 'ShortlistRequest' api/models.py
grep -n '/resume/contact' api/main.py
grep -n '/resume/shortlist' api/main.py
# Expected: each returns at least 1 line
```

> **Why POST, not GET?** These endpoints represent *actions* (contacting a candidate, adding to a shortlist), not data retrieval. Using POST follows REST conventions and adds HTTP method diversity to the dataset — your BigQuery queries can now analyze `GET` vs `POST` patterns, just like ad platforms distinguish impression events (GET) from conversion events (POST).

### Step 8.3 — Test Middleware Locally
📍 **Firebase Terminal**

```bash
# Start the API
cd ~/resume-api && uv run -- python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &
sleep 2

# Hit some endpoints to generate log entries
curl http://localhost:8000/
curl http://localhost:8000/resume
curl "http://localhost:8000/resume/skills?keyword=sql"
curl http://localhost:8000/analytics/top-domains

# Test new funnel endpoints
curl -X POST http://localhost:8000/resume/contact \
  -H "Content-Type: application/json" \
  -d '{"recruiter_email": "test@example.com", "company": "TestCorp", "message": "Interested", "role": "Engineer"}'
# Expected: {"status": "received", "confirmation_id": "conf_...", "message": "..."}

curl -X POST http://localhost:8000/resume/shortlist \
  -H "Content-Type: application/json" \
  -d '{"list_name": "Cloud Team Q3", "priority": "high"}'
# Expected: {"status": "shortlisted", "message": "..."}

# Check the database has logged entries
uv run -- python -c "
import sqlite3
conn = sqlite3.connect('data/queries.db')
cursor = conn.execute('SELECT COUNT(*) FROM queries')
print(f'Logged requests: {cursor.fetchone()[0]}')
cursor = conn.execute('SELECT path, status_code, response_time_ms, method FROM queries ORDER BY query_id DESC LIMIT 5')
for row in cursor.fetchall():
    print(f'  {row[3]} {row[0]} -> {row[1]} ({row[2]}ms)')
conn.close()
"
# Expected: 6+ logged requests, GET and POST methods, all with status 200 and response times < 50ms

# Stop the server
kill $(pgrep -f uvicorn)
```

> **What to check:** Every request should create a log entry. Response times should be under 50ms (proving the writes are non-blocking). The `synced_to_bq` column should default to 0. Both GET and POST requests should be logged.

### Step 8.4 — Git Commit and Deploy
📍 **Firebase Terminal**

```bash
git add api/middleware/ api/database.py api/main.py api/models.py
git commit -m "Add funnel-tracking middleware and recruiter action endpoints"
git push
```

📍 **VM Terminal**

```bash
cd ~/resume-api
git pull origin main
docker compose up --build -d

# Test on VM
curl http://localhost:8080/resume
curl http://localhost:8080/analytics/top-domains

# Test POST endpoints on VM
curl -X POST http://localhost:8080/resume/contact \
  -H "Content-Type: application/json" \
  -d '{"recruiter_email": "test@example.com", "company": "TestCorp", "message": "Interested", "role": "Engineer"}'

curl -X POST http://localhost:8080/resume/shortlist \
  -H "Content-Type: application/json" \
  -d '{"list_name": "Cloud Team Q3", "priority": "high"}'

# Verify logging works on VM
docker compose exec api python -c "
import sqlite3
conn = sqlite3.connect('/app/data/queries.db')
print(f'Rows: {conn.execute(\"SELECT COUNT(*) FROM queries\").fetchone()[0]}')
cursor = conn.execute('SELECT path, method, status_code FROM queries ORDER BY query_id DESC LIMIT 5')
for row in cursor.fetchall():
    print(f'  {row[1]} {row[0]} -> {row[2]}')
conn.close()
"
```

---

## PHASE 9: TRAFFIC SIMULATION — RECRUITER FUNNEL FROM CLOUD SHELL (1-2 hours)

> Without real recruiters hitting your API, the pipeline has no data. Locust simulates realistic recruiter behavior with a full interaction funnel — impression, engagement, and contact actions. Each simulated recruiter gets a unique session, campaign, traffic source, device, and region.
>
> **Key design choice:** Locust runs from **Cloud Shell** (a separate GCP machine), NOT on the VM. This means traffic travels over the real internet to reach your API — just like real recruiter visits. The middleware captures real external IPs, actual network latency, and the funnel context headers.
>
> **The funnel model:** Not every recruiter who views a resume digs deeper. Not every one who digs deeper reaches out. The simulator models this realistically:
> - **45%** of sessions: impression only (view resume, leave)
> - **40%** of sessions: impression + engagement (drill into sections)
> - **15%** of sessions: full conversion (shortlist or contact)
>
> 📍 **Development in Firebase Studio. Traffic simulation from Cloud Shell.**

### Step 9.1 — Prompt for Gemini: Locust Traffic Simulator
📍 **Firebase Studio → Gemini Chat**

**PROMPT TO COPY:**

```
Read docs/gemini-context.md first. Create a Locust-based traffic simulator for Phase 2.

IMPORTANT CONTEXT: The traffic simulator runs from GCP Cloud Shell, NOT on the same
VM as the API. It hits the API's public IP over the real internet. This is intentional —
we want real network traffic, not localhost-to-localhost.

Each simulated recruiter follows a probabilistic funnel:
  45% — impression only (view resume, leave)
  40% — impression + engagement (drill into resume sections)
  15% — impression + engagement + contact (full conversion)

Create traffic-simulator/locustfile.py:

import os
import random
from locust import HttpUser, task, between
from faker import Faker

fake = Faker()

# Recruiting campaigns — weighted distribution mirrors real job search patterns
CAMPAIGNS = [
    ("senior-cloud-eng-dc", 30),
    ("python-backend-remote", 25),
    ("solutions-architect-gcp", 20),
    ("data-eng-east", 15),
    ("devops-lead-central", 10),
]

# Traffic sources — where recruiters find the resume
TRAFFIC_SOURCES = [
    ("linkedin", 40),
    ("indeed", 25),
    ("google", 15),
    ("referral", 12),
    ("direct", 8),
]

DEVICE_TYPES = [("desktop", 70), ("mobile", 25), ("tablet", 5)]
GEO_REGIONS = [("us-east", 35), ("us-west", 25), ("us-central", 20), ("eu-west", 12), ("apac", 8)]


def weighted_choice(options):
    """Pick from list of (value, weight) tuples."""
    values, weights = zip(*options)
    return random.choices(values, weights=weights, k=1)[0]


class RecruiterUser(HttpUser):
    """Simulates a recruiter browsing the resume API with funnel behavior.

    Each recruiter has a predetermined funnel depth (set at spawn):
    - impression: views resume only
    - engagement: views resume + drills into sections
    - contact: full journey including shortlist/contact action

    Custom headers on every request enable funnel analytics in BigQuery.
    """
    wait_time = between(3, 15)  # Seconds between actions

    def on_start(self):
        """Initialize recruiter identity, session, and funnel depth."""
        # Identity
        self.recruiter_domain = fake.domain_name()
        self.user_agent = fake.chrome()

        # Session context (sent as headers, captured by middleware)
        self.session_id = f"sess_{fake.hexify(text='^^^^^^^^')}"
        self.campaign = weighted_choice(CAMPAIGNS)
        self.traffic_source = weighted_choice(TRAFFIC_SOURCES)
        self.device_type = weighted_choice(DEVICE_TYPES)
        self.geo_region = weighted_choice(GEO_REGIONS)

        # Determine funnel depth ONCE at spawn
        roll = random.random()
        if roll < 0.45:
            self.max_stage = "impression"      # 45% — view and leave
        elif roll < 0.85:
            self.max_stage = "engagement"      # 40% — dig deeper
        else:
            self.max_stage = "contact"         # 15% — take action

        # Progression flags
        self.has_impressed = False
        self.has_engaged = False
        self.has_converted = False

    def _headers(self, funnel_stage: str) -> dict:
        """Build request headers with funnel tracking context."""
        return {
            "User-Agent": self.user_agent,
            "Referer": f"https://{self.recruiter_domain}/careers",
            "X-Session-ID": self.session_id,
            "X-Search-Campaign": self.campaign,
            "X-Traffic-Source": self.traffic_source,
            "X-Funnel-Stage": funnel_stage,
            "X-Device-Type": self.device_type,
            "X-Geo-Region": self.geo_region,
        }

    # --- IMPRESSION STAGE (all recruiters) ---
    @task(10)
    def view_resume(self):
        """Every recruiter views the resume — this is the impression."""
        self.client.get("/resume", headers=self._headers("impression"))
        self.has_impressed = True

    # --- ENGAGEMENT STAGE (55% of recruiters) ---
    @task(5)
    def view_experience(self):
        if self.max_stage in ("engagement", "contact") and self.has_impressed:
            self.client.get("/resume/experience", headers=self._headers("engagement"))
            self.has_engaged = True
        else:
            self.view_resume()  # Impression-only users re-view

    @task(3)
    def search_skills(self):
        if self.max_stage in ("engagement", "contact") and self.has_impressed:
            skills = ["python", "sql", "bigquery", "docker", "aws", "api", "cloud"]
            skill = random.choice(skills)
            self.client.get(f"/resume/skills?keyword={skill}",
                          headers=self._headers("engagement"))
            self.has_engaged = True
        else:
            self.view_resume()

    @task(2)
    def view_education(self):
        if self.max_stage in ("engagement", "contact") and self.has_impressed:
            self.client.get("/resume/education", headers=self._headers("engagement"))
            self.has_engaged = True
        else:
            self.view_resume()

    @task(2)
    def view_certifications(self):
        if self.max_stage in ("engagement", "contact") and self.has_impressed:
            self.client.get("/resume/certifications", headers=self._headers("engagement"))
            self.has_engaged = True
        else:
            self.view_resume()

    # --- CONTACT STAGE (15% of recruiters, once per session) ---
    @task(1)
    def request_contact(self):
        """Hard conversion — recruiter reaches out for an interview."""
        if self.max_stage == "contact" and self.has_engaged and not self.has_converted:
            self.client.post("/resume/contact",
                           json={
                               "recruiter_email": fake.company_email(),
                               "company": fake.company(),
                               "message": "Interested in discussing this role.",
                               "role": self.campaign.replace("-", " ").title()
                           },
                           headers=self._headers("contact"))
            self.has_converted = True

    @task(1)
    def shortlist_candidate(self):
        """Micro-conversion — recruiter saves candidate to shortlist."""
        if self.max_stage == "contact" and self.has_engaged and not self.has_converted:
            self.client.post("/resume/shortlist",
                           json={
                               "list_name": self.campaign.replace("-", " ").title(),
                               "priority": random.choice(["high", "medium", "low"])
                           },
                           headers=self._headers("contact"))
            self.has_converted = True

Also create traffic-simulator/requirements.txt:
locust>=2.20.0
faker>=20.0.0

IMPORTANT:
- NO Dockerfile needed — this runs directly in Cloud Shell, not in a container
- The --host flag will point to the VM's external IP (not localhost or Docker DNS)
- 3 simulated users with 1/second spawn rate = light, steady traffic
- Each user has a unique session ID (like a click ID) that tracks their entire journey
- Funnel depth is decided at spawn — not every user converts (realistic)
- Conversion happens ONCE per session (has_converted flag prevents repeats)
- Custom headers are captured by the middleware's funnel tracking columns
```

**After Gemini generates the files, verify:**

```bash
ls -la traffic-simulator/locustfile.py traffic-simulator/requirements.txt

grep -c '@task' traffic-simulator/locustfile.py
# Expected: 7 (impression + 4 engagement + 2 contact)

grep -n 'X-Session-ID' traffic-simulator/locustfile.py
# Expected: appears in _headers method

grep -n 'X-Funnel-Stage' traffic-simulator/locustfile.py
# Expected: appears in _headers method

grep -n 'max_stage' traffic-simulator/locustfile.py
# Expected: 3+ lines (assignment in on_start + checks in tasks)

grep -n '/resume/contact' traffic-simulator/locustfile.py
grep -n '/resume/shortlist' traffic-simulator/locustfile.py
# Expected: POST requests to conversion endpoints

# Make sure there's NO Dockerfile (Cloud Shell runs it directly)
ls traffic-simulator/Dockerfile 2>/dev/null && echo "ERROR: Remove Dockerfile — Locust runs in Cloud Shell, not Docker" || echo "OK: No Dockerfile"
```

### Step 9.2 — Git Commit
📍 **Firebase Terminal**

```bash
git add traffic-simulator/
git commit -m "Add Locust traffic simulator with realistic recruiter patterns"
git push
```

> **Note:** We do NOT add traffic-simulator to docker-compose.yml. The simulator runs externally from Cloud Shell, not on the VM.

### Step 9.3 — Run Traffic Simulation from Cloud Shell
📍 **Cloud Shell** (open from GCP Console — click the `>_` icon in the top-right)

> **What is Cloud Shell?** It's a free Linux terminal built into the GCP Console. It comes pre-installed with `git`, `python3`, and `gcloud`. It runs on a separate machine from your VM, so traffic from Cloud Shell to your VM travels over Google's network — real network hops, real latency, real IP addresses.

```bash
# 1. Clone your repo in Cloud Shell
git clone https://github.com/YOUR_USERNAME/resume-api.git
cd resume-api/traffic-simulator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Get your VM's external IP
VM_IP=$(gcloud compute instances describe resume-api-vm \
  --zone=us-central1-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
echo "VM IP: $VM_IP"

# 4. Verify the API is reachable over the internet
curl http://$VM_IP:8080/
# Expected: {"status": "healthy", ...}

# 5. Start Locust (headless mode — no web UI needed)
locust --headless \
  --host http://$VM_IP:8080 \
  --users 3 \
  --spawn-rate 1 \
  --run-time 30m \
  --autostart
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `gcloud compute instances describe` | Gets details about a VM, including its external IP |
| `--format='get(...natIP)'` | Extracts just the external IP from the VM description |
| `locust --headless` | Runs Locust without the web UI (terminal output only) |
| `--users 3` | Simulates 3 concurrent recruiter sessions |
| `--spawn-rate 1` | Adds 1 user per second until all 3 are active |
| `--run-time 30m` | Runs for 30 minutes then stops. Use `0` for indefinite |

</em></sub>

<sub><em style="color: #999; font-size: 0.65em;">

What the custom headers do:

| Header | Example Value | What It Tracks |
|--------|-------------|----------------|
| `X-Session-ID` | `sess_a4f8c2e1` | Groups all requests from one recruiter into a session (like a click ID) |
| `X-Search-Campaign` | `senior-cloud-eng-dc` | Which recruiting search led the recruiter here (campaign attribution) |
| `X-Traffic-Source` | `linkedin` | Where the recruiter found the resume (channel attribution) |
| `X-Funnel-Stage` | `impression` / `engagement` / `contact` | What stage of the interaction this request represents |
| `X-Device-Type` | `desktop` | Recruiter's device type (segmentation dimension) |
| `X-Geo-Region` | `us-east` | Recruiter's geographic region (segmentation dimension) |

These headers are captured by the middleware (Phase 8) and stored in SQLite. The ETL (Phase 10) syncs them to BigQuery where they enable funnel analysis queries (Phase 11).

</em></sub>

> **Cloud Shell timeout:** Cloud Shell disconnects after ~20 minutes of inactivity. But as long as Locust is printing output, it counts as active. For longer runs, you can use `--run-time 2h` or keep the tab visible. If it disconnects, just re-run the `locust` command — the API keeps logging regardless.

**While Locust is running, verify data is being captured:**

📍 **VM Terminal** (open a separate SSH session)

```bash
# Check the middleware is logging real traffic
docker compose exec api python -c "
import sqlite3
conn = sqlite3.connect('/app/data/queries.db')
count = conn.execute('SELECT COUNT(*) FROM queries').fetchone()[0]
domains = conn.execute('SELECT DISTINCT recruiter_domain FROM queries LIMIT 5').fetchall()
ips = conn.execute('SELECT DISTINCT client_ip FROM queries LIMIT 5').fetchall()
stages = conn.execute('SELECT funnel_stage, COUNT(*) FROM queries WHERE funnel_stage IS NOT NULL GROUP BY funnel_stage').fetchall()
campaigns = conn.execute('SELECT DISTINCT search_campaign FROM queries WHERE search_campaign IS NOT NULL LIMIT 5').fetchall()
print(f'Total logged requests: {count}')
print(f'Sample domains: {[d[0] for d in domains]}')
print(f'Client IPs: {[ip[0] for ip in ips]}')
print(f'Funnel stages: {dict(stages)}')
print(f'Campaigns: {[c[0] for c in campaigns]}')
conn.close()
"
# Expected:
#   count growing
#   fake domains from Faker
#   Cloud Shell's REAL IP (not 172.x.x.x)
#   Funnel stages: {'impression': X, 'engagement': Y, 'contact': Z} where X > Y > Z
#   Campaigns: ['senior-cloud-eng-dc', 'python-backend-remote', ...]
```

> **Key check:** The `client_ip` values should be real external IPs (like `35.x.x.x` from Cloud Shell), NOT Docker internal IPs (like `172.17.0.x`). If you see Docker IPs, Locust is running on the same machine — go back and run it from Cloud Shell instead.

---

## PHASE 10: ETL PIPELINE — SQLITE TO BIGQUERY (2-3 hours)

> This is the centerpiece of Phase 2. The ETL (Extract, Transform, Load) pipeline automatically syncs live request data from SQLite into BigQuery every 6 hours — completing the full operational → analytical data flow.
>
> 📍 **Development in Firebase Studio. BigQuery setup in GCP Console. Deployment on VM.**

### Step 10.1 — Create BigQuery Dataset for Live Data
📍 **BigQuery Console** or 📍 **Firebase Terminal**

The Phase 1 dataset (`resume_analytics.recruiter_queries`) contains static generated data. Create a new table for live pipeline data:

```bash
# Option A: CLI (from Firebase Terminal or VM Terminal)
bq mk --table resume_analytics.pipeline_queries \
  query_id:INTEGER,request_timestamp:TIMESTAMP,http_method:STRING,endpoint_path:STRING,query_params:STRING,recruiter_domain:STRING,user_agent:STRING,client_ip:STRING,http_status_code:INTEGER,response_time_ms:FLOAT,created_at:TIMESTAMP,hour_of_day:INTEGER,day_of_week:STRING,date:DATE,session_id:STRING,search_campaign:STRING,traffic_source:STRING,funnel_stage:STRING,device_type:STRING,geo_region:STRING
```

**Or Option B: BigQuery Console UI:**
1. Go to: `https://console.cloud.google.com/bigquery`
2. Click on `resume_analytics` dataset
3. Click **"Create Table"**
4. Source: **Empty table**
5. Table name: `pipeline_queries`
6. Add schema fields manually (or use auto-detect on first load)

<sub><em style="color: #999; font-size: 0.65em;">

💡 Why a separate table?

Phase 1's `recruiter_queries` table has 500K rows of generated data — it's a snapshot for SQL demos. Phase 2's `pipeline_queries` table will contain real, growing data from the live pipeline. Keeping them separate lets you:
- Compare static vs live data patterns
- Preserve Phase 1 benchmarks unchanged
- Run queries that show pipeline growth over time

</em></sub>

### Step 10.2 — Create BigQuery Service Account
📍 **GCP Console → IAM & Admin → Service Accounts**

The ETL container needs credentials to write to BigQuery. On a VM (unlike Cloud Run), you need an explicit service account key.

1. Go to: `https://console.cloud.google.com/iam-admin/serviceaccounts`
2. Click **"Create Service Account"**
3. Name: `etl-pipeline`
4. Description: "ETL service for syncing SQLite data to BigQuery"
5. Click **"Create and Continue"**
6. Grant role: **BigQuery Data Editor** (allows inserting data)
7. Also add: **BigQuery Job User** (allows running load jobs)
8. Click **"Done"**
9. Click on the new service account → **"Keys"** tab → **"Add Key"** → **"Create new key"** → **JSON**
10. Download the key file

> **Security note:** This key file grants BigQuery write access. Never commit it to Git. The `.gitignore` entry from Step 7.8 prevents this.

**Copy the key to your VM:**

📍 **Firebase Terminal** or your local terminal:

```bash
# Create credentials directory on VM
gcloud compute ssh resume-api-vm --zone=us-central1-a --command="mkdir -p ~/resume-api/credentials"

# Copy key file to VM (replace path with where you downloaded it)
gcloud compute scp /path/to/downloaded-key.json resume-api-vm:~/resume-api/credentials/service-account-key.json --zone=us-central1-a
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `gcloud compute ssh --command=` | Runs a single command on the VM without opening an interactive session |
| `gcloud compute scp` | Copies a file between your local machine and a GCP VM (Secure Copy) |

</em></sub>

### Step 10.3 — Prompt for Gemini: ETL Pipeline
📍 **Firebase Studio → Gemini Chat**

**PROMPT TO COPY:**

```
Read docs/gemini-context.md first. Create the ETL pipeline for Phase 2.

This pipeline syncs live request data from SQLite (captured by middleware) to BigQuery
(for analytical queries). It runs every 6 hours using APScheduler.

Create etl/sqlite_to_bigquery.py:

FOUR FUNCTIONS:

1. get_unsynced_records():
   - Connect to SQLite at /app/data/queries.db
   - SELECT * FROM queries WHERE synced_to_bq = 0 ORDER BY query_id LIMIT 10000
   - Return as pandas DataFrame
   - Return empty DataFrame if no unsynced records

2. transform_for_bigquery(df):
   - Convert timestamp (Unix epoch) to pandas Timestamp
   - Add derived columns:
     - hour_of_day: extracted from timestamp (0-23)
     - day_of_week: extracted from timestamp (Monday, Tuesday, etc.)
     - date: date only (for potential partitioning)
   - Rename columns to BigQuery conventions:
     - timestamp -> request_timestamp
     - method -> http_method
     - path -> endpoint_path
     - status_code -> http_status_code
   - Pass through funnel columns as-is (no rename needed):
     - session_id, search_campaign, traffic_source, funnel_stage, device_type, geo_region
   - Return transformed DataFrame

3. load_to_bigquery(df):
   - Use google.cloud.bigquery.Client()
   - Load using client.load_table_from_dataframe()
   - Target table: {GCP_PROJECT_ID}.resume_analytics.pipeline_queries
   - Write disposition: WRITE_APPEND (never truncate — always add)
   - Read GCP_PROJECT_ID from environment variable
   - Return number of rows loaded

4. mark_as_synced(query_ids):
   - UPDATE queries SET synced_to_bq = 1 WHERE query_id IN (...)
   - Use parameterized query (NOT string formatting — SQL injection risk)

5. run_etl():
   - Orchestrates: extract -> transform -> load -> mark synced
   - Logs each step with timing
   - Returns dict: {records_fetched, records_loaded, success, timestamp}
   - Handles errors gracefully (logs and continues)

Also create etl/scheduler.py:

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

- Schedule run_etl() every 6 hours (hour='*/6', minute='0')
- Set max_instances=1 (prevent concurrent ETL runs)
- Set coalesce=True (skip missed runs, don't pile up)
- Run an initial sync on startup (catches up unsynced records from before scheduler started)
- Log scheduler start and each job execution

Also create:
- etl/Dockerfile (python:3.11-slim, pip install, CMD python scheduler.py)
- etl/requirements.txt:
  apscheduler>=3.10.0
  google-cloud-bigquery>=3.0.0
  pandas>=2.0.0
  pyarrow>=14.0.0
  db-sqlite3>=0.0.1

IMPORTANT:
- BATCH loading only — BigQuery streaming inserts are NOT available on free tier
- The synced_to_bq flag prevents duplicate loading
- LIMIT 10000 prevents memory issues on e2-micro (1 GB RAM)
- Parameterized SQL queries for security (no f-strings in SQL)
- Read GCP_PROJECT_ID and BIGQUERY_DATASET from environment variables
- GOOGLE_APPLICATION_CREDENTIALS environment variable points to service account key
```

**Verify:**

```bash
ls -la etl/sqlite_to_bigquery.py etl/scheduler.py etl/Dockerfile etl/requirements.txt

grep -n 'synced_to_bq' etl/sqlite_to_bigquery.py
# Expected: multiple references (the tracking flag)

grep -n 'load_table_from_dataframe' etl/sqlite_to_bigquery.py
# Expected: 1 line (batch loading)

grep -n 'CronTrigger' etl/scheduler.py
# Expected: 1 line (the schedule)

grep -n 'WRITE_APPEND' etl/sqlite_to_bigquery.py
# Expected: 1 line (never truncate)
```

### Step 10.4 — Update docker-compose.yml to Add ETL Service
📍 **Firebase Studio → Gemini Chat**

**PROMPT TO COPY:**

```
Read docs/gemini-context.md first. Update docker-compose.yml to add the etl service.

Add this service AFTER the existing api service:

  etl:
    build:
      context: ./etl
      dockerfile: Dockerfile
    depends_on:
      api:
        condition: service_healthy
    volumes:
      - ./data:/app/data
      - ./credentials:/app/credentials:ro
    environment:
      - GCP_PROJECT_ID=resume-api-portfolio
      - BIGQUERY_DATASET=resume_analytics
      - BIGQUERY_TABLE=pipeline_queries
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account-key.json
      - DATABASE_PATH=/app/data/queries.db
    restart: unless-stopped

IMPORTANT:
- volumes: ./data:/app/data — shares SQLite database with the API container
- volumes: ./credentials:/app/credentials:ro — read-only access to service account key
- GOOGLE_APPLICATION_CREDENTIALS — tells the BigQuery Python client where the key is
- Do NOT modify the existing api service
```

### Step 10.5 — Test ETL Locally (Before BigQuery)
📍 **Firebase Terminal**

Before connecting to BigQuery, test that the extract and transform steps work:

```bash
# Start API to serve requests
docker compose up api -d
sleep 5

# Generate some test traffic manually (or run Locust from Cloud Shell)
curl http://localhost:8080/resume
curl http://localhost:8080/resume/experience
curl http://localhost:8080/resume/skills?keyword=python
curl http://localhost:8080/analytics/top-domains
sleep 2  # Let middleware log the requests

# Test the ETL extract function
docker compose run --rm etl python -c "
from sqlite_to_bigquery import get_unsynced_records
df = get_unsynced_records()
print(f'Unsynced records: {len(df)}')
if len(df) > 0:
    print(df.head())
"

docker compose down
```

### Step 10.6 — Deploy and Test Full Pipeline
📍 **VM Terminal**

```bash
cd ~/resume-api
git pull origin main

# Verify credentials are in place
ls -la credentials/service-account-key.json
# Expected: file exists (from Step 10.2)

# Start everything
docker compose up --build -d

# Check both containers are running
docker compose ps
# Expected: api (healthy), etl (running)

# Watch ETL logs for the initial sync
docker compose logs -f etl
# Expected: "Starting initial sync..." then records loaded count
# Press Ctrl+C to stop watching

# After the initial sync completes, verify in BigQuery
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) as rows FROM resume_analytics.pipeline_queries'
# Expected: some number > 0 (however many requests were captured before first sync)
```

### Step 10.7 — Git Commit
📍 **Firebase Terminal**

```bash
git add etl/ docker-compose.yml
git commit -m "Add APScheduler ETL pipeline syncing SQLite to BigQuery"
git push
```

---

## PHASE 11: BIGQUERY ANALYTICS — PIPELINE INSIGHTS (1-2 hours)

> Now that live data is flowing into BigQuery, write queries that demonstrate the pipeline is working and generating meaningful analytics.
>
> 📍 **SQL queries in BigQuery Console. API endpoints in Firebase Studio.**

### Step 11.1 — Analytics Queries
📍 **BigQuery Console** — paste each query into the query editor

> **Note:** These queries target `pipeline_queries` (live data), not `recruiter_queries` (Phase 1 static data). If your pipeline just started, you may need to wait for at least one ETL cycle (6 hours) or trigger a manual sync from the VM:
> ```bash
> docker compose exec etl python -c "from sqlite_to_bigquery import run_etl; print(run_etl())"
> ```

---

**Query 1: Top Recruiter Domains (Last 24 Hours)**

```sql
-- Which domains are hitting the API most frequently?
-- This mirrors "top advertisers by impressions" in ad tech reporting
SELECT
  recruiter_domain,
  COUNT(*) AS total_hits,
  ROUND(AVG(response_time_ms), 2) AS avg_response_ms,
  COUNTIF(http_status_code = 200) AS successful_hits,
  ROUND(SAFE_DIVIDE(COUNTIF(http_status_code = 200), COUNT(*)) * 100, 1) AS success_rate_pct
FROM `resume-api-portfolio.resume_analytics.pipeline_queries`
WHERE request_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY recruiter_domain
ORDER BY total_hits DESC
LIMIT 10;
```

---

**Query 2: Hourly Traffic Distribution**

```sql
-- When do recruiters browse? Business hours vs off-hours
-- Mirrors "ad delivery by hour of day" reporting
SELECT
  hour_of_day,
  COUNT(*) AS requests,
  ROUND(AVG(response_time_ms), 2) AS avg_latency_ms
FROM `resume-api-portfolio.resume_analytics.pipeline_queries`
WHERE request_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY hour_of_day
ORDER BY hour_of_day;
```

---

**Query 3: Most Viewed Endpoints**

```sql
-- Which resume sections get the most attention?
-- Mirrors "campaign type performance" in ad tech
SELECT
  endpoint_path,
  COUNT(*) AS hits,
  ROUND(AVG(response_time_ms), 2) AS avg_latency_ms,
  APPROX_QUANTILES(response_time_ms, 100)[OFFSET(95)] AS p95_latency_ms
FROM `resume-api-portfolio.resume_analytics.pipeline_queries`
WHERE request_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY endpoint_path
ORDER BY hits DESC;
```

---

**Query 4: Pipeline Health Check**

```sql
-- Is the ETL pipeline working? How many records per sync batch?
-- Mirrors "data freshness monitoring" in production pipelines
SELECT
  DATE(request_timestamp) AS sync_date,
  COUNT(*) AS records,
  MIN(request_timestamp) AS earliest,
  MAX(request_timestamp) AS latest,
  COUNT(DISTINCT recruiter_domain) AS unique_domains
FROM `resume-api-portfolio.resume_analytics.pipeline_queries`
GROUP BY sync_date
ORDER BY sync_date DESC
LIMIT 7;
```

---

**Query 5: Skill Search Analysis**

```sql
-- What skills are recruiters searching for?
-- Mirrors "keyword performance" in Google Ads
SELECT
  REGEXP_EXTRACT(query_params, r'keyword=([^&]+)') AS skill_searched,
  COUNT(*) AS search_count,
  COUNT(DISTINCT recruiter_domain) AS unique_recruiters
FROM `resume-api-portfolio.resume_analytics.pipeline_queries`
WHERE endpoint_path = '/resume/skills'
  AND query_params LIKE '%keyword%'
  AND request_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY skill_searched
ORDER BY search_count DESC;
```

---

### Funnel Analytics Queries

> These queries analyze the recruiter interaction funnel — impression, engagement, and contact. The session-level tracking and campaign attribution create the same analytical patterns used in campaign performance reporting.

---

**Query 6: Funnel Conversion Rate by Campaign**

```sql
-- Which recruiting campaigns drive the most conversions?
-- Same pattern as campaign performance reports: impressions, engagement rate, conversion rate
WITH session_funnel AS (
  SELECT
    session_id,
    search_campaign,
    traffic_source,
    MAX(CASE WHEN funnel_stage = 'impression' THEN 1 ELSE 0 END) AS had_impression,
    MAX(CASE WHEN funnel_stage = 'engagement' THEN 1 ELSE 0 END) AS had_engagement,
    MAX(CASE WHEN funnel_stage = 'contact' THEN 1 ELSE 0 END)    AS had_contact
  FROM `resume-api-portfolio.resume_analytics.pipeline_queries`
  WHERE funnel_stage IS NOT NULL
    AND request_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  GROUP BY session_id, search_campaign, traffic_source
)

SELECT
  search_campaign,
  COUNT(*) AS total_sessions,
  COUNTIF(had_impression = 1) AS impressions,
  COUNTIF(had_engagement = 1) AS engagements,
  COUNTIF(had_contact = 1) AS contacts,
  ROUND(SAFE_DIVIDE(COUNTIF(had_engagement = 1), COUNTIF(had_impression = 1)) * 100, 2) AS engagement_rate_pct,
  ROUND(SAFE_DIVIDE(COUNTIF(had_contact = 1), COUNTIF(had_impression = 1)) * 100, 2) AS conversion_rate_pct
FROM session_funnel
GROUP BY search_campaign
ORDER BY total_sessions DESC;
```

> **What this shows:** Each campaign's full funnel — how many sessions started (impressions), how many dug deeper (engagements), and how many took action (contacts). The `SAFE_DIVIDE` handles the zero-division case gracefully. The CTE with `MAX(CASE WHEN...)` is a standard session-level attribution pattern.

---

**Query 7: Funnel Drop-Off Analysis**

```sql
-- Where do recruiters abandon the funnel?
-- Shows absolute counts and percentage that progress at each stage
WITH funnel_counts AS (
  SELECT
    COUNT(DISTINCT CASE WHEN funnel_stage = 'impression' THEN session_id END) AS step_1_impressions,
    COUNT(DISTINCT CASE WHEN funnel_stage = 'engagement' THEN session_id END) AS step_2_engagements,
    COUNT(DISTINCT CASE WHEN funnel_stage = 'contact'    THEN session_id END) AS step_3_contacts
  FROM `resume-api-portfolio.resume_analytics.pipeline_queries`
  WHERE funnel_stage IS NOT NULL
    AND request_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
)

SELECT
  step_1_impressions,
  step_2_engagements,
  step_3_contacts,
  ROUND(SAFE_DIVIDE(step_2_engagements, step_1_impressions) * 100, 1) AS impression_to_engagement_pct,
  ROUND(SAFE_DIVIDE(step_3_contacts, step_2_engagements) * 100, 1) AS engagement_to_contact_pct,
  ROUND(SAFE_DIVIDE(step_3_contacts, step_1_impressions) * 100, 1) AS overall_conversion_pct,
  step_1_impressions - step_2_engagements AS dropped_after_impression,
  step_2_engagements - step_3_contacts AS dropped_after_engagement
FROM funnel_counts;
```

> **What this shows:** The classic funnel visualization — how many recruiters are at each stage, what percentage progress to the next, and exactly how many drop off at each step. The `dropped_after_impression` count tells you how many recruiters saw the resume but didn't explore further.

---

**Query 8: Conversion Rate by Traffic Source**

```sql
-- Which traffic sources drive the best conversion rates?
-- Same pattern as channel attribution reports
WITH source_sessions AS (
  SELECT
    session_id,
    traffic_source,
    MAX(CASE WHEN funnel_stage = 'contact' THEN 1 ELSE 0 END) AS converted
  FROM `resume-api-portfolio.resume_analytics.pipeline_queries`
  WHERE funnel_stage IS NOT NULL
    AND request_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  GROUP BY session_id, traffic_source
)

SELECT
  traffic_source,
  COUNT(*) AS total_sessions,
  COUNTIF(converted = 1) AS conversions,
  ROUND(SAFE_DIVIDE(COUNTIF(converted = 1), COUNT(*)) * 100, 2) AS conversion_rate_pct,
  RANK() OVER (ORDER BY SAFE_DIVIDE(COUNTIF(converted = 1), COUNT(*)) DESC) AS source_rank
FROM source_sessions
GROUP BY traffic_source
ORDER BY conversion_rate_pct DESC;
```

> **What this shows:** Which channels (LinkedIn, Indeed, Google, referral, direct) produce the highest conversion rates. The `RANK() OVER` window function adds a ranking column — a pattern used in any "top N" performance report.

---

**Query 9: Campaign Performance by Device & Region**

```sql
-- How does performance vary by device type and geographic region?
-- Cross-segmentation report — standard in campaign analytics
SELECT
  search_campaign,
  device_type,
  geo_region,
  COUNT(DISTINCT session_id) AS sessions,
  COUNT(*) AS total_events,
  COUNTIF(funnel_stage = 'impression') AS impressions,
  COUNTIF(funnel_stage = 'engagement') AS engagements,
  COUNTIF(funnel_stage = 'contact') AS contacts,
  ROUND(AVG(response_time_ms), 2) AS avg_latency_ms,
  ROUND(SAFE_DIVIDE(COUNTIF(funnel_stage = 'contact'), COUNTIF(funnel_stage = 'impression')) * 100, 2) AS cvr_pct
FROM `resume-api-portfolio.resume_analytics.pipeline_queries`
WHERE funnel_stage IS NOT NULL
  AND request_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY search_campaign, device_type, geo_region
HAVING impressions > 0
ORDER BY sessions DESC;
```

> **What this shows:** Campaign performance sliced by device type and geography — the same dimensions used in ad platform reporting. The `HAVING impressions > 0` avoids division-by-zero noise in the conversion rate calculation.

---

**Query 10: Session Engagement Depth — Do Engaged Recruiters Convert?**

```sql
-- Do recruiters who view more sections convert at higher rates?
-- Engagement depth analysis — analogous to Quality Score / landing page experience
WITH session_depth AS (
  SELECT
    session_id,
    search_campaign,
    COUNT(*) AS total_hits,
    COUNT(DISTINCT endpoint_path) AS unique_sections_viewed,
    MAX(CASE WHEN funnel_stage = 'contact' THEN 1 ELSE 0 END) AS converted,
    ROUND(MAX(request_timestamp) - MIN(request_timestamp), 2) AS session_duration_sec
  FROM `resume-api-portfolio.resume_analytics.pipeline_queries`
  WHERE funnel_stage IS NOT NULL
    AND request_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  GROUP BY session_id, search_campaign
)

SELECT
  search_campaign,
  ROUND(AVG(unique_sections_viewed), 1) AS avg_sections_viewed,
  ROUND(AVG(session_duration_sec), 1) AS avg_session_duration_sec,
  ROUND(AVG(CASE WHEN converted = 1 THEN unique_sections_viewed END), 1) AS avg_sections_converters,
  ROUND(AVG(CASE WHEN converted = 0 THEN unique_sections_viewed END), 1) AS avg_sections_non_converters
FROM session_depth
GROUP BY search_campaign
ORDER BY avg_sections_viewed DESC;
```

> **What this shows:** Recruiters who convert view more resume sections than those who don't. This proves engagement depth predicts conversion — a core insight in campaign optimization (analogous to Quality Score in search ads). The split between `avg_sections_converters` vs `avg_sections_non_converters` makes this immediately visible.

---

Save these queries to your `sql/` directory:

📍 **Firebase Editor**

```bash
# Save each query to a file in sql/
# (Copy each query from above into the corresponding file)
touch sql/pipeline_top_domains.sql
touch sql/pipeline_hourly.sql
touch sql/pipeline_endpoints.sql
touch sql/pipeline_health.sql
touch sql/pipeline_skills.sql
# Funnel analysis queries
touch sql/funnel_conversion_by_campaign.sql
touch sql/funnel_dropoff_analysis.sql
touch sql/funnel_conversion_by_source.sql
touch sql/funnel_campaign_device_region.sql
touch sql/funnel_engagement_depth.sql
```

### Step 11.2 — (Optional) Add BigQuery API Endpoints
📍 **Firebase Studio → Gemini Chat**

If you want to expose pipeline analytics through the API:

**PROMPT TO COPY:**

```
Read docs/gemini-context.md first. Add 3 new API endpoints that query BigQuery pipeline data.

Create api/analytics_bigquery.py:
- Uses google.cloud.bigquery.Client()
- Reads GCP_PROJECT_ID from environment (with fallback to "resume-api-portfolio")

Add to api/main.py:
1. GET /analytics/bigquery/top-domains?limit=10&hours=24
   - Returns top recruiter domains from pipeline_queries
   - Default: last 24 hours, top 10

2. GET /analytics/bigquery/hourly?days=7
   - Returns request count by hour of day
   - Default: last 7 days

3. GET /analytics/bigquery/health
   - Returns pipeline health stats (records per day, last sync time)

IMPORTANT:
- These are OPTIONAL endpoints — they require BigQuery credentials at runtime
- Add error handling: if BigQuery is not configured, return a helpful error message
- Do NOT modify existing endpoints
- These endpoints read from pipeline_queries (live data), not recruiter_queries (static)
```

### Step 11.3 — Git Commit
📍 **Firebase Terminal**

```bash
git add sql/ api/analytics_bigquery.py api/main.py
git commit -m "Add BigQuery analytics queries for pipeline insights"
git push
```

---

## PHASE 12: SECURITY HARDENING (30 minutes)

> Your VM has a public IP. Basic security is non-negotiable.
>
> 📍 **All commands on VM Terminal.**

### Step 12.1 — Install fail2ban
📍 **VM Terminal**

```bash
sudo apt-get update
sudo apt-get install -y fail2ban

# Create SSH jail configuration
sudo tee /etc/fail2ban/jail.local << 'EOF'
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 5
bantime = 3600
findtime = 600
EOF

# Start and enable
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Verify
sudo fail2ban-client status sshd
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `fail2ban` | Monitors log files and bans IPs that show malicious signs (too many failed logins) |
| `sudo tee` | Writes to a file that requires root permissions |
| `maxretry = 5` | Ban after 5 failed SSH attempts |
| `bantime = 3600` | Ban for 1 hour (3600 seconds) |
| `findtime = 600` | Count failures within 10 minutes (600 seconds) |

</em></sub>

> **What is fail2ban?** It watches your SSH login logs. If someone tries to brute-force your password (5 failed attempts in 10 minutes), their IP gets banned for an hour. This is basic but essential for any public-facing VM.

### Step 12.2 — Verify Docker Security
📍 **VM Terminal**

```bash
# Verify API container runs as non-root
docker compose exec api whoami
# Expected: appuser (NOT root)

# Check container isolation
docker compose exec api cat /etc/passwd | grep appuser
# Expected: appuser entry exists
```

---

## PHASE 13: IMPLEMENTATION GUIDE REVIEW & VERIFICATION (1 hour)

> Before calling Phase 2 complete, verify the entire pipeline end-to-end.
>
> 📍 **VM Terminal for verification. BigQuery Console for data checks.**

### Step 13.1 — Full Pipeline Verification Checklist
📍 **VM Terminal**

Run through this checklist systematically:

```bash
# === INFRASTRUCTURE ===

# 1. Both containers running on VM
docker compose ps
# Expected: api (healthy), etl (running)

# 2. API responds externally
curl http://localhost:8080/
# Expected: {"status": "healthy", ...}

# 3. systemd auto-start enabled
sudo systemctl is-enabled resume-api
# Expected: enabled


# === DATA PIPELINE ===

# 4. Traffic simulator generating requests (run from Cloud Shell)
# In Cloud Shell: locust --headless --host http://VM_IP:8080 --users 3 --spawn-rate 1 --run-time 10m --autostart
# Then check here on VM:

# 5. Middleware capturing requests to SQLite
docker compose exec api python -c "
import sqlite3
conn = sqlite3.connect('/app/data/queries.db')
count = conn.execute('SELECT COUNT(*) FROM queries').fetchone()[0]
unsynced = conn.execute('SELECT COUNT(*) FROM queries WHERE synced_to_bq = 0').fetchone()[0]
synced = conn.execute('SELECT COUNT(*) FROM queries WHERE synced_to_bq = 1').fetchone()[0]
print(f'Total: {count} | Synced: {synced} | Pending: {unsynced}')
conn.close()
"
# Expected: Total > 0, Synced and Pending counts

# 6. ETL scheduler running
docker compose logs --tail=10 etl
# Expected: Scheduler started, next run time shown


# === BIGQUERY ===

# 7. Pipeline data in BigQuery (run from Firebase Terminal or VM)
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) as rows, MIN(request_timestamp) as first, MAX(request_timestamp) as last FROM resume_analytics.pipeline_queries'
# Expected: rows > 0, timestamps from recent activity

# === FUNNEL TRACKING ===

# 8. Funnel stages present in data
docker compose exec api python -c "
import sqlite3
conn = sqlite3.connect('/app/data/queries.db')
stages = conn.execute('SELECT funnel_stage, COUNT(*) FROM queries WHERE funnel_stage IS NOT NULL GROUP BY funnel_stage').fetchall()
campaigns = conn.execute('SELECT search_campaign, COUNT(*) FROM queries WHERE search_campaign IS NOT NULL GROUP BY search_campaign').fetchall()
print(f'Funnel stages: {dict(stages)}')
print(f'Campaigns: {dict(campaigns)}')
conn.close()
"
# Expected: stages shows impression > engagement > contact counts
# Expected: campaigns shows 3-5 different campaign names

# 9. Funnel data in BigQuery
bq query --use_legacy_sql=false \
  'SELECT funnel_stage, COUNT(*) as events, COUNT(DISTINCT session_id) as sessions FROM resume_analytics.pipeline_queries WHERE funnel_stage IS NOT NULL GROUP BY funnel_stage ORDER BY events DESC'
# Expected: impression events > engagement > contact
```

### Step 13.2 — Screenshot Checklist (Phase 2)

| # | Screenshot | Where | What It Demonstrates |
|---|-----------|-------|---------------------|
| 1 | `docker compose ps` showing 2 containers | 📍 VM Terminal | Multi-container orchestration |
| 2 | `curl` to VM external IP returning JSON | 📍 Your Browser or Terminal | Persistent hosting works |
| 3 | Locust output showing traffic generation | 📍 Cloud Shell | External traffic simulation over real internet |
| 4 | SQLite query count showing real external IPs | 📍 VM Terminal | Live data collection with real network traffic |
| 5 | BigQuery pipeline_queries row count | 📍 BigQuery Console | ETL pipeline working |
| 6 | BigQuery analytics query results | 📍 BigQuery Console | Pipeline insights |
| 7 | `systemctl status resume-api` | 📍 VM Terminal | Auto-start on boot |
| 8 | fail2ban status | 📍 VM Terminal | Security hardening |
| 9 | Funnel stage distribution in SQLite | 📍 VM Terminal | Funnel tracking working (impression > engagement > contact) |
| 10 | BigQuery funnel conversion query results | 📍 BigQuery Console | Full pipeline with funnel analytics |

### Step 13.3 — Final Git Commits
📍 **Firebase Terminal**

```bash
# Add any remaining files
git add sql/ docs/
git commit -m "Complete Phase 2: end-to-end data pipeline"
git push
```

---

## UPDATED ARCHITECTURE (After Phase 2)

```
Phase 1 (Static Demo):              Phase 2 (Live Pipeline):

[Cloud Run]                          [Cloud Shell]
  └── FastAPI + SQLite                 └── Locust (traffic over real internet)
                                              │
[BigQuery]                                    ▼
  └── 500K static rows               [e2-micro VM]
                                       ├── API Container (FastAPI + Middleware)
[Manual bq load]                       ├── ETL Container (APScheduler)
                                       └── SQLite (live request logs)

                                     [Automated ETL]
                                       └── Every 6 hours → BigQuery

                                     [BigQuery]
                                       ├── recruiter_queries (500K static — Phase 1)
                                       └── pipeline_queries (growing — Phase 2)
```

---

## KEY DECISIONS LOG (Phase 2)

| Decision | Choice | Why | Alternative Rejected |
|----------|--------|-----|---------------------|
| Hosting | e2-micro VM | Always Free, persistent, runs 24/7 | Cloud Run (ephemeral, can't run scheduled ETL) |
| Container orchestration | Docker Compose | Simple, single-host, 2 containers (API + ETL) | Docker run (no dependency management) |
| Traffic simulation | Locust from Cloud Shell | Real internet traffic, weighted tasks, realistic behavior | Locust on same VM (localhost traffic, no real network path) |
| ETL scheduling | APScheduler | Unlimited free jobs, Python-native | Cloud Scheduler (only 3 free jobs) |
| BigQuery loading | Batch (load_table_from_dataframe) | Free tier compatible | Streaming inserts (NOT free — $0.005/100K rows) |
| Request logging | BackgroundTask on response | Non-blocking, <50ms impact | Synchronous writes (blocks response) |
| Data tracking | synced_to_bq flag | Prevents duplicate loading | Timestamp-based (fragile, gaps possible) |
| Security | fail2ban + non-root Docker | Minimal attack surface | iptables (more complex, harder to maintain) |

---

## TROUBLESHOOTING (Phase 2)

| Problem | Cause | Fix |
|---------|-------|-----|
| Container won't start | Build error or missing dependency | `docker compose logs api` — read the error |
| API returns "Connection refused" | Container not running or wrong port | `docker compose ps` — check status |
| Locust can't reach VM | Firewall or wrong IP | Verify: `curl http://VM_IP:8080/` from Cloud Shell. Check firewall rule `allow-api-8080` |
| Cloud Shell disconnects | 20 min inactivity timeout | Re-run `locust` command. Data already captured stays in SQLite |
| ETL reports "Permission denied" | Service account key missing or wrong path | `ls credentials/service-account-key.json` — verify file exists |
| BigQuery returns 0 rows | ETL hasn't run yet or credentials wrong | `docker compose logs etl` — check for errors |
| SQLite "database locked" | Concurrent writes from middleware + ETL | ETL uses LIMIT 10000 and separate connection — shouldn't happen. Check for stale processes |
| VM out of memory | Too many containers or image too large | `free -h` on VM. Use multi-stage builds to reduce image size |
| Can't SSH into VM | fail2ban banned your IP | Wait 1 hour, or use GCP Console browser SSH (different IP) |
| Firewall blocking traffic | Port 8080 rule missing | GCP Console → VPC Network → Firewall → verify `allow-api-8080` exists |
| `docker compose` not found | Docker Compose plugin not installed | `sudo apt-get install docker-compose-plugin` |

---

## CLEANUP: PHASE 2 RESOURCES

When you're done and want to stop all charges:

📍 **VM Terminal**

```bash
# Stop all containers
docker compose down

# Disable auto-start
sudo systemctl disable resume-api
```

📍 **GCP Console**

```bash
# Delete the VM (stops all compute charges)
gcloud compute instances delete resume-api-vm --zone=us-central1-a

# Delete the firewall rule
gcloud compute firewall-rules delete allow-api-8080

# Remove pipeline data from BigQuery (keep Phase 1 data if you want)
bq rm -t resume_analytics.pipeline_queries

# Delete service account
gcloud iam service-accounts delete etl-pipeline@resume-api-portfolio.iam.gserviceaccount.com
```

> **What costs $0 while running:** e2-micro VM (Always Free), 30 GB disk (Always Free), BigQuery storage under 10 GB (Always Free), BigQuery queries under 1 TB/month (Always Free). The only risk is if you accidentally create a second VM or upgrade machine type.

---

## WHAT YOU'VE BUILT

| Component | Technology | What It Does |
|-----------|-----------|-------------|
| Persistent API | FastAPI on Docker Compose | Serves resume data 24/7 |
| Traffic Simulation | Locust from Cloud Shell | Generates realistic recruiter traffic over the real internet |
| Data Collection | Custom middleware + SQLite | Captures every request non-blocking |
| Automated ETL | APScheduler → BigQuery | Syncs operational data to analytical warehouse every 6 hours |
| Analytics | BigQuery SQL | Pipeline health, traffic patterns, recruiter behavior |
| Infrastructure | e2-micro VM + systemd | Auto-starts on boot, survives reboots |
| Security | fail2ban + non-root containers | Basic but essential protection |

**The pipeline pattern:**
```
[Cloud Shell: Locust] ──internet──> [VM: FastAPI + Middleware] → [SQLite] → [APScheduler ETL] → [BigQuery] → [Analytics Queries]
```

This is the same operational → analytical pipeline pattern used in ad tech: event capture → operational store → batch ETL → analytical warehouse → reporting. The traffic travels over the real internet — not localhost. The only difference from production is scale, but the architecture is identical.
