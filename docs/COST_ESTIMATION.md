# CipherFlow Infrastructure Cost Estimation

## Monthly Cost Breakdown (DigitalOcean)

### Minimum Viable Production (Current Setup)

| Resource | Specification | Monthly Cost |
|----------|---------------|-------------|
| DOKS Cluster | 1 node, s-2vcpu-4gb | $24.00 |
| DOKS Control Plane | Free (managed) | $0.00 |
| Container Registry | Starter tier | $0.00 |
| LoadBalancer (backend) | 1x standard | $12.00 |
| LoadBalancer (frontend) | 1x standard | $12.00 |
| **Total** | | **$48.00/mo** |

### Recommended Production

| Resource | Specification | Monthly Cost |
|----------|---------------|-------------|
| DOKS Cluster | 2 nodes, s-2vcpu-4gb | $48.00 |
| DOKS Control Plane | Free (managed) | $0.00 |
| Container Registry | Basic tier | $5.00 |
| LoadBalancer (backend) | 1x standard | $12.00 |
| LoadBalancer (frontend) | 1x standard | $12.00 |
| Spaces (Terraform state) | 250GB included | $5.00 |
| **Total** | | **$82.00/mo** |

### High Availability Production

| Resource | Specification | Monthly Cost |
|----------|---------------|-------------|
| DOKS Cluster | 3 nodes, s-4vcpu-8gb | $144.00 |
| DOKS Control Plane (HA) | Free (managed) | $0.00 |
| Container Registry | Professional | $12.00 |
| LoadBalancer (backend) | 1x standard | $12.00 |
| LoadBalancer (frontend) | 1x standard | $12.00 |
| Managed Database | PostgreSQL basic | $15.00 |
| Spaces (backups + state) | 250GB included | $5.00 |
| Monitoring (DO native) | Free tier | $0.00 |
| **Total** | | **$200.00/mo** |

## Equivalent Costs on Other Providers

| Provider | K8s Control Plane | 2-Node Cluster | Registry | Total Estimate |
|----------|-------------------|----------------|----------|----------------|
| DigitalOcean | Free | $48 | Free | ~$82/mo |
| Google Cloud (GKE) | Free (1 zonal) | $49 | $0 (500MB free) | ~$85/mo |
| AWS (EKS) | $73 | $49 | $0 (500MB free) | ~$135/mo |
| Azure (AKS) | Free | $53 | $5 (Basic) | ~$90/mo |

## Cost Optimization Tips

1. Use spot/preemptible nodes for non-critical workloads (60-90% savings)
2. Right-size pods with resource requests matching actual usage
3. HPA scales down during low traffic automatically
4. Single LoadBalancer with Ingress controller instead of one per service
5. Use ClusterIP + Ingress instead of multiple LoadBalancers (saves $12/mo each)
6. Schedule non-production clusters to shut down nights and weekends
