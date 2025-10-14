# Documents Service - Detailed Scenarios with Examples
## Living Documents & Document Management - Complete Usage Scenarios

**Service**: Documents Service (Port 8016)
**ISO Clause**: 7.5 - Documented information
**Total Scenarios**: 15
**Status**: Ready for Implementation

---

## Table of Contents

1. [Core Scenarios (6.1-6.10)](#core-scenarios)
2. [Advanced Scenarios (6.11-6.15)](#advanced-scenarios)
3. [API Reference](#api-reference)
4. [Event Flow Diagrams](#event-flow-diagrams)

---

## Core Scenarios

### 6.1 Living Documents (Auto-Updating Plans)

**Business Context**: BC plans, BIA reports, and risk registers should automatically update when underlying data changes, ensuring documents stay current

**Inputs**:
```json
{
  "document_id": "doc_bc_plan_ed_001",
  "document_type": "business_continuity_plan",
  "living_mode": "enabled",
  "update_triggers": {
    "bia_data_changes": true,
    "risk_register_changes": true,
    "contact_list_changes": true,
    "infrastructure_changes": true
  },
  "auto_update_policy": {
    "mode": "suggest_changes",
    "approval_required": true,
    "approvers": ["bcm_manager", "department_head"]
  }
}
```

**API Endpoint**: `POST /api/documents/{document_id}/living-mode/enable`

**Living Documents Architecture**:
```
Event Bus → Documents Service → Change Detection → AI Analysis → Update Suggestion
  ↓
  When event received (e.g., bia.updated):
  1. Identify affected documents
  2. Determine specific sections needing updates
  3. Generate update suggestions (AI)
  4. Create approval request
  5. Apply changes when approved
  6. Version control automatic
  ↓
Return: update_suggestions, approval_workflow_id
```

**Scenario Example - BIA Data Changes**:

**Event Received**:
```json
{
  "event": "bia.rto_updated",
  "timestamp": "2025-11-20T14:30:00Z",
  "payload": {
    "bia_id": "bia_2025_001",
    "department": "Emergency Department",
    "process": "EHR Manual Workaround",
    "old_rto": "15 minutes",
    "new_rto": "10 minutes",
    "reason": "Exercise results showed we can achieve faster activation"
  }
}
```

**Documents Service Detects Impact**:
```json
{
  "affected_documents": [
    {
      "document_id": "doc_bc_plan_ed_001",
      "document_name": "BC Plan - Emergency Department",
      "section_affected": "Section 5.2 - EHR Recovery Procedures",
      "current_content": "Activate manual EHR workaround within 15 minutes of EHR failure.",
      "trigger": "bia.rto_updated"
    },
    {
      "document_id": "doc_sla_it_services_001",
      "document_name": "IT Services SLA Document",
      "section_affected": "Appendix A - Recovery Time Objectives",
      "current_content": "EHR Recovery RTO: 15 minutes",
      "trigger": "bia.rto_updated"
    }
  ],
  "impact_analysis": {
    "documents_affected": 2,
    "sections_requiring_update": 3,
    "cascading_changes": true
  }
}
```

**AI Generates Update Suggestions** (Claude Sonnet):
```json
{
  "update_suggestions": [
    {
      "suggestion_id": "upd_001",
      "document_id": "doc_bc_plan_ed_001",
      "section": "Section 5.2 - EHR Recovery Procedures",
      "change_type": "content_update",
      "current_text": "Activate manual EHR workaround within 15 minutes of EHR failure. This includes:\n1. Notify ED staff of EHR outage (target: 2 minutes)\n2. Distribute paper patient tracking forms (target: 5 minutes)\n3. Activate manual medication ordering process (target: 10 minutes)\n4. Confirm all critical processes operational (target: 15 minutes)",
      "suggested_text": "Activate manual EHR workaround within 10 minutes of EHR failure. This includes:\n1. Notify ED staff of EHR outage (target: 2 minutes)\n2. Distribute paper patient tracking forms (target: 3 minutes)\n3. Activate manual medication ordering process (target: 7 minutes)\n4. Confirm all critical processes operational (target: 10 minutes)",
      "rationale": "RTO updated from 15 to 10 minutes based on exercise results (EX-2025-001) showing faster activation is achievable. Sub-step timings proportionally adjusted to align with new 10-minute target.",
      "confidence": 0.95,
      "requires_human_review": true,
      "review_reason": "Shortened timelines may need operational validation"
    },
    {
      "suggestion_id": "upd_002",
      "document_id": "doc_bc_plan_ed_001",
      "section": "Section 1.3 - Recovery Time Objectives Summary",
      "change_type": "table_update",
      "current_table_row": "| EHR Manual Workaround | 15 minutes | Critical | Paper-based patient tracking |",
      "suggested_table_row": "| EHR Manual Workaround | 10 minutes | Critical | Paper-based patient tracking |",
      "rationale": "Update RTO summary table to reflect new 10-minute target.",
      "confidence": 0.99,
      "requires_human_review": false,
      "review_reason": "Straightforward data update"
    },
    {
      "suggestion_id": "upd_003",
      "document_id": "doc_sla_it_services_001",
      "section": "Appendix A - Recovery Time Objectives",
      "change_type": "content_update",
      "current_text": "EHR Recovery RTO: 15 minutes",
      "suggested_text": "EHR Recovery RTO: 10 minutes (Updated Nov 2025 based on BIA review)",
      "rationale": "Align IT SLA document with updated BIA RTO for consistency.",
      "confidence": 0.97,
      "requires_human_review": true,
      "review_reason": "SLA change may have contractual implications"
    }
  ],
  "approval_workflow": {
    "workflow_id": "appr_001",
    "status": "pending_approval",
    "approvers": [
      {
        "approver": "BCM Manager (John Smith)",
        "email": "john.smith@hospital.com",
        "approval_level": "required",
        "status": "pending"
      },
      {
        "approver": "ED Director (Dr. Michael Chen)",
        "email": "michael.chen@hospital.com",
        "approval_level": "required",
        "status": "pending",
        "note": "Operational validation needed for shortened timelines"
      },
      {
        "approver": "CIO (Tom Williams)",
        "email": "tom.williams@hospital.com",
        "approval_level": "optional",
        "status": "pending",
        "note": "FYI for IT SLA implications"
      }
    ],
    "approval_deadline": "2025-11-27",
    "notification_sent": true
  }
}
```

**Approval Interface** (for BCM Manager):
```json
{
  "approval_request": {
    "request_id": "appr_001",
    "title": "Living Document Update: Emergency Department BC Plan",
    "triggered_by": "BIA RTO change (bia_2025_001)",
    "summary": "The BIA for Emergency Department has updated the EHR Manual Workaround RTO from 15 minutes to 10 minutes based on recent exercise results. This change affects 2 documents across 3 sections.",
    "changes_preview": {
      "documents_affected": 2,
      "sections_changed": 3,
      "impact": "Low-Medium (timing updates only, no structural changes)"
    },
    "suggested_changes": [
      {
        "document": "BC Plan - Emergency Department",
        "section": "5.2 - EHR Recovery Procedures",
        "change": "RTO: 15 min → 10 min (sub-steps adjusted proportionally)",
        "preview_url": "/api/documents/doc_bc_plan_ed_001/preview?suggestion=upd_001",
        "diff_view": "Available"
      },
      {
        "document": "BC Plan - Emergency Department",
        "section": "1.3 - RTO Summary Table",
        "change": "Table update: 15 min → 10 min",
        "preview_url": "/api/documents/doc_bc_plan_ed_001/preview?suggestion=upd_002"
      },
      {
        "document": "IT Services SLA",
        "section": "Appendix A",
        "change": "RTO: 15 min → 10 min (with date note)",
        "preview_url": "/api/documents/doc_sla_it_services_001/preview?suggestion=upd_003"
      }
    ],
    "approval_options": [
      {
        "option": "approve_all",
        "action": "Approve all 3 suggested changes",
        "effect": "Documents updated immediately, new version created, stakeholders notified"
      },
      {
        "option": "approve_selective",
        "action": "Select which changes to approve",
        "effect": "Only selected changes applied"
      },
      {
        "option": "reject_with_feedback",
        "action": "Reject and provide feedback for AI to revise",
        "effect": "AI generates revised suggestions based on feedback"
      },
      {
        "option": "manual_edit",
        "action": "Make manual edits instead",
        "effect": "Disable auto-update for this change, manual editing enabled"
      }
    ],
    "recommendation": {
      "ai_recommendation": "approve_all",
      "rationale": "Changes are straightforward RTO updates consistent with BIA data. No policy or structural changes. Confidence: 95%.",
      "risk_assessment": "Low risk - timing adjustments only, based on validated exercise data"
    }
  }
}
```

**After Approval**:
```json
{
  "update_applied": {
    "approval_id": "appr_001",
    "approved_by": "BCM Manager (John Smith)",
    "approved_at": "2025-11-21T09:15:00Z",
    "changes_applied": 3,
    "documents_updated": [
      {
        "document_id": "doc_bc_plan_ed_001",
        "old_version": "v2.3",
        "new_version": "v2.4",
        "changes": "Sections 1.3 and 5.2 updated (RTO: 15→10 min)",
        "change_log": "Auto-updated based on BIA bia_2025_001 RTO change. Exercise EX-2025-001 validated 10-minute achievability. Approved by BCM Manager.",
        "document_url": "/api/documents/doc_bc_plan_ed_001/v2.4"
      },
      {
        "document_id": "doc_sla_it_services_001",
        "old_version": "v1.8",
        "new_version": "v1.9",
        "changes": "Appendix A updated (EHR RTO: 15→10 min)",
        "change_log": "Auto-updated to align with BIA bia_2025_001. Approved by BCM Manager.",
        "document_url": "/api/documents/doc_sla_it_services_001/v1.9"
      }
    ],
    "notifications_sent": {
      "stakeholders": [
        "ED Director (document owner)",
        "CIO (IT SLA affected)",
        "All BC Plan subscribers (15 people)"
      ],
      "notification_content": "Emergency Department BC Plan updated (v2.4) - EHR RTO changed from 15 to 10 minutes based on recent BIA update and exercise validation."
    },
    "audit_trail": {
      "trigger_event": "bia.rto_updated",
      "ai_suggestion": "upd_001, upd_002, upd_003",
      "approver": "john.smith@hospital.com",
      "approval_timestamp": "2025-11-21T09:15:00Z",
      "changes_applied": 3,
      "version_history": "preserved"
    }
  }
}
```

**Events Published**:
```yaml
- event: document.auto_update.suggested
  payload:
    document_id: doc_bc_plan_ed_001
    trigger: bia.rto_updated
    suggestions_count: 3
    approval_required: true
  subscribers:
    - notification-service (notify approvers)
    - workflow-engine (track approval)

- event: document.version.created
  payload:
    document_id: doc_bc_plan_ed_001
    old_version: v2.3
    new_version: v2.4
    change_type: auto_update
    approver: john.smith@hospital.com
  subscribers:
    - notification-service (notify stakeholders)
    - compliance-service (log ISO 7.5 evidence)
    - audit-service (record change)
```

**Components Used**:
- Documents Service (orchestration)
- Event Bus (trigger detection)
- AI Foundation (Claude Sonnet - change analysis and suggestion)
- Workflow Engine (approval process)
- Version Control (Git-like storage)
- Notification Service (stakeholder alerts)

**Business Value**:
- **Always Current**: Documents automatically stay aligned with latest data
- **Reduced Manual Work**: No need to manually search and update all affected documents
- **Consistency**: Ensures all related documents updated together
- **Audit Trail**: Complete history of why and when documents changed
- **Intelligent**: AI suggests appropriate changes, not blind replacements

**Configuration Options**:
```json
{
  "living_document_policies": {
    "auto_approve_threshold": {
      "confidence": 0.99,
      "change_types": ["table_updates", "number_changes"],
      "max_changes_per_event": 5
    },
    "always_require_approval": {
      "document_types": ["board_approved_policies", "external_contracts"],
      "section_types": ["objectives", "scope", "responsibilities"]
    },
    "notification_preferences": {
      "immediate": ["document_owners", "primary_approvers"],
      "daily_digest": ["document_subscribers"],
      "weekly_summary": ["executives"]
    }
  }
}
```

---

### 6.2 Document Version Control

**Business Context**: Track all document changes over time, enable rollback, compare versions, maintain complete audit trail

**Inputs**:
```json
{
  "document_id": "doc_bc_plan_ed_001",
  "change_description": "Update contact list - replace retiring BCM Manager",
  "changes": {
    "section": "Appendix B - Contact List",
    "old_content": "BCM Manager: John Smith, john.smith@hospital.com, 555-0123",
    "new_content": "BCM Manager: Jane Doe, jane.doe@hospital.com, 555-0456",
    "change_type": "content_update"
  },
  "author": {
    "user_id": "user_789",
    "name": "Admin User",
    "email": "admin@hospital.com"
  },
  "change_reason": "Personnel change - John Smith retired, Jane Doe assumed BCM Manager role"
}
```

**API Endpoint**: `POST /api/documents/{document_id}/versions/create`

**Version Control Process**:
```
Git-Like Version Control:
  ↓
  1. Create snapshot of current version
  2. Apply changes to new version
  3. Generate diff report
  4. Store version metadata
  5. Update document HEAD
  6. Preserve all previous versions
  ↓
Return: new_version, diff_report, version_history
```

**Response**:
```json
{
  "document_id": "doc_bc_plan_ed_001",
  "version_created": {
    "version_id": "v2.5",
    "previous_version": "v2.4",
    "created_at": "2025-11-25T10:30:00Z",
    "created_by": "Admin User (admin@hospital.com)",
    "change_description": "Update contact list - replace retiring BCM Manager",
    "change_reason": "Personnel change - John Smith retired, Jane Doe assumed BCM Manager role",
    "document_url": "/api/documents/doc_bc_plan_ed_001/v2.5",
    "previous_url": "/api/documents/doc_bc_plan_ed_001/v2.4"
  },
  "diff_report": {
    "sections_changed": 1,
    "lines_added": 1,
    "lines_removed": 1,
    "lines_modified": 0,
    "changes": [
      {
        "section": "Appendix B - Contact List",
        "change_type": "content_replacement",
        "removed": "- BCM Manager: John Smith, john.smith@hospital.com, 555-0123",
        "added": "+ BCM Manager: Jane Doe, jane.doe@hospital.com, 555-0456",
        "context_before": "Emergency Contact List:",
        "context_after": "CMO: Dr. Sarah Johnson, sarah.johnson@hospital.com, 555-0100"
      }
    ],
    "diff_visualization_url": "/api/documents/doc_bc_plan_ed_001/diff?from=v2.4&to=v2.5"
  },
  "version_history": {
    "total_versions": 5,
    "current_version": "v2.5",
    "versions": [
      {
        "version": "v2.5",
        "date": "2025-11-25T10:30:00Z",
        "author": "Admin User",
        "description": "Update contact list - replace retiring BCM Manager",
        "status": "current"
      },
      {
        "version": "v2.4",
        "date": "2025-11-21T09:15:00Z",
        "author": "Auto-Update (AI)",
        "description": "RTO updates based on BIA changes",
        "status": "superseded"
      },
      {
        "version": "v2.3",
        "date": "2025-10-15T14:20:00Z",
        "author": "BCM Manager (John Smith)",
        "description": "Annual review - minor updates to recovery procedures",
        "status": "superseded"
      },
      {
        "version": "v2.2",
        "date": "2025-06-10T11:00:00Z",
        "author": "BCM Manager (John Smith)",
        "description": "Post-exercise updates based on EX-2024-008 lessons learned",
        "status": "superseded"
      },
      {
        "version": "v2.1",
        "date": "2025-01-05T09:00:00Z",
        "author": "BCM Manager (John Smith)",
        "description": "New year update - contact list refresh",
        "status": "superseded"
      }
    ],
    "version_tree_url": "/api/documents/doc_bc_plan_ed_001/history"
  },
  "rollback_options": {
    "can_rollback": true,
    "available_versions": ["v2.4", "v2.3", "v2.2", "v2.1"],
    "rollback_api": "POST /api/documents/doc_bc_plan_ed_001/rollback",
    "note": "Rollback creates new version (v2.6) with content from selected previous version"
  },
  "metadata": {
    "document_size": "2.4 MB",
    "format": "PDF + DOCX",
    "classification": "Internal - Business Continuity",
    "retention_policy": "Permanent (regulatory requirement)",
    "access_control": "RBAC - BCM team + ED leadership"
  }
}
```

**Version Comparison API**:
```json
{
  "compare_request": {
    "document_id": "doc_bc_plan_ed_001",
    "version_a": "v2.3",
    "version_b": "v2.5"
  },
  "comparison_result": {
    "versions_compared": "v2.3 vs v2.5",
    "time_span": "40 days (2025-10-15 to 2025-11-25)",
    "total_changes": 4,
    "changes_by_type": {
      "content_updates": 3,
      "contact_changes": 1
    },
    "detailed_changes": [
      {
        "change_id": 1,
        "version": "v2.4",
        "date": "2025-11-21",
        "section": "Section 1.3 - RTO Summary",
        "change": "EHR RTO: 15 min → 10 min",
        "author": "Auto-Update (AI)"
      },
      {
        "change_id": 2,
        "version": "v2.4",
        "date": "2025-11-21",
        "section": "Section 5.2 - EHR Recovery",
        "change": "Sub-step timings adjusted for 10-min RTO",
        "author": "Auto-Update (AI)"
      },
      {
        "change_id": 3,
        "version": "v2.5",
        "date": "2025-11-25",
        "section": "Appendix B - Contact List",
        "change": "BCM Manager contact updated (John Smith → Jane Doe)",
        "author": "Admin User"
      }
    ],
    "side_by_side_url": "/api/documents/doc_bc_plan_ed_001/compare?v1=v2.3&v2=v2.5"
  }
}
```

**Rollback Example**:
```json
{
  "rollback_request": {
    "document_id": "doc_bc_plan_ed_001",
    "rollback_to_version": "v2.3",
    "reason": "RTO changes in v2.4 not approved by operations team, rolling back pending review"
  },
  "rollback_result": {
    "status": "success",
    "new_version_created": "v2.6",
    "description": "Rollback to v2.3 content",
    "content_source": "v2.3 (2025-10-15)",
    "rollback_performed_by": "BCM Manager",
    "rollback_timestamp": "2025-11-26T08:00:00Z",
    "changes_reverted": [
      "RTO changes from v2.4",
      "Contact list change from v2.5"
    ],
    "note": "v2.6 is now current version with v2.3 content. All versions preserved in history.",
    "notification_sent": "All document subscribers notified of rollback"
  }
}
```

**Events Published**:
```yaml
- event: document.version.created
  payload:
    document_id: doc_bc_plan_ed_001
    old_version: v2.4
    new_version: v2.5
    author: admin@hospital.com
    change_type: content_update
  subscribers:
    - notification-service (notify subscribers)
    - audit-service (log change)
    - compliance-service (version control evidence)

- event: document.rollback.performed
  payload:
    document_id: doc_bc_plan_ed_001
    rolled_back_from: v2.5
    rolled_back_to: v2.3
    new_version: v2.6
    reason: RTO changes not approved
  subscribers:
    - notification-service (alert stakeholders)
    - audit-service (log rollback)
```

**Components Used**:
- Documents Service
- Git-like Version Control Storage
- Diff Engine (change comparison)
- Audit Trail (PostgreSQL event sourcing)
- Notification Service

**Business Value**:
- **Complete History**: Never lose document versions
- **Audit Trail**: Who changed what, when, why
- **Rollback**: Easily revert problematic changes
- **Comparison**: See exactly what changed between versions
- **Compliance**: Meets ISO 7.5 document control requirements

---

### 6.3 Document Template Library

**Business Context**: Provide industry-standard templates for all BCM documents, customized for organization profile

**Inputs**:
```json
{
  "template_request": {
    "template_type": "business_continuity_plan",
    "industry": "healthcare",
    "organization_size": "500_employees",
    "standard": "iso_22301",
    "customization": {
      "department": "Radiology",
      "critical_processes": ["Diagnostic Imaging", "PACS", "Radiologist Reporting"],
      "technology_stack": ["PACS", "RIS", "EHR Integration"],
      "regulatory_requirements": ["HIPAA", "Joint Commission"]
    }
  }
}
```

**API Endpoint**: `POST /api/documents/templates/generate`

**Template Generation Process**:
```
1. RAG Template Retrieval
   ├─ Query: "healthcare business continuity plan radiology ISO 22301"
   ├─ Collections: [bcm_templates, iso_22301_templates, healthcare_templates]
   └─ Returns: 5 relevant base templates

2. AI Customization (Claude Sonnet)
   ├─ Base: Retrieved templates
   ├─ Customize: For Radiology department + healthcare industry
   ├─ Pre-fill: Known data (processes, tech, contacts)
   └─ Generate: 80% complete customized template

3. Validation
   ├─ Verify: ISO 22301 structure compliance
   ├─ Check: All required sections present
   └─ Quality: Ensure medical terminology correct
```

**Response** (Abbreviated):
```json
{
  "template_id": "tmpl_bc_plan_radiology_001",
  "template_name": "Business Continuity Plan - Radiology Department",
  "based_on": "ISO 22301:2019 BC Plan Template (Healthcare)",
  "customization_level": "80% complete",
  "generated_document": {
    "format": "DOCX + PDF",
    "sections": [
      {
        "section_number": "1.0",
        "title": "Introduction and Purpose",
        "completion": "100%",
        "content_preview": "This Business Continuity Plan establishes the framework for maintaining Radiology Department operations during disruptions. The plan ensures diagnostic imaging services continue to support patient care in alignment with [Hospital Name]'s mission to provide excellent healthcare...",
        "customization_notes": "Pre-filled with Radiology-specific context. Hospital name placeholder to be replaced."
      },
      {
        "section_number": "2.0",
        "title": "Scope",
        "completion": "90%",
        "content_preview": "This plan covers the Radiology Department, including:\n- Diagnostic Imaging Services (X-Ray, CT, MRI, Ultrasound)\n- PACS (Picture Archiving and Communication System)\n- Radiologist Reporting Workflow\n- Integration with EHR and Hospital Information Systems\n\nThe plan addresses disruptions to: Technology (PACS, RIS, EHR integration), Facilities (imaging equipment, reading rooms), Staff (radiologists, technicians), and External Dependencies (contrast media supply, equipment maintenance vendors).",
        "customization_notes": "Scope pre-filled based on 'critical_processes' and 'technology_stack' inputs. Review and adjust as needed."
      },
      {
        "section_number": "3.0",
        "title": "Critical Processes and Dependencies",
        "completion": "70%",
        "content_preview": "Critical Process 1: Diagnostic Imaging\n- RTO: [TO BE DETERMINED - recommend BIA]\n- Technology Dependencies: PACS, Imaging equipment, RIS\n- Staff Dependencies: Radiologic technologists (minimum 3 on duty)\n- Impact if Unavailable: Unable to perform diagnostic imaging, delays in diagnosis and treatment\n\nCritical Process 2: Radiologist Reporting\n- RTO: [TO BE DETERMINED - recommend BIA]\n- Technology Dependencies: PACS workstations, Voice recognition software\n- Staff Dependencies: Radiologists (minimum 1 on duty for STAT reads)\n- Impact if Unavailable: Delayed radiology reports, clinical decision-making impaired",
        "customization_notes": "Critical processes identified from inputs. RTOs need to be filled in from BIA data. Consider integrating with BIA Service API to auto-populate."
      },
      {
        "section_number": "4.0",
        "title": "Recovery Strategies",
        "completion": "60%",
        "content_preview": "PACS Failure Recovery:\n1. Immediate: Switch to PACS backup system (if available)\n2. Short-term: Use web-based PACS viewer for critical image access\n3. Medium-term: Coordinate with PACS vendor for emergency restoration\n4. Workaround: Film-based imaging (if equipment supports), manual image distribution\n\nRIS Failure Recovery:\n1. Immediate: Paper-based exam ordering and tracking\n2. Short-term: Temporary manual scheduling\n3. Workaround: Phone/fax orders from clinical departments\n\nEHR Integration Failure:\n1. Manual patient registration at Radiology\n2. Fax/phone results to ordering physicians\n3. Paper requisitions for exam orders",
        "customization_notes": "Recovery strategies are healthcare radiology best practices. Customize based on your specific PACS/RIS vendors and backup capabilities."
      },
      {
        "section_number": "5.0",
        "title": "Roles and Responsibilities",
        "completion": "80%",
        "content_preview": "BC Plan Owner: Radiology Director\nAlternate: [TO BE FILLED]\n\nCrisis Team Roles:\n- Radiology Director: Overall incident coordination, clinical prioritization decisions\n- Chief Radiologist: Clinical operations continuity, radiologist staffing\n- PACS Administrator: Technology recovery coordination, vendor liaison\n- Radiology Nursing Supervisor: Patient flow management, staff coordination\n- [Hospital] BCM Manager: BC plan activation support, enterprise coordination\n\nDecision Authority:\n- Radiology Director has authority to activate this BC plan\n- Escalation to CMO/COO required for: Service diversion decisions, budgetary impacts >$50K, multi-day service disruptions",
        "customization_notes": "Roles based on typical radiology structure. Fill in specific names and contact information in Appendix."
      },
      {
        "section_number": "6.0",
        "title": "Plan Activation Criteria",
        "completion": "75%",
        "content_preview": "Activate this BC Plan when:\n1. PACS unavailable for >15 minutes with no immediate resolution\n2. Critical imaging equipment (CT/MRI) failure affecting >50% capacity\n3. Radiology department inaccessible (facility damage, contamination)\n4. Radiologist staffing <50% of minimum required for >2 hours\n5. Multiple system failures creating inability to perform/report diagnostic imaging\n\nActivation Process:\n1. Radiology Director (or alternate) assesses incident\n2. Determine if activation criteria met\n3. Notify Hospital BCM Manager and CMO/COO\n4. Convene Radiology Crisis Team\n5. Implement recovery strategies per Section 4.0\n6. Document decisions in crisis log",
        "customization_notes": "Activation criteria based on healthcare radiology best practices. Adjust thresholds based on your department size and patient volume."
      },
      {
        "section_number": "7.0",
        "title": "Communication Plan",
        "completion": "70%",
        "content_preview": "Internal Communication:\n- Radiology Staff: [Method: overhead page, text alerts, in-person briefing]\n- Ordering Physicians: [Method: EHR alerts, phone tree, email blast]\n- Hospital Leadership: [Method: direct call to CMO/COO, situation reports every 2 hours]\n- IT Department: [Method: direct call to CIO/IT Director, joint crisis coordination]\n\nExternal Communication:\n- PACS Vendor: [Contact: TO BE FILLED, Escalation path: TO BE FILLED]\n- Imaging Equipment Vendors: [Contacts: TO BE FILLED per equipment type]\n- Contrast Media Supplier: [Contact: TO BE FILLED]\n- Referring Hospitals (for patient transfers if needed): [Contacts: TO BE FILLED]\n\nCommunication Templates:\n- Internal staff alert template (Appendix C)\n- Physician notification template (Appendix D)\n- Patient communication script (Appendix E)",
        "customization_notes": "Fill in specific contact methods and vendor contact information. Templates provided in appendices."
      },
      {
        "section_number": "8.0",
        "title": "Testing and Maintenance",
        "completion": "90%",
        "content_preview": "Plan Review:\n- Annual comprehensive review (due: [Month] each year)\n- Quarterly contact list verification\n- Post-incident review and update (within 30 days of activation)\n- After any significant organizational or technology changes\n\nExercise Program:\n- Annual table-top exercise (ISO 22301 requirement)\n- Bi-annual PACS failover drill (coordinate with IT)\n- Quarterly communication tree test\n\nPlan Distribution:\n- Electronic: Shared drive [Path: TO BE FILLED], BC Management platform\n- Print: Radiology Director office, PACS Administrator office, Hospital BCM office\n- Access: All Radiology leadership, Hospital BCM team, selected IT staff\n\nVersion Control:\n- Current version: 1.0 (generated [Date])\n- Living document: Auto-updates when BIA or risk data changes\n- Approval required: Radiology Director for updates",
        "customization_notes": "Testing frequency aligns with ISO 22301 requirements. Adjust based on your organization's risk tolerance and regulatory requirements."
      },
      {
        "section_number": "9.0",
        "title": "Regulatory and Compliance Considerations",
        "completion": "85%",
        "content_preview": "HIPAA Compliance:\n- Maintain patient privacy during manual processes\n- Secure paper-based patient information\n- Document all access to patient images/reports during incident\n- Breach notification process if patient data compromised\n\nJoint Commission Requirements:\n- Emergency management standard compliance\n- Patient safety during service disruptions\n- Staff training and competency\n- Documentation of BC capabilities\n\nState Regulations:\n- [State] Department of Health notification requirements for extended service disruptions\n- Radiation safety protocols during manual operations\n\nProfessional Standards:\n- ACR (American College of Radiology) practice parameters\n- Radiologist availability for critical reads\n- Image quality standards (even during disruptions)",
        "customization_notes": "Regulatory requirements customized for healthcare/radiology. Verify your state-specific requirements."
      }
    ],
    "appendices": [
      {
        "appendix": "A",
        "title": "Contact List",
        "completion": "40%",
        "content": "Template table provided. Fill in specific names, phone numbers, emails, after-hours contacts."
      },
      {
        "appendix": "B",
        "title": "Technology Asset Inventory",
        "completion": "50%",
        "content": "PACS system details, Imaging equipment list (CT, MRI, X-Ray, etc.), RIS details, Network dependencies. Integrate with CMDB if available."
      },
      {
        "appendix": "C-E",
        "title": "Communication Templates",
        "completion": "90%",
        "content": "Ready-to-use templates for staff alerts, physician notifications, patient communication scripts."
      },
      {
        "appendix": "F",
        "title": "Vendor Escalation Procedures",
        "completion": "30%",
        "content": "Template provided. Fill in vendor-specific escalation paths, SLA references, emergency contact procedures."
      }
    ]
  },
  "next_steps": [
    {
      "step": 1,
      "action": "Review and customize template",
      "owner": "Radiology Director",
      "estimated_time": "4-6 hours",
      "guidance": "Focus on filling in organization-specific details (contacts, vendors, specific procedures). Pre-filled content is based on best practices but should be validated for your environment."
    },
    {
      "step": 2,
      "action": "Integrate BIA data",
      "api_integration": "GET /api/bia/{bia_id}/data → auto-fill RTOs and dependencies",
      "estimated_time": "30 minutes (automated)",
      "guidance": "If you have completed a BIA for Radiology, we can automatically populate RTO/RPO data and dependencies."
    },
    {
      "step": 3,
      "action": "Stakeholder review",
      "reviewers": ["Radiology Director", "Chief Radiologist", "PACS Administrator", "BCM Manager"],
      "estimated_time": "2-3 hours (meeting + revisions)",
      "guidance": "Schedule review meeting with key stakeholders to validate content, fill in gaps, ensure buy-in."
    },
    {
      "step": 4,
      "action": "Approval and distribution",
      "approvers": ["Radiology Director", "CMO", "BCM Manager"],
      "estimated_time": "1 week (approval workflow)",
      "guidance": "Submit for formal approval, then distribute to all stakeholders per Section 8.0 distribution list."
    }
  ],
  "ai_assistance_available": {
    "further_customization": "POST /api/documents/templates/tmpl_bc_plan_radiology_001/customize - provide additional context for deeper customization",
    "gap_filling": "POST /api/documents/templates/tmpl_bc_plan_radiology_001/fill-gaps - AI will suggest content for remaining 20% gaps",
    "bia_integration": "POST /api/documents/templates/tmpl_bc_plan_radiology_001/integrate-bia - auto-fill from BIA data",
    "compliance_check": "POST /api/documents/templates/tmpl_bc_plan_radiology_001/compliance-check - verify ISO 22301 alignment"
  },
  "template_metadata": {
    "generated_by": "Claude Sonnet via RAG",
    "generation_time": "35 seconds",
    "base_templates_used": 3,
    "customization_confidence": 0.88,
    "estimated_time_savings": "20-30 hours vs creating from scratch"
  }
}
```

**Events Published**:
```yaml
- event: document.template.generated
  payload:
    template_id: tmpl_bc_plan_radiology_001
    template_type: business_continuity_plan
    industry: healthcare
    department: Radiology
    completion: 80%
  subscribers:
    - notification-service (notify requester)
    - document-service (store template)
```

**Components Used**:
- Documents Service
- AI Foundation (Claude Sonnet)
- RAG (template library search)
- Knowledge Base (ISO 22301 templates, healthcare templates)
- BIA Service Integration (optional data fill)

**Business Value**:
- **Time Savings**: 20-30 hours saved vs manual creation
- **Expert Quality**: Based on ISO 22301 and industry best practices
- **Customization**: 80% pre-filled for specific department/industry
- **Consistency**: Standard structure across all departments
- **Compliance**: ISO 22301 requirements built-in

---

### 6.4 Document Approval Workflow

**Business Context**: Structured approval process for BC plans, policies, and critical documents with multi-level sign-off

**Inputs**:
```json
{
  "document_id": "doc_bc_plan_radiology_001",
  "workflow_type": "sequential_approval",
  "approvers": [
    {
      "level": 1,
      "role": "Radiology Director",
      "user": "dr.chen@hospital.com",
      "approval_type": "required",
      "delegation_allowed": false
    },
    {
      "level": 2,
      "role": "BCM Manager",
      "user": "jane.doe@hospital.com",
      "approval_type": "required",
      "delegation_allowed": true
    },
    {
      "level": 3,
      "role": "CMO",
      "user": "cmo@hospital.com",
      "approval_type": "required",
      "delegation_allowed": true
    },
    {
      "level": 4,
      "role": "CIO (Technical Review)",
      "user": "cio@hospital.com",
      "approval_type": "optional",
      "delegation_allowed": true
    }
  ],
  "due_date": "2025-12-15",
  "reminder_schedule": {
    "initial_reminder": "3_days_after_submission",
    "recurring_reminder": "every_2_days",
    "escalation": "1_day_before_due_date"
  }
}
```

**API Endpoint**: `POST /api/documents/{document_id}/approval/initiate`

**Approval Workflow Process**:
```
Sequential Approval Flow:
  ↓
  1. Notify Level 1 approver
  2. Wait for Level 1 approval
  3. If approved → notify Level 2
  4. If rejected → notify author, workflow ends
  5. Repeat for all levels
  6. When all required approvals → document approved
  ↓
Track status, send reminders, handle escalations
```

**Response**:
```json
{
  "workflow_id": "wf_approval_001",
  "document_id": "doc_bc_plan_radiology_001",
  "document_name": "Business Continuity Plan - Radiology Department v1.0",
  "status": "in_progress",
  "initiated_by": "Radiology Planning Team",
  "initiated_at": "2025-12-01T09:00:00Z",
  "due_date": "2025-12-15T23:59:59Z",
  "workflow_type": "sequential_approval",
  "approval_stages": [
    {
      "stage": 1,
      "approver": "Radiology Director (Dr. Michael Chen)",
      "email": "dr.chen@hospital.com",
      "approval_type": "required",
      "status": "pending",
      "notified_at": "2025-12-01T09:00:00Z",
      "due_date": "2025-12-05",
      "reminder_sent": 0,
      "approval_link": "/api/documents/doc_bc_plan_radiology_001/approve?token=abc123",
      "comment_required": false
    },
    {
      "stage": 2,
      "approver": "BCM Manager (Jane Doe)",
      "email": "jane.doe@hospital.com",
      "approval_type": "required",
      "status": "waiting_for_previous",
      "notified_at": null,
      "note": "Will be notified after Stage 1 approval"
    },
    {
      "stage": 3,
      "approver": "CMO",
      "email": "cmo@hospital.com",
      "approval_type": "required",
      "status": "waiting_for_previous",
      "notified_at": null
    },
    {
      "stage": 4,
      "approver": "CIO (Technical Review)",
      "email": "cio@hospital.com",
      "approval_type": "optional",
      "status": "waiting_for_previous",
      "note": "Optional technical review, can approve in parallel with CMO"
    }
  ],
  "progress": {
    "total_required_approvals": 3,
    "approvals_completed": 0,
    "approvals_pending": 3,
    "optional_approvals": 1,
    "overall_progress": "0% (0/3 required)"
  }
}
```

**Approver Experience** (Dr. Chen receives):
```json
{
  "notification": {
    "type": "approval_request",
    "subject": "Action Required: Approve BC Plan - Radiology Department",
    "priority": "high",
    "document": {
      "name": "Business Continuity Plan - Radiology Department v1.0",
      "type": "Business Continuity Plan",
      "department": "Radiology",
      "author": "Radiology Planning Team",
      "submitted_date": "2025-12-01",
      "due_date": "2025-12-05 (4 days remaining)"
    },
    "approval_request": {
      "your_role": "Radiology Director - Departmental Approval",
      "approval_level": "Stage 1 of 3 (required)",
      "what_to_review": "Review for operational accuracy, clinical feasibility, staff capacity, and radiology-specific considerations.",
      "time_estimate": "30-45 minutes",
      "approval_link": "https://bcm-platform.hospital.com/approve/doc_bc_plan_radiology_001?token=abc123"
    },
    "document_preview": {
      "key_sections": [
        "Section 3.0 - Critical Processes (Diagnostic Imaging, Radiologist Reporting)",
        "Section 4.0 - Recovery Strategies (PACS, RIS, EHR integration)",
        "Section 5.0 - Roles and Responsibilities (your role as BC Plan Owner)"
      ],
      "summary": "This plan establishes continuity procedures for Radiology Department operations during disruptions. It covers PACS, RIS, imaging equipment, and radiologist staffing continuity.",
      "full_document_url": "/api/documents/doc_bc_plan_radiology_001/download"
    },
    "actions": [
      {
        "action": "Approve",
        "button": "Approve Plan",
        "effect": "Approves plan and advances to next approval stage (BCM Manager)",
        "requires": "Optional comment"
      },
      {
        "action": "Approve with Comments",
        "button": "Approve with Suggestions",
        "effect": "Approves but provides feedback for future revisions",
        "requires": "Comment explaining suggestions"
      },
      {
        "action": "Request Changes",
        "button": "Request Revisions",
        "effect": "Does not approve. Document returned to author for revisions. Workflow restarts after revisions.",
        "requires": "Comment explaining required changes"
      },
      {
        "action": "Reject",
        "button": "Reject Plan",
        "effect": "Rejects document. Workflow ends. Requires significant justification.",
        "requires": "Comment explaining rejection rationale"
      },
      {
        "action": "Delegate",
        "button": "Delegate Approval",
        "effect": "Transfer approval to alternate (if delegation allowed)",
        "requires": "Select delegate",
        "available": false,
        "reason": "Delegation not allowed for this approval"
      }
    ]
  }
}
```

**After Dr. Chen Approves**:
```json
{
  "approval_recorded": {
    "workflow_id": "wf_approval_001",
    "stage": 1,
    "approver": "Dr. Michael Chen",
    "decision": "approved_with_comments",
    "approved_at": "2025-12-02T14:30:00Z",
    "comment": "Plan looks comprehensive. I recommend adding specific contact information for after-hours radiologist on-call in Appendix A. Also, please verify PACS vendor emergency support phone number - I believe it changed recently. Otherwise, approved.",
    "attachments": [],
    "next_stage": {
      "stage": 2,
      "approver": "BCM Manager (Jane Doe)",
      "notified_at": "2025-12-02T14:31:00Z",
      "status": "Approval request sent"
    },
    "workflow_status": {
      "overall_status": "in_progress",
      "progress": "33% (1/3 required approvals complete)",
      "estimated_completion": "2025-12-10 (if approvals proceed on schedule)"
    }
  }
}
```

**Escalation Example** (if approver doesn't respond):
```json
{
  "escalation_triggered": {
    "workflow_id": "wf_approval_001",
    "stage": 2,
    "approver": "BCM Manager (Jane Doe)",
    "issue": "No response for 4 days (submitted 2025-12-02, now 2025-12-06)",
    "reminders_sent": 2,
    "due_date": "2025-12-15 (9 days remaining)",
    "escalation_action": {
      "action": "Notify manager",
      "recipient": "COO (BCM Manager's supervisor)",
      "message": "BCM Manager approval pending for 4 days on critical BC Plan. Due date: Dec 15. Please follow up.",
      "sent_at": "2025-12-06T09:00:00Z"
    },
    "next_escalation": {
      "if_no_response_by": "2025-12-14",
      "action": "Auto-delegate to alternate BCM Manager (if configured)"
    }
  }
}
```

**Final Approval**:
```json
{
  "workflow_complete": {
    "workflow_id": "wf_approval_001",
    "document_id": "doc_bc_plan_radiology_001",
    "status": "approved",
    "completed_at": "2025-12-08T16:45:00Z",
    "total_duration": "7 days (2025-12-01 to 2025-12-08)",
    "approvals": [
      {
        "stage": 1,
        "approver": "Dr. Michael Chen (Radiology Director)",
        "decision": "approved_with_comments",
        "approved_at": "2025-12-02T14:30:00Z",
        "comment": "Plan looks comprehensive. Recommend adding after-hours contact info..."
      },
      {
        "stage": 2,
        "approver": "Jane Doe (BCM Manager)",
        "decision": "approved",
        "approved_at": "2025-12-06T10:15:00Z",
        "comment": "Excellent work. Plan aligns with ISO 22301 requirements and hospital BCM standards."
      },
      {
        "stage": 3,
        "approver": "Dr. Sarah Johnson (CMO)",
        "decision": "approved",
        "approved_at": "2025-12-08T16:45:00Z",
        "comment": "Approved. Critical component of our clinical continuity capabilities."
      },
      {
        "stage": 4,
        "approver": "CIO (optional)",
        "decision": "not_required",
        "note": "Optional approval - workflow completed without CIO review"
      }
    ],
    "document_status": {
      "previous_status": "draft",
      "new_status": "approved",
      "version": "v1.0 (approved)",
      "approval_date": "2025-12-08",
      "next_review_date": "2025-12-08 (annual review)",
      "distribution": "All Radiology staff, Hospital BCM team, Executive leadership"
    },
    "post_approval_actions": [
      {
        "action": "Distribute approved document",
        "status": "completed",
        "recipients": 47,
        "notification_sent": "2025-12-08T17:00:00Z"
      },
      {
        "action": "Add to BC plan library",
        "status": "completed",
        "url": "/api/documents/library/bc-plans/radiology"
      },
      {
        "action": "Schedule annual review",
        "status": "completed",
        "review_due_date": "2026-12-08",
        "reminder_scheduled": true
      },
      {
        "action": "Log compliance evidence (ISO 7.5)",
        "status": "completed",
        "compliance_record": "Document control evidence logged"
      }
    ],
    "approval_suggestions_tracking": {
      "total_suggestions": 2,
      "from_dr_chen": [
        "Add after-hours radiologist contact info",
        "Verify PACS vendor emergency number"
      ],
      "action_taken": "Suggestions added to document backlog for v1.1 update"
    }
  }
}
```

**Events Published**:
```yaml
- event: document.approval.initiated
  payload:
    workflow_id: wf_approval_001
    document_id: doc_bc_plan_radiology_001
    approvers_count: 4
    required_approvals: 3

- event: document.approval.stage_completed
  count: 3

- event: document.approved
  payload:
    workflow_id: wf_approval_001
    document_id: doc_bc_plan_radiology_001
    duration_days: 7
    approvers: [dr.chen, jane.doe, cmo]

- event: document.status.changed
  payload:
    document_id: doc_bc_plan_radiology_001
    old_status: draft
    new_status: approved
```

**Components Used**:
- Documents Service
- Workflow Engine (approval orchestration)
- Notification Service (emails, reminders, escalations)
- Calendar Integration (due dates, reminders)
- Audit Trail (approval history)

**Business Value**:
- **Structured Process**: Clear approval hierarchy and accountability
- **Tracking**: Real-time visibility into approval status
- **Automation**: Reminders and escalations reduce delays
- **Audit Trail**: Complete record of who approved what when
- **Flexibility**: Sequential, parallel, or mixed approval workflows

---

### 6.5 Document Search (Semantic)

**Business Context**: Find relevant documents using natural language queries, not just keywords

**Inputs**:
```json
{
  "search_query": "What should I do if the hospital loses power and the generator fails?",
  "search_type": "semantic",
  "filters": {
    "document_types": ["business_continuity_plan", "emergency_procedure", "policy"],
    "departments": ["Facilities", "Operations", "Clinical"],
    "classification": ["approved", "current"]
  },
  "result_preferences": {
    "max_results": 10,
    "include_snippets": true,
    "relevance_threshold": 0.7
  }
}
```

**API Endpoint**: `POST /api/documents/search/semantic`

**Semantic Search Process**:
```
Hybrid Search (70% Vector + 30% Keyword):
  ↓
  1. Generate query embedding (Sentence Transformer)
  2. Vector search in Qdrant (semantic similarity)
  3. Keyword search in PostgreSQL (exact matches)
  4. Combine and rank results (weighted)
  5. Extract relevant snippets
  6. Return ranked results with context
  ↓
Return: relevant_documents, snippets, relevance_scores
```

**Response**:
```json
{
  "search_query": "What should I do if the hospital loses power and the generator fails?",
  "search_type": "semantic",
  "results_found": 7,
  "search_time": "0.8 seconds",
  "results": [
    {
      "rank": 1,
      "document_id": "doc_bc_plan_facilities_001",
      "document_name": "Business Continuity Plan - Facilities Management",
      "document_type": "business_continuity_plan",
      "department": "Facilities",
      "version": "v3.2",
      "status": "approved",
      "relevance_score": 0.94,
      "match_explanation": "Exact match for power loss + generator failure scenario. Document Section 6.3 covers complete power failure response procedures.",
      "relevant_sections": [
        {
          "section": "6.3 - Complete Power Failure (Utility + Generator)",
          "snippet": "**Complete Power Failure (Utility Power + Generator Failure)**\n\nIf both utility power and backup generator fail:\n\n**Immediate Actions (First 15 Minutes):**\n1. Declare facility emergency - notify Hospital Incident Command\n2. Assess patient life support systems - prioritize ventilators, ICU equipment\n3. Activate UPS (Uninterruptible Power Supply) systems - provides 30-60 min backup for critical systems\n4. Notify utility company emergency line: [Contact]\n5. Mobilize emergency generator vendor: [Contact]\n\n**Life Safety Priority:**\n- ICU: Manual ventilation for patients on ventilators (nursing staff trained)\n- OR: Complete urgent surgeries ASAP, postpone elective cases\n- Emergency Department: Continue emergency care using portable battery equipment\n\n**Communication:**\n- Overhead announcement: 'Code Black - Complete Power Failure'\n- Notify all department heads\n- Alert local EMS: Hospital may need to divert patients\n\n**Recovery Steps:**\n- Coordinate mobile generator rental (ETA 2-4 hours)\n- Prioritize restoration: ICU → OR → Emergency Dept → General floors...",
          "page": 23,
          "url": "/api/documents/doc_bc_plan_facilities_001/section/6.3"
        },
        {
          "section": "Appendix E - Emergency Generator Vendor Contacts",
          "snippet": "Primary Vendor: [Company Name]\n- Emergency Hotline: 1-800-XXX-XXXX\n- Service Level: 24/7, 2-hour response time\n- Mobile Generator Availability: 3-4 hours\n\nBackup Vendor: [Company Name]\n- Emergency Contact: 1-888-XXX-XXXX...",
          "page": 78,
          "url": "/api/documents/doc_bc_plan_facilities_001/appendix/E"
        }
      ]
    },
    {
      "rank": 2,
      "document_id": "doc_emergency_power_procedure_001",
      "document_name": "Emergency Procedure - Power Failure Response",
      "document_type": "emergency_procedure",
      "department": "Facilities",
      "version": "v2.1",
      "status": "approved",
      "relevance_score": 0.91,
      "match_explanation": "Dedicated emergency procedure for power failures. Quick reference guide for immediate response.",
      "relevant_sections": [
        {
          "section": "Section 2 - Complete Power Failure (Both Sources)",
          "snippet": "**COMPLETE POWER FAILURE - IMMEDIATE ACTIONS**\n\n✓ DECLARE CODE BLACK (overhead announcement)\n✓ CALL GENERATOR VENDOR EMERGENCY LINE: 1-800-XXX-XXXX\n✓ NOTIFY HOSPITAL INCIDENT COMMAND: XXX-XXXX\n✓ PRIORITIZE LIFE SUPPORT:\n   - ICU ventilators (manual ventilation protocol)\n   - OR equipment (complete urgent surgeries)\n   - Emergency Dept (battery backup equipment)\n\n✓ UPS SYSTEMS: 30-60 min battery backup active\n   - Critical systems protected temporarily\n   - Monitor UPS status dashboard\n\n✓ PATIENT SAFETY:\n   - Assess all patients on electrical life support\n   - Implement manual backup procedures\n   - Consider patient transfers if extended outage expected...",
          "page": 3,
          "url": "/api/documents/doc_emergency_power_procedure_001/section/2"
        }
      ]
    },
    {
      "rank": 3,
      "document_id": "doc_bc_plan_clinical_ops_001",
      "document_name": "Business Continuity Plan - Clinical Operations",
      "document_type": "business_continuity_plan",
      "department": "Clinical",
      "version": "v4.5",
      "status": "approved",
      "relevance_score": 0.87,
      "match_explanation": "Addresses clinical implications of power failure, patient care continuity during power loss.",
      "relevant_sections": [
        {
          "section": "4.8 - Utilities Failure (Power, Water, HVAC)",
          "snippet": "**Power Failure Impact on Clinical Care:**\n\nCritical Care Areas:\n- ICU: Patients on ventilators require immediate manual ventilation if UPS battery expires (30-60 min). ICU nursing staff trained on manual ventilation techniques. Backup manual resuscitation bags available in each ICU room.\n- Operating Rooms: Complete urgent/emergency surgeries ASAP. Postpone all elective surgeries. Portable battery-powered surgical lights available for critical cases.\n- Emergency Department: Continue emergency care using portable battery equipment. Divert ambulances if power not restored within 2 hours.\n\nMedication Management:\n- Automated medication dispensing systems (Pyxis) have 4-hour battery backup\n- After 4 hours: manual pharmacy access procedures\n- Refrigerated medications: pharmacy to monitor temperatures, relocate to backup refrigeration if needed...",
          "page": 34,
          "url": "/api/documents/doc_bc_plan_clinical_ops_001/section/4.8"
        }
      ]
    },
    {
      "rank": 4,
      "document_id": "doc_incident_response_plan_001",
      "document_name": "Hospital Incident Response Plan",
      "document_type": "emergency_response_plan",
      "department": "Operations",
      "version": "v5.0",
      "status": "approved",
      "relevance_score": 0.83,
      "match_explanation": "General incident response framework, includes utilities failure as a trigger event.",
      "relevant_sections": [
        {
          "section": "Section 3 - Incident Categories and Triggers",
          "snippet": "**Category 4: Utilities / Infrastructure Failure**\n\nTrigger Events:\n- Complete power failure (utility + generator)\n- Water supply failure\n- HVAC system failure\n- Medical gas system failure\n\nIncident Command Structure:\n- Incident Commander: COO (or designated alternate)\n- Operations Chief: Facilities Director\n- Medical Director: CMO\n- Planning Chief: Emergency Manager\n\nActivation: Facilities Director activates in coordination with Hospital Incident Command...",
          "page": 15,
          "url": "/api/documents/doc_incident_response_plan_001/section/3"
        }
      ]
    },
    {
      "rank": 5,
      "document_id": "doc_facilities_policy_generator_001",
      "document_name": "Policy - Emergency Generator Testing and Maintenance",
      "document_type": "policy",
      "department": "Facilities",
      "version": "v1.3",
      "status": "approved",
      "relevance_score": 0.76,
      "match_explanation": "Related to generator operations, but focused on prevention (testing/maintenance) rather than failure response.",
      "relevant_sections": [
        {
          "section": "Section 5 - Generator Failure Investigation",
          "snippet": "In the event of generator failure to start or sustain load:\n\n1. Immediate Actions:\n   - Contact generator maintenance vendor (emergency line)\n   - Notify Facilities Director and Hospital Incident Command\n   - Activate BC Plan - Facilities (complete power failure procedures)\n\n2. Failure Investigation:\n   - Document failure mode, symptoms, timeline\n   - Vendor assessment within 2 hours\n   - Root cause analysis within 48 hours\n   - Corrective actions implemented before generator returned to service...",
          "page": 12,
          "url": "/api/documents/doc_facilities_policy_generator_001/section/5"
        }
      ]
    }
  ],
  "related_documents": [
    {
      "document_id": "doc_exercise_power_failure_2024",
      "document_name": "After-Action Report: Power Failure Exercise 2024",
      "relevance": "Historical exercise testing power failure response",
      "relevance_score": 0.68
    },
    {
      "document_id": "doc_bia_facilities_2025",
      "document_name": "BIA Report - Facilities Department",
      "relevance": "RTO/RPO for power restoration",
      "relevance_score": 0.65
    }
  ],
  "suggested_follow_up_queries": [
    "How long can UPS systems support critical equipment?",
    "What is the process for renting mobile generators?",
    "Which clinical areas are prioritized during power restoration?",
    "How to manually ventilate ICU patients?"
  ],
  "search_metadata": {
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "vector_search_results": 12,
    "keyword_search_results": 8,
    "combined_results": 7,
    "relevance_threshold": 0.7,
    "documents_indexed": 247
  }
}
```

**Events Published**:
```yaml
- event: document.search.performed
  payload:
    search_query: "power loss and generator failure"
    search_type: semantic
    results_found: 7
    search_time: 0.8
  subscribers:
    - analytics-service (track search patterns)
```

**Components Used**:
- Documents Service
- Qdrant (vector database for semantic search)
- Sentence Transformers (embedding model)
- PostgreSQL (keyword search, metadata)
- RAG (retrieval augmented generation)

**Business Value**:
- **Natural Language**: Search using questions, not keywords
- **Semantic Understanding**: Finds relevant content even with different wording
- **Context**: Provides snippets showing why results are relevant
- **Fast**: Sub-second search across hundreds of documents
- **Intelligent**: Suggests follow-up queries

---

### 6.6 Document Classification (Auto-Tagging)

**Business Context**: Automatically classify and tag uploaded documents using AI to ensure proper organization, searchability, and compliance tracking

**Inputs**:
```json
{
  "document_upload": {
    "file_name": "Emergency_Dept_Recovery_Procedures_Draft.docx",
    "file_size": "1.2 MB",
    "uploaded_by": "jane.doe@hospital.com",
    "upload_timestamp": "2025-12-10T10:30:00Z"
  },
  "classification_options": {
    "auto_classify": true,
    "confidence_threshold": 0.75,
    "manual_override_allowed": true,
    "extract_metadata": true
  }
}
```

**API Endpoint**: `POST /api/documents/upload`

**Auto-Classification Process**:
```
Document Upload → Content Extraction → AI Analysis → Classification → Metadata Extraction
  ↓
  1. Extract text from document (PDF/DOCX parser)
  2. Analyze content structure and terminology (AI)
  3. Classify document type, department, ISO clause
  4. Extract key metadata (dates, contacts, RTOs)
  5. Generate tags and keywords
  6. Assign access permissions based on classification
  ↓
Return: classified_document, extracted_metadata, suggested_tags
```

**Response**:
```json
{
  "document_id": "doc_bc_plan_ed_002",
  "upload_status": "success",
  "file_info": {
    "original_name": "Emergency_Dept_Recovery_Procedures_Draft.docx",
    "stored_name": "doc_bc_plan_ed_002_v1.0.docx",
    "file_size": "1.2 MB",
    "format": "DOCX",
    "uploaded_by": "jane.doe@hospital.com",
    "upload_timestamp": "2025-12-10T10:30:00Z"
  },
  "ai_classification": {
    "document_type": {
      "primary_type": "business_continuity_plan",
      "confidence": 0.92,
      "reasoning": "Document contains BC plan structure: scope, critical processes, recovery procedures, roles/responsibilities, activation criteria. Follows ISO 22301 BC plan format."
    },
    "sub_type": {
      "category": "departmental_bc_plan",
      "confidence": 0.89,
      "reasoning": "Focuses on specific department (Emergency Department) rather than enterprise-wide plan."
    },
    "department": {
      "primary_department": "Emergency Department",
      "confidence": 0.95,
      "secondary_departments": ["Clinical Operations", "Facilities"],
      "reasoning": "Document title and content explicitly reference Emergency Department. Cross-department dependencies identified with Facilities and Clinical Ops."
    },
    "iso_22301_mapping": {
      "primary_clause": "8.4.3 - Business continuity procedures",
      "confidence": 0.88,
      "related_clauses": [
        "8.4.2 - Business continuity strategies",
        "8.4.5 - Testing and exercising"
      ],
      "reasoning": "Document establishes detailed BC procedures for Emergency Department, aligning with ISO 22301 clause 8.4.3 requirements."
    },
    "document_status": {
      "lifecycle_stage": "draft",
      "confidence": 0.97,
      "reasoning": "Filename includes 'Draft', no approval signatures found, version indicates 'draft' status."
    },
    "classification_accuracy": {
      "overall_confidence": 0.90,
      "high_confidence_fields": ["document_type", "department", "status"],
      "medium_confidence_fields": ["iso_clause"],
      "requires_review": false,
      "review_reason": null
    }
  },
  "extracted_metadata": {
    "title": "Emergency Department Business Continuity Plan",
    "version": "Draft v0.9",
    "author": "Jane Doe (BCM Manager)",
    "creation_date": "2025-11-15",
    "last_modified": "2025-12-08",
    "document_owner": "Emergency Department Director",
    "key_dates": {
      "target_approval_date": "2025-12-20",
      "next_review_date": "Not yet set (pending approval)"
    },
    "critical_information": {
      "rto_values": [
        {
          "process": "EHR Manual Workaround",
          "rto": "10 minutes",
          "section": "Section 3.2"
        },
        {
          "process": "Patient Registration Backup",
          "rto": "5 minutes",
          "section": "Section 3.4"
        },
        {
          "process": "Emergency Medication Access",
          "rto": "15 minutes",
          "section": "Section 3.5"
        }
      ],
      "contact_count": 12,
      "recovery_strategies": 8,
      "dependencies_identified": 15
    },
    "document_statistics": {
      "pages": 28,
      "sections": 9,
      "appendices": 4,
      "word_count": 8450,
      "tables": 5,
      "diagrams": 2
    }
  },
  "auto_generated_tags": {
    "primary_tags": [
      "business_continuity",
      "emergency_department",
      "clinical_operations",
      "iso_22301",
      "recovery_procedures"
    ],
    "process_tags": [
      "ehr_continuity",
      "patient_registration",
      "medication_management",
      "triage_operations"
    ],
    "technology_tags": [
      "ehr_system",
      "patient_tracking_software",
      "pharmacy_systems"
    ],
    "compliance_tags": [
      "iso_22301_8.4.3",
      "hipaa_compliance",
      "joint_commission"
    ],
    "department_tags": [
      "emergency_medicine",
      "clinical_care",
      "critical_care"
    ],
    "total_tags": 18,
    "tag_confidence": 0.87
  },
  "access_control_recommendations": {
    "suggested_access_level": "department_restricted",
    "rationale": "BC plan contains operational details and contact information. Recommend access limited to Emergency Department staff, BCM team, and executive leadership.",
    "suggested_permissions": {
      "read": ["emergency_dept_staff", "bcm_team", "executives", "clinical_leadership"],
      "edit": ["emergency_dept_director", "bcm_manager"],
      "approve": ["emergency_dept_director", "cmo", "bcm_manager"]
    },
    "classification_level": "Internal - Business Continuity",
    "retention_policy": "Permanent (regulatory requirement)",
    "auto_applied": true
  },
  "content_quality_assessment": {
    "completeness_score": 0.75,
    "completeness_analysis": {
      "complete_sections": [
        "Introduction",
        "Scope",
        "Critical Processes",
        "Recovery Strategies",
        "Roles & Responsibilities"
      ],
      "incomplete_sections": [
        {
          "section": "Appendix A - Contact List",
          "issue": "Placeholder contacts not filled in",
          "suggestion": "Complete contact information for all key personnel"
        },
        {
          "section": "Section 7.0 - Testing Schedule",
          "issue": "Testing dates marked as 'TBD'",
          "suggestion": "Establish specific exercise schedule"
        }
      ],
      "missing_required_sections": []
    },
    "iso_22301_compliance_score": 0.82,
    "compliance_gaps": [
      "Testing and exercise schedule incomplete (Clause 8.5)",
      "Performance evaluation metrics not defined (Clause 9.1)"
    ],
    "recommendations": [
      "Complete contact information before final approval",
      "Add performance metrics for BC plan effectiveness",
      "Schedule initial table-top exercise within 60 days of approval"
    ]
  },
  "related_documents_suggestions": {
    "should_link_to": [
      {
        "document_id": "doc_bia_ed_2025",
        "document_name": "BIA Report - Emergency Department",
        "relationship": "Referenced BIA data",
        "confidence": 0.95
      },
      {
        "document_id": "doc_bc_plan_clinical_ops_001",
        "document_name": "BC Plan - Clinical Operations",
        "relationship": "Parent/enterprise plan",
        "confidence": 0.88
      },
      {
        "document_id": "doc_risk_register_ed_001",
        "document_name": "Risk Register - Emergency Department",
        "relationship": "Risk mitigation strategies",
        "confidence": 0.82
      }
    ],
    "auto_link": true
  },
  "next_actions": [
    {
      "action": "Review AI classification",
      "assigned_to": "jane.doe@hospital.com",
      "priority": "high",
      "due": "2025-12-11",
      "description": "Verify AI-generated classification and tags are accurate. Adjust if needed."
    },
    {
      "action": "Complete missing information",
      "assigned_to": "jane.doe@hospital.com",
      "priority": "high",
      "due": "2025-12-15",
      "description": "Fill in contact information and testing schedule per quality assessment."
    },
    {
      "action": "Submit for approval",
      "assigned_to": "jane.doe@hospital.com",
      "priority": "medium",
      "due": "2025-12-20",
      "description": "Initiate approval workflow after completing missing information."
    }
  ]
}
```

**Manual Override Example** (if user disagrees with AI classification):
```json
{
  "override_request": {
    "document_id": "doc_bc_plan_ed_002",
    "override_by": "jane.doe@hospital.com",
    "changes": {
      "document_type": {
        "ai_suggestion": "business_continuity_plan",
        "user_override": "emergency_procedure",
        "reason": "This is more of a quick reference procedure guide, not a full BC plan"
      },
      "tags": {
        "remove_tags": ["iso_22301_8.4.3"],
        "add_tags": ["quick_reference", "emergency_response"],
        "reason": "Better reflects actual document purpose"
      }
    }
  },
  "override_result": {
    "status": "accepted",
    "classification_updated": true,
    "ai_learning": "Classification feedback logged for model improvement",
    "reclassification_confidence": 0.88
  }
}
```

**Events Published**:
```yaml
- event: document.uploaded
  payload:
    document_id: doc_bc_plan_ed_002
    uploaded_by: jane.doe@hospital.com
    file_size: 1.2 MB
  subscribers:
    - document-service (process document)
    - notification-service (notify stakeholders)

- event: document.auto_classified
  payload:
    document_id: doc_bc_plan_ed_002
    document_type: business_continuity_plan
    department: Emergency Department
    confidence: 0.90
  subscribers:
    - analytics-service (track classification accuracy)
    - search-indexer (update search index)

- event: document.metadata.extracted
  payload:
    document_id: doc_bc_plan_ed_002
    metadata_count: 25
    rto_values_found: 3
  subscribers:
    - bia-service (link to BIA data)
    - compliance-service (track ISO requirements)
```

**Components Used**:
- Documents Service
- AI Foundation (Claude Sonnet - content analysis)
- NLP (text extraction, entity recognition)
- RAG (classification model training data)
- PostgreSQL (metadata storage)
- Qdrant (document indexing)

**Business Value**:
- **Time Savings**: Manual classification takes 15-30 minutes, AI does it in seconds
- **Consistency**: Standard classification across all documents
- **Discoverability**: Better tags = better search results
- **Compliance**: Automatic ISO clause mapping
- **Quality Control**: Identifies incomplete sections before approval

---

### 6.7 Document Access Control

**Business Context**: Role-based access control with granular permissions, ensuring sensitive BC documents only accessible to authorized personnel with complete audit trail

**Inputs**:
```json
{
  "document_id": "doc_bc_plan_ed_001",
  "access_control_policy": {
    "classification_level": "internal_confidential",
    "default_access": "deny",
    "role_based_permissions": [
      {
        "role": "emergency_dept_staff",
        "permissions": ["read"],
        "conditions": {
          "requires_authentication": true,
          "ip_restrictions": "internal_network_only"
        }
      },
      {
        "role": "emergency_dept_leadership",
        "permissions": ["read", "comment"],
        "conditions": {
          "requires_authentication": true
        }
      },
      {
        "role": "emergency_dept_director",
        "permissions": ["read", "edit", "approve", "delete"],
        "conditions": {
          "requires_authentication": true,
          "mfa_required": true
        }
      },
      {
        "role": "bcm_team",
        "permissions": ["read", "edit", "comment"],
        "conditions": {
          "requires_authentication": true
        }
      },
      {
        "role": "executives",
        "permissions": ["read"],
        "conditions": {
          "requires_authentication": true
        }
      }
    ],
    "user_specific_overrides": [
      {
        "user": "external_consultant@bcmfirm.com",
        "permissions": ["read"],
        "expiry": "2026-01-31",
        "reason": "Temporary access for BC plan review project"
      }
    ]
  }
}
```

**API Endpoint**: `POST /api/documents/{document_id}/access-control/set`

**Access Control Architecture**:
```
Request → Authentication → Role Check → Permission Verification → Audit Log → Access Decision
  ↓
  For each access attempt:
  1. Verify user authenticated (JWT token)
  2. Load user roles from RBAC system
  3. Check document access policy
  4. Verify conditions (MFA, IP, expiry)
  5. Log access attempt (approved/denied)
  6. Grant/deny access
  ↓
Return: access_granted OR access_denied (with reason)
```

**Response**:
```json
{
  "document_id": "doc_bc_plan_ed_001",
  "access_control_status": "active",
  "policy_applied": {
    "classification": "Internal Confidential",
    "default_access": "deny",
    "total_roles_with_access": 5,
    "total_users_with_access": 47,
    "special_access_grants": 1,
    "policy_effective_date": "2025-12-10T10:00:00Z"
  },
  "permission_matrix": {
    "emergency_dept_staff": {
      "users_count": 32,
      "permissions": ["read"],
      "conditions": ["internal_network_only"],
      "last_accessed": "2025-12-10T14:30:00Z"
    },
    "emergency_dept_leadership": {
      "users_count": 5,
      "permissions": ["read", "comment"],
      "conditions": ["authentication_required"],
      "last_accessed": "2025-12-10T09:15:00Z"
    },
    "emergency_dept_director": {
      "users_count": 2,
      "permissions": ["read", "edit", "approve", "delete"],
      "conditions": ["authentication_required", "mfa_required"],
      "last_accessed": "2025-12-09T16:45:00Z"
    },
    "bcm_team": {
      "users_count": 4,
      "permissions": ["read", "edit", "comment"],
      "conditions": ["authentication_required"],
      "last_accessed": "2025-12-10T11:20:00Z"
    },
    "executives": {
      "users_count": 4,
      "permissions": ["read"],
      "conditions": ["authentication_required"],
      "last_accessed": "2025-12-05T10:00:00Z"
    }
  },
  "special_access": [
    {
      "user": "external_consultant@bcmfirm.com",
      "permissions": ["read"],
      "granted_by": "BCM Manager",
      "granted_date": "2025-11-01",
      "expiry_date": "2026-01-31",
      "reason": "Temporary access for BC plan review project",
      "access_count": 12,
      "last_accessed": "2025-12-08T13:30:00Z"
    }
  ],
  "audit_settings": {
    "log_all_access": true,
    "log_failed_attempts": true,
    "alert_on_unauthorized_access": true,
    "retention_period": "7 years (regulatory requirement)"
  }
}
```

**Access Request Example** (User trying to access document):
```json
{
  "access_request": {
    "document_id": "doc_bc_plan_ed_001",
    "requested_by": "nurse.smith@hospital.com",
    "requested_action": "read",
    "timestamp": "2025-12-10T15:30:00Z",
    "user_context": {
      "authenticated": true,
      "roles": ["emergency_dept_staff", "registered_nurse"],
      "ip_address": "10.20.30.45",
      "device": "Hospital Workstation ED-WS-012",
      "network": "internal"
    }
  },
  "access_decision": {
    "decision": "granted",
    "reason": "User has 'emergency_dept_staff' role with 'read' permission. Request from internal network meets all conditions.",
    "granted_permissions": ["read"],
    "conditions_met": {
      "authentication": true,
      "internal_network": true
    },
    "session_id": "sess_abc123",
    "access_expires": "2025-12-10T23:59:59Z",
    "watermark": "Internal Confidential - Nurse Smith - 2025-12-10"
  },
  "audit_logged": {
    "audit_id": "audit_001234",
    "user": "nurse.smith@hospital.com",
    "document": "doc_bc_plan_ed_001",
    "action": "read",
    "decision": "granted",
    "timestamp": "2025-12-10T15:30:00Z",
    "ip": "10.20.30.45",
    "device": "ED-WS-012"
  }
}
```

**Access Denied Example** (Unauthorized access attempt):
```json
{
  "access_request": {
    "document_id": "doc_bc_plan_ed_001",
    "requested_by": "contractor.jones@vendor.com",
    "requested_action": "read",
    "timestamp": "2025-12-10T16:00:00Z",
    "user_context": {
      "authenticated": true,
      "roles": ["external_contractor"],
      "ip_address": "203.45.67.89",
      "device": "Personal Laptop",
      "network": "external"
    }
  },
  "access_decision": {
    "decision": "denied",
    "reason": "User role 'external_contractor' does not have access to this document. Document classification 'Internal Confidential' requires specific authorized roles.",
    "denied_permission": "read",
    "conditions_not_met": [
      "User role not in authorized list",
      "External network access not permitted for this classification"
    ],
    "recommendation": "Contact document owner (Emergency Dept Director) to request special access if needed."
  },
  "audit_logged": {
    "audit_id": "audit_001235",
    "user": "contractor.jones@vendor.com",
    "document": "doc_bc_plan_ed_001",
    "action": "read",
    "decision": "denied",
    "reason": "unauthorized_role",
    "timestamp": "2025-12-10T16:00:00Z",
    "ip": "203.45.67.89",
    "device": "Unknown",
    "alert_sent": true,
    "alert_recipients": ["security_team", "document_owner"]
  }
}
```

**Temporary Access Grant Example**:
```json
{
  "grant_request": {
    "document_id": "doc_bc_plan_ed_001",
    "grant_to": "auditor@external-firm.com",
    "permissions": ["read"],
    "duration": "30_days",
    "reason": "ISO 22301 certification audit - auditor needs to review BC plans",
    "granted_by": "bcm.manager@hospital.com",
    "conditions": {
      "require_nda": true,
      "watermark_required": true,
      "download_allowed": false,
      "print_allowed": false
    }
  },
  "grant_result": {
    "status": "granted",
    "grant_id": "grant_temp_001",
    "user": "auditor@external-firm.com",
    "permissions": ["read"],
    "valid_from": "2025-12-10T17:00:00Z",
    "valid_until": "2026-01-09T23:59:59Z",
    "conditions_applied": {
      "nda_signed": "required_before_access",
      "watermark": "Applied to all views",
      "download": "disabled",
      "print": "disabled",
      "screenshots": "blocked_via_browser_policy"
    },
    "access_link": "https://bcm-platform.hospital.com/documents/doc_bc_plan_ed_001?access_token=temp_xyz789",
    "notification_sent": {
      "to_user": "auditor@external-firm.com",
      "to_document_owner": "emergency.director@hospital.com",
      "to_security": "security@hospital.com"
    }
  }
}
```

**Access Analytics Dashboard**:
```json
{
  "document_id": "doc_bc_plan_ed_001",
  "access_analytics": {
    "time_period": "last_30_days",
    "total_access_attempts": 287,
    "successful_access": 279,
    "denied_access": 8,
    "denial_rate": "2.8%",
    "unique_users": 43,
    "most_active_users": [
      {
        "user": "ed.director@hospital.com",
        "access_count": 45,
        "last_access": "2025-12-10T09:15:00Z"
      },
      {
        "user": "bcm.manager@hospital.com",
        "access_count": 38,
        "last_access": "2025-12-10T14:30:00Z"
      },
      {
        "user": "nurse.supervisor@hospital.com",
        "access_count": 22,
        "last_access": "2025-12-09T16:45:00Z"
      }
    ],
    "access_by_action": {
      "read": 265,
      "edit": 12,
      "comment": 8,
      "approve": 2
    },
    "denied_access_reasons": [
      {
        "reason": "unauthorized_role",
        "count": 5
      },
      {
        "reason": "external_network_blocked",
        "count": 2
      },
      {
        "reason": "expired_temporary_access",
        "count": 1
      }
    ],
    "peak_access_times": {
      "weekday": "Monday",
      "hour": "09:00-10:00"
    }
  }
}
```

**Events Published**:
```yaml
- event: document.access.granted
  count: 279 (per month)
  payload:
    document_id: doc_bc_plan_ed_001
    user: [varies]
    action: [read/edit/etc]
  subscribers:
    - audit-service (compliance logging)
    - analytics-service (usage tracking)

- event: document.access.denied
  count: 8 (per month)
  payload:
    document_id: doc_bc_plan_ed_001
    user: [varies]
    reason: unauthorized_role
  subscribers:
    - security-service (alert on suspicious patterns)
    - audit-service (security logging)

- event: document.access.temporary_granted
  payload:
    document_id: doc_bc_plan_ed_001
    user: auditor@external-firm.com
    expiry: 2026-01-09
  subscribers:
    - notification-service (notify stakeholders)
    - audit-service (track external access)
```

**Components Used**:
- Documents Service
- RBAC Service (role verification)
- Authentication Service (JWT validation)
- Audit Trail (PostgreSQL event log)
- Security Service (MFA, IP restrictions)
- Notification Service (alerts)

**Business Value**:
- **Security**: Sensitive BC plans protected from unauthorized access
- **Compliance**: HIPAA/GDPR access control requirements met
- **Audit Trail**: Complete record of who accessed what when
- **Flexibility**: Temporary access for auditors, consultants, etc.
- **Granular Control**: Different permissions for different roles

---

### 6.8 Document Expiry & Review Tracking

**Business Context**: Automate document review cycles, expiry notifications, and ensure BC plans stay current per ISO 22301 requirements

**Inputs**:
```json
{
  "document_id": "doc_bc_plan_ed_001",
  "review_policy": {
    "review_frequency": "annual",
    "next_review_date": "2026-12-08",
    "review_owner": "emergency.director@hospital.com",
    "alternate_owner": "ed.manager@hospital.com",
    "early_review_triggers": [
      "major_organizational_change",
      "post_incident_activation",
      "failed_exercise",
      "significant_dependency_change"
    ],
    "notification_schedule": {
      "advance_notice": "60_days_before",
      "reminder_frequency": "every_14_days",
      "escalation": "14_days_before",
      "final_notice": "7_days_before",
      "overdue_alerts": "daily_after_due_date"
    },
    "auto_expire": {
      "enabled": true,
      "grace_period": "30_days",
      "status_after_expiry": "expired_pending_review"
    }
  }
}
```

**API Endpoint**: `POST /api/documents/{document_id}/review-policy/set`

**Review Tracking Architecture**:
```
Review Scheduler → Date Monitoring → Notification Engine → Review Workflow → Version Update
  ↓
  Daily check:
  1. Scan all documents for upcoming reviews
  2. Check expiry dates and grace periods
  3. Identify overdue documents
  4. Send notifications per schedule
  5. Trigger review workflows
  6. Update document status on expiry
  ↓
Track: review completion, extensions, overdue documents
```

**Response**:
```json
{
  "document_id": "doc_bc_plan_ed_001",
  "document_name": "Business Continuity Plan - Emergency Department",
  "current_version": "v2.5",
  "approval_date": "2025-12-08",
  "review_status": {
    "status": "active",
    "next_review_due": "2026-12-08",
    "days_until_review": 363,
    "review_frequency": "annual",
    "last_reviewed": "2025-12-08",
    "review_cycle": "1 of 1 (year 1)",
    "compliance_status": "compliant"
  },
  "review_ownership": {
    "primary_owner": {
      "name": "Dr. Michael Chen",
      "email": "emergency.director@hospital.com",
      "role": "Emergency Department Director",
      "responsibility": "Lead document review, ensure accuracy and relevance"
    },
    "alternate_owner": {
      "name": "Sarah Lee",
      "email": "ed.manager@hospital.com",
      "role": "ED Manager",
      "responsibility": "Backup review owner if primary unavailable"
    },
    "review_participants": [
      "emergency.director@hospital.com",
      "bcm.manager@hospital.com",
      "ed.manager@hospital.com",
      "clinical.ops.director@hospital.com"
    ]
  },
  "notification_schedule": {
    "60_day_advance_notice": {
      "date": "2026-10-09",
      "status": "scheduled",
      "message": "BC Plan review due in 60 days. Begin planning review process."
    },
    "45_day_reminder": {
      "date": "2026-10-24",
      "status": "scheduled"
    },
    "30_day_reminder": {
      "date": "2026-11-08",
      "status": "scheduled"
    },
    "14_day_escalation": {
      "date": "2026-11-24",
      "status": "scheduled",
      "escalate_to": "COO",
      "message": "BC Plan review due in 14 days. Escalation notice sent to COO."
    },
    "7_day_final_notice": {
      "date": "2026-12-01",
      "status": "scheduled",
      "urgency": "high"
    },
    "overdue_alerts": {
      "trigger": "2026-12-09",
      "frequency": "daily",
      "alert_recipients": ["document_owner", "bcm_manager", "coo"]
    }
  },
  "early_review_triggers": {
    "enabled": true,
    "trigger_conditions": [
      {
        "trigger": "major_organizational_change",
        "description": "Department restructure, merger, acquisition",
        "action": "Initiate early review immediately",
        "last_triggered": null
      },
      {
        "trigger": "post_incident_activation",
        "description": "BC plan activated due to real incident",
        "action": "Review within 30 days of incident resolution",
        "last_triggered": null
      },
      {
        "trigger": "failed_exercise",
        "description": "BC exercise identifies significant plan gaps",
        "action": "Review and update within 60 days",
        "last_triggered": null
      },
      {
        "trigger": "significant_dependency_change",
        "description": "Critical technology or vendor change",
        "action": "Review affected sections within 30 days",
        "last_triggered": null
      }
    ]
  },
  "expiry_settings": {
    "auto_expire_enabled": true,
    "grace_period": "30 days",
    "expiry_date_if_not_reviewed": "2027-01-07",
    "status_after_expiry": "expired_pending_review",
    "actions_on_expiry": [
      "Change document status to 'expired'",
      "Add warning banner to document viewer",
      "Notify all stakeholders",
      "Restrict access to view-only (no editing)",
      "Flag in compliance dashboard as 'overdue'"
    ]
  },
  "review_history": [
    {
      "review_date": "2025-12-08",
      "review_type": "annual",
      "reviewed_by": "Dr. Michael Chen",
      "outcome": "approved",
      "changes_made": "Updated contact list, revised RTO timings",
      "new_version": "v2.5",
      "next_review_scheduled": "2026-12-08"
    },
    {
      "review_date": "2024-12-15",
      "review_type": "annual",
      "reviewed_by": "Dr. Michael Chen",
      "outcome": "approved_with_minor_updates",
      "changes_made": "Updated recovery strategies section",
      "new_version": "v2.0",
      "next_review_scheduled": "2025-12-15"
    }
  ]
}
```

**60-Day Advance Notice Example**:
```json
{
  "notification": {
    "type": "review_advance_notice",
    "urgency": "normal",
    "subject": "Document Review Due in 60 Days: BC Plan - Emergency Department",
    "recipient": "emergency.director@hospital.com",
    "cc": ["ed.manager@hospital.com", "bcm.manager@hospital.com"],
    "sent_date": "2026-10-09T09:00:00Z",
    "message": {
      "summary": "Your annual review of the Emergency Department Business Continuity Plan is due in 60 days (December 8, 2026).",
      "document_info": {
        "document_name": "BC Plan - Emergency Department",
        "current_version": "v2.5",
        "last_reviewed": "2025-12-08",
        "review_due": "2026-12-08",
        "days_remaining": 60
      },
      "review_checklist": [
        "Verify all contact information is current",
        "Confirm RTO/RPO values still achievable",
        "Review recovery strategies for relevance",
        "Update any changed dependencies or vendors",
        "Check for organizational/technology changes requiring plan updates",
        "Coordinate with stakeholders for input",
        "Schedule review meeting with key personnel"
      ],
      "review_process": {
        "step_1": "Review document sections for accuracy and relevance",
        "step_2": "Gather stakeholder input and feedback",
        "step_3": "Make necessary updates to document",
        "step_4": "Submit updated document for approval (if changes made)",
        "step_5": "Confirm review completion in system"
      },
      "actions": [
        {
          "action": "Start Review",
          "link": "/api/documents/doc_bc_plan_ed_001/review/start",
          "description": "Begin document review process"
        },
        {
          "action": "View Document",
          "link": "/api/documents/doc_bc_plan_ed_001",
          "description": "View current version of document"
        },
        {
          "action": "Schedule Extension",
          "link": "/api/documents/doc_bc_plan_ed_001/review/request-extension",
          "description": "Request extension if more time needed"
        }
      ],
      "reminder": "You will receive additional reminders at 45, 30, 14, and 7 days before the due date."
    }
  }
}
```

**Overdue Document Alert Example**:
```json
{
  "overdue_alert": {
    "type": "document_overdue",
    "urgency": "high",
    "subject": "OVERDUE: BC Plan - Emergency Department Review Past Due",
    "recipient": "emergency.director@hospital.com",
    "cc": ["ed.manager@hospital.com", "bcm.manager@hospital.com", "coo@hospital.com"],
    "sent_date": "2026-12-09T09:00:00Z",
    "alert_number": 1,
    "message": {
      "summary": "The Emergency Department Business Continuity Plan review was due yesterday (December 8, 2026) and is now OVERDUE.",
      "document_info": {
        "document_name": "BC Plan - Emergency Department",
        "current_version": "v2.5",
        "review_due": "2026-12-08",
        "days_overdue": 1,
        "status": "overdue",
        "compliance_impact": "Document will expire in 30 days if not reviewed (grace period)"
      },
      "urgency_notice": "This document is critical for ISO 22301 compliance and operational readiness. Immediate attention required.",
      "consequences": [
        "Document status changed to 'overdue' - visible in compliance dashboard",
        "Daily overdue alerts sent to document owner and management",
        "If not reviewed within 30 days (grace period), document will expire",
        "Expired documents flagged in audit reports and compliance reviews"
      ],
      "immediate_actions_required": [
        {
          "action": "Complete Review Immediately",
          "priority": "critical",
          "link": "/api/documents/doc_bc_plan_ed_001/review/start"
        },
        {
          "action": "Request Extension (with justification)",
          "priority": "high",
          "link": "/api/documents/doc_bc_plan_ed_001/review/request-extension",
          "note": "Extension requires approval from BCM Manager"
        }
      ]
    },
    "escalation": {
      "escalated_to": "COO",
      "escalation_reason": "Document overdue, compliance risk",
      "escalation_date": "2026-12-09T09:00:00Z"
    }
  }
}
```

**Early Review Trigger Example** (BC plan activated during incident):
```json
{
  "early_review_triggered": {
    "trigger_type": "post_incident_activation",
    "trigger_event": {
      "event_id": "incident_2026_042",
      "event_name": "EHR System Outage - 4 hours",
      "event_date": "2026-03-15",
      "bc_plan_activated": true,
      "activation_duration": "4 hours 15 minutes"
    },
    "document_affected": {
      "document_id": "doc_bc_plan_ed_001",
      "document_name": "BC Plan - Emergency Department",
      "next_review_original": "2026-12-08",
      "next_review_accelerated": "2026-04-14"
    },
    "early_review_details": {
      "reason": "BC plan activated during real incident. Post-incident review required per ISO 22301 (Clause 8.6).",
      "review_deadline": "2026-04-14 (30 days after incident resolution)",
      "review_focus": [
        "Evaluate plan effectiveness during activation",
        "Identify gaps or issues encountered",
        "Update procedures based on lessons learned",
        "Verify RTO/RPO targets were achievable",
        "Review communication effectiveness",
        "Update based on after-action report findings"
      ],
      "related_documents": {
        "after_action_report": "doc_aar_incident_2026_042",
        "incident_log": "doc_incident_log_2026_042"
      }
    },
    "notification_sent": {
      "to": "emergency.director@hospital.com",
      "cc": ["bcm.manager@hospital.com", "ed.manager@hospital.com"],
      "subject": "Early BC Plan Review Required - Plan Activated During Incident",
      "sent_at": "2026-03-16T09:00:00Z"
    }
  }
}
```

**Review Completion Example**:
```json
{
  "review_completed": {
    "document_id": "doc_bc_plan_ed_001",
    "review_date": "2026-12-05",
    "reviewed_by": "Dr. Michael Chen",
    "review_type": "annual",
    "review_outcome": {
      "decision": "approved_with_updates",
      "summary": "Annual review completed. Document updated with current contact information, revised recovery strategies for new PACS system, and updated testing schedule.",
      "changes_made": [
        "Updated contact list (3 personnel changes)",
        "Revised Section 4.2 recovery strategies (new PACS backup system)",
        "Updated testing schedule for 2027",
        "Added new vendor contact (PACS provider changed)"
      ],
      "new_version_created": "v2.6",
      "participants": [
        "Dr. Michael Chen (Emergency Director)",
        "Jane Doe (BCM Manager)",
        "Sarah Lee (ED Manager)",
        "Tom Williams (CIO - for IT system updates)"
      ]
    },
    "next_review_scheduled": {
      "next_review_date": "2027-12-05",
      "review_frequency": "annual",
      "notifications_scheduled": true
    },
    "compliance_status": {
      "status": "compliant",
      "iso_22301_requirement": "8.4.3 - BC procedures maintained and reviewed",
      "evidence_logged": true,
      "audit_trail_updated": true
    },
    "notifications_sent": {
      "review_complete_notification": {
        "to": ["all_document_subscribers", "bcm_team", "executives"],
        "message": "BC Plan - Emergency Department has been reviewed and updated (v2.6). Key changes: contact list updated, PACS recovery strategies revised."
      }
    }
  }
}
```

**Compliance Dashboard View**:
```json
{
  "document_review_compliance": {
    "organization": "City General Hospital",
    "report_date": "2026-01-15",
    "total_bc_documents": 47,
    "review_compliance_summary": {
      "current_compliant": 42,
      "upcoming_reviews_60_days": 8,
      "upcoming_reviews_30_days": 3,
      "overdue": 2,
      "compliance_rate": "89.4%"
    },
    "overdue_documents": [
      {
        "document_id": "doc_bc_plan_facilities_001",
        "document_name": "BC Plan - Facilities",
        "review_due": "2026-01-10",
        "days_overdue": 5,
        "owner": "facilities.director@hospital.com",
        "status": "overdue",
        "grace_period_expires": "2026-02-09"
      },
      {
        "document_id": "doc_policy_incident_response_001",
        "document_name": "Incident Response Policy",
        "review_due": "2026-01-01",
        "days_overdue": 14,
        "owner": "cio@hospital.com",
        "status": "overdue",
        "grace_period_expires": "2026-01-31"
      }
    ],
    "upcoming_reviews": [
      {
        "document_id": "doc_bc_plan_it_001",
        "document_name": "BC Plan - IT Department",
        "review_due": "2026-02-28",
        "days_until_due": 44,
        "owner": "cio@hospital.com",
        "status": "advance_notice_sent"
      }
    ],
    "compliance_trends": {
      "last_quarter_compliance_rate": "91.2%",
      "current_quarter_compliance_rate": "89.4%",
      "trend": "slight_decline",
      "note": "2 documents overdue this quarter vs 0 last quarter"
    }
  }
}
```

**Events Published**:
```yaml
- event: document.review.due_soon
  payload:
    document_id: doc_bc_plan_ed_001
    review_due: 2026-12-08
    days_until_due: 60
  subscribers:
    - notification-service (send reminder)
    - compliance-service (track review status)

- event: document.review.overdue
  payload:
    document_id: doc_bc_plan_ed_001
    review_due: 2026-12-08
    days_overdue: 1
  subscribers:
    - notification-service (send overdue alert)
    - compliance-service (flag compliance issue)
    - escalation-service (escalate to management)

- event: document.review.completed
  payload:
    document_id: doc_bc_plan_ed_001
    review_date: 2026-12-05
    outcome: approved_with_updates
    new_version: v2.6
  subscribers:
    - notification-service (notify stakeholders)
    - compliance-service (update compliance status)
    - audit-service (log review evidence)

- event: document.expired
  payload:
    document_id: doc_bc_plan_ed_001
    expiry_date: 2027-01-07
    reason: not_reviewed_within_grace_period
  subscribers:
    - notification-service (alert critical stakeholders)
    - compliance-service (flag critical compliance issue)
    - document-service (restrict access)
```

**Components Used**:
- Documents Service
- Scheduler (cron jobs for review monitoring)
- Notification Service (reminders, alerts, escalations)
- Compliance Service (tracking review status)
- Workflow Engine (review process orchestration)
- Calendar Integration (due date management)

**Business Value**:
- **ISO 22301 Compliance**: Automated review cycles meet Clause 8.4.3 requirements
- **Never Miss Reviews**: Automated notifications prevent overdue documents
- **Accountability**: Clear ownership and escalation paths
- **Early Review Triggers**: Ensures plans updated after incidents
- **Compliance Visibility**: Dashboard shows all document review status

---

### 6.9 Document Export (Multiple Formats)

**Business Context**: Export BC plans and documents in various formats (PDF, DOCX, HTML) with formatting preservation for sharing, printing, and offline access

**Inputs**:
```json
{
  "document_id": "doc_bc_plan_ed_001",
  "export_format": "pdf",
  "export_options": {
    "include_metadata": true,
    "include_version_history": false,
    "include_approval_signatures": true,
    "include_table_of_contents": true,
    "watermark": {
      "enabled": true,
      "text": "Internal Confidential",
      "position": "footer"
    },
    "page_numbering": true,
    "header_footer": {
      "header": "Emergency Department BC Plan",
      "footer": "Version 2.5 | Approved: Dec 8, 2025 | Page {page} of {total}"
    }
  }
}
```

**API Endpoint**: `POST /api/documents/{document_id}/export`

**Export Process**:
```
Document Retrieval → Format Conversion → Styling Application → Metadata Injection → File Generation
  ↓
  1. Retrieve document content and metadata
  2. Convert to target format (PDF/DOCX/HTML)
  3. Apply styling (headers, footers, page numbers)
  4. Inject metadata, watermarks, signatures
  5. Generate file
  6. Store temporarily for download
  ↓
Return: download_url, expiry_time
```

**Response**:
```json
{
  "export_id": "exp_001234",
  "document_id": "doc_bc_plan_ed_001",
  "document_name": "BC Plan - Emergency Department",
  "export_status": "completed",
  "export_format": "pdf",
  "file_info": {
    "file_name": "BC_Plan_Emergency_Department_v2.5.pdf",
    "file_size": "3.8 MB",
    "pages": 28,
    "generated_at": "2025-12-10T16:30:00Z",
    "download_url": "/api/documents/doc_bc_plan_ed_001/export/exp_001234/download",
    "download_expires": "2025-12-11T16:30:00Z",
    "expiry_note": "Download link expires in 24 hours for security"
  },
  "export_options_applied": {
    "metadata_included": true,
    "version_history_included": false,
    "approval_signatures_included": true,
    "table_of_contents": true,
    "watermark": "Internal Confidential (footer)",
    "page_numbering": true,
    "header_footer": true
  },
  "document_metadata_embedded": {
    "title": "Business Continuity Plan - Emergency Department",
    "version": "v2.5",
    "author": "BCM Team - City General Hospital",
    "created_date": "2024-06-15",
    "last_modified": "2025-12-08",
    "approved_by": "Dr. Michael Chen (Emergency Director)",
    "approval_date": "2025-12-08",
    "classification": "Internal Confidential",
    "next_review_date": "2026-12-08",
    "keywords": ["business_continuity", "emergency_department", "iso_22301"]
  },
  "pdf_specific_features": {
    "pdf_version": "PDF/A-1b (archival standard)",
    "text_searchable": true,
    "bookmarks": true,
    "hyperlinks_preserved": true,
    "encryption": {
      "enabled": true,
      "permissions": {
        "printing": "allowed",
        "content_copying": "not_allowed",
        "editing": "not_allowed",
        "commenting": "allowed"
      }
    },
    "digital_signature": {
      "enabled": false,
      "note": "Digital signatures available for approved documents"
    }
  }
}
```

**Multiple Format Export Example**:
```json
{
  "bulk_export_request": {
    "document_id": "doc_bc_plan_ed_001",
    "export_formats": ["pdf", "docx", "html"],
    "export_reason": "Distribute to stakeholders - PDF for printing, DOCX for editing, HTML for web viewing"
  },
  "bulk_export_result": {
    "export_id": "exp_bulk_001",
    "status": "completed",
    "formats_generated": 3,
    "files": [
      {
        "format": "pdf",
        "file_name": "BC_Plan_Emergency_Department_v2.5.pdf",
        "file_size": "3.8 MB",
        "download_url": "/api/documents/exports/exp_bulk_001/pdf",
        "use_case": "Print distribution, email attachment"
      },
      {
        "format": "docx",
        "file_name": "BC_Plan_Emergency_Department_v2.5.docx",
        "file_size": "2.1 MB",
        "download_url": "/api/documents/exports/exp_bulk_001/docx",
        "use_case": "Editable version for annual review updates"
      },
      {
        "format": "html",
        "file_name": "BC_Plan_Emergency_Department_v2.5.html",
        "file_size": "1.5 MB",
        "download_url": "/api/documents/exports/exp_bulk_001/html",
        "use_case": "Intranet publishing, web-based viewing"
      }
    ],
    "zip_package": {
      "available": true,
      "file_name": "BC_Plan_Emergency_Department_v2.5_All_Formats.zip",
      "file_size": "6.2 MB",
      "download_url": "/api/documents/exports/exp_bulk_001/zip",
      "contents": "All 3 formats bundled for easy distribution"
    },
    "download_expires": "2025-12-11T16:30:00Z"
  }
}
```

**Print-Optimized PDF Export**:
```json
{
  "print_export_request": {
    "document_id": "doc_bc_plan_ed_001",
    "export_format": "pdf",
    "print_optimization": {
      "page_size": "letter",
      "orientation": "portrait",
      "margins": "0.75in",
      "color_mode": "grayscale",
      "high_quality_images": false,
      "include_blank_page_for_duplex": true
    }
  },
  "print_export_result": {
    "file_name": "BC_Plan_Emergency_Department_v2.5_Print.pdf",
    "file_size": "2.2 MB",
    "optimization_applied": {
      "color_mode": "grayscale",
      "image_compression": "optimized_for_print",
      "file_size_reduction": "42% smaller than original",
      "duplex_ready": true,
      "estimated_pages_to_print": 28
    },
    "printing_recommendations": {
      "recommended_printer": "Duplex laser printer",
      "paper_type": "Standard 20lb letter",
      "print_quality": "600 DPI or higher",
      "binding": "Three-hole punch for binder"
    }
  }
}
```

**Secure Distribution Export** (for external sharing):
```json
{
  "secure_export_request": {
    "document_id": "doc_bc_plan_ed_001",
    "export_format": "pdf",
    "security_options": {
      "password_protect": true,
      "password": "auto_generate",
      "expiry_date": "2025-12-31",
      "disable_printing": true,
      "disable_copying": true,
      "watermark": {
        "text": "Confidential - For External Consultant Use Only - Expires Dec 31, 2025",
        "diagonal": true,
        "opacity": 0.3
      }
    },
    "distribution": {
      "recipient": "consultant@external-firm.com",
      "send_via_email": true,
      "send_password_separately": true
    }
  },
  "secure_export_result": {
    "export_id": "exp_secure_001",
    "file_name": "BC_Plan_Emergency_Department_Confidential.pdf",
    "security_applied": {
      "password_protection": "enabled",
      "password": "Xk9mP2qL7n",
      "password_delivery": "Separate email to recipient",
      "printing": "disabled",
      "content_copying": "disabled",
      "expires": "2025-12-31T23:59:59Z",
      "watermark": "Applied to all pages"
    },
    "distribution_status": {
      "email_sent_to": "consultant@external-firm.com",
      "email_sent_at": "2025-12-10T17:00:00Z",
      "password_email_sent_at": "2025-12-10T17:05:00Z",
      "download_tracked": true
    },
    "audit_logged": {
      "exported_by": "bcm.manager@hospital.com",
      "export_reason": "External BC assessment project",
      "recipient": "consultant@external-firm.com",
      "security_level": "high",
      "approval_required": true,
      "approved_by": "coo@hospital.com"
    }
  }
}
```

**HTML Web Publishing Export**:
```json
{
  "web_export_request": {
    "document_id": "doc_bc_plan_ed_001",
    "export_format": "html",
    "web_options": {
      "responsive_design": true,
      "include_navigation": true,
      "include_search": true,
      "style_theme": "hospital_intranet",
      "embed_images": true,
      "generate_sitemap": true
    }
  },
  "web_export_result": {
    "export_id": "exp_web_001",
    "file_package": {
      "index_file": "index.html",
      "assets_folder": "assets/",
      "total_files": 15,
      "total_size": "2.8 MB"
    },
    "web_features": {
      "responsive": true,
      "mobile_friendly": true,
      "accessible": "WCAG 2.1 AA compliant",
      "navigation": "Left sidebar menu",
      "search": "Client-side JavaScript search",
      "print_stylesheet": "Included"
    },
    "deployment_options": [
      {
        "option": "Intranet Portal",
        "url": "https://intranet.hospital.com/bcm/ed-plan/",
        "status": "ready_to_deploy"
      },
      {
        "option": "SharePoint",
        "path": "/sites/BCM/Emergency_Department/",
        "status": "ready_to_upload"
      },
      {
        "option": "Download ZIP",
        "download_url": "/api/documents/exports/exp_web_001/download",
        "file_size": "2.8 MB"
      }
    ]
  }
}
```

**Batch Export Example** (multiple documents):
```json
{
  "batch_export_request": {
    "documents": [
      "doc_bc_plan_ed_001",
      "doc_bc_plan_radiology_001",
      "doc_bc_plan_it_001",
      "doc_bc_plan_facilities_001"
    ],
    "export_format": "pdf",
    "combine_into_single_file": true,
    "include_cover_page": true
  },
  "batch_export_result": {
    "export_id": "exp_batch_001",
    "status": "completed",
    "combined_file": {
      "file_name": "BC_Plans_All_Departments_2025.pdf",
      "file_size": "18.4 MB",
      "total_pages": 112,
      "documents_included": 4,
      "cover_page": "City General Hospital - Business Continuity Plans Compendium - 2025",
      "table_of_contents": "Auto-generated with page links"
    },
    "download_url": "/api/documents/exports/exp_batch_001/download",
    "individual_bookmarks": {
      "Emergency Department": "Page 1-28",
      "Radiology": "Page 29-56",
      "IT Department": "Page 57-89",
      "Facilities": "Page 90-112"
    }
  }
}
```

**Events Published**:
```yaml
- event: document.exported
  payload:
    document_id: doc_bc_plan_ed_001
    export_format: pdf
    exported_by: bcm.manager@hospital.com
    file_size: 3.8 MB
  subscribers:
    - audit-service (track export activity)
    - analytics-service (usage metrics)

- event: document.exported.secure_distribution
  payload:
    document_id: doc_bc_plan_ed_001
    recipient: consultant@external-firm.com
    security_level: high
    expires: 2025-12-31
  subscribers:
    - security-service (track external sharing)
    - audit-service (compliance logging)
    - notification-service (notify stakeholders)
```

**Components Used**:
- Documents Service
- Format Converters (PDF: wkhtmltopdf, DOCX: python-docx, HTML: templates)
- Styling Engine (CSS, headers/footers)
- Watermarking (ImageMagick/PyPDF2)
- Encryption (PyPDF2 for password protection)
- File Storage (temporary storage for downloads)

**Business Value**:
- **Flexibility**: Multiple formats for different use cases
- **Security**: Password protection, watermarks, expiry dates
- **Distribution**: Easy sharing with external parties
- **Printing**: Optimized PDFs for hard copy distribution
- **Web Publishing**: HTML exports for intranet/SharePoint

---

### 6.10 Document Comparison (Versions)

**Business Context**: Side-by-side comparison of document versions to see exactly what changed, why, and when

**Inputs**:
```json
{
  "document_id": "doc_bc_plan_ed_001",
  "comparison_request": {
    "version_a": "v2.3",
    "version_b": "v2.5",
    "comparison_mode": "detailed",
    "highlight_changes": true,
    "show_context": true,
    "filter_changes": {
      "include_types": ["content_updates", "additions", "deletions"],
      "exclude_types": ["formatting_only"]
    }
  }
}
```

**API Endpoint**: `POST /api/documents/{document_id}/compare`

**Comparison Process**:
```
Version Retrieval → Diff Algorithm → Change Classification → Visualization Generation → Context Extraction
  ↓
  1. Retrieve both versions from storage
  2. Run diff algorithm (line-by-line comparison)
  3. Classify changes (added, removed, modified)
  4. Generate side-by-side visualization
  5. Extract surrounding context for each change
  6. Identify significant vs minor changes
  ↓
Return: comparison_report, side_by_side_view, change_summary
```

**Response**:
```json
{
  "comparison_id": "comp_001234",
  "document_id": "doc_bc_plan_ed_001",
  "document_name": "Business Continuity Plan - Emergency Department",
  "versions_compared": {
    "version_a": {
      "version_id": "v2.3",
      "date": "2025-10-15T14:20:00Z",
      "author": "BCM Manager (John Smith)",
      "description": "Annual review - minor updates to recovery procedures"
    },
    "version_b": {
      "version_id": "v2.5",
      "date": "2025-11-25T10:30:00Z",
      "author": "Admin User",
      "description": "Contact list updated + RTO timing changes"
    }
  },
  "time_span": {
    "days_between_versions": 41,
    "intermediate_versions": ["v2.4"],
    "total_versions_between": 1
  },
  "change_summary": {
    "total_changes": 8,
    "lines_added": 6,
    "lines_removed": 5,
    "lines_modified": 3,
    "sections_affected": 3,
    "significance_level": "medium",
    "change_types": {
      "content_updates": 5,
      "contact_changes": 2,
      "table_updates": 1,
      "formatting_changes": 0
    }
  },
  "detailed_changes": [
    {
      "change_id": 1,
      "section": "Section 1.3 - Recovery Time Objectives Summary",
      "change_type": "table_update",
      "significance": "high",
      "changed_in_version": "v2.4 (2025-11-21)",
      "version_a_content": "| EHR Manual Workaround | 15 minutes | Critical | Paper-based patient tracking |",
      "version_b_content": "| EHR Manual Workaround | 10 minutes | Critical | Paper-based patient tracking |",
      "change_description": "RTO reduced from 15 to 10 minutes",
      "change_reason": "Auto-updated based on BIA bia_2025_001 RTO change",
      "diff_visualization": {
        "type": "inline",
        "before": "| EHR Manual Workaround | [removed: 15 minutes] | Critical | Paper-based patient tracking |",
        "after": "| EHR Manual Workaround | [added: 10 minutes] | Critical | Paper-based patient tracking |"
      },
      "impact_assessment": {
        "impact_level": "high",
        "rationale": "RTO timing is critical for operational readiness. Shortened RTO requires faster activation procedures.",
        "affected_sections": ["Section 5.2 - EHR Recovery Procedures"]
      }
    },
    {
      "change_id": 2,
      "section": "Section 5.2 - EHR Recovery Procedures",
      "change_type": "content_update",
      "significance": "high",
      "changed_in_version": "v2.4 (2025-11-21)",
      "version_a_content": "Activate manual EHR workaround within 15 minutes of EHR failure. This includes:\n1. Notify ED staff of EHR outage (target: 2 minutes)\n2. Distribute paper patient tracking forms (target: 5 minutes)\n3. Activate manual medication ordering process (target: 10 minutes)\n4. Confirm all critical processes operational (target: 15 minutes)",
      "version_b_content": "Activate manual EHR workaround within 10 minutes of EHR failure. This includes:\n1. Notify ED staff of EHR outage (target: 2 minutes)\n2. Distribute paper patient tracking forms (target: 3 minutes)\n3. Activate manual medication ordering process (target: 7 minutes)\n4. Confirm all critical processes operational (target: 10 minutes)",
      "change_description": "RTO and sub-step timings updated to reflect 10-minute target",
      "change_reason": "Proportional adjustment to align with new 10-minute RTO from BIA update",
      "diff_visualization": {
        "type": "side_by_side",
        "url": "/api/documents/comparisons/comp_001234/change/2/visual"
      },
      "impact_assessment": {
        "impact_level": "high",
        "rationale": "Operational procedure timing changed. Staff training may be required to achieve faster activation.",
        "affected_sections": ["Section 1.3 - RTO Summary"]
      }
    },
    {
      "change_id": 3,
      "section": "Appendix B - Contact List",
      "change_type": "contact_update",
      "significance": "medium",
      "changed_in_version": "v2.5 (2025-11-25)",
      "version_a_content": "BCM Manager: John Smith\nEmail: john.smith@hospital.com\nPhone: 555-0123\nMobile: 555-0124",
      "version_b_content": "BCM Manager: Jane Doe\nEmail: jane.doe@hospital.com\nPhone: 555-0456\nMobile: 555-0457",
      "change_description": "BCM Manager contact information updated",
      "change_reason": "Personnel change - John Smith retired, Jane Doe assumed BCM Manager role",
      "diff_visualization": {
        "type": "inline",
        "before": "BCM Manager: [removed: John Smith, john.smith@hospital.com, 555-0123]",
        "after": "BCM Manager: [added: Jane Doe, jane.doe@hospital.com, 555-0456]"
      },
      "impact_assessment": {
        "impact_level": "medium",
        "rationale": "Contact information critical for crisis communication. All stakeholders should be notified of new BCM Manager contact.",
        "affected_sections": ["Section 5.0 - Roles and Responsibilities"]
      }
    },
    {
      "change_id": 4,
      "section": "Section 3.4 - Critical Dependencies",
      "change_type": "minor_update",
      "significance": "low",
      "changed_in_version": "v2.4 (2025-11-21)",
      "version_a_content": "External Dependencies: EHR vendor (Epic Systems), Pharmacy system vendor",
      "version_b_content": "External Dependencies: EHR vendor (Epic Systems), Pharmacy system vendor, Medical device integration partner",
      "change_description": "Added medical device integration partner to dependencies list",
      "change_reason": "New dependency identified during BIA update",
      "diff_visualization": {
        "type": "inline",
        "before": "External Dependencies: EHR vendor (Epic Systems), Pharmacy system vendor",
        "after": "External Dependencies: EHR vendor (Epic Systems), Pharmacy system vendor, [added: Medical device integration partner]"
      },
      "impact_assessment": {
        "impact_level": "low",
        "rationale": "Additional dependency noted. Minimal impact on existing procedures.",
        "affected_sections": []
      }
    }
  ],
  "side_by_side_view": {
    "available": true,
    "url": "/api/documents/comparisons/comp_001234/side-by-side",
    "format": "HTML (interactive)",
    "features": [
      "Highlight added content in green",
      "Highlight removed content in red",
      "Highlight modified content in yellow",
      "Click to expand context around changes",
      "Filter changes by section",
      "Jump to next/previous change"
    ]
  },
  "intermediate_versions": {
    "include_v2.4": true,
    "v2.4_summary": {
      "version_id": "v2.4",
      "date": "2025-11-21T09:15:00Z",
      "author": "Auto-Update (AI)",
      "description": "RTO updates based on BIA changes",
      "changes_in_v2.4": [
        "Section 1.3 - RTO table updated",
        "Section 5.2 - EHR recovery timing adjusted",
        "Section 3.4 - Dependency added"
      ],
      "changes_count": 3
    }
  },
  "change_classification": {
    "breaking_changes": 0,
    "high_impact_changes": 2,
    "medium_impact_changes": 1,
    "low_impact_changes": 5,
    "editorial_changes": 0
  },
  "recommendations": {
    "review_required": true,
    "review_reason": "2 high-impact changes detected (RTO timing adjustments). Recommend operational validation.",
    "stakeholders_to_notify": [
      "Emergency Department Director",
      "ED Manager",
      "All ED staff (for new timing requirements)"
    ],
    "follow_up_actions": [
      "Schedule staff training for new 10-minute RTO timeline",
      "Update contact information in all communication systems",
      "Verify new dependencies have proper vendor agreements"
    ]
  },
  "export_options": {
    "pdf_comparison_report": {
      "available": true,
      "url": "/api/documents/comparisons/comp_001234/export/pdf",
      "description": "Full comparison report in PDF format"
    },
    "excel_change_log": {
      "available": true,
      "url": "/api/documents/comparisons/comp_001234/export/excel",
      "description": "Change log in spreadsheet format"
    },
    "word_track_changes": {
      "available": true,
      "url": "/api/documents/comparisons/comp_001234/export/docx",
      "description": "Document with Microsoft Word track changes markup"
    }
  }
}
```

**Visual Comparison Example** (HTML side-by-side view):
```html
<!-- Side-by-side comparison UI -->
<div class="document-comparison">
  <div class="comparison-header">
    <h2>Document Comparison: BC Plan - Emergency Department</h2>
    <div class="version-info">
      <div class="version-a">
        <strong>Version 2.3</strong>
        <span>Oct 15, 2025</span>
        <span>by BCM Manager</span>
      </div>
      <div class="comparison-icon">⇔</div>
      <div class="version-b">
        <strong>Version 2.5</strong>
        <span>Nov 25, 2025</span>
        <span>by Admin User</span>
      </div>
    </div>
  </div>

  <div class="comparison-body split-view">
    <div class="version-a-content">
      <h3>Section 1.3 - RTO Summary</h3>
      <table>
        <tr>
          <td>EHR Manual Workaround</td>
          <td class="removed">15 minutes</td>
          <td>Critical</td>
        </tr>
      </table>
    </div>

    <div class="version-b-content">
      <h3>Section 1.3 - RTO Summary</h3>
      <table>
        <tr>
          <td>EHR Manual Workaround</td>
          <td class="added">10 minutes</td>
          <td>Critical</td>
        </tr>
      </table>
      <div class="change-note">
        Change: RTO reduced from 15 to 10 minutes (Auto-updated based on BIA)
      </div>
    </div>
  </div>

  <div class="comparison-controls">
    <button>Previous Change</button>
    <button>Next Change</button>
    <button>Expand All Context</button>
    <button>Export Report</button>
  </div>
</div>
```

**Three-Way Comparison Example** (comparing v2.3 → v2.4 → v2.5):
```json
{
  "three_way_comparison": {
    "document_id": "doc_bc_plan_ed_001",
    "versions": ["v2.3", "v2.4", "v2.5"],
    "comparison_type": "evolutionary",
    "change_tracking": {
      "v2.3_to_v2.4": {
        "date": "2025-11-21",
        "changes": 3,
        "author": "Auto-Update (AI)",
        "theme": "RTO timing adjustments from BIA update"
      },
      "v2.4_to_v2.5": {
        "date": "2025-11-25",
        "changes": 1,
        "author": "Admin User",
        "theme": "Personnel contact change"
      }
    },
    "evolution_visualization": {
      "url": "/api/documents/comparisons/comp_threeway_001/visual",
      "shows": "Side-by-side-by-side view showing progression through all 3 versions"
    }
  }
}
```

**Events Published**:
```yaml
- event: document.comparison.performed
  payload:
    document_id: doc_bc_plan_ed_001
    version_a: v2.3
    version_b: v2.5
    changes_found: 8
    performed_by: bcm.manager@hospital.com
  subscribers:
    - analytics-service (track comparison usage)
    - audit-service (log activity)
```

**Components Used**:
- Documents Service
- Diff Algorithm (difflib, git-diff)
- Version Control Storage
- Visualization Engine (HTML/CSS rendering)
- NLP (change significance assessment)
- Export Generators (PDF, DOCX, Excel)

**Business Value**:
- **Transparency**: See exactly what changed between versions
- **Audit Trail**: Understand evolution of document over time
- **Review Efficiency**: Quickly identify significant vs minor changes
- **Stakeholder Communication**: Export comparison reports for distribution
- **Quality Assurance**: Catch unintended changes before approval

---

### 6.11 Document Archive Management

**Business Context**: Automatically archive superseded documents, maintain retention policies, ensure regulatory compliance with document lifecycle management

**Inputs**:
```json
{
  "document_id": "doc_bc_plan_ed_001",
  "archive_policy": {
    "archive_trigger": "new_version_approved",
    "archive_previous_versions": true,
    "retention_period": "7_years",
    "retention_reason": "ISO 22301 + HIPAA regulatory requirements",
    "archive_storage": "cold_storage",
    "archival_format": "pdf_a",
    "metadata_preservation": "full",
    "accessibility": "read_only",
    "automatic_deletion_after_retention": false,
    "deletion_requires_approval": true
  }
}
```

**API Endpoint**: `POST /api/documents/{document_id}/archive-policy/set`

**Archive Management Architecture**:
```
Version Approval → Archive Trigger → Archive Preparation → Move to Archive Storage → Index Update
  ↓
  When new version approved:
  1. Identify superseded versions
  2. Prepare for archival (convert to PDF/A, embed metadata)
  3. Move to cold storage
  4. Update access permissions (read-only)
  5. Update search index (mark as archived)
  6. Set retention expiry date
  ↓
Track: archived documents, retention periods, deletion eligibility
```

**Response**:
```json
{
  "document_id": "doc_bc_plan_ed_001",
  "document_name": "Business Continuity Plan - Emergency Department",
  "current_version": "v2.6",
  "archive_status": {
    "archive_policy": "active",
    "auto_archive_enabled": true,
    "retention_period": "7 years",
    "retention_rationale": "ISO 22301 (Clause 7.5.3) + HIPAA require minimum 7-year retention for BC documentation"
  },
  "archived_versions": {
    "total_archived": 5,
    "versions": [
      {
        "version_id": "v2.5",
        "original_date": "2025-11-25",
        "archived_date": "2025-12-10",
        "archived_reason": "Superseded by v2.6",
        "archive_storage": "cold_storage",
        "archive_format": "PDF/A-1b",
        "file_size": "3.2 MB",
        "retention_expires": "2032-11-25",
        "days_until_expiry": 2547,
        "access": "read_only",
        "deletion_eligible": false
      },
      {
        "version_id": "v2.4",
        "original_date": "2025-11-21",
        "archived_date": "2025-11-25",
        "archived_reason": "Superseded by v2.5",
        "archive_storage": "cold_storage",
        "archive_format": "PDF/A-1b",
        "file_size": "3.1 MB",
        "retention_expires": "2032-11-21",
        "days_until_expiry": 2543,
        "access": "read_only",
        "deletion_eligible": false
      },
      {
        "version_id": "v2.3",
        "original_date": "2025-10-15",
        "archived_date": "2025-11-21",
        "archived_reason": "Superseded by v2.4",
        "archive_storage": "cold_storage",
        "archive_format": "PDF/A-1b",
        "file_size": "3.0 MB",
        "retention_expires": "2032-10-15",
        "days_until_expiry": 2506,
        "access": "read_only",
        "deletion_eligible": false
      },
      {
        "version_id": "v2.2",
        "original_date": "2025-06-10",
        "archived_date": "2025-10-15",
        "archived_reason": "Superseded by v2.3",
        "archive_storage": "cold_storage",
        "archive_format": "PDF/A-1b",
        "file_size": "2.9 MB",
        "retention_expires": "2032-06-10",
        "days_until_expiry": 2379,
        "access": "read_only",
        "deletion_eligible": false
      },
      {
        "version_id": "v2.1",
        "original_date": "2025-01-05",
        "archived_date": "2025-06-10",
        "archived_reason": "Superseded by v2.2",
        "archive_storage": "cold_storage",
        "archive_format": "PDF/A-1b",
        "file_size": "2.8 MB",
        "retention_expires": "2032-01-05",
        "days_until_expiry": 2223,
        "access": "read_only",
        "deletion_eligible": false
      }
    ]
  },
  "archive_storage_info": {
    "storage_tier": "cold_storage",
    "storage_location": "AWS S3 Glacier Deep Archive",
    "retrieval_time": "12-48 hours",
    "storage_cost": "$0.00099/GB/month",
    "total_archived_size": "15.0 MB",
    "estimated_monthly_cost": "$0.015"
  },
  "retention_compliance": {
    "compliance_status": "compliant",
    "regulatory_requirements": [
      {
        "regulation": "ISO 22301:2019",
        "clause": "7.5.3 - Control of documented information",
        "requirement": "Retain BC documentation for appropriate period considering legal, regulatory, and business requirements",
        "organization_policy": "7 years minimum",
        "status": "compliant"
      },
      {
        "regulation": "HIPAA",
        "requirement": "Maintain BC and disaster recovery documentation for minimum 6 years",
        "organization_policy": "7 years (exceeds requirement)",
        "status": "compliant"
      }
    ]
  }
}
```

**Archival Process Example** (when v2.6 approved, v2.5 archived):
```json
{
  "archive_event": {
    "trigger": "new_version_approved",
    "document_id": "doc_bc_plan_ed_001",
    "new_version": "v2.6",
    "superseded_version": "v2.5",
    "archive_timestamp": "2025-12-10T10:00:00Z"
  },
  "archival_process": {
    "step_1_preparation": {
      "action": "Convert to archival format",
      "original_format": "DOCX",
      "archival_format": "PDF/A-1b",
      "conversion_status": "completed",
      "file_size_before": "2.1 MB (DOCX)",
      "file_size_after": "3.2 MB (PDF/A)"
    },
    "step_2_metadata_embedding": {
      "action": "Embed metadata in archival file",
      "metadata_embedded": {
        "title": "BC Plan - Emergency Department v2.5",
        "author": "Admin User",
        "created_date": "2025-11-25",
        "archived_date": "2025-12-10",
        "superseded_by": "v2.6",
        "retention_period": "7 years",
        "retention_expires": "2032-11-25",
        "classification": "Internal Confidential",
        "regulatory_hold": false
      },
      "status": "completed"
    },
    "step_3_storage_migration": {
      "action": "Move to cold storage",
      "source_storage": "hot_storage (PostgreSQL + S3 Standard)",
      "destination_storage": "cold_storage (S3 Glacier Deep Archive)",
      "migration_status": "completed",
      "migration_time": "15 seconds",
      "storage_cost_reduction": "97% (from $0.023/GB/month to $0.00099/GB/month)"
    },
    "step_4_access_update": {
      "action": "Update access permissions",
      "previous_access": "read, edit (for authorized users)",
      "new_access": "read_only (archive access)",
      "access_note": "Archived versions are read-only. Retrieval time: 12-48 hours for cold storage."
    },
    "step_5_index_update": {
      "action": "Update search index",
      "indexed_as": "archived",
      "search_visibility": "visible in archive search only",
      "tag_added": "archived_version"
    },
    "step_6_retention_tracking": {
      "action": "Set retention expiry",
      "retention_period": "7 years",
      "retention_start_date": "2025-11-25 (original approval date)",
      "retention_expiry_date": "2032-11-25",
      "auto_delete_enabled": false,
      "deletion_approval_required": true
    }
  },
  "notification_sent": {
    "to": "document_owner",
    "message": "BC Plan - Emergency Department v2.5 has been archived. Current version is now v2.6."
  }
}
```

**Archive Retrieval Example** (accessing archived version):
```json
{
  "retrieval_request": {
    "document_id": "doc_bc_plan_ed_001",
    "version": "v2.3",
    "requested_by": "auditor@hospital.com",
    "request_reason": "ISO 22301 certification audit - need to review historical BC plan from Oct 2025"
  },
  "retrieval_process": {
    "status": "initiated",
    "storage_tier": "cold_storage (S3 Glacier Deep Archive)",
    "estimated_retrieval_time": "12-48 hours",
    "retrieval_cost": "$0.02 (per retrieval)",
    "expedited_option": {
      "available": true,
      "retrieval_time": "1-5 minutes",
      "cost": "$10.00",
      "note": "Expedited retrieval for urgent needs"
    },
    "notification": {
      "when_ready": "Email sent to auditor@hospital.com when document available",
      "download_link_expiry": "24 hours after availability"
    }
  },
  "retrieval_result": {
    "status": "completed",
    "retrieval_time": "14 hours",
    "document_available": true,
    "download_url": "/api/documents/doc_bc_plan_ed_001/archive/v2.3/download",
    "download_expires": "2025-12-12T10:00:00Z",
    "format": "PDF/A-1b",
    "file_size": "3.0 MB",
    "watermark": "Archived Version - v2.3 - Retrieved Dec 11, 2025"
  }
}
```

**Retention Expiry & Deletion Example**:
```json
{
  "retention_expiry_report": {
    "report_date": "2032-11-25",
    "document_id": "doc_bc_plan_ed_001",
    "version": "v2.5",
    "retention_status": "expired",
    "retention_period": "7 years",
    "archived_date": "2025-11-25",
    "retention_expiry_date": "2032-11-25",
    "days_since_expiry": 0,
    "deletion_eligibility": {
      "eligible_for_deletion": true,
      "auto_delete_enabled": false,
      "deletion_requires_approval": true,
      "legal_hold": {
        "active": false,
        "reason": null
      },
      "compliance_check": {
        "no_active_audits": true,
        "no_litigation_hold": true,
        "no_regulatory_investigation": true
      }
    },
    "deletion_approval_process": {
      "approval_required_from": ["BCM Manager", "Legal Counsel"],
      "approval_deadline": "2032-12-25 (30 days grace period)",
      "approval_status": "pending",
      "deletion_action": {
        "if_approved": "Permanent deletion from archive storage",
        "if_rejected": "Extend retention period",
        "if_no_response": "Default: extend retention 1 year"
      }
    }
  }
}
```

**Archive Analytics Dashboard**:
```json
{
  "archive_analytics": {
    "organization": "City General Hospital",
    "total_documents_managed": 247,
    "active_documents": 196,
    "archived_versions": 512,
    "archive_statistics": {
      "total_archive_size": "8.4 GB",
      "monthly_storage_cost": "$8.32",
      "average_document_retention": "7 years",
      "retention_compliance_rate": "100%"
    },
    "retention_expiry_upcoming": {
      "next_30_days": 0,
      "next_90_days": 2,
      "next_365_days": 15
    },
    "archive_by_document_type": {
      "business_continuity_plans": {
        "active": 15,
        "archived_versions": 87,
        "retention_period": "7 years"
      },
      "risk_registers": {
        "active": 12,
        "archived_versions": 45,
        "retention_period": "10 years"
      },
      "exercise_reports": {
        "active": 8,
        "archived_versions": 124,
        "retention_period": "5 years"
      },
      "policies": {
        "active": 23,
        "archived_versions": 67,
        "retention_period": "permanent"
      }
    },
    "compliance_summary": {
      "iso_22301_compliant": true,
      "hipaa_compliant": true,
      "sox_compliant": true,
      "overdue_deletions": 0,
      "legal_holds_active": 0
    }
  }
}
```

**Events Published**:
```yaml
- event: document.archived
  payload:
    document_id: doc_bc_plan_ed_001
    version: v2.5
    archived_date: 2025-12-10
    retention_expires: 2032-11-25
  subscribers:
    - notification-service (notify stakeholders)
    - compliance-service (track retention)
    - audit-service (log archival)

- event: document.retention.expiring_soon
  payload:
    document_id: doc_bc_plan_ed_001
    version: v2.5
    retention_expires: 2032-11-25
    days_until_expiry: 30
  subscribers:
    - notification-service (alert legal/BCM team)
    - compliance-service (initiate disposal review)

- event: document.archive.retrieved
  payload:
    document_id: doc_bc_plan_ed_001
    version: v2.3
    retrieved_by: auditor@hospital.com
    reason: audit_review
  subscribers:
    - audit-service (log retrieval)
    - analytics-service (track archive usage)
```

**Components Used**:
- Documents Service
- Archive Storage (AWS S3 Glacier Deep Archive)
- PDF/A Converter (archival format)
- Retention Manager (policy enforcement)
- Scheduler (retention expiry monitoring)
- Compliance Tracking (regulatory requirements)

**Business Value**:
- **Compliance**: Meet ISO 22301, HIPAA, SOX retention requirements
- **Cost Savings**: Cold storage 97% cheaper than hot storage
- **Audit Trail**: Complete history preserved for investigations/audits
- **Legal Protection**: Defensible disposition process
- **Storage Efficiency**: Automatic lifecycle management reduces manual overhead

---

### 6.12 Document Collaboration (Real-Time)

**Business Context**: Multiple stakeholders need to collaborate on BC plan development in real-time with live editing and comments

**Inputs**:
```json
{
  "document_id": "doc_bc_plan_it_001",
  "collaboration_mode": "real_time",
  "collaborators": [
    {
      "user": "cio@hospital.com",
      "role": "editor",
      "display_name": "Tom Williams (CIO)"
    },
    {
      "user": "it.manager@hospital.com",
      "role": "editor",
      "display_name": "Sarah Lee (IT Manager)"
    },
    {
      "user": "bcm.manager@hospital.com",
      "role": "reviewer",
      "display_name": "Jane Doe (BCM Manager)"
    }
  ],
  "collaboration_features": {
    "live_editing": true,
    "live_cursor_tracking": true,
    "comments": true,
    "suggestions": true,
    "chat": true
  }
}
```

**API Endpoint**: `WS /api/documents/{document_id}/collaborate`

**Real-Time Collaboration Architecture**:
```
WebSocket Connection → Operational Transform (OT) → Conflict Resolution → All Participants
  ↓
  Real-time updates:
  1. User A types → broadcast to User B, C
  2. Cursor positions synchronized
  3. Comments/suggestions appear instantly
  4. Chat messages delivered in real-time
  5. Conflict resolution automatic (OT algorithm)
  ↓
All users see same content in <100ms
```

**Collaboration Session**:
```json
{
  "session_id": "collab_session_001",
  "document_id": "doc_bc_plan_it_001",
  "document_name": "BC Plan - IT Department (Draft)",
  "active_collaborators": [
    {
      "user": "Tom Williams (CIO)",
      "role": "editor",
      "status": "active",
      "last_active": "2025-12-05T14:32:15Z",
      "cursor_position": {
        "section": "Section 4.2 - Data Center Recovery",
        "line": 45,
        "color": "blue"
      },
      "current_action": "editing"
    },
    {
      "user": "Sarah Lee (IT Manager)",
      "role": "editor",
      "status": "active",
      "last_active": "2025-12-05T14:32:18Z",
      "cursor_position": {
        "section": "Section 5.1 - Roles and Responsibilities",
        "line": 89,
        "color": "green"
      },
      "current_action": "adding_comment"
    },
    {
      "user": "Jane Doe (BCM Manager)",
      "role": "reviewer",
      "status": "active",
      "last_active": "2025-12-05T14:32:10Z",
      "cursor_position": {
        "section": "Section 1.0 - Introduction",
        "line": 5,
        "color": "purple"
      },
      "current_action": "reading"
    }
  ],
  "live_editing_example": {
    "timestamp": "2025-12-05T14:32:20Z",
    "edit_by": "Tom Williams (CIO)",
    "section": "Section 4.2 - Data Center Recovery",
    "original_text": "Data center recovery RTO: 24 hours",
    "edit_operation": {
      "type": "replace",
      "position": 45,
      "remove": "24 hours",
      "insert": "4 hours (updated based on new SAN replication capability)",
      "broadcast_to": ["Sarah Lee", "Jane Doe"],
      "conflict_status": "none"
    },
    "all_users_see": "Data center recovery RTO: 4 hours (updated based on new SAN replication capability) [Tom Williams is typing...]",
    "change_tracked": {
      "revision_id": "rev_1234",
      "author": "Tom Williams",
      "timestamp": "2025-12-05T14:32:20Z",
      "tracked_in_version_history": true
    }
  },
  "comment_example": {
    "timestamp": "2025-12-05T14:32:25Z",
    "comment_by": "Sarah Lee (IT Manager)",
    "section": "Section 5.1 - Roles and Responsibilities",
    "line": 89,
    "comment_text": "@Tom - Should we add the new Cloud Infrastructure Manager role here? They're now responsible for AWS/Azure failover.",
    "comment_type": "question",
    "mentions": ["Tom Williams"],
    "comment_id": "cmt_456",
    "status": "open",
    "visible_to": "all_collaborators",
    "notification_sent": {
      "to": "Tom Williams",
      "type": "mention_notification",
      "delivered": "instant"
    }
  },
  "suggestion_example": {
    "timestamp": "2025-12-05T14:33:00Z",
    "suggestion_by": "Jane Doe (BCM Manager)",
    "section": "Section 3.0 - Critical IT Services",
    "suggestion_text": "Consider adding 'Email Services' as a critical IT service. It's not currently listed but is essential for crisis communication.",
    "suggestion_type": "content_addition",
    "suggestion_id": "sug_789",
    "status": "pending",
    "actions_available": [
      {
        "action": "accept",
        "effect": "Add 'Email Services' to critical services list",
        "can_be_done_by": ["editors"]
      },
      {
        "action": "reject",
        "effect": "Dismiss suggestion",
        "can_be_done_by": ["editors"]
      },
      {
        "action": "discuss",
        "effect": "Reply to suggestion with comment",
        "can_be_done_by": ["all"]
      }
    ]
  },
  "chat_example": {
    "timestamp": "2025-12-05T14:34:00Z",
    "chat_by": "Tom Williams",
    "message": "@Sarah - Good point about Cloud Infrastructure Manager role. Let's add it. Can you draft the responsibilities for that role?",
    "mentions": ["Sarah Lee"],
    "message_id": "msg_101",
    "chat_history": [
      {
        "timestamp": "2025-12-05T14:32:25Z",
        "user": "Sarah Lee",
        "message": "@Tom - Should we add the new Cloud Infrastructure Manager role here?"
      },
      {
        "timestamp": "2025-12-05T14:34:00Z",
        "user": "Tom Williams",
        "message": "@Sarah - Good point about Cloud Infrastructure Manager role. Let's add it. Can you draft the responsibilities for that role?"
      }
    ]
  },
  "conflict_resolution_example": {
    "timestamp": "2025-12-05T14:35:00Z",
    "conflict_detected": false,
    "note": "Tom and Sarah editing different sections - no conflict",
    "operational_transform_applied": true,
    "example_scenario": "If both users edited same line simultaneously, OT algorithm would merge changes intelligently or prompt for manual resolution."
  },
  "collaboration_metrics": {
    "session_duration": "42 minutes",
    "total_edits": 37,
    "comments_added": 8,
    "suggestions_made": 3,
    "chat_messages": 12,
    "conflicts_resolved": 0,
    "participants_active": 3,
    "engagement_score": 9.2
  }
}
```

**Events Published**:
```yaml
- event: document.collaboration.started
  payload:
    document_id: doc_bc_plan_it_001
    collaborators: 3
    session_id: collab_session_001

- event: document.edit.realtime
  count: 37
  avg_latency: 87ms

- event: document.comment.added
  count: 8

- event: document.collaboration.ended
  payload:
    session_id: collab_session_001
    duration_minutes: 42
    total_changes: 37
```

**Components Used**:
- Documents Service
- WebSocket (real-time communication)
- Operational Transform (OT) algorithm (conflict resolution)
- PostgreSQL (persistent storage)
- Redis (real-time state)

**Business Value**:
- **Real-Time**: All users see changes instantly (<100ms latency)
- **No Conflicts**: Intelligent merge of simultaneous edits
- **Context**: See who's editing what, where cursors are
- **Communication**: Comments, suggestions, chat built-in
- **Version Control**: All changes tracked automatically

---

### 6.13 Document Import (Bulk)

**Business Context**: Import multiple existing BC documents at once with automatic classification, metadata extraction, and organization

**Inputs**:
```json
{
  "bulk_import_request": {
    "import_method": "file_upload",
    "files": [
      {
        "file_name": "BC_Plan_Emergency_Dept.pdf",
        "file_size": "3.2 MB",
        "file_type": "pdf"
      },
      {
        "file_name": "BC_Plan_Radiology.docx",
        "file_size": "2.1 MB",
        "file_type": "docx"
      },
      {
        "file_name": "Risk_Register_2025.xlsx",
        "file_size": "1.5 MB",
        "file_type": "xlsx"
      },
      {
        "file_name": "BIA_Report_IT_Department.pdf",
        "file_size": "2.8 MB",
        "file_type": "pdf"
      }
    ],
    "import_options": {
      "auto_classify": true,
      "extract_metadata": true,
      "create_versions": true,
      "apply_access_control": true,
      "link_related_documents": true,
      "notify_document_owners": true
    }
  }
}
```

**API Endpoint**: `POST /api/documents/import/bulk`

**Bulk Import Process**:
```
File Upload → Validation → Parallel Processing → Classification → Metadata Extraction → Organization
  ↓
  For each file (parallel):
  1. Validate file format and size
  2. Extract content (OCR if needed for PDFs)
  3. AI classification (type, department, ISO clause)
  4. Extract metadata (dates, contacts, RTOs)
  5. Detect related documents
  6. Apply access control
  7. Index for search
  ↓
Return: import_summary, document_list, issues
```

**Response**:
```json
{
  "import_id": "import_bulk_001",
  "import_status": "completed",
  "import_summary": {
    "total_files": 4,
    "successfully_imported": 4,
    "failed_imports": 0,
    "warnings": 0,
    "processing_time": "42 seconds",
    "import_date": "2025-12-10T14:00:00Z"
  },
  "imported_documents": [
    {
      "document_id": "doc_bc_plan_ed_001",
      "original_file_name": "BC_Plan_Emergency_Dept.pdf",
      "stored_file_name": "doc_bc_plan_ed_001_v1.0.pdf",
      "file_size": "3.2 MB",
      "import_status": "success",
      "ai_classification": {
        "document_type": "business_continuity_plan",
        "department": "Emergency Department",
        "iso_clause": "8.4.3 - Business continuity procedures",
        "confidence": 0.94,
        "tags": ["business_continuity", "emergency_department", "iso_22301", "clinical_operations"]
      },
      "extracted_metadata": {
        "title": "Business Continuity Plan - Emergency Department",
        "version": "v2.5",
        "author": "BCM Team",
        "creation_date": "2024-06-15",
        "last_modified": "2025-11-25",
        "approval_date": "2025-12-08",
        "approved_by": "Dr. Michael Chen",
        "next_review_date": "2026-12-08",
        "rto_values_found": 3,
        "contact_count": 12
      },
      "access_control_applied": {
        "classification": "Internal Confidential",
        "read_access": ["emergency_dept_staff", "bcm_team", "executives"],
        "edit_access": ["emergency_dept_director", "bcm_manager"]
      },
      "related_documents_detected": [
        {
          "document_id": "doc_bia_it_department_001",
          "relationship": "referenced_in_document",
          "confidence": 0.87
        }
      ],
      "search_indexed": true,
      "document_url": "/api/documents/doc_bc_plan_ed_001"
    },
    {
      "document_id": "doc_bc_plan_radiology_001",
      "original_file_name": "BC_Plan_Radiology.docx",
      "stored_file_name": "doc_bc_plan_radiology_001_v1.0.docx",
      "file_size": "2.1 MB",
      "import_status": "success",
      "ai_classification": {
        "document_type": "business_continuity_plan",
        "department": "Radiology",
        "iso_clause": "8.4.3 - Business continuity procedures",
        "confidence": 0.92,
        "tags": ["business_continuity", "radiology", "iso_22301", "medical_imaging", "pacs"]
      },
      "extracted_metadata": {
        "title": "Business Continuity Plan - Radiology Department",
        "version": "v1.0",
        "author": "Radiology Director",
        "creation_date": "2025-09-01",
        "last_modified": "2025-11-30",
        "approval_date": "2025-12-05",
        "approved_by": "Radiology Director",
        "next_review_date": "2026-12-05",
        "rto_values_found": 5,
        "contact_count": 8
      },
      "access_control_applied": {
        "classification": "Internal Confidential",
        "read_access": ["radiology_staff", "bcm_team", "executives"],
        "edit_access": ["radiology_director", "bcm_manager"]
      },
      "related_documents_detected": [
        {
          "document_id": "doc_bc_plan_ed_001",
          "relationship": "similar_department",
          "confidence": 0.72
        }
      ],
      "search_indexed": true,
      "document_url": "/api/documents/doc_bc_plan_radiology_001"
    },
    {
      "document_id": "doc_risk_register_2025_001",
      "original_file_name": "Risk_Register_2025.xlsx",
      "stored_file_name": "doc_risk_register_2025_001_v1.0.xlsx",
      "file_size": "1.5 MB",
      "import_status": "success",
      "ai_classification": {
        "document_type": "risk_register",
        "department": "Enterprise",
        "iso_clause": "6.1.2 - Risk assessment",
        "confidence": 0.96,
        "tags": ["risk_management", "iso_22301", "enterprise_risk", "risk_assessment"]
      },
      "extracted_metadata": {
        "title": "Enterprise Risk Register 2025",
        "version": "v3.2",
        "author": "Risk Management Team",
        "creation_date": "2025-01-01",
        "last_modified": "2025-12-01",
        "total_risks": 87,
        "high_priority_risks": 12,
        "review_frequency": "quarterly"
      },
      "access_control_applied": {
        "classification": "Internal Confidential",
        "read_access": ["risk_committee", "bcm_team", "executives", "department_heads"],
        "edit_access": ["risk_manager", "bcm_manager"]
      },
      "related_documents_detected": [
        {
          "document_id": "doc_bc_plan_ed_001",
          "relationship": "risks_mitigated_by",
          "confidence": 0.81
        },
        {
          "document_id": "doc_bc_plan_radiology_001",
          "relationship": "risks_mitigated_by",
          "confidence": 0.78
        }
      },
      "search_indexed": true,
      "document_url": "/api/documents/doc_risk_register_2025_001"
    },
    {
      "document_id": "doc_bia_it_department_001",
      "original_file_name": "BIA_Report_IT_Department.pdf",
      "stored_file_name": "doc_bia_it_department_001_v1.0.pdf",
      "file_size": "2.8 MB",
      "import_status": "success",
      "ai_classification": {
        "document_type": "bia_report",
        "department": "IT Department",
        "iso_clause": "8.2 - Business impact analysis",
        "confidence": 0.95,
        "tags": ["bia", "business_impact_analysis", "iso_22301", "it_services", "rto_rpo"]
      },
      "extracted_metadata": {
        "title": "Business Impact Analysis - IT Department",
        "version": "v2.1",
        "author": "BIA Team",
        "creation_date": "2025-08-15",
        "last_modified": "2025-11-15",
        "approval_date": "2025-11-20",
        "approved_by": "CIO",
        "processes_analyzed": 15,
        "critical_processes": 8,
        "rto_values_found": 15
      },
      "access_control_applied": {
        "classification": "Internal Confidential",
        "read_access": ["it_department", "bcm_team", "executives"],
        "edit_access": ["cio", "bcm_manager"]
      },
      "related_documents_detected": [
        {
          "document_id": "doc_bc_plan_ed_001",
          "relationship": "provides_data_for",
          "confidence": 0.89
        }
      ],
      "search_indexed": true,
      "document_url": "/api/documents/doc_bia_it_department_001"
    }
  ],
  "import_analytics": {
    "document_types_imported": {
      "business_continuity_plan": 2,
      "risk_register": 1,
      "bia_report": 1
    },
    "departments_identified": {
      "Emergency Department": 1,
      "Radiology": 1,
      "Enterprise": 1,
      "IT Department": 1
    },
    "total_metadata_extracted": 67,
    "total_rto_values_found": 23,
    "total_tags_generated": 32,
    "related_document_links_created": 6
  },
  "post_import_actions": [
    {
      "action": "Document owners notified",
      "status": "completed",
      "notifications_sent": 4,
      "recipients": ["dr.chen@hospital.com", "radiology.director@hospital.com", "risk.manager@hospital.com", "cio@hospital.com"]
    },
    {
      "action": "Search index updated",
      "status": "completed",
      "documents_indexed": 4
    },
    {
      "action": "Related documents linked",
      "status": "completed",
      "total_links_created": 6
    },
    {
      "action": "Access control policies applied",
      "status": "completed",
      "policies_set": 4
    }
  ],
  "recommendations": [
    {
      "recommendation": "Review AI classifications",
      "reason": "Verify auto-classification accuracy before relying on document organization",
      "priority": "medium",
      "action_url": "/api/documents/import/import_bulk_001/review-classifications"
    },
    {
      "recommendation": "Complete missing metadata",
      "reason": "Some documents have incomplete contact lists or testing schedules",
      "priority": "low",
      "documents_affected": 2
    },
    {
      "recommendation": "Set review schedules",
      "reason": "Ensure all imported documents have review cycles configured",
      "priority": "medium",
      "action_url": "/api/documents/import/import_bulk_001/configure-reviews"
    }
  ]
}
```

**Import with Issues Example**:
```json
{
  "import_id": "import_bulk_002",
  "import_status": "completed_with_warnings",
  "import_summary": {
    "total_files": 5,
    "successfully_imported": 3,
    "failed_imports": 1,
    "warnings": 1,
    "processing_time": "38 seconds"
  },
  "imported_documents": [
    "... (3 successful imports)"
  ],
  "failed_imports": [
    {
      "file_name": "Old_BC_Plan_Corrupted.pdf",
      "file_size": "4.2 MB",
      "failure_reason": "File corrupted - unable to extract content",
      "error_code": "EXTRACTION_FAILED",
      "recommendation": "Re-export file from original source and retry import"
    }
  ],
  "warnings": [
    {
      "document_id": "doc_policy_old_format_001",
      "file_name": "Old_Policy_Document.doc",
      "warning_type": "legacy_format",
      "message": "Document imported but format is outdated (.doc instead of .docx). Consider converting to modern format.",
      "impact": "low",
      "recommendation": "Export as DOCX for better compatibility"
    }
  ]
}
```

**Events Published**:
```yaml
- event: document.bulk_import.started
  payload:
    import_id: import_bulk_001
    total_files: 4
    initiated_by: admin@hospital.com
  subscribers:
    - notification-service (notify progress)
    - analytics-service (track import activity)

- event: document.bulk_import.completed
  payload:
    import_id: import_bulk_001
    successfully_imported: 4
    failed: 0
    processing_time: 42
  subscribers:
    - notification-service (notify completion)
    - audit-service (log import)

- event: document.imported
  count: 4
  payload:
    document_id: [varies]
    document_type: [varies]
    department: [varies]
  subscribers:
    - search-indexer (index new documents)
    - compliance-service (track document inventory)
```

**Components Used**:
- Documents Service
- AI Foundation (Claude Sonnet - classification)
- OCR Engine (Tesseract for scanned PDFs)
- NLP (metadata extraction)
- File Parsers (PDF, DOCX, XLSX)
- Qdrant (search indexing)
- PostgreSQL (document metadata)

**Business Value**:
- **Time Savings**: Import 100+ documents in minutes instead of days of manual entry
- **Automatic Organization**: AI classification and tagging eliminates manual categorization
- **Metadata Extraction**: Auto-populate document details from content
- **Relationship Detection**: Automatically link related documents
- **Quality Control**: Identify issues during import for immediate resolution

---

### 6.14 Document Audit Trail

**Business Context**: Complete tracking of all document lifecycle events for compliance, security, and forensic investigation

**Inputs**:
```json
{
  "audit_query": {
    "document_id": "doc_bc_plan_ed_001",
    "time_range": {
      "start_date": "2025-01-01",
      "end_date": "2025-12-31"
    },
    "event_types": [
      "created",
      "viewed",
      "edited",
      "approved",
      "version_created",
      "access_granted",
      "access_denied",
      "exported",
      "archived"
    ],
    "include_user_details": true,
    "include_ip_addresses": true,
    "include_device_info": true
  }
}
```

**API Endpoint**: `POST /api/documents/{document_id}/audit-trail`

**Audit Trail Architecture**:
```
Every Document Action → Event Capture → Enrichment → Immutable Storage → Indexed Search
  ↓
  For each action:
  1. Capture event details (who, what, when, where)
  2. Enrich with context (IP, device, auth method)
  3. Store in append-only audit log (PostgreSQL + S3)
  4. Index for fast querying (Elasticsearch)
  5. Apply retention policy (7+ years)
  ↓
Track: complete document lifecycle history
```

**Response**:
```json
{
  "audit_trail_id": "audit_trail_001",
  "document_id": "doc_bc_plan_ed_001",
  "document_name": "Business Continuity Plan - Emergency Department",
  "query_parameters": {
    "time_range": "2025-01-01 to 2025-12-31",
    "total_events_found": 342,
    "query_time": "0.3 seconds"
  },
  "audit_summary": {
    "total_events": 342,
    "events_by_type": {
      "viewed": 265,
      "edited": 12,
      "version_created": 5,
      "approved": 3,
      "exported": 8,
      "access_denied": 2,
      "archived": 5,
      "comments_added": 15,
      "access_granted_temporary": 1,
      "review_completed": 2,
      "rollback_performed": 1
    },
    "unique_users": 43,
    "unique_ip_addresses": 28,
    "time_span": "365 days"
  },
  "audit_events": [
    {
      "event_id": "evt_001234",
      "timestamp": "2025-12-08T16:45:00Z",
      "event_type": "approved",
      "event_category": "lifecycle",
      "severity": "high",
      "user": {
        "user_id": "user_789",
        "name": "Dr. Sarah Johnson",
        "email": "sarah.johnson@hospital.com",
        "role": "CMO"
      },
      "action_details": {
        "action": "Approved document version v2.5",
        "workflow_id": "wf_approval_001",
        "approval_level": "Stage 3 of 3 (final approval)",
        "comment": "Approved. Critical component of our clinical continuity capabilities.",
        "previous_status": "pending_approval",
        "new_status": "approved"
      },
      "context": {
        "ip_address": "10.20.30.55",
        "device": "Hospital Executive Workstation",
        "location": "Executive Office Building",
        "network": "internal",
        "authentication_method": "SSO + MFA",
        "session_id": "sess_xyz789"
      },
      "related_events": [
        "evt_001233 (approval request sent)",
        "evt_001235 (notifications sent to stakeholders)"
      ]
    },
    {
      "event_id": "evt_001180",
      "timestamp": "2025-11-25T10:30:00Z",
      "event_type": "version_created",
      "event_category": "lifecycle",
      "severity": "medium",
      "user": {
        "user_id": "user_456",
        "name": "Admin User",
        "email": "admin@hospital.com",
        "role": "Administrator"
      },
      "action_details": {
        "action": "Created new version v2.5",
        "previous_version": "v2.4",
        "new_version": "v2.5",
        "change_description": "Update contact list - replace retiring BCM Manager",
        "change_reason": "Personnel change - John Smith retired, Jane Doe assumed BCM Manager role",
        "sections_changed": 1,
        "lines_added": 1,
        "lines_removed": 1
      },
      "context": {
        "ip_address": "10.20.30.40",
        "device": "Admin Workstation AD-WS-05",
        "location": "IT Department",
        "network": "internal",
        "authentication_method": "SSO",
        "session_id": "sess_abc123"
      },
      "related_events": [
        "evt_001179 (document edited)",
        "evt_001181 (version archived)"
      ]
    },
    {
      "event_id": "evt_001052",
      "timestamp": "2025-10-15T14:30:00Z",
      "event_type": "viewed",
      "event_category": "access",
      "severity": "low",
      "user": {
        "user_id": "user_234",
        "name": "Nurse Mary Smith",
        "email": "mary.smith@hospital.com",
        "role": "Emergency Dept Staff"
      },
      "action_details": {
        "action": "Viewed document",
        "version": "v2.3",
        "view_duration": "8 minutes",
        "sections_viewed": ["Section 5.2 - EHR Recovery Procedures", "Appendix B - Contact List"],
        "access_method": "web_browser"
      },
      "context": {
        "ip_address": "10.20.30.45",
        "device": "Hospital Workstation ED-WS-012",
        "location": "Emergency Department",
        "network": "internal",
        "authentication_method": "SSO",
        "session_id": "sess_def456"
      },
      "access_decision": {
        "decision": "granted",
        "reason": "User has 'emergency_dept_staff' role with 'read' permission",
        "conditions_met": ["authenticated", "internal_network"]
      }
    },
    {
      "event_id": "evt_000987",
      "timestamp": "2025-09-22T11:15:00Z",
      "event_type": "access_denied",
      "event_category": "security",
      "severity": "medium",
      "user": {
        "user_id": "user_external_001",
        "name": "Contractor John Jones",
        "email": "john.jones@vendor.com",
        "role": "External Contractor"
      },
      "action_details": {
        "action": "Attempted to view document",
        "version": "v2.2",
        "access_denied_reason": "User role 'external_contractor' does not have access to this document classification",
        "requested_permission": "read"
      },
      "context": {
        "ip_address": "203.45.67.89",
        "device": "Personal Laptop",
        "location": "External (Internet)",
        "network": "external",
        "authentication_method": "SSO",
        "session_id": "sess_ghi789"
      },
      "access_decision": {
        "decision": "denied",
        "reason": "Unauthorized role + External network access not permitted",
        "security_alert_sent": true,
        "alert_recipients": ["security@hospital.com", "document_owner@hospital.com"]
      }
    },
    {
      "event_id": "evt_000876",
      "timestamp": "2025-08-10T09:00:00Z",
      "event_type": "exported",
      "event_category": "distribution",
      "severity": "medium",
      "user": {
        "user_id": "user_123",
        "name": "BCM Manager Jane Doe",
        "email": "jane.doe@hospital.com",
        "role": "BCM Manager"
      },
      "action_details": {
        "action": "Exported document to PDF",
        "version": "v2.1",
        "export_format": "PDF",
        "file_size": "3.5 MB",
        "security_options": {
          "password_protected": false,
          "watermark": "Internal Confidential",
          "printing_allowed": true,
          "copying_disabled": true
        },
        "distribution": {
          "shared_with": "Executive team for quarterly review",
          "recipients": 8
        }
      },
      "context": {
        "ip_address": "10.20.30.50",
        "device": "BCM Manager Laptop",
        "location": "BCM Office",
        "network": "internal",
        "authentication_method": "SSO + MFA",
        "session_id": "sess_jkl012"
      }
    },
    {
      "event_id": "evt_000654",
      "timestamp": "2025-06-15T14:00:00Z",
      "event_type": "review_completed",
      "event_category": "lifecycle",
      "severity": "high",
      "user": {
        "user_id": "user_345",
        "name": "Dr. Michael Chen",
        "email": "michael.chen@hospital.com",
        "role": "Emergency Department Director"
      },
      "action_details": {
        "action": "Completed annual document review",
        "review_type": "annual",
        "review_outcome": "approved_with_updates",
        "changes_made": ["Updated contact list", "Revised RTO timings"],
        "new_version_created": "v2.0",
        "next_review_scheduled": "2026-06-15",
        "review_participants": 4
      },
      "context": {
        "ip_address": "10.20.30.60",
        "device": "ED Director Workstation",
        "location": "Emergency Department",
        "network": "internal",
        "authentication_method": "SSO",
        "session_id": "sess_mno345"
      }
    }
  ],
  "audit_analytics": {
    "most_active_users": [
      {
        "user": "dr.chen@hospital.com",
        "total_actions": 45,
        "most_common_action": "viewed"
      },
      {
        "user": "jane.doe@hospital.com",
        "total_actions": 38,
        "most_common_action": "edited"
      },
      {
        "user": "mary.smith@hospital.com",
        "total_actions": 22,
        "most_common_action": "viewed"
      }
    ],
    "access_patterns": {
      "peak_access_day": "Monday",
      "peak_access_hour": "09:00-10:00",
      "average_views_per_day": 0.73,
      "average_edits_per_month": 1.2
    },
    "security_events": {
      "total_denied_access_attempts": 2,
      "unauthorized_users": 1,
      "external_access_attempts": 2,
      "alerts_generated": 2
    }
  },
  "compliance_reporting": {
    "iso_22301_evidence": {
      "document_control": "Complete audit trail maintained per Clause 7.5.3",
      "access_control": "All access attempts logged and controlled",
      "review_tracking": "Document reviews tracked and completed on schedule"
    },
    "hipaa_evidence": {
      "access_logging": "All access to BC documentation containing PHI logged",
      "retention": "Audit trail retained for 7 years per HIPAA requirements"
    },
    "audit_report_url": "/api/documents/doc_bc_plan_ed_001/audit-trail/audit_trail_001/export/pdf"
  }
}
```

**Forensic Investigation Example**:
```json
{
  "investigation_query": {
    "investigation_type": "unauthorized_access",
    "document_id": "doc_bc_plan_ed_001",
    "suspicious_event_id": "evt_000987",
    "investigation_scope": {
      "related_events": true,
      "user_activity_history": true,
      "timeline_reconstruction": true
    }
  },
  "investigation_result": {
    "summary": "External contractor attempted to access confidential BC plan. Access denied. No breach occurred.",
    "timeline": [
      {
        "timestamp": "2025-09-22T11:14:30Z",
        "event": "User logged in via SSO",
        "user": "john.jones@vendor.com",
        "ip": "203.45.67.89",
        "location": "External"
      },
      {
        "timestamp": "2025-09-22T11:15:00Z",
        "event": "Attempted to access BC Plan - Emergency Department",
        "result": "Access denied - unauthorized role",
        "alert_triggered": true
      },
      {
        "timestamp": "2025-09-22T11:15:05Z",
        "event": "Security alert sent to security team and document owner",
        "recipients": ["security@hospital.com", "dr.chen@hospital.com"]
      },
      {
        "timestamp": "2025-09-22T11:20:00Z",
        "event": "User logged out",
        "session_duration": "5 minutes 30 seconds"
      }
    ],
    "user_activity_history": {
      "user": "john.jones@vendor.com",
      "role": "External Contractor",
      "total_access_attempts": 3,
      "successful_accesses": 1,
      "denied_accesses": 2,
      "documents_attempted": ["doc_bc_plan_ed_001", "doc_bc_plan_it_001"],
      "documents_accessed_successfully": ["doc_vendor_manual_001"],
      "assessment": "User attempted to access documents outside authorized scope. No successful unauthorized access."
    },
    "remediation_actions": [
      "User access reviewed by security team",
      "User reminded of access restrictions",
      "No further unauthorized attempts detected"
    ]
  }
}
```

**Events Published**:
```yaml
- event: audit.trail.queried
  payload:
    document_id: doc_bc_plan_ed_001
    queried_by: compliance.officer@hospital.com
    time_range: 2025-01-01 to 2025-12-31
    events_found: 342
  subscribers:
    - analytics-service (track audit queries)

- event: security.access_denied
  count: 2 (per year)
  payload:
    document_id: doc_bc_plan_ed_001
    user: [varies]
    reason: unauthorized_role
  subscribers:
    - security-service (investigate suspicious activity)
    - notification-service (alert security team)
```

**Components Used**:
- Documents Service
- Audit Trail (PostgreSQL append-only log + S3 long-term storage)
- Elasticsearch (fast audit query)
- Security Service (threat detection)
- Compliance Service (regulatory evidence)

**Business Value**:
- **Complete Visibility**: Track every action on every document
- **Compliance**: Meet ISO 22301, HIPAA, SOX, GDPR audit requirements
- **Security**: Detect and investigate unauthorized access attempts
- **Forensics**: Reconstruct document history for investigations
- **Evidence**: Defensible audit trail for legal/regulatory proceedings

---

### 6.15 Document Compliance Check

**Business Context**: AI-powered compliance validation against ISO 22301, ISO 27001, and industry standards with gap analysis and remediation recommendations

**Inputs**:
```json
{
  "compliance_check_request": {
    "document_id": "doc_bc_plan_ed_001",
    "standards": [
      "iso_22301:2019",
      "iso_27001:2022",
      "hipaa",
      "joint_commission"
    ],
    "check_type": "comprehensive",
    "include_recommendations": true,
    "generate_remediation_plan": true
  }
}
```

**API Endpoint**: `POST /api/documents/{document_id}/compliance-check`

**Compliance Check Process**:
```
Document Analysis → Standard Mapping → AI Gap Detection → Scoring → Recommendations
  ↓
  1. Extract document structure and content
  2. Map to standard requirements (ISO 22301, etc.)
  3. AI analysis for compliance gaps (Claude Sonnet)
  4. Score compliance level per requirement
  5. Generate remediation recommendations
  6. Prioritize gaps by criticality
  ↓
Return: compliance_report, gaps, recommendations, score
```

**Response**:
```json
{
  "compliance_check_id": "comp_check_001",
  "document_id": "doc_bc_plan_ed_001",
  "document_name": "Business Continuity Plan - Emergency Department",
  "document_version": "v2.5",
  "check_date": "2025-12-10T15:00:00Z",
  "check_type": "comprehensive",
  "overall_compliance_score": 87,
  "compliance_level": "Substantially Compliant",
  "standards_checked": [
    {
      "standard": "ISO 22301:2019",
      "compliance_score": 92,
      "status": "compliant",
      "total_requirements": 45,
      "requirements_met": 41,
      "requirements_partially_met": 3,
      "requirements_not_met": 1,
      "critical_gaps": 0
    },
    {
      "standard": "ISO 27001:2022",
      "compliance_score": 85,
      "status": "substantially_compliant",
      "total_requirements": 28,
      "requirements_met": 24,
      "requirements_partially_met": 3,
      "requirements_not_met": 1,
      "critical_gaps": 0
    },
    {
      "standard": "HIPAA",
      "compliance_score": 90,
      "status": "compliant",
      "total_requirements": 15,
      "requirements_met": 14,
      "requirements_partially_met": 1,
      "requirements_not_met": 0,
      "critical_gaps": 0
    },
    {
      "standard": "Joint Commission",
      "compliance_score": 82,
      "status": "substantially_compliant",
      "total_requirements": 12,
      "requirements_met": 10,
      "requirements_partially_met": 1,
      "requirements_not_met": 1,
      "critical_gaps": 0
    }
  ],
  "detailed_compliance_analysis": [
    {
      "standard": "ISO 22301:2019",
      "clause": "8.4.3 - Business continuity procedures",
      "requirement": "Document shall establish, implement and maintain procedures to manage incidents",
      "compliance_status": "met",
      "confidence": 0.95,
      "evidence_found": [
        "Section 5.0 defines incident response procedures",
        "Section 6.0 details activation criteria",
        "Section 7.0 establishes communication protocols",
        "Appendices provide detailed procedures and checklists"
      ],
      "assessment": "Document fully addresses ISO 22301 Clause 8.4.3 requirements for BC procedures. All required elements present and well-documented."
    },
    {
      "standard": "ISO 22301:2019",
      "clause": "8.5 - Testing and exercising",
      "requirement": "Organization shall test and exercise BC procedures at planned intervals",
      "compliance_status": "partially_met",
      "confidence": 0.88,
      "evidence_found": [
        "Section 8.0 mentions annual testing requirement",
        "Exercise schedule referenced but not fully detailed"
      ],
      "gaps_identified": [
        "Specific exercise dates not defined (marked as TBD)",
        "Exercise scenarios not detailed",
        "Post-exercise review process not documented"
      ],
      "assessment": "Document acknowledges testing requirement but lacks detailed exercise schedule and procedures. Meets intent but needs more specificity.",
      "criticality": "medium"
    },
    {
      "standard": "ISO 22301:2019",
      "clause": "9.1 - Monitoring, measurement, analysis and evaluation",
      "requirement": "Organization shall determine what needs to be monitored and measured for BCMS effectiveness",
      "compliance_status": "not_met",
      "confidence": 0.92,
      "evidence_found": [],
      "gaps_identified": [
        "No performance metrics defined for BC plan effectiveness",
        "No monitoring procedures established",
        "No measurement criteria specified"
      ],
      "assessment": "Document does not address performance monitoring and measurement requirements from Clause 9.1. This is a significant gap.",
      "criticality": "high",
      "remediation_priority": 1
    },
    {
      "standard": "ISO 27001:2022",
      "clause": "A.17.1 - Business continuity and disaster recovery",
      "requirement": "BC plans shall include information security aspects",
      "compliance_status": "met",
      "confidence": 0.87,
      "evidence_found": [
        "Section 4.2 addresses EHR system security during outages",
        "Section 7.0 includes secure communication protocols",
        "Appendix D covers data protection procedures during manual operations"
      ],
      "assessment": "Document adequately addresses information security considerations during BC scenarios."
    },
    {
      "standard": "HIPAA",
      "clause": "164.308(a)(7) - Contingency Plan",
      "requirement": "Establish procedures to respond to emergencies affecting electronic PHI",
      "compliance_status": "met",
      "confidence": 0.93,
      "evidence_found": [
        "Section 5.2 details EHR failure response procedures",
        "Manual patient tracking procedures protect PHI",
        "Data access controls maintained during outages"
      ],
      "assessment": "Document meets HIPAA contingency plan requirements for protecting ePHI during BC scenarios."
    }
  ],
  "gap_analysis": {
    "total_gaps": 6,
    "critical_gaps": 0,
    "high_priority_gaps": 1,
    "medium_priority_gaps": 3,
    "low_priority_gaps": 2,
    "gaps_by_standard": {
      "ISO 22301:2019": 4,
      "ISO 27001:2022": 1,
      "Joint Commission": 1
    }
  },
  "identified_gaps": [
    {
      "gap_id": "gap_001",
      "standard": "ISO 22301:2019",
      "clause": "9.1 - Performance monitoring",
      "gap_description": "No performance metrics defined for BC plan effectiveness",
      "criticality": "high",
      "impact": "Unable to measure BC plan effectiveness or demonstrate continuous improvement. May fail ISO 22301 certification audit.",
      "remediation_recommendation": {
        "action": "Define BC plan performance metrics",
        "specific_steps": [
          "Define key performance indicators (KPIs): plan activation time, recovery time achievement, exercise success rate",
          "Establish measurement procedures and data collection methods",
          "Set performance targets based on organizational objectives",
          "Document monitoring frequency (e.g., quarterly reviews)",
          "Create Section 9.0 - Performance Monitoring in BC plan"
        ],
        "estimated_effort": "4-6 hours",
        "responsible": "BCM Manager with ED Director input",
        "priority": 1,
        "due_date_recommendation": "Within 30 days"
      }
    },
    {
      "gap_id": "gap_002",
      "standard": "ISO 22301:2019",
      "clause": "8.5 - Testing and exercising",
      "gap_description": "Exercise schedule incomplete - dates marked as TBD",
      "criticality": "medium",
      "impact": "Cannot demonstrate commitment to testing BC procedures. May be flagged in ISO 22301 audit.",
      "remediation_recommendation": {
        "action": "Complete exercise schedule with specific dates",
        "specific_steps": [
          "Schedule annual table-top exercise (suggest Q1 2026)",
          "Schedule bi-annual communication tree test",
          "Define exercise scenarios for each critical process",
          "Document post-exercise review process",
          "Update Section 8.0 with specific dates and scenarios"
        ],
        "estimated_effort": "2-3 hours",
        "responsible": "BCM Manager",
        "priority": 2,
        "due_date_recommendation": "Within 60 days"
      }
    },
    {
      "gap_id": "gap_003",
      "standard": "ISO 22301:2019",
      "clause": "Appendix A - Contact List",
      "gap_description": "Some contact information marked as placeholders",
      "criticality": "medium",
      "impact": "Incomplete contact information could delay crisis response. Reduces operational readiness.",
      "remediation_recommendation": {
        "action": "Complete all contact information",
        "specific_steps": [
          "Fill in after-hours contact numbers for all key personnel",
          "Add alternate contacts for each role",
          "Verify all phone numbers and email addresses",
          "Add emergency vendor contact escalation paths"
        ],
        "estimated_effort": "1-2 hours",
        "responsible": "ED Manager",
        "priority": 3,
        "due_date_recommendation": "Before next review"
      }
    }
  ],
  "remediation_plan": {
    "plan_id": "remediation_plan_001",
    "total_actions": 6,
    "estimated_total_effort": "12-18 hours",
    "recommended_timeline": "90 days to full compliance",
    "phased_approach": {
      "phase_1_critical": {
        "duration": "30 days",
        "actions": ["gap_001"],
        "objective": "Address high-priority gap (performance metrics)"
      },
      "phase_2_important": {
        "duration": "60 days",
        "actions": ["gap_002", "gap_003"],
        "objective": "Complete exercise schedule and contact information"
      },
      "phase_3_minor": {
        "duration": "90 days",
        "actions": ["gap_004", "gap_005", "gap_006"],
        "objective": "Address remaining minor gaps"
      }
    },
    "tracking_url": "/api/documents/doc_bc_plan_ed_001/compliance/remediation-plan/remediation_plan_001/track"
  },
  "compliance_certification_readiness": {
    "iso_22301_certification": {
      "current_readiness": "85%",
      "readiness_assessment": "Substantially ready for certification audit. Address high-priority gap (performance metrics) before audit.",
      "blockers": ["Performance monitoring metrics not defined"],
      "estimated_time_to_ready": "30 days (after addressing gap_001)"
    },
    "iso_27001_certification": {
      "current_readiness": "90%",
      "readiness_assessment": "Ready for certification audit with minor improvements recommended.",
      "blockers": [],
      "estimated_time_to_ready": "Ready now"
    }
  },
  "ai_confidence": {
    "overall_confidence": 0.89,
    "high_confidence_findings": 38,
    "medium_confidence_findings": 8,
    "low_confidence_findings": 2,
    "manual_review_recommended": true,
    "manual_review_reason": "Some requirements subjective and require human judgment. AI analysis provides strong baseline but human validation recommended for certification prep."
  }
}
```

**Events Published**:
```yaml
- event: document.compliance_check.performed
  payload:
    document_id: doc_bc_plan_ed_001
    overall_score: 87
    standards_checked: [iso_22301, iso_27001, hipaa, joint_commission]
    gaps_found: 6
    performed_by: bcm.manager@hospital.com
  subscribers:
    - compliance-service (track compliance status)
    - notification-service (notify document owner of results)
    - analytics-service (compliance trends)

- event: compliance.gap.identified
  count: 6
  payload:
    document_id: doc_bc_plan_ed_001
    gap_criticality: [varies]
    standard: [varies]
  subscribers:
    - remediation-tracker (create remediation tasks)
    - compliance-dashboard (update compliance view)
```

**Components Used**:
- Documents Service
- AI Foundation (Claude Sonnet - compliance analysis)
- RAG (ISO 22301/27001 knowledge base)
- Compliance Rules Engine
- NLP (requirement mapping)
- Remediation Planner

**Business Value**:
- **Certification Readiness**: Know exactly what's needed for ISO 22301/27001 certification
- **Gap Identification**: AI detects compliance gaps humans might miss
- **Remediation Guidance**: Specific steps to close each gap
- **Time Savings**: Automated compliance checking vs manual review (days to minutes)
- **Continuous Compliance**: Check compliance after every document update

---

## API Reference

### Core Document APIs

**Living Documents**:
- `POST /api/documents/{id}/living-mode/enable` - Enable auto-updates
- `GET /api/documents/{id}/update-suggestions` - Get AI update suggestions
- `POST /api/documents/{id}/approve-update` - Approve suggested changes

**Version Control**:
- `POST /api/documents/{id}/versions/create` - Create new version
- `GET /api/documents/{id}/versions/history` - Version history
- `POST /api/documents/{id}/rollback` - Rollback to previous version
- `GET /api/documents/{id}/diff` - Compare versions

**Templates**:
- `POST /api/documents/templates/generate` - AI template generation
- `GET /api/documents/templates/library` - Browse template library
- `POST /api/documents/templates/{id}/customize` - Customize template

**Approval Workflow**:
- `POST /api/documents/{id}/approval/initiate` - Start approval workflow
- `POST /api/documents/{id}/approve` - Approve document
- `POST /api/documents/{id}/reject` - Reject with feedback

**Search & Discovery**:
- `POST /api/documents/search/semantic` - Semantic search
- `POST /api/documents/search/keyword` - Keyword search
- `GET /api/documents/related` - Find related documents

**Collaboration**:
- `WS /api/documents/{id}/collaborate` - Real-time collaboration
- `POST /api/documents/{id}/comments/add` - Add comment
- `POST /api/documents/{id}/suggestions/create` - Create suggestion

---

## Event Flow Diagrams

*[Mermaid diagrams showing event choreography for key scenarios]*

---

**Status**: ✅ All 15 Documents Service scenarios completed (100% complete)
**Total Scenarios**: 15 detailed scenarios with complete examples
**Completion Date**: 2025-10-10

### Scenarios Summary:
1. **6.1 Living Documents (Auto-Updating Plans)** - AI-powered automatic document updates
2. **6.2 Document Version Control** - Git-like versioning with rollback capability
3. **6.3 Document Template Library** - AI-generated ISO 22301 compliant templates
4. **6.4 Document Approval Workflow** - Multi-level approval with tracking
5. **6.5 Document Search (Semantic)** - Natural language document search
6. **6.6 Document Classification (Auto-Tagging)** - AI-powered classification and metadata extraction
7. **6.7 Document Access Control** - RBAC with granular permissions and audit
8. **6.8 Document Expiry & Review Tracking** - Automated review cycles and compliance
9. **6.9 Document Export (Multiple Formats)** - PDF/DOCX/HTML export with security
10. **6.10 Document Comparison (Versions)** - Side-by-side diff with impact analysis
11. **6.11 Document Archive Management** - Automated archival and retention policies
12. **6.12 Document Collaboration (Real-Time)** - Live editing with conflict resolution
13. **6.13 Document Import (Bulk)** - Bulk import with AI classification
14. **6.14 Document Audit Trail** - Complete lifecycle tracking for compliance
15. **6.15 Document Compliance Check** - AI-powered ISO compliance validation

**Next Steps**: Implementation phase ready to begin
