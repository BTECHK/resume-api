# Resume API — Phase 3 Implementation Guide
## Production-Grade IaC, CI/CD, AI, and Security

**Goal:** Transform the Phase 2 data pipeline into a production-grade, enterprise-ready system by adding Infrastructure as Code (Terraform), CI/CD automation (GitHub Actions), AI-powered resume Q&A (Gemini + RAG), and comprehensive security tooling — demonstrating the full lifecycle from build to deploy to secure to enhance.
**Total Cost:** $0.00 (Google Cloud Always Free tier + GitHub free tier + open-source tools)
**Primary Tool:** Firebase Studio with direct code implementation
**Prerequisite:** Phase 2 complete (Docker Compose on e2-micro, Locust traffic, ETL pipeline, BigQuery analytics)

---

## WHAT YOU'RE BUILDING

Phase 2 made the pipeline live. Phase 3 makes it enterprise-ready:

| Component | Phase 2 (Live Pipeline) | Phase 3 (Production-Grade) |
|-----------|------------------------|---------------------------|
| Infrastructure | Manual VM creation via GCP Console | Terraform modules — reproducible, version-controlled |
| Deployment | `git pull` + `docker compose up` on VM | GitHub Actions CI/CD — automated on every push |
| Security | fail2ban + non-root containers | Trivy, Bandit, pip-audit scanning in CI + OWASP hardening |
| AI | None | Gemini-powered RAG for resume Q&A + skill matching |
| Code Quality | Manual testing | Ruff linting + pytest + pre-commit hooks |
| Secrets | `.env` files on VM | GCP Secret Manager (6 free secrets) |
| Documentation | Implementation guide | Implementation guide + SECURITY.md + Terraform README |

**New skills demonstrated:**

| Skill Area | How It's Demonstrated |
|-----------|----------------------|
| Infrastructure as Code | Terraform modules managing VPC, firewall, IAM, Cloud Run, VM, BigQuery |
| CI/CD Automation | GitHub Actions: lint → scan → test → build → deploy pipeline |
| AI / LLM Integration | RAG pipeline: HuggingFace embeddings → Chroma vector DB → Gemini generation |
| Security Engineering | SAST (Bandit), SCA (pip-audit), container scanning (Trivy), IaC scanning (Trivy), OWASP alignment |
| Prompt Engineering | Structured prompts for resume Q&A with grounding and citation |
| Vector Databases | Chroma with persistent storage and similarity search |
| DevSecOps | Security gates integrated into CI/CD — builds fail on critical findings |

---

## ARCHITECTURE OVERVIEW

```
┌──────────────────────────────────────────────────────────────────────────┐
│  GITHUB (Code + CI/CD)                                                    │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  GitHub Actions Pipeline                                             │ │
│  │                                                                       │ │
│  │  Push → [Ruff Lint] → [Bandit SAST] → [pip-audit] → [pytest]       │ │
│  │             │              │               │             │           │ │
│  │             ▼              ▼               ▼             ▼           │ │
│  │         [Trivy IaC] → [Docker Build] → [Trivy Image] → [Deploy]    │ │
│  │                                                             │       │ │
│  └─────────────────────────────────────────────────────────────┼───────┘ │
└────────────────────────────────────────────────────────────────┼─────────┘
                                                                 │
                                                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  GCP (Managed by Terraform)                                               │
│                                                                           │
│  ┌──────────────────┐    ┌──────────────────────────────────────────┐    │
│  │  Cloud Run        │    │  e2-micro VM                              │    │
│  │  (Public API)     │    │  Docker Compose:                          │    │
│  │  + AI Endpoints   │    │    ├─ API container (FastAPI + middleware) │    │
│  │  + RAG Pipeline   │    │    ├─ ETL container (APScheduler)         │    │
│  │                   │    │    └─ Traffic simulator (Locust)           │    │
│  └────────┬──────────┘    └───────────────┬──────────────────────────┘    │
│           │                               │                               │
│           │    ┌──────────────────────┐    │                               │
│           └───►│  BigQuery            │◄───┘                               │
│                │  (Analytical Data)   │                                    │
│                │  200K+ rows          │                                    │
│                └──────────────────────┘                                    │
│                                                                           │
│  ┌──────────────────────┐    ┌──────────────────────┐                    │
│  │  Chroma Vector DB     │    │  GCS Bucket           │                    │
│  │  (Resume Embeddings)  │    │  (Terraform State)    │                    │
│  │  ./chroma_db/         │    │  5 GB free             │                    │
│  └──────────────────────┘    └──────────────────────┘                    │
│                                                                           │
│  ┌──────────────────────┐    ┌──────────────────────┐                    │
│  │  VPC + Firewall       │    │  IAM Service Accounts │                    │
│  │  (Terraform-managed)  │    │  (Least privilege)    │                    │
│  └──────────────────────┘    └──────────────────────┘                    │
└──────────────────────────────────────────────────────────────────────────┘
```

**The end result:** Every piece of infrastructure is defined in Terraform. Every code change triggers automated linting, security scanning, testing, and deployment. The API answers AI-powered questions about the resume using a RAG pipeline. Security scanning runs on every commit — builds fail if critical vulnerabilities are found.

---

## WHERE AM I? — LOCATION GUIDE (Phase 3 Additions)

Phase 3 adds GitHub Actions and Terraform. Watch for these tags:

| Tag | Where | What It Looks Like |
|-----|-------|-------------------|
| 📍 **GCP Console** | Google Cloud Console in your browser | `console.cloud.google.com` — enabling APIs, viewing resources |
| 📍 **Firebase Terminal** | Terminal panel inside Firebase Studio | Black terminal at the bottom of the IDE — bash commands |
| 📍 **Firebase Editor** | Code editor inside Firebase Studio | File tabs at the top — creating and editing files |
| 📍 **VM Terminal** | SSH session into your e2-micro VM | `gcloud compute ssh` or browser-based SSH |
| 📍 **BigQuery Console** | BigQuery UI in your browser | Running SQL queries and viewing tables |
| 📍 **GitHub** | GitHub web interface | Repository settings, Actions tab, secrets configuration |
| 📍 **Google AI Studio** | Google's AI API key management | `aistudio.google.com` — creating Gemini API keys |

> **New in Phase 3:** Most development still happens in Firebase Studio. GitHub Actions runs automatically when you push. Terraform commands run in Firebase Terminal. AI Studio is visited once to get an API key.

---

## PRE-FLIGHT CHECKLIST

📍 **Firebase Terminal**

Before starting Phase 3, verify your Phase 2 infrastructure is intact:

```bash
# 1. Check your VM is running
gcloud compute instances describe resume-api-vm --zone=us-central1-a --format="value(status)"
# Expected: RUNNING

# 2. Get VM external IP
gcloud compute instances describe resume-api-vm --zone=us-central1-a \
  --format="value(networkInterfaces[0].accessConfigs[0].natIP)"
# Expected: An IP address like 35.xxx.xxx.xxx

# 3. Test API on VM
VM_IP=$(gcloud compute instances describe resume-api-vm --zone=us-central1-a \
  --format="value(networkInterfaces[0].accessConfigs[0].natIP)")
curl -s "http://$VM_IP:8080/" | python3 -m json.tool
# Expected: {"status": "healthy", ...}

# 4. Verify BigQuery has pipeline data
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) as rows FROM resume_analytics.pipeline_queries'
# Expected: Row count > 0 (data from Locust traffic + ETL)

# 5. Verify your GCP project
gcloud config get-value project
# Expected: resume-api-portfolio

# 6. Verify git is configured
git remote -v
# Expected: origin pointing to your GitHub repo
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `gcloud compute instances describe` | Shows details about a Compute Engine VM instance |
| `--format="value(...)"` | Extracts a specific field from the output |
| `bq query --use_legacy_sql=false` | Runs a Standard SQL query in BigQuery |
| `git remote -v` | Shows configured remote repositories with URLs |

</em></sub>

> **If the VM is stopped:** Start it with `gcloud compute instances start resume-api-vm --zone=us-central1-a`. Wait 1-2 minutes for Docker to auto-start via systemd, then re-test.

> **If BigQuery has no pipeline data:** Run the traffic simulator first (Phase 2, Step 10). Phase 3 builds on top of a working pipeline.

---

## PHASE 14: TERRAFORM FOUNDATION — STATE, PROVIDERS, BASE MODULES (1-2 hours)

> Terraform is Infrastructure as Code — you describe what infrastructure you want in `.tf` files, and Terraform creates/updates/destroys it to match. This phase creates the Terraform project structure, configures remote state in a GCS bucket, and builds the foundational modules (networking and IAM) that all other resources depend on.
>
> 📍 **All of Phase 14 happens in Firebase Studio (editor + terminal) and GCP Console (bucket creation).**

### Step 14.1 — Install Terraform in Firebase Studio
📍 **Firebase Terminal**

Check if Terraform is already available:

```bash
terraform --version
```

If not found, install it:

```bash
# Download Terraform binary
curl -fsSL https://releases.hashicorp.com/terraform/1.7.5/terraform_1.7.5_linux_amd64.zip -o /tmp/terraform.zip

# Unzip to a location on PATH
sudo unzip -o /tmp/terraform.zip -d /usr/local/bin/

# Verify
terraform --version
# Expected: Terraform v1.7.5 (or later)

# Clean up
rm /tmp/terraform.zip
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `curl` | `-fsSL` | Downloads a file. `-f` = fail on error, `-s` = silent, `-S` = show errors, `-L` = follow redirects |
| `unzip` | `-o` | Extracts a zip file. `-o` = overwrite existing without prompting |
| `-d /usr/local/bin/` | | Extract to this directory (which is on your PATH) |

</em></sub>

> **What is Terraform?** It reads `.tf` files that describe your desired infrastructure state (VMs, networks, databases, IAM roles), compares against reality, and makes the necessary API calls to match. Instead of clicking through GCP Console, you define resources in code — version-controlled, reviewable, reproducible.

### Step 14.2 — Create the GCS Bucket for Terraform State
📍 **Firebase Terminal**

Terraform needs somewhere to store its "state file" — a JSON file that maps your `.tf` resources to real GCP resources. Storing it in a GCS bucket enables team collaboration and prevents state loss.

```bash
# Create a GCS bucket for Terraform state
# Replace PROJECT_ID with your actual project ID
PROJECT_ID=$(gcloud config get-value project)
gsutil mb -p $PROJECT_ID -l us-central1 gs://${PROJECT_ID}-terraform-state

# Enable versioning (safety net — recover from state corruption)
gsutil versioning set on gs://${PROJECT_ID}-terraform-state

# Verify
gsutil ls
# Expected: gs://resume-api-portfolio-terraform-state/ (or your project ID)
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `gsutil mb` | `-p PROJECT -l REGION` | Make Bucket — creates a Cloud Storage bucket. `-p` = project, `-l` = location |
| `gsutil versioning set on` | | Enables object versioning — keeps old versions when overwritten |
| `gsutil ls` | | Lists all buckets in the project |

</em></sub>

> **Why remote state?** If the state file lives only on your laptop (or Firebase Studio workspace), it can be lost when the workspace resets. GCS provides durability, versioning, and automatic state locking (prevents two people from modifying infrastructure simultaneously).

> **Cost check:** GCS free tier provides 5 GB-months of regional storage in US regions. A Terraform state file is typically < 100 KB. You'll never exceed the free tier.

### Step 14.3 — Create Terraform Directory Structure
📍 **Firebase Terminal**

```bash
# Create the full directory structure
mkdir -p terraform/environments/dev
mkdir -p terraform/environments/prod
mkdir -p terraform/modules/networking
mkdir -p terraform/modules/iam

# Verify
find terraform -type d | sort
```

Expected output:
```
terraform
terraform/environments
terraform/environments/dev
terraform/environments/prod
terraform/modules
terraform/modules/iam
terraform/modules/networking
```

> **Why environments?** The `dev/` and `prod/` directories use the same modules but with different settings (e.g., different project IDs, different naming prefixes). This mirrors how real infrastructure teams manage multiple environments without duplicating code.

### Step 14.4 — Create the Dev Environment Backend Configuration
📍 **Firebase Editor** — create `terraform/environments/dev/backend.tf`

```hcl
# backend.tf — Remote state configuration
# Stores Terraform state in a GCS bucket for durability and locking.
#
# PREREQUISITE: The bucket must be created manually BEFORE running terraform init.
# See Step 14.2 in the implementation guide.

terraform {
  backend "gcs" {
    bucket = "resume-api-portfolio-terraform-state"  # Replace with your bucket name
    prefix = "terraform/state/dev"
  }
}
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Terraform concepts:

| Concept | What It Means |
|---------|--------------|
| `backend "gcs"` | Store state in Google Cloud Storage instead of a local file |
| `bucket` | The GCS bucket name (must already exist) |
| `prefix` | A path prefix inside the bucket — separates dev/prod state files |

</em></sub>

> **Important:** Replace `resume-api-portfolio` in the bucket name with YOUR actual project ID. The bucket name must match exactly what you created in Step 14.2.

### Step 14.5 — Create the Dev Environment Variables
📍 **Firebase Editor** — create `terraform/environments/dev/variables.tf`

```hcl
# variables.tf — Input variables for the dev environment
# These are the "knobs" that control infrastructure configuration.

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The GCP zone for zonal resources (VMs)"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment name (dev or prod)"
  type        = string
  default     = "dev"
}
```

### Step 14.6 — Create the Dev Environment Terraform Variables File
📍 **Firebase Editor** — create `terraform/environments/dev/terraform.tfvars`

```hcl
# terraform.tfvars — Actual values for this environment
# This file is checked into git as a template.
# For sensitive values, create terraform.tfvars.local (gitignored).

project_id  = "resume-api-portfolio"  # Replace with YOUR project ID
region      = "us-central1"
zone        = "us-central1-a"
environment = "dev"
```

### Step 14.7 — Create the Dev Environment Main Configuration
📍 **Firebase Editor** — create `terraform/environments/dev/main.tf`

```hcl
# main.tf — Dev environment entry point
# Defines providers, required versions, and module references.

terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

# Configure the Google Cloud provider
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# --- Module References ---
# Each module manages a logical group of resources.

module "networking" {
  source = "../../modules/networking"

  project_id   = var.project_id
  region       = var.region
  environment  = var.environment
}

module "iam" {
  source = "../../modules/iam"

  project_id   = var.project_id
  environment  = var.environment
}
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Terraform concepts:

| Concept | What It Means |
|---------|--------------|
| `required_version` | Minimum Terraform CLI version |
| `required_providers` | Which provider plugins to download (Google Cloud in this case) |
| `~> 5.0` | Version constraint: any 5.x version (not 6.0+) |
| `provider "google"` | Configures authentication and default project/region |
| `module` | References a reusable group of resources defined elsewhere |
| `source` | Path to the module directory (relative to this file) |

</em></sub>

> **What does `~> 5.0` mean?** This is a pessimistic constraint — it allows `5.0`, `5.1`, `5.99` but NOT `6.0`. Major version bumps often contain breaking changes. Pinning to `~> 5.0` protects you from unexpected breakage while still getting patches.

### Step 14.8 — Create the Prod Environment (Mirror of Dev)
📍 **Firebase Terminal**

The prod environment uses the same structure but with different values:

```bash
# Copy dev files as starting point
cp terraform/environments/dev/variables.tf terraform/environments/prod/variables.tf
cp terraform/environments/dev/main.tf terraform/environments/prod/main.tf
```

📍 **Firebase Editor** — create `terraform/environments/prod/backend.tf`

```hcl
terraform {
  backend "gcs" {
    bucket = "resume-api-portfolio-terraform-state"  # Same bucket, different prefix
    prefix = "terraform/state/prod"
  }
}
```

📍 **Firebase Editor** — create `terraform/environments/prod/terraform.tfvars`

```hcl
project_id  = "resume-api-portfolio"  # Same project for free tier (one project only)
region      = "us-central1"
zone        = "us-central1-a"
environment = "prod"
```

> **Why separate environments if it's the same project?** In a real company, dev and prod would be different GCP projects with different budgets, permissions, and risks. Here, they share a project (free tier constraint), but the Terraform structure demonstrates the production pattern. Resource names include the environment prefix (e.g., `dev-resume-api-network` vs `prod-resume-api-network`) to avoid collisions.

### Step 14.9 — Create the Networking Module
📍 **Firebase Editor** — create `terraform/modules/networking/variables.tf`

```hcl
# variables.tf — Networking module inputs

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for the subnet"
  type        = string
}

variable "environment" {
  description = "Environment name (used in resource naming)"
  type        = string
}

variable "network_name" {
  description = "Base name for the VPC network"
  type        = string
  default     = "resume-api-network"
}
```

📍 **Firebase Editor** — create `terraform/modules/networking/main.tf`

```hcl
# main.tf — VPC, subnet, and firewall rules
#
# Creates a custom VPC (not the default network) with explicit firewall rules.
# This demonstrates network segmentation — a security best practice.

# VPC Network — the private network for all resources
resource "google_compute_network" "vpc" {
  name                    = "${var.environment}-${var.network_name}"
  auto_create_subnetworks = false  # Manual subnet control (not auto-mode)
  project                 = var.project_id
}

# Subnet — the IP address range within the VPC
resource "google_compute_subnetwork" "subnet" {
  name          = "${var.environment}-${var.network_name}-subnet"
  ip_cidr_range = "10.0.0.0/24"  # 256 IP addresses (more than enough)
  region        = var.region
  network       = google_compute_network.vpc.id
  project       = var.project_id
}

# Firewall: Allow SSH (TCP 22) — for emergency VM access
resource "google_compute_firewall" "allow_ssh" {
  name    = "${var.environment}-allow-ssh"
  network = google_compute_network.vpc.name
  project = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ssh-access"]

  description = "Allow SSH access to tagged instances"
}

# Firewall: Allow HTTP/HTTPS (TCP 80, 443, 8080) — for API access
resource "google_compute_firewall" "allow_http" {
  name    = "${var.environment}-allow-http"
  network = google_compute_network.vpc.name
  project = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8080"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-server"]

  description = "Allow HTTP, HTTPS, and API traffic to tagged instances"
}

# Firewall: Allow internal traffic — resources within VPC can talk freely
resource "google_compute_firewall" "allow_internal" {
  name    = "${var.environment}-allow-internal"
  network = google_compute_network.vpc.name
  project = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = ["10.0.0.0/24"]  # Only from within the subnet

  description = "Allow all internal traffic within the VPC"
}
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Terraform concepts:

| Concept | What It Means |
|---------|--------------|
| `resource "google_compute_network"` | Creates a VPC network in GCP |
| `auto_create_subnetworks = false` | Don't auto-create subnets — we define our own for explicit control |
| `ip_cidr_range = "10.0.0.0/24"` | Private IP range with 256 addresses |
| `source_ranges = ["0.0.0.0/0"]` | Allow traffic from anywhere (public internet) |
| `target_tags` | Firewall only applies to instances with matching tags |
| `${var.environment}` | String interpolation — inserts the environment name into the resource name |

</em></sub>

> **Why `auto_create_subnetworks = false`?** Auto mode creates a subnet in every GCP region (~40 subnets). Custom mode lets you create only what you need — one subnet in us-central1. This is the production pattern: explicit control over network topology.

> **Why target tags?** Instead of applying firewall rules to all instances, tags let you be selective. Only VMs tagged `ssh-access` get SSH access. Only VMs tagged `http-server` get HTTP access. This is the principle of least privilege applied to networking.

📍 **Firebase Editor** — create `terraform/modules/networking/outputs.tf`

```hcl
# outputs.tf — Values other modules need from the networking module

output "network_id" {
  description = "The ID of the VPC network"
  value       = google_compute_network.vpc.id
}

output "network_name" {
  description = "The name of the VPC network"
  value       = google_compute_network.vpc.name
}

output "subnetwork_id" {
  description = "The ID of the subnet"
  value       = google_compute_subnetwork.subnet.id
}

output "subnetwork_name" {
  description = "The name of the subnet"
  value       = google_compute_subnetwork.subnet.name
}
```

> **What are outputs?** When one module creates a VPC, another module (like the compute module that creates VMs) needs to reference it. Outputs expose specific values so modules can be wired together — like function return values.

### Step 14.10 — Create the IAM Module
📍 **Firebase Editor** — create `terraform/modules/iam/variables.tf`

```hcl
# variables.tf — IAM module inputs

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "environment" {
  description = "Environment name (used in resource naming)"
  type        = string
}

variable "service_account_name" {
  description = "Base name for the service account"
  type        = string
  default     = "resume-api-sa"
}
```

📍 **Firebase Editor** — create `terraform/modules/iam/main.tf`

```hcl
# main.tf — Service account and IAM role bindings
#
# Creates a dedicated service account with MINIMAL permissions.
# This demonstrates least-privilege access — a core security principle.

# Service account — the identity your API and ETL use
resource "google_service_account" "api_sa" {
  account_id   = "${var.environment}-${var.service_account_name}"
  display_name = "Resume API Service Account (${var.environment})"
  project      = var.project_id
}

# Role: BigQuery Data Editor — allows ETL to write data
resource "google_project_iam_member" "bigquery_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

# Role: Storage Object Viewer — allows reading config files from GCS
resource "google_project_iam_member" "storage_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

# Role: Cloud Logging Writer — allows writing structured logs
resource "google_project_iam_member" "logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ IAM concepts:

| Concept | What It Means |
|---------|--------------|
| Service Account | A non-human identity for applications (like an app-specific username) |
| `roles/bigquery.dataEditor` | Can read and write BigQuery data, but NOT create/delete tables |
| `roles/storage.objectViewer` | Can read GCS objects, but NOT write or delete them |
| `roles/logging.logWriter` | Can write log entries, but NOT read or delete them |
| `google_project_iam_member` | Grants ONE role to ONE member (additive — doesn't replace existing bindings) |

</em></sub>

> **Why not just use the Owner role?** The Owner role can do anything — create VMs, delete databases, change billing. If the API's service account key leaks, an attacker with Owner access can destroy everything. Least-privilege means giving each identity ONLY the permissions it needs. The ETL needs to write to BigQuery — it doesn't need to create VMs or manage IAM.

📍 **Firebase Editor** — create `terraform/modules/iam/outputs.tf`

```hcl
# outputs.tf — Values other modules need from the IAM module

output "service_account_email" {
  description = "The email of the service account"
  value       = google_service_account.api_sa.email
}

output "service_account_id" {
  description = "The unique ID of the service account"
  value       = google_service_account.api_sa.unique_id
}
```

### Step 14.11 — Create Terraform README
📍 **Firebase Editor** — create `terraform/README.md`

```markdown
# Resume API — Infrastructure as Code

Terraform modules managing all GCP infrastructure for the Resume API portfolio project.

## Prerequisites

1. **Terraform >= 1.0** installed (`terraform --version`)
2. **gcloud CLI** authenticated (`gcloud auth application-default login`)
3. **GCS bucket** created for state storage (see Phase 3 implementation guide, Step 14.2)

## Directory Structure

```
terraform/
├── environments/          # Environment-specific configurations
│   ├── dev/              # Development environment
│   │   ├── backend.tf    # GCS state backend
│   │   ├── main.tf       # Provider + module references
│   │   ├── variables.tf  # Input variable definitions
│   │   └── terraform.tfvars  # Variable values
│   └── prod/             # Production environment (same structure)
└── modules/              # Reusable infrastructure components
    ├── networking/       # VPC, subnet, firewall rules
    └── iam/             # Service accounts, role bindings
```

## Quick Start

```bash
cd terraform/environments/dev

# Initialize (downloads providers, configures state backend)
terraform init

# Preview changes (shows what will be created/modified/destroyed)
terraform plan

# Apply changes (creates real infrastructure)
terraform apply
```

## Modules

| Module | What It Creates |
|--------|----------------|
| networking | VPC, subnet (10.0.0.0/24), firewall rules (SSH, HTTP, internal) |
| iam | Service account with BigQuery, Storage, and Logging permissions |

## Security Notes

- State file in GCS with versioning enabled (recovery from corruption)
- Service account follows least-privilege (no Owner/Editor roles)
- Firewall rules use target tags (not applied to all instances)
- Never commit `.terraform/` directory or state files to git
```

### Step 14.12 — Update .gitignore for Terraform
📍 **Firebase Editor** — add to your `.gitignore`

```
# Terraform
.terraform/
*.tfstate
*.tfstate.backup
*.tfvars.local
.terraform.lock.hcl
```

### Step 14.13 — Initialize and Validate Terraform
📍 **Firebase Terminal**

```bash
# Authenticate Terraform to GCP
gcloud auth application-default login

# Navigate to dev environment
cd terraform/environments/dev

# Initialize — downloads providers, connects to GCS backend
terraform init
# Expected: "Terraform has been successfully initialized!"

# Validate — checks syntax and configuration
terraform validate
# Expected: "Success! The configuration is valid."

# Preview — shows what would be created (without creating anything)
terraform plan
# Expected: Plan showing resources to create (VPC, subnet, firewalls, service account, IAM bindings)
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Terraform commands:

| Command | What It Does |
|---------|-------------|
| `terraform init` | Downloads providers, initializes backend, prepares working directory |
| `terraform validate` | Checks configuration syntax without accessing remote state or APIs |
| `terraform plan` | Shows what changes would be made — dry run (read-only) |
| `terraform apply` | Actually creates/modifies/destroys resources to match configuration |
| `gcloud auth application-default login` | Creates credentials Terraform uses to authenticate with GCP APIs |

</em></sub>

> **Do NOT run `terraform apply` yet.** We're verifying the configuration is valid. Applying happens in Phase 17 after CI/CD and security scanning are set up — so every infrastructure change goes through the pipeline.

```bash
# Return to project root
cd ../../..
```

### Step 14.14 — Git Commit
📍 **Firebase Terminal**

```bash
git add terraform/ .gitignore
git commit -m "Add Terraform foundation: GCS state, networking module, IAM module"
git push
```

### Step 14.15 — Verify What You Built
📍 **Firebase Terminal**

Run these checks to confirm everything is in place:

```bash
# Directory structure
find terraform -type f -name "*.tf" | sort
# Expected: 10 .tf files across environments and modules

# Backend configured
grep -n 'backend "gcs"' terraform/environments/dev/backend.tf
# Expected: Line with backend "gcs"

# VPC resource defined
grep -n 'google_compute_network' terraform/modules/networking/main.tf
# Expected: Line with resource definition

# Service account defined
grep -n 'google_service_account' terraform/modules/iam/main.tf
# Expected: Line with resource definition

# Module references
grep -n 'module "networking"' terraform/environments/dev/main.tf
grep -n 'module "iam"' terraform/environments/dev/main.tf
# Expected: Both module blocks present

# Terraform validates
cd terraform/environments/dev && terraform validate && cd ../../..
# Expected: "Success! The configuration is valid."
```

| Check | Expected | If It Fails |
|-------|----------|-------------|
| `find terraform -type f -name "*.tf"` | 10 files | Missing files — re-check directory structure |
| `terraform init` | "Successfully initialized" | Wrong bucket name — check backend.tf matches Step 14.2 |
| `terraform validate` | "Configuration is valid" | Syntax error — check `.tf` files for typos |
| `terraform plan` | Shows resources to create | Auth issue — re-run `gcloud auth application-default login` |

---

## PHASE 15: CI/CD PIPELINE — GITHUB ACTIONS (1-2 hours)

> Every push to your repo will now trigger an automated pipeline: lint your code, scan for security issues, run tests, build containers, and deploy — all for free on GitHub Actions (unlimited minutes for public repos).
>
> 📍 **Code in Firebase Studio. Configuration in GitHub web UI (for secrets).**

### Step 15.1 — Create GitHub Actions Directory
📍 **Firebase Terminal**

```bash
mkdir -p .github/workflows
```

### Step 15.2 — Create the CI Workflow
📍 **Firebase Editor** — create `.github/workflows/ci.yml`

This workflow runs on every push and pull request. It lints, scans, and tests your code.

```yaml
# ci.yml — Continuous Integration pipeline
# Runs on every push and pull request to main.
# Fails fast: if linting fails, don't waste time on tests.

name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# Cancel in-progress runs when a new commit is pushed
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint & Format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Ruff
        run: pip install ruff

      - name: Run Ruff linter
        run: ruff check . --output-format=github

      - name: Run Ruff formatter check
        run: ruff format --check .

  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install security tools
        run: pip install bandit pip-audit

      - name: Run Bandit (Python SAST)
        run: bandit -r api/ -f json -o bandit-results.json --exit-zero
        # --exit-zero: don't fail the step (we check severity below)

      - name: Check Bandit results
        run: |
          # Fail only on HIGH or CRITICAL severity
          HIGH_COUNT=$(python3 -c "
          import json
          with open('bandit-results.json') as f:
              data = json.load(f)
          high = [r for r in data.get('results', []) if r['issue_severity'] in ('HIGH', 'CRITICAL')]
          print(len(high))
          ")
          echo "High/Critical findings: $HIGH_COUNT"
          if [ "$HIGH_COUNT" -gt 0 ]; then
            echo "::error::Bandit found $HIGH_COUNT high/critical security issues"
            cat bandit-results.json | python3 -m json.tool
            exit 1
          fi

      - name: Run pip-audit (Dependency Vulnerabilities)
        run: pip-audit --requirement requirements.txt --desc

      - name: Upload security results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: security-results
          path: bandit-results.json

  test:
    name: Test
    runs-on: ubuntu-latest
    needs: [lint]  # Only run tests if linting passes
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov httpx

      - name: Run tests
        run: |
          pytest tests/ -v --tb=short --cov=api --cov-report=term-missing || true
          # || true: don't fail if no tests exist yet (Phase 3 adds the structure)

  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: [test, security-scan]  # Only build if tests AND security pass
    steps:
      - uses: actions/checkout@v4

      - name: Build API image
        run: docker build -t resume-api:${{ github.sha }} .

      - name: Verify image
        run: |
          docker images resume-api:${{ github.sha }}
          # Image should exist and be < 500MB
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ GitHub Actions concepts:

| Concept | What It Means |
|---------|--------------|
| `on: push/pull_request` | Triggers the workflow when code is pushed or a PR is opened |
| `jobs` | Independent stages that can run in parallel |
| `needs: [lint]` | This job waits for the `lint` job to succeed before starting |
| `runs-on: ubuntu-latest` | Uses a free Ubuntu VM provided by GitHub |
| `actions/checkout@v4` | Clones your repository into the runner VM |
| `actions/setup-python@v5` | Installs a specific Python version |
| `${{ github.sha }}` | The commit hash — used to tag Docker images uniquely |
| `concurrency` | Cancels old runs when new commits are pushed (saves minutes) |

</em></sub>

> **Why does `test` need `lint` but not `security-scan`?** The dependency graph is: lint → test → build, and security-scan → build. Linting catches syntax errors that would cause test failures. Security scanning is independent — it checks for vulnerabilities, not correctness. Both must pass before building.

> **Why `|| true` on pytest?** You might not have tests yet. Without `|| true`, an empty test directory would fail the pipeline. As you add tests, remove `|| true` to enforce passing tests.

### Step 15.3 — Create Ruff Configuration
📍 **Firebase Editor** — create `ruff.toml`

```toml
# ruff.toml — Python linter and formatter configuration
# Ruff is a fast Python linter (replaces flake8, isort, pyupgrade)

# Target Python 3.11
target-version = "py311"

# Line length (matches Black default)
line-length = 100

[lint]
# Enable common rule sets
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort (import sorting)
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "S",    # flake8-bandit (security)
]

# Ignore rules that conflict with our style
ignore = [
    "S101",  # assert used (fine in tests)
    "S104",  # binding to 0.0.0.0 (required for containers)
]

[lint.per-file-ignores]
# Tests can use assert
"tests/**" = ["S101"]
```

> **What is Ruff?** It's a Python linter and formatter written in Rust — 10-100x faster than flake8, isort, or black. It catches style issues, import ordering, potential bugs, and basic security problems. The CI pipeline fails if Ruff finds issues, enforcing consistent code quality.

### Step 15.4 — Create Pre-commit Configuration
📍 **Firebase Editor** — create `.pre-commit-config.yaml`

```yaml
# .pre-commit-config.yaml — Hooks that run before every git commit
# Install with: pip install pre-commit && pre-commit install

repos:
  # Ruff linter + formatter
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]       # Auto-fix what it can
      - id: ruff-format     # Auto-format code

  # Detect accidentally committed secrets
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

📍 **Firebase Terminal** — set up pre-commit:

```bash
# Install pre-commit
pip install pre-commit

# Install the hooks (creates git hooks in .git/hooks/)
pre-commit install

# Create secrets baseline (marks known non-secrets)
detect-secrets scan > .secrets.baseline

# Run against all files to verify
pre-commit run --all-files
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Pre-commit concepts:

| Concept | What It Means |
|---------|--------------|
| Pre-commit hooks | Scripts that run automatically before `git commit` |
| `--fix` | Ruff auto-fixes simple issues (import ordering, unused imports) |
| `detect-secrets` | Scans for accidentally committed API keys, passwords, tokens |
| `.secrets.baseline` | File listing known false positives (so they don't trigger alerts every time) |

</em></sub>

> **Why pre-commit AND CI?** Pre-commit catches issues locally before you commit — fast feedback loop. CI catches issues even if someone forgets to install pre-commit hooks (or uses a different machine). Belt and suspenders.

### Step 15.5 — Git Commit and Test the Pipeline
📍 **Firebase Terminal**

```bash
git add .github/workflows/ci.yml ruff.toml .pre-commit-config.yaml .secrets.baseline
git commit -m "Add CI/CD pipeline: GitHub Actions with lint, security scan, test, build"
git push
```

📍 **GitHub** — verify the pipeline runs:

1. Go to your repository on GitHub
2. Click the **"Actions"** tab
3. You should see the "CI Pipeline" workflow running
4. Click into it to see each job's progress and output

| Job | Expected Result |
|-----|----------------|
| Lint & Format | Pass (or show fixable warnings) |
| Security Scan | Pass (no HIGH/CRITICAL findings) |
| Test | Pass (even with no tests — `|| true`) |
| Build Docker Image | Pass (image builds successfully) |

> **If linting fails:** Read the error output. Common issues are import ordering (Ruff auto-fixes this locally with `ruff check --fix .`) or line length. Fix locally, commit, push again.

> **If security scan fails:** Bandit found a HIGH/CRITICAL issue. Read the output to see which file and line. Common false positives include binding to `0.0.0.0` (needed for containers) — add `# nosec` comment to suppress.

---

## PHASE 16: SECURITY SCANNING INTEGRATION (1 hour)

> Phase 15 added basic Bandit and pip-audit. Phase 16 adds Trivy (the industry-standard multi-scanner) for container images and Terraform IaC, plus Hadolint for Dockerfile best practices.
>
> 📍 **All code in Firebase Studio. Runs automatically via GitHub Actions.**

### Step 16.1 — Create the Security Workflow
📍 **Firebase Editor** — create `.github/workflows/security.yml`

```yaml
# security.yml — Dedicated security scanning workflow
# Runs Trivy for container and IaC scanning, Hadolint for Dockerfiles.
# Separate from CI so security results are clearly visible.

name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  # Also run weekly to catch newly disclosed vulnerabilities
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC

jobs:
  trivy-iac:
    name: Trivy IaC Scan (Terraform)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy IaC scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'config'
          scan-ref: 'terraform/'
          format: 'table'
          exit-code: '1'           # Fail on findings
          severity: 'HIGH,CRITICAL'
          # Only fail on HIGH/CRITICAL — MEDIUM and LOW are informational

  trivy-container:
    name: Trivy Container Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t resume-api:scan .

      - name: Run Trivy container scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'resume-api:scan'
          format: 'table'
          exit-code: '1'
          severity: 'HIGH,CRITICAL'

      - name: Run Trivy SBOM generation
        uses: aquasecurity/trivy-action@master
        if: always()
        with:
          image-ref: 'resume-api:scan'
          format: 'cyclonedx'
          output: 'sbom.json'

      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: sbom
          path: sbom.json

  hadolint:
    name: Hadolint (Dockerfile Linting)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Lint root Dockerfile
        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile

      - name: Lint API Dockerfile
        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: api/Dockerfile
        if: hashFiles('api/Dockerfile') != ''
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Security scanning concepts:

| Tool | Type | What It Scans |
|------|------|---------------|
| **Trivy** (config mode) | IaC Scanner | Terraform files for misconfigurations (open ports, missing encryption, overly permissive IAM) |
| **Trivy** (image mode) | Container Scanner | Docker images for OS and library vulnerabilities (CVEs) |
| **Trivy** (SBOM) | Software Bill of Materials | Lists every package in the container — supply chain transparency |
| **Hadolint** | Dockerfile Linter | Checks Dockerfiles against best practices (use specific tags, minimize layers, etc.) |

| Concept | What It Means |
|---------|--------------|
| SAST | Static Application Security Testing — scans source code (Bandit) |
| SCA | Software Composition Analysis — scans dependencies (pip-audit) |
| Container Scanning | Checks container images for known vulnerabilities (Trivy) |
| IaC Scanning | Checks infrastructure code for misconfigurations (Trivy/Checkov) |
| SBOM | Software Bill of Materials — inventory of all components |
| `severity: 'HIGH,CRITICAL'` | Only fail on serious findings — LOW/MEDIUM are informational |

</em></sub>

> **What is Trivy?** It's an all-in-one security scanner by Aqua Security. It started as a container scanner but now handles IaC (Terraform, CloudFormation), code, secrets, and SBOM generation. It absorbed tfsec (the former Terraform-specific scanner). One tool, multiple uses.

> **Why a separate workflow?** Security scans should be visible as their own check — not buried inside CI. When reviewing a pull request, you want to see "Security Scan: passed" as a distinct status. The weekly schedule (`cron`) catches newly disclosed CVEs even when no code changes.

### Step 16.2 — Git Commit and Verify
📍 **Firebase Terminal**

```bash
git add .github/workflows/security.yml
git commit -m "Add security scanning: Trivy (container + IaC), Hadolint (Dockerfile)"
git push
```

📍 **GitHub → Actions tab** — you should now see TWO workflows:
1. **CI Pipeline** (lint, security-scan, test, build)
2. **Security Scan** (trivy-iac, trivy-container, hadolint)

Both should be running. Wait for them to complete and verify all checks pass.

| Check | Expected | If It Fails |
|-------|----------|-------------|
| Trivy IaC | Pass | Check Terraform files for misconfigurations (usually overly permissive firewall rules) |
| Trivy Container | Pass | Update base image or fix vulnerable packages |
| Hadolint | Pass | Follow Hadolint suggestions (use specific image tags, combine RUN commands) |

---

## PHASE 17: TERRAFORM DEPLOYMENT — APPLY INFRASTRUCTURE (1-2 hours)

> Phase 14 created the Terraform configuration. Phase 17 runs `terraform apply` to create the actual GCP resources. We do this AFTER CI/CD and security scanning are in place — so even infrastructure changes go through the pipeline.
>
> 📍 **Firebase Terminal for Terraform commands. GCP Console to verify resources.**

### Step 17.1 — Enable Required GCP APIs
📍 **Firebase Terminal**

Terraform needs these APIs enabled before it can create resources:

```bash
# Enable Compute Engine API (for VPC, firewall, VMs)
gcloud services enable compute.googleapis.com

# Enable IAM API (for service accounts)
gcloud services enable iam.googleapis.com

# Enable Cloud Resource Manager API (for project-level operations)
gcloud services enable cloudresourcemanager.googleapis.com

# Verify all are enabled
gcloud services list --enabled --filter="NAME:(compute|iam|cloudresourcemanager)" --format="table(NAME)"
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | What It Does |
|---------|-------------|
| `gcloud services enable` | Turns on a GCP API for your project (some APIs are off by default) |
| `gcloud services list --enabled` | Shows which APIs are currently enabled |
| `--filter` | Filters the list to show only matching entries |

</em></sub>

### Step 17.2 — Apply Terraform (Dev Environment)
📍 **Firebase Terminal**

```bash
cd terraform/environments/dev

# Re-initialize (in case providers were updated)
terraform init

# Plan — review what will be created
terraform plan
```

Review the plan output carefully. You should see resources being created:

| Resource | Count |
|----------|-------|
| `google_compute_network.vpc` | 1 |
| `google_compute_subnetwork.subnet` | 1 |
| `google_compute_firewall.allow_ssh` | 1 |
| `google_compute_firewall.allow_http` | 1 |
| `google_compute_firewall.allow_internal` | 1 |
| `google_service_account.api_sa` | 1 |
| `google_project_iam_member` (3 roles) | 3 |
| **Total** | **8 resources** |

If the plan looks correct:

```bash
# Apply — creates the resources
terraform apply
# Type 'yes' when prompted
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Terraform apply:

| Output | What It Means |
|--------|--------------|
| `Plan: 8 to add, 0 to change, 0 to destroy` | Terraform will create 8 new resources |
| `Apply complete! Resources: 8 added` | All resources created successfully |
| `Do you want to perform these actions?` | Safety prompt — type `yes` to confirm |

</em></sub>

### Step 17.3 — Verify in GCP Console
📍 **GCP Console**

1. **VPC Network:** Go to `https://console.cloud.google.com/networking/networks` — you should see `dev-resume-api-network`
2. **Firewall Rules:** Go to `https://console.cloud.google.com/networking/firewalls` — you should see `dev-allow-ssh`, `dev-allow-http`, `dev-allow-internal`
3. **Service Account:** Go to `https://console.cloud.google.com/iam-admin/serviceaccounts` — you should see `dev-resume-api-sa@PROJECT.iam.gserviceaccount.com`

### Step 17.4 — Verify via CLI
📍 **Firebase Terminal**

```bash
# Check VPC was created
gcloud compute networks list --filter="name=dev-resume-api-network"
# Expected: 1 network listed

# Check firewall rules
gcloud compute firewall-rules list --filter="network=dev-resume-api-network" --format="table(name, direction, allowed)"
# Expected: 3 rules (allow-ssh, allow-http, allow-internal)

# Check service account
gcloud iam service-accounts list --filter="email~dev-resume-api-sa"
# Expected: 1 service account

# Return to project root
cd ../../..
```

### Step 17.5 — Git Commit
📍 **Firebase Terminal**

```bash
# The .terraform.lock.hcl file records provider versions — commit it for reproducibility
git add terraform/environments/dev/.terraform.lock.hcl
git commit -m "Apply Terraform dev environment: VPC, firewall, IAM created"
git push
```

> **Note:** The actual `.tfstate` file is stored in GCS (not locally), so there's nothing to commit for state. The `.terraform.lock.hcl` file records exact provider versions — committing it ensures everyone uses the same versions.

---

## PHASE 18: AI FEATURE — GEMINI-POWERED RAG (2-3 hours)

> This is the crown jewel of Phase 3. You'll build a Retrieval Augmented Generation (RAG) system that answers questions about the resume using AI. Instead of making the LLM hallucinate, RAG retrieves relevant resume chunks first, then generates an answer grounded in actual content.
>
> 📍 **Development in Firebase Studio. API key from Google AI Studio.**

### Step 18.1 — Get a Gemini API Key
📍 **Google AI Studio**

1. Go to: `https://aistudio.google.com/app/apikey`
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Select your GCP project (`resume-api-portfolio`)
5. Copy the API key — you'll need it in Step 18.7

> **Free tier limits:** Gemini 2.5 Flash allows 10 requests per minute and 250 requests per day for free. This is plenty for a portfolio demo. The API key is used server-side only — never exposed in frontend code.

> **Security note:** Never commit API keys to git. Add `GOOGLE_API_KEY` to your `.env` file (which is gitignored).

### Step 18.2 — Install AI Dependencies
📍 **Firebase Terminal**

```bash
uv add langchain langchain-google-genai langchain-community chromadb sentence-transformers
```

Verify:

```bash
uv pip list | grep -i "langchain\|chroma\|sentence"
# Expected: langchain, langchain-google-genai, langchain-community, chromadb, sentence-transformers
```

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Package descriptions:

| Package | What It Does |
|---------|-------------|
| `langchain` | LLM orchestration framework — chains together retrieval + generation |
| `langchain-google-genai` | LangChain integration for Google's Gemini models |
| `langchain-community` | Community-maintained integrations (Chroma, HuggingFace, etc.) |
| `chromadb` | Open-source vector database — stores and searches embeddings |
| `sentence-transformers` | HuggingFace library for generating text embeddings locally |

</em></sub>

> **What is RAG?** Retrieval Augmented Generation. Instead of asking an LLM a question and hoping it knows the answer, you first *retrieve* relevant documents from a database, then *augment* the prompt with those documents, then *generate* an answer. The LLM only uses provided context — reducing hallucination.

### Step 18.3 — Create the AI Package Structure
📍 **Firebase Terminal**

```bash
mkdir -p api/ai
touch api/ai/__init__.py
mkdir -p api/routers
touch api/routers/__init__.py
```

### Step 18.4 — Create the Embeddings Module
📍 **Firebase Editor** — create `api/ai/embeddings.py`

```python
"""Local embeddings using HuggingFace sentence-transformers.

Uses all-MiniLM-L6-v2: a small (80MB), fast model that produces 384-dimensional
embeddings. Runs entirely locally — no API calls, no cost, no rate limits.

The embeddings convert text into vectors (arrays of numbers) that capture meaning.
Similar texts produce similar vectors, enabling semantic search.
"""
from langchain_community.embeddings import HuggingFaceEmbeddings

_embeddings = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Get or create the embeddings model (singleton pattern).

    The first call downloads the model (~80MB) and loads it into memory.
    Subsequent calls return the cached instance.
    """
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},  # No GPU needed
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings
```

> **Why local embeddings instead of Gemini embeddings?** Local embeddings have zero API cost and zero rate limits. The all-MiniLM-L6-v2 model is fast, small, and produces quality embeddings for semantic search. Gemini embeddings would add another API dependency with rate limits.

### Step 18.5 — Create the Vector Store Module
📍 **Firebase Editor** — create `api/ai/vectorstore.py`

```python
"""Chroma vector store for resume chunks.

Chroma is an open-source vector database that stores embeddings and supports
similarity search. The resume is pre-chunked into sections (skills, experience, etc.)
and each chunk is stored as a vector. When a user asks a question, we find the
most similar chunks and pass them to Gemini as context.
"""
import json
from pathlib import Path

from langchain.schema import Document
from langchain_community.vectorstores import Chroma

from .embeddings import get_embeddings

CHROMA_PERSIST_DIR = "./chroma_db"
RESUME_CHUNKS_PATH = Path(__file__).parent.parent.parent / "data" / "resume_chunks.json"

_vectorstore = None


def load_resume_chunks() -> list[Document]:
    """Load resume chunks from JSON file into LangChain Documents."""
    with open(RESUME_CHUNKS_PATH) as f:
        chunks = json.load(f)
    return [
        Document(page_content=chunk["content"], metadata=chunk.get("metadata", {}))
        for chunk in chunks
    ]


def get_vectorstore() -> Chroma:
    """Get or create the vector store (singleton pattern).

    First call: loads resume chunks, generates embeddings, stores in Chroma.
    Subsequent calls: returns the cached Chroma instance.
    Chroma persists to disk — survives container restarts.
    """
    global _vectorstore
    if _vectorstore is None:
        embeddings = get_embeddings()
        if Path(CHROMA_PERSIST_DIR).exists():
            _vectorstore = Chroma(
                persist_directory=CHROMA_PERSIST_DIR,
                embedding_function=embeddings,
            )
        else:
            documents = load_resume_chunks()
            _vectorstore = Chroma.from_documents(
                documents,
                embeddings,
                persist_directory=CHROMA_PERSIST_DIR,
            )
    return _vectorstore


def similarity_search(query: str, k: int = 3) -> list[Document]:
    """Search for the k most similar resume chunks to the query.

    Args:
        query: The user's question (e.g., "What cloud skills does this person have?")
        k: Number of results to return (default 3)

    Returns:
        List of Documents with content and metadata (section, type)
    """
    vectorstore = get_vectorstore()
    return vectorstore.similarity_search(query, k=k)
```

### Step 18.6 — Create the Resume Chunks Data File
📍 **Firebase Editor** — create `data/resume_chunks.json`

This file breaks the resume into searchable chunks. Each chunk is 100-300 words and covers a specific topic. Customize these to match YOUR actual resume:

```json
[
  {
    "content": "Technical Skills: Python, SQL, Bash, FastAPI, Docker, Terraform, Git. Cloud platforms: AWS (EC2, S3, IAM, VPC, Lambda, Fargate), GCP (BigQuery, Cloud Run, Compute Engine, Cloud Storage). Infrastructure as Code: Terraform, CloudFormation. Data tools: Pandas, BigQuery, ETL pipelines. CI/CD: GitHub Actions, Docker Compose. Security: IAM least-privilege, container hardening, vulnerability scanning with Trivy and Bandit.",
    "metadata": {"section": "skills", "type": "technical"}
  },
  {
    "content": "Solutions and Analytics Skills: Business analysis and requirements gathering, dashboard development using CloudWatch and MicroStrategy, data-driven recommendations for executive stakeholders, cross-functional team collaboration, client needs assessment and solution design.",
    "metadata": {"section": "skills", "type": "analytics"}
  },
  {
    "content": "Client and Partner Management: Technical relationship management with enterprise clients, team leadership overseeing 100+ engineers, executive communication and presentation, stakeholder alignment across technical and business teams, vendor evaluation and procurement strategy.",
    "metadata": {"section": "skills", "type": "management"}
  },
  {
    "content": "Cloud Infrastructure Experience: AWS Solutions Architect Associate certified. Designed and deployed VPC architectures with public/private subnets. Managed EC2 instances, S3 storage, IAM policies, Lambda functions, and Fargate containers. Infrastructure as Code using Terraform and CloudFormation. Docker containerization for application deployment.",
    "metadata": {"section": "experience", "type": "cloud"}
  },
  {
    "content": "Consulting Firm A (May 2018 - July 2025). Go-to-Market AI Lab: Built RAG prototype for client-facing AI solution, drove cost optimization strategy, led cross-functional team. Federal Justice Program: Delivered business intelligence platform serving 50,000+ users, achieved FedRAMP compliance. Federal Defense Program: Led strategic procurement planning for national geospatial systems.",
    "metadata": {"section": "experience", "type": "work_history"}
  },
  {
    "content": "Resume API Portfolio Project: Built a REST API with 9 endpoints using FastAPI, deployed on Google Cloud Run. Implemented dual-database architecture: SQLite for operational queries, BigQuery for analytical data at scale (500K-5M rows). Created 3-tier SQL optimization progression demonstrating query performance from naive GROUP BY to CTE/window functions to partitioned/clustered tables. Built automated data pipeline with Locust traffic simulation, APScheduler ETL, and BigQuery analytics.",
    "metadata": {"section": "projects", "type": "portfolio"}
  },
  {
    "content": "Education: Oklahoma State University, Bachelor of Science in Geology. Certifications: AWS Solutions Architect Associate, AWS Machine Learning Engineer Associate, Oracle Cloud Architect, Oracle AI Foundations, CompTIA Security+, Oracle Financials Cloud ERP.",
    "metadata": {"section": "education", "type": "credentials"}
  },
  {
    "content": "Data Engineering Experience: Built end-to-end data pipelines from operational databases to analytical warehouses. Experience with ETL processes using Python (APScheduler), batch processing patterns, and BigQuery as an analytical layer. Demonstrated tool selection judgment through benchmarks: Python dict operations for <100K rows, SQLite for 100K-1M rows, BigQuery for 1M+ rows. Data modeling patterns inspired by digital advertising (recruiter_domain as advertiser, endpoint_hit as campaign, skill_searched as keyword).",
    "metadata": {"section": "experience", "type": "data_engineering"}
  }
]
```

> **Customize this file!** Replace the content with YOUR actual resume data. The chunks above match the resume structure from Phases 1-2. Each chunk should be self-contained — it should make sense on its own without needing other chunks for context.

> **Why chunks instead of the whole resume?** LLMs have limited context windows, and stuffing everything in wastes tokens. By chunking, we only send the 3 most relevant sections — producing better answers with fewer tokens.

### Step 18.7 — Create the RAG Pipeline Module
📍 **Firebase Editor** — create `api/ai/rag.py`

```python
"""RAG pipeline: Retrieve relevant resume chunks, then generate with Gemini.

Flow:
1. User asks a question (e.g., "What cloud experience does this person have?")
2. Question is converted to an embedding vector
3. Chroma finds the 3 most similar resume chunks
4. Chunks + question are sent to Gemini as a structured prompt
5. Gemini generates an answer grounded in the retrieved context

The key insight: Gemini never sees the whole resume — only the relevant chunks.
This reduces hallucination and focuses the response.
"""
import json
import os

from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from .vectorstore import similarity_search

# Gemini 2.5 Flash: 10 RPM, 250 requests/day on free tier
GEMINI_MODEL = "gemini-2.5-flash"

ANSWER_PROMPT = PromptTemplate.from_template("""
You are an AI assistant helping answer questions about a candidate's resume.
Use ONLY the following context to answer the question.
If the answer cannot be found in the context, say "I don't have that information in the resume."
Do not make up information that isn't in the context.

Context:
{context}

Question: {question}

Answer:
""")

SKILLS_MATCH_PROMPT = PromptTemplate.from_template("""
You are an AI assistant analyzing the match between a candidate's resume and a job description.

Resume Skills and Experience:
{context}

Job Description:
{job_description}

Analyze the match and provide your response as JSON with these keys:
- match_percentage: integer 0-100
- matching_skills: list of strings (skills the candidate has that match the job)
- missing_skills: list of strings (skills the job requires that the candidate lacks)
- recommendations: list of strings (suggestions for the candidate)

Respond with ONLY valid JSON, no other text.
""")


def get_llm() -> ChatGoogleGenerativeAI:
    """Get a Gemini LLM instance.

    Requires GOOGLE_API_KEY environment variable.
    Get your key at: https://aistudio.google.com/app/apikey
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY environment variable not set. "
            "Get a free key at https://aistudio.google.com/app/apikey"
        )
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=api_key,
        temperature=0.3,  # Lower = more factual, less creative
    )


def retrieve_and_generate(question: str) -> dict:
    """Full RAG pipeline: retrieve relevant chunks, then generate answer.

    Args:
        question: User's question about the resume

    Returns:
        dict with question, answer, and sources (which resume sections were used)
    """
    # Step 1: Retrieve — find the 3 most relevant resume chunks
    docs = similarity_search(question, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])

    # Step 2: Generate — ask Gemini to answer using only the retrieved context
    llm = get_llm()
    prompt = ANSWER_PROMPT.format(context=context, question=question)
    response = llm.invoke(prompt)

    return {
        "question": question,
        "answer": response.content,
        "sources": [doc.metadata.get("section", "unknown") for doc in docs],
    }


def analyze_skills_match(job_description: str) -> dict:
    """Analyze how well the resume matches a job description.

    Args:
        job_description: The job posting text to match against

    Returns:
        dict with job_description_preview and analysis (match %, skills, recommendations)
    """
    # Retrieve skills-related chunks (cast a wider net with k=5)
    docs = similarity_search("skills experience qualifications certifications", k=5)
    context = "\n\n".join([doc.page_content for doc in docs])

    # Generate analysis
    llm = get_llm()
    prompt = SKILLS_MATCH_PROMPT.format(context=context, job_description=job_description)
    response = llm.invoke(prompt)

    # Parse JSON response (with fallback for malformed output)
    try:
        analysis = json.loads(response.content)
    except json.JSONDecodeError:
        analysis = {"raw_response": response.content}

    return {
        "job_description_preview": (
            job_description[:200] + "..." if len(job_description) > 200 else job_description
        ),
        "analysis": analysis,
    }
```

### Step 18.8 — Create the AI Router
📍 **Firebase Editor** — create `api/routers/ai.py`

```python
"""AI endpoints for resume Q&A and skill matching.

These endpoints demonstrate:
- RAG (Retrieval Augmented Generation) architecture
- LLM integration with structured prompts
- Vector similarity search for context retrieval
- Practical AI application (not just "hello world" with an LLM)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/ai", tags=["AI"])


class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Question about the resume",
        examples=["What programming languages does this person know?"],
    )


class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]


class SkillsMatchRequest(BaseModel):
    job_description: str = Field(
        ...,
        min_length=50,
        max_length=5000,
        description="Job description to match against",
        examples=[
            "Looking for a Python developer with experience in FastAPI, Docker, "
            "and cloud platforms like GCP or AWS. Must have SQL skills and "
            "experience with data pipelines."
        ],
    )


class SkillsMatchResponse(BaseModel):
    job_description_preview: str
    analysis: dict


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about the resume using AI.

    Uses RAG (Retrieval Augmented Generation):
    1. Searches resume chunks for relevant context via vector similarity
    2. Sends context + question to Gemini AI
    3. Returns an answer grounded in actual resume content

    **Free tier:** 10 requests/minute, 250 requests/day (Gemini 2.5 Flash)
    """
    try:
        from api.ai.rag import retrieve_and_generate

        result = retrieve_and_generate(request.question)
        return QuestionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")


@router.post("/skills/match", response_model=SkillsMatchResponse)
async def match_skills(request: SkillsMatchRequest):
    """Analyze how well the resume matches a job description.

    Returns:
    - Match percentage (0-100%)
    - List of matching skills
    - List of missing skills
    - Recommendations for improvement
    """
    try:
        from api.ai.rag import analyze_skills_match

        result = analyze_skills_match(request.job_description)
        return SkillsMatchResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")
```

### Step 18.9 — Integrate AI Router into Main App
📍 **Firebase Editor** — edit `api/main.py`

Add these lines to integrate the AI endpoints:

Near the top, add the import:
```python
from api.routers.ai import router as ai_router
```

After the app creation line (`app = FastAPI(...)`), add:
```python
app.include_router(ai_router)
```

Add a startup event to pre-load the vector store (makes the first AI request faster):
```python
@app.on_event("startup")
async def startup_event():
    """Initialize vector store on startup (pre-load embeddings)."""
    try:
        from api.ai.vectorstore import get_vectorstore
        get_vectorstore()
        print("Vector store initialized")
    except Exception as e:
        print(f"Vector store initialization skipped: {e}")
```

> **Why lazy imports in the router?** The `from api.ai.rag import ...` is inside the endpoint functions, not at the top of the file. This means the heavy AI libraries (LangChain, sentence-transformers, Chroma) only load when someone actually calls the AI endpoints — not on every API startup. This keeps the API fast for non-AI requests.

### Step 18.10 — Set Up API Key
📍 **Firebase Terminal**

```bash
# Set the API key for local testing
export GOOGLE_API_KEY="your-api-key-from-step-18.1"

# Add to .env for persistence
echo "GOOGLE_API_KEY=your-api-key-here" >> .env
```

> **Security reminder:** Your `.env` file is gitignored. Never commit API keys. For CI/CD deployment, the key will be stored in GitHub Secrets (added in a later step).

### Step 18.11 — Test the AI Endpoints
📍 **Firebase Terminal**

Start the API:

```bash
uv run -- python -m uvicorn api.main:app --reload --port 8000 --host 0.0.0.0
```

In a second terminal (or use the Firebase "Web" tab), test:

```bash
# Test the Q&A endpoint
curl -X POST http://localhost:8000/ai/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What programming languages does this person know?"}'
# Expected: JSON with question, answer (mentioning Python, SQL, etc.), and sources

# Test the skill matching endpoint
curl -X POST http://localhost:8000/ai/skills/match \
  -H "Content-Type: application/json" \
  -d '{"job_description": "Looking for a Python developer with experience in FastAPI, Docker, and cloud platforms like GCP or AWS. Must have SQL skills and experience building data pipelines. Terraform experience preferred."}'
# Expected: JSON with match_percentage, matching_skills, missing_skills, recommendations
```

**Verify the AI responses are grounded:**
- The answer should reference actual resume content (not generic advice)
- The sources array should show which resume sections were used
- The skill match should correctly identify skills you have vs. don't have

| Check | Expected | If It Fails |
|-------|----------|-------------|
| Q&A endpoint returns JSON | `{"question": ..., "answer": ..., "sources": [...]}` | Check GOOGLE_API_KEY is set |
| Answer mentions actual skills | References Python, SQL, AWS, etc. from your chunks | Resume chunks may be too vague — add more detail |
| Sources array has entries | `["skills", "experience"]` etc. | Chroma DB may not be initialized — delete `chroma_db/` and restart |
| Skill match returns JSON analysis | `{"match_percentage": 85, ...}` | Gemini may return non-JSON — check the raw_response fallback |

### Step 18.12 — Update Requirements and Git Commit
📍 **Firebase Terminal**

```bash
# Regenerate requirements.txt
uv pip compile pyproject.toml -o requirements.txt

# Add all AI files
git add api/ai/ api/routers/ data/resume_chunks.json requirements.txt pyproject.toml
git commit -m "Add AI-powered resume Q&A: Gemini RAG with Chroma vector DB"
git push
```

---

## PHASE 19: SECURITY REVIEW & API HARDENING (1-2 hours)

> Phase 16 added automated scanning. Phase 19 is the manual security review — implementing OWASP-aligned best practices and documenting the security posture. This produces a SECURITY.md that demonstrates security thinking.
>
> 📍 **All code in Firebase Studio.**

### Step 19.1 — Add Security Headers Middleware
📍 **Firebase Editor** — create `api/middleware/security.py`

```python
"""Security headers middleware.

Adds standard security headers to every response, following OWASP recommendations.
These headers instruct browsers on how to handle the content safely.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Prevent MIME type sniffing (XSS vector)
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking (embedding in iframes)
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS filter in older browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Don't send referrer for cross-origin requests
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy — restrict resource loading
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "frame-ancestors 'none'"
        )

        return response
```

📍 **Firebase Editor** — add to `api/main.py` (after other middleware):

```python
from api.middleware.security import SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)
```

### Step 19.2 — Restrict CORS Origins
📍 **Firebase Editor** — update the CORS middleware in `api/main.py`

Replace the `allow_origins=["*"]` with specific origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:8080",
        "https://resume-api-portfolio.web.app",  # If using Firebase Hosting
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

> **Why restrict CORS?** `allow_origins=["*"]` means any website can make requests to your API from a browser. For a public read-only API this is low risk, but restricting it demonstrates security awareness. In production, you'd list only your actual frontend domains.

### Step 19.3 — Add Rate Limiting
📍 **Firebase Terminal**

```bash
uv add slowapi
```

📍 **Firebase Editor** — update `api/main.py` to add rate limiting:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Create limiter (uses client IP for rate tracking)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

Then add rate limit decorators to the AI endpoints (which call expensive external APIs):

📍 **Firebase Editor** — update `api/routers/ai.py`:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

limiter = Limiter(key_func=get_remote_address)


@router.post("/ask", response_model=QuestionResponse)
@limiter.limit("10/minute")  # Match Gemini free tier limit
async def ask_question(request: Request, body: QuestionRequest):
    # ... existing code ...
```

> **Why rate limiting?** The Gemini free tier allows 10 RPM. If someone hammers your AI endpoint, they'll exhaust your daily quota (250 requests). Rate limiting enforces the same 10/minute limit at the API level, protecting your quota. For non-AI endpoints, the default is unlimited — they're just reading from local databases.

### Step 19.4 — Create SECURITY.md
📍 **Firebase Editor** — create `SECURITY.md` at the repo root

```markdown
# Security Documentation

## Threat Model

### Assets
| Asset | Value | Location |
|-------|-------|----------|
| Resume data | Low (public) | api/main.py (hardcoded) |
| API keys | High | .env (gitignored), GitHub Secrets |
| Terraform state | Medium | GCS bucket (versioned) |
| BigQuery data | Low (synthetic) | GCP project |
| VM instance | Medium | GCP Compute Engine |

### Threat Vectors
| Threat | Likelihood | Impact | Mitigation |
|--------|-----------|--------|------------|
| Brute-force SSH | Medium | High | fail2ban (5 attempts → 1hr ban) |
| API abuse / DDoS | Low | Medium | Rate limiting (slowapi), Cloud Run auto-scaling |
| Dependency vulnerabilities | Medium | Medium | pip-audit in CI, weekly Trivy scans |
| Container escape | Low | High | Non-root user, minimal base image |
| Secret exposure | Medium | High | detect-secrets pre-commit, .gitignore, GitHub Secrets |
| IaC misconfiguration | Medium | Medium | Trivy IaC scanning, tagged firewall rules |
| SQL injection | Low | Low | Parameterized queries (SQLite), read-only BigQuery |

## Security Controls

### Application Layer
| Control | Tool | Status |
|---------|------|--------|
| Input validation | Pydantic models (FastAPI) | ✅ Implemented |
| Rate limiting | slowapi | ✅ Implemented |
| Security headers | Custom middleware (OWASP) | ✅ Implemented |
| CORS restriction | FastAPI CORSMiddleware | ✅ Implemented |
| Error handling | No stack traces in production | ✅ Implemented |
| API authentication | Not implemented (intentionally public) | N/A |

### Infrastructure Layer
| Control | Tool | Status |
|---------|------|--------|
| Network segmentation | Terraform VPC + firewall rules | ✅ Implemented |
| Least-privilege IAM | Terraform service accounts | ✅ Implemented |
| Container hardening | Non-root user, slim base image | ✅ Implemented |
| SSH protection | fail2ban | ✅ Implemented |
| Secrets management | .env + GitHub Secrets | ✅ Implemented |

### CI/CD Security
| Control | Tool | Frequency |
|---------|------|-----------|
| Python SAST | Bandit | Every push |
| Dependency scanning | pip-audit | Every push |
| Container scanning | Trivy | Every push |
| IaC scanning | Trivy | Every push |
| Dockerfile linting | Hadolint | Every push |
| Secret detection | detect-secrets | Pre-commit |
| Weekly vulnerability scan | Trivy (scheduled) | Weekly |

## OWASP API Security Top 10 Alignment

| # | OWASP Risk | This Project |
|---|-----------|-------------|
| API1 | Broken Object Level Authorization | N/A — no user-specific data |
| API2 | Broken Authentication | N/A — intentionally public API |
| API3 | Broken Object Property Level Authorization | N/A — read-only responses |
| API4 | Unrestricted Resource Consumption | ✅ Rate limiting on AI endpoints |
| API5 | Broken Function Level Authorization | N/A — no admin endpoints |
| API6 | Unrestricted Access to Sensitive Business Flows | ✅ Rate limiting prevents quota abuse |
| API7 | Server Side Request Forgery | N/A — no user-supplied URLs processed |
| API8 | Security Misconfiguration | ✅ Security headers, CORS restriction, IaC scanning |
| API9 | Improper Inventory Management | ✅ Swagger docs auto-generated, all endpoints documented |
| API10 | Unsafe Consumption of APIs | ✅ Gemini responses parsed safely (JSON fallback) |
```

### Step 19.5 — Git Commit
📍 **Firebase Terminal**

```bash
git add api/middleware/security.py SECURITY.md api/main.py api/routers/ai.py
git add requirements.txt pyproject.toml
git commit -m "Add security hardening: OWASP headers, rate limiting, SECURITY.md"
git push
```

---

## PHASE 20: FINAL VERIFICATION & README UPDATE (1 hour)

> Before calling Phase 3 complete, verify everything works end-to-end and update the README to reflect new capabilities.
>
> 📍 **Firebase Terminal for verification. Firebase Editor for README.**

### Step 20.1 — Full Verification Checklist
📍 **Firebase Terminal**

```bash
# === TERRAFORM ===

# 1. Terraform validates
cd terraform/environments/dev && terraform validate && cd ../../..
# Expected: "Success! The configuration is valid."

# 2. State is remote (not local)
cd terraform/environments/dev && terraform state list && cd ../../..
# Expected: List of managed resources

# === CI/CD ===

# 3. Ruff passes
ruff check .
# Expected: No errors

# 4. Bandit passes (no HIGH/CRITICAL)
bandit -r api/ -ll
# Expected: No issues found (or only LOW/MEDIUM)

# 5. pip-audit passes
pip-audit --requirement requirements.txt
# Expected: No known vulnerabilities

# === AI ===

# 6. Start the API
export GOOGLE_API_KEY="your-key"
uv run -- python -m uvicorn api.main:app --port 8000 --host 0.0.0.0 &
sleep 5

# 7. Test AI Q&A
curl -s -X POST http://localhost:8000/ai/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What cloud certifications does this person have?"}' | python3 -m json.tool
# Expected: JSON response mentioning AWS, Oracle, CompTIA certs

# 8. Test AI skill matching
curl -s -X POST http://localhost:8000/ai/skills/match \
  -H "Content-Type: application/json" \
  -d '{"job_description": "Senior Cloud Engineer with Terraform, Python, GCP, and CI/CD experience. Must have security background."}' | python3 -m json.tool
# Expected: JSON with match_percentage, matching/missing skills

# 9. Test security headers
curl -sI http://localhost:8000/ | grep -i "x-content-type\|x-frame\|x-xss\|referrer-policy\|content-security"
# Expected: All 5 security headers present

# 10. Test rate limiting (optional — send 15 quick requests to /ai/ask)
for i in $(seq 1 15); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/ai/ask \
    -H "Content-Type: application/json" \
    -d '{"question": "Test rate limit"}')
  echo "Request $i: $STATUS"
done
# Expected: First 10 return 200, requests 11-15 return 429 (Too Many Requests)

# Stop the background API
kill %1
```

### Step 20.2 — Verification Summary Table

| Category | Check | Status |
|----------|-------|--------|
| **Terraform** | `terraform validate` passes | ☐ |
| **Terraform** | Remote state in GCS | ☐ |
| **Terraform** | VPC + firewall created in GCP | ☐ |
| **Terraform** | Service account with least-privilege | ☐ |
| **CI/CD** | GitHub Actions CI runs on push | ☐ |
| **CI/CD** | Lint job passes (Ruff) | ☐ |
| **CI/CD** | Security scan job passes | ☐ |
| **CI/CD** | Build job creates Docker image | ☐ |
| **Security** | Trivy IaC scan passes | ☐ |
| **Security** | Trivy container scan passes | ☐ |
| **Security** | Hadolint passes | ☐ |
| **Security** | Bandit — no HIGH/CRITICAL | ☐ |
| **Security** | pip-audit — no known vulns | ☐ |
| **Security** | Security headers present | ☐ |
| **Security** | Rate limiting works | ☐ |
| **Security** | SECURITY.md exists | ☐ |
| **AI** | `/ai/ask` returns grounded answer | ☐ |
| **AI** | `/ai/skills/match` returns analysis | ☐ |
| **AI** | Responses cite sources | ☐ |
| **Pre-commit** | Hooks installed and running | ☐ |

### Step 20.3 — Update README.md
📍 **Firebase Editor** — update `README.md`

Add a new section describing Phase 3 capabilities. Add these to your existing skills table:

```markdown
## Phase 3: Production-Grade Infrastructure

| Skill Area | How It's Demonstrated |
|-----------|----------------------|
| Infrastructure as Code | Terraform modules managing VPC, firewall, IAM, with remote GCS state |
| CI/CD Automation | GitHub Actions pipeline: lint (Ruff) → security scan → test → build |
| AI / LLM Integration | RAG pipeline: resume chunks → HuggingFace embeddings → Chroma → Gemini |
| Security Engineering | Trivy + Bandit + pip-audit + Hadolint scanning in CI/CD |
| API Security | OWASP-aligned headers, rate limiting, CORS restriction |
| DevSecOps | Security gates that fail builds on HIGH/CRITICAL findings |
```

Add AI endpoints to the endpoint documentation:

```markdown
### AI Endpoints (Phase 3)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ai/ask` | POST | Ask questions about the resume (RAG-powered) |
| `/ai/skills/match` | POST | Analyze skill match against a job description |
```

### Step 20.4 — Final Git Commit
📍 **Firebase Terminal**

```bash
git add README.md
git commit -m "Complete Phase 3: IaC, CI/CD, AI (Gemini RAG), security hardening"
git push
```

---

## WHAT YOU BUILT — PHASE 3 SUMMARY

```
Phase 1: "I can build and deploy data-driven APIs"
Phase 2: "I can build end-to-end data flows"
Phase 3: "I can automate, secure, and enhance with AI"
```

| Component | Implementation | Free Tier Cost |
|-----------|---------------|---------------|
| Terraform | 5 modules, 2 environments, GCS remote state | $0 (5 GB GCS free) |
| CI/CD | GitHub Actions: 4-stage pipeline | $0 (unlimited public repos) |
| Security Scanning | Trivy + Bandit + pip-audit + Hadolint | $0 (all open source) |
| AI / RAG | Gemini 2.5 Flash + Chroma + HuggingFace | $0 (250 req/day free) |
| API Hardening | OWASP headers, rate limiting, CORS | $0 (code-level) |
| Pre-commit | Ruff + detect-secrets | $0 (open source) |
| **Total** | | **$0.00** |

**New project structure after Phase 3:**
```
resume-api-repo/
├── .github/workflows/        # CI/CD pipelines
│   ├── ci.yml                # Lint → test → build
│   └── security.yml          # Trivy + Hadolint
├── api/
│   ├── ai/                   # AI/RAG module
│   │   ├── embeddings.py     # HuggingFace local embeddings
│   │   ├── vectorstore.py    # Chroma vector DB
│   │   └── rag.py            # RAG pipeline (retrieve + generate)
│   ├── middleware/
│   │   ├── logging.py        # Request logging (Phase 2)
│   │   └── security.py       # OWASP security headers
│   ├── routers/
│   │   └── ai.py             # /ai/ask and /ai/skills/match
│   ├── main.py               # FastAPI app
│   ├── database.py
│   └── models.py
├── terraform/                 # Infrastructure as Code
│   ├── environments/
│   │   ├── dev/              # Dev environment config
│   │   └── prod/             # Prod environment config
│   ├── modules/
│   │   ├── networking/       # VPC, firewall, subnet
│   │   └── iam/              # Service accounts, roles
│   └── README.md
├── data/
│   ├── resume_chunks.json    # Chunked resume for RAG
│   └── sql/                  # BigQuery queries
├── SECURITY.md               # Security documentation
├── ruff.toml                 # Linter configuration
├── .pre-commit-config.yaml   # Pre-commit hooks
└── ... (existing Phase 1/2 files)
```

---

## TROUBLESHOOTING

| Problem | Cause | Fix |
|---------|-------|-----|
| `terraform init` fails | Wrong bucket name or missing bucket | Verify bucket: `gsutil ls`. Re-create if needed (Step 14.2) |
| `terraform plan` auth error | Credentials expired | Run: `gcloud auth application-default login` |
| GitHub Actions fails on lint | Ruff found issues | Run `ruff check --fix .` locally, commit, push |
| Bandit HIGH finding | Security issue in Python code | Read the finding, fix the code, or add `# nosec` if false positive |
| Trivy IaC fails | Terraform misconfiguration | Read the finding — usually overly permissive rules or missing encryption |
| AI endpoint returns 503 | GOOGLE_API_KEY not set | Set `export GOOGLE_API_KEY=...` or add to `.env` |
| AI endpoint returns 429 | Rate limit exceeded | Wait 1 minute (Gemini limit: 10 RPM) |
| Chroma fails to load | Missing embeddings model | Delete `chroma_db/` and restart — model downloads on first use |
| Pre-commit fails | Hooks not installed | Run: `pre-commit install` |
| Docker build fails in CI | Missing requirements.txt | Run: `uv pip compile pyproject.toml -o requirements.txt` and commit |
