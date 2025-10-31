# Assistant Activity Event Schema

## Overview

The Assistant Activity Event Schema defines the standardized structure for logging all AI Assistant activities within the BCM Platform. These events provide complete audit trails, enable performance analysis, and support compliance reporting according to ISO 22301 requirements.

## Core Event Structure

### Base Event Schema
```json
{
  "event_type": "assistant.activity",
  "tenant_id": "string (required)",
  "user_id": "string (required)", 
  "data": {
    "intent": "string (required)",
    "workflow": "string (required)",
    "phase": "string (required)",
    "correlation_id": "string (required)",
    "session_id": "string (required)",
    "reason": "string (required)",
    "confidence_score": "number (0.0-1.0)",
    "execution_context": {},
    "actions": [],
    "results": {},
    "performance_metrics": {},
    "status": "string (required)"
  },
  "timestamp": "ISO8601 datetime (required)",
  "version": "string (required, current: 2.0)",
  "source": "assistant (constant)"
}
```

### Field Definitions

#### Root Level Fields
- **event_type**: Always "assistant.activity" for assistant operations
- **tenant_id**: Multi-tenant identifier for data isolation
- **user_id**: User who initiated the assistant interaction  
- **timestamp**: ISO8601 formatted UTC timestamp
- **version**: Schema version for backward compatibility
- **source**: Always "assistant" to identify event origin

#### Data Object Structure
- **intent**: Primary intent classification (from intents.md)
- **workflow**: Workflow category (bia_analysis, plan_generation, etc.)
- **phase**: Workflow execution phase (initiation, progress, completion)
- **correlation_id**: UUID linking related events across systems
- **session_id**: User session identifier for interaction tracking
- **reason**: Human-readable explanation for the action
- **confidence_score**: AI confidence in recommendations (0.0-1.0)
- **status**: Current status (initiated, in_progress, completed, error, cancelled)

## Intent-Specific Event Schemas

### BIA Analysis Events

#### BIA Initiation Event
```json
{
  "event_type": "assistant.activity",
  "tenant_id": "demo_hospital",
  "user_id": "user_12345",
  "data": {
    "intent": "plan_generate_bia",
    "workflow": "bia_analysis", 
    "phase": "initiation",
    "correlation_id": "bia_001_20240315_143022",
    "session_id": "sess_abc123def456",
    "reason": "BIA coverage at 64%, EHR process missing current BIA",
    "confidence_score": 0.92,
    "execution_context": {
      "trigger_type": "automatic",
      "kpi_threshold_breach": {
        "metric": "bia_coverage",
        "current_value": 0.64,
        "target_value": 0.80
      },
      "process_info": {
        "process_id": "EHR",
        "process_name": "Electronic Health Records", 
        "criticality": 4.8,
        "last_bia_date": null
      }
    },
    "actions": [
      {
        "type": "orchestrator_call",
        "endpoint": "/api/recommendations", 
        "method": "POST",
        "params": {
          "context": "bia_analysis",
          "action_type": "bia_computation",
          "process_id": "EHR",
          "analysis_scope": "full"
        },
        "timestamp": "2024-03-15T14:30:22Z",
        "status": "requested"
      }
    ],
    "results": {
      "orchestrator_response": {
        "decision_id": "dec_98765",
        "estimated_duration": "10-14 business days",
        "stakeholders_engaged": 4,
        "expected_events": [
          "bcm.bia.computation_started",
          "bcm.bia.stakeholder_responses_collected",
          "bcm.bia.completed"
        ]
      }
    },
    "performance_metrics": {
      "response_time_ms": 1250,
      "api_call_duration_ms": 890,
      "decision_time_ms": 45
    },
    "status": "initiated"
  },
  "timestamp": "2024-03-15T14:30:22Z",
  "version": "2.0",
  "source": "assistant"
}
```

#### BIA Completion Event
```json
{
  "event_type": "assistant.activity",
  "tenant_id": "demo_hospital", 
  "user_id": "user_12345",
  "data": {
    "intent": "plan_generate_bia",
    "workflow": "bia_analysis",
    "phase": "completion",
    "correlation_id": "bia_001_20240315_143022",
    "session_id": "sess_abc123def456", 
    "reason": "BIA computation completed successfully for EHR process",
    "confidence_score": 0.94,
    "execution_context": {
      "original_trigger": "kpi_threshold_breach",
      "completion_timeline": "12 business days",
      "stakeholder_participation": 4
    },
    "actions": [
      {
        "type": "kpi_update",
        "metric": "bia_coverage", 
        "previous_value": 0.64,
        "new_value": 0.68,
        "timestamp": "2024-03-29T16:45:33Z"
      },
      {
        "type": "next_step_recommendation",
        "recommended_intent": "plan_generate_draft",
        "priority": "high",
        "rationale": "Critical process with 4-hour RTO requires formal recovery plan"
      }
    ],
    "results": {
      "bia_outcomes": {
        "process_id": "EHR",
        "rto_hours": 4,
        "rpo_minutes": 30, 
        "criticality_score": 4.8,
        "financial_impact_per_hour": 45000,
        "dependencies_identified": 12,
        "stakeholder_consensus": 0.96
      },
      "quality_metrics": {
        "completeness_score": 0.94,
        "stakeholder_satisfaction": 4.6,
        "data_quality": 0.91
      }
    },
    "performance_metrics": {
      "total_duration_hours": 288,
      "stakeholder_response_rate": 1.0,
      "objective_completion_rate": 1.0
    },
    "status": "completed"
  },
  "timestamp": "2024-03-29T16:45:33Z",
  "version": "2.0",
  "source": "assistant"
}
```

### Plan Generation Events

#### Plan Generation Initiation
```json
{
  "event_type": "assistant.activity",
  "tenant_id": "demo_hospital",
  "user_id": "user_12345", 
  "data": {
    "intent": "plan_generate_draft",
    "workflow": "plan_generation",
    "phase": "initiation",
    "correlation_id": "plan_001_20240330_091500", 
    "session_id": "sess_def789ghi012",
    "reason": "EHR plan outdated (185 days), new BIA completed with 4-hour RTO",
    "confidence_score": 0.89,
    "execution_context": {
      "trigger_type": "user_initiated",
      "prerequisites_check": {
        "bia_current": true,
        "rto_rpo_defined": true,
        "stakeholders_mapped": true,
        "process_owner_confirmed": true
      },
      "plan_scope": {
        "process_id": "EHR",
        "plan_type": "business_continuity_plan",
        "complexity": "complex",
        "template": "iso_22301_healthcare",
        "estimated_pages": 45
      }
    },
    "actions": [
      {
        "type": "orchestrator_call",
        "endpoint": "/api/recommendations",
        "method": "POST", 
        "params": {
          "context": "plan_generation",
          "action_type": "plan_generation",
          "process_id": "EHR",
          "plan_scope": {
            "rto_hours": 4,
            "rpo_minutes": 30,
            "template": "iso_22301_healthcare"
          }
        },
        "timestamp": "2024-03-30T09:15:00Z",
        "status": "requested"
      }
    ],
    "results": {
      "generation_request": {
        "decision_id": "dec_11223",
        "estimated_duration": "25-30 minutes",
        "sections_to_generate": 9,
        "customizations_planned": 15
      }
    },
    "performance_metrics": {
      "prerequisite_check_time_ms": 340,
      "scope_determination_time_ms": 120,
      "api_call_time_ms": 780
    },
    "status": "initiated"
  },
  "timestamp": "2024-03-30T09:15:00Z",
  "version": "2.0",
  "source": "assistant"
}
```

### Incident Response Events

#### Incident Assessment Event
```json
{
  "event_type": "assistant.activity",
  "tenant_id": "demo_hospital",
  "user_id": "user_12345",
  "data": {
    "intent": "incident_draft_response", 
    "workflow": "incident_response",
    "phase": "assessment",
    "correlation_id": "inc_001_20240401_104500",
    "session_id": "sess_inc_789xyz123",
    "reason": "Critical incident detected: EHR system outage affecting patient care",
    "confidence_score": 0.97,
    "execution_context": {
      "incident_data": {
        "incident_id": "INC-2024-001",
        "severity": "critical", 
        "affected_processes": ["EHR", "patient_admission"],
        "impact_scope": "hospital_wide",
        "duration_elapsed_minutes": 15
      },
      "assessment_factors": {
        "patient_safety_impact": "high",
        "financial_impact_per_hour": 85000,
        "regulatory_implications": "medium",
        "rto_risk": "approaching_threshold"
      }
    },
    "actions": [
      {
        "type": "emergency_response_activation",
        "procedures": [
          "activate_incident_command",
          "notify_stakeholders", 
          "implement_alternative_procedures"
        ],
        "timeline": "immediate",
        "status": "executing"
      },
      {
        "type": "orchestrator_call",
        "endpoint": "/api/recommendations",
        "method": "POST",
        "params": {
          "context": "incident_response",
          "action_type": "incident_response",
          "incident_id": "INC-2024-001", 
          "severity": "critical"
        }
      }
    ],
    "results": {
      "severity_classification": {
        "calculated_severity": "critical",
        "impact_score": 0.94,
        "urgency_score": 0.98,
        "rto_consumption": 0.06
      },
      "response_plan": {
        "immediate_actions": 8,
        "stakeholders_notified": 12,
        "alternative_procedures_activated": true
      }
    },
    "performance_metrics": {
      "assessment_time_ms": 2340,
      "response_generation_time_ms": 1560,
      "notification_time_ms": 890
    },
    "status": "assessment_complete"
  },
  "timestamp": "2024-04-01T10:45:00Z",
  "version": "2.0",
  "source": "assistant"
}
```

### Exercise Planning Events

#### Exercise Design Event
```json
{
  "event_type": "assistant.activity",
  "tenant_id": "demo_hospital",
  "user_id": "user_12345",
  "data": {
    "intent": "schedule_exercise",
    "workflow": "exercise_planning",
    "phase": "design_complete",
    "correlation_id": "ex_001_20240405_133000",
    "session_id": "sess_exercise_456def789",
    "reason": "EHR recovery plan requires validation, no exercise in 210 days",
    "confidence_score": 0.85,
    "execution_context": {
      "exercise_requirements": {
        "process_id": "EHR",
        "last_exercise": "2023-08-15",
        "days_since_last": 210,
        "plan_validation_needed": true
      },
      "exercise_design": {
        "type": "simulation", 
        "duration_hours": 6,
        "participant_count": 25,
        "scenario": "database_failure_peak_hours"
      }
    },
    "actions": [
      {
        "type": "orchestrator_call",
        "endpoint": "/api/recommendations",
        "method": "POST",
        "params": {
          "context": "exercise_planning", 
          "action_type": "exercise_design",
          "process_id": "EHR",
          "exercise_type": "simulation"
        }
      },
      {
        "type": "logistics_coordination",
        "tasks": [
          "facility_reservation",
          "participant_invitation",
          "material_preparation"
        ]
      }
    ],
    "results": {
      "exercise_plan": {
        "objectives": 4,
        "success_criteria": 8,
        "logistics_requirements": 12,
        "estimated_cost": 3500
      },
      "participant_engagement": {
        "invitations_sent": 25,
        "confirmations_received": 23,
        "observers_included": 3
      }
    },
    "performance_metrics": {
      "design_time_ms": 4560,
      "stakeholder_identification_ms": 1230,
      "logistics_planning_ms": 2340
    },
    "status": "planned"
  },
  "timestamp": "2024-04-05T13:30:00Z",
  "version": "2.0",
  "source": "assistant"
}
```

### Audit and CAPA Events

#### Audit Analysis Event
```json
{
  "event_type": "assistant.activity",
  "tenant_id": "demo_hospital",
  "user_id": "user_12345", 
  "data": {
    "intent": "audit_summarize",
    "workflow": "audit_analysis",
    "phase": "evidence_analysis_complete",
    "correlation_id": "audit_001_20240410_140000",
    "session_id": "sess_audit_123abc456",
    "reason": "Q1 audit findings require analysis, 6 major findings identified",
    "confidence_score": 0.91,
    "execution_context": {
      "audit_scope": {
        "period": "Q1_2024",
        "iso_clauses": ["4.1", "6.1.2", "8.4.1", "9.1"],
        "finding_count": 23,
        "major_findings": 6
      },
      "evidence_sources": {
        "audit_reports": 3,
        "incident_analysis": 5,
        "exercise_results": 8,
        "kpi_data_months": 12
      }
    },
    "actions": [
      {
        "type": "orchestrator_call",
        "endpoint": "/api/audit/summarize",
        "method": "POST",
        "params": {
          "context": "audit_evidence",
          "finding_ids": ["AUD-2024-001", "AUD-2024-002", "AUD-2024-003"],
          "analysis_type": "comprehensive"
        }
      },
      {
        "type": "capa_generation",
        "priority_findings": 6,
        "estimated_capa_items": 8
      }
    ],
    "results": {
      "compliance_assessment": {
        "overall_score": 0.76,
        "clause_scores": {
          "clause_4": 0.92,
          "clause_6": 0.74, 
          "clause_8": 0.71,
          "clause_9": 0.65
        }
      },
      "capa_recommendations": {
        "critical_priority": 1,
        "high_priority": 2,
        "medium_priority": 3,
        "estimated_cost": 33000,
        "timeline_months": 6
      }
    },
    "performance_metrics": {
      "evidence_analysis_time_ms": 8940,
      "prioritization_time_ms": 2340,
      "capa_generation_time_ms": 5670
    },
    "status": "analysis_complete"
  },
  "timestamp": "2024-04-10T14:00:00Z", 
  "version": "2.0",
  "source": "assistant"
}
```

### KPI Monitoring Events

#### KPI Calculation Event
```json
{
  "event_type": "assistant.activity",
  "tenant_id": "demo_hospital",
  "user_id": "user_12345",
  "data": {
    "intent": "kpi_calculate",
    "workflow": "performance_monitoring", 
    "phase": "calculation_complete",
    "correlation_id": "kpi_001_20240415_080000",
    "session_id": "sess_kpi_auto_789def123",
    "reason": "Monthly KPI calculation cycle, performance assessment required",
    "confidence_score": 0.96,
    "execution_context": {
      "calculation_period": {
        "start_date": "2024-03-01",
        "end_date": "2024-03-31",
        "period_type": "monthly"
      },
      "data_sources": {
        "processes_analyzed": 35,
        "incidents_reviewed": 8,
        "capa_items_assessed": 12,
        "exercises_evaluated": 3
      }
    },
    "actions": [
      {
        "type": "kpi_data_collection",
        "sources": ["odoo_bcm", "eventbus", "document_processor"],
        "metrics_calculated": 10
      },
      {
        "type": "trend_analysis",
        "historical_periods": 12,
        "forecast_periods": 3
      },
      {
        "type": "threshold_assessment",
        "breaches_detected": 2,
        "warnings_identified": 1
      }
    ],
    "results": {
      "kpi_values": {
        "bia_coverage": 0.68,
        "plans_up_to_date": 0.75,
        "capa_on_time": 0.92, 
        "incident_response_time": 3.8,
        "exercise_completion": 0.94,
        "training_completion": 0.81
      },
      "performance_assessment": {
        "overall_health_score": 81,
        "improving_metrics": 3,
        "declining_metrics": 2,
        "stable_metrics": 5
      },
      "threshold_analysis": {
        "breaches": [
          {"metric": "training_completion", "current": 0.81, "target": 0.85}
        ],
        "warnings": [
          {"metric": "plans_up_to_date", "current": 0.75, "target": 0.80}
        ]
      }
    },
    "performance_metrics": {
      "data_collection_time_ms": 5670,
      "calculation_time_ms": 3450,
      "analysis_time_ms": 7890
    },
    "status": "completed"
  },
  "timestamp": "2024-04-15T08:00:00Z",
  "version": "2.0", 
  "source": "assistant"
}
```

## Error and Exception Events

### Error Event Schema
```json
{
  "event_type": "assistant.error",
  "tenant_id": "demo_hospital",
  "user_id": "user_12345",
  "data": {
    "intent": "plan_generate_draft",
    "workflow": "plan_generation",
    "phase": "execution_failed", 
    "correlation_id": "plan_002_20240420_110000",
    "session_id": "sess_error_abc123def",
    "error_type": "ServiceUnavailableError",
    "error_message": "Orchestrator service timeout after 30 seconds",
    "error_context": {
      "service_endpoint": "/api/recommendations", 
      "request_params": {
        "process_id": "pharmacy",
        "action_type": "plan_generation"
      },
      "retry_attempts": 3,
      "timeout_duration_ms": 30000
    },
    "fallback_actions": [
      {
        "type": "fallback_guidance",
        "action": "provide_manual_templates",
        "resources": [
          "iso_22301_bcp_template.docx",
          "plan_development_guide.pdf"
        ]
      }
    ],
    "user_impact": {
      "severity": "medium",
      "alternative_provided": true,
      "user_notified": true
    },
    "status": "error_handled"
  },
  "timestamp": "2024-04-20T11:00:00Z",
  "version": "2.0",
  "source": "assistant"
}
```

## Event Analytics and Reporting

### Performance Aggregation Queries
```sql
-- Assistant response time analysis
SELECT 
  DATE(timestamp) as date,
  intent,
  AVG(JSON_EXTRACT(data, '$.performance_metrics.response_time_ms')) as avg_response_time,
  COUNT(*) as interaction_count
FROM assistant_activities 
WHERE event_type = 'assistant.activity'
  AND timestamp > DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(timestamp), intent;

-- Workflow success rate analysis  
SELECT 
  workflow,
  status,
  COUNT(*) as count,
  COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY workflow) as percentage
FROM assistant_activities
WHERE event_type = 'assistant.activity'
  AND timestamp > DATE_SUB(NOW(), INTERVAL 90 DAY)
GROUP BY workflow, status;

-- User engagement analysis
SELECT 
  user_id,
  COUNT(DISTINCT session_id) as sessions,
  COUNT(*) as total_interactions,
  COUNT(*) / COUNT(DISTINCT session_id) as interactions_per_session
FROM assistant_activities  
WHERE timestamp > DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY user_id;
```

### Compliance Reporting Queries
```sql
-- ISO 22301 activity coverage
SELECT 
  intent,
  COUNT(*) as activity_count,
  COUNT(DISTINCT tenant_id) as tenant_coverage,
  AVG(JSON_EXTRACT(data, '$.confidence_score')) as avg_confidence
FROM assistant_activities
WHERE event_type = 'assistant.activity' 
  AND JSON_EXTRACT(data, '$.status') = 'completed'
  AND timestamp > DATE_SUB(NOW(), INTERVAL 90 DAY)
GROUP BY intent;

-- Audit trail completeness
SELECT 
  tenant_id,
  DATE(timestamp) as date,
  COUNT(*) as activity_count,
  COUNT(DISTINCT correlation_id) as workflow_count,
  COUNT(DISTINCT user_id) as user_count
FROM assistant_activities
WHERE timestamp > DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY tenant_id, DATE(timestamp);
```

## Event Retention and Archival

### Retention Policies
```json
{
  "retention_policies": {
    "assistant.activity": {
      "hot_storage": "90_days",
      "warm_storage": "2_years", 
      "cold_storage": "7_years",
      "deletion": "never"
    },
    "assistant.error": {
      "hot_storage": "30_days",
      "warm_storage": "1_year",
      "cold_storage": "3_years", 
      "deletion": "after_cold"
    },
    "assistant.performance": {
      "hot_storage": "30_days",
      "warm_storage": "6_months",
      "cold_storage": "2_years",
      "deletion": "after_cold"
    }
  },
  "archival_triggers": {
    "size_based": "10GB_per_tenant",
    "time_based": "daily_at_02:00_UTC",
    "compliance_based": "regulatory_requirement_change"
  }
}
```

## Security and Privacy Considerations

### Data Sanitization Rules
```json
{
  "sanitization_rules": {
    "before_logging": [
      "remove_personal_identifiers",
      "mask_sensitive_data", 
      "redact_credentials",
      "anonymize_patient_data"
    ],
    "sensitive_fields": [
      "password", "token", "api_key", "ssn", "medical_record_number",
      "patient_name", "phone_number", "email_address", "home_address"
    ],
    "masking_patterns": {
      "ssn": "XXX-XX-XXXX",
      "phone": "XXX-XXX-XXXX",
      "email": "****@****.***",
      "medical_record": "MRN-****"
    }
  }
}
```

### Access Control for Events
```json
{
  "access_control": {
    "tenant_isolation": {
      "rule": "users_can_only_access_own_tenant_events",
      "enforcement": "database_row_level_security"
    },
    "role_based_access": {
      "bcm_manager": ["read", "analyze", "export"],
      "bcm_analyst": ["read", "analyze"],
      "auditor": ["read", "export"],
      "admin": ["read", "analyze", "export", "delete"]
    },
    "audit_requirements": {
      "log_all_access": true,
      "require_justification": true,
      "retention_period": "7_years"
    }
  }
}
```

This comprehensive event schema ensures complete activity tracking, performance monitoring, and compliance reporting for the AI Assistant's PDCA conductor operations within the BCM platform.
