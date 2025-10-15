# 🚀 Quick Start: Service Registry + Service Discovery Integration

**One-page guide to get started in 2 minutes**

---

## ✨ What You Get

Register a service with **one API call** and get:
- ✅ Catalog entry (YAML)
- ✅ Service Discovery registration
- ✅ FastAPI template (optional)

---

## 📋 Prerequisites

```bash
# Install dependencies (if not already)
cd /Users/MD/AI-Platform-ISO/infrastructure/runtime/service_registry_management
pip install -r requirements.txt

cd /Users/MD/AI-Platform-ISO/infrastructure/runtime/service_discovery
pip install -r requirements.txt
```

---

## 🏃 Start Services (2 terminals)

### Terminal 1: Service Discovery
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/runtime/service_discovery
python main.py
```

**Expected**: `🚀 Service Discovery v2.0 started on port 8500`

### Terminal 2: Service Registry Management
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/runtime/service_registry_management
python main.py
```

**Expected**: `🚀 Service Registry Management started on port 8200`

---

## ✅ Verify Services Running

```bash
# Check Service Discovery
curl http://localhost:8500/health

# Check Service Registry
curl http://localhost:8200/health
```

---

## 🎯 Register Your First Service

### Method 1: cURL (Simple)

```bash
curl -X POST http://localhost:8200/api/v1/services/register \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "my_analytics_service",
    "service_type": "platform",
    "description": "My awesome analytics service",
    "component": "platform_services",
    "create_template": true,
    "purpose": ["Real-time analytics", "Data processing"],
    "capabilities": ["Data aggregation", "Report generation"]
  }'
```

### Method 2: Python Script

```python
import httpx
import asyncio

async def register_service():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8200/api/v1/services/register",
            json={
                "service_name": "my_analytics_service",
                "service_type": "platform",
                "description": "My awesome analytics service",
                "component": "platform_services",
                "create_template": True,
                "purpose": ["Real-time analytics", "Data processing"],
                "capabilities": ["Data aggregation", "Report generation"]
            }
        )
        print(response.json())

asyncio.run(register_service())
```

### Expected Response

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

---

## 🔍 Verify Integration

### 1. Check Catalog Entry

```bash
cat /Users/MD/AI-Platform-ISO/catalogs/platform-services/my_analytics_service.yaml
```

### 2. Check Service Discovery

```bash
curl http://localhost:8500/v2/catalog/services | grep my_analytics_service
```

### 3. Check Generated Template

```bash
ls -la /Users/MD/AI-Platform-ISO/infrastructure/my_analytics_service/
# Should show: main.py, requirements.txt, README.md
```

---

## 🏃‍♂️ Start Your Service

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/my_analytics_service
pip install -r requirements.txt
python main.py
```

**Expected**: Service starts on assigned port (e.g., 8066)

**Verify**:
```bash
curl http://localhost:8066/health
curl http://localhost:8066/metrics
```

---

## 📊 View Statistics

### Port Usage

```bash
curl http://localhost:8200/api/v1/ports/usage
```

### Service Statistics

```bash
curl http://localhost:8200/api/v1/services/stats
```

### All Services in Discovery

```bash
curl http://localhost:8500/v2/catalog/services
```

---

## 🧪 Run Integration Demo

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/runtime/service_registry_management
python demo_integration.py
```

This will:
1. ✅ Register a test service
2. ✅ Verify catalog creation
3. ✅ Verify Service Discovery registration
4. ✅ Verify template generation
5. ✅ Show statistics

---

## 🎨 Service Types & Port Ranges

| Service Type | Component | Port Range | Example |
|--------------|-----------|------------|---------|
| `platform` | `platform_services` | 8000-8099 | Analytics, ACE |
| `ai_core` | `intelligent_core` | 8100-8199 | AI Orchestrator |
| `infrastructure` | `infrastructure` | 8200-8299 | Gateway, Discovery |
| `integration` | `integration` | 8300-8399 | GitHub, MCP |

---

## 🔧 Common Operations

### Get Port Suggestions

```bash
curl "http://localhost:8200/api/v1/ports/suggestions/platform_services?count=5"
```

### Register with Specific Port

```bash
curl -X POST http://localhost:8200/api/v1/services/register \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "special_service",
    "service_type": "platform",
    "description": "Special service",
    "component": "platform_services",
    "port": 8070
  }'
```

### Register Without Template

```bash
curl -X POST http://localhost:8200/api/v1/services/register \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "simple_service",
    "service_type": "platform",
    "description": "Simple service",
    "component": "platform_services",
    "create_template": false
  }'
```

---

## 🐛 Troubleshooting

### Service Discovery Not Available

**Symptom**: Registration works but warns about Service Discovery

**Solution**: Start Service Discovery
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/runtime/service_discovery
python main.py
```

**Note**: Service registration still succeeds and creates catalog/template

### Port Already in Use

**Solution**: Get suggestions
```bash
curl "http://localhost:8200/api/v1/ports/suggestions/platform_services?count=5"
```

### Service Not in Discovery

**Check**:
```bash
# Verify ENABLE_SERVICE_DISCOVERY is true
echo $ENABLE_SERVICE_DISCOVERY

# Check logs
tail -f service_registry.log
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Service Registry Management
export SERVICE_REGISTRY_PORT=8200
export REPO_ROOT=/Users/MD/AI-Platform-ISO
export SERVICE_DISCOVERY_URL=http://localhost:8500
export ENABLE_SERVICE_DISCOVERY=true

# Service Discovery
export SERVICE_DISCOVERY_PORT=8500
```

---

## 📚 Full Documentation

- **Integration Guide**: `/doc-project/SERVICE_REGISTRY_INTEGRATION_COMPLETE.md`
- **Service Registry README**: `README.md`
- **Service Discovery**: `/infrastructure/runtime/service_discovery/README.md`

---

## 🎉 You're Ready!

**Next Steps**:
1. Register your services via API
2. Start generated services
3. Monitor via Prometheus metrics
4. Discover services via Service Discovery API

**Questions?** Check `/doc-project/SERVICE_REGISTRY_INTEGRATION_COMPLETE.md`

---

**Version**: 1.0.0
**Updated**: 2025-10-15
**Status**: ✅ Production Ready
