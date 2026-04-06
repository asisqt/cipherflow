# CipherFlow

A secure cloud-native data processing pipeline built with FastAPI, Docker, Kubernetes, and a full CI/CD delivery workflow via GitHub Actions and Sonatype Nexus.

---

## Architecture

```
Developer → GitHub → GitHub Actions Pipeline
                          │
               ┌──────────┼──────────┐
             Lint        Test       Build
           (ruff)  (unit+integ+BDD) (Docker)
                                      │
                                 Nexus Registry
                              (immutable SHA tags)
                                      │
                              DigitalOcean DOKS
                                      │
                         NGINX Ingress Controller
                                      │
                              cipherflow-api (FastAPI)
                              /api/v1/process
                              /api/v1/auth/token
```

**Pipeline stages:**

1. **Lint** — `ruff` checks all source and test code
2. **Test** — unit tests (TDD), integration tests, BDD scenarios (behave)
3. **Build & Push** — Docker image built with BuildKit cache, pushed to Nexus with immutable git SHA tag
4. **Deploy** — `kubectl rollout` with readiness-probe gating; automatic rollback on failure

---

## Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI + Uvicorn |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Encryption | Fernet / AES-128-CBC (cryptography) |
| CI/CD | GitHub Actions |
| Artifact registry | Sonatype Nexus 3 (Docker hosted repo) |
| Container runtime | Docker (multi-stage build) |
| Orchestration | DigitalOcean Kubernetes (DOKS) |
| Ingress | NGINX Ingress Controller |
| Infrastructure | Terraform + DigitalOcean provider |
| Testing | pytest (unit + integration) + behave (BDD) |
| Linting | ruff |

---

## Project Structure

```
cipherflow/
├── .github/workflows/
│   └── ci_cd_pipeline.yml       # 4-stage pipeline: lint → test → build → deploy
├── infrastructure/
│   ├── main.tf                  # DOKS cluster + VPC + firewalls
│   ├── variables.tf             # Region, node size, Nexus IP
│   └── security.tf              # Firewalls, SSH keys, RBAC model, DO project
├── src/
│   ├── main.py                  # FastAPI app with lifespan, middleware, router
│   ├── api/
│   │   ├── routes.py            # All endpoints: auth, health, process, info
│   │   └── dependencies.py      # JWT validation, user auth, DI type aliases
│   ├── core/
│   │   ├── config.py            # Pydantic Settings — env-var driven config
│   │   └── security_utils.py    # bcrypt, JWT sign/verify, Fernet encrypt/decrypt
│   └── services/
│       └── data_processor.py    # Validate → normalise → redact → checksum → encrypt
├── tests/
│   ├── unit/
│   │   └── test_data_processor.py   # 18 TDD unit tests, no I/O
│   ├── integration/
│   │   └── test_api_routes.py       # 20 integration tests via TestClient
│   └── features/
│       ├── secure_processing.feature # 6 Gherkin BDD scenarios
│       └── environment.py            # Behave step definitions
├── Dockerfile                   # Multi-stage: builder + lean runtime, non-root user
├── docker-compose.yml           # Local stack: API + Nexus
├── requirements.txt
└── README.md
```

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/token` | No | Issue JWT with username + password |
| `GET` | `/api/v1/health` | No | Liveness probe |
| `GET` | `/api/v1/ready` | No | Readiness probe |
| `POST` | `/api/v1/process` | Bearer JWT | Validate, normalise, redact, checksum |
| `POST` | `/api/v1/process/encrypted` | Bearer JWT | Same + Fernet-encrypt the output |
| `GET` | `/api/v1/info` | Bearer JWT | Build tag, version, environment |

Interactive docs available at `/docs` (Swagger UI) and `/redoc`.

---

## Quick Start (local)

### Run with Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8000/docs
- Nexus UI: http://localhost:8081 (takes ~2 min to start)

### Run without Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload
```

### Call the API

```bash
# 1. Get a token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"cipherflow-secret"}' | jq -r .access_token)

# 2. Process a payload
curl -X POST http://localhost:8000/api/v1/process \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payload_id": "demo-001",
    "source": "readme-example",
    "data": {"name": "Ashish Khatri", "role": "DevOps Engineer", "password": "secret123"}
  }'
```

Expected response:
```json
{
  "status": "success",
  "record_id": "demo-001",
  "checksum": "a3f9...64 hex chars",
  "processed": {
    "data": {
      "name": "ashish khatri",
      "role": "devops engineer",
      "password": "secr********"
    }
  },
  "encrypted": false,
  "warnings": []
}
```

---

## Running Tests

```bash
# Unit tests with coverage
pytest tests/unit/ -v --cov=src --cov-report=term-missing

# Integration tests
pytest tests/integration/ -v

# All tests together
pytest tests/unit/ tests/integration/ -v --cov=src --cov-fail-under=80

# BDD scenarios
behave tests/features/ --no-capture
```

---

## Infrastructure Setup

### Prerequisites

- DigitalOcean account with an API token
- Terraform ≥ 1.6
- `doctl` CLI installed
- An existing DO Droplet running Nexus (your $48/mo machine)

### 1 — Start Nexus on your existing Droplet

SSH into your droplet and run:

```bash
docker run -d \
  --name nexus \
  --restart unless-stopped \
  -p 8081:8081 \
  -p 8083:8083 \
  -v nexus-data:/nexus-data \
  sonatype/nexus3:latest

# Wait 2 min then get the initial admin password
docker exec nexus cat /nexus-data/admin.password
```

Open `http://<your-droplet-ip>:8081`, log in, then:

1. Change the admin password
2. Create a **Docker (hosted)** repository → HTTP connector on port 8083
3. Enable **Docker Bearer Token Realm**: Security → Realms → activate it

### 2 — Provision the DOKS cluster

```bash
cd infrastructure
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars: set nexus_droplet_ip to your droplet's public IP

export TF_VAR_do_token="your-digitalocean-api-token"

terraform init
terraform plan
terraform apply
```

Terraform provisions: VPC, DOKS cluster (2 × s-2vcpu-4gb in blr1), firewalls, SSH key, DO project.

### 3 — Configure kubectl

```bash
doctl kubernetes cluster kubeconfig save cipherflow
kubectl get nodes   # should show 2 Ready nodes
```

### 4 — Install NGINX Ingress Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.0/deploy/static/provider/aws/deploy.yaml
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=180s
```

### 5 — Create Nexus image pull secret in cluster

```bash
kubectl create namespace cipherflow
kubectl create secret docker-registry nexus-pull-secret \
  --namespace=cipherflow \
  --docker-server=<YOUR_DROPLET_IP>:8083 \
  --docker-username=admin \
  --docker-password=<YOUR_NEXUS_PASS>
```

### 6 — Add GitHub Secrets

In your repo → **Settings → Secrets and variables → Actions**:

| Secret | Value |
|---|---|
| `NEXUS_HOST` | Your droplet public IP |
| `NEXUS_USER` | `admin` |
| `NEXUS_PASS` | Your Nexus admin password |
| `DO_TOKEN` | Your DigitalOcean API token |
| `DOKS_CLUSTER_NAME` | `cipherflow` |

### 7 — Deploy

```bash
git push origin main
```

Watch at: `https://github.com/<you>/cipherflow/actions`

---

## Key Design Decisions

**TDD + BDD together** — Unit tests (`pytest`) verify individual functions in isolation. Integration tests verify component interaction via FastAPI's `TestClient`. BDD scenarios (`behave`) verify complete user workflows in Gherkin, making tests readable as documentation.

**Immutable artifacts** — Every image is tagged with `$GITHUB_SHA`. Images pushed to Nexus are never overwritten. Rollbacks redeploy a prior SHA tag rather than rebuilding.

**Health-check gated rollouts** — `kubectl rollout status --timeout=3m` blocks the pipeline until new pods pass readiness probes. Failure triggers `kubectl rollout undo` automatically.

**Non-root container** — The Dockerfile creates a `cfuser` system account. The runtime stage runs as that user, so a container escape has no root privileges on the host.

**Fernet encryption** — `POST /process/encrypted` returns a Fernet-encrypted blob. Only parties with the `ENCRYPTION_KEY` can decrypt it, making the pipeline safe for sensitive data in transit through intermediate systems.

---

## Cost Estimate (DigitalOcean blr1)

| Resource | Cost |
|---|---|
| Existing Droplet (Nexus) | $48/mo (already running) |
| DOKS — 2 × s-2vcpu-4gb | $48/mo |
| DO Load Balancer (auto) | $12/mo |
| **Total extra** | **~$60/mo** |

Destroy the DOKS cluster when not in use: `terraform destroy`

---

## Teardown

```bash
kubectl delete namespace cipherflow
cd infrastructure && terraform destroy
```
