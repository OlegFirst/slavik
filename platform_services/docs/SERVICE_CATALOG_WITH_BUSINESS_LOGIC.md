# SERVICE CATALOG - Complete Business Logic & Functions
## Полный каталог сервисов с бизнес-логикой и функциями

**Дата**: 2025-10-10
**Версия**: 2.0 (Enhanced with Business Logic)
**Статус**: ✅ Ready for Production

**Business Scenarios Reference**: [business-scenarios/ALL_USAGE_SCENARIOS_CATALOG.md](./business-scenarios/ALL_USAGE_SCENARIOS_CATALOG.md)

---

## 📚 TABLE OF CONTENTS

1. [ISO 22301 Services (10)](#iso-22301-services)
2. [Platform Services (5)](#platform-services)
3. [Business Logic Overview](#business-logic-overview)
4. [Integration Patterns](#integration-patterns)

---

## ISO 22301 SERVICES

### 1. BIA Service (Port 8012)

#### Business Purpose
**ISO 22301 Clause 8.2.2** - Business Impact Analysis
Определяет критичные бизнес-процессы, RTO/RPO requirements, зависимости и приоритеты recovery.

#### Core Business Logic

**1. BIA Planning & Execution**
```
Input: Organization structure, business processes
Process:
  1. Create BIA project (scope, timeline, team)
  2. AI-assisted interview questionnaire generation
  3. Stakeholder identification & notification
  4. Schedule coordination across departments
  5. Real-time interview support (AI suggestions)
Output: Structured BIA plan with assigned responsibilities
Events: bia.project.created, bia.interviews.scheduled
```

**2. Impact Assessment**
```
Input: Interview responses, process data
Process:
  1. Financial impact analysis (revenue loss per hour)
  2. Operational impact (customers affected, SLA breaches)
  3. Regulatory impact (compliance violations, fines)
  4. Reputational impact (brand damage, customer churn)
  5. ML-powered RTO/RPO recommendations
Output: Impact matrix, criticality scores, recovery priorities
Events: bia.impact.analyzed, bia.critical_process.identified
```

**3. Dependency Mapping**
```
Input: Process relationships, infrastructure data
Process:
  1. Build dependency graph (processes → systems → suppliers)
  2. Identify single points of failure (SPOFs)
  3. Calculate cascading failure impact
  4. Generate resilience recommendations
Output: Visual dependency map, SPOF alerts, mitigation suggestions
Events: bia.dependencies.mapped, bia.spof.detected
```

**4. AI-Powered Features**
- **Auto-RTO Calculation**: ML model trained on industry benchmarks
- **Interview Generation**: Claude generates contextual questions
- **Real-time Suggestions**: During interviews, AI suggests probing questions
- **Gap Detection**: Identifies missing dependencies automatically

#### Key Functions (16 API Endpoints)

| Function | Endpoint | Business Logic |
|----------|----------|----------------|
| Create BIA | `POST /bia/projects` | Validates scope, creates project, schedules kickoff |
| Schedule Interviews | `POST /bia/projects/{id}/interviews` | AI generates questions, books calendar slots |
| Conduct Interview | `POST /bia/interviews/{id}/responses` | Real-time AI support, auto-saves, validates completeness |
| Analyze Impact | `POST /bia/processes/{id}/analyze` | Runs ML models, calculates financial/operational impact |
| Map Dependencies | `GET /bia/processes/{id}/dependencies` | Builds graph, detects SPOFs, suggests resilience |
| Generate Report | `POST /bia/projects/{id}/report` | AI-generated executive summary + detailed findings |

#### Integration Points
- **→ Risk Service**: BIA results feed into risk assessment
- **→ Planning Service**: Critical processes inform BC strategy
- **→ Compliance Service**: Evidence for ISO 22301 Clause 8.2.2
- **→ AI Foundation**: RAG for templates, LLM for generation

#### Business Scenarios (25 total)
See: [BIA Service - 25 scenarios](./business-scenarios/ALL_USAGE_SCENARIOS_CATALOG.md#1-bia-service---25-сценариев-использования)

**Core**: Start BIA, AI-assisted planning, Interview generation, Impact analysis
**Advanced**: Multi-site coordination, Data import, Dependency mapping
**Industry**: Healthcare (WHO guidelines), Finance (NIST), Manufacturing

---

### 2. Risk Service (Port 8040)

#### Business Purpose
**ISO 22301 Clause 8.2.3** - Risk Assessment
Identifies threats to business continuity, assesses likelihood/impact, plans treatment strategies.

#### Core Business Logic

**1. Risk Identification**
```
Input: BIA results, threat catalogs, historical incidents
Process:
  1. Auto-suggest risks based on industry (healthcare: pandemic, IT: ransomware)
  2. AI analyzes past incidents for recurring patterns
  3. Collective intelligence: learn from similar organizations
  4. Stakeholder workshops for emerging risks
Output: Comprehensive risk register
Events: risk.identified, risk.catalog.updated
```

**2. Risk Analysis (FAIR Framework)**
```
Input: Risk description, BIA data
Process:
  1. Loss Event Frequency (LEF) calculation
  2. Loss Magnitude estimation (Primary + Secondary losses)
  3. Monte Carlo simulation (10,000 iterations)
  4. Risk exposure distribution (P10, P50, P90)
  5. ML model predicts likelihood based on historical data
Output: Risk score (1-25), financial exposure range, likelihood %
Events: risk.analyzed, risk.high_severity.detected
```

**3. Risk Treatment Planning**
```
Input: Analyzed risk, organization risk appetite
Process:
  1. Evaluate 4Ts: Treat, Tolerate, Transfer, Terminate
  2. Cost-benefit analysis for each treatment option
  3. AI recommends optimal strategy based on risk appetite
  4. Generate treatment plan with actions, owners, timeline
Output: Treatment plan, action items, budget estimate
Events: risk.treatment.planned, risk.treatment.approved
```

**4. Continuous Risk Monitoring (KRIs)**
```
Input: Risk indicators (e.g., failed logins, server downtime)
Process:
  1. Real-time KRI tracking (green/yellow/red thresholds)
  2. Predictive ML: "This KRI will breach in 3 days"
  3. Auto-escalation when threshold exceeded
  4. Integration with monitoring systems
Output: KRI dashboard, predictive alerts, auto-escalation
Events: risk.kri.threshold_exceeded, risk.kri.predictive_breach
```

#### Key Functions (18 API Endpoints)

| Function | Endpoint | Business Logic |
|----------|----------|----------------|
| Create Risk | `POST /risk/risks` | AI suggests description, auto-links to BIA processes |
| FAIR Analysis | `POST /risk/risks/{id}/fair-analysis` | Runs Monte Carlo, calculates exposure distribution |
| 5x5 Matrix | `POST /risk/risks/{id}/matrix` | Maps to likelihood × impact grid, color codes |
| Treatment Plan | `POST /risk/risks/{id}/treatment` | Evaluates 4Ts, recommends strategy, estimates cost |
| KRI Monitoring | `POST /risk/kris` | Sets thresholds, connects to metrics, enables alerts |
| Scenario Analysis | `POST /risk/scenarios` | "What if pandemic + cyber attack?" cascading impact |

#### Integration Points
- **← BIA Service**: Critical processes inform risk context
- **→ Planning Service**: High risks trigger BC plan development
- **→ Compliance Service**: Risk register = ISO 22301 evidence
- **→ AI Foundation**: ML models for likelihood prediction

#### Business Scenarios (22 total)
See: [Risk Service - 22 scenarios](./business-scenarios/ALL_USAGE_SCENARIOS_CATALOG.md#2-risk-service---22-сценария-использования)

**Core**: Risk assessment, ML predictions, Impact analysis, Treatment planning
**Advanced**: Third-party risk, Cyber risk, Risk appetite, Scenario analysis
**Continuous**: KRI monitoring, Dynamic risk assessment

---

### 3. Governance Service (Port 8013)

#### Business Purpose
**ISO 22301 Clauses 5, 6, 7** - BCM Governance
Leadership commitment, objectives, resources, documentation, communication.

#### Core Business Logic

**1. BCM Policy Management**
```
Input: Organization structure, regulatory requirements
Process:
  1. Generate BCM policy from template (customized to industry)
  2. Define scope & objectives (aligned with business strategy)
  3. Approval workflow: Draft → Review → Board Approval
  4. Version control & change tracking
  5. Annual review scheduling
Output: Approved BCM policy, signed by top management
Events: policy.created, policy.approved, policy.review_due
```

**2. Roles & Responsibilities (RACI)**
```
Input: BCM activities, organization chart
Process:
  1. Define roles: BCM Manager, Crisis Team, Recovery Teams
  2. Assign responsibilities (RACI matrix generation)
  3. Competency tracking (required skills vs actual)
  4. Training needs analysis
Output: RACI matrix, competency gaps, training plan
Events: roles.assigned, competency.gap_identified
```

**3. Organizational Context (Clause 4)**
```
Input: External factors (regulations, threats), Internal (capabilities, culture)
Process:
  1. PESTLE analysis (Political, Economic, Social, Tech, Legal, Environment)
  2. Stakeholder analysis (interests, power, influence)
  3. Regulatory requirements mapping (HIPAA, GDPR, SOX)
  4. AI-powered gap analysis
Output: Context documentation, stakeholder register, compliance matrix
Events: context.analyzed, stakeholder.identified, regulation.mapped
```

**4. BCM Objectives & Metrics (Clause 6.2)**
```
Input: Business strategy, risk appetite
Process:
  1. Define SMART objectives (aligned with corporate goals)
  2. Cascade objectives to departments
  3. Define KPIs (RTO achievement %, exercise completion, audit findings)
  4. Dashboard for executive oversight
Output: BCM objectives, KPI dashboard, quarterly scorecard
Events: objectives.set, kpi.tracked, objective.at_risk
```

#### Key Functions (12 API Endpoints)

| Function | Endpoint | Business Logic |
|----------|----------|----------------|
| Create Policy | `POST /governance/policies` | Template generation, approval workflow |
| Assign Roles | `POST /governance/roles` | RACI generation, competency tracking |
| Analyze Context | `POST /governance/context` | PESTLE, stakeholder analysis, AI gaps |
| Set Objectives | `POST /governance/objectives` | SMART validation, KPI definition |
| Track Competency | `GET /governance/competency` | Skills matrix, training needs analysis |

#### Integration Points
- **→ All Services**: Provides governance framework
- **→ Compliance Service**: Policy = ISO evidence
- **→ Learning Service**: Training needs → training plans
- **→ Validation Service**: KPIs tracked here

#### Business Scenarios (11 total)
See: [Governance Service](./business-scenarios/ALL_USAGE_SCENARIOS_CATALOG.md#8-12-remaining-platform-services-summary)

---

### 4. Compliance Service (Port 8014)

#### Business Purpose
**ISO 22301 Clauses 9.1, 9.2, 9.3** - Performance Evaluation
Monitoring, internal audit, management review.

#### Core Business Logic

**1. Real-Time Compliance Monitoring**
```
Input: All BCM activities, ISO 22301 requirements
Process:
  1. Map 10 ISO clauses to platform activities
  2. Real-time tracking: "BIA completed? ✅  Risk assessment? ✅"
  3. Gap detection: "Clause 8.4 missing: BC plans not tested"
  4. Auto-alerts when compliance drops below threshold
Output: Compliance dashboard (% complete per clause), gap list
Events: compliance.gap_detected, compliance.threshold_breached
```

**2. Evidence Collection**
```
Input: Documents, records, activity logs
Process:
  1. Auto-link evidence to ISO clauses (BIA report → 8.2.2)
  2. Completeness check (all required docs present?)
  3. Version control (latest policy approved?)
  4. Evidence repository with search
Output: Evidence library mapped to ISO clauses
Events: evidence.collected, evidence.gap_identified
```

**3. Internal Audit (Clause 9.2)**
```
Input: Audit schedule, ISO 22301 checklist
Process:
  1. Generate audit plan (scope, criteria, schedule)
  2. AI-powered audit checklist customization
  3. Audit execution tracking (findings, observations)
  4. Nonconformity management (major/minor)
  5. Corrective Action Plans (CAPA)
Output: Audit report, nonconformity register, CAPA tracking
Events: audit.scheduled, audit.finding_raised, capa.assigned
```

**4. Management Review (Clause 9.3)**
```
Input: Compliance status, audit findings, KPIs
Process:
  1. Quarterly management review agenda generation
  2. Executive dashboard (compliance %, KPIs, audit status)
  3. AI-generated executive summary
  4. Action items tracking from previous reviews
Output: Management review report, decisions, action items
Events: review.scheduled, review.completed, action.assigned
```

#### Key Functions (15 API Endpoints)

| Function | Endpoint | Business Logic |
|----------|----------|----------------|
| Monitor Compliance | `GET /compliance/status` | Real-time dashboard, gap detection |
| Collect Evidence | `POST /compliance/evidence` | Auto-mapping to ISO clauses |
| Schedule Audit | `POST /compliance/audits` | AI checklist generation, calendar integration |
| Raise Finding | `POST /compliance/findings` | Severity assessment, CAPA workflow |
| Management Review | `POST /compliance/reviews` | AI summary generation, action tracking |

#### Integration Points
- **← All Services**: Collects evidence from all activities
- **→ Documents Service**: Evidence storage
- **→ Notification Service**: Audit reminders, gap alerts
- **→ Validation Service**: KPIs for management review

#### Business Scenarios (20 total)
See: [Compliance Service - 20 scenarios](./business-scenarios/ALL_USAGE_SCENARIOS_CATALOG.md#4-compliance-service---20-сценариев-использования)

---

### 5. Plans Service (Port 8023)

#### Business Purpose
**ISO 22301 Clause 8.4** - BC Plans and Procedures
Documented recovery procedures, contact lists, resource requirements.

#### Core Business Logic

**1. BC Plan Development**
```
Input: BIA results (critical processes), Risk assessment
Process:
  1. Template selection (IT Recovery, Pandemic, Natural Disaster)
  2. AI-generated plan structure based on BIA
  3. Procedure generation (step-by-step recovery actions)
  4. Resource requirements (personnel, facilities, tech)
  5. Contact lists (emergency contacts, vendors)
  6. Approval workflow: Draft → Review → Approved → Active
Output: Comprehensive BC plan, ready for activation
Events: plan.created, plan.approved, plan.activated
```

**2. Procedure Dependency Management**
```
Input: Recovery procedures
Process:
  1. Define procedure execution order (prerequisites)
  2. Dependency graph visualization
  3. Circular dependency detection
  4. Critical path analysis (longest chain)
Output: Procedure sequence, dependency map, critical path
Events: procedure.added, dependency.circular_detected
```

**3. Plan Activation (Real Incident)**
```
Input: Incident declaration, selected plan
Process:
  1. Activate plan → notify recovery teams
  2. Track procedure execution in real-time
  3. RTO countdown timer
  4. Resource allocation tracking
  5. Communication log
Output: Active incident dashboard, procedure checklist, RTO status
Events: plan.activated, procedure.completed, rto.exceeded
```

**4. Plan Testing & Maintenance**
```
Input: BC plan, test schedule
Process:
  1. Schedule table-top exercise
  2. Digital twin simulation
  3. Track test results, gaps identified
  4. Update plan based on lessons learned
  5. Annual review trigger
Output: Test report, plan updates, next test schedule
Events: plan.tested, plan.updated, plan.review_due
```

#### Key Functions (25+ API Endpoints)

| Function | Endpoint | Business Logic |
|----------|----------|----------------|
| Create Plan | `POST /plans/plans` | Template selection, AI structure generation |
| Add Procedure | `POST /plans/plans/{id}/procedures` | Dependency tracking, critical path |
| Activate Plan | `POST /plans/plans/{id}/activate-real` | Team notification, RTO timer, tracking |
| Test Plan | `POST /plans/plans/{id}/test` | Exercise execution, gap analysis |
| Update Plan | `PUT /plans/plans/{id}` | Version control, approval re-trigger |

#### Integration Points
- **← BIA Service**: Critical processes → plans
- **← Risk Service**: High risks → specific plans
- **→ Exercise Service**: Plan testing
- **→ Response Service**: Plan activation during incidents
- **→ Workflow Intelligence**: Tracks plan development journey

#### Business Scenarios (included in Planning Service - 28 total)
See: [Planning Service](./business-scenarios/ALL_USAGE_SCENARIOS_CATALOG.md#3-planning-service---28-сценариев-использования)

---

### 6-10. Additional ISO Services (Summary)

#### 6. Validation Service (Port 8022)
**ISO 22301 Clause 10** - Improvement
- Exercise planning & execution
- KPI tracking (RTO achievement, test frequency)
- Nonconformity management (CAPA)
- Continual improvement cycles

**Key Logic**: Schedule exercises → Execute → Collect results → Identify gaps → Create CAPAs → Track closure

#### 7. Response Service (Port 8041)
**ISO 22301 Clause 8.4.2** - Incident Response
- Incident detection & classification
- BC plan activation
- RTO/RPO tracking
- Crisis management team coordination
- Post-incident review (PIR)

**Key Logic**: Detect incident → Classify severity → Activate plan → Track RTO → Resolve → PIR → Lessons learned

#### 8. Learning Service (Port 8021)
**ISO 22301 Clause 7.2** - Competence
- Training program management
- BCM awareness campaigns
- Competency tracking
- E-learning modules
- Certification tracking

**Key Logic**: Identify training needs → Create programs → Schedule sessions → Track attendance → Assess competency → Certificate

#### 9. Planning Service (Port 8011)
**ISO 22301 Clause 6** - Planning
- BCM strategy development
- Journey management (ISO certification path)
- Predictive analytics (will we finish on time?)
- Budget planning
- Roadmap visualization

**Key Logic**: Set objectives → Create journey → AI predicts timeline → Detect stuck workflows → Recommend interventions

#### 10. Documents Service (Port 8024)
**ISO 22301 Clause 7.5** - Documented Information
- Document management
- Version control
- Living documents (auto-update)
- Approval workflows
- Search & retrieval

**Key Logic**: Create doc → Approval workflow → Version control → Link to ISO clause → Auto-update from data sources

---

## PLATFORM SERVICES

### 11. Community Portal (Port 8033)

#### Business Purpose
Marketplace for BCM specialists, templates, services. Community collaboration.

#### Core Business Logic

**1. Specialist Marketplace**
```
Input: Organization BCM needs
Process:
  1. Post service request (e.g., "Need BIA consultant")
  2. AI matches specialists (skills, availability, reviews)
  3. Proposal submission & evaluation
  4. Contract & payment escrow
  5. Service delivery tracking
  6. Review & rating
Output: Engaged specialist, completed work, feedback
Events: request.posted, specialist.matched, contract.signed
```

**2. Template Library**
```
Input: User search (e.g., "pandemic BC plan template")
Process:
  1. Search templates (filterable by industry, ISO clause)
  2. Preview & rating review
  3. Purchase/download
  4. Customization with AI assistance
  5. Share back to community (optional, anonymized)
Output: Customized template ready for use
Events: template.downloaded, template.customized, template.shared
```

**3. Peer Review & Synthesis**
```
Input: User-created content (plans, policies)
Process:
  1. Submit for peer review
  2. Anonymous specialist review (3 reviewers)
  3. Consolidate feedback with AI synthesis
  4. Reputation points for reviewers
Output: Improved document, reviewer credits
Events: review.requested, review.completed, synthesis.generated
```

#### Key Functions (20+ API Endpoints)
- Service requests, specialist matching
- Template search & download
- Peer review workflows
- Reputation & rating systems

#### Integration Points
- **→ All Services**: Templates integrated into workflows
- **→ Collective Intelligence**: Community patterns shared (k-anonymous)

---

### 12. Community Marketplace (Port 8032)

#### Business Purpose
Monetization of templates, services, collective intelligence.

#### Core Business Logic
- Pricing & payments
- Revenue sharing (70% specialist, 30% platform)
- Subscription management
- Analytics for sellers

---

### 13. Living Docs (Port 8034)

#### Business Purpose
Self-updating documentation that stays current automatically.

#### Core Business Logic

**Auto-Update Example**:
```
Document: "BCM Roles & Responsibilities"
Data Source: governance-service /roles endpoint
Update Trigger: Role assignment change
Process:
  1. Detect change via webhook
  2. Regenerate affected section
  3. Version control (track what changed)
  4. Notify stakeholders
Output: Always-current document
```

---

### 14. Compliance Monitoring (Port 8779)

**Path**: `/business-monitoring/compliance-monitoring/`

#### Business Purpose
**Business-level ISO 22301 compliance tracking** (NOT infrastructure monitoring).

#### Core Business Logic

**1. ISO 22301 Clause Coverage**
```
Input: All BCM services activity
Process:
  1. Map services to ISO clauses:
     - BIA Service → Clause 8.2.2
     - Risk Service → Clause 8.2.3
     - etc.
  2. Track compliance status per clause (compliant/partial/non-compliant)
  3. Calculate overall compliance score
  4. Real-time alerts for gaps
Output: Compliance dashboard, gap alerts, audit readiness %
Events: compliance.gap_detected, compliance.score_updated
```

**2. Nonconformity Management (Clause 10.1)**
```
Input: Audit findings, exercise gaps
Process:
  1. Create nonconformity record (major/minor)
  2. Root cause analysis workflow
  3. Corrective action assignment
  4. Preventive action planning
  5. Effectiveness verification
Output: NC register, CAPA tracker, closure evidence
Events: nc.created, capa.assigned, nc.closed
```

**3. Audit Requirements Tracking (Clause 9.2)**
```
Input: ISO 22301 requirements
Process:
  1. Break down each clause into specific requirements
  2. Map to evidence (documents, records, activities)
  3. Track evidence completeness
  4. Schedule next audit
Output: Requirements checklist, evidence map, audit schedule
Events: requirement.evidence_added, audit.scheduled
```

#### Key Functions (33 API Endpoints)
- Compliance status by clause
- Nonconformity CRUD
- Audit requirement tracking
- Real-time WebSocket alerts

#### Integration Points
- **← All ISO Services**: Monitors their compliance
- **→ MIO Manager**: Infrastructure health feeds into compliance
- **→ Prometheus/Grafana**: Metrics visualization

**NOTE**: This is **business compliance**, NOT infrastructure monitoring.

---

### 15. Process Analytics (Port 8780)

**Path**: `/business-monitoring/process-analytics/`

#### Business Purpose
Optimize BCM workflows through process mining and analytics.

#### Core Business Logic

**1. Process Mining**
```
Input: Event logs from all services (bia.started, bia.interview.completed, etc.)
Process:
  1. Reconstruct actual workflow execution paths
  2. Discover common patterns ("90% of BIAs follow this path")
  3. Identify deviations ("This BIA skipped dependency mapping")
  4. Detect bottlenecks ("Approval step averages 6 days")
Output: Process map, pattern library, deviation alerts
Events: pattern.discovered, deviation.detected, bottleneck.identified
```

**2. Performance Analysis**
```
Input: Workflow metrics (duration, resource usage)
Process:
  1. Calculate avg completion time per workflow type
  2. Identify bottlenecks (longest steps)
  3. Resource utilization (who's overloaded?)
  4. Predictive: "This workflow will take 14 days"
Output: Performance dashboard, bottleneck report, predictions
Events: bottleneck.detected, performance.degraded
```

**3. Optimization Suggestions**
```
Input: Inefficient workflows
Process:
  1. AI analyzes patterns from successful workflows
  2. Suggests optimizations ("Automate RTO calculation → save 2 days")
  3. Simulates improvement impact
  4. Generates optimization plan
Output: Optimization recommendations, ROI estimates
Events: optimization.suggested, optimization.implemented
```

#### Key Functions (15+ API Endpoints)
- Process mining
- Bottleneck detection
- Performance metrics
- Optimization suggestions

#### Integration Points
- **← All Services**: Analyzes their workflows
- **→ Orchestrator**: Optimization suggestions
- **→ Collective Intelligence**: Pattern sharing

**NOTE**: This is **workflow analytics**, NOT infrastructure performance.

---

## BUSINESS LOGIC OVERVIEW

### Cross-Service Business Flows

#### End-to-End: ISO 22301 Certification Journey
```
PHASE 1: PREPARATION (Months 1-2)
├─ Governance: Create BCM policy, assign roles
├─ Planning: Define objectives, create journey
└─ Learning: BCM awareness training for staff

PHASE 2: RISK ASSESSMENT (Months 3-4)
├─ BIA: Conduct BIA, identify critical processes
├─ Risk: Assess threats, treatment planning
└─ Compliance: Map requirements, evidence collection

PHASE 3: PLANNING (Months 5-6)
├─ Plans: Develop BC plans, procedures
├─ Response: Define incident response structure
└─ Documents: Document all processes

PHASE 4: IMPLEMENTATION (Months 7-8)
├─ Learning: Train recovery teams
├─ Validation: Conduct table-top exercises
└─ Compliance: Internal audit

PHASE 5: TESTING & IMPROVEMENT (Months 9-12)
├─ Validation: Full-scale exercise
├─ Response: Test incident response
├─ Compliance: Management review, CAPA
└─ Planning: Certification audit preparation

PHASE 6: CERTIFICATION (Month 12+)
└─ Compliance: External audit, certification achieved
```

**Services Used**: All 10 ISO services + All platform services
**Duration**: 12-18 months
**AI Features**: Predictive timeline, stuck detection, auto-recommendations

#### Real-Time: Incident Response
```
MINUTE 0: Detection
├─ Response: Incident detected (monitoring alert)
└─ Event: incident.detected → all services notified

MINUTE 1-5: Assessment
├─ Response: Classify severity (Minor/Major/Crisis)
├─ BIA: Lookup affected critical processes
├─ Risk: Check if matches known risk scenario
└─ Event: incident.classified

MINUTE 5-10: Activation
├─ Plans: Select appropriate BC plan
├─ Response: Activate plan, notify recovery teams
├─ Notification: Multi-channel alerts (SMS, email, Teams)
└─ Event: plan.activated

MINUTE 10+: Execution
├─ Response: Track procedure execution, RTO timer
├─ Documents: Access recovery procedures (Living Docs)
├─ Monitoring: Track system recovery progress
└─ Event: procedure.completed, rto.tracked

HOUR 1+: Recovery
├─ Response: Monitor RTO achievement
├─ Notification: Status updates to stakeholders
└─ Event: service.recovered

DAY 1+: Post-Incident
├─ Response: Post-Incident Review (PIR)
├─ Compliance: Lessons learned, CAPA
├─ Plans: Update BC plan based on learnings
└─ Event: pir.completed, plan.updated
```

**Services Used**: Response, Plans, BIA, Risk, Notification, Monitoring, Documents, Compliance
**Duration**: Minutes to days
**AI Features**: Auto-classification, recovery suggestions, PIR generation

---

## INTEGRATION PATTERNS

### Event-Driven Choreography (60+ Events)

**Pattern**: Services react to events independently

```
Event: bia.analysis.completed
Listeners:
  ├─ Risk Service: Trigger risk assessment
  ├─ Planning Service: Update BCM strategy
  ├─ Compliance Service: Mark evidence collected
  └─ Process Analytics: Log workflow progress
```

### Orchestrated Workflows (via AI Orchestrator)

**Pattern**: Orchestrator coordinates multi-service journeys

```
Journey: "Complete BIA"
Orchestrator:
  1. Call BIA Service: Create project
  2. Call AI Foundation: Generate interview questions
  3. Call Notification: Schedule interviews
  4. [Wait for completion]
  5. Call BIA Service: Analyze results
  6. Call Risk Service: Trigger risk assessment
  7. Call Planning Service: Update strategy
```

### Shared Data Access (via Database)

**Pattern**: Services share common data models

```
Shared Schema: bcm.shared_resources
Tables:
  ├─ organizations (tenant isolation)
  ├─ users (authentication)
  ├─ teams (role assignments)
  └─ templates (reusable across services)

Each service: Own schema + bcm schema access
```

---

## 📊 STATISTICS

- **Total Services**: 15
- **Total API Endpoints**: 200+
- **Total Business Scenarios**: 570+
- **Total Events**: 60+
- **Database Schemas**: 13
- **Database Tables**: 172

---

## 🔗 RELATED DOCUMENTATION

- **[Business Scenarios](./business-scenarios/ALL_USAGE_SCENARIOS_CATALOG.md)** - 570+ detailed scenarios
- **[API Documentation](./api/)** - Swagger/OpenAPI specs
- **[Deployment Guide](./deployment/)** - Infrastructure setup
- **[Integration Guide](../doc-project/)** - Cross-service patterns

---

**Created**: 2025-10-10
**Status**: ✅ Complete with Business Logic
**Next**: Service deployment and integration testing
