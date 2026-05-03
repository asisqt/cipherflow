# CipherFlow Service Level Agreement (SLA)

## Availability Target

| Tier | Uptime | Monthly Downtime Budget |
|------|--------|------------------------|
| Standard | 99.5% | 3 hours 39 minutes |
| Professional | 99.9% | 43 minutes |
| Enterprise | 99.95% | 21 minutes |

## Performance SLOs (Service Level Objectives)

| Metric | Target | Measurement |
|--------|--------|-------------|
| API response time (p50) | < 50ms | Median latency |
| API response time (p95) | < 200ms | 95th percentile |
| API response time (p99) | < 500ms | 99th percentile |
| Error rate | < 0.1% | 5xx responses / total |
| Time to first byte | < 100ms | TTFB from client |
| Throughput | > 500 req/s | Per pod, sustained |

## Recovery Objectives

| Metric | Target | Description |
|--------|--------|-------------|
| RTO (Recovery Time Objective) | < 15 minutes | Time to restore service |
| RPO (Recovery Point Objective) | 0 data loss | Stateless architecture |
| MTTR (Mean Time to Recovery) | < 10 minutes | Average restoration time |
| MTBF (Mean Time Between Failures) | > 720 hours | Target reliability |

## Incident Severity Levels

| Level | Description | Response Time | Resolution Time |
|-------|-------------|---------------|-----------------|
| P1 Critical | Complete service outage | 15 minutes | 1 hour |
| P2 High | Partial outage or degraded performance | 30 minutes | 4 hours |
| P3 Medium | Non-critical feature broken | 2 hours | 24 hours |
| P4 Low | Cosmetic issue or improvement | 24 hours | 1 week |

## Monitoring and Alerting

| Check | Frequency | Alert Threshold |
|-------|-----------|-----------------|
| Health endpoint | 30 seconds | 2 consecutive failures |
| Readiness probe | 10 seconds | 1 failure (removes from LB) |
| CPU utilization | 60 seconds | > 70% for 2 minutes |
| Memory utilization | 60 seconds | > 80% for 2 minutes |
| Error rate | 60 seconds | > 0.1% for 5 minutes |
| Pod restart count | 300 seconds | > 3 restarts per hour |

## Exclusions

SLA does not apply to:
- Scheduled maintenance windows (announced 48 hours in advance)
- Force majeure events
- Issues caused by client-side misconfiguration
- Free trial and development environments
- Third-party dependency failures (cloud provider outages)
