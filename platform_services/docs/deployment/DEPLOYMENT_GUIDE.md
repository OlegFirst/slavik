# BCM Platform Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Business Continuity Management (BCM) Platform to production environments. The platform is designed to comply with ISO 22301:2019 standards and consists of multiple microservices with supporting infrastructure.

### Platform Architecture

The BCM Platform consists of the following components:

**Core Services:**
- Planning Service (Port 8011) - ISO 22301 Clause 8.3 BCM Planning
- Plans Service (Port 8023) - ISO 22301 Clause 8.4 Business Continuity Plans
- BIA Service (Port 8012) - Business Impact Analysis (ISO 22301 Clause 8.2.2)
- Compliance Service (Port 8014) - ISO 22301 Compliance Management

**Supporting Infrastructure:**
- PostgreSQL 15+ - Primary database
- Redis 7+ - Caching and rate limiting
- EventBus - Inter-service communication
- Prometheus - Metrics collection
- Grafana - Metrics visualization
- Monitoring Service (Port 8045) - Active monitoring and alerting

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Load Balancer / API Gateway               │
│                    (nginx/traefik with SSL/TLS)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼────────┐ ┌────▼────────┐
│  Planning      │ │   Plans     │ │    BIA      │
│  Service       │ │   Service   │ │  Service    │
│  :8011         │ │   :8023     │ │   :8012     │
└───────┬────────┘ └────┬────────┘ └────┬────────┘
        │               │               │
        └───────┬───────┴───────┬───────┘
                │               │
        ┌───────▼───────┐ ┌─────▼──────┐
        │  PostgreSQL   │ │   Redis    │
        │  :5432        │ │   :6379    │
        └───────┬───────┘ └─────┬──────┘
                │               │
        ┌───────▼───────────────▼──────┐
        │      Monitoring Stack        │
        │  Prometheus + Grafana        │
        │  Monitoring Service          │
        └──────────────────────────────┘
```

## Prerequisites

### System Requirements

**Minimum Production Requirements:**
- **CPU:** 8 cores (2 cores per service minimum)
- **RAM:** 16 GB (4 GB for services, 4 GB for PostgreSQL, 2 GB for Redis, rest for OS)
- **Disk:** 100 GB SSD (50 GB for data, 50 GB for logs and backups)
- **Network:** 1 Gbps network interface
- **OS:** Ubuntu 22.04 LTS, RHEL 8+, or compatible Linux distribution

**Recommended Production Requirements:**
- **CPU:** 16 cores
- **RAM:** 32 GB
- **Disk:** 500 GB SSD with RAID 10
- **Network:** 10 Gbps network interface

### Software Prerequisites

```bash
# Docker Engine 24.0+
docker --version

# Docker Compose 2.20+
docker-compose --version

# PostgreSQL Client (for management)
psql --version

# curl (for health checks)
curl --version

# jq (for JSON processing)
jq --version
```

### Network Requirements

**Required Ports:**
- 443 (HTTPS) - External access via load balancer
- 5432 (PostgreSQL) - Database access (internal only)
- 6379 (Redis) - Cache access (internal only)
- 8011 (Planning Service) - Internal/Load balancer
- 8012 (BIA Service) - Internal/Load balancer
- 8014 (Compliance Service) - Internal/Load balancer
- 8023 (Plans Service) - Internal/Load balancer
- 8045 (Monitoring Service) - Internal only
- 9090 (Prometheus) - Internal only
- 3000 (Grafana) - Internal only

**Firewall Rules:**
- Allow inbound: 443 (from internet/users)
- Allow internal: All services within BCM network
- Deny direct access to services from internet (use load balancer)

## Pre-Deployment Checklist

Before deploying to production, complete the following:

### Security Checklist
- [ ] Generate production JWT RSA key pairs (4096-bit)
- [ ] Change all default passwords (PostgreSQL, Redis, Grafana)
- [ ] Configure secret management (HashiCorp Vault or AWS Secrets Manager)
- [ ] Obtain SSL/TLS certificates (Let's Encrypt or commercial CA)
- [ ] Configure firewall rules on host and cloud security groups
- [ ] Set up VPN or bastion host for administrative access
- [ ] Enable database encryption at rest
- [ ] Configure audit logging

### Infrastructure Checklist
- [ ] Provision production servers/VMs
- [ ] Configure DNS records
- [ ] Set up load balancer (nginx/traefik/AWS ALB)
- [ ] Configure backup storage (S3/NFS/backup server)
- [ ] Set up monitoring alerts (PagerDuty/Opsgenie)
- [ ] Configure log aggregation (ELK/CloudWatch)
- [ ] Test disaster recovery procedures

### Application Checklist
- [ ] Review and test all Docker images
- [ ] Configure production environment variables
- [ ] Set up database connection pooling
- [ ] Configure CORS whitelist for production domains
- [ ] Set appropriate rate limits
- [ ] Configure email/SMS for notifications
- [ ] Test all health check endpoints

### Documentation Checklist
- [ ] Document production architecture
- [ ] Create runbook for common operations
- [ ] Document incident response procedures
- [ ] Train operations team
- [ ] Document backup and restore procedures

## Environment Configuration

Create a production `.env` file. See [ENVIRONMENT_CONFIGURATION.md](./ENVIRONMENT_CONFIGURATION.md) for detailed configuration options.

**Production .env Template:**

```bash
# Database Configuration
POSTGRES_DB=bcm_platform
POSTGRES_USER=bcm_user
POSTGRES_PASSWORD=<SECURE_PASSWORD_FROM_VAULT>
DATABASE_URL=postgresql+asyncpg://bcm_user:<PASSWORD>@postgres:5432/bcm_platform

# Redis Configuration
REDIS_URL=redis://:redis_password@redis:6379/0

# JWT Configuration (RSA 4096-bit keys)
JWT_PUBLIC_KEY=<BASE64_ENCODED_PUBLIC_KEY>
JWT_PRIVATE_KEY=<BASE64_ENCODED_PRIVATE_KEY>
JWT_ALGORITHM=RS256
JWT_EXPIRATION_HOURS=24

# Service Configuration
PLANNING_SERVICE_URL=http://planning-service:8011
PLANS_SERVICE_URL=http://plans-service:8023
BIA_SERVICE_URL=http://bia-service:8012
COMPLIANCE_SERVICE_URL=http://compliance-service:8014

# CORS Configuration
ALLOWED_ORIGINS=https://bcm.yourdomain.com,https://app.yourdomain.com

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_PERIOD=3600

# Monitoring
ALERT_EMAIL=alerts@yourdomain.com
PAGERDUTY_API_KEY=<PAGERDUTY_KEY>

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Environment
ENVIRONMENT=production
```

## Database Setup

Detailed database setup instructions are in [DATABASE_SETUP.md](./DATABASE_SETUP.md).

### Quick Database Setup

```bash
# 1. Start PostgreSQL container
docker-compose up -d postgres

# 2. Wait for PostgreSQL to be ready
docker-compose exec postgres pg_isready -U bcm_user

# 3. Create databases (handled by init script)
# The init-databases.sh script creates: planning, plans, governance, risk, response, learning

# 4. Run migrations (will be created by services on first start)
docker-compose up -d planning-service plans-service bia-service compliance-service

# 5. Verify databases
docker-compose exec postgres psql -U bcm_user -d bcm_platform -c "\l"
```

## Service Deployment

### Step 1: Build Docker Images

```bash
# Navigate to platform directory
cd /Users/MD/AI-Platform-ISO/platform-services

# Build all service images
docker-compose build

# Tag images for production
docker tag platform-services-planning-service:latest bcm/planning-service:1.0.0
docker tag platform-services-plans-service:latest bcm/plans-service:1.0.0
docker tag platform-services-bia-service:latest bcm/bia-service:1.0.0
docker tag platform-services-compliance-service:latest bcm/compliance-service:1.0.0

# Optional: Push to private registry
docker push your-registry.com/bcm/planning-service:1.0.0
docker push your-registry.com/bcm/plans-service:1.0.0
docker push your-registry.com/bcm/bia-service:1.0.0
docker push your-registry.com/bcm/compliance-service:1.0.0
```

### Step 2: Deploy Infrastructure Services

```bash
# Start infrastructure services first
docker-compose up -d postgres redis eventbus

# Wait for health checks to pass
docker-compose ps

# Verify connectivity
docker-compose exec redis redis-cli ping
docker-compose exec postgres pg_isready -U bcm_user
```

### Step 3: Deploy Application Services

```bash
# Deploy services in dependency order
docker-compose up -d planning-service

# Wait for planning service to be healthy
sleep 30

# Deploy dependent services
docker-compose up -d plans-service bia-service compliance-service

# Deploy monitoring
docker-compose up -d monitoring-service prometheus grafana
```

### Step 4: Verify Deployment

```bash
# Check all services are running
docker-compose ps

# Check health endpoints
curl http://localhost:8011/health  # Planning Service
curl http://localhost:8023/health  # Plans Service
curl http://localhost:8012/health  # BIA Service
curl http://localhost:8014/health  # Compliance Service
curl http://localhost:8045/health  # Monitoring Service

# Check logs for errors
docker-compose logs --tail=50 planning-service
docker-compose logs --tail=50 plans-service
docker-compose logs --tail=50 bia-service
docker-compose logs --tail=50 compliance-service
```

## Health Checks and Verification

### Service Health Checks

Each service exposes a `/health` endpoint:

```bash
#!/bin/bash
# health_check.sh

SERVICES=(
    "planning-service:8011"
    "plans-service:8023"
    "bia-service:8012"
    "compliance-service:8014"
    "monitoring-service:8045"
)

echo "Checking service health..."
for service in "${SERVICES[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -f -s http://localhost:$port/health > /dev/null; then
        echo "✓ $name is healthy"
    else
        echo "✗ $name is unhealthy"
    fi
done
```

### Database Health Check

```bash
# PostgreSQL connection
docker-compose exec postgres pg_isready -U bcm_user -d bcm_platform

# Check database size
docker-compose exec postgres psql -U bcm_user -d bcm_platform -c "
    SELECT pg_database.datname,
           pg_size_pretty(pg_database_size(pg_database.datname)) AS size
    FROM pg_database;"

# Check active connections
docker-compose exec postgres psql -U bcm_user -d bcm_platform -c "
    SELECT count(*) FROM pg_stat_activity;"
```

### Redis Health Check

```bash
# Redis ping
docker-compose exec redis redis-cli ping

# Check Redis memory
docker-compose exec redis redis-cli INFO memory

# Check Redis stats
docker-compose exec redis redis-cli INFO stats
```

## Monitoring Setup

See [MONITORING_GUIDE.md](./MONITORING_GUIDE.md) for comprehensive monitoring setup.

### Quick Monitoring Setup

1. **Access Grafana**: http://localhost:3000
   - Default username: admin
   - Default password: admin (CHANGE THIS)

2. **Import Dashboards**:
   - BCM Platform Overview
   - Service Metrics
   - Database Performance
   - System Resources

3. **Configure Alerts**:
   - Service down alerts
   - High error rate alerts
   - Database connection alerts
   - Disk space alerts

### Prometheus Metrics

Access Prometheus at http://localhost:9090

**Key Metrics to Monitor:**
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `db_connections_active` - Active database connections
- `redis_hits_total` - Redis cache hit rate
- `service_health_status` - Service health (1=healthy, 0=unhealthy)

## Backup and Disaster Recovery

See [BACKUP_DR_GUIDE.md](./BACKUP_DR_GUIDE.md) for detailed backup procedures.

### Quick Backup

```bash
# Database backup
docker-compose exec postgres pg_dump -U bcm_user bcm_platform > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup volumes
docker run --rm -v platform-services_postgres_data:/data -v $(pwd)/backups:/backup ubuntu tar czf /backup/postgres_data_$(date +%Y%m%d).tar.gz /data

# Backup environment and configs
tar czf config_backup_$(date +%Y%m%d).tar.gz .env docker-compose.yml monitoring/
```

### Quick Restore

```bash
# Restore database
cat backup_20241003_120000.sql | docker-compose exec -T postgres psql -U bcm_user bcm_platform

# Restart services
docker-compose restart
```

## Troubleshooting

See [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md) for comprehensive troubleshooting.

### Common Issues

**Service won't start:**
```bash
# Check logs
docker-compose logs service-name

# Check dependencies
docker-compose ps

# Restart service
docker-compose restart service-name
```

**Database connection errors:**
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check connection string
docker-compose exec planning-service env | grep DATABASE_URL

# Test connection
docker-compose exec postgres psql -U bcm_user -d bcm_platform -c "SELECT 1"
```

**High memory usage:**
```bash
# Check container stats
docker stats

# Check PostgreSQL memory
docker-compose exec postgres psql -U bcm_user -c "SHOW shared_buffers"

# Adjust memory limits in docker-compose.yml
```

## Post-Deployment Tasks

### 1. Verify All Services

```bash
# Run comprehensive health check
./docs/deployment/scripts/health_check.sh

# Check service versions
curl http://localhost:8011/version
curl http://localhost:8023/version
```

### 2. Configure Monitoring Alerts

- Set up PagerDuty/Opsgenie integration
- Configure alert thresholds
- Test alert delivery

### 3. Performance Baseline

```bash
# Capture initial metrics
curl http://localhost:9090/api/v1/query?query=up

# Run load test (if applicable)
# ab -n 1000 -c 10 http://localhost:8011/health
```

### 4. Documentation

- Document deployment date and version
- Update runbook with any deviations
- Schedule team training

### 5. Security Hardening

- Disable unnecessary ports
- Configure fail2ban for SSH
- Set up log monitoring for security events
- Schedule security audit

## Rollback Procedures

### Quick Rollback

```bash
# Stop current services
docker-compose down

# Restore previous version
docker-compose pull  # or use specific image tags
docker-compose up -d

# Restore database if needed
cat backup_previous.sql | docker-compose exec -T postgres psql -U bcm_user bcm_platform

# Verify services
./docs/deployment/scripts/health_check.sh
```

### Zero-Downtime Rollback

For zero-downtime rollbacks, use blue-green deployment strategy (see [CICD_PIPELINE.md](./CICD_PIPELINE.md)).

## Related Documentation

- [Environment Configuration](./ENVIRONMENT_CONFIGURATION.md)
- [Database Setup](./DATABASE_SETUP.md)
- [Docker Deployment](./DOCKER_DEPLOYMENT.md)
- [Kubernetes Deployment](./KUBERNETES_DEPLOYMENT.md)
- [Security Guide](./SECURITY_GUIDE.md)
- [Monitoring Guide](./MONITORING_GUIDE.md)
- [Backup and DR Guide](./BACKUP_DR_GUIDE.md)
- [CI/CD Pipeline](./CICD_PIPELINE.md)
- [Production Checklist](./PRODUCTION_CHECKLIST.md)
- [Maintenance Guide](./MAINTENANCE_GUIDE.md)
- [Troubleshooting Guide](./TROUBLESHOOTING_GUIDE.md)
- [Performance Tuning](./PERFORMANCE_TUNING.md)
- [Scaling Guide](./SCALING_GUIDE.md)

## Support and Contacts

**Emergency Contacts:**
- On-Call Engineer: [Phone/Email]
- Backup On-Call: [Phone/Email]
- Platform Team Lead: [Email]

**Support Channels:**
- Slack: #bcm-platform-support
- Email: platform-support@yourdomain.com
- Incident Management: [PagerDuty/Opsgenie URL]

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2024-10-03 | Initial production deployment guide | BCM Platform Team |

---

**Last Updated:** 2024-10-03
**Document Owner:** Platform Engineering Team
**Review Schedule:** Quarterly
