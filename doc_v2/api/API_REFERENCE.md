# AI-Platform-ISO: Unified API Reference

**Version**: 1.0.0
**Date**: 2025-10-09
**Status**: Production
**Architecture**: ISO 22301:2019 Compliant BCM Platform

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Common Patterns](#common-patterns)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Infrastructure Layer APIs](#infrastructure-layer-apis)
7. [Intelligent Core APIs](#intelligent-core-apis)
8. [Platform Services APIs](#platform-services-apis)
9. [Response Formats](#response-formats)
10. [Versioning](#versioning)

---

## Overview

The AI-Platform-ISO provides a comprehensive REST API across three architectural layers:

### Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│  Platform Services (12 BCM Microservices)           │  Ports 8012-8025
├─────────────────────────────────────────────────────┤
│  Intelligent Core (AI + Workflow Intelligence)      │  Ports 8033-8040
├─────────────────────────────────────────────────────┤
│  Infrastructure (Gateway, EventBus, Database)       │  Ports 8000-8010
└─────────────────────────────────────────────────────┘
```

### Base URLs

| Environment | Base URL |
|-------------|----------|
| Development | `http://localhost:8000` (API Gateway) |
| Staging | `https://staging-api.bcm-platform.com` |
| Production | `https://api.bcm-platform.com` |

### API Design Principles

- **RESTful**: Resource-based URLs, HTTP verbs
- **JSON**: All requests/responses in JSON
- **Async**: Asynchronous processing where appropriate
- **Event-Driven**: Critical operations publish events
- **Multi-Tenant**: All services support tenant isolation
- **ISO Compliant**: Aligned with ISO 22301:2019 clauses

---

## Authentication

### JWT Bearer Token

All API endpoints (except health checks) require JWT authentication.

#### Headers

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-Tenant-ID: <tenant_id>
```

#### Example Request

```bash
curl -X GET \
  "https://api.bcm-platform.com/api/bia/processes" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "X-Tenant-ID: tenant_123"
```

### Development Mode

For development/testing, use the `X-Dev-User` header:

```http
X-Dev-User: {"user_id": "user_123", "tenant_id": "tenant_123", "permissions": ["BIA_CREATE", "BIA_VIEW"]}
```

### Token Structure

```json
{
  "user_id": "user_123",
  "tenant_id": "tenant_123",
  "email": "user@example.com",
  "permissions": [
    "BIA_VIEW",
    "BIA_CREATE",
    "RISK_MANAGE"
  ],
  "exp": 1633024800,
  "iat": 1633021200
}
```

### Permission Model

| Permission | Scope | Description |
|------------|-------|-------------|
| `BIA_VIEW` | BIA Service | View BIA processes |
| `BIA_CREATE` | BIA Service | Create BIA processes |
| `BIA_UPDATE` | BIA Service | Update BIA processes |
| `BIA_DELETE` | BIA Service | Delete BIA processes |
| `BIA_COMPLETE` | BIA Service | Mark BIA complete |
| `BIA_AI_SUGGEST` | BIA Service | Use AI features |
| `RISK_VIEW` | Risk Service | View risk assessments |
| `RISK_MANAGE` | Risk Service | Manage risks |
| `COMPLIANCE_VIEW` | Compliance | View assessments |
| `COMPLIANCE_MANAGE` | Compliance | Manage compliance |
| `ASSESSMENT_CREATE` | Compliance | Create assessments |
| `ADMIN` | All | Full platform access |

---

## Common Patterns

### Pagination

All list endpoints support pagination:

**Query Parameters:**
- `limit`: Max results per page (default: 100, max: 1000)
- `offset`: Number of records to skip (default: 0)

**Example:**
```bash
GET /api/bia/processes?limit=50&offset=100
```

**Response:**
```json
{
  "total": 500,
  "limit": 50,
  "offset": 100,
  "items": [...]
}
```

### Filtering

List endpoints support filtering via query parameters:

```bash
GET /api/bia/processes?criticality=critical&status=completed&industry=healthcare
```

### Sorting

Use `sort_by` and `sort_order`:

```bash
GET /api/bia/processes?sort_by=created_at&sort_order=desc
```

### Field Selection

Use `fields` parameter to select specific fields:

```bash
GET /api/bia/processes?fields=id,name,criticality,rto_hours
```

### Bulk Operations

Most services support bulk operations:

```http
POST /api/bia/processes/bulk
PATCH /api/bia/processes/bulk
DELETE /api/bia/processes/bulk
```

---

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message describing what went wrong",
  "error_code": "VALIDATION_ERROR",
  "status_code": 400,
  "timestamp": "2025-10-09T10:30:00Z",
  "path": "/api/bia/processes",
  "request_id": "req_abc123"
}
```

### HTTP Status Codes

| Code | Description | Common Causes |
|------|-------------|---------------|
| 200 | OK | Successful GET/PATCH/DELETE |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE with no body |
| 400 | Bad Request | Invalid input, validation error |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Insufficient permissions, tenant mismatch |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Duplicate resource, business rule violation |
| 422 | Unprocessable Entity | Business logic constraint violated |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily down |

### Error Codes

| Code | Description | Action |
|------|-------------|--------|
| `VALIDATION_ERROR` | Invalid input data | Check request schema |
| `TENANT_MISMATCH` | Tenant access denied | Verify tenant_id |
| `PERMISSION_DENIED` | Insufficient permissions | Check user permissions |
| `RESOURCE_NOT_FOUND` | Resource not found | Verify resource ID |
| `DUPLICATE_RESOURCE` | Resource already exists | Use different identifier |
| `BUSINESS_RULE_VIOLATION` | Business constraint violated | Review business rules |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait and retry |
| `DEPENDENCY_FAILED` | External service failed | Check service status |

---

## Rate Limiting

### Default Limits

| Endpoint Type | Rate Limit | Window |
|---------------|------------|--------|
| Read (GET) | 1000/min | 60s |
| Write (POST/PUT/PATCH) | 100/min | 60s |
| Delete (DELETE) | 50/min | 60s |
| AI Operations | 20/min | 60s |
| Bulk Operations | 10/min | 60s |

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1633024800
```

### Rate Limit Exceeded Response

```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "status_code": 429,
  "retry_after": 45
}
```

---

## Infrastructure Layer APIs

### API Gateway

**Base URL**: `http://localhost:8000`
**Purpose**: Unified entry point, routing, authentication

#### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Gateway health check |
| `GET` | `/api/v1/gateway/services` | List available services |
| `POST` | `/api/v1/gateway/ai/analyze` | AI analysis request |
| `POST` | `/api/v1/gateway/ai/optimize` | AI optimization request |
| `POST` | `/auth/odoo` | Odoo authentication |
| `GET` | `/auth/odoo/session/{session_id}` | Get session details |
| `DELETE` | `/auth/odoo/session/{session_id}` | Delete session |
| `GET` | `/metrics` | Prometheus metrics |
| `POST` | `/query` | Unified query interface |

#### Gateway Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "eventbus": "healthy"
  },
  "timestamp": "2025-10-09T10:30:00Z"
}
```

#### List Services

```http
GET /api/v1/gateway/services
```

**Response:**
```json
{
  "services": [
    {
      "name": "bia-service",
      "url": "http://localhost:8012",
      "status": "healthy",
      "iso_clause": "8.2.2"
    },
    {
      "name": "risk-service",
      "url": "http://localhost:8040",
      "status": "healthy",
      "iso_clause": "8.2.3"
    }
  ]
}
```

---

## Intelligent Core APIs

### 1. Workflow Intelligence Service

**Base URL**: `http://localhost:8037`
**Port**: 8037
**Purpose**: Case Library, Workflow Analysis, ML Recommendations

#### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "module": "workflow_intelligence",
  "features": {
    "case_library": true,
    "ml_analysis": true,
    "workflow_engine": true
  }
}
```

#### Case Library

##### Add Case

```http
POST /api/cases
```

**Request:**
```json
{
  "case_data": {
    "title": "Healthcare System Outage",
    "scenario": "power_failure",
    "recovery_time": 4.5,
    "lessons_learned": "Backup generator critical"
  },
  "module": "bia",
  "source": "community",
  "metadata": {
    "industry": "healthcare",
    "organization_size": "large"
  }
}
```

**Response:**
```json
{
  "case_id": "case_123",
  "status": "added",
  "similarity_score": 0.85,
  "related_cases": ["case_45", "case_67"]
}
```

##### Get Similar Cases

```http
GET /api/cases/similar?module=bia&scenario=power_failure&limit=10
```

**Response:**
```json
{
  "total": 45,
  "cases": [
    {
      "case_id": "case_45",
      "title": "Hospital Power Failure Recovery",
      "similarity_score": 0.92,
      "recovery_time": 3.8,
      "industry": "healthcare"
    }
  ]
}
```

#### Workflow Analysis

```http
POST /api/workflow/analyze
```

**Request:**
```json
{
  "workflow_id": "wf_123",
  "context": {
    "module": "bia",
    "process_id": 456
  }
}
```

**Response:**
```json
{
  "bottlenecks": [
    {
      "step": "approval_wait",
      "avg_duration_hours": 48,
      "recommendation": "Implement automated approval for low-risk processes"
    }
  ],
  "optimization_score": 72,
  "estimated_time_savings": 24
}
```

### 2. AI Foundation Service

**Base URL**: `http://localhost:8040`
**Port**: 8040
**Purpose**: RAG, ML Models, Learning System

#### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "features": {
    "rag_enabled": true,
    "ml_models_loaded": true,
    "vector_db": "healthy"
  }
}
```

### 3. Event Intelligence Service

**Base URL**: `http://localhost:8039`
**Port**: 8039
**Purpose**: Event Pattern Detection, Real-time Analytics

#### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "events_processed": 15234,
  "active_patterns": 8
}
```

### 4. Orchestration Service

**Base URL**: `http://localhost:8037`
**Port**: 8037
**Purpose**: Service Coordination, Workflow Orchestration

#### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "active_workflows": 12,
  "pending_tasks": 45
}
```

### 5. Learning System

**Base URL**: `http://localhost:8033`
**Port**: 8033
**Purpose**: Knowledge Management, Continuous Learning

#### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "knowledge_base_size": 5000,
  "learning_models_active": 3
}
```

### 6. Knowledge System

**Base URL**: `http://localhost:8034`
**Port**: 8034
**Purpose**: Standards Library, Best Practices

#### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "standards_loaded": ["ISO22301", "NIST", "WHO"],
  "cases_indexed": 1200
}
```

---

## Platform Services APIs

### 1. BIA Service

**Base URL**: `http://localhost:8012`
**Port**: 8012
**ISO Clause**: 8.2.2 - Business Impact Analysis
**API Prefix**: `/api/bia`

#### Process Management

##### Create BIA Process

```http
POST /api/bia/processes
```

**Request:**
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
  "operational_impact": "Complete loss of payment processing",
  "reputational_impact": "severe",
  "regulatory_impact": "high",
  "dependencies": [
    {
      "type": "technology",
      "name": "Payment Gateway API",
      "criticality": 5,
      "is_downstream": true
    }
  ],
  "resource_requirements": {
    "minimum_staff": 5,
    "key_personnel": ["Payment Engineer", "Database Admin"],
    "facilities": ["Primary Data Center"],
    "technology": ["Payment Gateway", "Database Cluster"]
  }
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "tenant_id": "tenant_123",
  "name": "Payment Processing System",
  "status": "draft",
  "created_at": "2025-10-09T10:30:00Z",
  "updated_at": "2025-10-09T10:30:00Z"
}
```

##### List BIA Processes

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
      "name": "Payment Processing System",
      "criticality": "critical",
      "rto_hours": 2.0,
      "status": "completed"
    }
  ]
}
```

##### Get BIA Process

```http
GET /api/bia/processes/{id}?tenant_id=tenant_123
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "tenant_id": "tenant_123",
  "name": "Payment Processing System",
  "criticality": "critical",
  "rto_hours": 2.0,
  "financial_impact": {...},
  "dependencies": [...],
  "status": "completed"
}
```

##### Update BIA Process

```http
PUT /api/bia/processes/{id}
```

**Request:**
```json
{
  "tenant_id": "tenant_123",
  "rto_hours": 1.5,
  "rpo_hours": 0.25
}
```

**Response:** `200 OK`

##### Delete BIA Process

```http
DELETE /api/bia/processes/{id}?tenant_id=tenant_123
```

**Response:** `200 OK`
```json
{
  "message": "BIA process deleted successfully",
  "process_id": 1
}
```

##### Mark Process Complete

```http
POST /api/bia/processes/{id}/complete
```

**Request:**
```json
{
  "tenant_id": "tenant_123"
}
```

**Response:** `200 OK`

#### AI-Powered Analysis

##### AI RTO/RPO Suggestion

```http
POST /api/bia/processes/{id}/suggest-rto
```

**Request:**
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
  "reasoning": "Based on CRITICAL criticality and $200K/4hr impact",
  "industry_benchmark": "Financial Services: 1-4 hours RTO",
  "alternative_scenarios": [
    {
      "scenario": "Conservative",
      "rto_hours": 1.0,
      "cost_impact": "Higher infrastructure costs"
    }
  ]
}
```

##### AI Dependency Discovery

```http
POST /api/bia/processes/{id}/discover-dependencies
```

**Request:**
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
      "criticality": 5,
      "confidence": 0.9
    }
  ],
  "total_discovered": 2
}
```

#### Bulk Operations

##### Bulk Create

```http
POST /api/bia/processes/bulk
```

**Request:**
```json
{
  "processes": [
    {
      "tenant_id": "tenant_123",
      "name": "Process 1",
      "criticality": "high",
      "rto_hours": 4.0
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
    }
  ]
}
```

##### Bulk Update

```http
PATCH /api/bia/processes/bulk
```

##### Bulk Delete

```http
DELETE /api/bia/processes/bulk
```

##### Validate Bulk Import

```http
POST /api/bia/processes/bulk/validate
```

**Response:** `200 OK`
```json
{
  "valid": true,
  "total_processes": 2,
  "errors": [],
  "warnings": [
    "Process 'Process 1': RTO below industry benchmark"
  ]
}
```

#### Reporting

##### Summary Report

```http
GET /api/bia/reports/summary?tenant_id=tenant_123
```

**Response:** `200 OK`
```json
{
  "tenant_id": "tenant_123",
  "total_processes": 50,
  "critical_processes": 12,
  "completed_bia_count": 45,
  "average_rto_hours": 6.5,
  "total_financial_impact_24h": 15000000,
  "processes_by_criticality": {
    "critical": 12,
    "high": 18,
    "medium": 15,
    "low": 5
  }
}
```

##### Critical Processes Report

```http
GET /api/bia/reports/critical-processes?tenant_id=tenant_123&min_criticality=high
```

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
      "financial_impact_24h": 1200000
    }
  ]
}
```

##### Dependencies Report

```http
GET /api/bia/reports/dependencies?tenant_id=tenant_123&process_id=1
```

**Response:** `200 OK`
```json
{
  "dependency_graph": [
    {
      "process_id": 1,
      "process_name": "Payment Processing",
      "upstream_dependencies": [...],
      "downstream_dependencies": [...]
    }
  ]
}
```

#### Health & Monitoring

##### Health Check

```http
GET /health
```

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "service": "bia",
  "iso_clause": "8.2.2",
  "port": 8012,
  "features": {
    "ai_enabled": true,
    "eventbus": true
  }
}
```

##### Cache Metrics

```http
GET /metrics/cache
```

**Response:** `200 OK`
```json
{
  "hits": 1250,
  "misses": 180,
  "hit_rate": 0.874,
  "memory_usage_mb": 45.2
}
```

##### ISO Compliance Check

```http
GET /api/compliance/check
```

**Response:** `200 OK`
```json
{
  "iso_clause": "8.2.2",
  "module": "bia",
  "compliance_status": {
    "compliant": true,
    "requirements_met": 15,
    "compliance_percentage": 100.0
  }
}
```

---

### 2. Risk Service

**Base URL**: `http://localhost:8040`
**Port**: 8040
**ISO Clause**: 8.2.3 - Risk Assessment
**API Prefix**: `/api/risk`

#### Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health |
| `POST` | `/api/risk/assessments` | Create risk assessment |
| `GET` | `/api/risk/assessments` | List assessments |
| `GET` | `/api/risk/assessments/{id}` | Get assessment |
| `PUT` | `/api/risk/assessments/{id}` | Update assessment |
| `DELETE` | `/api/risk/assessments/{id}` | Delete assessment |
| `POST` | `/api/risk/assessments/{id}/analyze` | AI risk analysis |
| `GET` | `/api/risk/reports/summary` | Risk summary |
| `GET` | `/api/risk/reports/heat-map` | Risk heat map |

---

### 3. Compliance Service

**Base URL**: `http://localhost:8014`
**Port**: 8014
**ISO Clause**: 9.2, 10.1, 10.2 - Compliance Management
**API Prefix**: `/api/compliance`

#### Assessments

##### Create Assessment

```http
POST /api/compliance/assessments
```

**Request:**
```json
{
  "tenant_id": "tenant_123",
  "name": "Q4 2025 ISO 22301 Assessment",
  "description": "Quarterly compliance assessment",
  "target_compliance": 95.0,
  "scope": ["clause_8", "clause_9", "clause_10"]
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "tenant_id": "tenant_123",
  "name": "Q4 2025 ISO 22301 Assessment",
  "status": "draft",
  "created_at": "2025-10-09T10:30:00Z"
}
```

##### List Assessments

```http
GET /api/compliance/assessments?tenant_id=tenant_123
```

##### Get Assessment

```http
GET /api/compliance/assessments/{id}
```

##### Run Assessment

```http
POST /api/compliance/assessments/{id}/run
```

**Request:**
```json
{
  "tenant_id": "tenant_123",
  "ai_scan_enabled": true
}
```

**Response:** `200 OK`
```json
{
  "assessment_id": 1,
  "overall_score": 87.5,
  "compliance_percentage": 87.5,
  "gaps_identified": 8,
  "clauses_assessed": 15,
  "status": "completed"
}
```

##### Get Assessment Results

```http
GET /api/compliance/assessments/{id}/results
```

**Response:** `200 OK`
```json
{
  "assessment_id": 1,
  "overall_score": 87.5,
  "clause_scores": {
    "clause_8": 92.0,
    "clause_9": 85.0,
    "clause_10": 86.0
  },
  "gaps": [
    {
      "clause": "8.2.2",
      "severity": "medium",
      "description": "BIA coverage incomplete"
    }
  ]
}
```

##### Batch AI Scan

```http
POST /api/compliance/assessments/batch-ai-scan
```

**Request:**
```json
{
  "tenant_id": "tenant_123",
  "clauses": ["8.2.2", "8.2.3", "8.4"],
  "modules": ["bia", "risk", "response"]
}
```

#### Evidence Management

##### Create Evidence

```http
POST /api/compliance/evidence
```

**Request:**
```json
{
  "tenant_id": "tenant_123",
  "clause": "8.2.2",
  "title": "BIA Process Documentation",
  "description": "Completed BIA for critical processes",
  "evidence_type": "document",
  "url": "https://docs.example.com/bia-report.pdf",
  "metadata": {
    "processes_covered": 12,
    "completion_date": "2025-10-01"
  }
}
```

**Response:** `201 Created`

##### List Evidence

```http
GET /api/compliance/evidence?tenant_id=tenant_123&clause=8.2.2
```

##### Get Evidence

```http
GET /api/compliance/evidence/{id}
```

##### Update Evidence

```http
PATCH /api/compliance/evidence/{id}
```

##### Transition Evidence Status

```http
POST /api/compliance/evidence/{id}/transition
```

**Request:**
```json
{
  "tenant_id": "tenant_123",
  "target_status": "approved",
  "notes": "Evidence reviewed and approved"
}
```

##### Get Evidence History

```http
GET /api/compliance/evidence/{id}/history
```

#### Gap Analysis

##### List Gaps

```http
GET /api/compliance/gaps?tenant_id=tenant_123&severity=high
```

**Response:** `200 OK`
```json
{
  "total": 8,
  "gaps": [
    {
      "id": 1,
      "clause": "8.2.2",
      "severity": "high",
      "description": "BIA coverage at 60%, target 95%",
      "remediation_plan": "Complete BIA for remaining processes",
      "target_date": "2025-12-31",
      "status": "open"
    }
  ]
}
```

#### Improvements (ISO 10.2)

##### Create Improvement Initiative

```http
POST /api/compliance/improvements
```

**Request:**
```json
{
  "tenant_id": "tenant_123",
  "title": "Automate BIA Process",
  "description": "Implement AI-powered BIA automation",
  "category": "process_improvement",
  "priority": "high",
  "estimated_effort": 160,
  "expected_roi": 300
}
```

**Response:** `201 Created`

##### List Improvements

```http
GET /api/compliance/improvements?tenant_id=tenant_123
```

##### Get Improvement

```http
GET /api/compliance/improvements/{id}
```

##### Update Progress

```http
PATCH /api/compliance/improvements/{id}/progress
```

**Request:**
```json
{
  "tenant_id": "tenant_123",
  "progress_percentage": 75,
  "status": "in_progress",
  "notes": "Integration testing complete"
}
```

##### Verify Improvement

```http
POST /api/compliance/improvements/{id}/verify
```

##### Improvements Dashboard

```http
GET /api/compliance/improvements/dashboard?tenant_id=tenant_123
```

##### ROI Analysis

```http
GET /api/compliance/improvements/roi-analysis?tenant_id=tenant_123
```

#### Management Review (ISO 9.3)

##### Create Management Review

```http
POST /api/compliance/management-review
```

**Request:**
```json
{
  "tenant_id": "tenant_123",
  "review_period_start": "2025-07-01",
  "review_period_end": "2025-09-30",
  "participants": ["ceo@example.com", "ciso@example.com"]
}
```

##### List Reviews

```http
GET /api/compliance/management-review?tenant_id=tenant_123
```

##### Get Review

```http
GET /api/compliance/management-review/{id}
```

##### Get Review Inputs

```http
GET /api/compliance/management-review/{id}/inputs
```

**Response:** `200 OK`
```json
{
  "review_id": 1,
  "inputs": {
    "internal_audits": 3,
    "nonconformities": 5,
    "improvement_initiatives": 8,
    "incidents": 2,
    "compliance_score": 87.5
  }
}
```

##### Start Review

```http
POST /api/compliance/management-review/{id}/start
```

##### Add Decisions

```http
POST /api/compliance/management-review/{id}/decisions
```

**Request:**
```json
{
  "tenant_id": "tenant_123",
  "decisions": [
    {
      "topic": "BIA Coverage",
      "decision": "Increase coverage to 100% by Q1 2026",
      "owner": "bcm-manager@example.com",
      "due_date": "2026-03-31"
    }
  ]
}
```

##### Complete Review

```http
POST /api/compliance/management-review/{id}/complete
```

##### Get Review Report

```http
GET /api/compliance/management-review/{id}/report
```

#### Nonconformities (ISO 10.1)

##### Create Nonconformity

```http
POST /api/compliance/nonconformities
```

##### List Nonconformities

```http
GET /api/compliance/nonconformities?tenant_id=tenant_123
```

##### Get Nonconformity

```http
GET /api/compliance/nonconformities/{id}
```

##### Update Nonconformity

```http
PATCH /api/compliance/nonconformities/{id}
```

#### Internal Audit (ISO 9.2)

##### Create Audit

```http
POST /api/compliance/audit
```

##### List Audits

```http
GET /api/compliance/audit?tenant_id=tenant_123
```

##### Get Audit

```http
GET /api/compliance/audit/{id}
```

#### Dashboard & Analytics

##### Dashboard Overview

```http
GET /api/compliance/dashboard/overview?tenant_id=tenant_123
```

**Response:** `200 OK`
```json
{
  "overall_compliance": 87.5,
  "total_assessments": 12,
  "open_gaps": 8,
  "improvement_initiatives": 15,
  "recent_audits": 3,
  "trend": "improving"
}
```

##### Requirements Matrix

```http
GET /api/compliance/dashboard/requirements-matrix?tenant_id=tenant_123
```

##### Compliance Roadmap

```http
GET /api/compliance/dashboard/roadmap?tenant_id=tenant_123
```

##### Analytics

```http
GET /api/compliance/dashboard/analytics?tenant_id=tenant_123
```

#### Knowledge Base

##### Best Practices Library

```http
GET /api/compliance/library/best-practices
```

**Response:** `200 OK`
```json
{
  "categories": [
    {
      "name": "Business Impact Analysis",
      "practices": [
        {
          "title": "Automated BIA Templates",
          "description": "Pre-built templates for common scenarios",
          "source": "ISO 22301"
        }
      ]
    }
  ]
}
```

##### Implementation Guides

```http
GET /api/compliance/library/guides
```

##### Get Specific Guide

```http
GET /api/compliance/library/guides/{guide_id}
```

##### Research Sources

```http
GET /api/compliance/library/research
```

##### Case Studies

```http
GET /api/compliance/library/case-studies
```

#### Module Health

##### Overall Module Health

```http
GET /api/compliance/modules/health
```

**Response:** `200 OK`
```json
{
  "overall_status": "healthy",
  "modules": [
    {
      "name": "bia-service",
      "status": "healthy",
      "compliance_score": 92.0
    },
    {
      "name": "risk-service",
      "status": "healthy",
      "compliance_score": 88.5
    }
  ]
}
```

##### Specific Module Health

```http
GET /api/compliance/modules/health/{service_name}
```

---

### 4. Response Service

**Base URL**: `http://localhost:8015`
**Port**: 8015
**ISO Clause**: 8.4 - Incident Response
**API Prefix**: `/api/response`

#### Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health |
| `POST` | `/api/response/incidents` | Create incident |
| `GET` | `/api/response/incidents` | List incidents |
| `GET` | `/api/response/incidents/{id}` | Get incident |
| `PATCH` | `/api/response/incidents/{id}` | Update incident |
| `POST` | `/api/response/incidents/{id}/activate` | Activate response |
| `POST` | `/api/response/incidents/{id}/escalate` | Escalate incident |
| `GET` | `/api/response/playbooks` | List playbooks |
| `GET` | `/api/response/reports/timeline` | Incident timeline |

---

### 5. Governance Service

**Base URL**: `http://localhost:8016`
**Port**: 8016
**ISO Clause**: 4, 5, 7 - Governance
**API Prefix**: `/api/governance`

#### Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health |
| `POST` | `/api/governance/policies` | Create policy |
| `GET` | `/api/governance/policies` | List policies |
| `POST` | `/api/governance/roles` | Create role |
| `GET` | `/api/governance/roles` | List roles |
| `POST` | `/api/governance/committees` | Create committee |
| `GET` | `/api/governance/reports/structure` | Governance structure |

---

### 6. Documents Service

**Base URL**: `http://localhost:8017`
**Port**: 8017
**ISO Clause**: 7.5 - Documented Information
**API Prefix**: `/api/documents`

#### Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health |
| `POST` | `/api/documents` | Upload document |
| `GET` | `/api/documents` | List documents |
| `GET` | `/api/documents/{id}` | Get document |
| `PUT` | `/api/documents/{id}` | Update document |
| `DELETE` | `/api/documents/{id}` | Delete document |
| `POST` | `/api/documents/{id}/versions` | Create version |
| `GET` | `/api/documents/{id}/versions` | List versions |
| `POST` | `/api/documents/search` | Search documents |

---

### 7. Validation Service

**Base URL**: `http://localhost:8018`
**Port**: 8018
**ISO Clause**: 8.5 - Testing and Exercises
**API Prefix**: `/api/validation`

#### Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health |
| `POST` | `/api/validation/exercises` | Create exercise |
| `GET` | `/api/validation/exercises` | List exercises |
| `GET` | `/api/validation/exercises/{id}` | Get exercise |
| `POST` | `/api/validation/exercises/{id}/execute` | Execute exercise |
| `GET` | `/api/validation/exercises/{id}/results` | Get results |
| `GET` | `/api/validation/reports/summary` | Exercise summary |

---

### 8. Learning Service

**Base URL**: `http://localhost:8019`
**Port**: 8019
**ISO Clause**: 7.2, 10.2 - Competence & Learning
**API Prefix**: `/api/learning`

#### Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health |
| `POST` | `/api/learning/courses` | Create course |
| `GET` | `/api/learning/courses` | List courses |
| `POST` | `/api/learning/enrollments` | Enroll user |
| `GET` | `/api/learning/progress/{user_id}` | Get progress |
| `POST` | `/api/learning/assessments` | Create assessment |
| `GET` | `/api/learning/certifications` | List certifications |

---

### 9. Planning Service

**Base URL**: `http://localhost:8020`
**Port**: 8020
**ISO Clause**: 8.3 - BCM Strategy
**API Prefix**: `/api/planning`

#### Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health |
| `POST` | `/api/planning/strategies` | Create strategy |
| `GET` | `/api/planning/strategies` | List strategies |
| `GET` | `/api/planning/strategies/{id}` | Get strategy |
| `PUT` | `/api/planning/strategies/{id}` | Update strategy |
| `POST` | `/api/planning/strategies/{id}/approve` | Approve strategy |
| `GET` | `/api/planning/reports/coverage` | Strategy coverage |

---

### 10. Plans Service

**Base URL**: `http://localhost:8021`
**Port**: 8021
**ISO Clause**: 8.4.2 - Recovery Plans
**API Prefix**: `/api/plans`

#### Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health |
| `POST` | `/api/plans` | Create plan |
| `GET` | `/api/plans` | List plans |
| `GET` | `/api/plans/{id}` | Get plan |
| `PUT` | `/api/plans/{id}` | Update plan |
| `POST` | `/api/plans/{id}/activate` | Activate plan |
| `GET` | `/api/plans/{id}/versions` | Plan versions |
| `POST` | `/api/plans/{id}/test` | Test plan |

---

### 11. Community Service

**Base URL**: `http://localhost:8022`
**Port**: 8022
**Purpose**: Community Intelligence & Collaboration
**API Prefix**: `/api/community`

#### Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health |
| `POST` | `/api/community/cases` | Share case |
| `GET` | `/api/community/cases` | Browse cases |
| `GET` | `/api/community/cases/{id}` | Get case |
| `POST` | `/api/community/contributions` | Submit contribution |
| `GET` | `/api/community/reputation/{user_id}` | Get reputation |
| `POST` | `/api/community/reviews` | Submit review |

---

### 12. BCM Coordination Service

**Base URL**: `http://localhost:8023`
**Port**: 8023
**ISO Clause**: Cross-functional Coordination
**API Prefix**: `/api/coordination`

#### Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health |
| `POST` | `/api/coordination/tasks` | Create task |
| `GET` | `/api/coordination/tasks` | List tasks |
| `POST` | `/api/coordination/meetings` | Schedule meeting |
| `GET` | `/api/coordination/dashboard` | Coordination dashboard |
| `POST` | `/api/coordination/notifications` | Send notification |

---

## Response Formats

### Success Response

```json
{
  "data": {...},
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2025-10-09T10:30:00Z",
    "version": "1.0.0"
  }
}
```

### List Response

```json
{
  "data": [...],
  "meta": {
    "total": 100,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

### Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "rto_hours",
      "constraint": "must be positive number"
    }
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2025-10-09T10:30:00Z"
  }
}
```

---

## Versioning

### API Version Strategy

- **URL Versioning**: `/api/v1/...`, `/api/v2/...`
- **Header Versioning**: `Accept: application/vnd.bcm-platform.v1+json`
- **Current Version**: v1
- **Deprecation Policy**: 6 months notice

### Version Header

```http
X-API-Version: 1.0.0
```

---

## WebSocket APIs

### Real-time Updates

**Endpoint**: `ws://localhost:8000/ws`

#### Subscribe to Events

```json
{
  "action": "subscribe",
  "channels": [
    "incidents.created",
    "assessments.completed"
  ],
  "tenant_id": "tenant_123"
}
```

#### Event Message

```json
{
  "event": "incident.created",
  "data": {
    "incident_id": 123,
    "severity": "high",
    "title": "Database Outage"
  },
  "timestamp": "2025-10-09T10:30:00Z"
}
```

---

## Batch Operations

### Standard Batch Request

```json
{
  "operations": [
    {
      "method": "POST",
      "path": "/api/bia/processes",
      "body": {...}
    },
    {
      "method": "PUT",
      "path": "/api/bia/processes/123",
      "body": {...}
    }
  ],
  "max_concurrency": 10
}
```

### Batch Response

```json
{
  "results": [
    {
      "status": "success",
      "status_code": 201,
      "data": {...}
    },
    {
      "status": "error",
      "status_code": 400,
      "error": {...}
    }
  ],
  "summary": {
    "total": 2,
    "successful": 1,
    "failed": 1
  }
}
```

---

## SDK Examples

### Python SDK

```python
from bcm_platform import BCMClient

client = BCMClient(
    api_key="your_api_key",
    base_url="https://api.bcm-platform.com"
)

# Create BIA process
process = client.bia.create_process(
    tenant_id="tenant_123",
    name="Payment Processing",
    criticality="critical",
    rto_hours=2.0
)

# Get AI suggestions
suggestions = client.bia.suggest_rto(process.id)
print(f"Suggested RTO: {suggestions.suggested_rto_hours} hours")
```

### JavaScript SDK

```javascript
import { BCMClient } from '@bcm-platform/sdk';

const client = new BCMClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.bcm-platform.com'
});

// Create BIA process
const process = await client.bia.createProcess({
  tenantId: 'tenant_123',
  name: 'Payment Processing',
  criticality: 'critical',
  rtoHours: 2.0
});

// Get AI suggestions
const suggestions = await client.bia.suggestRto(process.id);
console.log(`Suggested RTO: ${suggestions.suggestedRtoHours} hours`);
```

---

## Appendix A: Common Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `tenant_id` | string | Tenant identifier | `tenant_123` |
| `limit` | integer | Max results | `50` |
| `offset` | integer | Skip records | `100` |
| `sort_by` | string | Sort field | `created_at` |
| `sort_order` | string | Sort direction | `asc`, `desc` |
| `fields` | string | Field selection | `id,name,status` |
| `filter` | string | Filter expression | `status:active` |
| `search` | string | Full-text search | `payment processing` |

---

## Appendix B: ISO 22301 Clause Mapping

| Clause | Service | Primary Endpoints |
|--------|---------|-------------------|
| 4 | Governance | `/api/governance/context` |
| 5 | Governance | `/api/governance/leadership` |
| 7 | Governance, Documents | `/api/governance/resources`, `/api/documents` |
| 7.2 | Learning | `/api/learning/courses` |
| 7.5 | Documents | `/api/documents` |
| 8.2.2 | BIA | `/api/bia/processes` |
| 8.2.3 | Risk | `/api/risk/assessments` |
| 8.3 | Planning | `/api/planning/strategies` |
| 8.4 | Response | `/api/response/incidents` |
| 8.4.2 | Plans | `/api/plans` |
| 8.5 | Validation | `/api/validation/exercises` |
| 9.2 | Compliance | `/api/compliance/audit` |
| 10.1 | Compliance | `/api/compliance/nonconformities` |
| 10.2 | Compliance | `/api/compliance/improvements` |

---

## Appendix C: Service Port Reference

| Service | Port | Layer | ISO Clause |
|---------|------|-------|------------|
| API Gateway | 8000 | Infrastructure | - |
| EventBus | 6379 | Infrastructure | - |
| BIA Service | 8012 | Platform | 8.2.2 |
| Compliance Service | 8014 | Platform | 9.2, 10.1, 10.2 |
| Response Service | 8015 | Platform | 8.4 |
| Governance Service | 8016 | Platform | 4, 5, 7 |
| Documents Service | 8017 | Platform | 7.5 |
| Validation Service | 8018 | Platform | 8.5 |
| Learning Service | 8019 | Platform | 7.2, 10.2 |
| Planning Service | 8020 | Platform | 8.3 |
| Plans Service | 8021 | Platform | 8.4.2 |
| Community Service | 8022 | Platform | - |
| BCM Coordination | 8023 | Platform | - |
| Learning System | 8033 | Intelligent Core | - |
| Knowledge System | 8034 | Intelligent Core | - |
| Expertise Center | 8035 | Intelligent Core | - |
| Workflow Engine | 8036 | Intelligent Core | - |
| Workflow Intelligence | 8037 | Intelligent Core | - |
| Event Intelligence | 8039 | Intelligent Core | - |
| AI Foundation | 8040 | Intelligent Core | - |
| Risk Service | 8040 | Platform | 8.2.3 |

---

## Support

**Documentation**: https://docs.bcm-platform.com
**API Status**: https://status.bcm-platform.com
**Support Email**: api-support@bcm-platform.com
**GitHub**: https://github.com/bcm-platform/api-docs

---

**Document Control**
- Version: 1.0.0
- Last Updated: 2025-10-09
- Author: AI Platform Team
- Review Cycle: Quarterly
- Next Review: 2026-01-09
