# BCM AI Platform - OpenAPI 3.0 Specification

> **Complete REST API specification for the BCM AI Platform**
> **Version:** 1.0.0
> **OpenAPI Version:** 3.0.3
> **Last Updated:** 2025-10-07

---

## Table of Contents

1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [Core API Specifications](#core-api-specifications)
4. [Complete OpenAPI YAML](#complete-openapi-yaml)
5. [API Usage Examples](#api-usage-examples)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Versioning](#versioning)

---

## API Overview

### Base URLs

| Environment | Base URL | Purpose |
|-------------|----------|---------|
| **Production** | `https://api.bcm.example.com/v1` | Live production environment |
| **Staging** | `https://staging-api.bcm.example.com/v1` | Pre-production testing |
| **Development** | `https://dev-api.bcm.example.com/v1` | Development environment |

### API Architecture

```mermaid
graph TB
    Client[API Client] --> Gateway[API Gateway<br/>Rate Limiting + Auth]

    Gateway --> BIA[BIA Service<br/>:8002]
    Gateway --> Risk[Risk Service<br/>:8004]
    Gateway --> Gov[Governance Service<br/>:8020]
    Gateway --> Val[Validation Service<br/>:8022]
    Gateway --> Doc[Documents Service<br/>:8024]
    Gateway --> User[User Profile Service<br/>:8028]

    BIA --> AI[AI Foundation]
    Risk --> AI
    Gov --> AI

    AI --> DB[(PostgreSQL)]
    AI --> Vector[(Qdrant)]
```

---

## Authentication

### OAuth 2.0 Flow

```yaml
security:
  - OAuth2:
      - read
      - write
  - BearerAuth: []

securitySchemes:
  OAuth2:
    type: oauth2
    flows:
      authorizationCode:
        authorizationUrl: https://api.bcm.example.com/oauth/authorize
        tokenUrl: https://api.bcm.example.com/oauth/token
        scopes:
          read: Read access to resources
          write: Write access to resources
          admin: Administrative access

  BearerAuth:
    type: http
    scheme: bearer
    bearerFormat: JWT
```

### Getting Access Token

```bash
# 1. Authorization Code Flow
curl -X POST https://api.bcm.example.com/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=AUTH_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=https://yourapp.com/callback"

# Response
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 900,
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "scope": "read write"
}
```

---

## Core API Specifications

### 1. BIA (Business Impact Analysis) API

#### Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/bia` | List all BIA analyses | ✅ |
| `POST` | `/bia` | Create new BIA | ✅ |
| `GET` | `/bia/{id}` | Get BIA by ID | ✅ |
| `PUT` | `/bia/{id}` | Update BIA | ✅ |
| `DELETE` | `/bia/{id}` | Delete BIA | ✅ |
| `POST` | `/bia/{id}/analyze` | Run AI analysis | ✅ |
| `GET` | `/bia/reports/criticality-matrix` | Get criticality matrix | ✅ |

#### Data Models

**BIA Analysis:**
```yaml
BIAAnalysis:
  type: object
  required:
    - process_name
    - owner_id
    - mtpd_hours
    - rto_hours
    - rpo_hours
  properties:
    id:
      type: string
      format: uuid
      example: "550e8400-e29b-41d4-a716-446655440000"
    tenant_id:
      type: string
      format: uuid
    process_name:
      type: string
      minLength: 3
      maxLength: 200
      example: "Customer Billing Process"
    process_description:
      type: string
      maxLength: 5000
      example: "Monthly billing cycle for all customers"
    owner_id:
      type: string
      format: uuid
    department:
      type: string
      example: "Finance"

    # Impact Analysis
    mtpd_hours:
      type: integer
      minimum: 1
      description: "Maximum Tolerable Period of Disruption"
      example: 24
    rto_hours:
      type: integer
      minimum: 1
      description: "Recovery Time Objective"
      example: 12
    rpo_hours:
      type: integer
      minimum: 0
      description: "Recovery Point Objective"
      example: 4

    financial_impact_per_hour:
      type: number
      format: decimal
      example: 50000.00
    financial_impact_peak_period:
      type: number
      format: decimal
      example: 150000.00

    operational_impact:
      type: string
      enum: [critical, high, medium, low]
      example: "high"
    reputational_impact:
      type: string
      enum: [critical, high, medium, low]
    legal_regulatory_impact:
      type: string
      enum: [critical, high, medium, low]

    # Classification
    criticality:
      type: string
      enum: [critical, important, normal]
      example: "critical"
    priority_tier:
      type: integer
      minimum: 1
      maximum: 5
      example: 1

    # Resources
    minimum_staff_required:
      type: integer
      example: 5
    key_personnel:
      type: array
      items:
        type: object
        properties:
          role:
            type: string
          name:
            type: string
          is_critical:
            type: boolean

    critical_systems:
      type: array
      items:
        type: string
      example: ["ERP System", "Payment Gateway"]

    critical_suppliers:
      type: array
      items:
        type: object
        properties:
          supplier_name:
            type: string
          criticality:
            type: string

    # Dependencies
    upstream_dependencies:
      type: array
      items:
        type: string
        format: uuid
    downstream_dependencies:
      type: array
      items:
        type: string
        format: uuid

    # Metadata
    status:
      type: string
      enum: [draft, in_review, approved, archived]
      example: "approved"
    last_review_date:
      type: string
      format: date
    next_review_date:
      type: string
      format: date
    created_at:
      type: string
      format: date-time
    updated_at:
      type: string
      format: date-time
```

#### Example Request: Create BIA

```http
POST /v1/bia HTTP/1.1
Host: api.bcm.example.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "process_name": "Customer Billing Process",
  "process_description": "Monthly billing cycle for all customers",
  "owner_id": "123e4567-e89b-12d3-a456-426614174000",
  "department": "Finance",
  "mtpd_hours": 24,
  "rto_hours": 12,
  "rpo_hours": 4,
  "financial_impact_per_hour": 50000.00,
  "operational_impact": "high",
  "criticality": "critical",
  "priority_tier": 1,
  "minimum_staff_required": 5,
  "critical_systems": ["ERP System", "Payment Gateway"]
}
```

#### Example Response

```http
HTTP/1.1 201 Created
Content-Type: application/json
Location: /v1/bia/550e8400-e29b-41d4-a716-446655440000

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "tenant_abc",
  "process_name": "Customer Billing Process",
  "process_description": "Monthly billing cycle for all customers",
  "owner_id": "123e4567-e89b-12d3-a456-426614174000",
  "department": "Finance",
  "mtpd_hours": 24,
  "rto_hours": 12,
  "rpo_hours": 4,
  "financial_impact_per_hour": 50000.00,
  "operational_impact": "high",
  "criticality": "critical",
  "priority_tier": 1,
  "status": "draft",
  "created_at": "2025-01-07T14:30:00Z",
  "updated_at": "2025-01-07T14:30:00Z"
}
```

---

### 2. Risk Assessment API

#### Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/risks` | List all risks | ✅ |
| `POST` | `/risks` | Create new risk | ✅ |
| `GET` | `/risks/{id}` | Get risk by ID | ✅ |
| `PUT` | `/risks/{id}` | Update risk | ✅ |
| `DELETE` | `/risks/{id}` | Delete risk | ✅ |
| `POST` | `/risks/{id}/assess` | Run AI risk assessment | ✅ |
| `GET` | `/risks/heatmap` | Get risk heat map | ✅ |
| `GET` | `/risks/reports/treatment-plan` | Get treatment plan report | ✅ |

#### Data Models

**Risk:**
```yaml
Risk:
  type: object
  required:
    - title
    - category
    - likelihood
    - impact
  properties:
    id:
      type: string
      format: uuid
    tenant_id:
      type: string
      format: uuid

    # Identification
    title:
      type: string
      example: "Data Center Power Failure"
    description:
      type: string
      example: "Primary data center experiences extended power outage"
    category:
      type: string
      enum: [strategic, operational, financial, compliance, technology, environmental]
      example: "operational"
    source:
      type: string
      enum: [bia, context_analysis, stakeholder_input, incident, audit]
      example: "bia"

    # Analysis
    likelihood:
      type: string
      enum: [very_low, low, medium, high, very_high]
      example: "low"
    likelihood_score:
      type: integer
      minimum: 1
      maximum: 5
      example: 2

    impact:
      type: string
      enum: [very_low, low, medium, high, very_high]
      example: "very_high"
    impact_score:
      type: integer
      minimum: 1
      maximum: 5
      example: 5

    risk_score:
      type: number
      description: "Calculated as likelihood_score * impact_score"
      example: 10

    inherent_risk_level:
      type: string
      enum: [low, medium, high, critical]
      example: "high"

    # Treatment
    treatment_strategy:
      type: string
      enum: [avoid, reduce, transfer, accept]
      example: "reduce"

    controls:
      type: array
      items:
        type: object
        properties:
          control_name:
            type: string
          effectiveness:
            type: string
            enum: [low, medium, high]
          implementation_status:
            type: string
            enum: [planned, in_progress, implemented]

    residual_risk_level:
      type: string
      enum: [low, medium, high, critical]
      example: "medium"

    # Ownership
    owner_id:
      type: string
      format: uuid
    reviewer_id:
      type: string
      format: uuid

    # Timeline
    review_date:
      type: string
      format: date

    # Status
    status:
      type: string
      enum: [identified, analyzed, treated, monitored, closed]
      example: "treated"

    created_at:
      type: string
      format: date-time
    updated_at:
      type: string
      format: date-time
```

---

### 3. BC Plans API

#### Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/plans` | List all BC plans | ✅ |
| `POST` | `/plans` | Create new BC plan | ✅ |
| `GET` | `/plans/{id}` | Get plan by ID | ✅ |
| `PUT` | `/plans/{id}` | Update plan | ✅ |
| `DELETE` | `/plans/{id}` | Delete plan | ✅ |
| `POST` | `/plans/{id}/activate` | Activate BC plan (incident) | ✅ |
| `POST` | `/plans/{id}/deactivate` | Deactivate BC plan | ✅ |
| `POST` | `/plans/generate` | AI-generate BC plan from BIA | ✅ |
| `GET` | `/plans/{id}/pdf` | Export plan as PDF | ✅ |

#### Data Models

**BC Plan:**
```yaml
BCPlan:
  type: object
  required:
    - plan_name
    - processes_covered
    - activation_criteria
  properties:
    id:
      type: string
      format: uuid
    tenant_id:
      type: string
      format: uuid
    plan_id:
      type: string
      example: "BCP-2025-001"
    plan_name:
      type: string
      example: "Customer Billing Process BC Plan"
    version:
      type: string
      example: "2.1"
    effective_date:
      type: string
      format: date

    # Scope
    processes_covered:
      type: array
      items:
        type: string
        format: uuid
    activation_criteria:
      type: array
      items:
        type: string
      example:
        - "Primary billing system unavailable > 2 hours"
        - "Payment gateway failure"

    # Structure
    incident_commander_id:
      type: string
      format: uuid
    response_team:
      type: array
      items:
        type: object
        properties:
          role:
            type: string
          user_id:
            type: string
            format: uuid
          responsibilities:
            type: array
            items:
              type: string

    procedures:
      type: object
      properties:
        activation:
          type: array
          items:
            $ref: '#/components/schemas/ProcedureStep'
        continuity:
          type: array
          items:
            $ref: '#/components/schemas/ProcedureStep'
        recovery:
          type: array
          items:
            $ref: '#/components/schemas/ProcedureStep'
        standdown:
          type: array
          items:
            $ref: '#/components/schemas/ProcedureStep'

    resources:
      type: object
      properties:
        personnel:
          type: array
          items:
            type: object
        systems:
          type: array
          items:
            type: object
        facilities:
          type: array
          items:
            type: object
        suppliers:
          type: array
          items:
            type: object

    communication_plan:
      type: object
      properties:
        stakeholders:
          type: array
          items:
            type: object
            properties:
              group:
                type: string
              channel:
                type: string
              frequency:
                type: string
              template:
                type: string

    # Ownership
    owner_id:
      type: string
      format: uuid
    approver_id:
      type: string
      format: uuid
    approval_date:
      type: string
      format: date

    # Status
    status:
      type: string
      enum: [draft, approved, active, archived]
    last_review_date:
      type: string
      format: date
    next_review_date:
      type: string
      format: date
    last_tested_date:
      type: string
      format: date
    next_test_date:
      type: string
      format: date

    classification:
      type: string
      enum: [public, internal, confidential, restricted]

    created_at:
      type: string
      format: date-time
    updated_at:
      type: string
      format: date-time

ProcedureStep:
  type: object
  required:
    - step
    - responsible
  properties:
    step:
      type: string
      example: "Assess situation severity"
    responsible:
      type: string
      example: "Incident Commander"
    time_limit:
      type: string
      example: "15 minutes"
    details:
      type: string
    checklist:
      type: array
      items:
        type: string
```

---

### 4. Exercises API

#### Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/exercises` | List all exercises | ✅ |
| `POST` | `/exercises` | Create new exercise | ✅ |
| `GET` | `/exercises/{id}` | Get exercise by ID | ✅ |
| `PUT` | `/exercises/{id}` | Update exercise | ✅ |
| `POST` | `/exercises/{id}/start` | Start exercise | ✅ |
| `POST` | `/exercises/{id}/inject` | Send scenario inject | ✅ |
| `POST` | `/exercises/{id}/observe` | Add observation | ✅ |
| `POST` | `/exercises/{id}/complete` | Complete exercise | ✅ |
| `GET` | `/exercises/{id}/report` | Generate after-action report | ✅ |

---

### 5. Incidents API

#### Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/incidents` | List all incidents | ✅ |
| `POST` | `/incidents` | Create new incident | ✅ |
| `GET` | `/incidents/{id}` | Get incident by ID | ✅ |
| `PUT` | `/incidents/{id}` | Update incident | ✅ |
| `POST` | `/incidents/{id}/activate-plan` | Activate BC plan | ✅ |
| `POST` | `/incidents/{id}/log` | Add incident log entry | ✅ |
| `POST` | `/incidents/{id}/resolve` | Resolve incident | ✅ |
| `GET` | `/incidents/{id}/timeline` | Get incident timeline | ✅ |

#### Data Models

**Incident:**
```yaml
Incident:
  type: object
  required:
    - title
    - severity
    - incident_type
  properties:
    id:
      type: string
      format: uuid
    tenant_id:
      type: string
      format: uuid
    incident_id:
      type: string
      example: "INC-2025-0042"

    # Identification
    title:
      type: string
      example: "Primary Data Center Power Failure"
    description:
      type: string
    incident_type:
      type: string
      enum: [natural_disaster, cyber_attack, system_failure, supply_chain, personnel, other]
      example: "system_failure"
    severity:
      type: string
      enum: [low, medium, high, critical]
      example: "critical"

    # Impact
    affected_processes:
      type: array
      items:
        type: string
        format: uuid
    affected_systems:
      type: array
      items:
        type: string
    estimated_impact:
      type: string

    # Response
    incident_commander_id:
      type: string
      format: uuid
    response_team:
      type: array
      items:
        type: string
        format: uuid
    activated_plans:
      type: array
      items:
        type: string
        format: uuid

    # Timeline
    detected_at:
      type: string
      format: date-time
    acknowledged_at:
      type: string
      format: date-time
    resolved_at:
      type: string
      format: date-time

    # Status
    status:
      type: string
      enum: [detected, acknowledged, in_progress, resolved, closed]
      example: "in_progress"

    # Metrics
    rto_achievement:
      type: boolean
    actual_recovery_time_hours:
      type: number

    created_at:
      type: string
      format: date-time
    updated_at:
      type: string
      format: date-time
```

---

### 6. Users & Authentication API

#### Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/auth/login` | User login | ❌ |
| `POST` | `/auth/logout` | User logout | ✅ |
| `POST` | `/auth/refresh` | Refresh access token | ✅ |
| `POST` | `/auth/register` | Register new user | ❌ |
| `POST` | `/auth/password/reset` | Request password reset | ❌ |
| `GET` | `/users/me` | Get current user profile | ✅ |
| `PUT` | `/users/me` | Update current user profile | ✅ |
| `GET` | `/users` | List users (admin only) | ✅ |
| `GET` | `/users/{id}` | Get user by ID | ✅ |
| `PUT` | `/users/{id}/role` | Update user role (admin only) | ✅ |

---

### 7. Analytics & Reporting API

#### Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/analytics/dashboard` | Get dashboard metrics | ✅ |
| `GET` | `/analytics/kpis` | Get KPI measurements | ✅ |
| `GET` | `/reports/bia-summary` | BIA summary report | ✅ |
| `GET` | `/reports/risk-summary` | Risk summary report | ✅ |
| `GET` | `/reports/compliance` | Compliance report | ✅ |
| `GET` | `/reports/executive-summary` | Executive summary | ✅ |

---

## Complete OpenAPI YAML

```yaml
openapi: 3.0.3
info:
  title: BCM AI Platform API
  version: 1.0.0
  description: |
    Enterprise Business Continuity Management Platform with AI/ML capabilities.

    ## Features
    - Business Impact Analysis (BIA)
    - Risk Assessment & Management
    - Business Continuity Planning
    - Incident Response
    - Exercise Management
    - Compliance Tracking (ISO 22301)
    - AI-Powered Analytics

    ## Authentication
    All endpoints require OAuth 2.0 Bearer token authentication except for auth endpoints.

  contact:
    name: API Support
    email: api-support@bcm.example.com
    url: https://docs.bcm.example.com
  license:
    name: Proprietary
    url: https://bcm.example.com/license

servers:
  - url: https://api.bcm.example.com/v1
    description: Production
  - url: https://staging-api.bcm.example.com/v1
    description: Staging
  - url: https://dev-api.bcm.example.com/v1
    description: Development

tags:
  - name: BIA
    description: Business Impact Analysis operations
  - name: Risk
    description: Risk assessment and management
  - name: Plans
    description: Business continuity plans
  - name: Exercises
    description: Exercise and testing management
  - name: Incidents
    description: Incident response and management
  - name: Auth
    description: Authentication and authorization
  - name: Users
    description: User management
  - name: Analytics
    description: Analytics and reporting

security:
  - BearerAuth: []

paths:
  # BIA Endpoints
  /bia:
    get:
      tags: [BIA]
      summary: List BIA analyses
      description: Retrieve a list of all BIA analyses for the authenticated tenant
      operationId: listBIAs
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [draft, in_review, approved, archived]
        - name: criticality
          in: query
          schema:
            type: string
            enum: [critical, important, normal]
        - name: limit
          in: query
          schema:
            type: integer
            default: 50
            maximum: 100
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/BIAAnalysis'
                  pagination:
                    $ref: '#/components/schemas/Pagination'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          $ref: '#/components/responses/Forbidden'

    post:
      tags: [BIA]
      summary: Create BIA analysis
      description: Create a new BIA analysis
      operationId: createBIA
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BIAAnalysisCreate'
      responses:
        '201':
          description: BIA created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BIAAnalysis'
          headers:
            Location:
              schema:
                type: string
              description: URL of the created resource
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          $ref: '#/components/responses/Forbidden'

  /bia/{id}:
    get:
      tags: [BIA]
      summary: Get BIA by ID
      operationId: getBIAById
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BIAAnalysis'
        '404':
          $ref: '#/components/responses/NotFound'

    put:
      tags: [BIA]
      summary: Update BIA
      operationId: updateBIA
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BIAAnalysisUpdate'
      responses:
        '200':
          description: BIA updated successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BIAAnalysis'
        '400':
          $ref: '#/components/responses/BadRequest'
        '404':
          $ref: '#/components/responses/NotFound'

    delete:
      tags: [BIA]
      summary: Delete BIA
      operationId: deleteBIA
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '204':
          description: BIA deleted successfully
        '404':
          $ref: '#/components/responses/NotFound'

  /bia/{id}/analyze:
    post:
      tags: [BIA]
      summary: AI analysis of BIA
      description: Run AI-powered analysis to provide insights and recommendations
      operationId: analyzeBIA
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Analysis completed
          content:
            application/json:
              schema:
                type: object
                properties:
                  criticality_assessment:
                    type: string
                  recommended_rto:
                    type: integer
                  recommended_rpo:
                    type: integer
                  similar_processes:
                    type: array
                    items:
                      type: object
                  insights:
                    type: array
                    items:
                      type: string

  # Auth Endpoints
  /auth/login:
    post:
      tags: [Auth]
      summary: User login
      description: Authenticate user and receive access token
      operationId: login
      security: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - email
                - password
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
                  format: password
      responses:
        '200':
          description: Login successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                  token_type:
                    type: string
                    example: "Bearer"
                  expires_in:
                    type: integer
                    example: 900
                  refresh_token:
                    type: string
                  user:
                    $ref: '#/components/schemas/User'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /auth/refresh:
    post:
      tags: [Auth]
      summary: Refresh access token
      operationId: refreshToken
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - refresh_token
              properties:
                refresh_token:
                  type: string
      responses:
        '200':
          description: Token refreshed
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                  token_type:
                    type: string
                  expires_in:
                    type: integer

  # Users
  /users/me:
    get:
      tags: [Users]
      summary: Get current user profile
      operationId: getCurrentUser
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://api.bcm.example.com/oauth/authorize
          tokenUrl: https://api.bcm.example.com/oauth/token
          scopes:
            read: Read access
            write: Write access
            admin: Admin access

  schemas:
    BIAAnalysis:
      type: object
      properties:
        id:
          type: string
          format: uuid
        tenant_id:
          type: string
          format: uuid
        process_name:
          type: string
        process_description:
          type: string
        owner_id:
          type: string
          format: uuid
        department:
          type: string
        mtpd_hours:
          type: integer
        rto_hours:
          type: integer
        rpo_hours:
          type: integer
        financial_impact_per_hour:
          type: number
        operational_impact:
          type: string
          enum: [critical, high, medium, low]
        criticality:
          type: string
          enum: [critical, important, normal]
        priority_tier:
          type: integer
        status:
          type: string
          enum: [draft, in_review, approved, archived]
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    BIAAnalysisCreate:
      type: object
      required:
        - process_name
        - owner_id
        - mtpd_hours
        - rto_hours
        - rpo_hours
      properties:
        process_name:
          type: string
        process_description:
          type: string
        owner_id:
          type: string
          format: uuid
        department:
          type: string
        mtpd_hours:
          type: integer
        rto_hours:
          type: integer
        rpo_hours:
          type: integer
        financial_impact_per_hour:
          type: number
        operational_impact:
          type: string
          enum: [critical, high, medium, low]

    BIAAnalysisUpdate:
      type: object
      properties:
        process_name:
          type: string
        process_description:
          type: string
        mtpd_hours:
          type: integer
        rto_hours:
          type: integer
        rpo_hours:
          type: integer
        status:
          type: string
          enum: [draft, in_review, approved, archived]

    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        name:
          type: string
        role:
          type: string
          enum: [super_admin, tenant_admin, bcm_manager, analyst, contributor, viewer]
        tenant_id:
          type: string
          format: uuid
        created_at:
          type: string
          format: date-time

    Pagination:
      type: object
      properties:
        total:
          type: integer
        limit:
          type: integer
        offset:
          type: integer
        has_more:
          type: boolean

    Error:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
            message:
              type: string
            details:
              type: object

  responses:
    BadRequest:
      description: Bad request
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

    Unauthorized:
      description: Unauthorized
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

    Forbidden:
      description: Forbidden
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
```

---

## API Usage Examples

### Python Client

```python
import requests
from typing import Optional

class BCMClient:
    def __init__(self, base_url: str, access_token: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def create_bia(self, data: dict) -> dict:
        """Create a new BIA analysis"""
        response = requests.post(
            f"{self.base_url}/bia",
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_bia(self, bia_id: str) -> dict:
        """Get BIA by ID"""
        response = requests.get(
            f"{self.base_url}/bia/{bia_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def list_bias(
        self,
        status: Optional[str] = None,
        criticality: Optional[str] = None,
        limit: int = 50
    ) -> dict:
        """List BIA analyses"""
        params = {"limit": limit}
        if status:
            params["status"] = status
        if criticality:
            params["criticality"] = criticality

        response = requests.get(
            f"{self.base_url}/bia",
            params=params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Usage
client = BCMClient(
    base_url="https://api.bcm.example.com/v1",
    access_token="your_access_token"
)

# Create BIA
bia = client.create_bia({
    "process_name": "Customer Billing",
    "owner_id": "123e4567-e89b-12d3-a456-426614174000",
    "mtpd_hours": 24,
    "rto_hours": 12,
    "rpo_hours": 4,
    "financial_impact_per_hour": 50000,
    "operational_impact": "high"
})

print(f"Created BIA: {bia['id']}")
```

### JavaScript/TypeScript Client

```typescript
class BCMClient {
  private baseUrl: string;
  private accessToken: string;

  constructor(baseUrl: string, accessToken: string) {
    this.baseUrl = baseUrl;
    this.accessToken = accessToken;
  }

  async createBIA(data: any): Promise<any> {
    const response = await fetch(`${this.baseUrl}/bia`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async getBIA(id: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/bia/${id}`, {
      headers: {
        'Authorization': `Bearer ${this.accessToken}`
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }
}

// Usage
const client = new BCMClient(
  'https://api.bcm.example.com/v1',
  'your_access_token'
);

const bia = await client.createBIA({
  process_name: 'Customer Billing',
  owner_id: '123e4567-e89b-12d3-a456-426614174000',
  mtpd_hours: 24,
  rto_hours: 12,
  rpo_hours: 4
});
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "rto_hours",
      "reason": "RTO must be less than MTPD"
    }
  }
}
```

### Error Codes

| HTTP Status | Error Code | Description |
|-------------|-----------|-------------|
| 400 | `VALIDATION_ERROR` | Request validation failed |
| 401 | `UNAUTHORIZED` | Authentication required |
| 401 | `INVALID_TOKEN` | Access token is invalid or expired |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 409 | `CONFLICT` | Resource conflict (duplicate) |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |
| 500 | `INTERNAL_SERVER_ERROR` | Server error |
| 503 | `SERVICE_UNAVAILABLE` | Service temporarily unavailable |

---

## Rate Limiting

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1735689600
```

### Rate Limit Tiers

| Tier | Requests/Minute | Requests/Hour |
|------|----------------|---------------|
| Free | 60 | 1,000 |
| Professional | 300 | 10,000 |
| Enterprise | 1,000 | 50,000 |

---

## Versioning

### URL Versioning

API version is specified in the URL path:
- `/v1/bia` - Version 1 (current)
- `/v2/bia` - Version 2 (future)

### Version Lifecycle

- **Supported:** Minimum 12 months after deprecation notice
- **Deprecated:** 90 days notice before deprecation
- **Sunset:** Version becomes unavailable

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-07
**Maintained By:** API Team
