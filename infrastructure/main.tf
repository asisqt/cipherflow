# ═══════════════════════════════════════════════════════════════════════════════
# CipherFlow Infrastructure — DigitalOcean Kubernetes (DOKS)
# ═══════════════════════════════════════════════════════════════════════════════
# Provisions:
#   1. A managed Kubernetes cluster in the Bangalore region
#   2. A container registry for Docker images
#   3. Registry-to-cluster integration for private image pulls
# ═══════════════════════════════════════════════════════════════════════════════

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

# ── Kubernetes Cluster ───────────────────────────────────────────────────────

resource "digitalocean_kubernetes_cluster" "cipherflow" {
  name    = var.cluster_name
  region  = var.region
  version = var.k8s_version

  node_pool {
    name       = "${var.cluster_name}-pool"
    size       = var.node_size
    node_count = var.node_count

    labels = {
      project     = "cipherflow"
      environment = var.environment
    }
  }

  tags = ["cipherflow", var.environment]
}

# ── Container Registry ───────────────────────────────────────────────────────

resource "digitalocean_container_registry" "cipherflow" {
  name                   = var.registry_name
  subscription_tier_slug = "starter"
  region                 = var.region
}

# ── Registry → Cluster Integration ───────────────────────────────────────────
# Allows the K8s cluster to pull images from the private DOCR registry

resource "digitalocean_container_registry_docker_credentials" "cipherflow" {
  registry_name = digitalocean_container_registry.cipherflow.name
}

# ── Outputs ──────────────────────────────────────────────────────────────────

output "cluster_id" {
  description = "The ID of the Kubernetes cluster"
  value       = digitalocean_kubernetes_cluster.cipherflow.id
}

output "cluster_endpoint" {
  description = "The API endpoint of the Kubernetes cluster"
  value       = digitalocean_kubernetes_cluster.cipherflow.endpoint
}

output "registry_endpoint" {
  description = "The endpoint of the container registry"
  value       = digitalocean_container_registry.cipherflow.endpoint
}

# ── Outputs for CI/CD integration ────────────────────────────────────────────

output "cluster_name" {
  description = "Name of the Kubernetes cluster for kubectl config"
  value       = digitalocean_kubernetes_cluster.cipherflow.name
}

output "node_pool_size" {
  description = "Current node count in the default pool"
  value       = digitalocean_kubernetes_cluster.cipherflow.node_pool[0].node_count
}
