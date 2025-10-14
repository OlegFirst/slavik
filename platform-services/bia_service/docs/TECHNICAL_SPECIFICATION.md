# BIA Service - Technical Specification

**Version**: 1.0.0
**Date**: 2025-10-09
**Status**: Approved
**ISO 22301 Clause**: 8.2.2

## Table of Contents

1. [Introduction](#1-introduction)
2. [Architecture](#2-architecture)
3. [Components](#3-components)
4. [Data Models](#4-data-models)
5. [Business Logic](#5-business-logic)
6. [API Specifications](#6-api-specifications)
7. [Integration Points](#7-integration-points)
8. [Performance Requirements](#8-performance-requirements)
9. [Security Considerations](#9-security-considerations)
10. [Testing Strategy](#10-testing-strategy)

## 1. Introduction

### 1.1 Purpose

This document specifies the technical architecture and implementation details of the BIA (Business Impact Analysis) Service. The service provides comprehensive BIA capabilities aligned with ISO 22301:2019 Clause 8.2.2 requirements.

### 1.2 Scope

The BIA Service is responsible for:
- Managing business process criticality assessments
- Defining and validating recovery objectives (RTO, RPO, MTPD)
- Analyzing financial and operational impacts
- Mapping process dependencies
- Generating BIA reports and analytics
- Providing AI-powered recommendations

### 1.3 Definitions

- **RTO (Recovery Time Objective)**: Maximum acceptable time period within which a process must be restored after a disruption
- **RPO (Recovery Point Objective)**: Maximum acceptable amount of data loss measured in time
- **MTPD (Maximum Tolerable Period of Disruption)**: Maximum time a process can be unavailable before causing unacceptable consequences
- **WHO Tier**: World Health Organization Essential Services classification (healthcare-specific)
- **Criticality Level**: Five-level classification (CRITICAL, HIGH, MEDIUM, LOW, NEGLIGIBLE)

## 2. Architecture

### 2.1 System Context

The BIA Service operates within the AI-Platform-ISO ecosystem:

```
┌─────────────────────┐
│   API Gateway       │
│   (Port 8000)       │
└──────────┬──────────┘
           │
           ├─────────────────┐
           │                 │
┌──────────▼──────────┐ ┌───▼──────────────┐
│  BIA Service        │ │  Other Services  │
│  (Port 8012)        │ │  - Risk          │
│                     │ │  - Compliance    │
│  ┌───────────────┐  │ │  - Planning      │
│  │ API Layer     │  │ └──────────────────┘
│  ├───────────────┤  │
│  │ Service Layer │  │ ┌──────────────────┐
│  ├───────────────┤  │ │ Infrastructure   │
│  │ Repository    │  │ │                  │
│  └───────────────┘  │ │ - Database       │
└─────────┬───────────┘ │ - Cache (Redis)  │
          │             │ - EventBus       │
          │             │ - AI Orch        │
          └─────────────┤ - Workflow Intel │
                        └──────────────────┘
```

### 2.2 Component Diagram

```
BIA Service Components:
┌──────────────────────────────────────────┐
│ API Layer (FastAPI)                      │
│ - routes.py (12 endpoints)               │
│ - workflow_ai.py (Workflow Intelligence) │
│ - history.py (Audit history)             │
└─────────────┬────────────────────────────┘
              │
┌─────────────▼────────────────────────────┐
│ Service Layer (Business Logic)           │
│ - bia_service.py (CRUD operations)       │
│ - ai_service.py (AI recommendations)     │
│ - report_service.py (Reports/analytics)  │
└─────────────┬────────────────────────────┘
              │
┌─────────────▼────────────────────────────┐
│ Repository Layer (Data Access)           │
│ - bia_repository.py (PostgreSQL access)  │
└─────────────┬────────────────────────────┘
              │
┌─────────────▼────────────────────────────┐
│ Data Layer                               │
│ - database/models.py (SQLAlchemy)        │
│ - models/domain.py (Pydantic)            │
│ - models/enums.py (Enumerations)         │
└──────────────────────────────────────────┘
```

### 2.3 Data Flow

**BIA Process Creation Flow:**

```
1. Client → POST /api/bia/processes
2. API Layer → Authentication & Authorization (JWT)
3. API Layer → Validate tenant_id
4. Service Layer → Validate business rules
5. Repository Layer → Insert into database
6. Service Layer → Calculate criticality score
7. Service Layer → Publish event (bcm.bia.started)
8. Repository Layer → Commit transaction
9. API Layer → Return BIAProcess response
```

**AI RTO Suggestion Flow:**

```
1. Client → POST /api/bia/processes/{id}/suggest-rto
2. API Layer → Get process from repository
3. AI Service → Extract process characteristics
4. AI Service → Call AI Orchestration Service
5. AI Service → Parse AI response
6. AI Service → Apply rule-based fallback (if needed)
7. AI Service → Add industry benchmarks
8. API Layer → Return AIRTOSuggestion
```

## 3. Components

### 3.1 API Layer Components

**routes.py**
- Endpoint definitions (12 core endpoints)
- Request validation (Pydantic models)
- Dependency injection (get_bia_service, get_ai_service)
- JWT authentication enforcement
- Tenant isolation validation

**workflow_ai.py**
- Workflow Intelligence integration endpoints
- Real-time workflow guidance
- Case collection for AI learning

**history.py**
- Audit history endpoints
- Change tracking and versioning

### 3.2 Service Layer Components

**BIAService**
- CRUD operations for BIA processes
- Criticality score calculation
- Business rule validation
- Event publishing

**AIService**
- RTO/RPO/MTPD suggestions using AI
- Dependency discovery automation
- Industry benchmark integration
- Rule-based fallback logic

**ReportService**
- Summary report generation
- Critical processes identification
- Dependency graph creation
- Export functionality

### 3.3 Repository Layer Components

**BIARepository**
- PostgreSQL data access via SQLAlchemy
- Async database operations
- Transaction management
- Query optimization

### 3.4 Data Layer Components

**Database Models (SQLAlchemy)**
- BIAProcessDB - Main BIA process table
- BIADependencyDB - Dependencies table
- BIAImpactDB - Impact assessments table

**Domain Models (Pydantic)**
- BIAProcess - Core domain model
- BIAProcessCreate - Creation DTO
- AIRTOSuggestion - AI recommendation model

**Enums**
- CriticalityLevel (5 levels)
- ProcessStatus (3 states)
- IndustryType (10 industries)

## 4. Data Models

### 4.1 Core Domain Models

**BIAProcess**

```python
class BIAProcess(BaseModel):
    id: int
    tenant_id: str
    name: str
    description: Optional[str]
    criticality: CriticalityLevel
    industry: IndustryType

    # Recovery Objectives
    rto_hours: float
    rpo_hours: float
    mtpd_hours: float

    # Impact Assessment
    financial_impact: Dict[str, float]
    operational_impact: str
    reputational_impact: ReputationalImpact
    regulatory_impact: RegulatoryImpact

    # Dependencies
    dependencies: List[Dependency]

    # Resource Requirements
    resource_requirements: ResourceRequirements

    # Metadata
    status: ProcessStatus
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
```

**AIRTOSuggestion**

```python
class AIRTOSuggestion(BaseModel):
    suggested_rto_hours: float
    suggested_rpo_hours: float
    suggested_mtpd_hours: float
    confidence_score: float
    reasoning: str
    industry_benchmark: str
    alternative_scenarios: List[Dict[str, Any]]
```

### 4.2 Database Schema

**Table: bia_processes**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| tenant_id | VARCHAR(255) | NOT NULL, INDEX | Tenant isolation |
| name | VARCHAR(500) | NOT NULL | Process name |
| description | TEXT | NULLABLE | Process description |
| criticality | VARCHAR(50) | NOT NULL | Criticality level |
| industry | VARCHAR(100) | NOT NULL | Industry type |
| rto_hours | DECIMAL(10,2) | NOT NULL | Recovery time objective |
| rpo_hours | DECIMAL(10,2) | NOT NULL | Recovery point objective |
| mtpd_hours | DECIMAL(10,2) | NOT NULL | Max tolerable disruption |
| financial_impact | JSONB | NOT NULL | Financial impact data |
| dependencies | JSONB | NOT NULL | Dependencies array |
| status | VARCHAR(50) | NOT NULL | Process status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Update timestamp |
| completed_at | TIMESTAMP | NULLABLE | Completion timestamp |

**Indexes:**
- idx_bia_tenant_id (tenant_id)
- idx_bia_criticality (tenant_id, criticality)
- idx_bia_status (tenant_id, status)
- idx_bia_created (tenant_id, created_at DESC)

### 4.3 Enumerations

**CriticalityLevel**
```python
class CriticalityLevel(str, Enum):
    CRITICAL = "critical"      # Score >= 4.0
    HIGH = "high"              # Score 3.0-3.9
    MEDIUM = "medium"          # Score 2.0-2.9
    LOW = "low"                # Score 1.0-1.9
    NEGLIGIBLE = "negligible"  # Score < 1.0
```

**ProcessStatus**
```python
class ProcessStatus(str, Enum):
    DRAFT = "draft"           # Initial state
    IN_PROGRESS = "in_progress"  # Being worked on
    COMPLETED = "completed"   # BIA completed
```

## 5. Business Logic

See [BUSINESS_LOGIC.md](BUSINESS_LOGIC.md) for detailed business rules, workflows, and decision logic.

## 6. API Specifications

See [API.md](API.md) for complete API documentation including request/response examples, error codes, and authentication requirements.

## 7. Integration Points

See [INTEGRATION.md](INTEGRATION.md) for integration patterns with other services and external systems.

## 8. Performance Requirements

### 8.1 Response Time Requirements

- **GET /api/bia/processes**: < 200ms (with caching)
- **POST /api/bia/processes**: < 500ms
- **PUT /api/bia/processes/{id}**: < 500ms
- **POST /api/bia/processes/{id}/suggest-rto**: < 2000ms (AI call)
- **GET /api/bia/reports/summary**: < 1000ms

### 8.2 Throughput Requirements

- Minimum 100 requests/second for read operations
- Minimum 50 requests/second for write operations
- Bulk operations support up to 1000 processes per request

### 8.3 Scalability

- Horizontal scaling via multiple service instances
- Stateless design (no server-side sessions)
- Database connection pooling (20 connections per instance)
- Redis caching for frequently accessed data

### 8.4 Caching Strategy

**Cache Keys:**
- `bia:process:{tenant_id}:{process_id}` - Individual process (TTL: 5 minutes)
- `bia:list:{tenant_id}:{query_hash}` - Process lists (TTL: 2 minutes)
- `bia:report:summary:{tenant_id}` - Summary reports (TTL: 10 minutes)

**Cache Invalidation:**
- On CREATE: Invalidate list caches for tenant
- On UPDATE: Invalidate process and list caches
- On DELETE: Invalidate process and list caches

## 9. Security Considerations

### 9.1 Authentication

- JWT Bearer token required for all endpoints (except /health)
- Token validation via shared/auth middleware
- Token expiration: 24 hours

### 9.2 Authorization

**RBAC Permissions:**
- BIA_CREATE - Create new BIA processes
- BIA_VIEW - View BIA processes
- BIA_UPDATE - Update BIA processes
- BIA_DELETE - Delete BIA processes
- BIA_COMPLETE - Mark BIA as completed
- BIA_AI_SUGGEST - Use AI suggestions

### 9.3 Tenant Isolation

- All queries filtered by tenant_id from JWT
- Row-level security enforced at repository layer
- 403 Forbidden if tenant mismatch detected

### 9.4 Data Protection

- Sensitive data encrypted at rest (database encryption)
- TLS 1.3 for data in transit
- No PII logging
- Audit logging for all modifications

### 9.5 Input Validation

- Pydantic models for request validation
- SQL injection prevention via SQLAlchemy ORM
- XSS prevention via FastAPI automatic escaping
- Rate limiting via API Gateway

## 10. Testing Strategy

### 10.1 Unit Testing

**Coverage Target**: 80% minimum

**Test Categories:**
- Service layer tests (business logic)
- Repository layer tests (data access)
- Utility function tests (calculations)

**Key Test Scenarios:**
- Criticality score calculation accuracy
- RTO/RPO/MTPD validation rules
- Dependency graph generation
- Financial impact calculations

### 10.2 Integration Testing

**Test Categories:**
- API endpoint tests
- Database integration tests
- EventBus integration tests
- Cache integration tests

**Key Test Scenarios:**
- End-to-end BIA creation workflow
- Multi-tenant isolation
- AI service integration
- Event publishing verification

### 10.3 Performance Testing

**Load Testing:**
- Simulate 100 concurrent users
- 1000 requests per minute
- Measure p50, p95, p99 latencies

**Stress Testing:**
- Identify breaking point
- Measure degradation patterns
- Validate error handling under load

### 10.4 Security Testing

- SQL injection attempts
- XSS attack vectors
- JWT tampering tests
- Tenant isolation boundary tests

### 10.5 Test Automation

- CI/CD pipeline integration
- Automated regression testing
- Pre-deployment validation
- Post-deployment smoke tests

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-09
**Approved By**: AI Platform Team
**Next Review**: 2025-11-09
