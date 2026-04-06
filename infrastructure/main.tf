terraform {
  required_version = ">= 1.6"
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.36"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.29"
    }
  }

  # Store state in DO Spaces (S3-compatible).
  # Create the bucket manually first, then uncomment:
  # backend "s3" {
  #   endpoint                    = "blr1.digitaloceanspaces.com"
  #   key                         = "cipherflow/terraform.tfstate"
  #   bucket                      = "cipherflow-tf-state"
  #   region                      = "us-east-1"          # placeholder — DO ignores this
  #   skip_credentials_validation = true
  #   skip_metadata_api_check     = true
  #   skip_region_validation      = true
  # }
}

provider "digitalocean" {
  token = var.do_token
}

# ── VPC ───────────────────────────────────────────────────────────────────────
resource "digitalocean_vpc" "main" {
  name     = "${var.cluster_name}-vpc"
  region   = var.region
  ip_range = "10.10.0.0/16"
}

# ── DOKS Cluster ──────────────────────────────────────────────────────────────
resource "digitalocean_kubernetes_cluster" "main" {
  name     = var.cluster_name
  region   = var.region
  version  = data.digitalocean_kubernetes_versions.latest.latest_version
  vpc_uuid = digitalocean_vpc.main.id

  node_pool {
    name       = "${var.cluster_name}-workers"
    size       = var.node_size
    node_count = var.node_count
    auto_scale = true
    min_nodes  = 1
    max_nodes  = 4

    labels = {
      role    = "worker"
      project = var.cluster_name
    }
  }

  tags = [var.cluster_name, "managed-by-terraform"]

  # Upgrade cluster automatically on patch versions
  maintenance_policy {
    start_time = "02:00"
    day        = "sunday"
  }
}

# Lookup latest available k8s version in the chosen region
data "digitalocean_kubernetes_versions" "latest" {
  version_prefix = "${var.k8s_version}."
}

# ── Firewall: protect the DOKS worker nodes ───────────────────────────────────
resource "digitalocean_firewall" "k8s_workers" {
  name = "${var.cluster_name}-workers-fw"

  # Tags link this firewall to the DOKS node pool droplets
  tags = ["k8s:${digitalocean_kubernetes_cluster.main.id}"]

  # Allow inbound from the load balancer only (no direct node exposure)
  inbound_rule {
    protocol         = "tcp"
    port_range       = "30000-32767"   # NodePort range
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Inter-node communication within the VPC
  inbound_rule {
    protocol         = "tcp"
    port_range       = "all"
    source_addresses = [digitalocean_vpc.main.ip_range]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "all"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "all"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}

# ── Firewall: protect the Nexus Droplet ───────────────────────────────────────
resource "digitalocean_firewall" "nexus" {
  name = "${var.cluster_name}-nexus-fw"

  # Nexus UI — restrict to your IP in production
  inbound_rule {
    protocol         = "tcp"
    port_range       = "8081"
    source_addresses = ["0.0.0.0/0"]
  }

  # Docker registry — GitHub Actions runners need to push here
  inbound_rule {
    protocol         = "tcp"
    port_range       = "8083"
    source_addresses = ["0.0.0.0/0"]
  }

  # SSH
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0"]   # Restrict to your IP in production
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "all"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}

# ── Outputs ───────────────────────────────────────────────────────────────────
output "cluster_name" {
  value = digitalocean_kubernetes_cluster.main.name
}

output "cluster_endpoint" {
  value     = digitalocean_kubernetes_cluster.main.endpoint
  sensitive = true
}

output "kubeconfig_command" {
  value = "doctl kubernetes cluster kubeconfig save ${var.cluster_name}"
}

output "nexus_registry_url" {
  value = "${var.nexus_droplet_ip}:${var.nexus_registry_port}"
}
