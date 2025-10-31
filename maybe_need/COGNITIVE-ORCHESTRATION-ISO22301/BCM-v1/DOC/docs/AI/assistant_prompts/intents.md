# AI Assistant Intent Map - PDCA Conductor

## Core Intent Classification

The BCM PDCA Conductor recognizes and responds to the following intents, each mapped to specific PDCA cycle phases and platform capabilities.

## Primary Navigation Intents

### `check_status`
**Purpose**: Assess current BCM system state and recommend next PDCA step
**PDCA Phase**: All phases (entry point)
**Triggers**: 
- User asks "What should I do next?"
- User requests system overview
- User wants current BCM status
- Session initialization

**Data Requirements**:
- Current KPIs via `/bcm/kpi`
- Recent events via `/api/events/history`
- Pending AI decisions via `/api/ai/decisions/pending`

**Decision Logic**:
```python
if critical_incidents > 0:
    return suggest_intent("incident_draft_response")
elif overdue_capa > 0:
    return suggest_intent("audit_summarize")
elif bia_coverage < 0.8:
    return suggest_intent("plan_generate_bia")
elif plans_up_to_date < 0.7:
    return suggest_intent("plan_generate_draft")
elif days_since_exercise > 180:
    return suggest_intent("schedule_exercise")
else:
    return show_status_dashboard()
```

**Response Format**:
```
## Current Status
📊 **KPIs**: BIA Coverage: 64%, Plans Current: 72%, CAPA On-time: 90%
🔥 **Issues**: 2 overdue CAPA items, EHR plan 185 days old

## Recommended Next Steps
[Action Button: Generate BCP Draft] (process_id=EHR)
[Action Button: Summarize Audit Evidence] (finding_ids=[1,3,7])
```

### `show_next_step`
**Purpose**: Provide guidance on optimal next PDCA action
**PDCA Phase**: Transition between phases
**Triggers**:
- User completed previous action
- User asks "What's next?"
- After workflow completion events

**Integration**:
- Correlates with recent `assistant.activity` events
- Considers workflow progression state
- Factors in compliance deadlines

---

## PLAN Phase Intents

### `plan_generate_bia`
**Purpose**: Initiate Business Impact Analysis for critical processes
**PDCA Phase**: Plan
**Triggers**:
- BIA coverage < 80%
- New critical process identified
- BIA older than 365 days
- User requests "analyze business impact"

**Orchestrator Integration**:
```python
POST /api/recommendations
{
    "context": "bia_analysis",
    "data": {
        "action_type": "bia_computation",
        "process_id": process_id,
        "priority": "high" if criticality >= 4 else "normal"
    },
    "tenant_id": tenant_id,
    "user_id": user_id
}
```

**Expected Events**: `bcm.bia.computation_started`, `bcm.bia.completed`

**Activity Logging**:
```python
{
    "event_type": "assistant.activity",
    "data": {
        "intent": "plan_generate_bia",
        "reason": f"BIA coverage at {bia_coverage}%, missing for process {process_id}",
        "actions": [{"type": "bia_computation", "process_id": process_id}],
        "status": "requested"
    }
}
```

### `plan_generate_draft`
**Purpose**: Generate Business Continuity Plan drafts
**PDCA Phase**: Plan
**Triggers**:
- Plans older than 180 days
- New BIA completed
- User requests plan creation/update
- Process criticality changed

**Parameters**:
- `process_id` (required): Target business process
- `plan_type` (optional): "bcp", "drp", "crisis_management"
- `template_id` (optional): Organization template preference

**Orchestrator Integration**:
```python
POST /api/recommendations
{
    "context": "plan_generation",
    "data": {
        "action_type": "plan_generation",
        "process_id": process_id,
        "plan_type": plan_type,
        "rationale": "plan_outdated_185_days"
    }
}
```

### `plan_context_analysis`
**Purpose**: Analyze organizational context for BCM planning
**PDCA Phase**: Plan
**Triggers**:
- New tenant onboarding
- Organizational changes detected
- User requests context review
- Stakeholder requirements unclear

---

## DO Phase Intents

### `schedule_exercise`
**Purpose**: Schedule BCM exercises and simulations
**PDCA Phase**: Do
**Triggers**:
- No exercise in last 180 days
- New plan requires validation
- User requests exercise scheduling
- Post-incident validation needed

**Exercise Types**:
- `tabletop`: Discussion-based scenario
- `walkthrough`: Step-by-step procedure validation
- `simulation`: Full-scale exercise with resource activation
- `component_test`: Individual system/process testing

**Integration Pattern**:
```python
POST /api/recommendations
{
    "context": "exercise_scheduling",
    "data": {
        "action_type": "exercise_schedule",
        "exercise_type": exercise_type,
        "process_id": process_id,
        "participants": participant_roles,
        "scenario": scenario_template
    }
}
```

### `incident_draft_response`
**Purpose**: Generate incident response procedures and checklists
**PDCA Phase**: Do
**Triggers**:
- New incident opened (`bcm.incident.opened`)
- High/critical severity incidents
- Missing response procedures
- User requests response guidance

**Severity-Based Logic**:
- **Critical**: Immediate response checklist + escalation
- **High**: Standard response with timeline
- **Medium**: Reference procedures + monitoring
- **Low**: Documentation + lessons learned

**Response Generation**:
```python
POST /api/recommendations
{
    "context": "incident_response",
    "data": {
        "action_type": "incident_response",
        "incident_id": incident_id,
        "severity": severity_level,
        "affected_processes": process_list,
        "response_type": "immediate|planned|post_incident"
    }
}
```

### `training_schedule`
**Purpose**: Schedule BCM awareness and response training
**PDCA Phase**: Do
**Triggers**:
- Training completion < 85%
- New personnel onboarded
- Post-exercise training gaps identified
- Annual training cycle due

---

## CHECK Phase Intents

### `audit_summarize`
**Purpose**: Analyze audit findings and generate CAPA recommendations
**PDCA Phase**: Check
**Triggers**:
- New audit findings available
- Overdue CAPA items
- User requests audit analysis
- Compliance review cycle

**Evidence Analysis**:
```python
POST /api/audit/summarize
{
    "context": "audit_evidence",
    "data": {
        "action_type": "evidence_analysis",
        "finding_ids": finding_ids,
        "audit_scope": iso_22301_clauses,
        "severity_filter": "major|minor|observation"
    }
}
```

**CAPA Generation Logic**:
- **Major Findings**: Immediate CAPA with 30-day timeline
- **Minor Findings**: Standard CAPA with 90-day timeline
- **Observations**: Improvement recommendations

### `documents_analyze`
**Purpose**: Analyze compliance documents for gaps and improvements
**PDCA Phase**: Check
**Triggers**:
- New documents uploaded
- Document review cycle due
- User requests document analysis
- Compliance score below threshold

**Document Processor Integration**:
```python
GET /api/documents/search?tenant_id={tenant_id}&document_type=bcm_policy
POST /api/documents/{doc_id}/analysis
{
    "analysis_type": "iso_22301_compliance",
    "focus_areas": ["clause_4", "clause_8", "clause_9"],
    "compare_against": "industry_standards"
}
```

### `kpi_calculate`
**Purpose**: Calculate and trend BCM key performance indicators
**PDCA Phase**: Check
**Triggers**:
- Monthly KPI review cycle
- User requests metrics
- KPI thresholds breached
- Management review preparation

**KPI Calculations**:
- **BIA Coverage**: (Processes with current BIA / Total critical processes) × 100
- **Plans Up-to-date**: (Plans < 180 days old / Total plans) × 100
- **CAPA On-time**: (CAPA completed by due date / Total CAPA) × 100
- **Exercise Completion**: (Processes exercised < 180 days / Total processes) × 100
- **Training Completion**: (Staff trained / Total staff) × 100

---

## ACT Phase Intents

### `capa_track`
**Purpose**: Monitor and escalate Corrective and Preventive Actions
**PDCA Phase**: Act
**Triggers**:
- CAPA due dates approaching
- Overdue CAPA items
- User requests CAPA status
- Management review preparation

### `management_review_prepare`
**Purpose**: Prepare management review dashboards and summaries
**PDCA Phase**: Act
**Triggers**:
- Quarterly review cycle
- User requests MR preparation
- KPI trends require attention
- Strategic decisions needed

### `system_improve`
**Purpose**: Identify and recommend BCMS improvements
**PDCA Phase**: Act
**Triggers**:
- Recurring issues identified
- Best practice opportunities
- User requests improvement analysis
- Maturity assessment completed

---

## Utility and Support Intents

### `explain_iso22301`
**Purpose**: Provide ISO 22301 guidance and education
**Triggers**:
- User asks about standards
- Compliance questions
- Process explanations needed

### `tenant_switch`
**Purpose**: Switch between tenant contexts (multi-tenant support)
**Triggers**:
- User has multiple tenant access
- Context switching required

### `help_workflow`
**Purpose**: Provide workflow guidance and tutorials
**Triggers**:
- User needs process guidance
- First-time feature usage
- Error recovery situations

---

## Intent Recognition Patterns

### Natural Language Patterns
```python
INTENT_PATTERNS = {
    "check_status": [
        "what should i do", "current status", "overview", "dashboard",
        "what's next", "priorities", "recommendations"
    ],
    "plan_generate_draft": [
        "create plan", "generate bcp", "draft plan", "update procedures",
        "business continuity plan", "disaster recovery"
    ],
    "incident_draft_response": [
        "incident response", "emergency procedures", "crisis management",
        "what to do in emergency", "response checklist"
    ],
    "audit_summarize": [
        "audit findings", "compliance gaps", "capa", "corrective actions",
        "audit summary", "findings analysis"
    ],
    "documents_analyze": [
        "analyze document", "compliance check", "document review",
        "policy analysis", "gap analysis"
    ],
    "schedule_exercise": [
        "schedule exercise", "tabletop", "simulation", "drill",
        "test plan", "exercise planning"
    ]
}
```

### Context-Aware Recognition
- **Recent Events**: Weight intents based on recent `bcm.*` events
- **KPI State**: Prioritize intents addressing current KPI gaps
- **User History**: Learn from user interaction patterns
- **Temporal Context**: Adjust suggestions based on review cycles

### Multi-Intent Handling
- **Sequential Intents**: Guide through multi-step workflows
- **Parallel Intents**: Handle simultaneous process improvements
- **Dependent Intents**: Ensure prerequisite completion (e.g., BIA before plan generation)

---

## Intent Execution Pipeline

### 1. Intent Recognition
- Parse user input using NLP patterns
- Analyze current system state
- Weight intent probability based on context

### 2. Parameter Extraction
- Extract required parameters (process_id, severity, etc.)
- Validate tenant access permissions
- Set default values where appropriate

### 3. Orchestrator Integration
- Map intent to appropriate API endpoint
- Format request payload with context
- Execute action via Orchestrator/EventBus/Document Processor

### 4. Event Monitoring
- Watch for expected confirmation events
- Timeout handling with fallback messaging
- Correlation ID tracking for activity logging

### 5. Response Generation
- Format user-friendly response
- Include next step recommendations
- Provide action buttons for immediate execution

### 6. Activity Logging
- Log all assistant activities
- Include decision rationale and confidence
- Maintain correlation tracking for audit trails
