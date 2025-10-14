# CI/CD Pipeline Guide

## Overview

The BCM Platform uses GitHub Actions for continuous integration and deployment. The pipeline includes automated testing, security scanning, Docker image building, and deployment to staging/production.

## Pipeline Architecture

```
┌──────────────┐
│  Git Push    │
│  /PR Created │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│         CI Pipeline (ci.yml)         │
├──────────────────────────────────────┤
│  1. Lint & Test (Python)             │
│  2. Build Docker Images              │
│  3. Security Scan (Trivy)            │
│  4. Integration Tests                │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│    Deploy Pipeline (deploy.yml)      │
├──────────────────────────────────────┤
│  1. Build & Push to Registry         │
│  2. Deploy to Staging (optional)     │
│  3. Deploy to Production (on tag)    │
│  4. Post-deployment Monitoring       │
└──────────────────────────────────────┘
```

## Workflows

### CI Workflow (.github/workflows/ci.yml)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs:**

1. **lint-and-test**
   - Code formatting (Black)
   - Import sorting (isort)
   - Linting (Pylint)
   - Security scan (Bandit)
   - Dependency check (Safety)
   - Unit tests (pytest)
   - Coverage report

2. **build-images**
   - Build Docker images for all services
   - Push to container registry
   - Use build cache for speed

3. **security-scan**
   - Trivy vulnerability scanner
   - Upload results to GitHub Security

4. **integration-tests**
   - Spin up PostgreSQL and Redis
   - Run full integration tests

### Deploy Workflow (.github/workflows/deploy.yml)

**Triggers:**
- Push tags matching `v*.*.*` (e.g., v1.0.0)
- Manual workflow dispatch

**Jobs:**

1. **build-and-push**
   - Build production images
   - Tag with version numbers
   - Push to registry (ghcr.io)

2. **deploy-staging**
   - Deploy to staging environment
   - Run health checks
   - Send Slack notification

3. **deploy-production**
   - Backup current production
   - Deploy new version
   - Run smoke tests
   - Rollback on failure
   - Create GitHub release

4. **post-deployment-monitoring**
   - Monitor health for 10 minutes
   - Check error rates
   - Alert on issues

## Setup Instructions

### 1. Configure Secrets

Add these secrets in GitHub Settings > Secrets and variables > Actions:

**Required Secrets:**
```
GITHUB_TOKEN                    # Auto-provided by GitHub
STAGING_SSH_KEY                 # SSH private key for staging server
STAGING_HOST                    # Staging server hostname
STAGING_USER                    # SSH user for staging
PRODUCTION_SSH_KEY              # SSH private key for production
PRODUCTION_HOST                 # Production server hostname
PRODUCTION_USER                 # SSH user for production
SLACK_WEBHOOK                   # Slack webhook URL for notifications
```

**Optional Secrets:**
```
DOCKER_REGISTRY_USER            # If using private registry
DOCKER_REGISTRY_PASSWORD        # Registry password
CODECOV_TOKEN                   # For code coverage reports
```

### 2. Configure Environments

In GitHub Settings > Environments, create:

**Staging Environment:**
- Protection rules: None (auto-deploy on develop)
- URL: https://staging.bcm.yourdomain.com

**Production Environment:**
- Protection rules: Required reviewers (1-2 approvers)
- URL: https://bcm.yourdomain.com
- Deployment branch rules: Only tagged releases

### 3. Server Setup

On deployment servers (staging/production):

```bash
# 1. Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Add deployment user
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy

# 3. Setup SSH key
sudo -u deploy mkdir -p ~/.ssh
echo "YOUR_PUBLIC_KEY" | sudo -u deploy tee ~/.ssh/authorized_keys
sudo chmod 600 ~deploy/.ssh/authorized_keys

# 4. Clone repository
sudo -u deploy git clone https://github.com/your-org/platform-services.git /opt/bcm-platform
cd /opt/bcm-platform

# 5. Configure environment
sudo -u deploy cp .env.example .env
sudo -u deploy vim .env  # Configure production values
```

## Manual Deployment

### Using GitHub UI

1. Go to Actions tab
2. Select "Deploy to Production" workflow
3. Click "Run workflow"
4. Choose environment (staging/production)
5. Monitor progress

### Using Git Tags

```bash
# Tag release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# This automatically triggers production deployment
```

### Manual SSH Deployment

```bash
# SSH to production server
ssh deploy@production-server

# Navigate to project
cd /opt/bcm-platform

# Pull latest code
git pull origin main

# Run deployment script
./docs/deployment/scripts/deploy.sh v1.0.0
```

## Deployment Strategies

### Blue-Green Deployment

```bash
# On server, configure two environments
# blue = current, green = new

# Deploy to green environment
docker compose -f docker-compose.green.yml up -d

# Switch nginx to green
sudo ln -sf /etc/nginx/sites-available/green /etc/nginx/sites-enabled/bcm
sudo nginx -s reload

# Keep blue running for quick rollback
# After verification, remove blue
docker compose -f docker-compose.blue.yml down
```

### Canary Deployment

```nginx
# nginx config - route 10% traffic to new version
upstream backend {
    server planning-service-v1:8011 weight=9;
    server planning-service-v2:8011 weight=1;
}
```

### Rolling Update

```bash
# Update services one at a time
for service in planning-service plans-service bia-service compliance-service; do
    docker compose up -d --no-deps $service
    sleep 30
    curl -f http://localhost:${PORT}/health || exit 1
done
```

## Monitoring and Notifications

### Slack Integration

```yaml
# In workflow
- name: Notify deployment
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Email Notifications

Configure in GitHub Settings > Notifications or use workflow:

```yaml
- name: Send email
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 587
    username: ${{ secrets.SMTP_USERNAME }}
    password: ${{ secrets.SMTP_PASSWORD }}
    subject: Deployment ${{ job.status }}
    to: team@yourdomain.com
    from: github-actions@yourdomain.com
    body: Deployment to production ${{ job.status }}
```

## Rollback Procedures

### Automatic Rollback

The deploy workflow includes automatic rollback on failure:

```yaml
- name: Rollback on failure
  if: failure()
  run: |
    ssh ${{ secrets.PRODUCTION_USER }}@${{ secrets.PRODUCTION_HOST }} << 'EOF'
      cd /opt/bcm-platform
      ./docs/deployment/scripts/restore.sh $(ls -t /var/backups/bcm/database/backup_* | head -1) --no-confirm
    EOF
```

### Manual Rollback

```bash
# 1. Find previous successful tag
git tag -l --sort=-v:refname | head -5

# 2. Redeploy previous version
git checkout v1.0.0
./docs/deployment/scripts/deploy.sh v1.0.0

# 3. Or use Docker tags
docker tag bcm/planning-service:v1.0.0 bcm/planning-service:latest
docker compose up -d
```

## Best Practices

### Version Tagging

```bash
# Use semantic versioning
git tag -a v1.0.0 -m "Major release"      # Breaking changes
git tag -a v1.1.0 -m "Feature release"    # New features
git tag -a v1.0.1 -m "Patch release"      # Bug fixes

# Always annotate tags
git tag -a -m "Description" v1.0.0

# Push tags
git push origin --tags
```

### Database Migrations

```yaml
# Include in deployment
- name: Run migrations
  run: |
    docker compose exec -T planning-service alembic upgrade head
```

### Feature Flags

```python
# Use feature flags for gradual rollout
FEATURE_FLAGS = {
    "advanced_analytics": os.getenv("FEATURE_ADVANCED_ANALYTICS", "false").lower() == "true",
    "new_ui": os.getenv("FEATURE_NEW_UI", "false").lower() == "true"
}
```

### Deployment Windows

- **Staging:** Anytime
- **Production:** Tuesday-Thursday, 10 AM - 4 PM
- **Avoid:** Mondays, Fridays, weekends, holidays

## Troubleshooting

### Workflow Fails

```bash
# Check workflow logs in GitHub Actions UI

# Re-run failed jobs
# GitHub UI > Actions > Select workflow > Re-run failed jobs

# Debug with SSH (tmate)
- name: Setup tmate session
  uses: mxschmitt/action-tmate@v3
  if: failure()
```

### Deployment Fails

```bash
# SSH to server and check logs
ssh deploy@production-server
cd /opt/bcm-platform
docker compose logs

# Check deployment script logs
tail -f /var/log/bcm/deployment.log

# Manual health check
./docs/deployment/scripts/health_check.sh
```

### Image Pull Fails

```bash
# Login to registry
docker login ghcr.io

# Pull specific version
docker pull ghcr.io/your-org/platform-services/planning-service:v1.0.0

# Check registry permissions
# Ensure GITHUB_TOKEN has packages:read permission
```

## Related Documentation

- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Docker Deployment](./DOCKER_DEPLOYMENT.md)
- [Production Checklist](./PRODUCTION_CHECKLIST.md)

---

**Last Updated:** 2024-10-03
