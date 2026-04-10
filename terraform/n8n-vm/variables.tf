variable "project_id" {
  type        = string
  description = "GCP project ID"
}

variable "region" {
  type        = string
  description = "GCP region for the VM and related resources"
  default     = "us-central1"
}

variable "zone" {
  type        = string
  description = "GCP zone for the e2-micro VM"
  default     = "us-central1-a"
}

variable "ssh_pub_key_path" {
  type        = string
  description = "Path to SSH public key file, e.g. ~/.ssh/id_ed25519.pub"
}

variable "ssh_user" {
  type        = string
  description = "Linux user on the VM that receives the SSH public key"
  default     = "ubuntu"
}

variable "instance_name" {
  type        = string
  description = "GCE instance name for the n8n VM"
  default     = "resume-bot-n8n"
}

variable "machine_type" {
  type        = string
  description = "GCE machine type (free tier: e2-micro)"
  default     = "e2-micro"
}

variable "disk_size_gb" {
  type        = number
  description = "Boot disk size in GB (free tier limit: 30)"
  default     = 30
}
