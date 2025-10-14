# Platform Services - Port Allocation

**Last Updated:** 2025-10-08
**Total Ports Allocated:** 19 service ports + 5 infrastructure ports

---

## Port Allocation Table

| Port | Service | Type | ISO Clause | Status | Container Name |
|------|---------|------|------------|--------|----------------|
| **8011** | Planning Service | BCM Core | 8.3 | Active | bcm-planning-service |
| **8012** | BIA Service | BCM Core | 8.2.2 | Active | bcm-bia-service |
| **8013** | Governance Service | BCM Core | 4, 5 | Active | bcm-governance-service |
| **8014** | Compliance Service | BCM Core | 9.2, 10.1, 10.2 | Active | bcm-compliance-service |
| **8021** | Learning Service | Intelligence | 7.2, 7.3 | Active | bcm-learning-service |
| **8022** | Validation Service | BCM Core | 8.5, 9.1-9.3, 10 | Active | bcm-validation-service |
| **8023** | Plans Service | BCM Core | 8.4 | Active | bcm-plans-service |
| **8024** | Documents Service | BCM Core | 7.5 | Active | bcm-documents-service |
| **8031** | Simulation Main | Intelligence | - | Active | - |
| **8032** | Community Marketplace | Community | - | Active | - |
| **8033** | Community Portal | Community | - | Active | - |
| **8034** | Living Docs | Intelligence | - | Active | bcm-living-docs |
| **8040** | Risk Service | BCM Core | 8.2.3 | Active | bcm-risk-service |
| **8041** | Response Service | BCM Core | 8.4.5 | Active | bcm-response-service |
| **8045** | Compliance Monitoring | Monitoring | - | Active | - |
| **8070** | BCM Coordination | Coordination | - | Active | bcm-coordination-service |
| **8082** | BIA Engine (Simulation) | Intelligence | - | Active | - |
| **8085** | Scenario Orchestrator | Intelligence | - | Active | - |
| **8780** | Process Analytics | Monitoring | - | Active | - |

---

## Infrastructure Ports

| Port | Service | Purpose | Status |
|------|---------|---------|--------|
| **3000** | Grafana | Metrics Visualization | Active |
| **5432** | PostgreSQL | Primary Database | Active |
| **5672** | RabbitMQ | Message Queue | Active |
| **6379** | Redis | Cache & Session Store | Active |
| **9090** | Prometheus | Metrics Collection | Active |

---

## Port Ranges by Category

### BCM Core Services (8011-8024, 8040-8041)
Primary business continuity management services implementing ISO 22301:2019 clauses.

- **8011-8014:** Planning, BIA, Governance, Compliance
- **8021-8024:** Learning, Validation, Plans, Documents
- **8040-8041:** Risk, Response

### Intelligence Services (8031-8034, 8082-8085)
AI-powered intelligence and simulation services.

- **8031:** Simulation Main
- **8034:** Living Docs
- **8082:** BIA Engine (Simulation)
- **8085:** Scenario Orchestrator

### Community Services (8032-8033)
Community collaboration and knowledge sharing.

- **8032:** Marketplace
- **8033:** Portal

### Coordination Services (8070)
Service orchestration and coordination.

- **8070:** BCM Coordination

### Monitoring Services (8045, 8780)
Monitoring and analytics services.

- **8045:** Compliance Monitoring
- **8780:** Process Analytics

---

## Port Conflict Resolution

### Historical Conflicts Resolved

1. **Governance Service: 8020 → 8013**
   - **Reason:** Port 8020 was used by workflow-intelligence
   - **Resolution:** Changed to 8013
   - **Date:** 2025-10-07
   - **Status:** ✅ Resolved

2. **Community Portal: 8031 → 8033**
   - **Reason:** Port 8031 was used by simulation service
   - **Resolution:** Changed to 8033
   - **Date:** 2025-10-07
   - **Status:** ✅ Resolved

### Current Port Status
✅ No conflicts detected
✅ All ports properly assigned
✅ Port ranges organized by service type

---

## Port Assignment Guidelines

### Rules for New Services

1. **BCM Core Services:** Use 8000-8049 range
   - Prefer: 8010-8029 for core ISO clauses
   - Prefer: 8040-8049 for extended features

2. **Intelligence Services:** Use 8080-8099 range
   - Simulation: 8080-8089
   - AI Services: 8090-8099

3. **Community Services:** Use 8030-8039 range

4. **Coordination Services:** Use 8070-8079 range

5. **Monitoring Services:** Use 8700-8799 range

### Reserved Ports

| Range | Purpose | Status |
|-------|---------|--------|
| 8000-8009 | Reserved for future BCM core | Available |
| 8050-8069 | Reserved for BCM extensions | Available |
| 8071-8079 | Reserved for coordination | Available |
| 8090-8099 | Reserved for AI services | Available |

---

## Docker Compose Port Mapping

All services use the same port internally and externally for simplicity:

```yaml
services:
  planning-service:
    ports:
      - "8011:8011"  # External:Internal
    environment:
      SERVICE_PORT: 8011
```

### Benefits
- ✅ Easy to remember (external = internal)
- ✅ Consistent with service configuration
- ✅ Simplified debugging and testing

---

## Health Check Endpoints

All services expose health checks on their assigned ports:

```bash
# Core BCM Services
curl http://localhost:8011/health  # Planning
curl http://localhost:8012/health  # BIA
curl http://localhost:8013/health  # Governance
curl http://localhost:8014/health  # Compliance
curl http://localhost:8021/health  # Learning
curl http://localhost:8022/health  # Validation
curl http://localhost:8023/health  # Plans
curl http://localhost:8024/health  # Documents
curl http://localhost:8040/health  # Risk
curl http://localhost:8041/health  # Response

# Intelligence Services
curl http://localhost:8031/health  # Simulation
curl http://localhost:8034/health  # Living Docs
curl http://localhost:8070/health  # Coordination
```

---

## API Documentation Endpoints

FastAPI services provide automatic API documentation:

```bash
# Core BCM Services
http://localhost:8011/docs  # Planning
http://localhost:8012/docs  # BIA
http://localhost:8013/docs  # Governance
http://localhost:8014/docs  # Compliance
http://localhost:8021/docs  # Learning
http://localhost:8022/docs  # Validation
http://localhost:8023/docs  # Plans
http://localhost:8024/docs  # Documents
http://localhost:8040/docs  # Risk
http://localhost:8041/docs  # Response

# Intelligence Services
http://localhost:8034/docs  # Living Docs
http://localhost:8070/docs  # Coordination
```

---

## Environment Variable Configuration

Each service can override its port via environment variable:

```bash
# Planning Service
PLANNING_SERVICE_PORT=8011

# BIA Service
BIA_SERVICE_PORT=8012

# Governance Service
GOVERNANCE_SERVICE_PORT=8013

# Compliance Service
COMPLIANCE_SERVICE_PORT=8014

# And so on...
```

### Configuration Files
- **config.py:** Default port defined
- **.env:** Override port via environment variable
- **docker-compose.yml:** Port mapping for containers

---

## Network Configuration

### Docker Network
All services run on the `bcm-platform` bridge network:

```yaml
networks:
  bcm-platform:
    driver: bridge
    name: bcm-platform
```

### Internal Communication
Services can communicate using container names:

```bash
# From one service to another
http://bcm-planning-service:8011
http://bcm-bia-service:8012
http://bcm-governance-service:8013
```

### External Access
Services are accessible from host machine:

```bash
http://localhost:8011
http://localhost:8012
http://localhost:8013
```

---

## Port Availability Check

### Check if Port is in Use

```bash
# macOS/Linux
lsof -i :8011
lsof -i :8012

# Check all BCM service ports
for port in 8011 8012 8013 8014 8021 8022 8023 8024 8031 8034 8040 8041 8070; do
  echo -n "Port $port: "
  lsof -i :$port > /dev/null 2>&1 && echo "IN USE" || echo "Available"
done
```

### Kill Process on Port

```bash
# Find process ID
lsof -ti :8011

# Kill process
kill -9 $(lsof -ti :8011)
```

---

## Firewall Configuration

### Allow Ports (if needed)

```bash
# macOS (typically not needed for localhost)
sudo pfctl -f /etc/pf.conf

# Linux (ufw)
sudo ufw allow 8011
sudo ufw allow 8012
# ... etc
```

### Development Environment
Usually no firewall configuration needed for localhost access.

### Production Environment
Configure firewall to:
1. Allow external access to API Gateway only
2. Block direct access to individual services
3. Allow internal service-to-service communication

---

## Load Balancer Configuration

### Future: API Gateway
When API Gateway is implemented, all service ports will be:
- **Internal Only:** Accessible only within Docker network
- **External Access:** Via API Gateway on port 8000

```
Client → API Gateway (8000) → Internal Services (8011+)
```

### Benefits
- ✅ Single entry point
- ✅ Centralized authentication
- ✅ Rate limiting
- ✅ Request routing
- ✅ SSL/TLS termination

---

## Monitoring Ports

### Prometheus Scrape Configuration

```yaml
scrape_configs:
  - job_name: 'planning-service'
    static_configs:
      - targets: ['planning-service:8011']

  - job_name: 'bia-service'
    static_configs:
      - targets: ['bia-service:8012']

  # ... etc for all services
```

### Health Check Monitoring

```bash
# Check all services
./scripts/health_check_all.sh

# Expected output:
# Planning Service (8011): healthy
# BIA Service (8012): healthy
# Governance Service (8013): healthy
# ...
```

---

## Troubleshooting

### Service Won't Start - Port Already in Use

```bash
# 1. Find what's using the port
lsof -i :8011

# 2. Kill the process or stop the container
docker stop bcm-planning-service

# 3. Restart the service
docker-compose up -d planning-service
```

### Cannot Access Service

```bash
# 1. Check if container is running
docker ps | grep bcm-planning-service

# 2. Check if port is exposed
docker port bcm-planning-service

# 3. Check service logs
docker logs bcm-planning-service

# 4. Test health endpoint
curl http://localhost:8011/health
```

### Port Conflict Between Services

```bash
# 1. Review port allocation
grep -r "SERVICE_PORT" platform-services/*/config.py

# 2. Update conflicting service
# Edit config.py to change port

# 3. Update docker-compose.yml
# Change port mapping

# 4. Rebuild and restart
docker-compose up -d --build
```

---

## Quick Reference Commands

### Start All Services
```bash
cd /Users/MD/AI-Platform-ISO/platform-services
docker-compose up -d
```

### Check All Ports
```bash
docker-compose ps | grep -E "8011|8012|8013|8014|8021|8022|8023|8024|8031|8034|8040|8041|8070"
```

### Test All Health Endpoints
```bash
for port in 8011 8012 8013 8014 8021 8022 8023 8024 8034 8040 8041 8070; do
  echo "Testing port $port..."
  curl -s http://localhost:$port/health | jq .
done
```

### View Service Logs by Port
```bash
# Find container by port
docker ps --format "{{.Names}}" | grep -E "planning|bia|governance"

# View logs
docker logs bcm-planning-service
```

---

## Future Enhancements

### Planned Changes
1. **API Gateway** - Single entry point on port 8000
2. **Service Mesh** - Internal communication via Istio/Linkerd
3. **Dynamic Port Assignment** - Service discovery via Consul/Etcd
4. **HTTPS** - SSL/TLS on all ports
5. **IPv6 Support** - Enable IPv6 for all services

### Port Migration Plan
When implementing API Gateway:
1. Keep existing ports for backward compatibility
2. Add API Gateway on port 8000
3. Gradually migrate clients to API Gateway
4. Eventually make service ports internal-only

---

**Document Version:** 1.0.0
**Maintained By:** Platform Infrastructure Team
**Related Documents:**
- [Platform Services Catalog](./PLATFORM_SERVICES_COMPLETE_CATALOG.md)
- [Architecture Overview](./ARCHITECTURE.md)
- [Quick Reference](./QUICK_REFERENCE.md)
