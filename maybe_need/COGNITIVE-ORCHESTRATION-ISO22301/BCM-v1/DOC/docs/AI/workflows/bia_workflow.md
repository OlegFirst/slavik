# BIA Workflow - Business Impact Analysis

## Workflow Overview

The Business Impact Analysis (BIA) workflow enables the AI Assistant to guide users through comprehensive business impact assessment, identifying critical processes, dependencies, and recovery requirements according to ISO 22301 standards.

## Trigger Conditions

### Automatic Triggers
- **BIA Coverage < 80%**: System detects insufficient BIA coverage across critical processes
- **New Critical Process**: Process criticality rating updated to 4 or 5
- **BIA Expiry**: Existing BIA older than 365 days requires refresh
- **Post-Incident**: Major incidents reveal gaps in impact understanding
- **Compliance Review**: Annual ISO 22301 compliance assessment

### User-Initiated Triggers
- Direct request: "Analyze business impact for [process]"
- Planning phase: "We need to update our BIA"
- Context analysis: "Help us understand critical processes"

## Workflow Steps

### Step 1: Process Identification and Validation
```python
# Assistant checks current process inventory
GET /bcm/processes?tenant_id={tenant_id}&criticality_min=3

# Validate process exists and user has access
if process_id not in accessible_processes:
    return suggest_process_selection()

# Check existing BIA status
existing_bia = get_process_bia(process_id, tenant_id)
if existing_bia and existing_bia.age_days < 180:
    return confirm_bia_update_needed()
```

**Assistant Response**:
```
## BIA Analysis Required

📊 **Current BIA Status**: 
- EHR System: BIA outdated (250 days)
- Pharmacy Operations: No BIA found
- Patient Records: BIA current

🎯 **Recommended Action**: Generate BIA for EHR System
**Rationale**: Critical process (Level 5) without current business impact assessment

[Action Button: Start BIA Analysis] (process_id=EHR)
```

### Step 2: Impact Assessment Data Gathering
```python
# Orchestrator call for BIA computation
POST /api/recommendations
{
    "context": "bia_analysis",
    "data": {
        "action_type": "bia_computation", 
        "process_id": "EHR",
        "analysis_scope": "full",  # full|update|quick
        "methodology": "iso_22301",
        "stakeholders": ["process_owner", "it_manager", "finance"],
        "impact_categories": [
            "financial", "operational", "regulatory", 
            "reputational", "customer_service"
        ]
    },
    "tenant_id": tenant_id,
    "user_id": user_id
}
```

**Expected Orchestrator Activities**:
- Stakeholder notification and questionnaire distribution
- Process mapping and dependency analysis
- Financial impact calculations
- Recovery time objectives (RTO) assessment
- Recovery point objectives (RPO) determination

### Step 3: BIA Computation Monitoring
```python
# Monitor for BIA computation events
expected_events = [
    "bcm.bia.computation_started",
    "bcm.bia.stakeholder_responses_collected", 
    "bcm.bia.impact_analysis_complete",
    "bcm.bia.draft_generated",
    "bcm.bia.ready_for_review"
]

# Wait for completion with timeout
await monitor_events(expected_events, timeout=1800)  # 30 minutes
```

**Progress Updates**:
```
## BIA Computation In Progress

⏳ **Status**: Collecting stakeholder responses (2/5 completed)
📋 **Next**: Financial impact analysis
⏱️ **ETA**: 15 minutes

**Completed Steps**:
✅ Process mapping identified 12 key dependencies
✅ Regulatory requirements analyzed
⚪ Awaiting: Finance team input on revenue impacts
⚪ Pending: Customer service impact assessment
```

### Step 4: BIA Results Analysis and Validation
```python
# Retrieve BIA computation results
bia_results = get_bia_results(decision_id, tenant_id)

# Analyze results for completeness and accuracy
validation_checks = {
    "rto_defined": check_rto_values(bia_results),
    "rpo_defined": check_rpo_values(bia_results), 
    "financial_impact_quantified": check_financial_data(bia_results),
    "dependencies_mapped": check_dependency_completeness(bia_results),
    "stakeholder_consensus": check_stakeholder_agreement(bia_results)
}

# Identify gaps or inconsistencies
if not all(validation_checks.values()):
    return suggest_bia_refinement(validation_checks)
```

**BIA Results Presentation**:
```
## BIA Analysis Complete - EHR System

### 📊 Critical Impact Metrics
- **RTO**: 4 hours (maximum acceptable downtime)
- **RPO**: 30 minutes (maximum data loss acceptable)
- **Peak Financial Impact**: $45,000/hour
- **Affected Customers**: 2,500 patients/day
- **Criticality Score**: 4.8/5.0

### 🔗 Key Dependencies Identified
1. **Primary Database Server** (Critical)
2. **Network Infrastructure** (Critical)
3. **Identity Management System** (High)
4. **Backup Systems** (High)

### ⚠️ Risk Factors
- Single point of failure in database architecture
- Limited redundancy in network connectivity
- Staff dependency on EHR for all patient interactions

### 📋 Recommended Actions
[Action Button: Generate Recovery Plan] (process_id=EHR, rto=4h, rpo=30min)
[Action Button: Schedule BIA Review] (review_date=+90days)
```

### Step 5: BIA Documentation and Integration
```python
# Generate BIA documentation
POST /api/recommendations
{
    "context": "bia_documentation",
    "data": {
        "action_type": "generate_bia_report",
        "process_id": process_id,
        "bia_results": bia_results,
        "format": "iso_22301_compliant",
        "include_sections": [
            "executive_summary", "impact_analysis", 
            "dependency_mapping", "recovery_requirements",
            "recommendations", "review_schedule"
        ]
    }
}

# Update KPIs
update_kpi_calculation({
    "bia_coverage": calculate_bia_coverage(),
    "processes_analyzed": get_analyzed_process_count(),
    "avg_rto": calculate_average_rto(),
    "critical_dependencies": count_critical_dependencies()
})
```

### Step 6: Follow-up Actions and Integration
```python
# Determine next logical steps based on BIA results
next_actions = []

if bia_results.rto <= 8:  # Critical RTO requirement
    next_actions.append({
        "intent": "plan_generate_draft",
        "priority": "high",
        "rationale": "Critical RTO requires formal recovery plan"
    })

if len(bia_results.critical_dependencies) > 3:
    next_actions.append({
        "intent": "schedule_exercise", 
        "priority": "medium",
        "rationale": "Complex dependencies require validation testing"
    })

# Update process criticality if BIA reveals new insights
if bia_results.criticality_score != current_process.criticality:
    suggest_criticality_update(process_id, bia_results.criticality_score)
```

## Workflow Decision Points

### BIA Scope Determination
```python
def determine_bia_scope(process_info, existing_bia, trigger_reason):
    if trigger_reason == "new_process":
        return "full"  # Comprehensive first-time analysis
    elif trigger_reason == "post_incident":
        return "focused"  # Incident-specific impact areas
    elif existing_bia.age_days > 365:
        return "update"  # Refresh existing analysis
    elif process_info.criticality >= 4:
        return "full"  # High-criticality requires comprehensive analysis
    else:
        return "quick"  # Standard periodic review
```

### Stakeholder Selection Logic
```python
def select_bia_stakeholders(process_id, process_info):
    stakeholders = ["process_owner"]  # Always required
    
    if process_info.has_financial_impact:
        stakeholders.append("finance_manager")
    
    if process_info.has_it_components:
        stakeholders.append("it_manager")
    
    if process_info.customer_facing:
        stakeholders.append("customer_service_manager")
    
    if process_info.regulatory_requirements:
        stakeholders.append("compliance_officer")
    
    return stakeholders
```

### RTO/RPO Validation Rules
```python
def validate_rto_rpo(process_id, proposed_rto, proposed_rpo):
    validation_results = {}
    
    # Industry benchmarks for healthcare
    if process_info.industry == "healthcare":
        if process_info.type == "patient_care" and proposed_rto > 4:
            validation_results["rto_warning"] = "Patient care processes typically require RTO ≤ 4 hours"
    
    # Technical feasibility
    if proposed_rpo < get_backup_frequency(process_id):
        validation_results["rpo_error"] = "RPO cannot be shorter than backup frequency"
    
    # Cost-benefit analysis
    estimated_cost = calculate_recovery_cost(proposed_rto, proposed_rpo)
    annual_risk = calculate_annual_risk_exposure(process_id)
    
    if estimated_cost > annual_risk * 0.1:  # 10% threshold
        validation_results["cost_warning"] = "Recovery costs may exceed risk exposure"
    
    return validation_results
```

## Activity Logging

### BIA Workflow Events
```python
assistant_activity_events = [
    {
        "event_type": "assistant.activity",
        "data": {
            "intent": "plan_generate_bia",
            "workflow": "bia_analysis",
            "phase": "initiation",
            "reason": "BIA coverage at 64%, EHR process missing current BIA",
            "actions": [
                {
                    "type": "orchestrator_call",
                    "endpoint": "/api/recommendations",
                    "params": {"process_id": "EHR", "action_type": "bia_computation"}
                }
            ],
            "expected_outcome": "Current BIA for critical process",
            "success_metrics": ["bia_completion_rate", "stakeholder_participation"],
            "status": "initiated"
        }
    },
    {
        "event_type": "assistant.activity", 
        "data": {
            "intent": "plan_generate_bia",
            "workflow": "bia_analysis",
            "phase": "completion",
            "results": {
                "process_id": "EHR",
                "rto_hours": 4,
                "rpo_minutes": 30,
                "criticality_score": 4.8,
                "stakeholders_engaged": 5,
                "dependencies_identified": 12
            },
            "follow_up_actions": [
                {"intent": "plan_generate_draft", "priority": "high"},
                {"intent": "schedule_exercise", "priority": "medium"}
            ],
            "status": "completed"
        }
    }
]
```

## Error Handling and Edge Cases

### Common Error Scenarios
1. **Stakeholder Non-Response**: 
   - Timeout after 24 hours
   - Escalate to process owner
   - Proceed with available data + assumptions documented

2. **Insufficient Data**:
   - Request additional information gathering
   - Suggest phased BIA approach
   - Provide templates for missing data

3. **Conflicting Stakeholder Input**:
   - Highlight discrepancies
   - Schedule stakeholder alignment meeting
   - Use conservative estimates until resolved

4. **Technical Integration Failures**:
   - Fallback to manual BIA templates
   - Provide step-by-step guidance
   - Log technical issues for resolution

### Fallback Procedures
```python
def bia_fallback_guidance():
    return {
        "message": "BIA computation service temporarily unavailable",
        "manual_steps": [
            "1. Download BIA template from document library",
            "2. Engage stakeholders for impact assessment meeting",
            "3. Complete RTO/RPO analysis using provided worksheets",
            "4. Submit completed BIA for review and approval"
        ],
        "templates": [
            "bia_questionnaire.xlsx",
            "impact_assessment_worksheet.docx", 
            "dependency_mapping_template.xlsx"
        ],
        "support_contact": "bcm_administrator@organization.com"
    }
```

## Success Metrics and KPIs

### Workflow Performance Metrics
- **BIA Completion Time**: Target < 48 hours from initiation
- **Stakeholder Engagement**: Target > 90% response rate
- **BIA Quality Score**: Completeness + accuracy assessment
- **Follow-up Action Rate**: % of BIAs leading to next PDCA steps

### Business Impact Metrics
- **BIA Coverage**: % of critical processes with current BIA
- **Average RTO**: Across all critical processes
- **Dependency Complexity**: Average dependencies per process
- **BIA Refresh Rate**: % of BIAs updated within 12 months

This workflow ensures comprehensive, ISO 22301-compliant business impact analysis while maintaining clear guidance for users and systematic integration with the broader BCM platform.
