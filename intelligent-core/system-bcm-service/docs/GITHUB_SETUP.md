# GitHub Setup Guide for System BCM Service

**Generated**: 2025-10-09
**Version**: 1.0.0

## Overview

This guide explains how to set up the GitHub repository for System BCM Service with complete CI/CD automation.

## Prerequisites

- GitHub account with repository access
- GitHub CLI installed (`brew install gh`) or manual setup via web

## Step 1: Repository Setup

### Option A: Using GitHub CLI (Recommended)

```bash
# Navigate to project directory
cd /Users/MD/AI-Platform-ISO/intelligent-core/system-bcm-service

# Initialize git if not already done
git init

# Create GitHub repository
gh repo create AI-Platform-ISO/system-bcm-service \
  --public \
  --description "Self-learning BCM platform that applies BCM to itself first" \
  --source=. \
  --remote=origin

# Push initial code
git add .
git commit -m "feat: Initial System BCM Service implementation"
git push -u origin main
```

### Option B: Manual Setup via GitHub Web

1. Go to https://github.com/new
2. Repository name: `system-bcm-service`
3. Description: "Self-learning BCM platform that applies BCM to itself first"
4. Visibility: Public (or Private)
5. Click "Create repository"

```bash
# Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/system-bcm-service.git
git branch -M main
git add .
git commit -m "feat: Initial System BCM Service implementation"
git push -u origin main
```

## Step 2: Branch Protection Rules

### Configure Main Branch Protection

Using GitHub CLI:
```bash
gh api repos/AI-Platform-ISO/system-bcm-service/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["code-quality","unit-tests","integration-tests","performance-tests","security-scan"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1}' \
  --field restrictions=null
```

Or via GitHub Web:
1. Go to: Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Check:
   - ✅ Require a pull request before merging
   - ✅ Require approvals (1)
   - ✅ Require status checks to pass before merging
     - code-quality
     - unit-tests
     - integration-tests
     - performance-tests
     - security-scan
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators
4. Save changes

### Configure Develop Branch Protection

```bash
gh api repos/AI-Platform-ISO/system-bcm-service/branches/develop/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["code-quality","unit-tests"]}' \
  --field enforce_admins=false \
  --field required_pull_request_reviews=null \
  --field restrictions=null
```

## Step 3: GitHub Secrets Configuration

### Required Secrets for CI/CD

Add these secrets via GitHub CLI or web interface:

```bash
# Using GitHub CLI
gh secret set DOCKER_USERNAME --body "your-dockerhub-username"
gh secret set DOCKER_PASSWORD --body "your-dockerhub-password"
gh secret set POSTGRES_PASSWORD --body "your-secure-postgres-password"
gh secret set REDIS_PASSWORD --body "your-secure-redis-password"
gh secret set GRAFANA_API_KEY --body "your-grafana-api-key"
gh secret set SLACK_WEBHOOK_URL --body "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
gh secret set PRODUCTION_SERVER --body "user@production-server.com"
gh secret set SSH_PRIVATE_KEY --body "$(cat ~/.ssh/id_rsa)"
```

Or via GitHub Web:
1. Go to: Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DOCKER_USERNAME` | Docker Hub username | `myusername` |
| `DOCKER_PASSWORD` | Docker Hub password/token | `dckr_pat_xxxxx` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `SecurePass123!` |
| `REDIS_PASSWORD` | Redis password | `RedisPass456!` |
| `GRAFANA_API_KEY` | Grafana API key | `glsa_xxxxx` |
| `SLACK_WEBHOOK_URL` | Slack notifications | `https://hooks.slack.com/...` |
| `PRODUCTION_SERVER` | Production server SSH | `user@prod.example.com` |
| `SSH_PRIVATE_KEY` | SSH key for deployment | `-----BEGIN RSA PRIVATE KEY-----...` |

### Optional Secrets

| Secret Name | Description | When Needed |
|-------------|-------------|-------------|
| `PAGERDUTY_INTEGRATION_KEY` | PagerDuty alerts | If using PagerDuty |
| `EMAIL_SMTP_PASSWORD` | Email notifications | If using email alerts |
| `OAUTH2_CLIENT_SECRET` | OAuth2 authentication | If using OAuth2 |

## Step 4: GitHub Actions Workflow

The workflow is already configured in `.github/workflows/ci-cd.yml`.

### Verify Workflow

```bash
# Check workflow syntax
gh workflow list

# View workflow runs
gh run list --workflow=ci-cd.yml

# Watch latest run
gh run watch
```

### Workflow Triggers

- **Push to `main`**: Full CI/CD + Production deployment
- **Push to `develop`**: Full CI/CD + Staging deployment
- **Pull Request**: CI only (no deployment)
- **Manual**: Via GitHub Actions UI

### Trigger Manual Workflow

```bash
gh workflow run ci-cd.yml
```

## Step 5: Repository Settings

### Topics (for discoverability)

```bash
gh repo edit --add-topic bcm
gh repo edit --add-topic business-continuity
gh repo edit --add-topic iso-22301
gh repo edit --add-topic fastapi
gh repo edit --add-topic python
gh repo edit --add-topic docker
gh repo edit --add-topic ai
gh repo edit --add-topic self-learning
gh repo edit --add-topic prometheus
gh repo edit --add-topic grafana
```

### About Section

```bash
gh repo edit \
  --description "Self-learning BCM platform that applies BCM to itself first" \
  --homepage "https://system-bcm.example.com"
```

## Step 6: Create Initial Issues

Create issues for tracking:

```bash
# Feature tracking
gh issue create \
  --title "Implement real-time dashboard" \
  --body "Create web UI for monitoring BCM cycles and recovery executions" \
  --label "enhancement,frontend"

gh issue create \
  --title "Add machine learning for pattern detection" \
  --body "Implement ML models for anomaly detection in platform behavior" \
  --label "enhancement,ai"

# Documentation
gh issue create \
  --title "Complete API documentation" \
  --body "Add OpenAPI/Swagger documentation for all endpoints" \
  --label "documentation"
```

## Step 7: Create Project Board

Using GitHub CLI:
```bash
gh project create --owner AI-Platform-ISO --title "System BCM Development"
```

Or via web:
1. Go to Projects → New project
2. Template: Board
3. Columns: Backlog, In Progress, Review, Done
4. Link repository

## Step 8: Configure Dependabot

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "your-username"
    labels:
      - "dependencies"
      - "python"

  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    reviewers:
      - "your-username"
    labels:
      - "dependencies"
      - "docker"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    reviewers:
      - "your-username"
    labels:
      - "dependencies"
      - "github-actions"
```

## Step 9: Create README.md for GitHub

Create a comprehensive README that will be displayed on GitHub:

```bash
# Copy the main README
cp README.md README.github.md

# Edit to add badges, links, etc.
```

## Step 10: Set up GitHub Pages (Optional)

For documentation hosting:

```bash
gh api repos/AI-Platform-ISO/system-bcm-service/pages \
  --method POST \
  --field source='{"branch":"main","path":"/docs"}'
```

## Verification Checklist

After setup, verify:

- [ ] Repository created and code pushed
- [ ] Main branch protection enabled
- [ ] Develop branch protection enabled
- [ ] All secrets configured
- [ ] GitHub Actions workflow running successfully
- [ ] Topics added
- [ ] About section configured
- [ ] Initial issues created
- [ ] Project board created
- [ ] Dependabot configured
- [ ] README displays correctly

## Quick Commands

```bash
# Clone repository
git clone https://github.com/AI-Platform-ISO/system-bcm-service.git
cd system-bcm-service

# Create feature branch
git checkout -b feature/your-feature

# Push and create PR
git push -u origin feature/your-feature
gh pr create --fill

# View CI/CD status
gh run list --limit 5

# View open PRs
gh pr list

# Merge PR after approval
gh pr merge --squash --delete-branch
```

## Troubleshooting

### Workflow Not Triggering

```bash
# Check workflow file syntax
gh workflow view ci-cd.yml

# Check recent runs
gh run list --limit 10

# View specific run logs
gh run view <run-id> --log
```

### Secret Not Found

```bash
# List all secrets
gh secret list

# Update secret
gh secret set SECRET_NAME --body "new-value"
```

### Branch Protection Issues

```bash
# View current protection
gh api repos/AI-Platform-ISO/system-bcm-service/branches/main/protection

# Disable temporarily (not recommended)
gh api repos/AI-Platform-ISO/system-bcm-service/branches/main/protection --method DELETE
```

## Integration with AI-Platform-ISO

This repository is part of the larger AI-Platform-ISO ecosystem:

```bash
# Link to main platform repository
gh repo edit --add-topic ai-platform-iso

# Reference in platform documentation
# Add to: /Users/MD/AI-Platform-ISO/docs/PLATFORM_ARCHITECTURE_MAP.md
```

## Continuous Monitoring

Set up GitHub Actions status badge in README:

```markdown
![CI/CD](https://github.com/AI-Platform-ISO/system-bcm-service/actions/workflows/ci-cd.yml/badge.svg)
```

## Next Steps

1. **Enable GitHub Advanced Security** (if available)
   - Code scanning
   - Secret scanning
   - Dependency review

2. **Set up GitHub Discussions**
   - Community Q&A
   - Feature requests
   - Announcements

3. **Configure Webhooks**
   - Slack notifications
   - Custom integrations

4. **Set up GitHub Insights**
   - Track contributor activity
   - Monitor repository health
   - Analyze code frequency

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
