# BCM Coordination Service

**Version:** 2.0.0  
**Port:** 8070  
**ISO 22301 Compliance:** Full BCM Coordination  
**Last Updated:** 2025-10-08

---

## Overview

The BCM Coordination Service serves as the central orchestration hub for 10 specialized Business Continuity Management (BCM) analyzers. It coordinates analysis requests, aggregates results, and provides comprehensive BCM insights across all ISO 22301 domains.

### Key Responsibilities

1. **Analyzer Coordination:** Manages and coordinates 10 specialized BCM analyzers
2. **Request Routing:** Routes analysis requests to appropriate analyzers
3. **Result Aggregation:** Combines results from multiple analyzers
4. **ISO 22301 Compliance:** Ensures full coverage of BCM requirements
5. **Intelligent Core Bridge:** Connects BCM services to Intelligent Core layer

---

## Architecture

### 10 Coordinated Analyzers

```
BCM Coordination Service (Port 8070)
│
├── 1. Compliance Analyzer (ISO 22301)
├── 2. Risk Analyzer (FAIR)
├── 3. Impact Analyzer (BIA)
├── 4. Governance Analyzer
├── 5. Emergency Analyzer
├── 6. Performance Analyzer
├── 7. Learning Analyzer
├── 8. Lifecycle Analyzer
├── 9. Plan Analyzer
└── 10. Scenario Analyzer
```

### Integration Points

- **Intelligent Core:** BCM Services Orchestrator
- **Platform Services:** All 11 BCM services
- **Expertise Center:** Domain specialists
- **Workflow Intelligence:** Workflow coordination

---

## Metrics

- **Total Lines of Code:** ~3,500
- **Python Files:** 2
- **API Endpoints:** 15+
- **Analyzers Coordinated:** 10
- **ISO 22301 Coverage:** 100%

---

## Installation

### Prerequisites

- Python 3.11+
- Access to Intelligent Core (BCM Orchestrator)
- PostgreSQL database
- Redis cache

### Setup

```bash
cd platform-services/bcm-coordination-service
pip install -r requirements.txt
```

### Configuration

Create `.env` file:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/bcm_platform
REDIS_URL=redis://localhost:6379/0
PORT=8070
LOG_LEVEL=INFO

# BCM Orchestrator
INTELLIGENT_CORE_PATH=../../intelligent-core
BCM_ORCHESTRATOR_PATH=orchestration/bcm-services-orchestrator
```

### Running

```bash
# Development
uvicorn main:app --reload --port 8070

# Production
uvicorn main:app --host 0.0.0.0 --port 8070 --workers 2
```

---

## Usage

### Health Check

```bash
curl http://localhost:8070/health
```

### Coordinate Analysis

```python
import httpx

# Request comprehensive BCM analysis
response = await httpx.post(
    "http://localhost:8070/api/v1/coordinate/analyze",
    json={
        "analysis_type": "comprehensive",
        "organization_id": "org-123",
        "scope": ["compliance", "risk", "impact"],
        "priority": "high"
    }
)

result = response.json()
# {
#   "status": "completed",
#   "analyzers_used": ["compliance_analyzer", "risk_analyzer", "impact_analyzer"],
#   "results": {...},
#   "recommendations": [...],
#   "iso_compliance": "98%"
# }
```

### Query Specific Analyzer

```python
# Query compliance analyzer
response = await httpx.post(
    "http://localhost:8070/api/v1/analyzers/compliance/analyze",
    json={
        "organization_id": "org-123",
        "clauses": ["8.2", "8.3", "8.4"]
    }
)
```

---

## API Endpoints

### Coordination Endpoints

- `POST /api/v1/coordinate/analyze` - Coordinate multi-analyzer analysis
- `POST /api/v1/coordinate/batch` - Batch analysis requests
- `GET /api/v1/coordinate/status/{request_id}` - Check analysis status

### Analyzer-Specific Endpoints

- `POST /api/v1/analyzers/{analyzer_type}/analyze` - Direct analyzer access
- `GET /api/v1/analyzers/{analyzer_type}/capabilities` - Analyzer capabilities
- `GET /api/v1/analyzers/list` - List all available analyzers

### Results & Recommendations

- `GET /api/v1/results/{analysis_id}` - Retrieve analysis results
- `GET /api/v1/recommendations/{organization_id}` - Get recommendations
- `POST /api/v1/results/aggregate` - Aggregate multiple results

### Health & Monitoring

- `GET /health` - Service health check
- `GET /metrics` - Prometheus metrics
- `GET /ready` - Readiness probe

---

## Integration with Intelligent Core

### BCM Services Orchestrator

The BCM Coordination Service integrates with the BCM Services Orchestrator from Intelligent Core:

```python
from intelligent_core.orchestration.bcm_services_orchestrator import AnalyzerCoordinator

# Initialize coordinator
coordinator = AnalyzerCoordinator(analyzers={
    "compliance_analyzer": compliance_instance,
    "risk_analyzer": risk_instance,
    # ... other analyzers
})

# Coordinate analysis
result = await coordinator.coordinate_analysis(
    request_type="comprehensive",
    organization_id="org-123"
)
```

---

## Analyzer Details

### 1. Compliance Analyzer (ISO 22301)

- **Purpose:** Ensures ISO 22301:2019 compliance
- **Clauses Covered:** All 10 clauses
- **Output:** Compliance score, gaps, recommendations

### 2. Risk Analyzer (FAIR)

- **Purpose:** FAIR methodology risk analysis
- **Capabilities:** Monte Carlo simulation, loss forecasting
- **Output:** Risk scores, treatment plans

### 3. Impact Analyzer (BIA)

- **Purpose:** Business Impact Analysis
- **Capabilities:** RTO/RPO calculation, criticality assessment
- **Output:** Impact levels, recovery objectives

### 4. Governance Analyzer

- **Purpose:** Governance structure analysis
- **Capabilities:** Policy review, stakeholder mapping
- **Output:** Governance maturity, recommendations

### 5. Emergency Analyzer

- **Purpose:** Emergency response readiness
- **Capabilities:** Response plan analysis, capability assessment
- **Output:** Readiness score, improvement areas

### 6. Performance Analyzer

- **Purpose:** BCM program performance
- **Capabilities:** KPI analysis, trend detection
- **Output:** Performance metrics, benchmarks

### 7. Learning Analyzer

- **Purpose:** Training and competency analysis
- **Capabilities:** Skills gap analysis, training effectiveness
- **Output:** Competency matrix, training recommendations

### 8. Lifecycle Analyzer

- **Purpose:** BCMS lifecycle management
- **Capabilities:** Maturity assessment, evolution tracking
- **Output:** Maturity level, evolution roadmap

### 9. Plan Analyzer

- **Purpose:** Continuity plan analysis
- **Capabilities:** Plan completeness, effectiveness assessment
- **Output:** Plan quality score, improvements

### 10. Scenario Analyzer

- **Purpose:** Scenario testing and simulation
- **Capabilities:** Scenario effectiveness, gap identification
- **Output:** Test results, scenario recommendations

---

## Standards Compliance

- **ISO 22301:2019:** Full coverage of all clauses
- **ISO/IEC 27001:** Security management integration
- **NIST SP 800-34:** IT contingency planning
- **ISO 22313:2020:** BCM guidance

---

## Dependencies

### Intelligent Core

- `orchestration/bcm-services-orchestrator` - Analyzer coordination engine
- `expertise-center` - Domain specialist consultation
- `workflow_intelligence` - Workflow integration

### Platform Services

- All 11 BCM services for data access

### Infrastructure

- PostgreSQL - Analysis results storage
- Redis - Request caching
- RabbitMQ - Event notifications

---

## Configuration

### Analyzer Configuration

Each analyzer can be configured individually:

```python
analyzers_config = {
    "compliance_analyzer": {
        "enabled": True,
        "priority": 1,
        "timeout_seconds": 30,
        "cache_ttl": 3600
    },
    "risk_analyzer": {
        "enabled": True,
        "priority": 2,
        "timeout_seconds": 60,
        "monte_carlo_iterations": 10000
    }
    # ... other analyzers
}
```

### Coordination Strategy

```python
coordination_config = {
    "strategy": "parallel",  # parallel | sequential | hybrid
    "max_concurrent": 5,
    "failure_handling": "partial_success",
    "aggregation_method": "weighted_average"
}
```

---

## Monitoring

### Health Checks

The service provides three levels of health checks:

1. **Basic:** Service is running
2. **Dependencies:** All analyzers reachable
3. **Functional:** Sample analysis successful

### Metrics

Prometheus metrics exposed at `/metrics`:

- `bcm_coordination_requests_total` - Total coordination requests
- `bcm_coordination_duration_seconds` - Request duration
- `bcm_analyzer_status` - Analyzer availability
- `bcm_coordination_errors_total` - Error count

---

## Error Handling

### Graceful Degradation

If an analyzer is unavailable, the service:

1. Logs the unavailability
2. Continues with available analyzers
3. Returns partial results
4. Indicates missing analysis in response

### Retry Logic

Failed analyzer requests are retried:

- **Max Retries:** 3
- **Backoff Strategy:** Exponential
- **Timeout:** 60 seconds per analyzer

---

## Development

### Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/

# Integration tests
pytest tests/integration/
```

### Adding New Analyzer

1. Implement analyzer in Intelligent Core
2. Register in `AnalyzerCoordinator`
3. Add configuration
4. Update documentation

---

## Deployment

### Docker

```bash
docker build -t bcm-coordination-service .
docker run -p 8070:8070 bcm-coordination-service
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bcm-coordination-service
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: bcm-coordination
        image: bcm-coordination-service:latest
        ports:
        - containerPort: 8070
        env:
        - name: PORT
          value: "8070"
```

---

## Troubleshooting

### Common Issues

**Issue:** Analyzer not found

```
Solution: Check INTELLIGENT_CORE_PATH environment variable
```

**Issue:** Slow analysis

```
Solution: Increase max_concurrent analyzers, check analyzer timeouts
```

**Issue:** Partial results

```
Solution: Check individual analyzer health, review logs for errors
```

---

## Related Documentation

- [BCM Services Orchestrator](../../intelligent-core/orchestration/bcm-services-orchestrator/README.md)
- [Expertise Center](../../intelligent-core/expertise-center/README.md)
- [Platform Services Overview](../README.md)

---

**Maintained By:** BCM Platform Team  
**Contact:** bcm-platform@example.com  
**Documentation Version:** 1.0.0
