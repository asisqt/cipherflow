# Backup and Disaster Recovery Strategy

## Overview

CipherFlow follows a stateless architecture where application pods store no persistent data.
All critical state is managed through version-controlled configuration and container images.

## What Needs Backing Up

| Component | Location | Backup Method | Frequency |
|-----------|----------|---------------|-----------|
| Application code | GitHub | Git distributed copies | Every push |
| Docker images | DOCR registry | Registry replication | Every CI/CD run |
| K8s secrets | k8s/secrets.yaml | Encrypted in git (template only) | On change |
| K8s manifests | k8s/ directory | Git version control | Every push |
| Terraform state | Local + remote backend | S3/Spaces remote state | On apply |
| Environment config | .env files | Secure vault (not in git) | On change |

## Recovery Procedures

### Scenario 1: Pod Failure
- **Impact**: Single pod goes down
- **Recovery**: Automatic — Kubernetes restarts the pod via liveness probe
- **RTO**: 30 seconds (probe interval + restart time)

### Scenario 2: Node Failure
- **Impact**: All pods on that node go down
- **Recovery**: Kubernetes reschedules pods to healthy nodes
- **RTO**: 2-5 minutes
- **Requirement**: Minimum 2 nodes in production

### Scenario 3: Cluster Failure
- **Impact**: Entire Kubernetes cluster is lost
- **Recovery**:
  1. terraform apply to provision new cluster
  2. git push to trigger CI/CD pipeline
  3. Pipeline rebuilds images and deploys to new cluster
- **RTO**: 20-30 minutes

### Scenario 4: Registry Failure
- **Impact**: Cannot pull container images
- **Recovery**: CI/CD pipeline rebuilds from source and pushes to new registry
- **RTO**: 10-15 minutes

### Scenario 5: Source Code Loss
- **Impact**: GitHub repository deleted or corrupted
- **Recovery**: Push from any developer local clone
- **RTO**: 5 minutes
- **Mitigation**: All developers maintain local clones with full history

## RPO (Recovery Point Objective)

- **Code**: Zero data loss (every commit is pushed)
- **Config**: Zero data loss (version controlled)
- **Secrets**: Potential loss if not backed up to vault — rotate and recreate

## Infrastructure Recreation Commands

    # Recreate cluster
    cd infrastructure
    terraform init
    terraform apply -var "do_token=YOUR_TOKEN" -auto-approve

    # Reconnect kubectl
    doctl kubernetes cluster kubeconfig save cipherflow-cluster

    # Redeploy (automatic via CI/CD on push, or manual)
    kubectl apply -f k8s/secrets.yaml
    kubectl apply -f k8s/api-deployment.yaml
    kubectl apply -f k8s/frontend-deployment.yaml
