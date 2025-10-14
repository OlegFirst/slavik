# Response Module - Quick Start Guide

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies

```bash
cd /Users/MD/AI-Platform-ISO/execution-engine/capabilities/response

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit .env if needed (optional - defaults work)
# Default port: 8041
# Default database: Supabase (already configured)
```

### 3. Run the Service

```bash
# Option 1: Direct Python
python3 main.py

# Option 2: Uvicorn (recommended)
uvicorn main:app --host 0.0.0.0 --port 8041 --reload

# Option 3: Uvicorn with custom log level
LOG_LEVEL=DEBUG uvicorn main:app --host 0.0.0.0 --port 8041 --reload
```

### 4. Access API Documentation

Open in browser:
- **Swagger UI**: http://localhost:8041/docs
- **ReDoc**: http://localhost:8041/redoc
- **Health Check**: http://localhost:8041/health

### 5. Test Basic Endpoints

```bash
# Health check
curl http://localhost:8041/health

# Root endpoint
curl http://localhost:8041/

# List incidents (requires organization_id)
curl "http://localhost:8041/api/v1/response/incidents?organization_id=00000000-0000-0000-0000-000000000001"
```

## 📝 Create Your First Incident

### Using cURL:

```bash
curl -X POST "http://localhost:8041/api/v1/response/incidents?organization_id=00000000-0000-0000-0000-000000000001" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Database Connection Failure",
    "description": "Production database not responding to connection requests",
    "incident_type": "system_failure",
    "severity": "high",
    "affected_systems": ["database-prod-01", "api-gateway"],
    "detected_by": "Monitoring System"
  }'
```

### Using Python:

```python
import requests

url = "http://localhost:8041/api/v1/response/incidents"
params = {"organization_id": "00000000-0000-0000-0000-000000000001"}

incident = {
    "title": "Database Connection Failure",
    "description": "Production database not responding",
    "incident_type": "system_failure",
    "severity": "high",
    "affected_systems": ["database-prod-01", "api-gateway"],
    "detected_by": "Monitoring System"
}

response = requests.post(url, params=params, json=incident)
print(response.json())
```

### Using Swagger UI:

1. Go to http://localhost:8041/docs
2. Find `POST /api/v1/response/incidents`
3. Click "Try it out"
4. Enter organization_id
5. Fill in the request body
6. Click "Execute"

## 🔍 Common Operations

### List Incidents

```bash
# All incidents for organization
curl "http://localhost:8041/api/v1/response/incidents?organization_id=ORG_ID"

# Filter by status
curl "http://localhost:8041/api/v1/response/incidents?organization_id=ORG_ID&status_filter=investigating"

# Filter by severity
curl "http://localhost:8041/api/v1/response/incidents?organization_id=ORG_ID&severity_filter=critical"

# Search
curl "http://localhost:8041/api/v1/response/incidents?organization_id=ORG_ID&search=database"
```

### Get Incident Details

```bash
curl "http://localhost:8041/api/v1/response/incidents/INCIDENT_ID"
```

### Update Incident Status

```bash
curl -X PATCH "http://localhost:8041/api/v1/response/incidents/INCIDENT_ID/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "investigating",
    "reason": "Response team has been notified",
    "notes": "Initial assessment in progress"
  }'
```

### Add Response Action

```bash
curl -X POST "http://localhost:8041/api/v1/response/incidents/INCIDENT_ID/actions" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Restart Database Service",
    "description": "Attempt to restart the database service",
    "action_type": "technical",
    "priority": "high",
    "assigned_to_name": "John Doe"
  }'
```

### Create Response Team

```bash
curl -X POST "http://localhost:8041/api/v1/response/organizations/ORG_ID/teams" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Critical Incident Response Team",
    "description": "Handles critical severity incidents",
    "is_active": true,
    "members": [
      {
        "user_id": "USER_ID",
        "role": "incident_manager",
        "name": "Jane Smith",
        "email": "jane@example.com",
        "is_primary": true
      }
    ]
  }'
```

### Get Dashboard

```bash
curl "http://localhost:8041/api/v1/response/organizations/ORG_ID/dashboard"
```

### Generate Report

```bash
curl "http://localhost:8041/api/v1/response/incidents/INCIDENT_ID/report"
```

## 🛠️ Development Mode

### With Auto-Reload

```bash
# Uvicorn with reload
uvicorn main:app --reload --port 8041

# With debug logging
DEBUG=true LOG_LEVEL=DEBUG uvicorn main:app --reload --port 8041
```

### Run Tests (if available)

```bash
pytest tests/ -v
```

## 🐳 Docker (Quick Deploy)

### Build Image

```bash
docker build -t response-service:latest .
```

### Run Container

```bash
docker run -d \
  --name response-service \
  -p 8041:8041 \
  -e DATABASE_URL="your_database_url" \
  response-service:latest
```

## 📊 Health Monitoring

### Health Check

```bash
curl http://localhost:8041/health
```

Response:
```json
{
  "status": "healthy",
  "service": "response",
  "version": "1.0.0",
  "iso_standard": "ISO 22301:2019",
  "iso_clause": "8.4",
  "components": {
    "database": {
      "status": "healthy",
      "latency_ms": 25.5
    },
    "event_bus": {
      "enabled": false,
      "status": "disabled"
    }
  }
}
```

### Kubernetes Probes

```bash
# Liveness probe
curl http://localhost:8041/live

# Readiness probe
curl http://localhost:8041/ready
```

## 🎯 Common Use Cases

### 1. System Outage Response

```python
import requests

# Create incident
incident = requests.post(
    "http://localhost:8041/api/v1/response/incidents",
    params={"organization_id": ORG_ID},
    json={
        "title": "Production System Down",
        "description": "Main application server not responding",
        "incident_type": "system_failure",
        "severity": "critical",
        "affected_systems": ["app-server-01"],
        "detected_by": "Monitoring"
    }
).json()

incident_id = incident["id"]

# Add recovery action
requests.post(
    f"http://localhost:8041/api/v1/response/incidents/{incident_id}/actions",
    json={
        "title": "Restart Application Server",
        "description": "Attempt restart of app-server-01",
        "action_type": "recovery",
        "priority": "urgent"
    }
)

# Log communication
requests.post(
    f"http://localhost:8041/api/v1/response/incidents/{incident_id}/communications",
    json={
        "communication_type": "email",
        "subject": "Critical: Production System Down",
        "content": "We are investigating the outage",
        "sender": "IT Team",
        "recipients": ["stakeholders@company.com"]
    }
)

# Add RTO/RPO metrics
requests.post(
    f"http://localhost:8041/api/v1/response/incidents/{incident_id}/metrics",
    json={
        "service_name": "Main Application",
        "target_rto_hours": 1.0,
        "target_rpo_hours": 0.5,
        "downtime_start": "2025-10-03T10:00:00Z"
    }
)
```

### 2. Security Breach Response

```python
# Create critical security incident
incident = requests.post(
    "http://localhost:8041/api/v1/response/incidents",
    params={"organization_id": ORG_ID},
    json={
        "title": "Unauthorized Access Detected",
        "description": "Suspicious login attempts from unknown IP",
        "incident_type": "security_breach",
        "severity": "critical",
        "affected_systems": ["auth-service"],
        "detected_by": "Security Monitoring"
    }
).json()

# Auto-escalates if critical
# Get timeline to verify
timeline = requests.get(
    f"http://localhost:8041/api/v1/response/incidents/{incident['id']}/timeline"
).json()
```

### 3. Track Recovery Compliance

```python
# Get organization metrics
metrics = requests.get(
    f"http://localhost:8041/api/v1/response/organizations/{ORG_ID}/metrics"
).json()

print(f"Average Resolution Time: {metrics['mttr']} hours")
print(f"Incidents This Month: {metrics['incidents_this_month']}")

# Get dashboard
dashboard = requests.get(
    f"http://localhost:8041/api/v1/response/organizations/{ORG_ID}/dashboard"
).json()

print(f"RTO Compliance Rate: {dashboard['rto_compliance_rate']}%")
print(f"RPO Compliance Rate: {dashboard['rpo_compliance_rate']}%")
```

## 📚 Next Steps

1. **Read Full Documentation**: [README.md](README.md)
2. **Explore API**: http://localhost:8041/docs
3. **Check Examples**: See VERIFICATION.md for complete examples
4. **Configure Production**: Update .env with production settings
5. **Set Up Monitoring**: Configure health check endpoints
6. **Enable Events**: Set up event bus for integrations

## 🆘 Troubleshooting

### Service Won't Start

```bash
# Check if port is in use
lsof -i :8041

# Check logs
LOG_LEVEL=DEBUG python3 main.py
```

### Database Connection Issues

```bash
# Test database connection
python3 -c "
from config import settings
print(settings.DATABASE_URL)
"

# Check database health
curl http://localhost:8041/health
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📞 Support

- **Documentation**: README.md
- **API Docs**: http://localhost:8041/docs
- **Health**: http://localhost:8041/health
- **Logs**: Check console output or LOG_FILE

## 🎉 You're Ready!

The Response module is now running and ready to handle incident response!

Start by:
1. Creating your first incident
2. Exploring the API documentation
3. Setting up response teams
4. Configuring your first RTO/RPO metrics

**Happy Incident Response! 🚀**
