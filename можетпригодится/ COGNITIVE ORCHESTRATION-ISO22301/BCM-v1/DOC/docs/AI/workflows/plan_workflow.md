# Plan Workflow - Business Continuity Plan Generation

## Workflow Overview

The Plan Generation workflow enables the AI Assistant to create comprehensive, ISO 22301-compliant Business Continuity Plans (BCPs) based on current BIA data, organizational context, and best practices. The workflow ensures plans are tailored, actionable, and integrated with existing BCM processes.

## Trigger Conditions

### Automatic Triggers
- **Plans Up-to-date < 70%**: System detects outdated or missing plans
- **Plan Age > 180 days**: Existing plan requires refresh
- **Post-BIA Generation**: New BIA completed, plan needed
- **Process Criticality Change**: Process upgraded to critical level
- **Post-Incident Review**: Incident reveals plan gaps
- **Regulatory Change**: New compliance requirements affecting plans

### User-Initiated Triggers  
- Direct request: "Generate plan for [process]"
- Planning cycle: "Update our business continuity plans"
- New process: "Create BCP for new service"

## Workflow Steps

### Step 1: Plan Prerequisites Validation
```python
# Validate prerequisites before plan generation
def validate_plan_prerequisites(process_id, tenant_id):
    prerequisites = {
        "bia_current": check_bia_status(process_id, tenant_id),
        "process_defined": check_process_definition(process_id, tenant_id),
        "stakeholders_identified": check_stakeholder_mapping(process_id),
        "dependencies_mapped": check_dependency_analysis(process_id),
        "rto_rpo_defined": check_recovery_objectives(process_id)
    }
    
    missing_prereqs = [k for k, v in prerequisites.items() if not v]
    
    if missing_prereqs:
        return suggest_prerequisite_completion(missing_prereqs)
    
    return proceed_with_plan_generation()
```

**Assistant Response for Missing Prerequisites**:
```
## Plan Generation Prerequisites Check

❌ **Missing Requirements for EHR System Plan**:
- Business Impact Analysis outdated (250 days)
- Recovery objectives not defined
- Dependency analysis incomplete

🔧 **Required Actions**:
[Action Button: Update BIA First] (process_id=EHR)
[Action Button: Define Recovery Objectives] (process_id=EHR)

💡 **Why This Matters**: Effective BCPs require current impact analysis and clear recovery targets to ensure relevant and actionable procedures.
```

### Step 2: Plan Scope and Template Selection
```python
# Determine plan scope and template based on process characteristics
def determine_plan_scope(process_info, bia_data, organizational_context):
    plan_scope = {
        "plan_type": "business_continuity_plan",  # bcp|drp|crisis_management|pandemic
        "complexity": "standard",  # simple|standard|complex
        "template": "iso_22301_healthcare",
        "sections": [],
        "stakeholders": [],
        "integration_points": []
    }
    
    # Determine plan complexity
    if bia_data.rto <= 4 and len(bia_data.dependencies) > 5:
        plan_scope["complexity"] = "complex"
    elif bia_data.rto > 24 and len(bia_data.dependencies) <= 3:
        plan_scope["complexity"] = "simple"
    
    # Select appropriate template
    if organizational_context.industry == "healthcare":
        plan_scope["template"] = f"iso_22301_{organizational_context.industry}"
    
    # Define required sections
    base_sections = [
        "executive_summary", "scope_objectives", "roles_responsibilities",
        "activation_procedures", "response_procedures", "recovery_procedures",
        "communication_plans", "resource_requirements", "testing_maintenance"
    ]
    
    if process_info.has_it_components:
        base_sections.extend(["it_recovery", "data_backup_restore"])
    
    if process_info.customer_facing:
        base_sections.append("customer_communication")
    
    plan_scope["sections"] = base_sections
    return plan_scope
```

### Step 3: Plan Content Generation
```python
# Generate comprehensive BCP content through Orchestrator
POST /api/recommendations
{
    "context": "plan_generation",
    "data": {
        "action_type": "plan_generation",
        "process_id": "EHR",
        "plan_scope": {
            "plan_type": "business_continuity_plan",
            "template": "iso_22301_healthcare",
            "complexity": "complex",
            "rto_hours": 4,
            "rpo_minutes": 30,
            "criticality": 4.8
        },
        "content_requirements": {
            "include_procedures": true,
            "include_checklists": true,
            "include_contact_lists": true,
            "include_resource_inventory": true,
            "compliance_standards": ["iso_22301", "hipaa", "hitech"]
        },
        "customization": {
            "organization_size": "medium",  # small|medium|large|enterprise
            "industry_sector": "healthcare",
            "geographic_scope": "single_site",  # single_site|multi_site|global
            "existing_plans": get_existing_plan_references()
        }
    },
    "tenant_id": tenant_id,
    "user_id": user_id
}
```

**Plan Generation Progress Tracking**:
```
## BCP Generation In Progress - EHR System

⏳ **Current Phase**: Content generation and customization
📋 **Template**: ISO 22301 Healthcare Standard
⏱️ **Progress**: 65% complete (estimated 8 minutes remaining)

**Generation Status**:
✅ Executive summary and scope definition
✅ Roles and responsibilities matrix  
✅ Activation criteria and procedures
🔄 Recovery procedures and checklists (current)
⚪ Communication templates
⚪ Resource requirements and contacts
⚪ Testing and maintenance procedures

**Customizations Applied**:
- Healthcare industry regulations (HIPAA, HITECH)
- 4-hour RTO requirements integrated
- Patient safety priority protocols
- Electronic health record specific procedures
```

### Step 4: Plan Content Review and Enhancement
```python
# Review generated plan content for completeness and accuracy
def review_generated_plan(plan_content, process_info, bia_data):
    review_checks = {
        "completeness": assess_section_completeness(plan_content),
        "accuracy": validate_technical_accuracy(plan_content, process_info),
        "compliance": check_regulatory_compliance(plan_content),
        "actionability": assess_procedure_clarity(plan_content),
        "consistency": check_cross_references(plan_content),
        "customization": verify_organization_specificity(plan_content)
    }
    
    improvement_areas = []
    for check, result in review_checks.items():
        if result.score < 0.8:  # 80% threshold
            improvement_areas.append({
                "area": check,
                "score": result.score,
                "recommendations": result.recommendations
            })
    
    if improvement_areas:
        return suggest_plan_refinement(improvement_areas)
    
    return approve_plan_for_review()
```

### Step 5: Plan Integration and Cross-References
```python
# Integrate plan with existing BCM documentation
def integrate_plan_with_bcm_system(plan_content, process_id):
    integration_tasks = [
        link_to_bia_documentation(process_id),
        update_master_plan_index(),
        cross_reference_related_plans(),
        update_contact_directories(),
        link_resource_inventories(),
        update_exercise_schedules()
    ]
    
    # Check for conflicts with existing plans
    conflicts = detect_plan_conflicts(plan_content)
    if conflicts:
        return resolve_plan_conflicts(conflicts)
    
    # Update plan hierarchy
    update_plan_hierarchy({
        "master_plan": get_master_bcm_plan(),
        "business_area_plans": get_business_area_plans(),
        "process_specific_plans": [plan_content],
        "support_plans": get_support_plans()
    })
```

### Step 6: Plan Validation and Approval Workflow
```python
# Prepare plan for stakeholder review and approval
POST /api/recommendations
{
    "context": "plan_review",
    "data": {
        "action_type": "plan_validation",
        "plan_id": generated_plan_id,
        "validation_type": "comprehensive",
        "reviewers": [
            {"role": "process_owner", "required": true},
            {"role": "bcm_manager", "required": true}, 
            {"role": "it_manager", "required": process_info.has_it_components},
            {"role": "legal_compliance", "required": process_info.regulatory_requirements}
        ],
        "review_criteria": [
            "technical_accuracy", "procedural_clarity", "resource_availability",
            "compliance_alignment", "integration_completeness"
        ],
        "approval_workflow": "parallel_review"  # parallel|sequential|hierarchical
    }
}
```

**Plan Review Presentation**:
```
## BCP Draft Ready for Review - EHR System

### 📋 Plan Overview
- **Document**: Business Continuity Plan - EHR System v1.0
- **Pages**: 42 pages with 12 detailed procedures
- **Recovery Time**: 4 hours maximum downtime
- **Scope**: Electronic health records, patient data access, clinical workflows

### 🎯 Key Features Generated
✅ **Activation Procedures**: Clear triggers and escalation matrix
✅ **Recovery Checklists**: Step-by-step technical and operational procedures  
✅ **Communication Templates**: Staff, patient, and stakeholder notifications
✅ **Resource Requirements**: Personnel, technology, and vendor contacts
✅ **Compliance Integration**: HIPAA and ISO 22301 alignment verified

### 👥 Required Reviews
- **Process Owner** (Dr. Sarah Chen): Technical accuracy validation
- **BCM Manager** (Mike Rodriguez): ISO 22301 compliance review
- **IT Manager** (Jennifer Kim): Technical recovery procedures
- **Legal Compliance** (David Park): Regulatory requirement validation

### 📊 Quality Metrics
- **Completeness Score**: 94% (ISO 22301 requirements)
- **Clarity Rating**: 4.7/5.0 (procedure actionability)
- **Customization Level**: High (organization-specific details)

### 📅 Next Steps
[Action Button: Send for Review] (reviewers=all_required)
[Action Button: Schedule Tabletop Exercise] (plan_id={plan_id})
[Action Button: Preview Full Document] (format=pdf)
```

## Plan Content Structure

### Generated Plan Sections
1. **Executive Summary**
   - Plan purpose and scope
   - Critical success factors
   - Recovery objectives summary

2. **Scope and Objectives**
   - Business process coverage
   - RTO/RPO targets
   - Success criteria

3. **Roles and Responsibilities**
   - Crisis management team structure
   - Individual role definitions
   - Decision-making authorities

4. **Activation Procedures**
   - Incident classification criteria
   - Escalation procedures
   - Plan activation decision matrix

5. **Response Procedures**
   - Immediate response actions (0-4 hours)
   - Damage assessment procedures
   - Safety and security protocols

6. **Recovery Procedures**
   - System restoration steps
   - Data recovery procedures
   - Service resumption criteria

7. **Communication Plans**
   - Internal communication protocols
   - External stakeholder messaging
   - Media and public communication

8. **Resource Requirements**
   - Personnel requirements
   - Technology and equipment needs
   - Vendor and supplier contacts

9. **Testing and Maintenance**
   - Exercise schedules and types
   - Plan review and update procedures
   - Training requirements

### Plan Customization Logic
```python
def customize_plan_content(base_template, process_info, bia_data, org_context):
    customizations = {}
    
    # Industry-specific adjustments
    if org_context.industry == "healthcare":
        customizations.update({
            "regulatory_sections": ["hipaa_compliance", "patient_safety"],
            "specialized_procedures": ["medical_device_backup", "patient_notification"],
            "escalation_contacts": ["medical_director", "privacy_officer"]
        })
    
    # RTO-based procedure complexity
    if bia_data.rto <= 2:
        customizations["procedure_detail"] = "high_detail"
        customizations["automation_emphasis"] = True
    elif bia_data.rto > 24:
        customizations["procedure_detail"] = "standard"
        customizations["manual_procedures"] = True
    
    # Dependency-based recovery sequences
    if len(bia_data.dependencies) > 5:
        customizations["recovery_sequencing"] = "complex_dependencies"
        customizations["include_dependency_matrix"] = True
    
    return apply_customizations(base_template, customizations)
```

## Activity Logging and Tracking

### Plan Generation Events
```python
plan_workflow_events = [
    {
        "event_type": "assistant.activity",
        "data": {
            "intent": "plan_generate_draft",
            "workflow": "plan_generation", 
            "phase": "initiation",
            "reason": "EHR plan outdated (250 days), new BIA completed",
            "prerequisites_check": {
                "bia_current": True,
                "rto_rpo_defined": True,
                "stakeholders_mapped": True
            },
            "plan_scope": {
                "process_id": "EHR",
                "plan_type": "business_continuity_plan",
                "complexity": "complex",
                "template": "iso_22301_healthcare"
            },
            "status": "initiated"
        }
    },
    {
        "event_type": "assistant.activity",
        "data": {
            "intent": "plan_generate_draft",
            "workflow": "plan_generation",
            "phase": "content_generated",
            "generation_metrics": {
                "sections_completed": 9,
                "procedures_created": 12,
                "checklists_generated": 8,
                "customizations_applied": 15,
                "compliance_checks_passed": 6
            },
            "quality_scores": {
                "completeness": 0.94,
                "clarity": 0.89,
                "compliance": 0.97,
                "customization": 0.91
            },
            "next_actions": [
                {"intent": "plan_review_process", "priority": "high"},
                {"intent": "schedule_exercise", "priority": "medium"}
            ],
            "status": "content_complete"
        }
    }
]
```

## Error Handling and Fallback Procedures

### Common Error Scenarios
1. **Missing BIA Data**:
   - Redirect to BIA workflow completion
   - Provide generic plan template with gaps noted
   - Schedule BIA and plan generation sequence

2. **Template Not Available**:
   - Fall back to generic ISO 22301 template
   - Note customization limitations
   - Suggest template development for future use

3. **Content Generation Timeout**:
   - Provide partially generated sections
   - Offer manual completion guidance
   - Schedule retry with reduced scope

4. **Stakeholder Unavailable for Review**:
   - Implement delegated review process
   - Extend review timeline
   - Proceed with available reviewers + noted limitations

### Fallback Plan Generation
```python
def provide_fallback_guidance():
    return {
        "message": "Plan generation service temporarily unavailable",
        "immediate_actions": [
            "Download ISO 22301 BCP template from document library",
            "Use BIA data to populate recovery objectives section",
            "Customize template with organization-specific information",
            "Schedule stakeholder review session for content validation"
        ],
        "templates_available": [
            "iso_22301_bcp_template.docx",
            "bcp_checklist_template.xlsx",
            "communication_plan_template.docx",
            "resource_inventory_template.xlsx"
        ],
        "guidance_documents": [
            "bcp_development_guide.pdf",
            "iso_22301_section_8_requirements.pdf",
            "plan_customization_examples.pdf"
        ],
        "support_escalation": "bcm_administrator@organization.com"
    }
```

## Integration Touchpoints

### Pre-Plan Generation
- **BIA Workflow**: Current impact analysis required
- **Process Management**: Process definition and ownership
- **Stakeholder Management**: Role identification and contact information
- **Resource Inventory**: Available recovery resources and capabilities

### Post-Plan Generation  
- **Exercise Scheduling**: Plan validation through testing
- **Training Management**: Staff awareness and procedure training
- **Document Management**: Plan storage, version control, and distribution
- **KPI Tracking**: Plan currency and effectiveness metrics

### Continuous Integration
- **Change Management**: Plan updates for process or organizational changes
- **Incident Management**: Plan activation and effectiveness feedback
- **Audit Management**: Plan compliance and improvement opportunities
- **Management Review**: Plan performance and strategic alignment

## Success Metrics and Quality Gates

### Plan Quality Indicators
- **Completeness Score**: All required ISO 22301 sections included
- **Clarity Rating**: Procedures are actionable and unambiguous  
- **Customization Level**: Organization-specific details incorporated
- **Compliance Alignment**: Regulatory requirements addressed
- **Integration Score**: Connectivity with related BCM documents

### Workflow Performance Metrics
- **Generation Time**: Target < 30 minutes for standard complexity
- **Review Completion**: Target < 5 business days for stakeholder validation
- **Quality Pass Rate**: Plans meeting quality thresholds on first generation
- **Stakeholder Satisfaction**: Review feedback and approval rates

This workflow ensures the generation of high-quality, compliant, and actionable business continuity plans that integrate seamlessly with the organization's broader BCM framework.
