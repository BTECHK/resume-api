output "instance_ip" {
  value       = google_compute_instance.n8n_vm.network_interface[0].access_config[0].nat_ip
  description = "External IP for SSH"
}

output "instance_name" {
  value       = google_compute_instance.n8n_vm.name
  description = "GCE instance name of the n8n VM"
}

output "ssh_command" {
  value       = "ssh ${var.ssh_user}@${google_compute_instance.n8n_vm.network_interface[0].access_config[0].nat_ip}"
  description = "Ready-to-run SSH command for logging into the VM"
}
