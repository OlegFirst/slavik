# PLATFORM SERVICES - COMPLETE CATALOG

**Generated:** 2025-10-08 (Latest Documentation Update)
**Total Services:** 12 Core Services + 3 Support Modules + 2 Monitoring Services
**Architecture:** ISO 22301:2019 Business Continuity Management Platform
**Integration:** Workflow Intelligence, AI Foundation, EventBus

---

## Executive Summary

### Platform Statistics
- **Total Microservices:** 12 core BCM services
- **Total API Endpoints:** 735+
- **Total Lines of Code:** 162,537
- **Port Range:** 8011-8085
- **Database:** PostgreSQL (bcm_platform) with multi-schema architecture
- **Cache:** Redis (shared across all services)
- **Message Queue:** RabbitMQ for async workflows
- **Event System:** EventBus integration (all services)
- **AI Integration:** Workflow Intelligence mounted volume
- **Containerization:** Docker + Docker Compose
- **Monitoring:** Prometheus + Grafana

### Integration Status
- **Workflow Intelligence:** 100% (all services mount /intelligent-core/workflow_intelligence)
- **AI Foundation:** 100% (integrated via WorkflowIntelligenceClient)
- **EventBus:** 100% (all services publish/subscribe)
- **Database Schemas:** Defined and isolated per domain
- **Health Checks:** 100% (all services have /health endpoint)
- **Metrics:** 100% (all services expose /metrics)

---

## Service Categories

### Core BCM Services (ISO 22301 Compliance)
1. **BIA Service** (8012) - Business Impact Analysis
2. **Risk Service** (8040) - Risk Management
3. **Compliance Service** (8014) - Audit & Compliance
4. **Governance Service** (8013) - Organizational Governance
5. **Documents Service** (8024) - Document Management
6. **Validation Service** (8022) - KPI & Validation

### Planning & Execution Services
7. **Planning Service** (8011) - Strategy Development
8. **Plans Service** (8023) - Plan Repository & Management
9. **Response Service** (8041) - Incident Response

### Intelligence & Learning Services
10. **Learning Service** (8021) - Training & Competency
11. **Living Docs** (8034) - Self-Improving Documentation
12. **Simulation** (8031+) - Scenario Testing & Digital Twin

### Coordination Services
13. **BCM Coordination** (8070) - Analyzer Coordination

### Community & Collaboration
14. **Community Service** (8031-8033) - Portal & Marketplace

### Monitoring Services
15. **Compliance Monitoring** (8045) - Compliance Analytics
16. **Process Analytics** (8780) - Process Mining

---

## Complete Service Catalog

### 1. BIA Service (Business Impact Analysis)

**ISO 22301 Clause:** 8.2.2
**Port:** 8012
**Status:** Active
**Version:** 2.0.0

**Purpose:**
Business Impact Analysis capabilities including criticality assessment, dependency mapping, and recovery time objective determination with AI-powered recommendations.

**Metrics:**
- Lines of Code: 6,919
- Python Files: 30
- Classes: 77
- Functions: 26
- API Endpoints: 31
- Dependencies: 60

**Database Tables:**
- `bia_processes` - Business processes with ISO 22301 fields
- `bia_assessments` - Impact assessments and recovery objectives
- `bia_resources` - Resource requirements tracking
- `bia_dependencies` - Process dependency mapping

**API Endpoints:**
- GET /health - Health check
- GET /metrics - Prometheus metrics
- POST /api/v1/bia - Create BIA process
- GET /api/v1/bia/{id} - Get BIA process
- PUT /api/v1/bia/{id} - Update BIA process
- DELETE /api/v1/bia/{id} - Delete BIA process
- GET /api/v1/bia/criticality/{level} - Filter by criticality
- POST /api/v1/bia/{id}/assessment - Create assessment
- GET /api/v1/bia/{id}/dependencies - Get dependencies
- POST /api/v1/bia/{id}/resources - Add resource requirement

**Dependencies:**
- Internal: workflow_intelligence, ai-foundation
- Database: PostgreSQL (bcm_platform)
- Cache: Redis
- Message Queue: RabbitMQ
- External: None

**EventBus Integration:**
- Publishes: `bia.created`, `bia.updated`, `bia.assessment.completed`
- Subscribes: `bia.*`

**Environment Variables:**
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/bcm_platform
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://user:pass@localhost:5672/
SERVICE_PORT=8012
```

**Docker:** bcm-bia-service
**Health Check:** http://localhost:8012/health
**API Docs:** http://localhost:8012/docs

**Issues:** None

---

### 2. Compliance Service

**ISO 22301 Clauses:** 9.2, 10.1, 10.2
**Port:** 8014
**Status:** Active
**Version:** 2.0.0

**Purpose:**
Manages regulatory compliance and standards adherence including gap analysis, audit management, nonconformity tracking with root cause analysis, and certification tracking.

**Metrics:**
- Lines of Code: 17,480
- Python Files: 55
- Classes: 136
- Functions: 41
- API Endpoints: 95
- Dependencies: 94

**Database Tables:**
- `audits` - Internal audit management
- `audit_evidence` - Evidence collection
- `audit_findings` - Findings and gaps
- `nonconformities` - NC tracking with RCA templates
- `corrective_actions` - CA planning and verification
- `improvements` - Continual improvement initiatives
- `audit_logs` - Audit trail for all operations
- `change_history` - Field-level change tracking

**API Endpoints:**
- GET /health - Health check
- GET /metrics - Prometheus metrics
- Audit endpoints (15): Create, list, update, schedule, evidence, findings
- Nonconformity endpoints (20): CRUD, RCA (5 Whys, Fishbone, Fault Tree)
- Corrective Action endpoints (15): Planning, tracking, effectiveness
- Improvement endpoints (12): Initiatives, KPIs, change tracking
- Workflow endpoints (10): Validation, state transitions
- Report endpoints (8): Gap analysis, compliance reports

**Dependencies:**
- Internal: workflow_intelligence, ai-foundation
- Database: PostgreSQL (bcm_platform)
- Cache: Redis
- Message Queue: RabbitMQ

**EventBus Integration:**
- Publishes: `compliance.audit.*`, `compliance.nonconformity.*`, `compliance.improvement.*`
- Subscribes: `compliance.*`

**Special Features:**
- Root Cause Analysis: 5 Whys, Fishbone Diagram, Fault Tree Analysis
- Workflow Validators: 68 edge case validations
- Audit Trail: ISO-compliant activity logging
- Change History: DeepDiff-based field-level tracking

**Docker:** bcm-compliance-service
**Health Check:** http://localhost:8014/health
**API Docs:** http://localhost:8014/docs

---

### 3. Governance Service

**ISO 22301 Clauses:** 4, 5
**Port:** 8013
**Status:** Active
**Version:** 2.0.0

**Purpose:**
Organizational governance frameworks for BCM including stakeholder management, decision-making processes, organizational context analysis, governance structure definition, and accountability tracking.

**Metrics:**
- Lines of Code: 7,224
- Python Files: 27
- Classes: 90
- Functions: 4
- API Endpoints: 46
- Dependencies: 48

**Database Tables:**
- `governance_policies` - Policy definitions
- `governance_stakeholders` - Stakeholder management
- `governance_responsibilities` - Role assignments
- `governance_context` - Organizational context
- `governance_decisions` - Decision tracking
- `governance_reviews` - Review cycles

**API Endpoints:**
- GET /health
- GET /metrics
- Policy endpoints (12): CRUD, approval workflows
- Stakeholder endpoints (10): Management, communication
- Context endpoints (8): Organization analysis
- Decision endpoints (10): Tracking, approval
- Review endpoints (6): Scheduling, reporting

**Dependencies:**
- Internal: workflow_intelligence, ai-foundation
- Database: PostgreSQL (bcm_platform), Supabase
- Cache: Redis
- Message Queue: RabbitMQ

**EventBus Integration:**
- Publishes: `governance.policy.*`, `governance.stakeholder.*`, `governance.decision.*`
- Subscribes: `governance.*`

**Environment Variables:**
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/bcm_platform
REDIS_URL=redis://localhost:6379/1
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_KEY=${SUPABASE_KEY}
SERVICE_PORT=8013
```

**Docker:** bcm-governance-service

---

### 4. Risk Service

**ISO 22301 Clause:** 8.2.3
**Port:** 8040
**Status:** Active
**Version:** 2.0.0

**Purpose:**
Comprehensive risk management including risk identification, assessment, treatment planning, and monitoring with risk matrices, heat maps, and integration with mitigation workflows.

**Metrics:**
- Lines of Code: 6,126
- Python Files: 23
- Classes: 48
- Functions: 23
- API Endpoints: 29
- Dependencies: 47

**Database Tables:**
- `risks` - Risk register
- `risk_assessments` - Impact and likelihood assessments
- `risk_treatments` - Treatment plans
- `risk_controls` - Control measures
- `risk_monitoring` - Monitoring activities

**API Endpoints:**
- GET /health
- GET /metrics
- Risk endpoints (10): CRUD, assessment
- Treatment endpoints (8): Planning, implementation
- Control endpoints (6): Management, effectiveness
- Monitoring endpoints (5): KPIs, dashboards

**Risk Features:**
- FAIR Analysis with confidence intervals
- Monte Carlo simulation (1,000-100,000 iterations)
- Risk scoring: Critical (>=20), High (15-19), Medium (8-14), Low (<8)
- Automated review scheduling by risk level

**Dependencies:**
- Internal: workflow_intelligence, ai-foundation
- Database: PostgreSQL (bcm_platform)
- Cache: Redis
- Message Queue: RabbitMQ

**EventBus Integration:**
- Publishes: `risk.created`, `risk.assessed`, `risk.treated`, `risk.escalated`
- Subscribes: `risk.*`

**Docker:** bcm-risk-service
**Port:** 8040

---

### 5. Documents Service

**ISO 22301 Clause:** 7.5
**Port:** 8024
**Status:** Active
**Version:** 2.0.0

**Purpose:**
Complete lifecycle management of business continuity documentation including policy documents, procedures, plans, and templates with version control, approval workflows, access control, and document generation.

**Metrics:**
- Lines of Code: 10,136
- Python Files: 32
- Classes: 71
- Functions: 51
- API Endpoints: 30
- Dependencies: 78

**Database Tables:**
- `documents` - Document metadata
- `document_versions` - Version history
- `document_approvals` - Approval workflows
- `document_access` - Access control
- `document_templates` - Template library
- `document_metadata` - Extended metadata

**API Endpoints:**
- GET /health
- GET /metrics
- Document endpoints (12): CRUD, upload, download
- Version endpoints (6): History, compare, restore
- Approval endpoints (5): Submit, approve, reject
- Template endpoints (4): Library, generate
- Search endpoints (3): Full-text, metadata

**Special Features:**
- Document analysis and classification (AI-powered)
- Document comparison and diff
- Vector database integration (Qdrant)
- Automated version control

**Dependencies:**
- Internal: workflow_intelligence, ai-foundation
- Database: PostgreSQL (bcm_platform)
- Cache: Redis
- Vector DB: Qdrant
- Message Queue: RabbitMQ
- Storage: Volume mount for uploads

**EventBus Integration:**
- Publishes: `documents.created`, `documents.approved`, `documents.archived`
- Subscribes: `documents.*`

**Docker:** bcm-documents-service
**Volumes:** document-uploads:/app/uploads

---

### 6. Validation Service

**ISO 22301 Clauses:** 8.5, 9.1-9.3, 10
**Port:** 8022
**Status:** Active
**Version:** 2.0.0

**Purpose:**
Comprehensive validation capabilities for BCM processes including KPI monitoring, alert management, continuous process improvement, automated validation workflows with real-time metrics collection, and threshold-based alerting.

**Metrics:**
- Lines of Code: 7,567
- Python Files: 32
- Classes: 109
- Functions: 53
- API Endpoints: 49
- Dependencies: 60

**Database Tables:**
- `validation_kpis` - KPI definitions
- `validation_metrics` - Metric data points
- `validation_alerts` - Alert configurations
- `validation_thresholds` - Threshold rules
- `validation_reports` - Validation reports
- `validation_improvements` - Improvement tracking

**API Endpoints:**
- GET /health
- GET /metrics
- KPI endpoints (15): Define, track, analyze
- Alert endpoints (10): Configure, trigger, acknowledge
- Metric endpoints (12): Collect, aggregate, query
- Report endpoints (8): Generate, schedule, distribute
- Improvement endpoints (4): Track, measure

**Dependencies:**
- Internal: workflow_intelligence, ai-foundation
- Database: PostgreSQL (bcm_platform)
- Cache: Redis
- Message Queue: RabbitMQ

**EventBus Integration:**
- Publishes: `validation.kpi.*`, `validation.alert.*`, `validation.threshold.exceeded`
- Subscribes: `validation.*`

**Docker:** bcm-validation-service

---

### 7. Planning Service

**ISO 22301 Clause:** 8.3
**Port:** 8011
**Status:** Active
**Version:** 2.0.0

**Purpose:**
Business Continuity Strategy development including multi-strategy types (preventive, detective, corrective, recovery), cost-benefit analysis with NPV and payback period, resource planning and allocation, and approval workflows.

**Metrics:**
- Lines of Code: 6,201
- Python Files: 35
- Classes: 50
- Functions: 10
- API Endpoints: 20
- Dependencies: 54

**Database Tables:**
- `strategies` - Business continuity strategies
- `strategy_resources` - Resource allocations
- `cost_benefit_analyses` - Financial analyses
- `strategy_approvals` - Approval workflows

**API Endpoints:**
- GET /health
- GET /metrics
- Strategy endpoints (10): CRUD, approval
- Cost-benefit endpoints (5): Calculate NPV, ROI, payback
- Resource endpoints (5): Allocate, track

**Financial Features:**
- NPV (Net Present Value) with proper discounting
- Payback Period with time value of money
- ROI calculations
- Support for 1-30 year timeframes
- 25+ Pydantic validators

**Dependencies:**
- Internal: workflow_intelligence
- Database: PostgreSQL (bcm_platform)
- Cache: Redis

**EventBus Integration:**
- Publishes: `planning_service.strategy.*`, `planning_service.approved`
- Subscribes: `planning_service.*`

**Docker:** bcm-planning-service
**Tests:** 127 tests, 85%+ coverage

---

### 8. Plans Service

**ISO 22301 Clause:** 8.4
**Port:** 8023
**Status:** Active
**Version:** 2.0.0

**Purpose:**
Centralized repository and management for all business continuity plans including plan storage, retrieval, distribution, activation workflows, version control, review and approval workflows, testing and exercise scheduling.

**Metrics:**
- Lines of Code: 8,612
- Python Files: 38
- Classes: 79
- Functions: 28
- API Endpoints: 32
- Dependencies: 64

**Database Tables:**
- `plans` - Business continuity plans
- `procedures` - Procedures with dependencies
- `plan_resources` - Resource allocations
- `plan_exercises` - Testing and exercises
- `plan_versions` - Version control
- `plan_approvals` - Approval workflows

**API Endpoints:**
- GET /health
- GET /metrics
- Plan endpoints (12): CRUD, activate, version
- Procedure endpoints (10): CRUD, dependencies, order
- Exercise endpoints (6): Schedule, execute, review
- Resource endpoints (4): Allocate, track

**Special Features:**
- Procedure Dependency Validator: Prevents circular dependencies
- Topological sorting for execution order (DFS algorithm)
- N+1 Query Prevention: Eager loading with SQLAlchemy
- Resource allocation tracking

**Dependencies:**
- Internal: workflow_intelligence
- Database: PostgreSQL (bcm_platform)
- Cache: Redis

**EventBus Integration:**
- Publishes: `plans_service.created`, `plans_service.activated`, `plans_service.tested`
- Subscribes: `plans_service.*`

**Docker:** bcm-plans-service
**Tests:** 95 tests, 85%+ coverage

---

### 9. Response Service

**ISO 22301 Clause:** 8.4.5
**Port:** 8041
**Status:** Active
**Version:** 2.0.0

**Purpose:**
Complete incident and emergency response lifecycle management from detection through resolution and post-incident review including response plan activation, team coordination, escalation workflows, and lessons learned capture.

**Metrics:**
- Lines of Code: 10,711
- Python Files: 30
- Classes: 80
- Functions: 33
- API Endpoints: 38
- Dependencies: 50

**Database Tables:**
- `incidents` - Incident tracking
- `incident_timeline` - Event timeline
- `incident_teams` - Response teams
- `incident_escalations` - Escalation tracking
- `incident_communications` - Communication log
- `lessons_learned` - Post-incident analysis

**API Endpoints:**
- GET /health
- GET /metrics
- Incident endpoints (15): CRUD, activate, resolve
- Timeline endpoints (5): Track events
- Team endpoints (6): Assign, coordinate
- Escalation endpoints (4): Trigger, manage
- Communication endpoints (4): Log, notify
- Lessons endpoints (4): Capture, analyze

**Response Features:**
- Auto-escalate critical incidents
- Auto-create timeline entries
- Response time tracking by severity:
  - Critical: 15 minutes
  - High: 60 minutes
  - Medium: 120 minutes
  - Low: 240 minutes
- Require root cause on resolution

**Dependencies:**
- Internal: workflow_intelligence, ai-foundation
- External Services:
  - Risk Service (8040)
  - Impact Service (8032)
  - Recovery Service (8042)
- Database: PostgreSQL (bcm_platform)
- Cache: Redis

**EventBus Integration:**
- Publishes: `response.incident.*`, `response.escalated`, `response.resolved`
- Subscribes: `response.*`

**Docker:** bcm-response-service

---

### 10. Learning Service

**ISO 22301 Clauses:** 7.2, 7.3
**Port:** 8021
**Status:** Active
**Version:** 2.0.0

**Purpose:**
Training, awareness, and competency development for BCM including learning paths, assessments, certification tracking, and skills gap analysis.

**Metrics:**
- Lines of Code: 6,267
- Python Files: 33
- Classes: 83
- Functions: 45
- API Endpoints: 34
- Dependencies: 48

**Database Tables:**
- `training_programs` - Program catalog
- `training_enrollments` - User enrollments
- `training_assessments` - Assessment tracking
- `training_certifications` - Certification management
- `competency_profiles` - Skill profiles
- `learning_paths` - Structured paths

**API Endpoints:**
- GET /health
- GET /metrics
- Program endpoints (8): Catalog, enroll
- Assessment endpoints (8): Take, grade, review
- Certification endpoints (6): Issue, renew, verify
- Competency endpoints (6): Profile, gap analysis
- Path endpoints (6): Define, assign, track

**Dependencies:**
- Internal: workflow_intelligence, ai-foundation
- Database: PostgreSQL (bcm_platform)
- Cache: Redis
- Vector DB: Qdrant
- AI: Anthropic API

**EventBus Integration:**
- Publishes: `learning.enrolled`, `learning.completed`, `learning.certified`
- Subscribes: `learning.*`

**Docker:** bcm-learning-service

---

### 11. Living Docs

**Purpose:** Self-Improving Documentation
**Port:** 8034
**Status:** Active
**Version:** 2.0.0

**Purpose:**
Self-improving documentation system with AI-powered content generation, personalization, and evolution based on user interactions.

**Metrics:**
- Lines of Code: 3,255
- Python Files: 9
- Classes: 24
- API Endpoints: 10
- Dependencies: 24

**Database Tables:**
- `documentation_pages` - Page content
- `documentation_interactions` - User feedback
- `documentation_gaps` - Identified gaps
- `documentation_improvements` - Auto-improvements
- `personalized_content` - User-specific versions

**API Endpoints:**
- GET / - Root documentation
- GET /gaps - Identified gaps
- GET /improvements - Auto-improvements
- GET /journey/{goal} - Personalized journey
- POST /examples/generate - AI example generation
- POST /feedback - User feedback
- GET /health
- GET /metrics

**AI Features:**
- AI Example Generator (8 methods)
- Documentation Evolution Engine (6 methods)
- Personalization Service
- Auto-improvement every 1 hour
- Min 10 interactions for analysis

**Dependencies:**
- Database: PostgreSQL (bcm_platform)
- Cache: Redis
- Vector DB: Qdrant
- AI: Anthropic API

**Docker:** bcm-living-docs

---

### 12. Simulation & Digital Twin

**Purpose:** Scenario Testing & Digital Twin
**Ports:** 8031 (main), 8082 (BIA engine), 8085 (orchestrator), 8000 (digital-twin)
**Status:** Active
**Version:** 2.0.0

**Purpose:**
Comprehensive simulation capabilities including scenario testing, digital twin modeling, BIA simulation engine, TheHive integration, and Monte Carlo analysis.

**Metrics:**
- Lines of Code: 44,465
- Python Files: 160
- Classes: 382
- Functions: 81
- API Endpoints: 233
- Dependencies: 138

**Sub-Components:**
1. **Simulation Main** (8031) - Core simulation engine
2. **BIA Engine** (8082) - BIA-specific simulations
3. **Scenario Orchestrator** (8085) - Scenario management
4. **Digital Twin** (8000) - Organization digital twin
5. **TheHive Adapter** (8007) - TheHive integration

**Database Tables:**
- `simulations` - Simulation definitions
- `simulation_scenarios` - Scenario library
- `simulation_results` - Execution results
- `digital_twin_organizations` - Org models
- `digital_twin_exercises` - Exercise tracking
- `thehive_cases` - Incident cases
- `monte_carlo_runs` - Statistical analysis

**Key Classes:**
- BCMIncidentUnified (47 methods)
- TheHiveClient (14 methods)
- ToCEngine (13 methods) - Theory of Constraints
- MonteCarloEngine (4 methods)

**Dependencies:**
- Database: PostgreSQL (bcm_platform)
- Cache: Redis
- EventBus integration

**Docker:** Multiple containers for sub-components

---

### 13. BCM Coordination Service

**Purpose:** Analyzer Coordinator
**Port:** 8070
**Status:** Active

**Purpose:**
Coordinates analyzers across the platform, integrating with intelligent-core for orchestration.

**API Endpoints:**
- GET /health
- Coordination endpoints

**Dependencies:**
- Mounts: /intelligent-core (full access, read-only)
- Database: PostgreSQL
- Cache: Redis

**Docker:** bcm-coordination-service

---

### 14. Community Service

**Purpose:** Portal & Marketplace
**Ports:** 8031-8033
**Status:** Active
**Version:** 2.0.0

**Sub-Services:**
- **Portal** (8033) - Community portal
- **Marketplace** (8032) - Service marketplace
- **Community Intelligence** - Knowledge sharing

**Metrics:**
- Lines of Code: 18,334
- Python Files: 70
- Classes: 170
- API Endpoints: 107
- Dependencies: 84

**Features:**
- Forums and knowledge bases
- Peer review capabilities
- Best practice exchange
- Collective intelligence

**Database Tables:**
- `community_members`
- `community_posts`
- `community_knowledge`
- `community_reviews`

**Dependencies:**
- Database: PostgreSQL (bcm_platform)
- Cache: Redis
- Message Queue: RabbitMQ

**EventBus Integration:**
- Publishes: `community.*`
- Subscribes: `community.*`

---

### 15. Compliance Monitoring

**Purpose:** Compliance Analytics
**Port:** 8045
**Status:** Active

**Purpose:**
Real-time compliance monitoring and analytics.

**Features:**
- Compliance dashboards
- Real-time alerts
- Trend analysis

**Docker:** Located in мониторинг/compliance-monitoring

---

### 16. Process Analytics

**Purpose:** Process Mining
**Port:** 8780
**Status:** Active

**Purpose:**
Process mining and analytics for BCM workflows.

**Features:**
- Process discovery
- Conformance checking
- Performance analysis

**Docker:** Located in мониторинг/process-analytics

---

## Integration Map

### Service Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                     Infrastructure Layer                      │
│  PostgreSQL (5432) │ Redis (6379) │ RabbitMQ (5672)          │
│  Qdrant (Vector DB) │ Prometheus (9090) │ Grafana (3000)     │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Shared Infrastructure                      │
│  EventBus │ Workflow Intelligence │ AI Foundation            │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                             │
┌───────────────────┐                     ┌──────────────────┐
│  Core BCM Layer   │                     │ Intelligence     │
│  (8011-8024)      │◄────────────────────│  Layer           │
│                   │                     │  (8021, 8034)    │
│ • BIA (8012)      │                     │                  │
│ • Risk (8040)     │                     │ • Learning (8021)│
│ • Compliance      │                     │ • Living Docs    │
│ • Governance      │                     │   (8034)         │
│ • Documents       │                     │ • Simulation     │
│ • Validation      │                     │   (8031+)        │
│ • Planning (8011) │                     │                  │
│ • Plans (8023)    │                     │                  │
│ • Response (8041) │                     │                  │
└───────────────────┘                     └──────────────────┘
        │                                             │
        └─────────────────────┬─────────────────────┘
                              │
                              ▼
                ┌──────────────────────────┐
                │   Coordination Layer     │
                │   BCM Coordination (8070)│
                └──────────────────────────┘
```

### Data Flow

1. **User Request** → API Gateway → Service
2. **Service** → Database (PostgreSQL)
3. **Service** → Cache (Redis) for performance
4. **Service** → EventBus → Other Services
5. **Service** → Workflow Intelligence → AI Foundation
6. **Service** → Metrics → Prometheus → Grafana

### Event Flow

```
BIA Service → bia.created → [EventBus] → Risk Service (auto-create risk)
Risk Service → risk.critical → [EventBus] → Response Service (auto-escalate)
Response Service → incident.created → [EventBus] → Learning Service (training needs)
Plans Service → plan.activated → [EventBus] → Validation Service (track KPIs)
```

---

## Port Allocation

### Active Services (8000-8099)
- **8011** - Planning Service
- **8012** - BIA Service
- **8013** - Governance Service
- **8014** - Compliance Service
- **8021** - Learning Service
- **8022** - Validation Service
- **8023** - Plans Service
- **8024** - Documents Service
- **8031** - Simulation Main
- **8032** - Community Marketplace
- **8033** - Community Portal
- **8034** - Living Docs
- **8040** - Risk Service
- **8041** - Response Service
- **8045** - Compliance Monitoring
- **8070** - BCM Coordination Service
- **8082** - BIA Engine (Simulation)
- **8085** - Scenario Orchestrator
- **8780** - Process Analytics

### Infrastructure Ports
- **5432** - PostgreSQL
- **6379** - Redis
- **5672** - RabbitMQ
- **9090** - Prometheus
- **3000** - Grafana

### Port Conflicts Resolved
- Governance: Changed from 8020 to 8013 (conflict with workflow-intelligence)
- Community Portal: Changed from 8031 to 8033 (conflict with simulation)

---

## Database Schema Map

### Schema Organization

**Database:** `bcm_platform`

**Schemas by Service:**

1. **bia** - BIA Service
   - bia_processes
   - bia_assessments
   - bia_resources
   - bia_dependencies

2. **risk** - Risk Service
   - risks
   - risk_assessments
   - risk_treatments
   - risk_controls
   - risk_monitoring

3. **compliance** - Compliance Service
   - audits
   - audit_evidence
   - audit_findings
   - nonconformities
   - corrective_actions
   - improvements

4. **governance** - Governance Service
   - governance_policies
   - governance_stakeholders
   - governance_responsibilities
   - governance_context
   - governance_decisions

5. **documents** - Documents Service
   - documents
   - document_versions
   - document_approvals
   - document_access
   - document_templates

6. **validation** - Validation Service
   - validation_kpis
   - validation_metrics
   - validation_alerts
   - validation_thresholds

7. **planning** - Planning Service
   - strategies
   - strategy_resources
   - cost_benefit_analyses

8. **plans** - Plans Service
   - plans
   - procedures
   - plan_resources
   - plan_exercises
   - plan_versions

9. **response** - Response Service
   - incidents
   - incident_timeline
   - incident_teams
   - incident_escalations
   - incident_communications
   - lessons_learned

10. **learning** - Learning Service
    - training_programs
    - training_enrollments
    - training_assessments
    - training_certifications
    - competency_profiles

11. **living_docs** - Living Docs
    - documentation_pages
    - documentation_interactions
    - documentation_gaps
    - documentation_improvements

12. **simulation** - Simulation
    - simulations
    - simulation_scenarios
    - simulation_results
    - digital_twin_organizations

13. **community** - Community Service
    - community_members
    - community_posts
    - community_knowledge

**Shared Tables:**
- `audit_logs` - Audit trail for all operations
- `change_history` - Field-level change tracking

**Total Tables:** 80+ tables across 13+ schemas

---

## Recommendations

### Immediate Actions
1. ✅ All services have defined ports - No conflicts
2. ✅ All services integrated with Workflow Intelligence
3. ✅ All services have health checks
4. ✅ All services have EventBus integration

### Improvements Needed
1. **Missing bcm-coordination-service README** - Create comprehensive README
2. **Community Service** - Split portal/marketplace into clearer structure
3. **Simulation Service** - Consolidate multiple entry points
4. **Test Coverage** - Increase coverage for newer services
5. **API Documentation** - Ensure all endpoints documented in OpenAPI

### Architecture Enhancements
1. **API Gateway Integration** - Centralized routing for all services
2. **Service Mesh** - Consider Istio/Linkerd for service-to-service communication
3. **Distributed Tracing** - Add Jaeger/Zipkin for request tracing
4. **Circuit Breakers** - Implement resilience patterns
5. **Rate Limiting** - Centralized rate limiting via API Gateway

### Security Enhancements
1. **mTLS** - Mutual TLS for service-to-service communication
2. **Secret Management** - Vault integration for secrets
3. **JWT Validation** - Centralized JWT validation
4. **RBAC** - Role-based access control across all services

### Performance Optimizations
1. **Connection Pooling** - Optimize database connection pools
2. **Caching Strategy** - Redis caching strategy per service
3. **Async Operations** - Maximize use of async/await
4. **Query Optimization** - Review N+1 queries, add indexes

### Monitoring Enhancements
1. **Distributed Logging** - ELK/EFK stack integration
2. **APM** - Application Performance Monitoring (DataDog/New Relic)
3. **Custom Dashboards** - Service-specific Grafana dashboards
4. **Alerting Rules** - Prometheus alerting for critical metrics

---

## Quick Reference

### Start All Services
```bash
cd /Users/MD/AI-Platform-ISO/platform-services
./start_all_services.sh
```

### Check Service Status
```bash
./status.sh
```

### View Logs
```bash
./logs.sh [service-name]
```

### Health Check All Services
```bash
for port in 8011 8012 8013 8014 8021 8022 8023 8024 8031 8034 8040 8041 8070; do
  echo "Port $port: $(curl -s http://localhost:$port/health | jq -r '.status')"
done
```

### Access API Documentation
- Planning: http://localhost:8011/docs
- BIA: http://localhost:8012/docs
- Governance: http://localhost:8013/docs
- Compliance: http://localhost:8014/docs
- Learning: http://localhost:8021/docs
- Validation: http://localhost:8022/docs
- Plans: http://localhost:8023/docs
- Documents: http://localhost:8024/docs
- Risk: http://localhost:8040/docs
- Response: http://localhost:8041/docs

---

**Document Version:** 1.0.0
**Last Updated:** 2025-10-08
**Maintained By:** AI Platform Team
**Related Documents:**
- [Architecture Overview](./ARCHITECTURE.md)
- [Quick Reference](./QUICK_REFERENCE.md)
- [API Reference](./API_REFERENCE.md)
- [Database Schema Map](./DATABASE_SCHEMA_MAP.md)
- [Port Allocation](./PORT_ALLOCATION.md)
