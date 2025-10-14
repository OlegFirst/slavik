# Docker Generated Configurations

**Type:** Auto-generated output files
**Purpose:** Quick-start infrastructure deployment
**Last Generated:** 2025-10-07
**Status:** ⚠️ Check for updates before use

---

## 📋 What's Here

This directory contains **auto-generated** Docker Compose configurations and startup scripts for the AI Platform infrastructure.

### Files

| File | Purpose | Size |
|------|---------|------|
| `docker-compose.full.yml` | Complete infrastructure | 4.7KB |
| `docker-compose.gateway.yml` | Gateway layer only | - |
| `docker-compose.integration.yml` | Integration services | - |
| `docker-compose.observability.yml` | Prometheus + Grafana | - |
| `docker-compose.runtime.yml` | Runtime services | - |
| `service-catalog.json` | Service definitions | 35KB |
| `start_infrastructure.sh` | Infrastructure startup | - |
| `stop_infrastructure.sh` | Infrastructure shutdown | - |
| `check_health.sh` | Health checker | - |

---

## 🚀 Quick Start

### Start Full Infrastructure

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/tools/docker-generated

# Start all services
./start_infrastructure.sh

# Check health
./check_health.sh

# Stop all services
./stop_infrastructure.sh
```

### Start Specific Layer

```bash
# Gateway only
docker-compose -f docker-compose.gateway.yml up -d

# Observability only
docker-compose -f docker-compose.observability.yml up -d

# Runtime services only
docker-compose -f docker-compose.runtime.yml up -d

# Integration layer only
docker-compose -f docker-compose.integration.yml up -d
```

---

## ⚠️ Important Notes

### This is OUTPUT, not SOURCE

- ✅ These files are **auto-generated**
- ✅ Safe to regenerate at any time
- ⚠️ **DO NOT manually edit** - changes will be overwritten
- ⚠️ Check generation date before using

### Last Generated

**Date:** 2025-10-07
**Status:** May be outdated

### Before Using

1. ✅ Check if configs match current platform state
2. ✅ Verify all service ports are correct
3. ✅ Review environment variables
4. ⚠️ Consider regenerating if outdated

---

## 🔄 Regeneration

**⚠️ TODO:** Document the regeneration process

### How to Regenerate (needs documentation)

```bash
# TODO: Add command to regenerate these configs
# Likely something like:
# python3 /infrastructure/tools/???/generator.py
```

### When to Regenerate

- After adding new services
- After changing service ports
- After infrastructure reorganization
- When configs are more than 1 month old

---

## 📊 Service Catalog

`service-catalog.json` (35KB) contains service definitions including:

- Service names and ports
- Dependencies
- Health check endpoints
- Metrics endpoints
- Configuration options

**To view:**
```bash
cat service-catalog.json | jq '.'
```

---

## 🎯 Usage Scenarios

### 1. Fresh Infrastructure Deployment

```bash
# Clone repository
git clone <repo-url>

# Navigate to docker-generated
cd infrastructure/tools/docker-generated

# Start everything
./start_infrastructure.sh

# Verify
./check_health.sh
```

### 2. Observability Stack Only

```bash
# Start Prometheus + Grafana
docker-compose -f docker-compose.observability.yml up -d

# Access:
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000
```

### 3. Gateway + Backend

```bash
# Start gateway layer
docker-compose -f docker-compose.gateway.yml up -d

# Start runtime services
docker-compose -f docker-compose.runtime.yml up -d
```

---

## 🔍 Troubleshooting

### Port Conflicts

If you encounter port conflicts:

1. Check what's running: `docker ps`
2. Check system ports: `lsof -i :PORT`
3. Update port in appropriate docker-compose file
4. Consider regenerating configs

### Services Not Starting

```bash
# Check logs
docker-compose -f docker-compose.full.yml logs SERVICE_NAME

# Check container status
docker ps -a | grep SERVICE_NAME

# Restart specific service
docker-compose -f docker-compose.full.yml restart SERVICE_NAME
```

### Health Check Fails

```bash
# Run health check script
./check_health.sh

# Check individual service health
curl http://localhost:PORT/health
```

---

## 📚 Related Documentation

- **Service Catalog v2.0:** `/infrastructure/runtime/service-catalog/README.md`
- **Service Discovery:** `/infrastructure/runtime/service-discovery/README.md`
- **Platform Services:** `/platform-services/SERVICE_CATALOG.md`
- **Full Component Catalog:** `/infrastructure/FULL_COMPONENT_CATALOG.md`

---

## 🔄 Maintenance

### Cleanup Old Configs

```bash
# Stop all services
./stop_infrastructure.sh

# Remove containers
docker-compose -f docker-compose.full.yml down

# Remove volumes (⚠️ WARNING: deletes data)
docker-compose -f docker-compose.full.yml down -v
```

### Update Configs

1. Stop services
2. Regenerate configs (see Regeneration section)
3. Review changes: `git diff`
4. Start services with new configs

---

## ⚡ Performance Tips

### Selective Startup

Instead of starting everything:

```bash
# Start only what you need
docker-compose -f docker-compose.runtime.yml up -d redis postgres
docker-compose -f docker-compose.gateway.yml up -d api-gateway
```

### Resource Limits

If system is slow, consider:

1. Reducing number of running services
2. Using separate docker-compose files for layers
3. Scaling down replicas

---

## 🎯 Integration with Platform

These configs integrate with:

- ✅ **Service Discovery v2.0** - auto-registration
- ✅ **MIO Manager** - monitoring and observability
- ✅ **EventBus** - event-driven coordination
- ✅ **Prometheus** - metrics collection
- ✅ **Grafana** - visualization

---

**Generated by:** Platform Configuration Generator
**Maintained by:** Infrastructure Team
**Last Updated:** 2025-10-11
**Status:** Production Ready (with regeneration needed)

---

## 📋 TODO

- [ ] Document regeneration process
- [ ] Add regeneration script
- [ ] Set up automated regeneration on infrastructure changes
- [ ] Add validation script for configs
- [ ] Create CI/CD integration
