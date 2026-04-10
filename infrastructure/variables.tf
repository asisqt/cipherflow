# ═══════════════════════════════════════════════════════════════════════════════
# CipherFlow Infrastructure Variables
# ═══════════════════════════════════════════════════════════════════════════════

variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "cluster_name" {
  description = "Name of the Kubernetes cluster"
  type        = string
  default     = "cipherflow-cluster"
}

variable "region" {
  description = "DigitalOcean region for all resources"
  type        = string
  default     = "blr1"
}

variable "k8s_version" {
  description = "Kubernetes version slug"
  type        = string
  default     = "1.32.13-do.2"
}

variable "node_size" {
  description = "Droplet size for worker nodes"
  type        = string
  default     = "s-2vcpu-4gb"
}

variable "node_count" {
  description = "Number of worker nodes"
  type        = number
  default     = 1
}

variable "environment" {
  description = "Deployment environment (production, staging, development)"
  type        = string
  default     = "production"
}

variable "registry_name" {
  description = "Name of the container registry"
  type        = string
  default     = "cipherflow-registry"
}
