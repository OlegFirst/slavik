# BIA Service - API Documentation

**Service**: BIA Service
**Base URL**: `http://localhost:8012` (development)
**API Prefix**: `/api/bia`
**Version**: 1.0.0

## Table of Contents

1. [Authentication](#authentication)
2. [Error Handling](#error-handling)
3. [Process Management Endpoints](#process-management-endpoints)
4. [AI-Powered Analysis Endpoints](#ai-powered-analysis-endpoints)
5. [Bulk Operations Endpoints](#bulk-operations-endpoints)
6. [Reporting Endpoints](#reporting-endpoints)
7. [Health & Monitoring Endpoints](#health--monitoring-endpoints)

## Authentication

All API endpoints (except `/health`) require JWT Bearer token authentication.

### Request Headers

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Development Mode

For development/testing, use the `X-Dev-User` header:

```http
X-Dev-User: {"user_id": "user_123", "tenant_id": "tenant_123", "permissions": ["BIA_CREATE", "BIA_VIEW"]}
```

### Required Permissions

| Endpoint | Required Permission |
|----------|---------------------|
| POST /processes | BIA_CREATE |
| GET /processes | BIA_VIEW |
| GET /processes/{id} | BIA_VIEW |
| PUT /processes/{id} | BIA_UPDATE |
| DELETE /processes/{id} | BIA_DELETE |
| POST /processes/{id}/complete | BIA_COMPLETE |
| POST /processes/{id}/suggest-rto | BIA_AI_SUGGEST |
| POST /processes/{id}/discover-dependencies | BIA_AI_SUGGEST |

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message",
  "error_code": "TENANT_MISMATCH",
  "status_code": 403
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created successfully |
| 400 | Bad request - validation error |
| 401 | Unauthorized - missing or invalid JWT |
| 403 | Forbidden - tenant mismatch or insufficient permissions |
| 404 | Resource not found |
| 422 | Business rule violation |
| 500 | Internal server error |

### Common Error Codes

- `VALIDATION_ERROR` - Invalid input data
- `TENANT_MISMATCH` - User cannot access resource from different tenant
- `PERMISSION_DENIED` - User lacks required permission
- `RESOURCE_NOT_FOUND` - Process not found
- `BUSINESS_RULE_VIOLATION` - Business logic constraint violated

## Process Management Endpoints

### 1. Create BIA Process

Creates a new Business Impact Analysis process.

**Endpoint:** `POST /api/bia/processes`

**Request Body:**

```json
{
  "tenant_id": "tenant_123",
  "name": "Payment Processing System",
  "description": "Core payment processing platform",
  "criticality": "critical",
  "industry": "financial_services",
  "rto_hours": 2.0,
  "rpo_hours": 0.5,
  "mtpd_hours": 4.0,
  "financial_impact": {
    "1_hour": 50000,
    "4_hours": 200000,
    "8_hours": 400000,
    "24_hours": 1200000,
    "1_week": 8400000,
    "1_month": 36000000
  },
  "operational_impact": "Complete loss of payment processing capability",
  "reputational_impact": "severe",
  "regulatory_impact": "high",
  "dependencies": [
    {
      "type": "technology",
      "name": "Payment Gateway API",
      "description": "Third-party payment gateway",
      "criticality": 5,
      "is_upstream": false,
      "is_downstream": true
    },
    {
      "type": "process",
      "name": "Customer Authentication",
      "criticality": 5,
      "is_upstream": true,
      "is_downstream": false
    }
  ],
  "resource_requirements": {
    "minimum_staff": 5,
    "key_personnel": ["Payment Engineer", "Database Admin"],
    "facilities": ["Primary Data Center"],
    "technology": ["Payment Gateway", "Database Cluster"],
    "information": ["Transaction Database", "Customer Data"],
    "materials": ["Network Infrastructure"]
  },
  "who_tier": "tier_1",
  "patient_safety_impact": "critical"
}
```

**Response:** `201 Created`

```json
{
  "id": 1,
  "tenant_id": "tenant_123",
  "name": "Payment Processing System",
  "description": "Core payment processing platform",
  "criticality": "critical",
  "industry": "financial_services",
  "rto_hours": 2.0,
  "rpo_hours": 0.5,
  "mtpd_hours": 4.0,
  "financial_impact": {
    "1_hour": 50000,
    "4_hours": 200000,
    "8_hours": 400000,
    "24_hours": 1200000,
    "1_week": 8400000,
    "1_month": 36000000
  },
  "dependencies": [...],
  "resource_requirements": {...},
  "status": "draft",
  "created_at": "2025-10-09T10:30:00Z",
  "updated_at": "2025-10-09T10:30:00Z",
  "completed_at": null
}
```

### 2. List BIA Processes

Retrieves a list of BIA processes with optional filtering.

**Endpoint:** `GET /api/bia/processes`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | string | Yes | Tenant identifier |
| criticality | string | No | Filter by criticality level |
| status | string | No | Filter by status |
| industry | string | No | Filter by industry |
| limit | integer | No | Max results (default: 100) |
| offset | integer | No | Pagination offset (default: 0) |

**Example Request:**

```http
GET /api/bia/processes?tenant_id=tenant_123&criticality=critical&status=completed
```

**Response:** `200 OK`

```json
{
  "total": 5,
  "limit": 100,
  "offset": 0,
  "processes": [
    {
      "id": 1,
      "tenant_id": "tenant_123",
      "name": "Payment Processing System",
      "criticality": "critical",
      "rto_hours": 2.0,
      "status": "completed",
      "created_at": "2025-10-09T10:30:00Z"
    }
  ]
}
```

### 3. Get BIA Process

Retrieves detailed information about a specific BIA process.

**Endpoint:** `GET /api/bia/processes/{id}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| id | integer | Process ID |

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | string | Yes | Tenant identifier |

**Response:** `200 OK`

```json
{
  "id": 1,
  "tenant_id": "tenant_123",
  "name": "Payment Processing System",
  "description": "Core payment processing platform",
  "criticality": "critical",
  "industry": "financial_services",
  "rto_hours": 2.0,
  "rpo_hours": 0.5,
  "mtpd_hours": 4.0,
  "financial_impact": {...},
  "dependencies": [...],
  "resource_requirements": {...},
  "status": "completed",
  "created_at": "2025-10-09T10:30:00Z",
  "updated_at": "2025-10-09T11:00:00Z",
  "completed_at": "2025-10-09T11:00:00Z"
}
```

### 4. Update BIA Process

Updates an existing BIA process.

**Endpoint:** `PUT /api/bia/processes/{id}`

**Request Body:** Partial update supported (send only fields to update)

```json
{
  "tenant_id": "tenant_123",
  "rto_hours": 1.5,
  "rpo_hours": 0.25,
  "financial_impact": {
    "1_hour": 60000,
    "4_hours": 240000
  }
}
```

**Response:** `200 OK`

Returns updated BIAProcess object.

### 5. Delete BIA Process

Deletes a BIA process.

**Endpoint:** `DELETE /api/bia/processes/{id}`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | string | Yes | Tenant identifier |

**Response:** `200 OK`

```json
{
  "message": "BIA process deleted successfully",
  "process_id": 1
}
```

### 6. Mark Process as Completed

Marks a BIA process as completed.

**Endpoint:** `POST /api/bia/processes/{id}/complete`

**Request Body:**

```json
{
  "tenant_id": "tenant_123"
}
```

**Response:** `200 OK`

Returns updated BIAProcess with status="completed" and completed_at timestamp.

## AI-Powered Analysis Endpoints

### 7. AI RTO/RPO Suggestion

Gets AI-powered suggestions for RTO, RPO, and MTPD based on process characteristics.

**Endpoint:** `POST /api/bia/processes/{id}/suggest-rto`

**Request Body:**

```json
{
  "tenant_id": "tenant_123"
}
```

**Response:** `200 OK`

```json
{
  "suggested_rto_hours": 2.0,
  "suggested_rpo_hours": 1.0,
  "suggested_mtpd_hours": 4.0,
  "confidence_score": 0.85,
  "reasoning": "Based on CRITICAL criticality and financial impact of $200K at 4 hours, RTO of 2 hours is recommended. Industry benchmark for financial services payment processing is 1-4 hours RTO.",
  "industry_benchmark": "Financial Services - Payment Processing: RTO 1-4 hours, RPO 0.5-2 hours",
  "alternative_scenarios": [
    {
      "scenario": "Conservative",
      "rto_hours": 1.0,
      "rpo_hours": 0.5,
      "cost_impact": "Higher infrastructure costs"
    },
    {
      "scenario": "Balanced",
      "rto_hours": 2.0,
      "rpo_hours": 1.0,
      "cost_impact": "Optimal cost/resilience balance"
    },
    {
      "scenario": "Cost-Optimized",
      "rto_hours": 4.0,
      "rpo_hours": 2.0,
      "cost_impact": "Lower infrastructure costs"
    }
  ]
}
```

### 8. AI Dependency Discovery

Discovers potential dependencies for a process using AI.

**Endpoint:** `POST /api/bia/processes/{id}/discover-dependencies`

**Request Body:**

```json
{
  "tenant_id": "tenant_123"
}
```

**Response:** `200 OK`

```json
{
  "discovered_dependencies": [
    {
      "type": "technology",
      "name": "Load Balancer",
      "description": "Distributes traffic across payment servers",
      "criticality": 5,
      "confidence": 0.9
    },
    {
      "type": "process",
      "name": "Fraud Detection",
      "description": "Real-time fraud screening",
      "criticality": 4,
      "confidence": 0.85
    }
  ],
  "total_discovered": 2
}
```

## Bulk Operations Endpoints

### 9. Bulk Create Processes

Creates multiple BIA processes in parallel.

**Endpoint:** `POST /api/bia/processes/bulk`

**Request Body:**

```json
{
  "processes": [
    {
      "tenant_id": "tenant_123",
      "name": "Process 1",
      "criticality": "high",
      "rto_hours": 4.0
    },
    {
      "tenant_id": "tenant_123",
      "name": "Process 2",
      "criticality": "medium",
      "rto_hours": 8.0
    }
  ],
  "max_concurrency": 10
}
```

**Response:** `200 OK`

```json
{
  "total_requested": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "status": "success",
      "process_id": 1,
      "name": "Process 1"
    },
    {
      "status": "success",
      "process_id": 2,
      "name": "Process 2"
    }
  ]
}
```

### 10. Bulk Update Processes

Updates multiple processes in parallel.

**Endpoint:** `PATCH /api/bia/processes/bulk`

**Request Body:**

```json
{
  "updates": [
    {
      "id": 1,
      "tenant_id": "tenant_123",
      "rto_hours": 3.0
    },
    {
      "id": 2,
      "tenant_id": "tenant_123",
      "rto_hours": 6.0
    }
  ],
  "max_concurrency": 10
}
```

**Response:** `200 OK`

Similar to bulk create response.

### 11. Bulk Delete Processes

Deletes multiple processes in parallel.

**Endpoint:** `DELETE /api/bia/processes/bulk`

**Request Body:**

```json
{
  "process_ids": [1, 2, 3],
  "tenant_id": "tenant_123",
  "max_concurrency": 10
}
```

**Response:** `200 OK`

### 12. Validate Bulk Import

Validates bulk data before import without creating records.

**Endpoint:** `POST /api/bia/processes/bulk/validate`

**Request Body:**

```json
{
  "processes": [...]
}
```

**Response:** `200 OK`

```json
{
  "valid": true,
  "total_processes": 2,
  "errors": [],
  "warnings": [
    "Process 'Process 1': RTO is below industry benchmark"
  ]
}
```

## Reporting Endpoints

### 13. Summary Report

Generates executive summary report for a tenant.

**Endpoint:** `GET /api/bia/reports/summary`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | string | Yes | Tenant identifier |

**Response:** `200 OK`

```json
{
  "tenant_id": "tenant_123",
  "total_processes": 50,
  "critical_processes": 12,
  "high_priority_processes": 18,
  "completed_bia_count": 45,
  "average_rto_hours": 6.5,
  "average_rpo_hours": 2.3,
  "total_financial_impact_24h": 15000000,
  "processes_by_criticality": {
    "critical": 12,
    "high": 18,
    "medium": 15,
    "low": 5
  },
  "processes_by_status": {
    "completed": 45,
    "in_progress": 3,
    "draft": 2
  },
  "top_dependencies": [
    {
      "name": "Payment Gateway",
      "count": 8,
      "type": "technology"
    }
  ]
}
```

### 14. Critical Processes Report

Lists all critical processes with detailed information.

**Endpoint:** `GET /api/bia/reports/critical-processes`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | string | Yes | Tenant identifier |
| min_criticality | string | No | Minimum criticality level (default: "high") |

**Response:** `200 OK`

```json
{
  "total_critical": 12,
  "processes": [
    {
      "id": 1,
      "name": "Payment Processing System",
      "criticality": "critical",
      "rto_hours": 2.0,
      "financial_impact_24h": 1200000,
      "dependencies_count": 5
    }
  ]
}
```

### 15. Dependencies Report

Generates dependency mapping report.

**Endpoint:** `GET /api/bia/reports/dependencies`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | string | Yes | Tenant identifier |
| process_id | integer | No | Filter by specific process |

**Response:** `200 OK`

```json
{
  "dependency_graph": [
    {
      "process_id": 1,
      "process_name": "Payment Processing",
      "upstream_dependencies": [
        {
          "name": "Customer Authentication",
          "type": "process",
          "criticality": 5
        }
      ],
      "downstream_dependencies": [
        {
          "name": "Payment Gateway",
          "type": "technology",
          "criticality": 5
        }
      ]
    }
  ]
}
```

## Health & Monitoring Endpoints

### 16. Health Check

Service health status.

**Endpoint:** `GET /health`

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "service": "bia",
  "iso_clause": "8.2.2",
  "port": 8012,
  "features": {
    "ai_enabled": true,
    "who_tier": true,
    "supply_chain": true,
    "eventbus": true
  },
  "cache": {
    "enabled": true,
    "type": "redis"
  }
}
```

### 17. Cache Metrics

Cache performance metrics.

**Endpoint:** `GET /metrics/cache`

**Response:** `200 OK`

```json
{
  "hits": 1250,
  "misses": 180,
  "hit_rate": 0.874,
  "total_keys": 350,
  "memory_usage_mb": 45.2
}
```

### 18. ISO Compliance Check

ISO 22301 Clause 8.2.2 compliance status.

**Endpoint:** `GET /api/compliance/check`

**Response:** `200 OK`

```json
{
  "iso_clause": "8.2.2",
  "module": "bia",
  "compliance_status": {
    "compliant": true,
    "requirements_met": 15,
    "requirements_total": 15,
    "compliance_percentage": 100.0
  }
}
```

---

**API Version**: 1.0.0
**Last Updated**: 2025-10-09
**Contact**: AI Platform Team
