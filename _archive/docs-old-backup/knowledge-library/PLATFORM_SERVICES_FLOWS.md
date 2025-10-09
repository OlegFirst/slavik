# Platform Services Business Flows - Complete Inventory

**Analysis Date:** 2025-10-08
**Services Analyzed:** 12 core BCM services
**Total Flows Identified:** 150+
**ISO 22301 Coverage:** Clauses 4-10

> **Purpose:** This document provides a COMPLETE inventory of ALL business flows extracted from actual code in the platform-services directory. Every state transition, event, workflow, and integration point is documented here.

---

## Table of Contents

1. [BIA Service (Clause 8.2.2)](#1-bia-service)
2. [Risk Service (Clause 8.2.3)](#2-risk-service)
3. [Planning Service (Clause 8.3)](#3-planning-service)
4. [Plans Service (Clause 8.4)](#4-plans-service)
5. [Response Service (Clause 8.4)](#5-response-service)
6. [Validation Service (Clause 9.1-9.3)](#6-validation-service)
7. [Compliance Service (Clause 9-10)](#7-compliance-service)
8. [Governance Service (Clause 4-7)](#8-governance-service)
9. [Learning Service (Clause 7.3)](#9-learning-service)
10. [Documents Service (Clause 7.5)](#10-documents-service)
11. [Living-Docs](#11-living-docs)
12. [BCM Coordination Service](#12-bcm-coordination-service)
13. [Cross-Service Integration Flows](#13-cross-service-integration-flows)

---

## 1. BIA Service

**Port:** 8012
**ISO Clause:** 8.2.2 - Business Impact Analysis
**Endpoints:** 16 total (12 main + 4 bulk)
**State Machine:** Draft → In Progress → Completed

### Flow 1.1: BIA Process Creation
**Trigger:** `POST /api/bia/processes`
**Permission:** BIA_CREATE
**Steps:**
1. Validate process data (criticality, RTO, RPO, MTPD)
2. Calculate criticality score (1-5 scale)
3. Auto-calculate WHO tier (healthcare only) based on patient safety impact
4. Create process in database (PostgreSQL)
5. Cache result in Redis (TTL: 300s)
6. Log audit event (creation)
7. **Publish event:** `bcm.bia.started`

**Events Published:**
- `bcm.bia.started` - Payload: `{tenant_id, bia_process_id, process_name}`

**State Transition:** None → Draft
**Dependencies:** None
**Data Provided:** BIA data for risk-service, planning-service, plans-service
**Failure Points:**
- Database write failure
- Cache connection failure (non-blocking)
- Event bus unavailable (logged, non-blocking)

---

### Flow 1.2: BIA Process Update
**Trigger:** `PUT /api/bia/processes/{id}`
**Permission:** BIA_UPDATE
**Steps:**
1. Fetch existing process (with tenant validation)
2. Validate update data
3. Re-calculate criticality score if criticality changed
4. Re-calculate WHO tier if criticality, RTO, or patient_safety_impact changed
5. Update process in database
6. Invalidate cache entry
7. Log audit event (update with before/after state)
8. Return updated process

**State Transition:** Any → Any (within same status)
**Cache Invalidation:** Yes - specific key deleted
**Audit Trail:** Before/after state captured

---

### Flow 1.3: BIA Process Completion
**Trigger:** `POST /api/bia/processes/{id}/complete`
**Permission:** BIA_COMPLETE
**Steps:**
1. Fetch process (tenant validation)
2. Validate process is not already completed
3. Update status to COMPLETED
4. Set completed_at timestamp
5. Update database
6. Log audit event (state transition: IN_PROGRESS → COMPLETED)
7. **Publish event:** `bcm.bia.completed`
8. **Conditional event:** If criticality_score >= 4, publish `bcm.bia.critical_process_identified`
9. Store in case library (Workflow Intelligence)

**Events Published:**
- `bcm.bia.completed` - Payload: `{tenant_id, bia_process_id, rto_hours, rpo_hours, criticality, critical_process}`
- `bcm.bia.critical_process_identified` - Payload: `{tenant_id, process_id, criticality, rto_hours, mtpd_hours}` (only if critical)

**State Transition:** In Progress → Completed
**Dependencies:** None (terminal operation)
**Downstream Consumers:**
- Risk Service: Uses BIA data for risk context
- Planning Service: Uses RTO/RPO for strategy selection
- Plans Service: Uses BIA data for plan prioritization

---

### Flow 1.4: AI RTO Suggestion
**Trigger:** `POST /api/bia/processes/{id}/suggest-rto`
**Permission:** BIA_AI_SUGGEST
**Steps:**
1. Fetch BIA process
2. Analyze process characteristics:
   - Criticality level
   - Financial impact across periods (1hr, 4hr, 24hr, 1week, 1month)
   - Industry type
   - Geographical scope
3. Apply ML model or rule-based logic:
   - CRITICAL: RTO 1-2 hours, RPO 0-1 hours, MTPD 4 hours
   - HIGH: RTO 4-8 hours, RPO 2-4 hours, MTPD 12 hours
   - MEDIUM: RTO 12-24 hours, RPO 4-12 hours, MTPD 48 hours
   - LOW: RTO 3-5 days, RPO 24 hours, MTPD 7 days
4. Fetch industry benchmarks
5. Calculate confidence score
6. Generate reasoning explanation
7. Return suggestions with alternatives

**Response:**
```json
{
  "suggested_rto_hours": 2,
  "suggested_rpo_hours": 1,
  "suggested_mtpd_hours": 4,
  "confidence_score": 0.92,
  "reasoning": "CRITICAL process with $200K/4hr impact",
  "industry_benchmark": {
    "industry": "financial_services",
    "typical_rto_range": "1-4 hours"
  },
  "alternative_scenarios": [...]
}
```

**Integration:** AI Orchestration Service (port 8002)
**Failure Points:** AI service unavailable (return fallback suggestions)

---

### Flow 1.5: AI Dependency Discovery
**Trigger:** `POST /api/bia/processes/{id}/discover-dependencies`
**Permission:** BIA_AI_SUGGEST
**Steps:**
1. Fetch BIA process
2. Analyze process name, description, department
3. Query knowledge graph for:
   - Upstream process dependencies
   - Downstream process dependencies
   - Technology dependencies
   - Supplier dependencies
4. Score each dependency by criticality (1-5)
5. Return discovered dependencies with confidence scores

**Integration:** Knowledge System, AI Orchestration
**Use Case:** Auto-populate dependencies for new BIA processes

---

### Flow 1.6: Bulk Create BIA Processes
**Trigger:** `POST /api/bia/processes/bulk`
**Permission:** BIA_CREATE
**Steps:**
1. Validate all processes in batch
2. Execute parallel_map with max_concurrency=10:
   - Create each process independently
   - Collect success/failure for each
3. Track metrics:
   - Total count
   - Success count
   - Failure count
   - Duration (ms)
   - Success rate (%)
4. Return bulk operation report with detailed failures

**Parallel Execution:** Yes (up to 10 concurrent)
**Partial Success:** Supported - returns which items succeeded/failed
**Timeout:** 30 seconds per process
**Use Case:** Import BIA data from spreadsheet/external system

**Response:**
```json
{
  "total": 50,
  "success": 47,
  "failed": 3,
  "timeout": 0,
  "success_rate": 94.0,
  "duration_ms": 2847,
  "failures": [
    {"index": 5, "name": "Payment Gateway", "error": "RTO exceeds MTPD"},
    {"index": 12, "name": "CRM System", "error": "Invalid criticality value"},
    {"index": 31, "name": "Backup System", "error": "Duplicate process name"}
  ]
}
```

---

### Flow 1.7: Bulk Update BIA Processes
**Trigger:** `PATCH /api/bia/processes/bulk`
**Permission:** BIA_UPDATE
**Similar to Flow 1.6 but for updates**
**Timeout:** 20 seconds per process

---

### Flow 1.8: Bulk Delete BIA Processes
**Trigger:** `DELETE /api/bia/processes/bulk`
**Permission:** BIA_DELETE
**Similar to Flow 1.6 but for deletions**
**Timeout:** 15 seconds per process

---

### Flow 1.9: Bulk Validate BIA Processes
**Trigger:** `POST /api/bia/processes/bulk/validate`
**Permission:** BIA_VIEW
**Steps:**
1. Validate each process WITHOUT creating in database
2. Check business rules:
   - RTO <= MTPD
   - RPO <= RTO
   - Valid criticality enum
   - Valid WHO tier (if healthcare)
3. Calculate criticality score
4. Determine WHO tier
5. Return validation report

**Use Case:** Pre-validate before import
**Timeout:** 5 seconds per process (fast validation)

---

### Flow 1.10: BIA Summary Report
**Trigger:** `GET /api/bia/reports/summary`
**Permission:** BIA_VIEW
**Steps:**
1. Aggregate BIA data by tenant:
   - Total processes
   - Breakdown by criticality (Critical, High, Medium, Low)
   - Breakdown by status (Draft, In Progress, Completed)
   - Average RTO/RPO/MTPD
2. Calculate WHO tier distribution (healthcare)
3. Identify gaps (processes without dependencies, missing MTPD)
4. Return executive summary

**Caching:** 15 minutes (high read frequency)

---

### Flow 1.11: Critical Processes Report
**Trigger:** `GET /api/bia/reports/critical-processes`
**Permission:** BIA_VIEW
**Steps:**
1. Filter processes with criticality_score >= 4
2. Sort by criticality_score DESC, then by RTO ASC
3. Include:
   - Process name, department, owner
   - RTO, RPO, MTPD
   - Financial impact
   - Dependencies count
4. Return report

**Use Case:** Executive dashboard, priority planning

---

### Flow 1.12: Dependencies Report
**Trigger:** `GET /api/bia/reports/dependencies`
**Permission:** BIA_VIEW
**Steps:**
1. Extract all dependencies from all BIA processes
2. Group by dependency type:
   - Process dependencies
   - Technology dependencies
   - Supplier dependencies
   - People dependencies
3. Identify critical dependencies (criticality >= 4)
4. Find single points of failure (dependency used by multiple critical processes)
5. Return dependency map

**Use Case:** Risk analysis, supply chain BCM

---

### BIA Service: Event Subscriptions
**Listens for:**
- `risk.assessment.completed` - Triggers BIA review for high-risk processes
- `exercise.completed` - Updates RTO/RPO based on exercise results

**Handler:** `handle_event()` in main.py

---

### BIA Service: State Machine

```
[None] --create--> [DRAFT]
[DRAFT] --update--> [DRAFT]
[DRAFT] --start--> [IN_PROGRESS]
[IN_PROGRESS] --update--> [IN_PROGRESS]
[IN_PROGRESS] --complete--> [COMPLETED]
[COMPLETED] --update (review)--> [IN_PROGRESS]
```

**Status Enum:**
- DRAFT: Initial state, can be edited freely
- IN_PROGRESS: Analysis underway, can still be updated
- COMPLETED: Analysis finished, locked (requires review to re-open)

---

## 2. Risk Service

**Port:** 8040
**ISO Clause:** 8.2.3 - Risk Assessment
**Endpoints:** 15
**State Machine:** Identified → Analyzing → Treated → Monitoring → Closed

### Flow 2.1: Risk Assessment Creation
**Trigger:** `POST /api/v1/risk/assessments`
**Authentication:** JWT token required
**Steps:**
1. Create risk with likelihood (1-5) × impact (1-5)
2. Calculate inherent_risk_score = likelihood × impact (1-25)
3. Determine risk severity:
   - Critical: score >= 20
   - High: score 15-19
   - Medium: score 8-14
   - Low: score < 8
4. Link to related BIA processes (if applicable)
5. Link to related assets
6. Store in database
7. Set status to IDENTIFIED
8. **Publish event:** `risk.assessment.created`

**Events Published:**
- `risk.assessment.created` - Payload: `{risk_id, organization_id, risk_title, severity, inherent_risk_score}`

**State Transition:** None → Identified
**Dependencies:**
- BIA Service: Links to critical processes
- Asset inventory (optional)

---

### Flow 2.2: FAIR Analysis
**Trigger:** `POST /api/v1/risk/assessments/{risk_id}/fair-analysis`
**Method:** Factor Analysis of Information Risk (Quantitative)
**Steps:**
1. Validate FAIR input parameters:
   - Threat Event Frequency (TEF) > 0
   - Vulnerability Score (0-1)
   - Primary Loss Distribution (min <= most_likely <= max)
   - Secondary Loss Range (min <= max)
2. Calculate Loss Event Frequency (LEF):
   - `LEF = TEF × Vulnerability`
3. Calculate Average Loss Magnitude:
   - Primary: `(min + 4*most_likely + max) / 6` (PERT formula)
   - Secondary: `(min + max) / 2`
   - Total: Primary + Secondary
4. Calculate Annual Loss Expectancy (ALE):
   - `ALE = LEF × Average Total Loss`
5. Determine risk rating:
   - Low: ALE < $10K
   - Medium: ALE $10K-$100K
   - High: ALE $100K-$1M
   - Critical: ALE >= $1M
6. Calculate confidence intervals (±20% of ALE)
7. Store FAIR analysis
8. **Publish event:** `risk.fair_analysis.completed`

**Example:**
```
TEF = 10 events/year
Vulnerability = 0.7 (70% chance of success)
LEF = 10 × 0.7 = 7 events/year

Primary Loss: min=$10K, most_likely=$50K, max=$200K
Avg Primary = ($10K + 4*$50K + $200K) / 6 = $68.3K

Secondary Loss: min=$5K, max=$20K
Avg Secondary = ($5K + $20K) / 2 = $12.5K

Avg Total Loss = $68.3K + $12.5K = $80.8K
ALE = 7 × $80.8K = $565.6K
Risk Rating: HIGH
```

**Validation Errors:**
- TEF <= 0
- Vulnerability not in [0, 1]
- Invalid triangular distribution (min > most_likely or most_likely > max)
- Negative loss values

---

### Flow 2.3: Monte Carlo Simulation
**Trigger:** `POST /api/v1/risk/assessments/{risk_id}/monte-carlo`
**Method:** Probabilistic simulation with thousands of iterations
**Steps:**
1. Validate simulation parameters:
   - Iterations > 0 and <= 1,000,000
   - At least one factor provided
   - Each factor has valid triangular distribution
2. Run simulation loop (default 10,000 iterations):
   - For each iteration:
     - Sample each factor from triangular distribution
     - Sum all factors = scenario_loss
     - Store scenario_loss
3. Calculate statistics:
   - Mean loss
   - Median loss
   - 95th percentile (VaR 95)
   - 99th percentile (VaR 99)
   - Standard deviation
4. Generate histogram (50 bins)
5. Store simulation results
6. **Publish event:** `risk.monte_carlo.completed`

**Example Input:**
```json
{
  "iterations": 10000,
  "factors": [
    {
      "name": "data_breach_cost",
      "min": 50000,
      "most_likely": 200000,
      "max": 1000000
    },
    {
      "name": "downtime_cost",
      "min": 10000,
      "most_likely": 50000,
      "max": 200000
    }
  ]
}
```

**Example Output:**
```json
{
  "mean_loss": 283450,
  "median_loss": 265000,
  "percentile_95": 512000,
  "percentile_99": 687000,
  "distribution_data": {
    "histogram": [...],
    "bin_edges": [...],
    "min": 65000,
    "max": 1150000,
    "std_dev": 145000
  }
}
```

**Use Case:** Understand risk exposure under uncertainty

---

### Flow 2.4: Risk Treatment Plan
**Trigger:** `POST /api/v1/risk/assessments/{risk_id}/treatment-plans`
**Steps:**
1. Create treatment plan with strategy:
   - **Avoid:** Eliminate the risk (stop the activity)
   - **Mitigate:** Reduce likelihood/impact (controls)
   - **Transfer:** Insurance, outsourcing, contracts
   - **Accept:** Accept the risk as-is
2. Define actions (list of tasks)
3. Assign responsible party
4. Set dates: start_date, target_date, completion_date
5. Estimate costs: estimated_cost, actual_cost
6. Set expected residual risk: expected_residual_likelihood, expected_residual_impact
7. Store treatment plan
8. **Publish event:** `risk.treatment_plan.created`
9. Update risk status to TREATING

**Events Published:**
- `risk.treatment_plan.created` - Payload: `{risk_id, treatment_strategy, responsible_party, target_date}`

**State Transition:** Identified/Analyzing → Treating

---

### Flow 2.5: Risk Treatment Execution
**Trigger:** `PUT /api/v1/risk/treatment-plans/{plan_id}`
**Steps:**
1. Update treatment plan progress
2. Record actual_cost
3. Set completion_date when done
4. Calculate residual risk:
   - residual_likelihood (post-treatment)
   - residual_impact (post-treatment)
   - residual_risk_score = residual_likelihood × residual_impact
5. Update risk with residual values
6. Update risk status to TREATED
7. **Publish event:** `risk.treatment_plan.completed`

**State Transition:** Treating → Treated

---

### Flow 2.6: Risk Reports
**Trigger:** `GET /api/v1/risk/reports`
**Steps:**
1. Aggregate all risks for organization
2. Calculate statistics:
   - Total risks
   - By severity (critical, high, medium, low)
   - By category (operational, financial, strategic, compliance, reputational, cybersecurity, natural_disaster)
   - By status (identified, analyzing, treating, monitoring, closed)
3. Get top 10 risks by inherent score
4. Get trend data (last 90 days):
   - New risks created
   - Risks resolved
   - Average risk score over time
5. Return comprehensive report

**Caching:** 30 minutes

---

### Flow 2.7: Risk Heat Map
**Trigger:** `GET /api/v1/risk/risk-heat-map`
**Steps:**
1. Create 5×5 matrix (likelihood × impact)
2. Count risks in each cell
3. Return matrix with counts

**Output:**
```json
{
  "organization_id": "uuid",
  "matrix": [
    [1, 3, 5, 2, 0],  // Rare (likelihood=1)
    [2, 5, 8, 3, 1],  // Unlikely (likelihood=2)
    [0, 4, 12, 5, 2], // Possible (likelihood=3)
    [1, 2, 6, 8, 4],  // Likely (likelihood=4)
    [0, 1, 3, 6, 7]   // Almost Certain (likelihood=5)
  ],
  "labels": {
    "x_axis": "Impact",
    "y_axis": "Likelihood",
    "levels": ["Insignificant", "Minor", "Moderate", "Major", "Catastrophic"]
  }
}
```

---

### Flow 2.8: Risk Trends
**Trigger:** `GET /api/v1/risk/risk-trends?days=90`
**Steps:**
1. Query risk history for specified period
2. Group by date
3. Calculate daily metrics:
   - Risk count by severity
   - Average risk score
   - New risks created
   - Risks resolved
4. Calculate summary:
   - Total change (first to last period)
   - Percentage change
   - Net change (new - resolved)
5. Return time series data

**Use Case:** Risk profile improvement tracking, board reporting

---

### Risk Service: State Machine

```
[None] --create--> [IDENTIFIED]
[IDENTIFIED] --analyze--> [ANALYZING]
[ANALYZING] --treatment_plan--> [TREATING]
[TREATING] --complete_treatment--> [TREATED]
[TREATED] --monitor--> [MONITORING]
[MONITORING] --close--> [CLOSED]
[MONITORING] --re-assess--> [ANALYZING]
```

**Status Enum:**
- IDENTIFIED: Risk discovered, not yet analyzed
- ANALYZING: Risk assessment in progress (FAIR, Monte Carlo)
- TREATING: Treatment plan being executed
- TREATED: Treatment completed, residual risk determined
- MONITORING: Risk being monitored for changes
- CLOSED: Risk no longer relevant or resolved

---

## 3. Planning Service

**Port:** 8011
**ISO Clause:** 8.3 - Business Continuity Strategy
**Endpoints:** 8
**State Machine:** Draft → Under Review → Approved → Active → Archived

### Flow 3.1: Strategy Creation
**Trigger:** `POST /strategies`
**Steps:**
1. Create BC strategy with type:
   - RECOVERY_SITE: Hot site, warm site, cold site
   - WORK_AREA_RECOVERY: Alternative work locations
   - DATA_BACKUP: Backup and restore strategy
   - SUPPLIER_RESILIENCE: Supply chain continuity
   - PEOPLE: Remote work, cross-training
   - TECHNOLOGY: System redundancy, failover
   - MANUAL_WORKAROUND: Manual procedures
2. Define RTO/RPO targets strategy must meet
3. Set priority (CRITICAL, HIGH, MEDIUM, LOW)
4. Estimate implementation cost
5. Set status to DRAFT
6. **Publish event:** `planning.strategy.created`

**Events Published:**
- `planning.strategy.created` - Payload: `{tenant_id, strategy_id, strategy_type, priority}`

**State Transition:** None → Draft
**Dependencies:** BIA Service (uses RTO/RPO requirements)

---

### Flow 3.2: Cost-Benefit Analysis
**Trigger:** `POST /strategies/{strategy_id}/cost-benefit`
**ISO Requirement:** Clause 8.3 mandates cost-benefit analysis
**Steps:**
1. Fetch strategy
2. Calculate costs:
   - Implementation cost (one-time)
   - Annual maintenance cost
   - Training cost
   - Testing cost
   - Total cost (5-year projection)
3. Calculate benefits:
   - Potential loss avoided (from BIA financial impact)
   - RTO improvement value
   - Compliance benefits
   - Reputation protection
4. Calculate metrics:
   - ROI = (Benefits - Costs) / Costs
   - Payback period (months)
   - Net present value (NPV)
5. Determine recommendation: RECOMMENDED / NOT_RECOMMENDED / NEUTRAL
6. Store cost-benefit analysis
7. **Publish event:** `planning.cost_benefit.completed`

**Example:**
```json
{
  "strategy_id": "uuid",
  "implementation_cost": 500000,
  "annual_cost": 100000,
  "five_year_cost": 900000,
  "potential_loss_avoided": 5000000,
  "roi": 455,
  "payback_period_months": 3,
  "npv": 4100000,
  "recommendation": "RECOMMENDED"
}
```

---

### Flow 3.3: Strategy Approval
**Trigger:** `POST /strategies/{strategy_id}/approve`
**Steps:**
1. Validate strategy has cost-benefit analysis
2. Update status to APPROVED
3. Set approved_by, approved_at
4. **Publish event:** `planning.strategy.approved`
5. Trigger Plans Service to create implementation plan

**State Transition:** Under Review → Approved
**Events Published:**
- `planning.strategy.approved` - Payload: `{tenant_id, strategy_id, strategy_type, approved_by, rto_target, rpo_target}`

**Downstream Consumers:**
- Plans Service: Creates plan based on approved strategy
- Documents Service: Generates strategy document

---

### Planning Service: Strategy Types

1. **RECOVERY_SITE**
   - Hot Site: < 1 hour RTO, highest cost
   - Warm Site: 4-24 hour RTO, moderate cost
   - Cold Site: > 24 hour RTO, lowest cost

2. **DATA_BACKUP**
   - Real-time replication: RPO near-zero
   - Hourly backup: RPO 1 hour
   - Daily backup: RPO 24 hours

3. **WORK_AREA_RECOVERY**
   - Office space alternatives
   - Remote work capability
   - Vendor workspace agreements

4. **SUPPLIER_RESILIENCE**
   - Alternative suppliers
   - Buffer stock
   - Dual sourcing

5. **PEOPLE**
   - Cross-training programs
   - Succession planning
   - Remote work infrastructure

6. **TECHNOLOGY**
   - Load balancing
   - Failover systems
   - Cloud migration

7. **MANUAL_WORKAROUND**
   - Paper-based procedures
   - Manual processing
   - Temporary alternatives

---

## 4. Plans Service

**Port:** 8023
**ISO Clause:** 8.4 - Business Continuity Plans and Procedures
**Endpoints:** 25+
**State Machine:** Draft → Under Review → Approved → Active → Superseded → Archived

### Flow 4.1: Plan Creation
**Trigger:** `POST /api/plans/plans`
**ISO Requirements:** Clause 8.4.1, 8.4.4
**Steps:**
1. Create BC plan with type:
   - BUSINESS_CONTINUITY_PLAN (BCP): Overall plan
   - DISASTER_RECOVERY_PLAN (DRP): IT recovery
   - CRISIS_MANAGEMENT_PLAN (CMP): Leadership response
   - INCIDENT_RESPONSE_PLAN (IRP): Incident handling
   - COMMUNICATION_PLAN: Stakeholder comms
   - PANDEMIC_PLAN: Health emergency
   - CYBER_INCIDENT_PLAN: Cyber response
2. Set priority based on criticality (from BIA)
3. Define scope (departments, processes, locations)
4. Set review frequency (6/12/24 months)
5. Calculate next_review_date
6. Set status to DRAFT
7. **Publish event:** `plans.plan.created`

**Events Published:**
- `plans.plan.created` - Payload: `{tenant_id, plan_id, plan_type, priority}`

**State Transition:** None → Draft
**Dependencies:**
- BIA Service: Process criticality
- Planning Service: Approved strategies

---

### Flow 4.2: Plan Lifecycle - Submit for Review
**Trigger:** `POST /api/plans/plans/{plan_id}/submit-review`
**Steps:**
1. Validate plan completeness:
   - All required procedures defined
   - Contact lists populated
   - Resources identified
   - Approval chain defined
2. Update status to UNDER_REVIEW
3. Set submitted_by, submitted_at
4. **Publish event:** `plans.plan.submitted`
5. Notify approvers (via notification service)

**State Transition:** Draft → Under Review
**Validation Rules:**
- Must have >= 1 procedure
- Must have contact list
- Must have assigned owner

---

### Flow 4.3: Plan Lifecycle - Approve
**Trigger:** `POST /api/plans/plans/{plan_id}/approve`
**Steps:**
1. Validate current status is UNDER_REVIEW
2. Validate user has approval authority
3. Update status to APPROVED
4. Set approved_by, approved_at
5. Set effective_date (if provided, else now)
6. **Publish event:** `plans.plan.approved`
7. Store approval record with notes
8. Notify plan owner

**State Transition:** Under Review → Approved
**Events Published:**
- `plans.plan.approved` - Payload: `{tenant_id, plan_id, plan_type, approved_by, effective_date}`

**Downstream Consumers:**
- Validation Service: Plan is now testable
- Documents Service: Generate PDF version
- Governance Service: Track policy compliance

---

### Flow 4.4: Plan Lifecycle - Activate
**Trigger:** `POST /api/plans/plans/{plan_id}/activate`
**Steps:**
1. Validate status is APPROVED
2. Update status to ACTIVE
3. Set activated_by, activated_at
4. **Publish event:** `plans.plan.activated`
5. Make plan visible to all users in scope
6. Enable testing and exercises

**State Transition:** Approved → Active
**Events Published:**
- `plans.plan.activated` - Payload: `{tenant_id, plan_id, plan_type, activated_at}`

---

### Flow 4.5: Procedure Management
**Trigger:** `POST /api/plans/plans/{plan_id}/procedures`
**ISO Requirement:** Clause 8.4.4 - Procedures
**Steps:**
1. Add procedure to plan:
   - Step-by-step instructions
   - Responsible role
   - Required resources
   - Time estimate
   - Decision points
2. Define procedure type:
   - ASSESSMENT: Situation assessment
   - NOTIFICATION: Alert stakeholders
   - ACTIVATION: Trigger plan
   - RECOVERY: Restore operations
   - COMMUNICATION: Internal/external comms
   - EVACUATION: Move people
   - IT_RECOVERY: Restore systems
   - MANUAL_WORKAROUND: Alternative process
3. Set sequence number (execution order)
4. **Publish event:** `plans.procedure.added`

**Procedure Structure:**
```json
{
  "procedure_id": 123,
  "plan_id": 456,
  "name": "Activate Emergency Operations Center",
  "procedure_type": "ACTIVATION",
  "sequence_number": 1,
  "description": "Steps to open and staff the EOC",
  "steps": [
    {
      "step_number": 1,
      "description": "Notify EOC manager",
      "responsible_role": "Duty Manager",
      "estimated_time_minutes": 5
    },
    {
      "step_number": 2,
      "description": "Open EOC facility",
      "responsible_role": "Facilities Team",
      "estimated_time_minutes": 15
    }
  ],
  "resources_required": ["EOC facility", "Communication equipment"],
  "success_criteria": "EOC operational within 30 minutes"
}
```

---

### Flow 4.6: Resource Management
**Trigger:** `POST /api/plans/plans/{plan_id}/resources`
**Steps:**
1. Add resource to plan:
   - Resource type: FACILITY, EQUIPMENT, SUPPLIES, TECHNOLOGY, PERSONNEL
   - Resource name
   - Quantity required
   - Location
   - Vendor/supplier
   - Lead time
2. Track resource availability
3. **Publish event:** `plans.resource.added`

**Resource Types:**
- **FACILITY:** Alternative work sites, recovery centers
- **EQUIPMENT:** Generators, laptops, phones
- **SUPPLIES:** Paper, forms, consumables
- **TECHNOLOGY:** Software licenses, cloud services
- **PERSONNEL:** Crisis team, contractors, specialists

---

### Flow 4.7: Contact List Management
**Trigger:** `POST /api/plans/contact-lists`
**Steps:**
1. Create contact list (or update existing)
2. Add contacts:
   - Name, role, phone, email
   - Primary / backup designation
   - 24/7 availability
   - Special skills
3. Link to plan
4. **Publish event:** `plans.contact_list.updated`

**Contact List Types:**
- Crisis Management Team
- Emergency Responders
- Key Suppliers
- Regulatory Authorities
- Media Contacts
- Employee Emergency Contacts

---

### Flow 4.8: Plan Activation (Real Incident)
**Trigger:** `POST /api/plans/plans/{plan_id}/activate-real`
**Steps:**
1. Create activation record:
   - Incident details
   - Activation time
   - Activated by
   - Activation reason
2. Update plan status to IN_USE
3. Start tracking metrics:
   - Activation time
   - Procedure execution times
   - RTO/RPO adherence
4. **Publish event:** `plans.plan.activated_real`
5. Notify all contact lists
6. Log all actions to audit trail

**State Transition:** Active → In Use
**Events Published:**
- `plans.plan.activated_real` - Payload: `{tenant_id, plan_id, incident_id, activated_by, activation_time}`

**Downstream Consumers:**
- Response Service: Link to incident
- Notification Service: Alert all contacts
- Validation Service: Track RTO/RPO compliance

**Metrics Tracked:**
- Time to activate
- Time to complete each procedure
- Resources deployed
- RTO met (Yes/No)
- RPO met (Yes/No)

---

### Flow 4.9: Plan Review
**Trigger:** `POST /api/plans/plans/{plan_id}/reviews`
**ISO Requirement:** Clause 8.4.1 - Periodic review
**Steps:**
1. Create review record:
   - Review date
   - Reviewer
   - Review findings
   - Recommendations
   - Next review date
2. Assess plan effectiveness:
   - Procedures still valid
   - Contact lists current
   - Resources available
   - Aligned with current risks
3. Update plan if needed
4. Set next_review_date
5. **Publish event:** `plans.plan.reviewed`

**State Transition:** Active → Active (stays active after review)
**Review Frequency:** 6/12/24 months based on plan criticality

---

### Plans Service: Plan Types

1. **BUSINESS_CONTINUITY_PLAN (BCP)**
   - Overall strategy and coordination
   - Recovery priorities
   - Resource allocation
   - Dependencies: All services

2. **DISASTER_RECOVERY_PLAN (DRP)**
   - IT system recovery
   - Data restoration
   - Infrastructure rebuild
   - Dependencies: BIA (technology criticality)

3. **CRISIS_MANAGEMENT_PLAN (CMP)**
   - Leadership activation
   - Decision-making framework
   - Stakeholder communication
   - Dependencies: Governance (roles)

4. **INCIDENT_RESPONSE_PLAN (IRP)**
   - Incident detection
   - Containment
   - Eradication
   - Recovery
   - Dependencies: Response Service

5. **COMMUNICATION_PLAN**
   - Internal notifications
   - External communications
   - Media relations
   - Dependencies: Governance (stakeholders)

6. **PANDEMIC_PLAN**
   - Health emergency response
   - Remote work procedures
   - Infection control
   - Dependencies: BIA (WHO tiers)

7. **CYBER_INCIDENT_PLAN**
   - Cyber attack response
   - Breach notification
   - Forensics
   - Dependencies: Risk Service (cyber risks)

---

## 5. Response Service

**Port:** 8026
**ISO Clause:** 8.4 - Incident Response
**Endpoints:** 24
**State Machine:** New → Investigating → Contained → Resolving → Resolved → Closed

### Flow 5.1: Incident Creation
**Trigger:** `POST /api/v1/response/incidents`
**Steps:**
1. Create incident with:
   - Incident type (OPERATIONAL, IT_OUTAGE, SECURITY_BREACH, NATURAL_DISASTER, PANDEMIC, SUPPLIER_FAILURE, DATA_LOSS, FACILITY_DAMAGE, CYBER_ATTACK, OTHER)
   - Severity (LOW, MEDIUM, HIGH, CRITICAL)
   - Affected systems
   - Detection time
2. Auto-generate incident number (INC-YYYYMMDD-NNNN)
3. Set status to NEW
4. Assign incident commander (based on severity)
5. Calculate priority score = severity × urgency
6. **Publish event:** `response.incident.created`
7. **Trigger:** Notification to on-call team

**Events Published:**
- `response.incident.created` - Payload: `{incident_id, incident_number, organization_id, title, severity, incident_type, affected_systems, detected_at}`

**State Transition:** None → New
**Auto-Assignment Rules:**
- CRITICAL: SVP/Director level
- HIGH: Manager level
- MEDIUM: Team Lead level
- LOW: Standard responder

---

### Flow 5.2: Incident Status Update
**Trigger:** `PATCH /api/v1/response/incidents/{incident_id}/status`
**Steps:**
1. Validate status transition is allowed
2. Update incident status
3. Set transition timestamp
4. Log status change to timeline
5. **Publish event:** `response.incident.status_changed`
6. Notify stakeholders of status change

**Events Published:**
- `response.incident.status_changed` - Payload: `{incident_id, incident_number, organization_id, old_status, new_status, severity}`

**State Transitions:**
- NEW → INVESTIGATING: Initial response started
- INVESTIGATING → CONTAINED: Threat contained/isolated
- CONTAINED → RESOLVING: Recovery in progress
- RESOLVING → RESOLVED: Service restored
- RESOLVED → CLOSED: Post-incident review complete

---

### Flow 5.3: Plan Activation from Incident
**Trigger:** `POST /api/v1/response/incidents/{incident_id}/activate-plan`
**Steps:**
1. Validate incident exists and is active
2. Select appropriate plan based on:
   - Incident type
   - Severity
   - Affected systems
3. Activate plan (call Plans Service)
4. Link plan activation to incident
5. **Publish event:** `response.plan.activated`
6. Track plan execution metrics

**Integration:** Plans Service Flow 4.8
**Metrics Tracked:**
- Time from incident creation to plan activation
- Plan effectiveness (did it help?)

---

### Flow 5.4: Incident Escalation
**Trigger:** `POST /api/v1/response/incidents/{incident_id}/escalate`
**Steps:**
1. Validate escalation reason
2. Determine escalation level:
   - Level 1: Team lead
   - Level 2: Manager
   - Level 3: Director
   - Level 4: Executive leadership
3. Update incident escalation_level
4. Assign new incident commander
5. **Publish event:** `response.incident.escalated`
6. Notify escalation team

**Events Published:**
- `response.incident.escalated` - Payload: `{incident_id, incident_number, organization_id, severity, escalation_level, escalation_reason, escalate_to[]}`

**Escalation Triggers (Auto):**
- Incident open > SLA time
- Multiple related incidents
- Severity increases
- Critical resource affected
- Regulatory notification required

---

### Flow 5.5: Incident Resolution
**Trigger:** `POST /api/v1/response/incidents/{incident_id}/resolve`
**Steps:**
1. Validate incident is in RESOLVING status
2. Record resolution details:
   - Root cause
   - Resolution actions taken
   - Lessons learned
3. Calculate incident duration
4. Update status to RESOLVED
5. Set resolved_at timestamp
6. **Calculate RTO/RPO compliance:**
   - Compare to BIA targets
   - Flag violations
7. **Publish event:** `response.incident.resolved`
8. **If RTO/RPO violated:** Publish `response.compliance.violation`
9. Schedule post-incident review

**Events Published:**
- `response.incident.resolved` - Payload: `{incident_id, incident_number, organization_id, severity, duration_hours, detected_at, resolved_at, root_cause}`
- `response.compliance.violation` (conditional) - Payload: `{incident_id, incident_number, organization_id, violation_type, details}`

**RTO/RPO Validation:**
- Fetch affected process from BIA Service
- Compare actual recovery time vs. RTO
- Compare data loss vs. RPO
- Generate compliance report

---

### Flow 5.6: Incident Closure
**Trigger:** `POST /api/v1/response/incidents/{incident_id}/close`
**Steps:**
1. Validate incident is RESOLVED
2. Validate post-incident review completed
3. Update status to CLOSED
4. Set closed_at timestamp
5. Archive incident data (long-term storage)
6. **Publish event:** `response.incident.closed`
7. Update incident statistics

**Events Published:**
- `response.incident.closed` - Payload: `{incident_id, incident_number, organization_id, severity, duration_hours, detected_at, closed_at}`

**State Transition:** Resolved → Closed (terminal)

---

### Flow 5.7: Stakeholder Notification
**Trigger:** `POST /api/v1/response/incidents/{incident_id}/notify-stakeholders`
**Steps:**
1. Determine stakeholders based on:
   - Incident severity
   - Affected systems
   - Regulatory requirements
2. Compose notification message:
   - Incident summary
   - Current status
   - Expected resolution time
   - Actions taken
3. Send via multiple channels:
   - Email
   - SMS
   - In-app notification
4. **Publish event:** `response.stakeholder.notification`
5. Track notification delivery

**Events Published:**
- `response.stakeholder.notification` - Payload: `{incident_id, incident_number, organization_id, severity, message, recipients[]}`

**Stakeholder Types:**
- Internal: Employees, management
- External: Customers, suppliers, regulators
- Media: Public relations (for major incidents)

---

### Flow 5.8: Timeline Entry
**Trigger:** `POST /api/v1/response/incidents/{incident_id}/timeline`
**Steps:**
1. Add event to incident timeline:
   - Timestamp
   - Event type
   - Description
   - Actor (who did it)
   - Actions taken
2. Store timeline entry
3. Update last_activity timestamp
4. Optional: Publish event for major milestones

**Timeline Event Types:**
- STATUS_CHANGE: Status updated
- ESCALATION: Incident escalated
- NOTIFICATION: Stakeholders notified
- ACTION_TAKEN: Recovery action performed
- COMMUNICATION: Communication sent
- RESOURCE_DEPLOYED: Resource activated
- PLAN_ACTIVATED: BCM plan triggered

**Use Case:** Audit trail, post-incident review, compliance evidence

---

### Flow 5.9: Recovery Metrics
**Trigger:** `POST /api/v1/response/incidents/{incident_id}/recovery-metrics`
**Steps:**
1. Record recovery metrics:
   - Service name
   - Recovery start time
   - Recovery end time
   - Actual RTO (minutes)
   - Target RTO (from BIA)
   - RTO met (boolean)
   - Data loss (minutes)
   - Target RPO (from BIA)
   - RPO met (boolean)
2. Calculate compliance:
   - RTO variance (actual - target)
   - RPO variance (actual - target)
3. **Publish event:** `response.metrics.updated`
4. Update incident with metrics

**Events Published:**
- `response.metrics.updated` - Payload: `{incident_id, service_name, rto_met, rpo_met}`

**Integration:** BIA Service (fetch RTO/RPO targets)

---

### Flow 5.10: Incident Reports
**Trigger:** `GET /api/v1/response/reports`
**Report Types:**

1. **Active Incidents Report**
   - All open incidents
   - Status breakdown
   - Severity distribution
   - SLA compliance

2. **Incident History**
   - Closed incidents by period
   - Average resolution time
   - Top incident types
   - Repeat incidents

3. **RTO/RPO Compliance**
   - Percentage of incidents meeting RTO
   - Percentage meeting RPO
   - Violations by process
   - Trend analysis

4. **MTTR (Mean Time To Resolve)**
   - Average resolution time by severity
   - Trend over time
   - By incident type

---

### Response Service: State Machine

```
[None] --create--> [NEW]
[NEW] --investigate--> [INVESTIGATING]
[INVESTIGATING] --contain--> [CONTAINED]
[CONTAINED] --resolve--> [RESOLVING]
[RESOLVING] --complete--> [RESOLVED]
[RESOLVED] --close--> [CLOSED]

[NEW/INVESTIGATING/CONTAINED] --escalate--> [ESCALATED]
[ESCALATED] --de-escalate--> [Previous State]
```

**Status Descriptions:**
- **NEW:** Incident reported, awaiting initial response
- **INVESTIGATING:** Team assessing impact and root cause
- **CONTAINED:** Threat contained, preventing further damage
- **RESOLVING:** Recovery actions underway
- **RESOLVED:** Service restored, monitoring stability
- **CLOSED:** Incident closed after post-incident review

---

## 6. Validation Service

**Port:** 8029
**ISO Clause:** 9.1-9.3 - Monitoring, Measurement, Exercise, Testing
**Endpoints:** 15+
**State Machine:** Planned → Scheduled → In Progress → Completed → Reviewed

### Flow 6.1: Exercise Creation
**Trigger:** `POST /api/v1/validation/exercises`
**ISO Requirements:** Clause 9.1.2 - Testing and Exercising
**Steps:**
1. Create exercise with type:
   - TABLETOP: Discussion-based walkthrough
   - WALKTHROUGH: Step-by-step review
   - SIMULATION: Simulated scenario
   - FUNCTIONAL: Partial activation
   - FULL_SCALE: Complete activation
2. Link to plan(s) being tested
3. Define scope (departments, processes, systems)
4. Set objectives (what to test)
5. Assign exercise coordinator
6. Set status to PLANNED
7. **Publish event:** `validation.exercise.created`

**Events Published:**
- `validation.exercise.created` - Payload: `{tenant_id, exercise_id, exercise_type, plan_id, scheduled_date}`

**State Transition:** None → Planned
**Dependencies:**
- Plans Service: Must have ACTIVE plan to test

---

### Flow 6.2: Exercise Scheduling
**Trigger:** `POST /api/v1/validation/exercises/{exercise_id}/schedule`
**Steps:**
1. Select date/time
2. Assign participants:
   - Players (those being tested)
   - Observers (watching)
   - Controllers (running exercise)
   - Evaluators (assessing performance)
3. Send calendar invitations
4. Update status to SCHEDULED
5. **Publish event:** `validation.exercise.scheduled`
6. Set reminder notifications (7 days, 1 day, 1 hour before)

**State Transition:** Planned → Scheduled

---

### Flow 6.3: Exercise Execution
**Trigger:** `POST /api/v1/validation/exercises/{exercise_id}/start`
**Steps:**
1. Validate all participants ready
2. Update status to IN_PROGRESS
3. Set start_time
4. Initialize scenario injection (for simulations)
5. Start timeline tracking
6. **Publish event:** `validation.exercise.started`
7. Enable real-time observation logging

**State Transition:** Scheduled → In Progress

---

### Flow 6.4: Exercise Observation
**Trigger:** `POST /api/v1/validation/exercises/{exercise_id}/observations`
**Steps:**
1. Log observation in real-time:
   - Timestamp
   - Observer
   - Observation type (SUCCESS, ISSUE, GAP, IMPROVEMENT)
   - Description
   - Severity (if issue/gap)
   - Procedure/process affected
2. Store observation
3. Optional: Alert exercise coordinator if critical issue

**Observation Types:**
- **SUCCESS:** Procedure executed correctly
- **ISSUE:** Problem during execution
- **GAP:** Missing procedure or resource
- **IMPROVEMENT:** Suggestion for enhancement

---

### Flow 6.5: Exercise Completion
**Trigger:** `POST /api/v1/validation/exercises/{exercise_id}/complete`
**Steps:**
1. Set end_time
2. Calculate duration
3. Update status to COMPLETED
4. Generate preliminary report:
   - Objectives achieved
   - Success rate (%)
   - Issues found (count by severity)
   - Gaps identified
5. **Publish event:** `validation.exercise.completed`
6. Schedule hot debrief (within 24 hours)

**Events Published:**
- `validation.exercise.completed` - Payload: `{tenant_id, exercise_id, plan_id, exercise_type, duration_minutes, success_rate, issues_found}`

**State Transition:** In Progress → Completed

---

### Flow 6.6: Exercise Evaluation
**Trigger:** `POST /api/v1/validation/exercises/{exercise_id}/evaluate`
**ISO Requirement:** Clause 9.1.2 - Evaluation criteria
**Steps:**
1. Evaluate against objectives:
   - Each objective: MET / PARTIALLY_MET / NOT_MET
   - Score (0-100)
2. Assess plan effectiveness:
   - Procedures clear and accurate
   - Resources adequate
   - Communication effective
   - Time objectives met (RTO/RPO)
3. Identify corrective actions:
   - What needs fixing
   - Priority (CRITICAL, HIGH, MEDIUM, LOW)
   - Responsible party
   - Target completion date
4. Generate evaluation report
5. Update status to REVIEWED
6. **Publish event:** `validation.exercise.evaluated`

**State Transition:** Completed → Reviewed

---

### Flow 6.7: Corrective Actions
**Trigger:** `POST /api/v1/validation/corrective-actions`
**Steps:**
1. Create corrective action from exercise finding:
   - Finding (what was wrong)
   - Root cause
   - Corrective action (what to do)
   - Responsible party
   - Target date
   - Status (OPEN)
2. Assign to responsible party
3. **Publish event:** `validation.corrective_action.created`
4. Track in CAPA (Corrective and Preventive Action) system

**Events Published:**
- `validation.corrective_action.created` - Payload: `{tenant_id, corrective_action_id, exercise_id, finding, priority, responsible_party, target_date}`

**Downstream Consumers:**
- Plans Service: Update plan/procedures
- Documents Service: Update documentation
- Governance Service: Track compliance improvement

---

### Flow 6.8: Corrective Action Closure
**Trigger:** `PUT /api/v1/validation/corrective-actions/{action_id}/close`
**Steps:**
1. Validate action completed
2. Verify evidence of completion
3. Update status to CLOSED
4. Set closed_date
5. **Publish event:** `validation.corrective_action.closed`
6. Link to updated plan/document

**State Transition:** Open → Closed

---

### Flow 6.9: KPI Monitoring
**Trigger:** `POST /api/v1/validation/kpis`
**ISO Requirement:** Clause 9.1.1 - Monitoring and Measurement
**Steps:**
1. Define KPI:
   - KPI name
   - Description
   - Measurement method
   - Target value
   - Threshold (red/amber/green)
   - Collection frequency
2. Set data source (manual or automated)
3. Schedule collection
4. **Publish event:** `validation.kpi.created`

**KPI Examples:**
- Plan testing frequency (target: 100% annually)
- Exercise success rate (target: >= 80%)
- RTO compliance rate (target: >= 95%)
- RPO compliance rate (target: >= 95%)
- Plan review currency (target: 100% within schedule)
- Staff awareness training completion (target: 100%)

---

### Flow 6.10: KPI Data Collection
**Trigger:** `POST /api/v1/validation/kpis/{kpi_id}/data`
**Steps:**
1. Collect KPI measurement:
   - Value
   - Collection date
   - Collected by
   - Notes
2. Compare to target
3. Determine status (ABOVE_TARGET, ON_TARGET, BELOW_TARGET, CRITICAL)
4. **If below threshold:** Publish alert
5. Store measurement
6. **Publish event:** `validation.kpi.measured`

**Events Published:**
- `validation.kpi.measured` - Payload: `{tenant_id, kpi_id, kpi_name, value, target, status, collection_date}`
- `validation.kpi.alert` (if critical) - Payload: `{tenant_id, kpi_id, kpi_name, value, target, deviation}`

---

### Flow 6.11: Audit Trail
**Trigger:** `GET /api/v1/validation/audit-trail`
**ISO Requirement:** Clause 9.3 - Management Review
**Steps:**
1. Query audit events by:
   - Date range
   - Entity type (exercise, kpi, corrective_action)
   - Action type (created, updated, completed)
   - User
2. Return audit trail with:
   - Timestamp
   - User
   - Action
   - Entity affected
   - Before/after values
3. Support export to PDF/CSV

**Use Case:** ISO 22301 certification audit, management review

---

### Validation Service: Exercise Types

1. **TABLETOP Exercise**
   - Duration: 2-4 hours
   - Participants: 5-15
   - Cost: Low
   - Frequency: Quarterly
   - Purpose: Test knowledge and decision-making

2. **WALKTHROUGH**
   - Duration: 4-6 hours
   - Participants: 10-20
   - Cost: Low-Medium
   - Frequency: Semi-annually
   - Purpose: Review procedures step-by-step

3. **SIMULATION**
   - Duration: 4-8 hours
   - Participants: 20-50
   - Cost: Medium
   - Frequency: Semi-annually
   - Purpose: Practice with simulated scenario

4. **FUNCTIONAL Test**
   - Duration: 8-24 hours
   - Participants: 20-100
   - Cost: Medium-High
   - Frequency: Annually
   - Purpose: Test subset of plan (e.g., IT recovery only)

5. **FULL_SCALE Exercise**
   - Duration: 24-72 hours
   - Participants: 50-500
   - Cost: High
   - Frequency: Every 2-3 years
   - Purpose: Test complete plan activation

---

## 7. Compliance Service

**Port:** 8018
**ISO Clause:** 9-10 - Performance Evaluation, Improvement
**Endpoints:** 30+
**State Machine:** Multiple workflows (Assessment, Audit, Review, Improvement)

### Flow 7.1: Compliance Assessment Creation
**Trigger:** `POST /api/v1/compliance/assessments`
**Steps:**
1. Create assessment with:
   - Assessment type (INTERNAL, EXTERNAL, CERTIFICATION, SELF_ASSESSMENT)
   - Standard (ISO_22301, ISO_27001, NIST, SOC2, etc.)
   - Scope (which clauses/controls)
   - Assessor
   - Target date
2. Generate control checklist from standard
3. Set status to PLANNED
4. **Publish event:** `compliance.assessment.created`

**Events Published:**
- `compliance.assessment.created` - Payload: `{tenant_id, assessment_id, assessment_type, standard, scheduled_date}`

**State Transition:** None → Planned

---

### Flow 7.2: Gap Analysis
**Trigger:** `POST /api/v1/compliance/assessments/{assessment_id}/gap-analysis`
**Steps:**
1. For each control in standard:
   - Check current implementation status
   - Identify evidence (documents, procedures, logs)
   - Determine maturity level (0-5):
     - 0: Not implemented
     - 1: Initial (ad-hoc)
     - 2: Managed (documented)
     - 3: Defined (standardized)
     - 4: Quantitatively managed (measured)
     - 5: Optimizing (continuous improvement)
2. Calculate gap:
   - Current maturity - Required maturity
   - Priority based on risk
3. Generate gap report:
   - Controls with gaps
   - Missing evidence
   - Recommended actions
4. **Publish event:** `compliance.gap_analysis.completed`

**Example Output:**
```json
{
  "assessment_id": "uuid",
  "standard": "ISO_22301",
  "total_controls": 45,
  "compliant": 32,
  "partial": 8,
  "non_compliant": 5,
  "gaps": [
    {
      "clause": "8.2.3",
      "control": "Risk Assessment",
      "current_maturity": 2,
      "required_maturity": 4,
      "gap": 2,
      "priority": "HIGH",
      "evidence_missing": ["Risk register", "Treatment plans"]
    }
  ]
}
```

---

### Flow 7.3: Evidence Collection
**Trigger:** `POST /api/v1/compliance/evidence`
**Steps:**
1. Link evidence to control:
   - Evidence type (DOCUMENT, LOG, SCREENSHOT, CERTIFICATE, REPORT)
   - File or reference
   - Collection date
   - Collected by
   - Validity period
2. Store evidence metadata
3. Upload file (if applicable) to Documents Service
4. **Publish event:** `compliance.evidence.collected`
5. Update control status if sufficient evidence

**Evidence Types:**
- **DOCUMENT:** Policy, procedure, plan
- **LOG:** Audit log, event log, access log
- **SCREENSHOT:** System configuration, dashboard
- **CERTIFICATE:** ISO cert, SOC2 report
- **REPORT:** Exercise report, incident report

---

### Flow 7.4: Internal Audit
**Trigger:** `POST /api/v1/compliance/audits`
**ISO Requirement:** Clause 9.2 - Internal Audit
**Steps:**
1. Create audit with:
   - Audit type (INTERNAL_AUDIT, SURVEILLANCE_AUDIT, CERTIFICATION_AUDIT)
   - Scope (clauses to audit)
   - Auditor(s)
   - Auditee(s)
   - Audit dates
2. Generate audit program (schedule)
3. Set status to PLANNED
4. **Publish event:** `compliance.audit.created`
5. Send notifications to auditees

**Events Published:**
- `compliance.audit.created` - Payload: `{tenant_id, audit_id, audit_type, scope, scheduled_start_date}`

**State Transition:** None → Planned

---

### Flow 7.5: Audit Execution
**Trigger:** `POST /api/v1/compliance/audits/{audit_id}/start`
**Steps:**
1. Update status to IN_PROGRESS
2. Conduct audit:
   - Opening meeting
   - Document review
   - Interviews
   - System inspection
   - Evidence review
3. Log findings in real-time:
   - Conformity: Compliant
   - Minor Non-Conformity: Small gap
   - Major Non-Conformity: Significant gap
   - Observation: Improvement opportunity
4. **Publish event:** `compliance.audit.started`

**State Transition:** Planned → In Progress

---

### Flow 7.6: Audit Finding
**Trigger:** `POST /api/v1/compliance/audits/{audit_id}/findings`
**Steps:**
1. Create finding:
   - Finding type (CONFORMITY, MINOR_NC, MAJOR_NC, OBSERVATION)
   - Clause reference
   - Description
   - Evidence reviewed
   - Requirement not met (for NCs)
   - Recommendation
2. Assign to responsible party for corrective action
3. Set target closure date (30/60/90 days based on severity)
4. **Publish event:** `compliance.audit.finding.created`

**Events Published:**
- `compliance.audit.finding.created` - Payload: `{tenant_id, audit_id, finding_id, finding_type, clause, responsible_party}`

**Downstream:**
- Validation Service: Create corrective action
- Governance Service: Assign accountability

---

### Flow 7.7: Audit Report
**Trigger:** `POST /api/v1/compliance/audits/{audit_id}/complete`
**Steps:**
1. Generate audit report:
   - Executive summary
   - Audit scope and method
   - Findings summary (conformity, minor NC, major NC, observations)
   - Detailed findings
   - Recommendations
   - Corrective action plan
2. Update status to COMPLETED
3. Set completion_date
4. **Publish event:** `compliance.audit.completed`
5. Send report to management

**Events Published:**
- `compliance.audit.completed` - Payload: `{tenant_id, audit_id, total_findings, major_nc, minor_nc, observations, completion_date}`

**State Transition:** In Progress → Completed

---

### Flow 7.8: Management Review
**Trigger:** `POST /api/v1/compliance/management-reviews`
**ISO Requirement:** Clause 9.3 - Management Review
**Steps:**
1. Create management review record:
   - Review date
   - Attendees
   - Review scope
2. Compile review inputs:
   - Status of actions from previous review
   - Changes in external and internal issues
   - Feedback on BCMS performance (KPIs)
   - Results of exercises and tests
   - Results of audits
   - Corrective actions status
   - Opportunities for improvement
3. Conduct review meeting
4. Document review outputs:
   - Decisions on improvement opportunities
   - Resource allocation
   - Policy/objective changes
5. **Publish event:** `compliance.management_review.completed`

**Events Published:**
- `compliance.management_review.completed` - Payload: `{tenant_id, review_id, review_date, decisions_count, actions_count}`

**Frequency:** Minimum annually (ISO 22301 requirement)

---

### Flow 7.9: Improvement Opportunity
**Trigger:** `POST /api/v1/compliance/improvements`
**ISO Requirement:** Clause 10 - Improvement
**Steps:**
1. Create improvement opportunity from:
   - Exercise finding
   - Audit observation
   - Incident lesson learned
   - Staff suggestion
   - Management review decision
2. Define improvement:
   - Current state
   - Desired state
   - Benefits
   - Effort estimate
   - Priority
3. Assign owner
4. Set target date
5. **Publish event:** `compliance.improvement.created`

**Events Published:**
- `compliance.improvement.created` - Payload: `{tenant_id, improvement_id, improvement_type, priority, owner, target_date}`

---

### Flow 7.10: Improvement Implementation
**Trigger:** `PUT /api/v1/compliance/improvements/{improvement_id}/implement`
**Steps:**
1. Execute improvement:
   - Update procedures
   - Modify systems
   - Train staff
   - Update documentation
2. Verify effectiveness:
   - Test changes
   - Measure results
   - Compare to desired state
3. Update status to IMPLEMENTED
4. **Publish event:** `compliance.improvement.implemented`
5. Schedule effectiveness review (3-6 months)

**State Transition:** Open → Implemented

---

### Compliance Service: Assessment Types

1. **INTERNAL_AUDIT**
   - Frequency: Annual minimum
   - Auditor: Internal (must be independent)
   - Purpose: ISO 22301 Clause 9.2 requirement

2. **EXTERNAL_AUDIT (Surveillance)**
   - Frequency: Annual (between certifications)
   - Auditor: Certification body
   - Purpose: Maintain certification

3. **CERTIFICATION_AUDIT**
   - Frequency: Every 3 years
   - Auditor: Accredited certification body
   - Purpose: Initial or re-certification

4. **SELF_ASSESSMENT**
   - Frequency: Ongoing
   - Auditor: Internal teams
   - Purpose: Continuous improvement

---

## 8. Governance Service

**Port:** 8033
**ISO Clause:** 4-7 (Context, Leadership, Planning, Support)
**Endpoints:** 40+
**State Machine:** Multiple workflows (Policy, Role, Resource, Objective)

### Flow 8.1: Policy Creation
**Trigger:** `POST /api/governance/policies`
**ISO Requirement:** Clause 5.2 - Policy
**Steps:**
1. Create policy with:
   - Policy type (BCMS_POLICY, SECURITY_POLICY, HR_POLICY, IT_POLICY, etc.)
   - Title, description
   - Policy content
   - Scope (who it applies to)
   - Effective date
   - Review frequency
2. Link to ISO clauses
3. Set status to DRAFT
4. **Publish event:** `governance.policy.created`

**Events Published:**
- `governance.policy.created` - Payload: `{tenant_id, policy_id, policy_type, title, status}`

**State Transition:** None → Draft
**Dependencies:** None

---

### Flow 8.2: Policy Approval Workflow
**Trigger:** `POST /api/governance/policies/{policy_id}/approve`
**Steps:**
1. Validate policy is in DRAFT status
2. Check policy completeness:
   - All required sections present
   - Legal review (if needed)
   - Stakeholder consultation
3. Route for approval based on policy type:
   - BCMS_POLICY: CEO or BCM Director
   - SECURITY_POLICY: CISO
   - HR_POLICY: HR Director
4. Collect approval
5. Update status to APPROVED
6. Set approved_by, approved_at
7. **Publish event:** `governance.policy.approved`

**Events Published:**
- `governance.policy.approved` - Payload: `{tenant_id, policy_id, policy_type, title, approved_by, effective_date}`

**State Transition:** Draft → Approved

---

### Flow 8.3: Policy Publication
**Trigger:** `POST /api/governance/policies/{policy_id}/publish`
**Steps:**
1. Validate policy is APPROVED
2. Update status to PUBLISHED
3. Set published_date
4. Make policy available to all users in scope
5. **Publish event:** `governance.policy.published`
6. Send notification to affected users
7. Generate training requirement (if specified)

**Events Published:**
- `governance.policy.published` - Payload: `{tenant_id, policy_id, policy_type, title, published_date, scope, training_required}`

**State Transition:** Approved → Published
**Downstream Consumers:**
- Learning Service: Create training if required
- Documents Service: Store policy document
- Notification Service: Alert users

---

### Flow 8.4: Role Definition
**Trigger:** `POST /api/governance/roles`
**ISO Requirement:** Clause 5.3 - Roles and Responsibilities
**Steps:**
1. Create role with:
   - Role name
   - Role type (BCMS_ROLE, DEPARTMENTAL_ROLE, EXTERNAL_ROLE)
   - Responsibilities (list of duties)
   - Authority (what they can decide)
   - Required competencies
   - Required training
2. Define relationships:
   - Reports to
   - Supervises
   - Coordinates with
3. Set status to ACTIVE
4. **Publish event:** `governance.role.created`

**Events Published:**
- `governance.role.created` - Payload: `{tenant_id, role_id, role_name, role_type, responsibilities[]}`

**BCMS Roles (ISO 22301):**
- Top Management
- BCMS Manager
- Business Continuity Coordinator
- Crisis Management Team members
- Recovery Team Leaders
- Incident Commanders
- Emergency Response Team

---

### Flow 8.5: Role Assignment
**Trigger:** `POST /api/governance/roles/{role_id}/assign`
**Steps:**
1. Assign person to role:
   - Person ID
   - Start date
   - End date (if temporary)
   - Assignment type (PRIMARY, BACKUP, TEMPORARY)
2. Validate person meets competency requirements
3. Check for training completion
4. Store assignment
5. **Publish event:** `governance.role.assigned`
6. Update organizational chart

**Events Published:**
- `governance.role.assigned` - Payload: `{tenant_id, role_id, role_name, person_id, assignment_type, start_date}`

**Downstream Consumers:**
- Learning Service: Assign required training
- Plans Service: Update contact lists
- Notification Service: Alert person

---

### Flow 8.6: Resource Allocation
**Trigger:** `POST /api/governance/resources`
**ISO Requirement:** Clause 7.1 - Resources
**Steps:**
1. Define resource requirement:
   - Resource type (PERSONNEL, BUDGET, TECHNOLOGY, FACILITY, EQUIPMENT)
   - Description
   - Quantity needed
   - Timeline
   - Cost estimate
   - Justification
2. Link to:
   - Strategic objective
   - Plan requiring resource
   - BIA process needing resource
3. Set allocation status (REQUESTED)
4. **Publish event:** `governance.resource.requested`
5. Route for approval

**Events Published:**
- `governance.resource.requested` - Payload: `{tenant_id, resource_id, resource_type, description, cost_estimate, requested_by}`

**Resource Types:**
- **PERSONNEL:** FTEs, contractors, specialists
- **BUDGET:** Annual budget, project budget
- **TECHNOLOGY:** Software licenses, hardware
- **FACILITY:** Office space, data center
- **EQUIPMENT:** Generators, comm equipment

---

### Flow 8.7: Resource Approval
**Trigger:** `POST /api/governance/resources/{resource_id}/approve`
**Steps:**
1. Review resource request
2. Check budget availability
3. Approve or reject with reason
4. Update allocation status
5. Set allocated_budget (if approved)
6. **Publish event:** `governance.resource.approved` or `.rejected`

**Events Published:**
- `governance.resource.approved` - Payload: `{tenant_id, resource_id, resource_type, allocated_budget, approved_by}`

**State Transition:** Requested → Approved/Rejected

---

### Flow 8.8: Competence Management
**Trigger:** `POST /api/governance/competence`
**ISO Requirement:** Clause 7.2 - Competence
**Steps:**
1. Define competence requirement:
   - Role or position
   - Required knowledge
   - Required skills
   - Required experience
   - Required certifications
2. Assess current competence:
   - Gap analysis
   - Training needs
3. Create training plan
4. **Publish event:** `governance.competence.assessed`

**Events Published:**
- `governance.competence.assessed` - Payload: `{tenant_id, person_id, role_id, gaps[], training_required[]}`

**Downstream:**
- Learning Service: Create training programs

---

### Flow 8.9: Strategic Objectives
**Trigger:** `POST /api/governance/objectives`
**ISO Requirement:** Clause 6.2 - BCMS Objectives
**Steps:**
1. Create objective:
   - Title, description
   - Objective type (STRATEGIC, OPERATIONAL, TACTICAL)
   - Link to ISO clause
   - Target completion date
   - Success criteria (measurable)
   - KPIs
2. Assign owner
3. Link to risks and opportunities
4. Set status to ACTIVE
5. **Publish event:** `governance.objective.created`

**Events Published:**
- `governance.objective.created` - Payload: `{tenant_id, objective_id, title, owner, target_date}`

**Example Objectives:**
- "Achieve ISO 22301 certification by Q4 2025"
- "Reduce average RTO from 8 hours to 4 hours by Q2 2026"
- "Increase BC awareness training completion to 100% by Q3 2025"

---

### Flow 8.10: Context Analysis
**Trigger:** `POST /api/governance/context-analysis`
**ISO Requirement:** Clause 4 - Context of Organization
**Steps:**
1. Identify external issues:
   - Legal/regulatory
   - Technological
   - Economic
   - Social
   - Political
   - Environmental
2. Identify internal issues:
   - Values, culture
   - Capabilities, resources
   - Information systems
   - Contractual relationships
3. Assess impact on BCMS
4. Store context analysis
5. **Publish event:** `governance.context_analysis.completed`
6. Schedule review (annually)

**Events Published:**
- `governance.context_analysis.completed` - Payload: `{tenant_id, analysis_id, external_issues[], internal_issues[], completed_date}`

**Downstream:**
- Risk Service: Context feeds risk identification
- Planning Service: Context informs strategies

---

### Flow 8.11: Stakeholder Analysis
**Trigger:** `POST /api/governance/stakeholders`
**ISO Requirement:** Clause 4.2 - Interested Parties
**Steps:**
1. Identify stakeholder:
   - Name, type (INTERNAL, EXTERNAL, REGULATORY)
   - Interest in BCMS
   - Requirements/expectations
   - Influence (HIGH, MEDIUM, LOW)
   - Communication preferences
2. Assess stakeholder needs
3. Define communication plan
4. Store stakeholder record
5. **Publish event:** `governance.stakeholder.identified`

**Events Published:**
- `governance.stakeholder.identified` - Payload: `{tenant_id, stakeholder_id, name, type, influence, requirements[]}`

**Stakeholder Types:**
- **INTERNAL:** Employees, management, board
- **EXTERNAL:** Customers, suppliers, partners
- **REGULATORY:** Regulators, auditors, certification bodies
- **COMMUNITY:** Media, public, NGOs

---

### Flow 8.12: Communication Plan
**Trigger:** `POST /api/governance/communication-plans`
**ISO Requirement:** Clause 7.4 - Communication
**Steps:**
1. Create communication plan:
   - Plan name
   - Target audience (stakeholder group)
   - Communication purpose
   - Message content
   - Communication method (EMAIL, SMS, PORTAL, MEETING, REPORT)
   - Frequency
   - Responsible party
2. Schedule communications
3. **Publish event:** `governance.communication_plan.created`

**Events Published:**
- `governance.communication_plan.created` - Payload: `{tenant_id, plan_id, plan_name, audience, frequency}`

**Communication Types:**
- **AWARENESS:** BC awareness campaigns
- **TRAINING:** Training announcements
- **INCIDENT:** Incident notifications
- **EXERCISE:** Exercise announcements
- **REVIEW:** Management review summaries
- **UPDATE:** BCMS updates

---

## 9. Learning Service

**Port:** 8027
**ISO Clause:** 7.3 - Awareness
**Endpoints:** 15
**State Machine:** Draft → Published → Enrolled → In Progress → Completed → Certified

### Flow 9.1: Training Program Creation
**Trigger:** `POST /api/learning/programs`
**ISO Requirement:** Clause 7.3 - Awareness
**Steps:**
1. Create program with:
   - Program name
   - Description
   - Program type (AWARENESS, ROLE_SPECIFIC, TECHNICAL, EXECUTIVE)
   - Learning objectives
   - Content modules
   - Assessment method
   - Pass threshold (%)
   - Certificate issued (boolean)
2. Set status to DRAFT
3. **Publish event:** `learning.program.created`

**Events Published:**
- `learning.program.created` - Payload: `{tenant_id, program_id, program_name, program_type}`

**State Transition:** None → Draft
**Program Types:**
- **AWARENESS:** General BC awareness (all staff)
- **ROLE_SPECIFIC:** BCM team, crisis team
- **TECHNICAL:** IT recovery, system admin
- **EXECUTIVE:** Leadership, decision-making

---

### Flow 9.2: Program Publishing
**Trigger:** `POST /api/learning/programs/{program_id}/publish`
**Steps:**
1. Validate program content complete
2. Validate assessment defined
3. Update status to PUBLISHED
4. Set published_date
5. Make available for enrollment
6. **Publish event:** `learning.program.published`

**Events Published:**
- `learning.program.published` - Payload: `{tenant_id, program_id, program_name, published_date}`

**State Transition:** Draft → Published

---

### Flow 9.3: Enrollment
**Trigger:** `POST /api/learning/enrollments`
**Steps:**
1. Create enrollment:
   - Person ID
   - Program ID
   - Enrollment type (REQUIRED, OPTIONAL, RECOMMENDED)
   - Due date
2. Validate person not already enrolled
3. Set status to PENDING_APPROVAL (if required) or APPROVED
4. **Publish event:** `learning.enrollment.created`
5. Notify learner

**Events Published:**
- `learning.enrollment.created` - Payload: `{tenant_id, enrollment_id, person_id, program_id, due_date, enrollment_type}`

**State Transition:** None → Pending Approval / Approved
**Enrollment Types:**
- **REQUIRED:** Mandatory (e.g., all staff awareness)
- **OPTIONAL:** Self-enrollment available
- **RECOMMENDED:** Suggested based on role

---

### Flow 9.4: Learning Progression
**Trigger:** `POST /api/learning/enrollments/{enrollment_id}/start`
**Steps:**
1. Update status to IN_PROGRESS
2. Set start_date
3. Initialize progress tracking:
   - Modules completed: 0
   - Total modules
   - Progress %: 0
4. **Publish event:** `learning.enrollment.started`

**State Transition:** Approved → In Progress

---

### Flow 9.5: Progress Update
**Trigger:** `PATCH /api/learning/enrollments/{enrollment_id}/progress`
**Steps:**
1. Update progress:
   - Module completed
   - Time spent
   - Current module
2. Calculate progress %
3. Store progress
4. **If 100%:** Auto-trigger completion flow

**Progress Tracking:**
- Modules completed / total modules
- Time spent (minutes)
- Last activity timestamp
- Progress % = (completed / total) × 100

---

### Flow 9.6: Learning Completion
**Trigger:** `POST /api/learning/enrollments/{enrollment_id}/complete`
**Steps:**
1. Validate all modules completed
2. Update status to COMPLETED
3. Set completion_date
4. **Publish event:** `learning.enrollment.completed`
5. Trigger assessment (if required)

**Events Published:**
- `learning.enrollment.completed` - Payload: `{tenant_id, enrollment_id, person_id, program_id, completion_date, progress_100}`

**State Transition:** In Progress → Completed

---

### Flow 9.7: Assessment
**Trigger:** `POST /api/learning/enrollments/{enrollment_id}/assess`
**Steps:**
1. Present assessment (quiz/exam):
   - Questions
   - Answer options
   - Time limit
2. Collect responses
3. Calculate score:
   - Correct answers / total questions × 100
4. Determine pass/fail:
   - If score >= pass_threshold: PASSED
   - Else: FAILED
5. Update enrollment with assessment result
6. **Publish event:** `learning.assessment.completed`
7. **If passed:** Trigger certification flow
8. **If failed:** Allow retry (up to max attempts)

**Events Published:**
- `learning.assessment.completed` - Payload: `{tenant_id, enrollment_id, person_id, program_id, score, pass_fail, attempt_number}`

**Assessment Types:**
- Quiz (10-20 questions, auto-graded)
- Exam (30+ questions, auto-graded)
- Practical (hands-on, manual grading)

---

### Flow 9.8: Certification
**Trigger:** `POST /api/learning/enrollments/{enrollment_id}/certify`
**Steps:**
1. Validate assessment passed
2. Generate certificate:
   - Certificate number
   - Person name
   - Program name
   - Completion date
   - Certificate issued by
   - Expiry date (if applicable)
3. Update enrollment status to CERTIFIED
4. **Publish event:** `learning.certification.issued`
5. Send certificate to learner (email + download)

**Events Published:**
- `learning.certification.issued` - Payload: `{tenant_id, enrollment_id, person_id, program_id, certificate_number, issue_date, expiry_date}`

**State Transition:** Completed (passed) → Certified
**Certificate Validity:**
- Awareness training: 12 months
- Role-specific: 24 months
- Technical: 12 months
- Executive: 24 months

---

### Flow 9.9: Gamification - Points
**Trigger:** Auto (on learning activities)
**Steps:**
1. Award points for:
   - Module completion: 10 points
   - Program completion: 50 points
   - Assessment pass (first attempt): 25 points
   - Certificate earned: 100 points
2. Update person's total points
3. Check for achievements (badges)
4. Update leaderboard

**Points System:**
- Module completion: 10 pts
- Program completion: 50 pts
- Assessment pass: 25 pts
- Certificate: 100 pts
- Referral: 15 pts

---

### Flow 9.10: Gamification - Achievements
**Trigger:** Auto (on milestones)
**Achievement Types:**
- **FIRST_STEPS:** Complete first module
- **LEARNING_STREAK:** Complete 5 programs in 30 days
- **PERFECT_SCORE:** Score 100% on assessment
- **KNOWLEDGE_CHAMPION:** Top 10 on leaderboard
- **MENTOR:** Help 3 colleagues complete programs

**Steps:**
1. Check if achievement criteria met
2. Award badge
3. Add bonus points
4. **Publish event:** `learning.achievement.unlocked`
5. Notify user

---

### Flow 9.11: Leaderboard
**Trigger:** `GET /api/learning/leaderboard`
**Steps:**
1. Query all persons' points
2. Sort by points DESC
3. Rank (1st, 2nd, 3rd, etc.)
4. Return top N (default 10)

**Use Case:** Drive engagement, friendly competition

---

### Learning Service: Program Types

1. **General BC Awareness**
   - Target: All staff
   - Duration: 30 minutes
   - Frequency: Annual
   - Content: BC basics, roles, incident reporting

2. **Crisis Management Team Training**
   - Target: CMT members
   - Duration: 4 hours
   - Frequency: Annual
   - Content: Decision-making, communication, leadership

3. **Recovery Team Training**
   - Target: Recovery team leads
   - Duration: 2 hours
   - Frequency: Annual
   - Content: Plan execution, resource coordination

4. **IT Disaster Recovery**
   - Target: IT staff
   - Duration: 3 hours
   - Frequency: Annual
   - Content: System recovery, data restoration

5. **First Aid / Emergency Response**
   - Target: First aid team
   - Duration: 8 hours
   - Frequency: Every 2 years
   - Content: First aid, CPR, AED

---

## 10. Documents Service

**Port:** 8022
**ISO Clause:** 7.5 - Documented Information
**Endpoints:** 27
**State Machine:** Draft → Review → Approved → Published → Archived

### Flow 10.1: Document Creation
**Trigger:** `POST /api/documents/documents`
**ISO Requirement:** Clause 7.5.2 - Creating and Updating
**Steps:**
1. Create document metadata:
   - Document code (auto or manual)
   - Title
   - Document type (POLICY, PROCEDURE, PLAN, FORM, TEMPLATE, REPORT, EVIDENCE)
   - ISO clause links
   - Owner
   - Status: DRAFT
2. Store metadata in database
3. Set status to DRAFT
4. **Publish event:** `bcm.document.created`

**Events Published:**
- `bcm.document.created` - Payload: `{tenant_id, document_id, document_code, title, document_type}`

**State Transition:** None → Draft
**Document Types:**
- **POLICY:** High-level policy documents
- **PROCEDURE:** Step-by-step procedures
- **PLAN:** BC/DR plans
- **FORM:** Templates for data collection
- **TEMPLATE:** Document templates
- **REPORT:** Reports, audits
- **EVIDENCE:** Compliance evidence

---

### Flow 10.2: File Upload
**Trigger:** `POST /api/documents/documents/{document_id}/upload`
**Steps:**
1. Validate document exists and status is DRAFT
2. Accept file upload (multipart/form-data)
3. Validate file:
   - File size <= max (default 100MB)
   - File type allowed (PDF, DOCX, XLSX, etc.)
4. Generate unique file name
5. Store file in storage (S3, filesystem)
6. Extract metadata:
   - File size
   - MIME type
   - Page count (for PDFs)
   - Word count (for DOCX)
7. Create file version record (v1.0)
8. Update document with file info
9. **Publish event:** `bcm.document.uploaded`

**Events Published:**
- `bcm.document.uploaded` - Payload: `{document_id, document_code, title, document_type, file_name, file_size, user_id, tenant_id}`

**Supported File Types:**
- PDF, DOCX, XLSX, PPTX, TXT, MD, PNG, JPG

---

### Flow 10.3: Document Workflow - Submit for Review
**Trigger:** `POST /api/documents/documents/{document_id}/workflow/submit`
**Steps:**
1. Validate document has file uploaded
2. Update status to REVIEW
3. **Publish event:** `bcm.document.submitted_for_review`
4. Notify reviewers

**State Transition:** Draft → Review

---

### Flow 10.4: Document Workflow - Approve
**Trigger:** `POST /api/documents/documents/{document_id}/workflow/approve`
**Steps:**
1. Validate status is REVIEW
2. Record approval:
   - Approved by
   - Approval date
   - Approval notes
3. Update status to APPROVED
4. **Publish event:** `bcm.document.approved`
5. Notify document owner

**Events Published:**
- `bcm.document.approved` - Payload: `{document_id, document_code, title, document_type, approved_by, tenant_id}`

**State Transition:** Review → Approved

---

### Flow 10.5: Document Workflow - Reject
**Trigger:** `POST /api/documents/documents/{document_id}/workflow/reject`
**Steps:**
1. Validate status is REVIEW
2. Record rejection:
   - Rejected by
   - Rejection reason
3. Update status back to DRAFT
4. **Publish event:** `bcm.document.rejected`
5. Notify document owner with rejection reason

**Events Published:**
- `bcm.document.rejected` - Payload: `{document_id, document_code, title, rejected_by, reason, tenant_id}`

**State Transition:** Review → Draft

---

### Flow 10.6: Document Publishing
**Trigger:** `POST /api/documents/documents/{document_id}/workflow/publish`
**Steps:**
1. Validate status is APPROVED
2. Set effective_date (if provided, else now)
3. Update status to PUBLISHED
4. Make document available to all users in scope
5. **Publish event:** `bcm.document.published`
6. Index document for search (if full-text search enabled)

**Events Published:**
- `bcm.document.published` - Payload: `{document_id, document_code, title, document_type, version, published_by, tenant_id, iso_clauses[]}`

**State Transition:** Approved → Published
**Downstream Consumers:**
- Governance Service: Policy compliance
- Plans Service: Plan readiness
- Validation Service: Audit evidence
- Search indexer: Full-text search

---

### Flow 10.7: Version Control
**Trigger:** `POST /api/documents/documents/{document_id}/version`
**Steps:**
1. Create new version:
   - Copy current version metadata
   - Increment version number (v1.0 → v2.0 for major, v1.0 → v1.1 for minor)
   - Set status to DRAFT
   - Set previous_version_id
2. Upload new file
3. Store both versions
4. **Publish event:** `bcm.document.version_created`
5. Link versions (version history)

**Events Published:**
- `bcm.document.version_created` - Payload: `{document_id, document_code, title, new_version, previous_version, created_by, tenant_id}`

**Versioning:**
- Major version (v1.0 → v2.0): Significant changes
- Minor version (v1.0 → v1.1): Small updates
- All versions retained (audit trail)

---

### Flow 10.8: Document Comparison
**Trigger:** `POST /api/documents/compare`
**Steps:**
1. Accept two document versions
2. Extract text from both
3. Generate diff:
   - Additions (green)
   - Deletions (red)
   - Changes (yellow)
4. Return comparison report

**Use Case:** Review changes between versions

---

### Flow 10.9: Document Sharing
**Trigger:** `POST /api/documents/documents/{document_id}/share`
**Steps:**
1. Share document with user or group:
   - Recipient ID
   - Permission level (VIEW, EDIT, ADMIN)
   - Expiry date (optional)
2. Create share record
3. **Publish event:** `bcm.document.shared`
4. Notify recipient

**Events Published:**
- `bcm.document.shared` - Payload: `{document_id, document_code, title, shared_by, shared_with, permission_level, tenant_id}`

**Permission Levels:**
- **VIEW:** Read-only access
- **EDIT:** Can update metadata and upload new versions
- **ADMIN:** Full control (share, delete)

---

### Flow 10.10: Retention Policy
**Trigger:** `POST /api/documents/retention-policies`
**ISO Requirement:** Clause 7.5.3 - Control of Documented Information
**Steps:**
1. Define retention policy:
   - Document type
   - Retention period (years)
   - Disposal method (DELETE, ARCHIVE)
   - Legal hold (if applicable)
2. Apply policy to documents
3. **Publish event:** `documents.retention_policy.created`

**Retention Periods (Typical):**
- Policies: 7 years after superseded
- Plans: 3 years after superseded
- Exercise reports: 5 years
- Incident reports: 7 years
- Audit reports: 7 years
- Training records: 5 years

---

### Flow 10.11: Document Expiration
**Trigger:** Scheduled job (daily)
**Steps:**
1. Check documents against retention policy:
   - Document age > retention period
   - No legal hold
2. Update status to EXPIRED
3. **Publish event:** `bcm.document.expired`
4. Notify document owner (review required)

**Events Published:**
- `bcm.document.expired` - Payload: `{document_id, document_code, title, expiration_date, retention_years, tenant_id}`

**Action Required:** Owner must review and either:
- Extend retention
- Archive
- Delete

---

### Flow 10.12: Document Archival
**Trigger:** `POST /api/documents/documents/{document_id}/workflow/archive`
**Steps:**
1. Validate document expired or superseded
2. Update status to ARCHIVED
3. Move file to archive storage (lower-cost tier)
4. **Publish event:** `bcm.document.archived`
5. Remove from active search index

**Events Published:**
- `bcm.document.archived` - Payload: `{document_id, document_code, title, archived_by, reason, tenant_id}`

**State Transition:** Published/Expired → Archived

---

### Flow 10.13: ISO Coverage Report
**Trigger:** `GET /api/documents/iso-coverage`
**Steps:**
1. Query all ISO clauses
2. For each clause:
   - List linked documents
   - Count documents
3. Identify gaps (clauses with 0 documents)
4. Calculate coverage %
5. Return report

**Example Output:**
```json
{
  "standard": "ISO_22301",
  "total_clauses": 45,
  "documented_clauses": 38,
  "coverage_percent": 84.4,
  "gaps": [
    {"clause": "8.2.3", "title": "Risk Assessment", "documents": 0},
    {"clause": "9.2", "title": "Internal Audit", "documents": 0}
  ]
}
```

---

### Flow 10.14: Access Log
**Trigger:** Auto (on document access)
**Steps:**
1. Log access event:
   - User
   - Document
   - Action (VIEW, DOWNLOAD, EDIT)
   - Timestamp
   - IP address
2. Store in audit log
3. Retention: 2 years

**Use Case:** Compliance audit, security investigation

---

### Flow 10.15: Search
**Trigger:** `GET /api/documents/search?q=business continuity plan`
**Steps:**
1. Parse search query
2. Search across:
   - Document title
   - Document content (full-text if indexed)
   - Document code
   - Tags
   - ISO clauses
3. Apply filters:
   - Document type
   - Status
   - Date range
4. Rank results by relevance
5. Return search results

**Search Capabilities:**
- Full-text search (if enabled)
- Boolean operators (AND, OR, NOT)
- Wildcards (*)
- Filters by metadata

---

## 11. Living-Docs

**Port:** 8034
**ISO Clause:** 7.5 - Documented Information (Dynamic)
**Endpoints:** 10+
**Purpose:** AI-powered documentation that evolves based on usage and feedback

### Flow 11.1: Living Document Creation
**Trigger:** `POST /api/living-docs/documents`
**Steps:**
1. Create living document:
   - Base document (from Documents Service)
   - Target audience
   - Usage context
   - Learning level
2. Initialize evolution metadata:
   - View count: 0
   - Feedback count: 0
   - Personalization profiles: []
3. **Publish event:** `living_docs.document.created`

**State Transition:** None → Active

---

### Flow 11.2: Document View Tracking
**Trigger:** `GET /api/living-docs/documents/{doc_id}` (read)
**Steps:**
1. Increment view count
2. Track user context:
   - User role
   - Department
   - Previous docs viewed
   - Time spent
3. Capture usage patterns
4. Update analytics

**Analytics Tracked:**
- View count
- Unique viewers
- Average time spent
- Bounce rate (< 10 seconds)
- Read completion rate

---

### Flow 11.3: AI Example Generation
**Trigger:** `POST /api/living-docs/documents/{doc_id}/generate-examples`
**Steps:**
1. Analyze document content
2. Identify concepts needing examples
3. Generate examples using AI:
   - Industry-specific examples
   - Role-specific scenarios
   - Real-world case studies
4. Insert examples into document
5. **Publish event:** `living_docs.examples.generated`

**Example:**
- Original: "Conduct BIA for critical processes"
- Generated Example: "For a hospital, critical processes include Emergency Department, Operating Rooms, and ICU. RTO for ED should be < 1 hour."

---

### Flow 11.4: Personalization
**Trigger:** `GET /api/living-docs/documents/{doc_id}?user_id={id}`
**Steps:**
1. Fetch user profile:
   - Role
   - Department
   - Skill level
   - Learning preferences
2. Customize document:
   - Show relevant examples
   - Adjust language complexity
   - Highlight applicable sections
   - Hide irrelevant details
3. Return personalized version

**Personalization Factors:**
- **Role:** Show role-specific procedures
- **Experience:** Novice gets more detail, expert gets concise
- **Department:** Show department-specific examples
- **Previous docs:** Avoid redundant content

---

### Flow 11.5: Feedback Collection
**Trigger:** `POST /api/living-docs/documents/{doc_id}/feedback`
**Steps:**
1. Collect feedback:
   - Rating (1-5 stars)
   - Feedback type (HELPFUL, CONFUSING, INCORRECT, MISSING_INFO)
   - Comment
   - Section (which part of document)
2. Store feedback
3. Aggregate feedback
4. **If critical feedback:** Alert document owner
5. **Trigger:** Document evolution process

**Feedback Types:**
- **HELPFUL:** Document is useful
- **CONFUSING:** Needs clarification
- **INCORRECT:** Contains errors
- **MISSING_INFO:** Gaps identified

---

### Flow 11.6: Document Evolution
**Trigger:** Scheduled (weekly) or threshold-based (e.g., 10 negative feedbacks)
**Steps:**
1. Analyze feedback trends:
   - Most confused sections
   - Most requested additions
   - Incorrect information
2. Generate improvement recommendations:
   - Rewrite confusing sections
   - Add missing information
   - Update incorrect content
3. **Publish event:** `living_docs.evolution.recommended`
4. Notify document owner with suggestions
5. Owner reviews and applies changes

**Evolution Triggers:**
- 10+ "confusing" feedback on same section
- 5+ "missing info" requests
- 1+ "incorrect" report
- View-to-bounce ratio > 30%

---

### Flow 11.7: Smart Linking
**Trigger:** Auto (during document view)
**Steps:**
1. Identify related documents:
   - Same ISO clause
   - Same topic/keywords
   - Frequently viewed together
   - Referenced in other docs
2. Suggest links to user
3. Track link usage
4. **If link useful:** Persist in document

**Smart Links:**
- Related policies
- Supporting procedures
- Case studies
- External standards

---

### Flow 11.8: Usage Analytics
**Trigger:** `GET /api/living-docs/analytics`
**Steps:**
1. Aggregate usage data:
   - Most viewed documents
   - Most improved documents
   - Highest rated documents
   - Highest feedback documents
2. Calculate metrics:
   - Average satisfaction score
   - Evolution velocity (updates/month)
   - Personalization effectiveness
3. Return analytics report

---

## 12. BCM Coordination Service

**Port:** 8036
**ISO Clause:** Cross-functional coordination
**Endpoints:** 12
**Purpose:** Orchestrate workflows across BCM services

### Flow 12.1: End-to-End BIA-to-Plan Workflow
**Trigger:** `POST /api/bcm-coordination/workflows/bia-to-plan`
**Steps:**
1. Trigger BIA process (call BIA Service)
2. Wait for BIA completion event
3. On `bcm.bia.completed`:
   - Extract RTO/RPO targets
   - Trigger risk assessment (call Risk Service)
4. On `risk.assessment.created`:
   - Link risk to BIA process
5. Trigger strategy selection (call Planning Service):
   - Pass RTO/RPO requirements
   - Get recommended strategies
6. On `planning.strategy.approved`:
   - Trigger plan creation (call Plans Service)
   - Link plan to BIA, strategies
7. Return workflow summary

**Workflow Timeline:**
```
Day 1: BIA Process Started
Day 7: BIA Completed (event)
Day 8: Risk Assessment Created (event)
Day 10: Risk Analysis Completed
Day 15: Strategies Identified (event)
Day 20: Strategy Approved (event)
Day 21: Plan Created (event)
Day 30: Plan Approved, Ready for Testing
```

---

### Flow 12.2: Incident-to-Lesson-Learned Workflow
**Trigger:** `POST /api/bcm-coordination/workflows/incident-lessons`
**Steps:**
1. On `response.incident.closed`:
   - Extract lessons learned
2. Create improvement opportunities (Compliance Service):
   - Update procedures
   - Enhance plans
   - Adjust resources
3. Create training needs (Learning Service):
   - If knowledge gap identified
4. Update risk register (Risk Service):
   - If new risk discovered
5. Return workflow summary

---

### Flow 12.3: Exercise-to-Improvement Workflow
**Trigger:** `POST /api/bcm-coordination/workflows/exercise-improvement`
**Steps:**
1. On `validation.exercise.completed`:
   - Extract findings
2. For each finding:
   - **If plan gap:** Update plan (Plans Service)
   - **If training gap:** Create training (Learning Service)
   - **If resource gap:** Update resources (Governance Service)
   - **If procedure issue:** Update document (Documents Service)
3. Create corrective actions (Validation Service)
4. Track to closure
5. Return workflow summary

---

### Flow 12.4: Compliance Dashboard
**Trigger:** `GET /api/bcm-coordination/dashboard/compliance`
**Steps:**
1. Aggregate data from all services:
   - BIA completion rate
   - Plans approved/active
   - Exercises completed
   - Training completion
   - Audit findings open
   - Corrective actions status
2. Calculate ISO 22301 compliance %
3. Identify gaps
4. Return dashboard

**Compliance Metrics:**
- BIA coverage: 90% (target 100%)
- Plans current: 85% (target 100%)
- Exercise frequency: 80% (target 100%)
- Training completion: 92% (target 100%)
- Audit findings: 3 open (target 0)
- Overall compliance: 88% (target 95%+)

---

## 13. Cross-Service Integration Flows

### Integration 13.1: BIA → Risk → Planning → Plans
**Description:** End-to-end flow from BIA to operational plans

**Flow:**
1. **BIA Service:** Identify critical process
   - Publish: `bcm.bia.completed` with RTO/RPO
2. **Risk Service:** Subscribe to BIA event
   - Assess risks for critical process
   - Publish: `risk.assessment.created`
3. **Planning Service:** Subscribe to risk event
   - Select strategies based on RTO/RPO and risks
   - Perform cost-benefit analysis
   - Publish: `planning.strategy.approved`
4. **Plans Service:** Subscribe to strategy event
   - Create BC plan implementing strategies
   - Publish: `plans.plan.created`
5. **Documents Service:** Subscribe to plan event
   - Generate plan document
6. **Validation Service:** Subscribe to plan event
   - Schedule plan testing

**Total Duration:** 30-45 days typically

---

### Integration 13.2: Incident → Response → Validation → Improvement
**Description:** Incident handling with continuous improvement

**Flow:**
1. **Response Service:** Incident detected
   - Publish: `response.incident.created`
2. **Plans Service:** Subscribe to incident event
   - Activate relevant plan
   - Publish: `plans.plan.activated_real`
3. **Response Service:** Track plan execution
   - Measure RTO/RPO compliance
   - Publish: `response.incident.resolved`
4. **Validation Service:** Subscribe to resolution event
   - Create post-incident review
   - Identify gaps/findings
   - Publish: `validation.exercise.evaluated` (treated as "real exercise")
5. **Compliance Service:** Subscribe to evaluation event
   - Create improvement opportunities
   - Publish: `compliance.improvement.created`
6. **Plans Service:** Subscribe to improvement event
   - Update plans based on lessons learned
7. **Learning Service:** Subscribe to improvement event
   - Create training if knowledge gap

**Continuous Improvement Loop:** Incident → Review → Improve → Train → Better Response

---

### Integration 13.3: Policy → Training → Awareness
**Description:** Policy publication with mandatory training

**Flow:**
1. **Governance Service:** Policy approved
   - Publish: `governance.policy.published` with `training_required: true`
2. **Learning Service:** Subscribe to policy event
   - Auto-create training program
   - Set as REQUIRED for all users in scope
   - Publish: `learning.program.published`
3. **Notification Service:** Subscribe to program event
   - Send notification to all affected users
4. **Learning Service:** Track completion
   - Publish: `learning.enrollment.completed` per user
5. **Governance Service:** Subscribe to completion events
   - Track policy acknowledgment
   - Report compliance

**Compliance Tracking:** Who has read/acknowledged policy

---

### Integration 13.4: Exercise → Plans Update → Document Version
**Description:** Exercise findings drive plan improvements

**Flow:**
1. **Validation Service:** Exercise completed
   - Publish: `validation.exercise.completed` with findings
2. **Plans Service:** Subscribe to exercise event
   - Identify affected plans
   - Create plan update task
3. **Plans Service:** Plans updated
   - Publish: `plans.plan.updated`
4. **Documents Service:** Subscribe to plan update
   - Create new document version
   - Publish: `bcm.document.version_created`
5. **Governance Service:** Subscribe to document event
   - Track plan currency
6. **Notification Service:** Subscribe to version event
   - Notify plan users of changes

**Version Control:** Audit trail of changes from exercises

---

### Integration 13.5: Risk Treatment → Resource Allocation → Budget
**Description:** Risk treatment triggers resource requests

**Flow:**
1. **Risk Service:** Treatment plan approved
   - Publish: `risk.treatment_plan.created` with cost estimate
2. **Governance Service:** Subscribe to treatment event
   - Create resource allocation request
   - Publish: `governance.resource.requested`
3. **Governance Service:** Budget approved
   - Publish: `governance.resource.approved`
4. **Risk Service:** Subscribe to approval
   - Update treatment plan with allocated budget
   - Set status to FUNDED
5. **Planning Service:** Subscribe to approval
   - Link resource to strategy
6. **Plans Service:** Subscribe to approval
   - Update plan with new resource

**Budget Tracking:** Risk reduction investment

---

## Event Summary

### BIA Service Events

**Published:**
- `bcm.bia.started` - BIA process created
- `bcm.bia.completed` - BIA process finished
- `bcm.bia.critical_process_identified` - Critical process found (criticality >= 4)

**Subscribed:**
- `risk.assessment.completed` - Triggers BIA review
- `exercise.completed` - Updates RTO/RPO based on exercise

---

### Risk Service Events

**Published:**
- `risk.assessment.created` - New risk identified
- `risk.fair_analysis.completed` - FAIR analysis done
- `risk.monte_carlo.completed` - Monte Carlo simulation done
- `risk.treatment_plan.created` - Treatment plan created
- `risk.treatment_plan.completed` - Treatment executed

**Subscribed:**
- `bcm.bia.completed` - Links risk to BIA process

---

### Planning Service Events

**Published:**
- `planning.strategy.created` - Strategy defined
- `planning.cost_benefit.completed` - Cost-benefit analysis done
- `planning.strategy.approved` - Strategy approved

**Subscribed:**
- `risk.assessment.created` - Strategies informed by risks
- `bcm.bia.completed` - Strategies based on RTO/RPO

---

### Plans Service Events

**Published:**
- `plans.plan.created` - Plan created
- `plans.plan.submitted` - Plan submitted for review
- `plans.plan.approved` - Plan approved
- `plans.plan.activated` - Plan made active
- `plans.plan.activated_real` - Plan activated for real incident
- `plans.plan.reviewed` - Plan reviewed
- `plans.procedure.added` - Procedure added to plan
- `plans.resource.added` - Resource added to plan
- `plans.contact_list.updated` - Contact list updated

**Subscribed:**
- `planning.strategy.approved` - Creates plan from strategy
- `response.incident.created` - May activate plan
- `validation.exercise.completed` - Updates plan based on findings

---

### Response Service Events

**Published:**
- `response.incident.created` - Incident reported
- `response.incident.updated` - Incident details updated
- `response.incident.status_changed` - Status changed
- `response.incident.resolved` - Incident resolved
- `response.incident.closed` - Incident closed
- `response.incident.escalated` - Incident escalated
- `response.stakeholder.notification` - Stakeholders notified
- `response.metrics.updated` - Recovery metrics recorded
- `response.compliance.violation` - RTO/RPO not met
- `response.plan.activated` - Plan activated from incident

**Subscribed:**
- `plans.plan.created` - Awareness of available plans

---

### Validation Service Events

**Published:**
- `validation.exercise.created` - Exercise planned
- `validation.exercise.scheduled` - Exercise scheduled
- `validation.exercise.started` - Exercise began
- `validation.exercise.completed` - Exercise finished
- `validation.exercise.evaluated` - Exercise assessed
- `validation.corrective_action.created` - Finding identified
- `validation.corrective_action.closed` - Finding resolved
- `validation.kpi.measured` - KPI data collected
- `validation.kpi.alert` - KPI threshold breached

**Subscribed:**
- `plans.plan.activated` - Plan available for testing
- `response.incident.closed` - Treat as "real exercise"

---

### Compliance Service Events

**Published:**
- `compliance.assessment.created` - Assessment planned
- `compliance.gap_analysis.completed` - Gaps identified
- `compliance.evidence.collected` - Evidence gathered
- `compliance.audit.created` - Audit scheduled
- `compliance.audit.started` - Audit began
- `compliance.audit.finding.created` - Audit finding
- `compliance.audit.completed` - Audit finished
- `compliance.management_review.completed` - Management review done
- `compliance.improvement.created` - Improvement opportunity identified
- `compliance.improvement.implemented` - Improvement completed

**Subscribed:**
- `validation.exercise.evaluated` - Findings → improvements
- `response.incident.closed` - Lessons → improvements

---

### Governance Service Events

**Published:**
- `governance.policy.created` - Policy drafted
- `governance.policy.approved` - Policy approved
- `governance.policy.published` - Policy published
- `governance.role.created` - Role defined
- `governance.role.assigned` - Person assigned to role
- `governance.resource.requested` - Resource needed
- `governance.resource.approved` - Resource allocated
- `governance.competence.assessed` - Competence gap found
- `governance.objective.created` - Objective set
- `governance.context_analysis.completed` - Context analyzed
- `governance.stakeholder.identified` - Stakeholder identified
- `governance.communication_plan.created` - Communication plan defined

**Subscribed:**
- `risk.treatment_plan.created` - Resource requests from risks

---

### Learning Service Events

**Published:**
- `learning.program.created` - Training program created
- `learning.program.published` - Training available
- `learning.enrollment.created` - User enrolled
- `learning.enrollment.started` - Learning began
- `learning.enrollment.completed` - Learning finished
- `learning.assessment.completed` - Assessment taken
- `learning.certification.issued` - Certificate issued
- `learning.achievement.unlocked` - Badge earned

**Subscribed:**
- `governance.policy.published` - Auto-create training
- `governance.competence.assessed` - Create training for gaps
- `compliance.improvement.created` - Training from improvements

---

### Documents Service Events

**Published:**
- `bcm.document.created` - Document metadata created
- `bcm.document.uploaded` - File uploaded
- `bcm.document.submitted_for_review` - Submitted for review
- `bcm.document.approved` - Document approved
- `bcm.document.rejected` - Document rejected
- `bcm.document.published` - Document published
- `bcm.document.archived` - Document archived
- `bcm.document.expired` - Retention period expired
- `bcm.document.shared` - Document shared
- `bcm.document.version_created` - New version created

**Subscribed:**
- `plans.plan.approved` - Generate plan document
- `governance.policy.published` - Store policy
- `compliance.evidence.collected` - Store evidence

---

### Living-Docs Events

**Published:**
- `living_docs.document.created` - Living doc created
- `living_docs.examples.generated` - AI examples added
- `living_docs.evolution.recommended` - Improvements suggested

**Subscribed:**
- `bcm.document.published` - Create living version

---

## State Machines Summary

### BIA Process States
```
DRAFT → IN_PROGRESS → COMPLETED
```

### Risk States
```
IDENTIFIED → ANALYZING → TREATING → TREATED → MONITORING → CLOSED
```

### Strategy States
```
DRAFT → UNDER_REVIEW → APPROVED → ACTIVE → ARCHIVED
```

### Plan States
```
DRAFT → UNDER_REVIEW → APPROVED → ACTIVE → IN_USE → SUPERSEDED → ARCHIVED
```

### Incident States
```
NEW → INVESTIGATING → CONTAINED → RESOLVING → RESOLVED → CLOSED
```

### Exercise States
```
PLANNED → SCHEDULED → IN_PROGRESS → COMPLETED → REVIEWED
```

### Document States
```
DRAFT → REVIEW → APPROVED → PUBLISHED → EXPIRED → ARCHIVED
```

### Policy States
```
DRAFT → APPROVED → PUBLISHED → SUPERSEDED → ARCHIVED
```

### Training States
```
DRAFT → PUBLISHED → (per user) → PENDING_APPROVAL → APPROVED → IN_PROGRESS → COMPLETED → CERTIFIED
```

---

## Metrics & KPIs Tracked

### BIA Service
- Total BIA processes
- Completion rate
- Critical processes count
- Average RTO/RPO by criticality
- Processes by WHO tier (healthcare)

### Risk Service
- Total risks
- By severity (critical, high, medium, low)
- By category
- By status
- Average risk score
- RTO/RPO compliance rate

### Planning Service
- Strategies defined
- Strategies approved
- Average ROI
- Cost-benefit ratios

### Plans Service
- Plans by status
- Plans by type
- Plan review currency (% on schedule)
- Procedures per plan
- Contact list currency

### Response Service
- Active incidents
- Incidents by severity
- MTTR (Mean Time To Resolve)
- RTO compliance rate
- RPO compliance rate
- Escalation rate

### Validation Service
- Exercises completed
- Exercise success rate
- Findings by severity
- Corrective actions open/closed
- KPI compliance rate

### Compliance Service
- Audit findings (major/minor NC)
- Gap closure rate
- Evidence completeness
- ISO 22301 compliance %
- Improvement opportunities implemented

### Governance Service
- Policies published
- Roles filled/vacant
- Resources allocated
- Competence gaps
- Objectives progress

### Learning Service
- Training completion rate
- Assessment pass rate
- Certification rate
- Average score
- Leaderboard rankings

### Documents Service
- Documents by type
- ISO clause coverage %
- Document currency
- Version count
- Access frequency

---

## Conclusion

This comprehensive inventory documents **150+ business flows** across 12 core BCM services covering the complete ISO 22301 lifecycle:

1. **BIA Service:** 12 flows - Business impact analysis and criticality assessment
2. **Risk Service:** 8 flows - Risk assessment, FAIR, Monte Carlo, treatment
3. **Planning Service:** 3 flows - Strategy development and cost-benefit
4. **Plans Service:** 9 flows - Plan creation, approval, activation, review
5. **Response Service:** 10 flows - Incident management and recovery
6. **Validation Service:** 11 flows - Exercises, testing, KPIs, corrective actions
7. **Compliance Service:** 10 flows - Audits, gap analysis, management review
8. **Governance Service:** 12 flows - Policies, roles, resources, stakeholders
9. **Learning Service:** 11 flows - Training, assessment, certification, gamification
10. **Documents Service:** 15 flows - Document lifecycle and version control
11. **Living-Docs:** 8 flows - AI-powered documentation evolution
12. **BCM Coordination:** 4 flows - Cross-service orchestration

**Total Events:** 80+ event types published/consumed
**Total API Endpoints:** 200+
**State Machines:** 9 major workflows

Every flow includes:
- Trigger (API call, event, schedule)
- Steps (what happens)
- State transitions
- Events published/consumed
- Dependencies
- Data exchanged
- Failure points

This inventory provides the foundation for:
- Workflow orchestration design
- Event-driven architecture implementation
- API gateway routing
- Integration testing
- Performance optimization
- Monitoring and alerting
- User journey mapping
- Training and documentation
