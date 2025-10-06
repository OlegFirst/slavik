# Platform Orchestrator API - Usage Guide

## Overview

The Platform Orchestrator API provides comprehensive monitoring and management for all 12 BCM Platform services through a unified interface.

**Location**: `/Users/MD/AI-Platform-ISO/intelligent-core/workflow-intelligence/api/platform_orchestrator.py`

**Base Path**: `/api/v1/platform`

## Services Covered (12 Total)

### Core BCM Services (10 with Workflow Intelligence)

1. **Planning Service** (8011) - ISO 8.3 - Strategy & Planning
2. **Plans Service** (8023) - ISO 8.4 - Plans & Procedures
3. **BIA Service** (8012) - ISO 8.2.2 - Business Impact Analysis
4. **Compliance Service** (8014) - ISO 9.2, 10.1, 10.2 - Audits & Improvement
5. **Risk Service** (8013) - ISO 8.2.3 - Risk Assessment & Treatment
6. **Response Service** (8015) - ISO 8.4.5 - Incident Response
7. **Validation Service** (8016) - ISO 8.4.6 - Exercise & Testing
8. **Documents Service** (8017) - ISO 7.5 - Document Control
9. **Learning Service** (8018) - ISO 7.2 - Training & Competence
10. **Governance Service** (8019) - ISO 5.3, 7.1, 7.3 - Governance

### Infrastructure Services

11. **File Service** (8020) - Storage & Assets

### Community Services

12. **Portal** (8031) - ISO 7.4 - Knowledge Base & Forums
13. **Marketplace** (8032) - ISO 7.1 - Specialists & Projects

## API Endpoints

### Health & Status

#### 1. Platform-wide Health Check
```http
GET /api/v1/platform/health
```

**Response:**
```json
{
  "platform_status": "healthy",
  "total_services": 12,
  "healthy_services": 12,
  "degraded_services": 0,
  "unhealthy_services": 0,
  "unreachable_services": 0,
  "services": [
    {
      "service_key": "planning",
      "service_name": "Planning Service",
      "module": "planning",
      "status": "healthy",
      "response_time_ms": 45.23,
      "workflow_intelligence_enabled": true,
      "iso_clause": "8.3",
      "component": "bcm-strategy",
      "timestamp": "2025-10-03T12:00:00Z"
    }
  ],
  "timestamp": "2025-10-03T12:00:00Z",
  "uptime_percentage": 100.0
}
```

**Status Levels:**
- `healthy`: All services operational
- `degraded`: Some services down but core functions work (80%+ healthy)
- `critical`: Critical services down (50%+ healthy)
- `down`: Platform unavailable (<50% healthy)

#### 2. Platform Status
```http
GET /api/v1/platform/status
```

**Response:**
```json
{
  "platform": "BCM Platform ISO 22301",
  "version": "2.0.0",
  "total_services": 12,
  "workflow_intelligence_services": 10,
  "components": {
    "bcm-strategy": [...],
    "bcm-plans": [...],
    "bcm-bia": [...]
  },
  "iso_coverage": {
    "clauses_covered": ["8.3", "8.4", "8.2.2", ...],
    "total_clauses": 13
  },
  "architecture": {
    "core_bcm_services": 10,
    "community_services": 2,
    "storage_services": 1
  }
}
```

#### 3. Service Registry
```http
GET /api/v1/platform/services
```

Returns complete list of all services with metadata.

### Per-Service Operations

#### 4. Individual Service Health
```http
GET /api/v1/platform/services/{service_name}/health
```

**Example:**
```bash
curl http://localhost:8000/api/v1/platform/services/planning/health
```

**Response:**
```json
{
  "service": "planning",
  "status": "healthy",
  "data": {
    "service": "Planning Service",
    "status": "healthy",
    "timestamp": "2025-10-03T12:00:00Z"
  }
}
```

#### 5. Individual Service Metrics
```http
GET /api/v1/platform/services/{service_name}/metrics
```

Returns Prometheus metrics from specific service.

#### 6. Individual Service Status
```http
GET /api/v1/platform/services/{service_name}/status
```

**Response:**
```json
{
  "service_key": "planning",
  "name": "Planning Service",
  "url": "http://localhost:8011",
  "module": "planning",
  "iso_clause": "8.3",
  "component": "bcm-strategy",
  "description": "Business Continuity Strategy & Planning",
  "workflow_intelligence": true,
  "health": {
    "is_healthy": true,
    "data": {...}
  },
  "endpoints": {
    "health": "http://localhost:8011/health",
    "metrics": "http://localhost:8011/metrics",
    "api_docs": "http://localhost:8011/docs"
  }
}
```

### Metrics Aggregation

#### 7. Platform Metrics Summary
```http
GET /api/v1/platform/metrics/summary
```

Aggregates metrics from all services concurrently.

**Response:**
```json
{
  "platform_metrics": {
    "total_services": 12,
    "services_reporting": 10,
    "services_silent": 2
  },
  "services": [
    {
      "service_key": "planning",
      "service_name": "Planning Service",
      "available": true,
      "metrics": {...}
    }
  ]
}
```

#### 8. Service-Specific Metrics
```http
GET /api/v1/platform/metrics/{service_name}
```

### Workflow Intelligence Aggregation

#### 9. All Benchmarks
```http
GET /api/v1/platform/workflow-intelligence/benchmarks/all
GET /api/v1/platform/workflow-intelligence/benchmarks/all?industry=finance
GET /api/v1/platform/workflow-intelligence/benchmarks/all?industry=healthcare&org_size=medium
```

Aggregates benchmarks from all 10 services with Workflow Intelligence.

**Response:**
```json
{
  "filters": {
    "industry": "finance",
    "org_size": "all"
  },
  "total_wi_services": 10,
  "successful_services": 10,
  "failed_services": 0,
  "benchmarks": [
    {
      "service": "planning",
      "module": "planning",
      "iso_clause": "8.3",
      "status": "success",
      "data": {
        "avg_duration_days": 45.2,
        "avg_stakeholders": 12,
        ...
      }
    }
  ]
}
```

#### 10. Cross-Service Case Search
```http
GET /api/v1/platform/workflow-intelligence/cases/search
GET /api/v1/platform/workflow-intelligence/cases/search?industry=finance&limit=20
GET /api/v1/platform/workflow-intelligence/cases/search?module=bia&org_size=large
```

Search similar cases across all services with Workflow Intelligence.

**Query Parameters:**
- `industry`: Filter by industry
- `org_size`: Filter by organization size
- `module`: Filter by specific module
- `limit`: Max results (1-100, default: 10)

**Response:**
```json
{
  "total_cases": 15,
  "cases": [
    {
      "case_id": "...",
      "industry": "finance",
      "org_size": "large",
      "source_service": "planning",
      "source_module": "planning",
      "relevance_score": 0.95,
      ...
    }
  ],
  "sources": ["planning", "bia", "compliance"]
}
```

#### 11. Platform Analytics
```http
GET /api/v1/platform/workflow-intelligence/analytics
GET /api/v1/platform/workflow-intelligence/analytics?days=90
```

Platform-wide workflow intelligence analytics.

**Response:**
```json
{
  "period_days": 30,
  "platform_totals": {
    "total_workflows": 1250,
    "total_cases_collected": 456,
    "total_ai_advice_requests": 2340,
    "total_benchmarks_calculated": 120
  },
  "by_module": {
    "planning": {
      "workflows": 180,
      "cases_collected": 45,
      "ai_advice_requests": 234,
      "completion_rate": 0.92
    },
    ...
  },
  "ai_usage": {
    "total_advice_requests": 2340,
    "acceptance_rate": 0.78,
    "avg_relevance_score": 0.85
  },
  "learning": {
    "total_industries_covered": 15,
    "total_org_sizes_covered": 4,
    "coverage_percentage": 85.0,
    "growth_rate": 12.5
  }
}
```

### Admin Operations

#### 12. Platform-wide Sync
```http
POST /api/v1/platform/admin/sync-all
```

Triggers synchronization across all services:
- Benchmark recalculation
- Cache refresh
- Database cleanup

**Response:**
```json
{
  "operation": "platform_sync",
  "total_services": 10,
  "successful": 10,
  "failed": 0,
  "results": [
    {
      "service": "planning",
      "status": "success",
      "message": "Sync triggered"
    }
  ]
}
```

#### 13. Comprehensive Health Check
```http
POST /api/v1/platform/admin/health-check-all
```

Admin-level health check with diagnostics.

**Response:**
```json
{
  "health": {...},
  "diagnostics": {
    "database_connections": "operational",
    "cache_status": "operational",
    "eventbus_status": "operational",
    "storage_status": "operational"
  }
}
```

#### 14. Platform Statistics
```http
GET /api/v1/platform/admin/stats
```

Comprehensive statistics for administrators.

**Response:**
```json
{
  "platform": {
    "total_services": 12,
    "workflow_intelligence_services": 10,
    "total_tenants": 45,
    "total_users": 1250,
    "total_workflows_all_time": 25000
  },
  "services": {
    "by_component": {...},
    "by_status": {...}
  },
  "performance": {
    "avg_response_time_ms": 125.5,
    "avg_workflow_duration_days": 32.5,
    "avg_db_query_ms": 15.2,
    "cache_hit_rate": 0.85
  },
  "workflow_intelligence": {
    "total_cases_library": 5600,
    "total_benchmarks": 230,
    "total_ai_advice_given": 12500,
    "ai_acceptance_rate": 0.78,
    "cases_per_day": 45.2,
    "learning_acceleration": 1.35
  }
}
```

### Discovery

#### 15. Platform Information
```http
GET /api/v1/platform/
```

High-level platform overview.

## Integration Example

### Python Client

```python
import httpx
import asyncio

class PlatformClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    async def check_health(self):
        """Check platform health"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/platform/health"
            )
            return response.json()

    async def get_all_benchmarks(self, industry=None, org_size=None):
        """Get benchmarks from all services"""
        params = {}
        if industry:
            params["industry"] = industry
        if org_size:
            params["org_size"] = org_size

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/platform/workflow-intelligence/benchmarks/all",
                params=params
            )
            return response.json()

    async def search_cases(self, industry=None, module=None, limit=10):
        """Search cases across services"""
        params = {"limit": limit}
        if industry:
            params["industry"] = industry
        if module:
            params["module"] = module

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/platform/workflow-intelligence/cases/search",
                params=params
            )
            return response.json()

# Usage
async def main():
    client = PlatformClient()

    # Check platform health
    health = await client.check_health()
    print(f"Platform status: {health['platform_status']}")
    print(f"Healthy services: {health['healthy_services']}/{health['total_services']}")

    # Get benchmarks for finance industry
    benchmarks = await client.get_all_benchmarks(industry="finance")
    print(f"Benchmarks from {benchmarks['successful_services']} services")

    # Search BIA cases
    cases = await client.search_cases(module="bia", limit=5)
    print(f"Found {cases['total_cases']} BIA cases")

asyncio.run(main())
```

### JavaScript/TypeScript Client

```typescript
class PlatformClient {
  constructor(private baseUrl = 'http://localhost:8000') {}

  async checkHealth(): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/platform/health`
    );
    return response.json();
  }

  async getAllBenchmarks(
    industry?: string,
    orgSize?: string
  ): Promise<any> {
    const params = new URLSearchParams();
    if (industry) params.append('industry', industry);
    if (orgSize) params.append('org_size', orgSize);

    const response = await fetch(
      `${this.baseUrl}/api/v1/platform/workflow-intelligence/benchmarks/all?${params}`
    );
    return response.json();
  }

  async searchCases(options: {
    industry?: string;
    module?: string;
    limit?: number;
  }): Promise<any> {
    const params = new URLSearchParams();
    if (options.industry) params.append('industry', options.industry);
    if (options.module) params.append('module', options.module);
    if (options.limit) params.append('limit', options.limit.toString());

    const response = await fetch(
      `${this.baseUrl}/api/v1/platform/workflow-intelligence/cases/search?${params}`
    );
    return response.json();
  }
}

// Usage
const client = new PlatformClient();

// Check health
const health = await client.checkHealth();
console.log(`Platform: ${health.platform_status}`);

// Get benchmarks
const benchmarks = await client.getAllBenchmarks('finance', 'large');
console.log(`Benchmarks: ${benchmarks.successful_services} services`);

// Search cases
const cases = await client.searchCases({
  module: 'compliance',
  limit: 10
});
console.log(`Cases: ${cases.total_cases}`);
```

## Monitoring Dashboard Example

```bash
# Health check every 30 seconds
watch -n 30 'curl -s http://localhost:8000/api/v1/platform/health | jq ".platform_status, .healthy_services"'

# Get metrics summary
curl http://localhost:8000/api/v1/platform/metrics/summary | jq

# Check specific service
curl http://localhost:8000/api/v1/platform/services/planning/health | jq

# Get platform analytics
curl http://localhost:8000/api/v1/platform/workflow-intelligence/analytics?days=7 | jq
```

## Performance Characteristics

### Concurrent Health Checks
- All 12 services checked in parallel
- Total time: ~50-200ms (depending on slowest service)
- Timeout: 3 seconds per service
- Non-blocking: Failures don't block other checks

### Metrics Aggregation
- Concurrent fetching from all services
- Timeout: 3 seconds per service
- Graceful degradation: Partial results returned if some services fail

### Workflow Intelligence Queries
- Concurrent queries to 10 WI-enabled services
- Smart result aggregation
- Cross-module relevance ranking

## Error Handling

All endpoints return consistent error formats:

```json
{
  "service": "planning",
  "status": "error",
  "error": "Connection timeout after 3s",
  "timestamp": "2025-10-03T12:00:00Z"
}
```

## Integration with Existing Systems

The Platform Orchestrator can be integrated as a standalone service or mounted in an existing FastAPI application:

```python
from fastapi import FastAPI
from workflow_intelligence.api import platform_orchestrator_router

app = FastAPI()

# Mount the platform orchestrator
app.include_router(platform_orchestrator_router)

# Now available at /api/v1/platform/*
```

## Future Enhancements

Planned features:
- WebSocket support for real-time health updates
- Alerting integration (PagerDuty, Slack)
- Advanced analytics and trend analysis
- Automated service recovery
- Intelligent routing based on service health
- Performance profiling and bottleneck detection

## Support

For issues or questions:
- Check service logs for detailed error messages
- Verify all services are running and accessible
- Ensure database connections are healthy
- Check network connectivity between services
