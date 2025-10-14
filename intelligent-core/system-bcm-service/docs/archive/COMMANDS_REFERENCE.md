# System BCM - Commands Reference

**Quick reference for all System BCM commands**

---

## 🚀 Deployment Commands

### Automated Integration (RECOMMENDED)

```bash
# Full automated integration with platform
cd /Users/MD/AI-Platform-ISO/intelligent-core/system-bcm-service
./integrate-with-platform.sh
```

### Manual Deployment

```bash
# Create platform network
docker network create platform_network

# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f system-bcm

# Stop services
docker-compose down

# Restart specific service
docker-compose restart system-bcm
```

---

## ✅ Validation Commands

### Full Deployment Validation (40+ tests)

```bash
# Run all validation tests
./validate-deployment.sh

# Expected output:
# Tests run: 42
# Tests passed: 42
# Success rate: 100%
```

### Quick Health Check

```bash
# Run health check script
./health-check.sh

# Manual health check
curl http://localhost:8050/health
```

---

## 📊 API Commands

### Health & Status

```bash
# Health check
curl http://localhost:8050/health

# Service status
curl http://localhost:8050/status

# Metrics (Prometheus format)
curl http://localhost:8050/metrics

# Swagger documentation
open http://localhost:8050/docs
```

### BCM Cycle Management

```bash
# Trigger BCM cycle manually
curl -X POST http://localhost:8050/cycle/trigger

# Get cycle status
curl http://localhost:8050/cycle/status

# Get cycle history
curl http://localhost:8050/cycle/history?limit=10

# Get cycle results
curl http://localhost:8050/cycle/results | jq
```

### Recovery Management

```bash
# Trigger recovery manually
curl -X POST http://localhost:8050/recovery/trigger \
  -H "Content-Type: application/json" \
  -d '{
    "service": "redis",
    "incident_type": "connection_pool_exhausted"
  }'

# Get recovery history
curl http://localhost:8050/recovery/history?service=redis

# Get all recovery procedures
curl http://localhost:8050/recovery/procedures | jq
```

### Learning & Insights

```bash
# Get generated insights
curl http://localhost:8050/insights | jq

# Get detected patterns
curl http://localhost:8050/patterns | jq

# Get learning effectiveness
curl http://localhost:8050/learning/effectiveness | jq

# Get improvements applied
curl http://localhost:8050/learning/improvements | jq
```

---

## 🐳 Docker Commands

### Container Management

```bash
# List all containers
docker ps -a

# View System BCM container
docker ps | grep system-bcm

# View logs
docker logs system-bcm-service -f

# Execute command in container
docker exec -it system-bcm-service bash

# View container stats
docker stats system-bcm-service

# Inspect container
docker inspect system-bcm-service
```

### Network Management

```bash
# List networks
docker network ls

# Inspect platform_network
docker network inspect platform_network

# Create network (if not exists)
docker network create platform_network

# Remove network
docker network rm platform_network
```

### Volume Management

```bash
# List volumes
docker volume ls

# Inspect volumes
docker volume inspect system-bcm-service_redis_data
docker volume inspect system-bcm-service_prometheus_data
docker volume inspect system-bcm-service_grafana_data

# Remove volumes (careful!)
docker volume rm system-bcm-service_redis_data
docker volume rm system-bcm-service_prometheus_data
docker volume rm system-bcm-service_grafana_data
```

---

## 📈 Monitoring Commands

### Prometheus

```bash
# Access Prometheus UI
open http://localhost:9090

# Check targets
curl http://localhost:9090/api/v1/targets | jq

# Check alerts
curl http://localhost:9090/api/v1/alerts | jq

# Query metric
curl 'http://localhost:9090/api/v1/query?query=system_bcm_running' | jq

# Query range
curl 'http://localhost:9090/api/v1/query_range?query=system_bcm_cycle_duration_seconds&start=2025-10-09T00:00:00Z&end=2025-10-09T23:59:59Z&step=1h' | jq
```

### Grafana

```bash
# Access Grafana UI
open http://localhost:3000

# Get datasources (requires auth)
curl -u admin:admin http://localhost:3000/api/datasources | jq

# Get dashboards
curl -u admin:admin http://localhost:3000/api/search | jq

# Get dashboard by UID
curl -u admin:admin http://localhost:3000/api/dashboards/uid/system-bcm | jq
```

### Redis EventBus

```bash
# Access Redis CLI
docker exec -it system-bcm-redis redis-cli

# Inside Redis CLI:
# Check all streams
KEYS platform.*

# Check stream info
XINFO STREAM platform.bcm.cycle.completed

# Get stream length
XLEN platform.bcm.cycle.completed

# Read from stream
XREAD STREAMS platform.bcm.cycle.completed 0
```

---

## 🔧 Configuration Commands

### Environment Configuration

```bash
# View current .env
cat .env

# Edit .env
nano .env
# or
vim .env

# Copy .env.example to .env
cp .env.example .env

# Validate .env (check for required variables)
grep -E "REDIS_HOST|SERVICE_PORT|CYCLE_INTERVAL_HOURS" .env
```

### Scenario Management

```bash
# List scenarios
ls -lh scenarios/

# Validate JSON scenarios
jq empty scenarios/platform_bia.json
jq empty scenarios/platform_risks.json
jq empty scenarios/recovery_procedures.json
jq empty scenarios/resource_priorities.json

# View scenario content
jq . scenarios/platform_bia.json | less

# Edit scenario
nano scenarios/platform_bia.json
```

---

## 🧪 Testing Commands

### Python Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_system_bcm.py

# Run with coverage
pytest --cov=system_bcm --cov-report=html
```

### Integration Tests

```bash
# Test EventBus connection
docker exec system-bcm-service python3 -c "
import redis
r = redis.Redis(host='redis', port=6379)
print('EventBus:', 'Connected' if r.ping() else 'Failed')
"

# Test platform service discovery
curl http://localhost:8050/services/discovered | jq

# Test recovery procedure execution
curl -X POST http://localhost:8050/test/recovery \
  -H "Content-Type: application/json" \
  -d '{"procedure": "eventbus_recovery"}'
```

---

## 🔍 Debugging Commands

### Logs

```bash
# System BCM logs
docker-compose logs -f system-bcm

# Redis logs
docker-compose logs -f redis

# Prometheus logs
docker-compose logs -f prometheus

# Grafana logs
docker-compose logs -f grafana

# All logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100 system-bcm

# Logs since 1 hour ago
docker-compose logs --since 1h system-bcm
```

### EventBus Debugging

```bash
# Monitor EventBus events in real-time
docker exec -it system-bcm-redis redis-cli MONITOR

# Subscribe to BCM events
docker exec -it system-bcm-redis redis-cli
# Then:
# XREAD BLOCK 0 STREAMS platform.bcm.cycle.completed $

# Check for specific event
docker exec -it system-bcm-redis redis-cli \
  XRANGE platform.bcm.cycle.completed - +
```

### Service Discovery

```bash
# Check Docker network services
docker network inspect platform_network | jq '.[0].Containers'

# Scan platform ports
for port in {8001..8012} 8031 8032 8036 8037 8038 8039 8041 8050; do
  echo -n "Port $port: "
  curl -s --max-time 1 http://localhost:$port/health && echo "✅" || echo "❌"
done

# Check specific service
curl -s http://localhost:8001/health | jq  # BIA Service
curl -s http://localhost:8037/health | jq  # Workflow Intelligence
```

---

## 🔐 Security Commands

### Secrets Management

```bash
# View Vault status
docker exec -it vault vault status

# Access Vault UI (if available)
open http://localhost:8200

# Get secret from Vault
docker exec -it vault vault kv get secret/system-bcm/config
```

### API Authentication

```bash
# Generate API key (if enabled)
curl -X POST http://localhost:8050/auth/generate-key \
  -H "Content-Type: application/json" \
  -d '{"name": "my-client"}'

# Use API key
curl http://localhost:8050/cycle/trigger \
  -H "X-API-Key: your-api-key-here"
```

---

## 🗄️ Database Commands

### PostgreSQL

```bash
# Access PostgreSQL
docker exec -it postgresql psql -U postgres -d platform

# Inside psql:
# List tables
\dt

# View BCM tables
SELECT * FROM system_bcm_cycles ORDER BY created_at DESC LIMIT 10;
SELECT * FROM system_bcm_insights ORDER BY generated_at DESC LIMIT 10;

# Exit psql
\q
```

### Qdrant Vector DB

```bash
# Access Qdrant API
curl http://localhost:6333/collections

# Get BCM knowledge collection
curl http://localhost:6333/collections/bcm_business_flows | jq

# Search in collection
curl -X POST http://localhost:6333/collections/bcm_business_flows/points/search \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [...],
    "limit": 5
  }' | jq
```

---

## 📦 Backup & Restore

### Backup Scenarios

```bash
# Backup all scenarios
tar -czf scenarios_backup_$(date +%Y%m%d).tar.gz scenarios/

# Backup specific scenario
cp scenarios/platform_bia.json scenarios/platform_bia.json.backup
```

### Backup Redis Data

```bash
# Trigger Redis save
docker exec system-bcm-redis redis-cli SAVE

# Copy RDB file
docker cp system-bcm-redis:/data/dump.rdb ./backup/redis_$(date +%Y%m%d).rdb
```

### Backup Grafana Dashboards

```bash
# Export dashboard
curl -u admin:admin http://localhost:3000/api/dashboards/uid/system-bcm | jq > backup/dashboard_$(date +%Y%m%d).json
```

### Restore

```bash
# Restore scenarios
tar -xzf scenarios_backup_20251009.tar.gz

# Restart services to pick up changes
docker-compose restart system-bcm
```

---

## 🧹 Cleanup Commands

### Remove All Containers

```bash
# Stop and remove all containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove containers, volumes, and orphans
docker-compose down -v --remove-orphans
```

### Clean Docker System

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune

# Remove everything (careful!)
docker system prune -a --volumes
```

### Clean Logs

```bash
# Truncate local logs
> logs/system-bcm-service.log

# Remove old log files
find logs/ -name "*.log.*" -mtime +7 -delete
```

---

## 🔄 Update Commands

### Pull Latest Code

```bash
# If using git
cd /Users/MD/AI-Platform-ISO
git pull origin main
```

### Rebuild Containers

```bash
# Rebuild System BCM image
docker-compose build system-bcm

# Rebuild with no cache
docker-compose build --no-cache system-bcm

# Rebuild and restart
docker-compose up -d --build system-bcm
```

### Update Dependencies

```bash
# Update Python dependencies
docker exec system-bcm-service pip install --upgrade -r requirements.txt

# Rebuild container with updated deps
docker-compose build system-bcm
docker-compose up -d system-bcm
```

---

## 📊 Performance Monitoring

### Resource Usage

```bash
# Container stats (real-time)
docker stats

# System BCM container stats
docker stats system-bcm-service

# Get specific metric
docker stats --no-stream --format "{{.Name}}\t{{.CPUPerc}}\t{{.MemPerc}}" system-bcm-service
```

### Benchmark BCM Cycle

```bash
# Time BCM cycle execution
time curl -X POST http://localhost:8050/cycle/trigger

# Monitor cycle performance
while true; do
  curl -s http://localhost:8050/metrics | grep system_bcm_cycle_duration_seconds
  sleep 5
done
```

---

## 🆘 Emergency Commands

### Force Restart

```bash
# Force restart System BCM
docker-compose restart system-bcm

# Force stop and start
docker-compose stop system-bcm
docker-compose start system-bcm

# Kill and restart
docker kill system-bcm-service
docker-compose up -d system-bcm
```

### Emergency Recovery

```bash
# Trigger all recovery procedures
for procedure in eventbus_recovery db_pool_recovery service_restart; do
  curl -X POST http://localhost:8050/recovery/trigger \
    -H "Content-Type: application/json" \
    -d "{\"procedure\": \"$procedure\"}"
done
```

### Reset to Clean State

```bash
# Stop all services
docker-compose down -v

# Remove all data
rm -rf logs/*
docker volume rm system-bcm-service_redis_data
docker volume rm system-bcm-service_prometheus_data
docker volume rm system-bcm-service_grafana_data

# Start fresh
docker-compose up -d
```

---

## 📚 Information Commands

### Version Information

```bash
# System BCM version
curl http://localhost:8050/status | jq .version

# Docker version
docker --version

# Docker Compose version
docker-compose --version

# Python version (in container)
docker exec system-bcm-service python3 --version
```

### Service Information

```bash
# Get all services info
curl http://localhost:8050/services/info | jq

# Get platform services
curl http://localhost:8050/services/platform | jq

# Get intelligent modules
curl http://localhost:8050/services/intelligent | jq

# Get infrastructure
curl http://localhost:8050/services/infrastructure | jq
```

---

## 🎯 Common Workflows

### Daily Check

```bash
# Quick daily health check
./health-check.sh

# View last cycle results
curl http://localhost:8050/cycle/results | jq

# Check for new insights
curl http://localhost:8050/insights?limit=5 | jq
```

### Weekly Review

```bash
# Get cycle history (last 7 days)
curl http://localhost:8050/cycle/history?days=7 | jq

# Get recovery statistics
curl http://localhost:8050/recovery/stats?days=7 | jq

# Get learning effectiveness
curl http://localhost:8050/learning/effectiveness?days=7 | jq
```

### Troubleshooting

```bash
# 1. Check service health
./health-check.sh

# 2. View recent logs
docker-compose logs --tail=100 system-bcm

# 3. Check EventBus connection
docker exec system-bcm-service python3 -c "
import redis
r = redis.Redis(host='redis')
print('PING:', r.ping())
"

# 4. Validate scenarios
for file in scenarios/*.json; do
  echo "Checking $file..."
  jq empty "$file" && echo "✅ Valid" || echo "❌ Invalid"
done

# 5. Run full validation
./validate-deployment.sh
```

---

**Commands Reference Complete! 📚**

For more details, see:
- [PLATFORM_INTEGRATION.md](PLATFORM_INTEGRATION.md) - Integration guide
- [README.md](README.md) - Main documentation
- [INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md) - Integration status
