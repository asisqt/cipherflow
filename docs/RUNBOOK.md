# CipherFlow Operations Runbook

## Common Operations

### Scale Backend Pods

    # Scale up for high traffic
    kubectl scale deployment cipherflow-api --replicas=4

    # Scale back down
    kubectl scale deployment cipherflow-api --replicas=2

    # Check current replicas
    kubectl get deployment cipherflow-api

### Rolling Restart (zero downtime)

    # Restart all backend pods one at a time
    kubectl rollout restart deployment/cipherflow-api

    # Watch rollout progress
    kubectl rollout status deployment/cipherflow-api

    # Rollback if something goes wrong
    kubectl rollout undo deployment/cipherflow-api

### View Logs

    # Backend logs (last 100 lines)
    kubectl logs -l app=cipherflow,component=api --tail=100

    # Frontend logs
    kubectl logs -l app=cipherflow,component=frontend --tail=100

    # Follow logs in real-time
    kubectl logs -l app=cipherflow,component=api -f

    # Logs from a specific pod
    kubectl logs cipherflow-api-xxxx-yyyy

### Debug a Pod

    # Get pod status and events
    kubectl describe pod cipherflow-api-xxxx-yyyy

    # Execute into a running pod
    kubectl exec -it cipherflow-api-xxxx-yyyy -- /bin/sh

    # Check environment variables
    kubectl exec cipherflow-api-xxxx-yyyy -- env | grep -E "SECRET|ENCRYPT|ENV"

### Update Secrets

    # Edit secrets directly
    kubectl edit secret cipherflow-secrets

    # Or delete and recreate
    kubectl delete secret cipherflow-secrets
    kubectl apply -f k8s/secrets.yaml

    # Restart pods to pick up new secrets
    kubectl rollout restart deployment/cipherflow-api

### Check Resource Usage

    # Pod CPU and memory
    kubectl top pods

    # Node resources
    kubectl top nodes

    # Detailed pod resource allocation
    kubectl describe nodes | grep -A 5 "Allocated resources"

### DNS and Networking

    # Check service endpoints
    kubectl get endpoints

    # Test internal DNS resolution
    kubectl run tmp --image=busybox --rm -it -- nslookup cipherflow-api

    # Check network policies
    kubectl get networkpolicies

### Certificate and Token Management

    # Check when JWT tokens expire
    # Decode a token (paste token value)
    echo "TOKEN_HERE" | cut -d. -f2 | base64 -d 2>/dev/null | python3 -m json.tool

    # Rotate DO registry credentials
    doctl registry kubernetes-manifest | kubectl apply -f -

### Emergency Procedures

    # Complete service restart
    kubectl rollout restart deployment/cipherflow-api
    kubectl rollout restart deployment/cipherflow-frontend

    # Nuclear option: delete and redeploy everything
    kubectl delete -f k8s/
    kubectl apply -f k8s/secrets.yaml
    kubectl apply -f k8s/api-deployment.yaml
    kubectl apply -f k8s/frontend-deployment.yaml

    # Check all resources
    kubectl get all -l app=cipherflow
