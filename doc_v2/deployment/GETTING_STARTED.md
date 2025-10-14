# Getting Started with AI-Platform-ISO

**Document Type:** Quick Start Guide
**Target Audience:** Developers, System Administrators, Implementation Teams
**Purpose:** Installation and initial configuration instructions
**Version:** 1.0.0
**Last Updated:** 2025-10-09

---

## Overview

This guide provides step-by-step instructions for installing, configuring, and running the AI-Platform-ISO system. By the end of this guide, you will have a fully functional platform instance running locally or in a development environment.

**Estimated Time:** 45-60 minutes

**What You'll Accomplish:**
- Install all prerequisites and dependencies
- Configure environment variables and API keys
- Deploy infrastructure services
- Initialize the database schema
- Start platform services
- Verify installation with health checks
- Run your first business continuity workflow

---

## Prerequisites

### System Requirements

**Hardware Requirements (Minimum):**
- CPU: 4 cores (8 cores recommended)
- RAM: 16 GB (32 GB recommended for production)
- Storage: 50 GB available disk space (SSD recommended)
- Network: Stable internet connection for AI API calls

**Operating System:**
- Linux (Ubuntu 22.04 LTS or later)
- macOS (12.0 Monterey or later)
- Windows 10/11 with WSL2 (Ubuntu distribution)

### Software Prerequisites

**Required Software:**

1. **Docker** (Version 24.0 or later)
   ```bash
   # Verify installation
   docker --version
   # Expected: Docker version 24.0.0 or higher
   ```
   Installation: https://docs.docker.com/get-docker/

2. **Docker Compose** (Version 2.0 or later)
   ```bash
   # Verify installation
   docker-compose --version
   # Expected: Docker Compose version 2.0.0 or higher
   ```

3. **Python** (Version 3.11 or later)
   ```bash
   # Verify installation
   python3 --version
   # Expected: Python 3.11.0 or higher
   ```
   Installation: https://www.python.org/downloads/

4. **Node.js** (Version 18 or later, for frontend development)
   ```bash
   # Verify installation
   node --version
   # Expected: v18.0.0 or higher
   ```
   Installation: https://nodejs.org/

5. **Git** (Latest version)
   ```bash
   # Verify installation
   git --version
   ```

### Cloud Service Accounts

**Required Accounts:**

1. **Anthropic API** (Primary AI provider)
   - Sign up: https://console.anthropic.com/
   - Create API key
   - Recommended: Start with Pro tier for development

2. **Supabase** (Managed PostgreSQL and authentication)
   - Sign up: https://supabase.com/
   - Create new project
   - Note project URL and API keys

3. **Qdrant Cloud** (Vector database for RAG)
   - Sign up: https://cloud.qdrant.io/
   - Create cluster
   - Note cluster URL and API key

**Optional Accounts:**

4. **OpenAI API** (Secondary AI provider)
   - Sign up: https://platform.openai.com/
   - Create API key
   - Used as fallback for Anthropic Claude

---

## Installation Steps

### Step 1: Clone Repository

Clone the AI-Platform-ISO repository to your local machine:

```bash
# Clone via HTTPS
git clone https://github.com/your-org/AI-Platform-ISO.git

# Or clone via SSH
git clone git@github.com:your-org/AI-Platform-ISO.git

# Navigate to project directory
cd AI-Platform-ISO
```

Verify the repository structure:

```bash
ls -la
# Expected directories: docs/, infrastructure/, intelligent-core/, platform-services/, shared/
```

### Step 2: Configure Environment Variables

Create environment configuration file:

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env  # or use your preferred editor
```

**Required Configuration:**

```bash
# =============================================================================
# AI PROVIDER CONFIGURATION
# =============================================================================

# Anthropic Claude API (Primary)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI API (Optional fallback)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Supabase (PostgreSQL)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# PostgreSQL Connection (from Supabase settings)
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=  # Leave empty for local development

# =============================================================================
# VECTOR DATABASE CONFIGURATION
# =============================================================================

# Qdrant Cloud
QDRANT_URL=https://xxxxx.qdrant.io
QDRANT_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# =============================================================================
# PLATFORM CONFIGURATION
# =============================================================================

# Environment
ENVIRONMENT=development  # Options: development, staging, production

# API Gateway
API_GATEWAY_HOST=0.0.0.0
API_GATEWAY_PORT=8000

# JWT Secret (generate random string)
JWT_SECRET=your-secret-key-here-use-strong-random-string
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# =============================================================================
# MONITORING AND OBSERVABILITY
# =============================================================================

# Prometheus
PROMETHEUS_PORT=9090

# Grafana
GRAFANA_PORT=3001
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin  # Change in production

# =============================================================================
# OPTIONAL INTEGRATIONS
# =============================================================================

# Slack notifications (optional)
SLACK_WEBHOOK_URL=

# Email notifications (optional)
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
```

**Security Best Practices:**

```bash
# Generate strong JWT secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Ensure .env is in .gitignore
echo ".env" >> .gitignore
```

### Step 3: Install Python Dependencies

Create and activate virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows (WSL):
source venv/Scripts/activate

# Verify activation (prompt should show (venv))
which python3
# Expected: /path/to/AI-Platform-ISO/venv/bin/python3
```

Install dependencies:

```bash
# Upgrade pip
pip install --upgrade pip

# Install platform dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### Step 4: Start Infrastructure Services

The infrastructure layer provides foundation services (database, event bus, monitoring):

```bash
# Navigate to infrastructure directory
cd infrastructure

# Start infrastructure services
docker-compose -f docker-compose.full-infrastructure.yml up -d

# Verify services are running
docker-compose ps
```

**Expected Services:**

| Service | Port | Status |
|---------|------|--------|
| PostgreSQL | 5432 | Up |
| Redis | 6379 | Up |
| Prometheus | 9090 | Up |
| Grafana | 3001 | Up |

**Health Checks:**

```bash
# Check Redis
redis-cli ping
# Expected: PONG

# Check PostgreSQL
psql $DATABASE_URL -c "SELECT version();"

# Check Prometheus
curl http://localhost:9090/-/healthy
# Expected: Prometheus is Healthy.

# Check Grafana
curl http://localhost:3001/api/health
# Expected: {"database": "ok", ...}
```

### Step 5: Initialize Database Schema

Create database tables and seed initial data:

```bash
# Return to project root
cd ..

# Run database initialization script
python scripts/init_database.py

# Expected output:
# Creating database schema...
# Creating tables for platform_services...
# Creating tables for intelligent_core...
# Seeding reference data...
# Database initialization complete.
```

**Verify Database Schema:**

```bash
# Connect to database
psql $DATABASE_URL

# List tables
\dt

# Expected tables:
# organizations, users, roles, permissions
# bia_analyses, risk_assessments, continuity_plans
# compliance_requirements, audit_logs
# workflows, workflow_executions, workflow_states

# Exit psql
\q
```

### Step 6: Start Platform Services

Start the intelligent core and platform services:

```bash
# Start all services
docker-compose up -d

# Monitor logs
docker-compose logs -f

# Verify services
docker-compose ps
```

**Expected Services:**

| Service | Port | Description |
|---------|------|-------------|
| API Gateway | 8000 | Main API entry point |
| BIA Service | 8001 | Business Impact Analysis |
| Risk Service | 8002 | Risk Assessment |
| Compliance Service | 8003 | ISO 22301 Compliance |
| Workflow Engine | 8010 | Workflow orchestration |
| AI Foundation | 8020 | AI model orchestration |

### Step 7: Verify Installation

Run comprehensive health checks:

```bash
# Health check script
python scripts/health_check.py

# Or use API endpoint
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "ai_foundation": "healthy",
    "bia_service": "healthy",
    "risk_service": "healthy",
    "compliance_service": "healthy"
  },
  "timestamp": "2025-10-09T12:00:00Z"
}
```

**Access Platform Interfaces:**

1. **API Documentation (Swagger)**
   - URL: http://localhost:8000/docs
   - Interactive API exploration

2. **Grafana Dashboards**
   - URL: http://localhost:3001
   - Username: admin
   - Password: admin (as configured in .env)

3. **Prometheus Metrics**
   - URL: http://localhost:9090

---

## First Workflow: Business Impact Analysis

Now that your platform is running, let's execute your first workflow.

### Step 1: Create Organization

Create a test organization:

```bash
# Using curl
curl -X POST http://localhost:8000/api/v1/organizations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Organization",
    "industry": "Technology",
    "size": "medium",
    "country": "US"
  }'

# Expected response:
{
  "id": "org-123abc",
  "name": "Test Organization",
  "created_at": "2025-10-09T12:00:00Z"
}
```

Save the organization ID for subsequent requests.

### Step 2: Authenticate

Generate authentication token:

```bash
# Create user account
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@testorg.com",
    "password": "SecurePassword123!",
    "organization_id": "org-123abc",
    "role": "admin"
  }'

# Login and get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@testorg.com",
    "password": "SecurePassword123!"
  }'

# Expected response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

Save the access_token for API requests.

### Step 3: Execute Business Impact Analysis

Trigger AI-powered BIA:

```bash
# Set token variable
TOKEN="your-access-token-here"

# Start BIA analysis
curl -X POST http://localhost:8000/api/v1/bia/analysis \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "org-123abc",
    "scope": "full",
    "analysis_type": "automated",
    "include_dependencies": true
  }'

# Expected response:
{
  "analysis_id": "bia-456def",
  "status": "processing",
  "estimated_completion": "2025-10-09T12:15:00Z",
  "message": "BIA analysis initiated. AI is analyzing business processes..."
}
```

### Step 4: Monitor Analysis Progress

Check analysis status:

```bash
# Get analysis status
curl -X GET http://localhost:8000/api/v1/bia/analysis/bia-456def \
  -H "Authorization: Bearer $TOKEN"

# Expected response (in progress):
{
  "analysis_id": "bia-456def",
  "status": "processing",
  "progress": 65,
  "current_step": "Analyzing critical business functions",
  "steps_completed": ["Data collection", "Process mapping"],
  "steps_remaining": ["Impact assessment", "RTO/RPO calculation"]
}

# Expected response (completed):
{
  "analysis_id": "bia-456def",
  "status": "completed",
  "progress": 100,
  "results": {
    "critical_functions": 12,
    "supporting_functions": 28,
    "total_dependencies": 156,
    "average_rto_hours": 4,
    "average_rpo_hours": 1,
    "high_priority_risks": 5
  },
  "recommendations": [
    "Implement redundancy for critical function: Payment Processing",
    "Reduce RTO for Customer Support to 2 hours",
    "Document disaster recovery procedures for IT Infrastructure"
  ]
}
```

### Step 5: View BIA Results

Retrieve detailed results:

```bash
# Get full BIA report
curl -X GET http://localhost:8000/api/v1/bia/analysis/bia-456def/report \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json"

# Download PDF report
curl -X GET http://localhost:8000/api/v1/bia/analysis/bia-456def/report \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/pdf" \
  -o bia-report.pdf
```

**Congratulations!** You have successfully:
- Installed and configured AI-Platform-ISO
- Started all platform services
- Created an organization
- Executed your first AI-powered Business Impact Analysis

---

## Common Tasks

### Starting and Stopping Services

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart bia-service

# View logs
docker-compose logs -f bia-service

# View all service logs
docker-compose logs -f
```

### Database Management

```bash
# Connect to PostgreSQL
psql $DATABASE_URL

# Run migrations
python scripts/run_migrations.py

# Backup database
pg_dump $DATABASE_URL > backup.sql

# Restore database
psql $DATABASE_URL < backup.sql
```

### Monitoring and Debugging

```bash
# Check service health
curl http://localhost:8000/health

# View metrics
curl http://localhost:9090/api/v1/query?query=up

# Check logs for specific service
docker-compose logs -f api-gateway

# Execute command in running container
docker-compose exec bia-service bash
```

### Updating Platform

```bash
# Pull latest changes
git pull origin main

# Rebuild services
docker-compose build

# Restart with new version
docker-compose down && docker-compose up -d

# Run database migrations
python scripts/run_migrations.py
```

---

## Development Workflow

### Local Development Setup

For active development with code hot-reloading:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Start infrastructure only
cd infrastructure
docker-compose up -d
cd ..

# Run services locally (hot reload enabled)
# Terminal 1: API Gateway
uvicorn infrastructure.gateway.api_gateway:app --reload --port 8000

# Terminal 2: BIA Service
uvicorn platform_services.bia_service.main:app --reload --port 8001

# Terminal 3: AI Foundation
uvicorn intelligent_core.ai_foundation.main:app --reload --port 8020
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test module
pytest tests/unit/test_bia_service.py

# Run integration tests
pytest tests/integration/

# View coverage report
open htmlcov/index.html
```

### Code Quality Checks

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .

# Security scan
bandit -r .
```

---

## Troubleshooting

### Issue: Services Won't Start

**Symptoms:** Docker containers exit immediately or fail health checks

**Solutions:**

1. Check Docker resources:
   ```bash
   docker system df
   docker system prune  # if low on space
   ```

2. Verify environment variables:
   ```bash
   cat .env | grep -E "API_KEY|DATABASE_URL"
   ```

3. Check logs:
   ```bash
   docker-compose logs [service-name]
   ```

### Issue: Database Connection Errors

**Symptoms:** "could not connect to server" or "password authentication failed"

**Solutions:**

1. Verify Supabase credentials:
   ```bash
   psql $DATABASE_URL -c "SELECT 1;"
   ```

2. Check network connectivity:
   ```bash
   ping db.xxxxx.supabase.co
   ```

3. Verify connection string format:
   ```
   postgresql://user:password@host:port/database
   ```

### Issue: AI API Errors

**Symptoms:** "401 Unauthorized" or "Rate limit exceeded"

**Solutions:**

1. Verify API key:
   ```bash
   echo $ANTHROPIC_API_KEY
   ```

2. Test API key directly:
   ```bash
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01"
   ```

3. Check rate limits and billing in Anthropic console

### Issue: Port Conflicts

**Symptoms:** "port is already allocated" errors

**Solutions:**

1. Check what's using the port:
   ```bash
   lsof -i :8000
   ```

2. Stop conflicting service or change port in docker-compose.yml:
   ```yaml
   ports:
     - "8080:8000"  # Map to different host port
   ```

### Issue: Slow Performance

**Symptoms:** Long response times, timeouts

**Solutions:**

1. Check system resources:
   ```bash
   docker stats
   ```

2. Increase Docker resource limits (Docker Desktop settings)

3. Enable Redis caching in .env:
   ```bash
   REDIS_ENABLED=true
   CACHE_TTL=3600
   ```

4. Check database indexes:
   ```sql
   SELECT schemaname, tablename, indexname
   FROM pg_indexes
   WHERE schemaname = 'public';
   ```

---

## Next Steps

Now that you have a running platform, explore these areas:

### 1. Learn the Platform

- **[Architecture Documentation](/docs/ARCHITECTURE.md)** - Understand system design
- **[API Reference](/docs/API_REFERENCE.md)** - Explore all available endpoints
- **[Standards Compliance](/docs/STANDARDS_COMPLIANCE.md)** - ISO 22301 requirements

### 2. Configure Your Organization

- Set up organizational structure and departments
- Define user roles and permissions
- Configure notification preferences
- Import existing BCM data

### 3. Explore Key Features

- **Business Impact Analysis:** Identify critical business functions
- **Risk Assessment:** Evaluate threats and vulnerabilities
- **Continuity Planning:** Create business continuity plans
- **Compliance Monitoring:** Track ISO 22301 compliance

### 4. Integrate with Existing Systems

- Connect to your ERP system
- Integrate with ITSM tools
- Set up Slack/email notifications
- Configure SSO authentication

### 5. Production Deployment

When ready for production:
- Review [DEPLOYMENT_GUIDE.md](/docs/DEPLOYMENT_GUIDE.md)
- Configure high availability
- Set up backup and disaster recovery
- Enable security hardening
- Configure monitoring and alerting

---

## Support Resources

### Documentation

- **Platform Overview:** [README.md](/docs/README.md)
- **Executive Summary:** [EXECUTIVE_SUMMARY.md](/docs/EXECUTIVE_SUMMARY.md)
- **API Documentation:** http://localhost:8000/docs (when running)

### Community

- **GitHub Issues:** Report bugs and request features
- **Community Forum:** [Planned]
- **Stack Overflow:** Tag questions with `ai-platform-iso`

### Professional Support

- **Email:** support@ai-platform-iso.com
- **Enterprise Support:** Contact sales team for SLA-backed support

---

## Document Information

**Document Version:** 1.0.0
**Last Updated:** 2025-10-09
**Next Review:** 2025-11-09
**Maintained By:** AI Platform Documentation Team
**Feedback:** documentation@ai-platform-iso.com

---

**Ready to get started?** Follow the installation steps above, and you'll have a running platform in under an hour. If you encounter any issues, consult the Troubleshooting section or reach out to our support team.
