# ═══════════════════════════════════════════════════════════════════════════════
# CipherFlow Terraform Remote State Backend
# ═══════════════════════════════════════════════════════════════════════════════
# Stores Terraform state in DigitalOcean Spaces (S3-compatible)
# instead of local filesystem. Enables team collaboration and
# prevents state file conflicts.
#
# Prerequisites:
#   1. Create a DO Spaces bucket named "cipherflow-tfstate"
#   2. Generate Spaces access keys from DO console
#   3. Export credentials:
#      export AWS_ACCESS_KEY_ID="your-spaces-key"
#      export AWS_SECRET_ACCESS_KEY="your-spaces-secret"
#
# Usage:
#   terraform init -backend-config="access_key=$AWS_ACCESS_KEY_ID" \
#                  -backend-config="secret_key=$AWS_SECRET_ACCESS_KEY"
# ═══════════════════════════════════════════════════════════════════════════════

terraform {
  backend "s3" {
    endpoint                    = "https://blr1.digitaloceanspaces.com"
    bucket                      = "cipherflow-tfstate"
    key                         = "terraform.tfstate"
    region                      = "us-east-1"
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_requesting_account_id  = true
    skip_s3_checksum            = true
  }
}
