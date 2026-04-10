# ═══════════════════════════════════════════════════════════════════════════════
# CipherFlow Security Configuration
# ═══════════════════════════════════════════════════════════════════════════════
# Defines network-level security: firewall rules restricting inbound traffic
# to only HTTPS (443), HTTP (80), and the Kubernetes API (6443).
# All other ports are blocked by default.
# ═══════════════════════════════════════════════════════════════════════════════

resource "digitalocean_firewall" "cipherflow" {
  name = "${var.cluster_name}-firewall"

  # Apply to all droplets tagged with "cipherflow"
  tags = ["cipherflow"]

  # ── Inbound Rules ────────────────────────────────────────────────────────
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

  inbound_rule {
    protocol         = "tcp"
    port_range       = "6443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Allow all inter-node communication within the cluster
  inbound_rule {
    protocol         = "tcp"
    port_range       = "1-65535"
    source_tags      = ["cipherflow"]
  }

  inbound_rule {
    protocol         = "udp"
    port_range       = "1-65535"
    source_tags      = ["cipherflow"]
  }

  # ── Outbound Rules ──────────────────────────────────────────────────────
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}
