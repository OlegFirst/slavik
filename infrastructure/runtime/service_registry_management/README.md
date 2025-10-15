# Service Registry Management

**Port**: 8200 (Infrastructure range)
**Status**: ✅ Production Ready
**Version**: 1.0.0

Centralized service registration and management system for AI Platform ISO.

---

## 🎯 Overview

Service Registry Management - это REST API для автоматической регистрации и управления сервисами в платформе.

### Основные возможности

- ✅ **Автоматическая регистрация** сервисов в каталоге
- ✅ **Управление портами** с предотвращением конфликтов
- ✅ **Генерация шаблонов** FastAPI сервисов
- ✅ **Интеграция** с Service Discovery и Catalog Integration
- ✅ **Мониторинг** через Prometheus metrics
- ✅ **Статистика** использования портов

---

## 🚀 Quick Start

### Installation

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/runtime/service_registry_management

# Install dependencies
pip install -r requirements.txt
```

### Start Service

```bash
# Default (port 8200)
python main.py

# Custom port
SERVICE_REGISTRY_PORT=8250 python main.py
```

### Verify Service is Running

```bash
# Health check
curl http://localhost:8200/health

# Service stats
curl http://localhost:8200/api/v1/services/stats

# Port usage
curl http://localhost:8200/api/v1/ports/usage
```

---

##  📡 API Endpoints

### 1. Health Check

```bash
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "service-registry-management",
  "version": "1.0.0",
  "port": 8200,
  "catalogs_dir": "/Users/MD/AI-Platform-ISO/catalogs",
  "total_services": 15
}
```

### 2. Prometheus Metrics

```bash
GET /metrics
```

**Metrics Exported**:
- `service_registry_registrations_total{service_type, status}` - Total registrations
- `service_registry_active_services` - Active services count
- `service_registry_port_usage{service_type}` - Port usage by type
- `service_registry_registration_duration_seconds` - Registration time histogram
- `service_registry_port_conflicts_total` - Port conflicts counter
- `service_registry_template_generations_total` - Templates generated counter

### 3. Port Usage Statistics

```bash
GET /api/v1/ports/usage
```

**Response**:
```json
{
  "platform_services": {
    "service_type": "platform_services",
    "range_start": 8000,
    "range_end": 8099,
    "total_ports": 100,
    "used_ports": 6,
    "available_ports": 94,
    "usage_percent": 6.0,
    "used_port_list": [8060, 8061, 8062, 8063, 8064, 8065]
  },
  "intelligent_core": {
    "service_type": "intelligent_core",
    "range_start": 8100,
    "range_end": 8199,
    "total_ports": 100,
    "used_ports": 0,
    "available_ports": 100,
    "usage_percent": 0.0,
    "used_port_list": []
  },
  // ... other service types
}
```

### 4. Port Suggestions

```bash
GET /api/v1/ports/suggestions/{service_type}?count=5
```

**Example**:
```bash
curl http://localhost:8200/api/v1/ports/suggestions/platform_services?count=5
```

**Response**:
```json
[
  {
    "port": 8066,
    "available": true,
    "in_catalog": false,
    "in_system": false
  },
  {
    "port": 8067,
    "available": true,
    "in_catalog": false,
    "in_system": false
  },
  // ... 3 more suggestions
]
```

### 5. Register Service ⭐

```bash
POST /api/v1/services/register
```

**Request Body**:
```json
{
  "service_name": "my_analytics_service",
  "service_type": "platform",
  "description": "Real-time analytics and reporting service",
  "component": "platform_services",
  "port": null,  // Auto-assign if null
  "location": null,  // Default: infrastructure/{service_name}
  "create_template": true,
  "purpose": [
    "Provide real-time analytics",
    "Generate reports",
    "Track KPIs"
  ],
  "capabilities": [
    "Data aggregation",
    "Report generation",
    "Dashboard APIs"
  ],
  "dependencies": [
    "postgresql",
    "redis"
  ]
}
```

**Response**:
```json
{
  "success": true,
  "service_name": "my_analytics_service",
  "catalog_file": "/Users/MD/AI-Platform-ISO/catalogs/platform-services/my_analytics_service.yaml",
  "port": 8066,
  "health_check_url": "http://localhost:8066/health",
  "template_created": true,
  "template_location": "/Users/MD/AI-Platform-ISO/infrastructure/my_analytics_service",
  "message": "Service my_analytics_service successfully registered on port 8066"
}
```

### 6. Service Statistics

```bash
GET /api/v1/services/stats
```

**Response**:
```json
{
  "timestamp": "2025-10-15T12:00:00Z",
  "total_services": 15,
  "total_capacity": 600,
  "total_used": 15,
  "total_available": 585,
  "usage_percent": 2.5,
  "by_type": {
    "platform_services": { /* ... */ },
    "intelligent_core": { /* ... */ },
    // ... other types
  }
}
```

---

## 💡 Usage Examples

### Example 1: Register Service with Auto Port

```bash
curl -X POST http://localhost:8200/api/v1/services/register \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "analytics_engine",
    "service_type": "platform",
    "description": "Analytics and reporting engine",
    "component": "platform_services",
    "create_template": true,
    "purpose": ["Analytics", "Reporting"],
    "capabilities": ["Real-time data", "Report generation"]
  }'
```

**Result**:
- ✅ Creates `/catalogs/platform-services/analytics_engine.yaml`
- ✅ Auto-assigns port (e.g., 8066)
- ✅ Creates `/infrastructure/analytics_engine/` with:
  - `main.py` - FastAPI service
  - `requirements.txt`
  - `README.md`

### Example 2: Register Service with Specific Port

```bash
curl -X POST http://localhost:8200/api/v1/services/register \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "special_service",
    "service_type": "infrastructure",
    "description": "Special infrastructure service",
    "component": "infrastructure",
    "port": 8250,
    "create_template": false
  }'
```

### Example 3: Get Port Suggestions Before Registration

```bash
# 1. Get available ports
curl http://localhost:8200/api/v1/ports/suggestions/platform_services?count=5

# 2. Choose a port and register
curl -X POST http://localhost:8200/api/v1/services/register \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "my_service",
    "service_type": "platform",
    "description": "My service",
    "component": "platform_services",
    "port": 8067
  }'
```

### Example 4: Python Client

```python
import httpx
import asyncio

async def register_service():
    async with httpx.AsyncClient() as client:
        # Register service
        response = await client.post(
            "http://localhost:8200/api/v1/services/register",
            json={
                "service_name": "my_awesome_service",
                "service_type": "platform",
                "description": "My awesome service",
                "component": "platform_services",
                "create_template": True,
                "purpose": ["Purpose 1", "Purpose 2"],
                "capabilities": ["Capability 1", "Capability 2"]
            }
        )

        result = response.json()
        print(f"✅ Service registered on port {result['port']}")
        print(f"📁 Catalog: {result['catalog_file']}")
        print(f"📂 Template: {result['template_location']}")

        return result

# Run
asyncio.run(register_service())
```

---

## 🔧 Port Ranges

| Service Type | Range | Total | Purpose |
|--------------|-------|-------|---------|
| **platform_services** | 8000-8099 | 100 | Platform services (ACE, Analytics, etc.) |
| **intelligent_core** | 8100-8199 | 100 | AI modules (Orchestration, Predictive, etc.) |
| **infrastructure** | 8200-8299 | 100 | Infrastructure (Gateway, Discovery, Registry) |
| **integration** | 8300-8399 | 100 | Integrations (GitHub, MCP, Blockchain) |
| **monitoring** | 9000-9099 | 100 | Monitoring (Prometheus, Grafana, Alerting) |
| **databases** | 5000-5099 | 100 | Database services (PostgreSQL, Redis, etc.) |

**Total Capacity**: 600 ports

---

## 📊 Generated Template Structure

When `create_template: true`, the service generates:

```
infrastructure/{service_name}/
├── main.py              # FastAPI service
├── requirements.txt     # Dependencies
└── README.md           # Documentation
```

### Generated main.py Features

- ✅ FastAPI application
- ✅ Health endpoint (`/health`)
- ✅ Metrics endpoint (`/metrics`)
- ✅ Root endpoint (`/`)
- ✅ CORS configured
- ✅ Logging configured
- ✅ Environment variable support
- ✅ Prometheus client integrated

---

## 🔗 Integration

### With Service Discovery

```python
# In service_discovery/main.py
from ..service_registry_management import port_manager

# Use port manager to validate ports before registration
port = port_manager.get_next_available_port("platform_services")
```

### With API Gateway

```python
# API Gateway can query service registry for routing
import httpx

async def get_service_info(service_name: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8200/api/v1/services/{service_name}"
        )
        return response.json()
```

### With Catalog Integration

Service Registry Management использует существующую структуру каталогов:

```
/Users/MD/AI-Platform-ISO/catalogs/
├── platform-services/
│   ├── SERVICE_CATALOG_DETAILED.yaml
│   ├── ace-service.yaml
│   ├── my_new_service.yaml  ← Created by Registry
│   └── ...
```

---

## 📈 Monitoring

### Prometheus Configuration

```yaml
- job_name: 'service-registry-management'
  scrape_interval: 10s
  metrics_path: '/metrics'
  static_configs:
    - targets: ['localhost:8200']
      labels:
        service: 'service-registry-management'
        component: 'infrastructure'
```

### Grafana Dashboard Queries

**Total Active Services**:
```promql
service_registry_active_services
```

**Registration Rate**:
```promql
rate(service_registry_registrations_total[5m])
```

**Port Usage by Type**:
```promql
service_registry_port_usage
```

**Registration Duration P95**:
```promql
histogram_quantile(0.95, service_registry_registration_duration_seconds_bucket)
```

**Port Conflicts**:
```promql
increase(service_registry_port_conflicts_total[1h])
```

---

## 🛠️ Troubleshooting

### Issue: "Port already in use"

**Solution**:
```bash
# Get available ports
curl http://localhost:8200/api/v1/ports/suggestions/platform_services

# Use suggested port in registration
```

### Issue: "Catalog directory not found"

**Solution**:
```bash
# Set REPO_ROOT environment variable
export REPO_ROOT=/Users/MD/AI-Platform-ISO
python main.py
```

### Issue: Service not responding

**Solution**:
```bash
# Check if service is running
lsof -i :8200

# Check logs
tail -f service_registry.log

# Restart service
python main.py
```

---

## 🎯 Best Practices

1. **Always use auto-assignment** unless you have a specific reason for a custom port
2. **Create templates** for new services to ensure consistency
3. **Monitor port usage** regularly to avoid exhaustion
4. **Document purpose and capabilities** for better discoverability
5. **Use appropriate service_type** for correct port range selection

---

## 📋 Service Types

- `learning_infrastructure` - Learning and training systems
- `ai_core` - Core AI functionality
- `platform` - Platform services
- `integration` - External integrations
- `infrastructure` - Infrastructure services

---

## 🔒 Security

- **Internal service only** (localhost:8200)
- **No authentication** (trusted internal network)
- **Write access** to `/catalogs` directory required
- **Read access** to existing catalogs for port scanning

---

## 📚 Related Documentation

- **Catalog Entry**: `/catalogs/platform-services/service-registry-management.yaml`
- **Summary**: `/doc-project/SERVICE_REGISTRATION_SYSTEM_COMPLETE.md`
- **Catalog Integration**: `/infrastructure/runtime/service_discovery/catalog_integration.py`
- **Service Discovery**: `/infrastructure/runtime/service_discovery/main.py`

---

## 🎉 Summary

Service Registry Management provides:

- ✅ **Automated registration** - No manual YAML editing
- ✅ **Zero port conflicts** - Intelligent port management
- ✅ **Standard templates** - Consistent service structure
- ✅ **Full monitoring** - Prometheus metrics integration
- ✅ **REST API** - Programmatic access

**Production Ready** - Deploy and use immediately! 🚀

---

**Created**: 2025-10-15
**Version**: 1.0.0
**Port**: 8200
**Location**: `/infrastructure/runtime/service_registry_management/`
