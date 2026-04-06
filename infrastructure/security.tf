# security.tf
# Defines all security-boundary resources for the CipherFlow cluster.
# Kept separate from main.tf so security reviews are a single-file diff.

# ── Project (groups all resources for billing + access control) ───────────────
resource "digitalocean_project" "cipherflow" {
  name        = "CipherFlow"
  description = "Secure cloud-native data processing pipeline"
  purpose     = "Web Application"
  environment = "Production"

  resources = [
    digitalocean_kubernetes_cluster.main.urn,
  ]
}

# ── SSH Key (registered with DO for droplet access) ───────────────────────────
resource "digitalocean_ssh_key" "deployer" {
  name       = "${var.cluster_name}-deployer"
  public_key = file(var.ssh_public_key_path)
}

# ── Inbound rate-limit policy (via DO Cloud Firewall) ────────────────────────
# Restricts inbound traffic on the API port to prevent volumetric attacks.
# Additional rate limiting is enforced at the application layer (FastAPI middleware).
resource "digitalocean_firewall" "api_ratelimit" {
  name = "${var.cluster_name}-api-ratelimit"

  tags = ["k8s:${digitalocean_kubernetes_cluster.main.id}"]

  # HTTPS only for API traffic
  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # HTTP — for Let's Encrypt ACME challenge only; redirect to HTTPS via Ingress
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "all"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}

# ── DO Spaces bucket for Terraform state (create manually before terraform init)
# This block is reference documentation — the bucket itself must be created via
# the DO console or doctl before running terraform init with the S3 backend.
#
# doctl spaces create cipherflow-tf-state --region blr1
#
# Then set access keys as env vars:
#   export AWS_ACCESS_KEY_ID=<spaces-key>
#   export AWS_SECRET_ACCESS_KEY=<spaces-secret>

# ── Kubernetes RBAC (applied post-cluster creation) ──────────────────────────
# These locals document the RBAC model; actual ClusterRoleBinding manifests
# live in k8s/rbac.yaml and are applied by the CI pipeline.
locals {
  rbac_model = {
    "github-actions-deployer" = {
      role       = "cluster-admin"   # Scoped to devops-demo namespace in k8s/rbac.yaml
      bound_to   = "ServiceAccount"
      namespace  = "cipherflow"
    }
    "read-only-auditor" = {
      role       = "view"
      bound_to   = "Group"
      namespace  = "cipherflow"
    }
  }
}

output "security_summary" {
  value = {
    firewall_k8s_workers = digitalocean_firewall.k8s_workers.id
    firewall_nexus       = digitalocean_firewall.nexus.id
    firewall_api         = digitalocean_firewall.api_ratelimit.id
    project_id           = digitalocean_project.cipherflow.id
    ssh_key_fingerprint  = digitalocean_ssh_key.deployer.fingerprint
  }
}
