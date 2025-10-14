# System BCM Service - Scripts

**Automation scripts for deployment, validation, and health monitoring**

---

## 📜 Available Scripts

### 1. integrate-with-platform.sh (12KB)
**Full platform integration automation**

```bash
./integrate-with-platform.sh
```

**What it does** (8 phases):
1. Discovers platform services (23 services)
2. Validates infrastructure (Redis, PostgreSQL, Prometheus)
3. Builds Docker image
4. Deploys service (port 8050)
5. Validates integration
6. Configures EventBus subscriptions
7. Starts monitoring
8. Runs health checks

**Duration**: ~5-10 minutes
**Prerequisites**: Docker, docker-compose, PostgreSQL access

---

### 2. validate-deployment.sh (14KB)
**Comprehensive deployment validation**

```bash
./validate-deployment.sh
```

**What it tests** (40+ tests):
- ✅ Service health (port 8050)
- ✅ Metrics endpoint (Prometheus)
- ✅ EventBus integration (Redis)
- ✅ Database connectivity (PostgreSQL)
- ✅ Auto-recovery procedures (7 procedures)
- ✅ Learning engine
- ✅ Integration with platform services

**Output**: Detailed validation report with pass/fail status

---

### 3. health-check.sh (13KB)
**Quick health verification**

```bash
./health-check.sh
```

**What it checks**:
- Service availability (HTTP 200)
- Port accessibility (8050)
- Response time
- Basic metrics

**Use case**: Quick status check, cron monitoring

---

### 4. start.sh (3.3KB)
**Simple service startup**

```bash
./start.sh
```

**What it does**:
- Starts System BCM Service on port 8050
- Loads environment variables
- Initializes logging
- Runs FastAPI with uvicorn

**Use case**: Development, manual deployment

---

## 🚀 Quick Start Workflow

### First Time Deployment
```bash
# 1. Full integration
./integrate-with-platform.sh

# 2. Validate everything
./validate-deployment.sh

# 3. Monitor health
./health-check.sh
```

### Daily Operations
```bash
# Quick health check
./health-check.sh

# Or just start service
./start.sh
```

### Troubleshooting
```bash
# Re-run full integration
./integrate-with-platform.sh

# Validate specific component
./validate-deployment.sh
```

---

## 📊 Script Comparison

| Script | Purpose | Duration | Complexity | Output |
|--------|---------|----------|------------|--------|
| integrate-with-platform.sh | Full deployment | 5-10 min | High | Integration report |
| validate-deployment.sh | Testing | 2-5 min | Medium | Validation report |
| health-check.sh | Quick check | <10 sec | Low | Health status |
| start.sh | Service start | <5 sec | Low | Service logs |

---

## 🔧 Configuration

All scripts use:
- **Service Port**: 8050
- **Config File**: `../.env`
- **Logs**: `../logs/`
- **Docker Compose**: `../docker-compose.yml`

### Environment Variables
```bash
# Required in .env
SERVICE_PORT=8050
REDIS_URL=redis://localhost:6379
POSTGRES_URL=postgresql://user:pass@host:5432/db
PROMETHEUS_URL=http://localhost:9090
```

---

## 📝 Script Details

### integrate-with-platform.sh

**Phase Breakdown**:
```
Phase 1: Service Discovery
- Discovers 12 platform services (8001-8012)
- Discovers 11 intelligent modules (8031-8050)
- Discovers 6 infrastructure components

Phase 2: Infrastructure Validation
- Redis (EventBus): ✅
- PostgreSQL (Database): ✅
- Prometheus (Metrics): ✅
- Grafana (Dashboards): ✅
- RabbitMQ (Queue): ✅
- Qdrant (Vector DB): ✅

Phase 3: Docker Build
- Builds system-bcm-service:latest

Phase 4: Deployment
- Starts service on port 8050
- Loads 7 auto-recovery procedures
- Initializes practice learning

Phase 5: Integration Validation
- Tests EventBus pub/sub
- Tests service discovery
- Tests auto-recovery triggers

Phase 6: EventBus Configuration
- Subscribe: health.degraded, service.failed, recovery.needed, platform.event
- Publish: cycle.completed, recovery.triggered, pattern.detected, improvement.applied, insight.generated

Phase 7: Monitoring Setup
- Prometheus scraping (8050/metrics)
- Grafana dashboard import (6 panels)
- Alerting rules (20+ rules)

Phase 8: Health Verification
- Final health check
- Metrics validation
- Integration confirmation
```

---

### validate-deployment.sh

**Test Categories**:
```
1. Service Tests (10 tests)
   - Port availability
   - HTTP response
   - Health endpoint
   - Metrics endpoint
   - API endpoints

2. Integration Tests (10 tests)
   - EventBus connectivity
   - Database connectivity
   - Service discovery
   - Platform service integration
   - Intelligent module integration

3. Functional Tests (10 tests)
   - Auto-recovery procedures (7)
   - Practice learning engine
   - Pattern detection
   - Insight generation

4. Performance Tests (10 tests)
   - Response time
   - Memory usage
   - CPU usage
   - Metrics collection
   - EventBus throughput
```

---

## 🐛 Troubleshooting

### Script fails with "Port 8050 already in use"
```bash
# Kill existing process
lsof -ti:8050 | xargs kill -9

# Or use different port in .env
SERVICE_PORT=8051
```

### Script fails with "Redis connection refused"
```bash
# Start Redis
docker-compose up -d redis

# Or use external Redis
REDIS_URL=redis://external-host:6379
```

### Script fails with "PostgreSQL connection error"
```bash
# Check credentials in .env
# Verify database exists
psql $POSTGRES_URL -c "SELECT 1;"
```

### Script hangs during validation
```bash
# Increase timeout
export VALIDATION_TIMEOUT=300  # 5 minutes

# Or run with verbose logging
./validate-deployment.sh --verbose
```

---

## 📈 Success Criteria

**integrate-with-platform.sh**:
- ✅ All 8 phases complete
- ✅ Service running on port 8050
- ✅ EventBus subscriptions active (4)
- ✅ Prometheus scraping metrics
- ✅ No errors in logs

**validate-deployment.sh**:
- ✅ 40/40 tests passing (100%)
- ✅ All integrations validated
- ✅ Auto-recovery procedures loaded
- ✅ Learning engine initialized

**health-check.sh**:
- ✅ HTTP 200 response
- ✅ Response time < 1s
- ✅ Metrics available

---

## 🔐 Security Notes

- Scripts require `.env` file with credentials
- Never commit `.env` to git (use `.env.example`)
- Use strong PostgreSQL passwords
- Restrict Redis access to localhost or private network
- Use TLS for production deployments

---

## 📚 Related Documentation

- **Main README**: `../README.md`
- **Integration Guide**: `../PLATFORM_INTEGRATION.md`
- **Deployment Guide**: `../docs/COMPLETE_DEPLOYMENT_GUIDE.md`
- **Troubleshooting**: `../docs/CRITICAL_ANALYSIS.md`

---

**Last Updated**: 2025-10-11
**Maintained By**: System BCM Service Team
**Support**: See main documentation for issues
