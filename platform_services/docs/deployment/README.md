# BCM Platform Deployment Documentation

## Quick Start

For production deployment, follow these steps in order:

1. **[Production Checklist](./PRODUCTION_CHECKLIST.md)** - Complete all pre-deployment tasks
2. **[Environment Configuration](./ENVIRONMENT_CONFIGURATION.md)** - Configure environment variables
3. **[Database Setup](./DATABASE_SETUP.md)** - Set up PostgreSQL databases
4. **[Security Guide](./SECURITY_GUIDE.md)** - Implement security measures
5. **[Docker Deployment](./DOCKER_DEPLOYMENT.md)** - Deploy with Docker Compose
6. **[Deployment Guide](./DEPLOYMENT_GUIDE.md)** - Main deployment procedures

## Documentation Index

### Core Guides
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** (556 lines)
  - Complete deployment procedures
  - Architecture overview
  - Health checks and verification
  - Post-deployment tasks

- **[ENVIRONMENT_CONFIGURATION.md](./ENVIRONMENT_CONFIGURATION.md)** (693 lines)
  - All environment variables
  - Secret management (Vault, AWS)
  - Service-specific configuration
  - Production .env template

- **[DATABASE_SETUP.md](./DATABASE_SETUP.md)** (810 lines)
  - PostgreSQL installation
  - Database creation
  - User permissions
  - Performance tuning
  - Backup configuration

### Deployment Methods
- **[DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)** (903 lines)
  - Docker installation
  - Image building and management
  - Container orchestration
  - Volume and network configuration
  - Security best practices

- **[CICD_PIPELINE.md](./CICD_PIPELINE.md)** (396 lines)
  - GitHub Actions workflows
  - Automated deployment
  - Rollback procedures
  - Deployment strategies

### Security & Compliance
- **[SECURITY_GUIDE.md](./SECURITY_GUIDE.md)** (777 lines)
  - JWT authentication
  - SSL/TLS configuration
  - Secret management
  - Network security
  - Audit logging

### Operations
- **[PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md)** (381 lines)
  - Pre-deployment checklist
  - Deployment execution steps
  - Post-deployment verification
  - Rollback checklist

- **[TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md)** (432 lines)
  - Common issues and solutions
  - Diagnostic commands
  - Emergency procedures

## Deployment Scripts

All scripts are located in `docs/deployment/scripts/` and have been validated for syntax:

- **[deploy.sh](./scripts/deploy.sh)** (417 lines)
  - Automated deployment
  - Pre-flight checks
  - Backup before deployment
  - Health verification
  - Automatic rollback on failure

- **[backup.sh](./scripts/backup.sh)** (320 lines)
  - Database backup
  - Volume backup
  - Configuration backup
  - S3 upload support
  - Automated cleanup

- **[restore.sh](./scripts/restore.sh)** (390 lines)
  - Restore from backup
  - Pre-restore backup
  - Verification steps

- **[health_check.sh](./scripts/health_check.sh)** (288 lines)
  - Service health checks
  - Database connectivity
  - System resources
  - JSON output support

### Using the Scripts

```bash
# Make scripts executable (already done)
chmod +x docs/deployment/scripts/*.sh

# Deploy to production
./docs/deployment/scripts/deploy.sh v1.0.0

# Backup all data
./docs/deployment/scripts/backup.sh full

# Restore from backup
./docs/deployment/scripts/restore.sh 20241003_120000

# Check system health
./docs/deployment/scripts/health_check.sh --verbose
```

## GitHub Actions Workflows

Located in `.github/workflows/`:

- **[ci.yml](./.github/workflows/ci.yml)** (197 lines)
  - Continuous Integration
  - Linting and testing
  - Security scanning
  - Integration tests

- **[deploy.yml](./.github/workflows/deploy.yml)** (231 lines)
  - Automated deployment
  - Staging and production
  - Health checks
  - Rollback on failure

## Production Configuration

- **[docker-compose.prod.yml](../../docker-compose.prod.yml)** (515 lines)
  - Production-ready Docker Compose
  - Resource limits
  - Health checks
  - Security hardening
  - Logging configuration

## Quick Commands

### Deployment
```bash
# Production deployment with script
./docs/deployment/scripts/deploy.sh v1.0.0

# Manual deployment
docker compose -f docker-compose.prod.yml up -d
./docs/deployment/scripts/health_check.sh
```

### Backup & Restore
```bash
# Full backup
./docs/deployment/scripts/backup.sh full

# Database only
./docs/deployment/scripts/backup.sh database

# Restore
./docs/deployment/scripts/restore.sh <timestamp>
```

### Monitoring
```bash
# Health check
./docs/deployment/scripts/health_check.sh

# View logs
docker compose logs -f

# Resource usage
docker stats
```

### Troubleshooting
```bash
# Check service status
docker compose ps

# View specific service logs
docker compose logs planning-service

# Restart service
docker compose restart planning-service

# Complete restart
docker compose down
docker compose up -d
```

## Environment Setup

### Required Environment Variables

Minimum required for production:

```bash
# Database
POSTGRES_PASSWORD=<secure_password>

# JWT
JWT_PUBLIC_KEY=<base64_encoded_public_key>

# Redis
REDIS_PASSWORD=<secure_password>

# Grafana
GRAFANA_ADMIN_PASSWORD=<secure_password>

# Monitoring
ALERT_EMAIL=alerts@yourdomain.com
```

See [ENVIRONMENT_CONFIGURATION.md](./ENVIRONMENT_CONFIGURATION.md) for complete list.

## Pre-Deployment Checklist

Essential tasks before deployment:

- [ ] Generate JWT keys (RSA 4096)
- [ ] Configure secrets in Vault/AWS Secrets Manager
- [ ] Obtain SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring alerts
- [ ] Test backup and restore
- [ ] Review security hardening
- [ ] Complete [PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md)

## Architecture Overview

```
┌─────────────────────────────────────────┐
│     Load Balancer (nginx/traefik)       │
│              SSL/TLS                     │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌──────▼────────┐
│  Planning      │  │   Plans       │
│  Service:8011  │  │   Service:8023│
└───────┬────────┘  └──────┬────────┘
        │                   │
        └─────────┬─────────┘
                  │
        ┌─────────▼─────────┐
        │   PostgreSQL      │
        │   Redis           │
        └───────────────────┘
```

## Support and Contacts

- **Documentation Issues:** Open GitHub issue
- **Production Support:** platform-support@yourdomain.com
- **Emergency:** Check PagerDuty or contact on-call engineer

## Related Documentation

- [Main README](../../README.md)
- [API Documentation](../api/)
- [Architecture Documentation](../../ARCHITECTURE.md)

## Document Statistics

**Total Documentation:**
- 8 Markdown guides
- 4 Shell scripts
- 2 GitHub Actions workflows
- 1 Production Docker Compose file

**Total Lines:** 6,791 lines of documentation and automation

**Last Updated:** 2024-10-03

---

**Quick Links:**
- [Start Here: Production Checklist](./PRODUCTION_CHECKLIST.md)
- [Security First: Security Guide](./SECURITY_GUIDE.md)
- [Deploy Now: Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Problems? Troubleshooting Guide](./TROUBLESHOOTING_GUIDE.md)
