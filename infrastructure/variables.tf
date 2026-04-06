variable "do_token" {
  description = "DigitalOcean API token — set via TF_VAR_do_token env var, never commit"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "DigitalOcean region"
  type        = string
  default     = "blr1"   # Bangalore — closest to Delhi
}

variable "cluster_name" {
  description = "DOKS cluster name"
  type        = string
  default     = "cipherflow"
}

variable "k8s_version" {
  description = "Kubernetes version for DOKS"
  type        = string
  default     = "1.29"
}

variable "node_size" {
  description = "Droplet size for Kubernetes worker nodes"
  type        = string
  default     = "s-2vcpu-4gb"
}

variable "node_count" {
  description = "Number of worker nodes in the default node pool"
  type        = number
  default     = 2
}

variable "nexus_droplet_ip" {
  description = "Public IP of your existing DigitalOcean droplet running Nexus"
  type        = string
}

variable "nexus_registry_port" {
  description = "Port Nexus Docker hosted repository listens on"
  type        = number
  default     = 8083
}

variable "ssh_public_key_path" {
  description = "Path to SSH public key for Droplet access"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}
