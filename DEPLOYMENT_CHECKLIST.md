# Deployment Checklist

Pre-deployment verification for CipherFlow releases.

## Before Deploying

- [ ] All tests pass locally (make test)
- [ ] Linter reports zero issues (make lint)
- [ ] Docker images build successfully (make build)
- [ ] Environment variables configured in K8s secrets
- [ ] SECRET_KEY is not using default value in production
- [ ] ENCRYPTION_KEY is not using default value in production
- [ ] CORS_ORIGINS restricted to known frontend domains
- [ ] Container registry (DOCR) is accessible
- [ ] Kubernetes cluster is healthy (kubectl get nodes)

## During Deployment

- [ ] CI/CD pipeline passes all stages
- [ ] Docker images tagged with commit SHA (immutable tags)
- [ ] K8s manifests applied without errors
- [ ] Rollout status shows successful completion
- [ ] No pods in CrashLoopBackOff or ImagePullBackOff

## After Deploying

- [ ] Health endpoint returns 200 OK
- [ ] Ready endpoint returns 200
- [ ] Frontend loads and displays landing page
- [ ] Authentication flow works (login with demo creds)
- [ ] Process endpoint returns valid response
- [ ] Encrypted endpoint returns encrypted blob
- [ ] Response headers present (X-Request-ID, X-Process-Time)
- [ ] No error spikes in pod logs (kubectl logs)

## Rollback Procedure

1. Identify the last working commit SHA
2. Run: kubectl set image deployment/cipherflow-api api=registry.digitalocean.com/cipherflow-registry/cipherflow:GOOD_SHA
3. Run: kubectl rollout status deployment/cipherflow-api
4. Verify health endpoint returns 200
