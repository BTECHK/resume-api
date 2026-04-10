terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# ──────────────────────────────────────────────────────────────
# n8n Email Bot host — GCE e2-micro (EMAIL-01, D-08, D-10)
# Boot-time: metadata_startup_script runs startup.sh which
# creates 2GB swap, installs Docker, and deploys the systemd unit.
# ──────────────────────────────────────────────────────────────
resource "google_compute_instance" "n8n_vm" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = var.zone

  tags = ["n8n-bot", "ssh-allowed"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = var.disk_size_gb
      type  = "pd-standard"
    }
  }

  network_interface {
    network = "default"

    # Ephemeral external IP so the operator can SSH in.
    # D-09: The n8n UI is NOT exposed to the internet — the
    # firewall rule below only opens port 22.
    access_config {}
  }

  metadata = {
    ssh-keys = "${var.ssh_user}:${file(var.ssh_pub_key_path)}"
  }

  # Pitfall #4: use the metadata_startup_script attribute (not the
  # metadata map key) to avoid Terraform provider issue #9459.
  metadata_startup_script = file("${path.module}/startup.sh")

  service_account {
    # cloud-platform scope allows future Secret Manager access
    # (Gmail OAuth secrets, AI service URL, etc.).
    scopes = ["cloud-platform"]
  }
}

# ──────────────────────────────────────────────────────────────
# Firewall: SSH (port 22) only (D-09)
# Intentionally NO rule for the n8n UI port — the n8n web UI is
# not publicly reachable. Access it via SSH port-forward instead.
# ──────────────────────────────────────────────────────────────
resource "google_compute_firewall" "allow_ssh" {
  name    = "resume-bot-n8n-allow-ssh"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ssh-allowed"]
}
