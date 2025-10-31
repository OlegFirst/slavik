# TheHive Integration for BCM Platform

Complete integration between TheHive incident response platform and the BCM Platform for unified incident management and business continuity response.

## 🏗️ Architecture

```
BCM Platform (Odoo) ←→ TheHive Bridge Service ←→ TheHive + Cortex
                    ←→ Webhook Receiver      ←→ Elasticsearch + Cassandra
```

## 🚀 Features

### ✅ Incident Management Integration
- **Automatic case creation** from BCM incidents in TheHive
- **Bi-directional sync** between BCM incidents and TheHive cases
- **Status synchronization** (Open ↔ Active, Resolved ↔ Resolved)
- **Severity mapping** between BCM and TheHive scales
- **Task management** with BCM-specific response procedures

### ✅ Exercise Integration
- **Exercise tracking** through TheHive cases
- **Tabletop exercise** case management
- **Participant tracking** and task assignments
- **Exercise evaluation** through case resolution

### ✅ Real-time Webhooks
- **Real-time updates** from TheHive back to BCM Platform
- **Event-driven architecture** with webhook receivers
- **Secure webhook verification** with HMAC signatures
- **Automatic incident creation** from critical alerts

### ✅ BCM-Specific Enhancements
- **Custom fields** for business impact, affected processes, RTO/RPO
- **BCM response tasks** automatically created for incidents
- **Business continuity tags** for proper case categorization
- **Company isolation** through BCM Platform multi-tenancy

## 📦 Components

### 1. TheHive Client (`thehive_client.py`)
- Python client library for TheHive API v5
- BCM-specific case creation and management
- Alert-to-case promotion with BCM context
- Task and observable management

### 2. Bridge Service (`bridge_service.py`)
- FastAPI service providing REST endpoints
- Handles incident ↔ case synchronization
- Background task processing
- Metrics and health monitoring

### 3. Webhook Handler (`webhooks.py`)
- Receives real-time updates from TheHive
- Processes case, task, and alert events
- Syncs changes back to BCM Platform
- Automatic incident creation from alerts

### 4. Docker Stack (`docker-compose.thehive.yml`)
- Complete TheHive 5.x deployment
- Cassandra + Elasticsearch backends
- Cortex for observable analysis
- Integration services with health checks

## 🛠️ Setup & Deployment

### Prerequisites
- Docker & Docker Compose
- BCM Platform running with API access
- Network connectivity between services

### 1. Environment Configuration
```bash
# Copy and configure environment
cp .env.example .env

# Required variables
THEHIVE_API_KEY=your-thehive-api-key
ODOO_URL=http://bcm-platform:8069
ODOO_API_KEY=your-bcm-api-key
WEBHOOK_SECRET=your-webhook-secret
BRIDGE_API_KEY=your-bridge-api-key
```

### 2. Deploy TheHive Stack
```bash
# Start TheHive with all dependencies
docker-compose -f docker-compose.thehive.yml up -d

# Check service health
docker-compose -f docker-compose.thehive.yml ps
```

### 3. Initialize TheHive
```bash
# Access TheHive web interface
open http://localhost:9000

# Create initial admin user
# Configure organizations and users
# Set up API keys
```

### 4. Configure Integration
```bash
# Update TheHive webhook configuration
# Point to: http://thehive-webhook-receiver:8091/webhook/thehive

# Test bridge service
curl http://localhost:8090/health
```

## 🔧 API Endpoints

### Bridge Service (Port 8090)

#### Create Case from BCM Incident
```bash
POST /api/v1/incident/create-case
Content-Type: application/json
Authorization: Bearer <bridge-api-key>

{
  "incident_id": "bcm-inc-001",
  "name": "Server Outage - Critical Systems",
  "description": "Database server failure affecting patient records",
  "severity": "critical",
  "incident_type": "infrastructure_failure",
  "business_impact": "High - Patient care systems offline",
  "affected_processes": ["patient_registration", "ehr_access"],
  "company_id": "hospital-001",
  "tags": ["infrastructure", "database", "critical"]
}
```

#### Create Exercise Case
```bash
POST /api/v1/exercise/create-case
Content-Type: application/json
Authorization: Bearer <bridge-api-key>

{
  "exercise_id": "ex-001",
  "name": "Tabletop Exercise - Ransomware Response",
  "description": "Simulated ransomware attack exercise",
  "exercise_type": "tabletop",
  "scenario": "Healthcare facility ransomware incident",
  "objectives": ["Test response procedures", "Evaluate communication"],
  "participants": ["IT Team", "BCM Team", "Management"],
  "company_id": "hospital-001"
}
```

#### Sync Case Status
```bash
POST /api/v1/case/{case_id}/sync?bcm_incident_id=inc-001
Authorization: Bearer <bridge-api-key>
```

#### List Cases
```bash
GET /api/v1/cases?status=Open&severity=3&tags=bcm-incident
Authorization: Bearer <bridge-api-key>
```

### Webhook Receiver (Port 8091)

#### TheHive Webhooks
```bash
POST /webhook/thehive
Content-Type: application/json
X-TheHive-Signature: sha256=...

{
  "operation": "Update",
  "objectType": "case",
  "objectId": "case-123",
  "object": { ... },
  "requestId": "req-456",
  "timestamp": 1645123456
}
```

## 🔐 Security

### Authentication & Authorization
- **API Key authentication** for all endpoints
- **HMAC webhook verification** for TheHive events
- **TLS encryption** for all communications
- **Network isolation** through Docker networks

### Data Protection
- **Multi-tenant isolation** through company IDs
- **Sensitive data masking** in logs
- **Secure credential storage** through environment variables
- **Regular security updates** for all dependencies

## 📊 Monitoring & Logging

### Health Checks
- **Service health endpoints** for all components
- **Dependency health monitoring** (TheHive, Elasticsearch, etc.)
- **Docker health checks** with automatic restarts
- **Prometheus metrics** export (planned)

### Logging
- **Structured JSON logging** for all services
- **Request/response tracing** for debugging
- **Error alerting** for critical failures
- **Log aggregation** compatible with ELK stack

## 🔄 Data Flow Examples

### Incident Response Flow
1. **BCM Incident Created** → Bridge creates TheHive case
2. **TheHive Case Updated** → Webhook syncs status to BCM
3. **Tasks Completed** → Updates reflected in BCM incident
4. **Case Resolved** → BCM incident automatically closed

### Exercise Management Flow
1. **BCM Exercise Planned** → TheHive case created for tracking
2. **Exercise Executed** → Tasks updated in TheHive
3. **Results Documented** → Observations added to case
4. **Lessons Learned** → Synced back to BCM exercise record

### Alert-to-Incident Flow
1. **Alert Created in TheHive** → Evaluated for BCM relevance
2. **Critical Alert** → Automatic BCM incident creation
3. **Incident Response** → Full BCM workflow activation
4. **Resolution** → Both systems updated

## 📈 Metrics & KPIs

### Integration Metrics
- **Case creation rate** and success percentage
- **Sync latency** and failure rates
- **Webhook delivery** success/failure rates
- **API response times** and error rates

### Business Metrics
- **Incident response time** improvement
- **Exercise completion** tracking
- **Stakeholder engagement** in incident response
- **Process efficiency** through automation

## 🧪 Testing

### Unit Tests
```bash
# Run unit tests
pytest tests/unit/

# Run with coverage
pytest --cov=. tests/unit/
```

### Integration Tests
```bash
# Test TheHive API connectivity
pytest tests/integration/test_thehive_client.py

# Test webhook processing
pytest tests/integration/test_webhooks.py

# Test bridge service endpoints
pytest tests/integration/test_bridge_service.py
```

### End-to-End Tests
```bash
# Full workflow tests
pytest tests/e2e/

# Performance tests
pytest tests/performance/
```

## 🔧 Troubleshooting

### Common Issues

#### TheHive Connection Issues
```bash
# Check TheHive service status
docker-compose -f docker-compose.thehive.yml logs thehive

# Verify API key
curl -H "Authorization: Bearer $THEHIVE_API_KEY" http://localhost:9000/api/v1/status
```

#### Webhook Delivery Issues
```bash
# Check webhook receiver logs
docker-compose -f docker-compose.thehive.yml logs thehive-webhook-receiver

# Verify webhook configuration in TheHive
curl -H "Authorization: Bearer $THEHIVE_API_KEY" http://localhost:9000/api/config
```

#### Sync Issues
```bash
# Check bridge service logs
docker-compose -f docker-compose.thehive.yml logs thehive-bcm-bridge

# Test manual sync
curl -X POST -H "Authorization: Bearer $BRIDGE_API_KEY" \
  http://localhost:8090/api/v1/case/case-123/sync?bcm_incident_id=inc-001
```

## 🚀 Production Deployment

### High Availability Setup
- **Multiple bridge service instances** behind load balancer
- **TheHive cluster** with Cassandra replication
- **Elasticsearch cluster** for search performance
- **Redis for webhook queue** management

### Monitoring & Alerting
- **Prometheus + Grafana** for metrics visualization
- **ELK Stack** for log aggregation and analysis
- **PagerDuty integration** for critical alerts
- **Health check monitoring** with automatic restarts

### Backup & Recovery
- **Automated daily backups** of Cassandra and Elasticsearch
- **Configuration backup** for TheHive and bridge services  
- **Disaster recovery procedures** documented and tested
- **Point-in-time recovery** capability

---

## 📚 Additional Resources

- [TheHive Documentation](https://docs.thehive-project.org/)
- [Cortex Analyzers](https://github.com/TheHive-Project/Cortex-Analyzers)
- [BCM Platform API Documentation](../../../docs/api/)
- [ISO 22301 Implementation Guide](../../../docs/compliance/)
