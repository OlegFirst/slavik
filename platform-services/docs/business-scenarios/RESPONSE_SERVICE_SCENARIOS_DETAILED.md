# Response Service - Detailed Scenarios with Examples
## Incident Response & Crisis Management - Complete Usage Scenarios

**Service**: Response Service (Port 8015)
**ISO Clause**: 8.4 - Incident Response
**Total Scenarios**: 18 (Part 1: 5.1-5.9)
**Status**: ✅ Ready for Implementation

---

## Table of Contents

1. [Incident Response Scenarios (5.1-5.9)](#incident-response-scenarios)
   - [5.1 Incident Detection & Auto-Creation](#51-incident-detection--auto-creation)
   - [5.2 Incident Classification & Prioritization](#52-incident-classification--prioritization)
   - [5.3 Automatic BC Plan Activation](#53-automatic-bc-plan-activation)
   - [5.4 Team Mobilization & Notification](#54-team-mobilization--notification)
   - [5.5 Incident Coordination Dashboard](#55-incident-coordination-dashboard)
   - [5.6 RTO/RPO Tracking](#56-rtorpo-tracking)
   - [5.7 Action Item Management](#57-action-item-management)
   - [5.8 Incident Communication (Internal)](#58-incident-communication-internal)
   - [5.9 Incident Communication (External)](#59-incident-communication-external)
2. [API Reference](#api-reference)
3. [Event Flow Diagrams](#event-flow-diagrams)

---

## Incident Response Scenarios

### 5.1 Incident Detection & Auto-Creation

**Business Context**: System automatically detects incidents from monitoring alerts and creates incident records with proper classification and initial assessment

**Inputs**:
```json
{
  "alert_source": "monitoring_service",
  "alert_id": "alert_2025_10_11_001",
  "severity": "critical",
  "alert_type": "service_degradation",
  "affected_systems": [
    {
      "system_id": "patient_portal",
      "system_name": "Patient Portal Application",
      "status": "degraded",
      "availability": "35%"
    },
    {
      "system_id": "appointment_system",
      "system_name": "Appointment Scheduling",
      "status": "down",
      "availability": "0%"
    }
  ],
  "metrics": {
    "error_rate": "78%",
    "response_time_ms": 15000,
    "affected_users": 450
  },
  "timestamp": "2025-10-11T14:23:15Z"
}
```

**API Endpoint**: `POST /api/response/incidents/auto-create`

**Process Flow**:
```
Monitoring Alert → Response Service → BIA Service (impact check) → Orchestrator
  ↓
  1. Receive alert from monitoring service
  2. Query BIA data for affected systems (RTO/RPO)
  3. Calculate business impact score
  4. Create incident record
  5. Auto-classify severity based on impact
  6. Check if BC plan activation needed
  7. Publish incident.created event
  ↓
Return: incident_id, classification, recommended_actions
```

**Response**:
```json
{
  "incident_id": "INC-2025-0234",
  "status": "detected",
  "classification": {
    "severity": "P1",
    "category": "service_outage",
    "priority_score": 92,
    "rationale": "Critical patient-facing systems affected. RTO for Patient Portal: 2 hours. Current downtime: 5 minutes."
  },
  "business_impact": {
    "affected_processes": [
      {
        "process_id": "proc_patient_scheduling",
        "process_name": "Patient Appointment Scheduling",
        "criticality": "critical",
        "rto_hours": 2,
        "rpo_hours": 1,
        "financial_impact_per_hour": "$15,000"
      }
    ],
    "total_affected_users": 450,
    "estimated_impact": {
      "financial_per_hour": "$15,000",
      "reputational": "high",
      "regulatory": "medium"
    }
  },
  "recommended_actions": [
    {
      "action": "activate_bc_plan",
      "plan_id": "bc_it_service_continuity",
      "reason": "Critical system outage exceeds acceptable degradation threshold"
    },
    {
      "action": "mobilize_response_team",
      "team": "it_incident_response",
      "urgency": "immediate"
    }
  ],
  "rto_countdown": {
    "target_resolution_time": "2025-10-11T16:23:15Z",
    "remaining_minutes": 115
  },
  "created_at": "2025-10-11T14:23:17Z",
  "created_by": "system_auto_detection"
}
```

**Events Published**:
```yaml
- event: incident.detected
  payload:
    incident_id: INC-2025-0234
    severity: P1
    affected_systems: [patient_portal, appointment_system]
    business_impact_score: 92
  subscribers:
    - orchestrator (initiate response workflow)
    - notification-service (alert on-call team)
    - monitoring-service (increase monitoring frequency)

- event: incident.created
  payload:
    incident_id: INC-2025-0234
    classification: P1
    rto_hours: 2
  subscribers:
    - planning-service (check BC plan activation)
    - compliance-service (track incident for reporting)
```

**Components Used**:
- Response Service (main)
- Monitoring Service (alert source)
- BIA Service (RTO/RPO data)
- Orchestrator (workflow initiation)
- PostgreSQL (incident storage)
- Event Bus (event publishing)

**Success Criteria**:
- ✅ Incident created within 2 seconds of alert
- ✅ Accurate severity classification (P1/P2/P3)
- ✅ Business impact calculated from BIA data
- ✅ RTO countdown timer started
- ✅ Response team notified

**Error Handling**:
```json
{
  "error": "BIADataNotFound",
  "message": "No BIA data found for affected system 'patient_portal'",
  "incident_id": "INC-2025-0234",
  "fallback_action": "Using default severity classification based on alert severity",
  "recommendation": "Complete BIA for critical systems to enable accurate impact assessment"
}
```

---

### 5.2 Incident Classification & Prioritization

**Business Context**: Once incident is created, system performs detailed classification using BIA data, organizational priorities, and AI-powered impact analysis

**Inputs**:
```json
{
  "incident_id": "INC-2025-0234",
  "incident_details": {
    "type": "service_outage",
    "affected_systems": ["patient_portal", "appointment_system"],
    "initial_severity": "critical"
  },
  "context": {
    "time_of_day": "14:23",
    "day_of_week": "friday",
    "current_workload": "high",
    "concurrent_incidents": 2
  }
}
```

**API Endpoint**: `POST /api/response/incidents/{incident_id}/classify`

**AI Classification Process**:
```
1. BIA Data Analysis
   ├─ Retrieve: RTO/RPO for affected systems
   ├─ Calculate: time sensitivity score
   └─ Identify: dependent processes

2. Historical Pattern Analysis
   ├─ Query: similar past incidents
   ├─ Analyze: resolution patterns
   └─ Predict: likely escalation path

3. Multi-Factor Priority Scoring
   ├─ Business Impact (40%)
   ├─ Time Sensitivity (25%)
   ├─ Risk of Escalation (20%)
   ├─ Resource Availability (15%)
   └─ Final Priority Score
```

**Response**:
```json
{
  "incident_id": "INC-2025-0234",
  "classification": {
    "priority": "P1",
    "category": "service_outage",
    "subcategory": "application_failure",
    "severity_level": "critical",
    "priority_score": 92
  },
  "scoring_breakdown": {
    "business_impact": {
      "score": 95,
      "weight": 0.40,
      "weighted_score": 38,
      "factors": [
        "Patient-facing critical system",
        "450 active users affected",
        "$15K/hour financial impact",
        "Regulatory reporting implications"
      ]
    },
    "time_sensitivity": {
      "score": 90,
      "weight": 0.25,
      "weighted_score": 22.5,
      "factors": [
        "RTO: 2 hours",
        "Peak usage hours",
        "Friday afternoon (high appointment volume)"
      ]
    },
    "escalation_risk": {
      "score": 85,
      "weight": 0.20,
      "weighted_score": 17,
      "factors": [
        "Multiple dependent systems",
        "High probability of cascade failure (72%)",
        "Similar incident escalated in past"
      ]
    },
    "resource_availability": {
      "score": 75,
      "weight": 0.15,
      "weighted_score": 11.25,
      "factors": [
        "Response team available",
        "2 concurrent incidents (capacity constraint)",
        "Vendor support available"
      ]
    },
    "total_score": 92
  },
  "impact_assessment": {
    "operational": {
      "level": "critical",
      "description": "Patient scheduling completely unavailable. Portal access severely degraded.",
      "affected_users": 450,
      "affected_departments": ["Registration", "Scheduling", "Clinical"]
    },
    "financial": {
      "level": "high",
      "estimated_cost_per_hour": "$15,000",
      "estimated_total_if_rto_met": "$30,000",
      "estimated_total_if_rto_missed": "$150,000+"
    },
    "reputational": {
      "level": "high",
      "factors": [
        "Patient frustration with online services",
        "Potential social media complaints",
        "Impact on digital transformation reputation"
      ]
    },
    "regulatory": {
      "level": "medium",
      "factors": [
        "HIPAA availability requirements",
        "State healthcare continuity regulations",
        "Required incident reporting if >4 hours"
      ]
    }
  },
  "similar_incidents": {
    "count": 3,
    "average_resolution_time_minutes": 87,
    "common_root_causes": [
      "Database connection pool exhaustion",
      "Application server memory leak",
      "Load balancer misconfiguration"
    ],
    "successful_interventions": [
      "Immediate restart of app servers",
      "Database connection pool increase",
      "Traffic rerouting to backup datacenter"
    ]
  },
  "recommended_response": {
    "immediate_actions": [
      "Activate IT Service Continuity Plan",
      "Mobilize Tier 3 support team",
      "Initiate communication to affected users"
    ],
    "escalation_path": [
      {
        "if": "No improvement in 30 minutes",
        "action": "Activate backup datacenter failover"
      },
      {
        "if": "RTO at 75% (90 minutes)",
        "action": "Escalate to Crisis Management Team"
      }
    ]
  },
  "confidence": 0.91,
  "classified_at": "2025-10-11T14:23:25Z"
}
```

**Events Published**:
```yaml
- event: incident.classified
  payload:
    incident_id: INC-2025-0234
    priority: P1
    priority_score: 92
    category: service_outage
  subscribers:
    - orchestrator (update workflow priority)
    - response-service (trigger appropriate response)
    - dashboards (update incident board)
```

**Components Used**:
- Response Service (classification engine)
- BIA Service (impact data)
- AI Foundation (pattern analysis, LLM Sonnet)
- Collective Intelligence (similar cases)
- Predictive Engine (escalation probability)

**Business Value**:
- **Accuracy**: 91% confidence in classification
- **Speed**: Classification completed in <10 seconds
- **Intelligence**: Leverages historical data and AI insights
- **Actionability**: Clear escalation path and next steps

---

### 5.3 Automatic BC Plan Activation

**Business Context**: For critical incidents exceeding severity thresholds, system automatically activates relevant Business Continuity plans and initiates recovery procedures

**Inputs**:
```json
{
  "incident_id": "INC-2025-0234",
  "classification": {
    "priority": "P1",
    "severity": "critical"
  },
  "affected_systems": ["patient_portal", "appointment_system"],
  "activation_criteria": {
    "auto_activate_if_p1": true,
    "auto_activate_if_rto_risk": true,
    "require_approval_threshold": "P2"
  }
}
```

**API Endpoint**: `POST /api/response/incidents/{incident_id}/activate-plan`

**Process Flow**:
```
Incident Classified → Response Service → Planning Service → BC Plan Repository
  ↓
  1. Check incident severity vs activation criteria
  2. Query Planning Service for applicable BC plans
  3. Retrieve plan details and action items
  4. Create plan activation record
  5. Generate action items for response team
  6. Assign tasks based on plan roles
  7. Notify all stakeholders
  8. Update incident status
  ↓
Return: activated_plan, action_items, team_assignments
```

**Response**:
```json
{
  "incident_id": "INC-2025-0234",
  "plan_activation": {
    "activation_id": "act_2025_234",
    "plan_id": "bc_it_service_continuity_v3.2",
    "plan_name": "IT Service Continuity Plan - Patient Systems",
    "plan_version": "3.2",
    "activated_at": "2025-10-11T14:23:30Z",
    "activated_by": "system_auto",
    "activation_reason": "P1 incident affecting critical patient systems with RTO risk",
    "iso_reference": "ISO 22301:2019 - Clause 8.4.5"
  },
  "action_items": [
    {
      "action_id": "act_001",
      "sequence": 1,
      "action": "Assess Impact and Activate Response Team",
      "assigned_to": "incident_commander",
      "assigned_person": "John Davis",
      "status": "in_progress",
      "deadline": "2025-10-11T14:33:30Z",
      "deadline_minutes": 10,
      "checklist": [
        "Confirm incident scope and affected systems",
        "Validate business impact assessment",
        "Activate incident response bridge",
        "Notify key stakeholders"
      ]
    },
    {
      "action_id": "act_002",
      "sequence": 2,
      "action": "Initiate System Diagnostics",
      "assigned_to": "technical_lead",
      "assigned_person": "Sarah Chen",
      "status": "pending",
      "deadline": "2025-10-11T14:38:30Z",
      "deadline_minutes": 15,
      "checklist": [
        "Check application server health",
        "Review database connection pools",
        "Analyze recent deployment changes",
        "Check infrastructure monitoring"
      ]
    },
    {
      "action_id": "act_003",
      "sequence": 3,
      "action": "Implement Immediate Workarounds",
      "assigned_to": "operations_team",
      "assigned_person": "Operations Team",
      "status": "pending",
      "deadline": "2025-10-11T14:53:30Z",
      "deadline_minutes": 30,
      "checklist": [
        "Enable manual appointment booking process",
        "Activate phone-based patient support",
        "Deploy status page for patients",
        "Route urgent cases to emergency backup system"
      ]
    },
    {
      "action_id": "act_004",
      "sequence": 4,
      "action": "Execute Recovery Procedures",
      "assigned_to": "technical_team",
      "assigned_person": "Technical Response Team",
      "status": "pending",
      "deadline": "2025-10-11T15:23:30Z",
      "deadline_minutes": 60,
      "recovery_options": [
        {
          "option": "Restart Application Servers",
          "estimated_time": "15 minutes",
          "risk": "low",
          "success_rate": "75%"
        },
        {
          "option": "Failover to Backup Datacenter",
          "estimated_time": "45 minutes",
          "risk": "medium",
          "success_rate": "95%"
        },
        {
          "option": "Restore from Last Good Backup",
          "estimated_time": "90 minutes",
          "risk": "medium",
          "success_rate": "98%",
          "data_loss": "up to 1 hour"
        }
      ]
    },
    {
      "action_id": "act_005",
      "sequence": 5,
      "action": "Validate Recovery and Resume Operations",
      "assigned_to": "qa_team",
      "assigned_person": "QA Team",
      "status": "pending",
      "deadline": "2025-10-11T16:23:30Z",
      "deadline_minutes": 120,
      "checklist": [
        "Verify system functionality",
        "Validate data integrity",
        "Confirm user access restored",
        "Monitor for stability (30 minutes)",
        "Communicate all-clear to stakeholders"
      ]
    }
  ],
  "team_assignments": {
    "incident_commander": {
      "name": "John Davis",
      "role": "IT Service Manager",
      "contact": {
        "mobile": "+1-555-0101",
        "email": "john.davis@hospital.com",
        "slack": "@johndavis"
      },
      "status": "notified",
      "acknowledged_at": "2025-10-11T14:23:35Z"
    },
    "technical_lead": {
      "name": "Sarah Chen",
      "role": "Senior DevOps Engineer",
      "contact": {
        "mobile": "+1-555-0102",
        "email": "sarah.chen@hospital.com",
        "slack": "@sarahchen"
      },
      "status": "notified",
      "acknowledged_at": "2025-10-11T14:23:38Z"
    },
    "operations_team": {
      "members": ["Mike Johnson", "Lisa Anderson", "Tom Wilson"],
      "status": "assembling",
      "bridge_url": "https://meet.hospital.com/incident-INC-2025-0234"
    }
  },
  "resources_activated": {
    "communication_bridge": "https://meet.hospital.com/incident-INC-2025-0234",
    "incident_dashboard": "https://bcm.hospital.com/incidents/INC-2025-0234",
    "runbook_url": "https://docs.hospital.com/bcm/it-service-continuity",
    "vendor_support": [
      {
        "vendor": "Application Vendor",
        "support_ticket": "SUP-78234",
        "priority": "critical",
        "contact": "support@vendor.com"
      }
    ]
  },
  "rto_tracking": {
    "target_rto_minutes": 120,
    "elapsed_minutes": 7,
    "remaining_minutes": 113,
    "on_track": true,
    "status": "green"
  },
  "escalation_triggers": [
    {
      "condition": "If no progress in 30 minutes",
      "action": "Escalate to Director of IT",
      "auto_trigger_at": "2025-10-11T14:53:30Z"
    },
    {
      "condition": "If RTO at 75% (90 minutes elapsed)",
      "action": "Activate Crisis Management Team",
      "auto_trigger_at": "2025-10-11T15:53:30Z"
    },
    {
      "condition": "If RTO exceeded",
      "action": "Escalate to Executive Leadership + Regulatory notification",
      "auto_trigger_at": "2025-10-11T16:23:30Z"
    }
  ]
}
```

**Events Published**:
```yaml
- event: plan.activated
  payload:
    incident_id: INC-2025-0234
    plan_id: bc_it_service_continuity_v3.2
    activation_id: act_2025_234
    iso_clause: "8.4.5"
  subscribers:
    - orchestrator (track plan execution)
    - task-queue (create action items)
    - notification-service (alert all stakeholders)
    - compliance-service (record activation for audit)
    - monitoring-service (increase monitoring)
```

**Components Used**:
- Response Service (activation logic)
- Planning Service (BC plan repository)
- Task Queue (action item management)
- Notification Service (team alerts)
- Orchestrator (workflow coordination)
- PostgreSQL (activation records)

**Success Criteria**:
- ✅ BC plan activated within 30 seconds of criteria met
- ✅ All action items created and assigned
- ✅ Response team notified and acknowledged
- ✅ Resources (bridge, dashboard) provisioned
- ✅ RTO tracking initiated

**Business Value**:
- **Speed**: Automatic activation eliminates decision delay
- **Completeness**: All plan actions immediately available
- **Coordination**: Team roles and responsibilities clear
- **Compliance**: ISO 22301 clause 8.4.5 requirements met
- **Visibility**: Real-time dashboards for all stakeholders

---

### 5.4 Team Mobilization & Notification

**Business Context**: Rapidly mobilize incident response team using multi-channel notifications, on-call schedules, and escalation workflows

**Inputs**:
```json
{
  "incident_id": "INC-2025-0234",
  "plan_activation_id": "act_2025_234",
  "required_roles": [
    "incident_commander",
    "technical_lead",
    "operations_team",
    "communications_lead"
  ],
  "urgency": "critical",
  "notification_preferences": {
    "primary_channel": "sms",
    "secondary_channel": "phone_call",
    "tertiary_channel": "email",
    "max_response_time_minutes": 5
  }
}
```

**API Endpoint**: `POST /api/response/incidents/{incident_id}/mobilize-team`

**Process Flow**:
```
Plan Activated → Response Service → On-Call Service → Notification Service
  ↓
  1. Identify required roles from BC plan
  2. Query on-call schedule for current assignments
  3. Prepare multi-channel notifications
  4. Send notifications (SMS → Phone → Email)
  5. Track acknowledgment status
  6. Escalate to backup if no response in 5 min
  7. Create incident response bridge
  8. Log all communications
  ↓
Return: team_status, notification_results, bridge_info
```

**Response**:
```json
{
  "incident_id": "INC-2025-0234",
  "mobilization": {
    "mobilization_id": "mob_2025_234",
    "initiated_at": "2025-10-11T14:23:30Z",
    "status": "in_progress",
    "target_response_time_minutes": 5
  },
  "team_notifications": [
    {
      "role": "incident_commander",
      "primary_person": {
        "name": "John Davis",
        "user_id": "user_jdavis",
        "on_call_status": "primary"
      },
      "notifications_sent": [
        {
          "channel": "sms",
          "phone": "+1-555-0101",
          "sent_at": "2025-10-11T14:23:31Z",
          "status": "delivered",
          "message": "🚨 CRITICAL INCIDENT INC-2025-0234: Patient Portal outage. You are Incident Commander. Acknowledge: https://bcm.hospital.com/ack/mob_2025_234"
        },
        {
          "channel": "phone_call",
          "phone": "+1-555-0101",
          "sent_at": "2025-10-11T14:23:32Z",
          "status": "in_progress",
          "call_id": "call_849234"
        },
        {
          "channel": "slack",
          "handle": "@johndavis",
          "sent_at": "2025-10-11T14:23:31Z",
          "status": "delivered"
        }
      ],
      "acknowledgment": {
        "acknowledged": true,
        "acknowledged_at": "2025-10-11T14:23:35Z",
        "acknowledged_via": "sms_link",
        "response_time_seconds": 4
      },
      "status": "mobilized"
    },
    {
      "role": "technical_lead",
      "primary_person": {
        "name": "Sarah Chen",
        "user_id": "user_schen",
        "on_call_status": "primary"
      },
      "notifications_sent": [
        {
          "channel": "sms",
          "phone": "+1-555-0102",
          "sent_at": "2025-10-11T14:23:31Z",
          "status": "delivered"
        },
        {
          "channel": "slack",
          "handle": "@sarahchen",
          "sent_at": "2025-10-11T14:23:31Z",
          "status": "delivered"
        }
      ],
      "acknowledgment": {
        "acknowledged": true,
        "acknowledged_at": "2025-10-11T14:23:38Z",
        "acknowledged_via": "slack",
        "response_time_seconds": 7
      },
      "status": "mobilized"
    },
    {
      "role": "operations_team",
      "team_members": [
        {
          "name": "Mike Johnson",
          "status": "acknowledged",
          "acknowledged_at": "2025-10-11T14:23:42Z"
        },
        {
          "name": "Lisa Anderson",
          "status": "acknowledged",
          "acknowledged_at": "2025-10-11T14:23:45Z"
        },
        {
          "name": "Tom Wilson",
          "status": "pending",
          "notifications_sent": 2,
          "escalation_due": "2025-10-11T14:28:30Z"
        }
      ],
      "status": "partial_mobilization"
    },
    {
      "role": "communications_lead",
      "primary_person": {
        "name": "Emily Martinez",
        "user_id": "user_emartinez",
        "on_call_status": "backup",
        "note": "Primary unavailable, automatically escalated to backup"
      },
      "primary_attempt": {
        "name": "Robert Taylor",
        "status": "no_response",
        "notifications_sent": 3,
        "escalation_reason": "No acknowledgment within 5 minutes"
      },
      "notifications_sent": [
        {
          "channel": "sms",
          "sent_at": "2025-10-11T14:28:31Z",
          "status": "delivered"
        },
        {
          "channel": "phone_call",
          "sent_at": "2025-10-11T14:28:32Z",
          "status": "answered",
          "call_duration_seconds": 45
        }
      ],
      "acknowledgment": {
        "acknowledged": true,
        "acknowledged_at": "2025-10-11T14:29:05Z",
        "acknowledged_via": "phone_call",
        "response_time_seconds": 34
      },
      "status": "mobilized_backup"
    }
  ],
  "communication_resources": {
    "incident_bridge": {
      "type": "video_conference",
      "url": "https://meet.hospital.com/incident-INC-2025-0234",
      "conference_id": "INC-2025-0234",
      "pin": "234567",
      "created_at": "2025-10-11T14:23:30Z",
      "participants_joined": 3
    },
    "slack_channel": {
      "name": "#incident-inc-2025-0234",
      "url": "https://hospital.slack.com/archives/C01INC0234",
      "created_at": "2025-10-11T14:23:31Z",
      "members_invited": 8,
      "members_joined": 6
    },
    "shared_document": {
      "type": "incident_log",
      "url": "https://docs.hospital.com/incidents/INC-2025-0234",
      "description": "Real-time incident log for collaboration"
    }
  },
  "mobilization_metrics": {
    "total_notifications_sent": 15,
    "acknowledgment_rate": "85%",
    "average_response_time_seconds": 15,
    "fastest_response_seconds": 4,
    "slowest_response_seconds": 34,
    "escalations_required": 1,
    "team_readiness": "operational"
  },
  "escalation_status": {
    "active_escalations": [
      {
        "role": "operations_team",
        "member": "Tom Wilson",
        "reason": "No acknowledgment",
        "next_action": "Contact backup: David Brown",
        "scheduled_for": "2025-10-11T14:28:30Z"
      }
    ]
  },
  "status_summary": {
    "incident_commander": "✅ Mobilized",
    "technical_lead": "✅ Mobilized",
    "operations_team": "⚠️ Partial (2/3)",
    "communications_lead": "✅ Mobilized (backup)",
    "overall_status": "operational",
    "ready_for_response": true
  }
}
```

**Events Published**:
```yaml
- event: team.notified
  payload:
    incident_id: INC-2025-0234
    mobilization_id: mob_2025_234
    roles_notified: [incident_commander, technical_lead, operations_team, communications_lead]
  subscribers:
    - orchestrator (track mobilization progress)
    - response-service (monitor acknowledgments)

- event: team.acknowledged
  payload:
    incident_id: INC-2025-0234
    role: incident_commander
    person: John Davis
    response_time_seconds: 4
  subscribers:
    - dashboards (update team status)
    - response-service (update mobilization status)

- event: team.mobilized
  payload:
    incident_id: INC-2025-0234
    mobilization_complete: true
    team_readiness: operational
  subscribers:
    - orchestrator (proceed with response)
    - response-service (begin action execution)
```

**Components Used**:
- Response Service (mobilization orchestration)
- Notification Service (multi-channel delivery)
- On-Call Service (schedule management)
- Communication Platform (bridge, Slack)
- PostgreSQL (team assignments, logs)

**Success Criteria**:
- ✅ All critical roles acknowledged within 5 minutes
- ✅ Multi-channel notifications delivered
- ✅ Automatic escalation to backup personnel
- ✅ Incident bridge created and active
- ✅ 85%+ acknowledgment rate achieved

**Business Value**:
- **Speed**: Team mobilized in under 1 minute
- **Reliability**: Automatic escalation ensures coverage
- **Coordination**: Centralized communication resources
- **Accountability**: Full audit trail of notifications
- **Flexibility**: Multi-channel delivery adapts to availability

---

### 5.5 Incident Coordination Dashboard

**Business Context**: Real-time dashboard provides unified view of incident status, team activities, RTO progress, and action items for effective coordination

**Inputs**:
```json
{
  "incident_id": "INC-2025-0234",
  "viewer_role": "incident_commander",
  "viewer_id": "user_jdavis"
}
```

**API Endpoint**: `GET /api/response/incidents/{incident_id}/dashboard`

**Dashboard Components**:
```
Real-Time Data Sources:
  ├─ Incident Status (Response Service)
  ├─ Action Items (Task Queue)
  ├─ Team Status (Notification Service)
  ├─ System Health (Monitoring Service)
  ├─ RTO/RPO Countdown (BIA Service)
  └─ Communication Feed (Event Bus)

Update Frequency: WebSocket (real-time)
```

**Response**:
```json
{
  "incident_id": "INC-2025-0234",
  "dashboard": {
    "overview": {
      "status": "in_progress",
      "severity": "P1",
      "category": "service_outage",
      "elapsed_time_minutes": 12,
      "last_update": "2025-10-11T14:35:15Z"
    },
    "rto_tracking": {
      "target_rto_minutes": 120,
      "elapsed_minutes": 12,
      "remaining_minutes": 108,
      "percentage_consumed": 10,
      "status": "on_track",
      "status_color": "green",
      "countdown_display": "01:48:00",
      "projected_resolution": "2025-10-11T15:45:00Z",
      "milestones": [
        {
          "milestone": "Initial diagnosis",
          "target_minutes": 15,
          "status": "in_progress",
          "completion": "80%"
        },
        {
          "milestone": "Implement workaround",
          "target_minutes": 30,
          "status": "pending"
        },
        {
          "milestone": "Full resolution",
          "target_minutes": 120,
          "status": "pending"
        }
      ]
    },
    "affected_systems": [
      {
        "system": "Patient Portal",
        "status": "degraded",
        "availability": "35%",
        "rto_hours": 2,
        "impact": "450 users affected",
        "recovery_status": "diagnosis_in_progress"
      },
      {
        "system": "Appointment Scheduling",
        "status": "down",
        "availability": "0%",
        "rto_hours": 2,
        "impact": "All scheduling unavailable",
        "recovery_status": "workaround_active"
      }
    ],
    "response_team": {
      "incident_commander": {
        "name": "John Davis",
        "status": "active",
        "location": "Incident Bridge",
        "last_activity": "2025-10-11T14:34:00Z",
        "current_action": "Coordinating diagnosis efforts"
      },
      "technical_lead": {
        "name": "Sarah Chen",
        "status": "active",
        "location": "Server Room",
        "last_activity": "2025-10-11T14:35:00Z",
        "current_action": "Analyzing application logs"
      },
      "operations_team": {
        "members_active": 2,
        "members": [
          {
            "name": "Mike Johnson",
            "status": "active",
            "current_action": "Implementing manual workaround"
          },
          {
            "name": "Lisa Anderson",
            "status": "active",
            "current_action": "Patient communication updates"
          }
        ]
      },
      "communications_lead": {
        "name": "Emily Martinez",
        "status": "active",
        "current_action": "Preparing stakeholder update"
      },
      "total_active": 5
    },
    "action_items": {
      "total": 12,
      "completed": 3,
      "in_progress": 5,
      "pending": 4,
      "overdue": 0,
      "critical_next_actions": [
        {
          "action_id": "act_002_3",
          "action": "Complete root cause diagnosis",
          "assigned_to": "Sarah Chen",
          "deadline": "2025-10-11T14:38:30Z",
          "remaining_minutes": 3,
          "status": "in_progress",
          "progress": 75
        },
        {
          "action_id": "act_003_2",
          "action": "Activate phone-based booking system",
          "assigned_to": "Mike Johnson",
          "deadline": "2025-10-11T14:40:00Z",
          "remaining_minutes": 5,
          "status": "in_progress",
          "progress": 50
        }
      ]
    },
    "timeline": [
      {
        "timestamp": "2025-10-11T14:23:15Z",
        "event": "Incident Detected",
        "description": "Monitoring alert: Patient Portal degraded",
        "severity": "critical"
      },
      {
        "timestamp": "2025-10-11T14:23:30Z",
        "event": "BC Plan Activated",
        "description": "IT Service Continuity Plan v3.2 activated",
        "action_by": "System Auto"
      },
      {
        "timestamp": "2025-10-11T14:23:35Z",
        "event": "Team Mobilized",
        "description": "Incident Commander acknowledged",
        "action_by": "John Davis"
      },
      {
        "timestamp": "2025-10-11T14:25:00Z",
        "event": "Initial Assessment Complete",
        "description": "Database connection pool exhaustion identified as likely cause",
        "action_by": "Sarah Chen"
      },
      {
        "timestamp": "2025-10-11T14:30:00Z",
        "event": "Workaround Initiated",
        "description": "Manual appointment booking process activated",
        "action_by": "Operations Team"
      },
      {
        "timestamp": "2025-10-11T14:35:00Z",
        "event": "Stakeholder Update Sent",
        "description": "Internal status update distributed",
        "action_by": "Emily Martinez"
      }
    ],
    "communication_feed": {
      "recent_updates": [
        {
          "timestamp": "2025-10-11T14:35:15Z",
          "from": "Sarah Chen",
          "channel": "slack",
          "message": "Root cause confirmed: DB connection pool maxed out. Preparing to increase pool size and restart app servers.",
          "type": "technical_update"
        },
        {
          "timestamp": "2025-10-11T14:34:30Z",
          "from": "Mike Johnson",
          "channel": "slack",
          "message": "Manual booking process live. Call center handling appointments. Capacity: ~20/hour.",
          "type": "workaround_status"
        },
        {
          "timestamp": "2025-10-11T14:33:00Z",
          "from": "Emily Martinez",
          "channel": "slack",
          "message": "Stakeholder update prepared. Sending to CMO and Dept Heads in 2 minutes.",
          "type": "communication_update"
        }
      ],
      "bridge_url": "https://meet.hospital.com/incident-INC-2025-0234",
      "slack_channel": "#incident-inc-2025-0234"
    },
    "system_metrics": {
      "patient_portal": {
        "availability": "35%",
        "error_rate": "65%",
        "response_time_ms": 15000,
        "active_sessions": 12,
        "trend": "stabilizing"
      },
      "appointment_system": {
        "availability": "0%",
        "status": "offline",
        "last_successful_transaction": "2025-10-11T14:22:00Z",
        "workaround_active": true
      },
      "database": {
        "connection_pool_usage": "100%",
        "active_connections": 250,
        "max_connections": 250,
        "queue_depth": 89,
        "issue": "Pool exhaustion confirmed"
      }
    },
    "decision_log": [
      {
        "timestamp": "2025-10-11T14:28:00Z",
        "decision": "Implement manual booking workaround before attempting server restart",
        "rationale": "Minimize service disruption risk, ensure patient care continuity",
        "made_by": "John Davis (IC)",
        "approved_by": "Team Consensus"
      },
      {
        "timestamp": "2025-10-11T14:32:00Z",
        "decision": "Increase DB connection pool from 250 to 500",
        "rationale": "Address root cause, tested in staging, low risk",
        "made_by": "Sarah Chen (TL)",
        "approved_by": "John Davis (IC)"
      }
    ],
    "next_steps": {
      "immediate": [
        "Complete root cause diagnosis (3 min)",
        "Activate phone-based booking system (5 min)",
        "Implement DB connection pool increase (10 min)"
      ],
      "short_term": [
        "Restart application servers with new config (20 min)",
        "Validate system recovery (30 min)",
        "Restore full patient portal functionality (45 min)"
      ],
      "contingency": [
        {
          "if": "Server restart fails",
          "action": "Failover to backup datacenter",
          "estimated_time": "45 min"
        }
      ]
    },
    "alerts": [
      {
        "type": "warning",
        "message": "RTO 10% consumed. On track but monitor closely.",
        "severity": "low"
      },
      {
        "type": "info",
        "message": "Operations team member Tom Wilson still pending acknowledgment. Backup contacted.",
        "severity": "low"
      }
    ]
  },
  "websocket_url": "wss://bcm.hospital.com/incidents/INC-2025-0234/updates",
  "refresh_rate_seconds": 5
}
```

**WebSocket Events** (Real-Time Updates):
```yaml
- event: dashboard.rto_update
  frequency: every_5_seconds
  payload:
    remaining_minutes: 108
    status: on_track

- event: dashboard.action_completed
  trigger: on_completion
  payload:
    action_id: act_002_3
    completed_by: Sarah Chen
    completion_time: 2025-10-11T14:38:25Z

- event: dashboard.team_update
  trigger: on_change
  payload:
    member: Sarah Chen
    current_action: Implementing DB pool increase
    location: Server Room

- event: dashboard.system_metric_update
  frequency: every_30_seconds
  payload:
    system: patient_portal
    availability: 38%
    trend: improving
```

**Components Used**:
- Response Service (dashboard orchestration)
- Monitoring Service (system metrics)
- Task Queue (action items)
- Notification Service (team status)
- BIA Service (RTO/RPO data)
- WebSocket Service (real-time updates)

**Success Criteria**:
- ✅ Dashboard loads in <2 seconds
- ✅ Real-time updates via WebSocket
- ✅ All critical information visible
- ✅ Mobile-responsive design
- ✅ Role-based data filtering

**Business Value**:
- **Visibility**: Complete incident picture in one view
- **Coordination**: Team activities synchronized
- **Decision Support**: Real-time data for commanders
- **Accountability**: Full timeline and decision log
- **Efficiency**: Eliminates status update meetings

---

### 5.6 RTO/RPO Tracking

**Business Context**: Continuous monitoring and tracking of Recovery Time Objective (RTO) and Recovery Point Objective (RPO) progress against incident recovery efforts

**Inputs**:
```json
{
  "incident_id": "INC-2025-0234",
  "affected_processes": [
    {
      "process_id": "proc_patient_scheduling",
      "rto_hours": 2,
      "rpo_hours": 1
    }
  ]
}
```

**API Endpoint**: `GET /api/response/incidents/{incident_id}/rto-tracking`

**Tracking Components**:
```
RTO/RPO Monitoring:
  ├─ BIA Service (target objectives)
  ├─ Incident Timeline (elapsed time)
  ├─ Recovery Progress (action completion)
  ├─ Predictive Engine (completion forecast)
  └─ Alert Engine (threshold warnings)

Update Frequency: Real-time (every 30 seconds)
```

**Response**:
```json
{
  "incident_id": "INC-2025-0234",
  "rto_tracking": {
    "process_id": "proc_patient_scheduling",
    "process_name": "Patient Appointment Scheduling",
    "rto_objective": {
      "target_hours": 2,
      "target_minutes": 120,
      "target_time": "2025-10-11T16:23:15Z"
    },
    "current_status": {
      "incident_start": "2025-10-11T14:23:15Z",
      "current_time": "2025-10-11T14:35:15Z",
      "elapsed_minutes": 12,
      "remaining_minutes": 108,
      "percentage_consumed": 10,
      "status": "on_track",
      "status_color": "green"
    },
    "milestones": [
      {
        "milestone": "Initial Response",
        "target_percentage": 5,
        "target_time": "2025-10-11T14:29:15Z",
        "actual_time": "2025-10-11T14:23:35Z",
        "status": "completed",
        "ahead_behind_minutes": -5.67,
        "actions": [
          "Team mobilized",
          "BC plan activated",
          "Initial assessment complete"
        ]
      },
      {
        "milestone": "Root Cause Identified",
        "target_percentage": 15,
        "target_time": "2025-10-11T14:41:15Z",
        "estimated_completion": "2025-10-11T14:38:30Z",
        "status": "in_progress",
        "ahead_behind_minutes": -2.75,
        "progress": 90,
        "actions": [
          "Database connection pool exhaustion confirmed",
          "Recovery plan prepared"
        ]
      },
      {
        "milestone": "Workaround Implemented",
        "target_percentage": 30,
        "target_time": "2025-10-11T14:59:15Z",
        "estimated_completion": "2025-10-11T14:53:00Z",
        "status": "in_progress",
        "ahead_behind_minutes": -6.25,
        "progress": 65,
        "actions": [
          "Manual appointment booking active",
          "Phone support operational"
        ]
      },
      {
        "milestone": "Primary System Recovery",
        "target_percentage": 70,
        "target_time": "2025-10-11T15:47:15Z",
        "estimated_completion": "2025-10-11T15:35:00Z",
        "status": "pending",
        "ahead_behind_minutes": -12.25,
        "actions": [
          "DB pool increase deployment",
          "Application server restart",
          "System validation"
        ]
      },
      {
        "milestone": "Full Service Restoration",
        "target_percentage": 100,
        "target_time": "2025-10-11T16:23:15Z",
        "estimated_completion": "2025-10-11T16:05:00Z",
        "status": "pending",
        "ahead_behind_minutes": -18.25,
        "actions": [
          "All systems operational",
          "User access verified",
          "Performance validated"
        ]
      }
    ],
    "predictive_analysis": {
      "predicted_completion_time": "2025-10-11T16:05:00Z",
      "prediction_confidence": 0.87,
      "ahead_of_schedule": true,
      "time_savings_minutes": 18,
      "factors": [
        "Rapid root cause identification",
        "Effective workaround implementation",
        "Team experience with similar incidents",
        "Available backup resources"
      ],
      "risks": [
        {
          "risk": "Server restart complications",
          "probability": 0.15,
          "potential_delay_minutes": 30,
          "mitigation": "Tested configuration in staging, backup failover ready"
        }
      ]
    },
    "threshold_alerts": [
      {
        "threshold": "25% consumed",
        "time": "2025-10-11T14:53:15Z",
        "status": "upcoming",
        "action": "Status update to stakeholders"
      },
      {
        "threshold": "50% consumed",
        "time": "2025-10-11T15:23:15Z",
        "status": "upcoming",
        "action": "Executive notification if not resolved"
      },
      {
        "threshold": "75% consumed",
        "time": "2025-10-11T15:53:15Z",
        "status": "upcoming",
        "action": "Escalate to Crisis Management Team"
      },
      {
        "threshold": "100% exceeded",
        "time": "2025-10-11T16:23:15Z",
        "status": "upcoming",
        "action": "Regulatory notification, executive escalation"
      }
    ],
    "recovery_velocity": {
      "current_velocity": "high",
      "progress_rate_per_hour": 32.5,
      "projected_total_duration_minutes": 102,
      "velocity_trend": "accelerating",
      "comparison_to_similar_incidents": "15% faster than average"
    }
  },
  "rpo_tracking": {
    "rpo_objective": {
      "target_hours": 1,
      "target_minutes": 60,
      "max_data_loss": "1 hour of appointment data"
    },
    "current_status": {
      "last_successful_backup": "2025-10-11T14:00:00Z",
      "incident_start": "2025-10-11T14:23:15Z",
      "potential_data_loss_minutes": 23,
      "rpo_status": "within_target",
      "status_color": "green"
    },
    "data_protection_status": {
      "appointment_transactions": {
        "last_committed": "2025-10-11T14:22:45Z",
        "transactions_at_risk": 8,
        "recovery_method": "Database transaction log replay",
        "expected_recovery": "100%"
      },
      "patient_portal_sessions": {
        "active_at_incident": 450,
        "sessions_lost": 450,
        "recovery_method": "Users must re-login",
        "data_impact": "Session state only, no data loss"
      }
    },
    "recovery_point_options": [
      {
        "recovery_point": "2025-10-11T14:22:45Z",
        "data_loss_minutes": 0.5,
        "method": "Transaction log replay",
        "estimated_time_minutes": 15,
        "recommended": true
      },
      {
        "recovery_point": "2025-10-11T14:00:00Z",
        "data_loss_minutes": 23,
        "method": "Last full backup",
        "estimated_time_minutes": 45,
        "recommended": false
      }
    ]
  },
  "visualization": {
    "rto_gauge": {
      "current": 10,
      "max": 100,
      "status": "green",
      "zones": {
        "green": "0-50%",
        "yellow": "50-75%",
        "red": "75-100%"
      }
    },
    "timeline_chart_url": "/api/response/incidents/INC-2025-0234/rto-chart",
    "progress_graph_url": "/api/response/incidents/INC-2025-0234/progress-graph"
  }
}
```

**Events Published**:
```yaml
- event: rto.milestone_completed
  payload:
    incident_id: INC-2025-0234
    milestone: Initial Response
    ahead_behind_minutes: -5.67
    status: ahead_of_schedule

- event: rto.threshold_reached
  payload:
    incident_id: INC-2025-0234
    threshold: 25%
    action_required: stakeholder_update

- event: rto.at_risk
  trigger: when_prediction_shows_rto_miss
  payload:
    incident_id: INC-2025-0234
    predicted_miss_by_minutes: 15
    recommended_actions: [escalate, activate_contingency]

- event: rto.achieved
  trigger: on_resolution
  payload:
    incident_id: INC-2025-0234
    target_minutes: 120
    actual_minutes: 102
    performance: ahead_by_18_minutes
```

**Components Used**:
- Response Service (RTO tracking logic)
- BIA Service (RTO/RPO targets)
- Predictive Engine (completion forecasting)
- Monitoring Service (recovery progress)
- Alert Service (threshold notifications)

**Success Criteria**:
- ✅ RTO/RPO targets clearly displayed
- ✅ Real-time countdown and progress tracking
- ✅ Predictive completion time with 85%+ accuracy
- ✅ Threshold alerts triggered automatically
- ✅ Visual indicators (green/yellow/red status)

**Business Value**:
- **Accountability**: Clear visibility of RTO/RPO compliance
- **Proactive Management**: Early warning of potential RTO misses
- **Decision Support**: Data-driven escalation decisions
- **Compliance**: ISO 22301 requirement for RTO tracking
- **Performance**: Historical comparison and improvement

---

### 5.7 Action Item Management

**Business Context**: Manage all incident response action items from BC plan activation, track completion, coordinate assignments, and ensure nothing falls through the cracks

**Inputs**:
```json
{
  "incident_id": "INC-2025-0234",
  "plan_activation_id": "act_2025_234"
}
```

**API Endpoint**: `GET /api/response/incidents/{incident_id}/actions`

**Action Management Flow**:
```
BC Plan Activated → Action Items Generated → Task Queue → Team Members
  ↓
  1. Extract actions from activated BC plan
  2. Create task records in queue
  3. Assign based on plan roles
  4. Set deadlines based on RTO
  5. Track completion status
  6. Monitor dependencies
  7. Escalate overdue items
  ↓
Return: action_list, completion_status, next_actions
```

**Response**:
```json
{
  "incident_id": "INC-2025-0234",
  "action_management": {
    "summary": {
      "total_actions": 18,
      "completed": 6,
      "in_progress": 8,
      "pending": 4,
      "overdue": 0,
      "completion_percentage": 33
    },
    "critical_path": [
      {
        "sequence": 1,
        "action_id": "act_001",
        "action": "Assess Impact and Activate Response Team",
        "status": "completed",
        "assigned_to": "John Davis (Incident Commander)",
        "started_at": "2025-10-11T14:23:30Z",
        "completed_at": "2025-10-11T14:25:00Z",
        "duration_minutes": 1.5,
        "on_critical_path": true
      },
      {
        "sequence": 2,
        "action_id": "act_002",
        "action": "Initiate System Diagnostics",
        "status": "completed",
        "assigned_to": "Sarah Chen (Technical Lead)",
        "started_at": "2025-10-11T14:25:00Z",
        "completed_at": "2025-10-11T14:35:00Z",
        "duration_minutes": 10,
        "on_critical_path": true,
        "findings": "Database connection pool exhaustion confirmed"
      },
      {
        "sequence": 3,
        "action_id": "act_003",
        "action": "Implement Immediate Workarounds",
        "status": "in_progress",
        "assigned_to": "Operations Team",
        "started_at": "2025-10-11T14:30:00Z",
        "deadline": "2025-10-11T14:53:30Z",
        "remaining_minutes": 18,
        "progress": 70,
        "on_critical_path": true,
        "sub_actions": [
          {
            "sub_action": "Enable manual appointment booking",
            "status": "completed",
            "completed_by": "Mike Johnson"
          },
          {
            "sub_action": "Activate phone-based support",
            "status": "in_progress",
            "assigned_to": "Lisa Anderson",
            "progress": 85
          },
          {
            "sub_action": "Deploy patient status page",
            "status": "completed",
            "completed_by": "Tom Wilson"
          }
        ]
      },
      {
        "sequence": 4,
        "action_id": "act_004",
        "action": "Execute Recovery Procedures",
        "status": "in_progress",
        "assigned_to": "Technical Team",
        "started_at": "2025-10-11T14:32:00Z",
        "deadline": "2025-10-11T15:23:30Z",
        "remaining_minutes": 48,
        "progress": 45,
        "on_critical_path": true,
        "selected_recovery_option": {
          "option": "Increase DB pool + Restart App Servers",
          "estimated_time_minutes": 30,
          "risk": "low",
          "current_step": "Deploying DB pool configuration"
        },
        "sub_actions": [
          {
            "sub_action": "Increase database connection pool (250→500)",
            "status": "in_progress",
            "assigned_to": "Sarah Chen",
            "progress": 80
          },
          {
            "sub_action": "Prepare application server restart",
            "status": "in_progress",
            "assigned_to": "David Kim",
            "progress": 60
          },
          {
            "sub_action": "Notify dependent systems of restart",
            "status": "completed",
            "completed_by": "Mike Johnson"
          }
        ]
      },
      {
        "sequence": 5,
        "action_id": "act_005",
        "action": "Validate Recovery and Resume Operations",
        "status": "pending",
        "assigned_to": "QA Team",
        "dependencies": ["act_004"],
        "estimated_start": "2025-10-11T15:05:00Z",
        "deadline": "2025-10-11T16:23:30Z",
        "on_critical_path": true
      }
    ],
    "supporting_actions": [
      {
        "action_id": "act_comm_001",
        "action": "Internal Stakeholder Communication",
        "status": "completed",
        "assigned_to": "Emily Martinez",
        "completed_at": "2025-10-11T14:35:00Z",
        "deliverable": "Status update sent to CMO, Dept Heads"
      },
      {
        "action_id": "act_comm_002",
        "action": "Patient Communication",
        "status": "in_progress",
        "assigned_to": "Communications Team",
        "progress": 60,
        "deadline": "2025-10-11T14:45:00Z",
        "deliverable": "Patient portal status message, social media update"
      },
      {
        "action_id": "act_vendor_001",
        "action": "Engage Vendor Support",
        "status": "completed",
        "assigned_to": "John Davis",
        "completed_at": "2025-10-11T14:28:00Z",
        "outcome": "Priority ticket SUP-78234 created, vendor on standby"
      },
      {
        "action_id": "act_doc_001",
        "action": "Document Incident Timeline",
        "status": "in_progress",
        "assigned_to": "Incident Scribe",
        "continuous": true,
        "last_update": "2025-10-11T14:35:00Z"
      }
    ],
    "action_dependencies": {
      "graph": [
        {
          "action": "act_004",
          "depends_on": ["act_002", "act_003"],
          "status": "dependencies_met",
          "can_proceed": true
        },
        {
          "action": "act_005",
          "depends_on": ["act_004"],
          "status": "waiting_on_dependencies",
          "can_proceed": false,
          "blocking_action": "act_004"
        }
      ]
    },
    "overdue_actions": [],
    "at_risk_actions": [
      {
        "action_id": "act_003",
        "action": "Implement Immediate Workarounds",
        "deadline": "2025-10-11T14:53:30Z",
        "remaining_minutes": 18,
        "progress": 70,
        "risk_level": "low",
        "reason": "On track but requires monitoring"
      }
    ],
    "next_critical_actions": [
      {
        "priority": 1,
        "action": "Complete DB pool increase deployment",
        "assigned_to": "Sarah Chen",
        "deadline_minutes": 3,
        "impact": "Unblocks recovery procedure"
      },
      {
        "priority": 2,
        "action": "Complete phone support activation",
        "assigned_to": "Lisa Anderson",
        "deadline_minutes": 10,
        "impact": "Full workaround operational"
      },
      {
        "priority": 3,
        "action": "Finalize patient communication",
        "assigned_to": "Communications Team",
        "deadline_minutes": 10,
        "impact": "Manage patient expectations"
      }
    ],
    "completion_forecast": {
      "estimated_all_complete": "2025-10-11T16:05:00Z",
      "confidence": 0.87,
      "critical_path_duration_minutes": 102,
      "rto_compliance": "on_track",
      "ahead_behind_schedule_minutes": -18
    }
  },
  "action_controls": {
    "bulk_operations": [
      {
        "operation": "complete_action",
        "endpoint": "POST /api/response/incidents/{incident_id}/actions/{action_id}/complete"
      },
      {
        "operation": "reassign_action",
        "endpoint": "POST /api/response/incidents/{incident_id}/actions/{action_id}/reassign"
      },
      {
        "operation": "update_progress",
        "endpoint": "PUT /api/response/incidents/{incident_id}/actions/{action_id}/progress"
      },
      {
        "operation": "add_note",
        "endpoint": "POST /api/response/incidents/{incident_id}/actions/{action_id}/notes"
      }
    ]
  },
  "team_workload": {
    "john_davis": {
      "role": "Incident Commander",
      "active_actions": 3,
      "completed_actions": 2,
      "workload": "moderate"
    },
    "sarah_chen": {
      "role": "Technical Lead",
      "active_actions": 5,
      "completed_actions": 3,
      "workload": "high"
    },
    "operations_team": {
      "active_actions": 6,
      "completed_actions": 4,
      "workload": "high"
    }
  }
}
```

**API Operations**:
```json
// Complete Action
POST /api/response/incidents/INC-2025-0234/actions/act_002/complete
{
  "completed_by": "Sarah Chen",
  "completion_notes": "Database connection pool exhaustion confirmed. Recovery plan prepared.",
  "outcome": "success",
  "findings": "Pool maxed at 250 connections. Increasing to 500."
}

// Update Progress
PUT /api/response/incidents/INC-2025-0234/actions/act_003/progress
{
  "progress": 70,
  "updated_by": "Mike Johnson",
  "status_note": "Manual booking active. Phone support 85% ready."
}

// Add Sub-Action
POST /api/response/incidents/INC-2025-0234/actions/act_004/sub-actions
{
  "sub_action": "Validate new DB pool configuration in staging",
  "assigned_to": "Sarah Chen",
  "deadline_minutes": 5
}

// Reassign Action
POST /api/response/incidents/INC-2025-0234/actions/act_005/reassign
{
  "from": "QA Team",
  "to": "Senior QA Lead: Jennifer White",
  "reason": "Specific expertise required for critical validation"
}
```

**Events Published**:
```yaml
- event: action.assigned
  payload:
    incident_id: INC-2025-0234
    action_id: act_004
    assigned_to: Technical Team
    deadline: 2025-10-11T15:23:30Z

- event: action.completed
  payload:
    incident_id: INC-2025-0234
    action_id: act_002
    completed_by: Sarah Chen
    duration_minutes: 10
    outcome: success

- event: action.overdue
  trigger: when_deadline_passed
  payload:
    incident_id: INC-2025-0234
    action_id: act_xxx
    assigned_to: person
    overdue_by_minutes: 5

- event: action.progress_updated
  payload:
    incident_id: INC-2025-0234
    action_id: act_003
    progress: 70
    status: in_progress
```

**Components Used**:
- Response Service (action management)
- Task Queue (action storage, dependencies)
- Notification Service (assignment alerts)
- Planning Service (BC plan actions)
- PostgreSQL (action records)

**Success Criteria**:
- ✅ All BC plan actions tracked
- ✅ Dependencies managed correctly
- ✅ Real-time progress updates
- ✅ Automatic overdue detection
- ✅ Clear next actions identified

**Business Value**:
- **Completeness**: No actions forgotten or overlooked
- **Coordination**: Clear assignments and dependencies
- **Accountability**: Full audit trail of action execution
- **Visibility**: Real-time progress for all stakeholders
- **Efficiency**: Critical path optimization

---

### 5.8 Incident Communication (Internal)

**Business Context**: Systematic internal communication to stakeholders with role-appropriate updates, maintaining awareness without information overload

**Inputs**:
```json
{
  "incident_id": "INC-2025-0234",
  "communication_type": "status_update",
  "audience": "internal_stakeholders",
  "severity": "P1"
}
```

**API Endpoint**: `POST /api/response/incidents/{incident_id}/communicate/internal`

**Communication Strategy**:
```
Stakeholder Identification → Message Tailoring → Multi-Channel Delivery
  ↓
  1. Identify stakeholders by role and impact
  2. Determine update frequency based on severity
  3. Tailor message content by audience
  4. Select delivery channels by preference
  5. Track receipt and acknowledgment
  6. Escalate if critical stakeholders miss update
  ↓
Return: communication_sent, delivery_status, next_update_scheduled
```

**Request**:
```json
{
  "incident_id": "INC-2025-0234",
  "update_type": "progress_update",
  "update_number": 2,
  "trigger": "scheduled_30_minutes",
  "include_sections": [
    "current_status",
    "actions_taken",
    "next_steps",
    "rto_status",
    "impact_assessment"
  ]
}
```

**Response**:
```json
{
  "incident_id": "INC-2025-0234",
  "communication": {
    "communication_id": "comm_int_2025_234_002",
    "type": "internal_status_update",
    "update_number": 2,
    "sent_at": "2025-10-11T14:35:00Z"
  },
  "stakeholder_communications": {
    "executive_leadership": {
      "recipients": [
        {
          "name": "Dr. Patricia Williams",
          "title": "Chief Medical Officer",
          "email": "patricia.williams@hospital.com"
        },
        {
          "name": "Michael Chang",
          "title": "CIO",
          "email": "michael.chang@hospital.com"
        }
      ],
      "message": {
        "subject": "P1 Incident Update #2: Patient Portal Outage - Recovery In Progress",
        "format": "executive_summary",
        "content": {
          "summary": "Patient Portal and Appointment System incident recovery is progressing well. Root cause identified (database connection limits). Workarounds active. Full resolution expected within RTO (by 4:23 PM).",
          "key_points": [
            "✓ Root cause identified: Database connection pool exhaustion",
            "✓ Manual appointment booking operational (20 bookings/hour capacity)",
            "✓ Recovery plan in execution: Database optimization in progress",
            "✓ RTO Status: 10% consumed, on track for resolution by 4:23 PM",
            "✓ Patient impact: 450 users affected, workarounds minimizing disruption"
          ],
          "business_impact": "Moderate service degradation. Patient care continuity maintained via manual processes. No patient safety impact.",
          "actions_required": "None at this time. Next update in 30 minutes or upon significant change.",
          "escalation_criteria": "Will escalate if no improvement by 3:53 PM (75% RTO consumed)"
        }
      },
      "delivery": {
        "channel": "email",
        "sent_at": "2025-10-11T14:35:00Z",
        "status": "delivered",
        "read_receipts": [
          {
            "recipient": "Dr. Patricia Williams",
            "read_at": "2025-10-11T14:36:15Z"
          },
          {
            "recipient": "Michael Chang",
            "read_at": "2025-10-11T14:35:45Z"
          }
        ]
      }
    },
    "department_heads": {
      "recipients": [
        {
          "name": "Dr. Robert Martinez",
          "title": "Head of Emergency Department",
          "department": "Emergency"
        },
        {
          "name": "Lisa Thompson",
          "title": "Director of Patient Services",
          "department": "Patient Services"
        },
        {
          "name": "James Anderson",
          "title": "Director of IT Operations",
          "department": "IT"
        }
      ],
      "message": {
        "subject": "Incident Update: Patient Portal Status - Manual Booking Active",
        "format": "operational_detail",
        "content": {
          "current_status": "Patient Portal degraded (35% availability). Appointment System offline. Manual processes activated.",
          "what_happened": "Database connection pool reached maximum capacity (250 connections), causing application failures.",
          "what_we_are_doing": [
            "Manual appointment booking via phone (ext. 5000) - operational",
            "Patient status page deployed - patients redirected to phone support",
            "Database optimization in progress - connection pool increase from 250 to 500",
            "Application server restart planned for 3:05 PM"
          ],
          "what_you_need_to_do": [
            "Emergency Dept: Direct patients to phone booking (ext. 5000) for appointments",
            "Patient Services: Extra call center staff deployed, manage patient inquiries",
            "IT Operations: Monitor manual workarounds, support recovery team"
          ],
          "timeline": {
            "incident_start": "2:23 PM",
            "workarounds_active": "2:30 PM",
            "expected_resolution": "4:05 PM (ahead of 4:23 PM RTO)"
          },
          "impact_to_your_area": {
            "emergency": "Patients may have delays booking follow-up appointments. Direct to ext. 5000.",
            "patient_services": "Increased call volume expected. Manual booking process available.",
            "it_operations": "All hands supporting recovery. Non-urgent work postponed."
          }
        }
      },
      "delivery": {
        "channel": "email + slack",
        "sent_at": "2025-10-11T14:35:00Z",
        "status": "delivered",
        "slack_channel": "#incident-updates",
        "acknowledgments": 3
      }
    },
    "it_staff": {
      "recipients": "All IT Department Staff",
      "message": {
        "subject": "Incident INC-2025-0234: Technical Update #2",
        "format": "technical_detail",
        "content": {
          "incident_summary": "Patient Portal (patient-portal-prod) and Appointment System (appt-sched-prod) experiencing service degradation due to database connection pool exhaustion.",
          "root_cause": {
            "issue": "PostgreSQL connection pool maxed at 250 connections",
            "trigger": "Gradual connection leak from app servers + higher than normal Friday afternoon traffic",
            "affected_components": [
              "patient-portal-prod (app servers 1-4)",
              "appt-sched-prod (app servers 1-2)",
              "patient-db-primary (PostgreSQL)"
            ]
          },
          "recovery_plan": {
            "phase_1": "Manual workarounds - COMPLETE",
            "phase_2": "DB connection pool increase (250→500) - IN PROGRESS (80%)",
            "phase_3": "App server rolling restart - PENDING (scheduled 3:05 PM)",
            "phase_4": "Validation and monitoring - PENDING"
          },
          "technical_actions": [
            "Sarah Chen: Deploying DB pool config change (ETA 2:38 PM)",
            "David Kim: Preparing app server restart procedure",
            "Mike Johnson: Monitoring manual booking system performance",
            "All: Standby for app server restart coordination"
          ],
          "infrastructure_status": {
            "patient_portal": "Degraded - 35% availability, high error rate",
            "appointment_system": "Offline - manual workaround active",
            "database": "Stable - connection pool at 100% (250/250), no performance issues",
            "network": "Normal",
            "storage": "Normal"
          },
          "what_to_watch": [
            "DB connection pool utilization after config change",
            "App server health during rolling restart",
            "User traffic patterns post-recovery"
          ]
        }
      },
      "delivery": {
        "channel": "slack + email",
        "slack_channel": "#it-team",
        "sent_at": "2025-10-11T14:35:00Z",
        "status": "delivered"
      }
    },
    "response_team": {
      "recipients": "Active Incident Response Team",
      "message": {
        "format": "real_time_updates",
        "channel": "incident_bridge + slack",
        "content": {
          "quick_status": "Root cause confirmed. Recovery 45% complete. On track.",
          "immediate_actions": [
            "Sarah: Complete DB pool deployment (3 min)",
            "David: App server restart prep (10 min)",
            "Lisa: Phone support 100% operational (5 min)"
          ],
          "blockers": "None",
          "next_milestone": "DB pool config deployed by 2:38 PM"
        }
      },
      "delivery": {
        "channel": "slack",
        "slack_channel": "#incident-inc-2025-0234",
        "sent_at": "2025-10-11T14:35:05Z",
        "status": "delivered"
      }
    }
  },
  "communication_metrics": {
    "total_recipients": 47,
    "messages_sent": 52,
    "delivery_rate": "100%",
    "read_rate": "87%",
    "average_time_to_read_minutes": 1.5,
    "acknowledgments": 15
  },
  "next_communication": {
    "scheduled_at": "2025-10-11T15:05:00Z",
    "trigger": "30_minute_interval",
    "type": "status_update",
    "update_number": 3,
    "unless": "significant_change_occurs_earlier"
  },
  "communication_rules": {
    "p1_incidents": {
      "executive_updates": "Every 30 minutes",
      "department_updates": "Every 30 minutes",
      "it_staff_updates": "Every 15 minutes",
      "response_team": "Real-time"
    },
    "escalation_triggers": [
      {
        "condition": "Executive doesn't read update within 15 minutes",
        "action": "SMS notification + phone call"
      },
      {
        "condition": "RTO at 75%",
        "action": "Immediate crisis communication activation"
      }
    ]
  }
}
```

**Events Published**:
```yaml
- event: incident.update.sent
  payload:
    incident_id: INC-2025-0234
    communication_id: comm_int_2025_234_002
    update_number: 2
    recipients: 47
    channels: [email, slack]

- event: incident.update.read
  payload:
    incident_id: INC-2025-0234
    communication_id: comm_int_2025_234_002
    recipient: Dr. Patricia Williams
    read_at: 2025-10-11T14:36:15Z

- event: communication.acknowledgment_required
  trigger: if_critical_stakeholder_no_read_15min
  payload:
    incident_id: INC-2025-0234
    stakeholder: executive
    action: escalate_to_sms_phone
```

**Components Used**:
- Response Service (communication orchestration)
- Notification Service (multi-channel delivery)
- Stakeholder Service (recipient lists, preferences)
- Template Service (message formatting)
- Tracking Service (read receipts, acknowledgments)

**Success Criteria**:
- ✅ Role-appropriate message tailoring
- ✅ 100% delivery rate
- ✅ 85%+ read rate within 15 minutes
- ✅ Automatic escalation for critical stakeholders
- ✅ Scheduled updates at appropriate intervals

**Business Value**:
- **Awareness**: All stakeholders informed appropriately
- **Efficiency**: No unnecessary meeting interruptions
- **Clarity**: Clear, actionable information for each role
- **Accountability**: Full tracking of who knows what when
- **Compliance**: Documentation of stakeholder communication

---

### 5.9 Incident Communication (External)

**Business Context**: Manage external communications to customers, patients, partners, and public during incidents, maintaining transparency while protecting organizational reputation

**Inputs**:
```json
{
  "incident_id": "INC-2025-0234",
  "communication_type": "customer_notification",
  "audience": "external",
  "approved_by": "communications_lead",
  "legal_review": "approved"
}
```

**API Endpoint**: `POST /api/response/incidents/{incident_id}/communicate/external`

**External Communication Workflow**:
```
Incident Impact Assessment → Message Drafting → Legal/PR Review → Multi-Channel Publishing
  ↓
  1. Assess public-facing impact
  2. Draft customer-appropriate message
  3. Legal and PR team review
  4. Executive approval (if required)
  5. Publish across external channels
  6. Monitor social media response
  7. Update as situation evolves
  ↓
Return: communication_sent, channels_used, monitoring_active
```

**Request**:
```json
{
  "incident_id": "INC-2025-0234",
  "external_communication": {
    "audience": "affected_patients",
    "message_type": "service_disruption_notice",
    "tone": "professional_empathetic",
    "channels": ["website", "email", "social_media", "sms"],
    "approval_chain": [
      {
        "role": "communications_lead",
        "approved_by": "Emily Martinez",
        "approved_at": "2025-10-11T14:32:00Z"
      },
      {
        "role": "legal_review",
        "approved_by": "Legal Team",
        "approved_at": "2025-10-11T14:33:30Z"
      }
    ]
  }
}
```

**Response**:
```json
{
  "incident_id": "INC-2025-0234",
  "external_communication": {
    "communication_id": "comm_ext_2025_234_001",
    "type": "customer_service_notification",
    "sent_at": "2025-10-11T14:40:00Z",
    "status": "published"
  },
  "messages": {
    "website_status_page": {
      "channel": "website",
      "url": "https://hospital.com/status",
      "published_at": "2025-10-11T14:40:00Z",
      "message": {
        "title": "Patient Portal - Temporary Service Issues",
        "status_indicator": "degraded_service",
        "content": {
          "headline": "We are experiencing temporary issues with our online patient portal and appointment booking system.",
          "current_status": "Our team is actively working to restore full service. Manual appointment booking is available by phone.",
          "what_you_can_do": [
            "For appointments: Please call (555) 123-5000 - our staff is ready to assist",
            "For urgent medical needs: Call (555) 123-9999 or visit the Emergency Department",
            "For prescription refills: Call your pharmacy or provider's office directly"
          ],
          "expected_resolution": "We expect to restore full online services by 4:30 PM today.",
          "last_updated": "2:40 PM, October 11, 2025",
          "apology": "We apologize for any inconvenience and appreciate your patience."
        }
      },
      "visibility": "public",
      "auto_update": true
    },
    "patient_email": {
      "channel": "email",
      "segment": "active_portal_users",
      "recipients_count": 450,
      "sent_at": "2025-10-11T14:40:05Z",
      "message": {
        "subject": "Important: Temporary Patient Portal Service Update",
        "preheader": "Alternative ways to book appointments and access services",
        "body": {
          "greeting": "Dear Patient,",
          "content": [
            "We want to inform you about temporary technical issues affecting our Patient Portal and online appointment booking.",
            "**What's Affected:**",
            "- Online appointment booking",
            "- Patient Portal login and access",
            "",
            "**How to Access Services:**",
            "- **Book Appointments:** Call (555) 123-5000 (available now)",
            "- **Urgent Needs:** Call (555) 123-9999 or visit Emergency Department",
            "- **Prescriptions:** Contact your pharmacy or provider directly",
            "",
            "**Timeline:**",
            "Our technical team is working diligently to restore full service. We expect the Patient Portal to be fully operational by 4:30 PM today.",
            "",
            "We sincerely apologize for this inconvenience and appreciate your understanding. Your care and safety remain our top priority.",
            "",
            "For questions, please contact Patient Services at (555) 123-6000.",
            "",
            "Thank you for your patience.",
            "",
            "Metropolitan Hospital Patient Services Team"
          ]
        }
      },
      "delivery_status": {
        "sent": 450,
        "delivered": 448,
        "opened": 187,
        "clicked": 42
      }
    },
    "social_media": {
      "platforms": [
        {
          "platform": "twitter",
          "account": "@MetroHospital",
          "posted_at": "2025-10-11T14:40:10Z",
          "post_id": "tweet_834923",
          "message": "SERVICE UPDATE: We're experiencing temporary issues with our Patient Portal. Appointments can be booked by calling (555) 123-5000. We expect full service restoration by 4:30 PM. We apologize for any inconvenience. #PatientCare",
          "engagement": {
            "impressions": 1250,
            "likes": 23,
            "retweets": 8,
            "replies": 15
          },
          "sentiment_monitoring": "active"
        },
        {
          "platform": "facebook",
          "page": "Metropolitan Hospital",
          "posted_at": "2025-10-11T14:40:15Z",
          "post_id": "fb_923847",
          "message": {
            "text": "Important Service Update\n\nWe are currently experiencing temporary technical issues with our Patient Portal and online appointment booking system.\n\n📞 To Book Appointments: Call (555) 123-5000\n🚨 For Urgent Needs: (555) 123-9999 or visit our Emergency Department\n💊 For Prescriptions: Contact your pharmacy directly\n\n⏰ Expected Resolution: 4:30 PM today\n\nOur team is working hard to restore full service. We sincerely apologize for any inconvenience and appreciate your patience.\n\n#PatientCare #ServiceUpdate"
          },
          "engagement": {
            "reach": 3400,
            "reactions": 47,
            "comments": 12,
            "shares": 5
          },
          "comment_monitoring": "active"
        }
      ],
      "sentiment_analysis": {
        "overall_sentiment": "neutral",
        "positive_responses": 35,
        "neutral_responses": 18,
        "negative_responses": 9,
        "concerning_comments": 2,
        "escalation_required": false
      }
    },
    "sms_notification": {
      "channel": "sms",
      "segment": "patients_with_appointments_today",
      "recipients_count": 78,
      "sent_at": "2025-10-11T14:40:20Z",
      "message": {
        "text": "Metropolitan Hospital: Our online booking is temporarily unavailable. Your scheduled appointment is confirmed. For changes, call (555) 123-5000. Full service by 4:30 PM. Thank you."
      },
      "delivery_status": {
        "sent": 78,
        "delivered": 78,
        "failed": 0
      }
    },
    "partner_notification": {
      "channel": "email",
      "recipients": [
        "Referring physicians (25)",
        "Pharmacy partners (8)",
        "Insurance providers (3)"
      ],
      "sent_at": "2025-10-11T14:40:25Z",
      "message": {
        "subject": "Partner Alert: Temporary Patient Portal Service Disruption",
        "content": {
          "summary": "Metropolitan Hospital is experiencing temporary technical issues with our Patient Portal and appointment booking system. Manual processes are in place to ensure continuity of patient care.",
          "impact_to_partners": [
            "Referring Physicians: Patient appointment confirmations may be delayed. Manual booking available at (555) 123-5000.",
            "Pharmacy Partners: Electronic prescription routing unaffected. Portal-based refill requests temporarily unavailable.",
            "Insurance Providers: Claims processing and authorization systems operating normally."
          ],
          "expected_resolution": "4:30 PM today, October 11, 2025",
          "contact": "For questions: Partner Services at (555) 123-7000"
        }
      }
    }
  },
  "media_monitoring": {
    "status": "active",
    "monitoring_keywords": [
      "Metropolitan Hospital",
      "patient portal down",
      "hospital outage",
      "@MetroHospital"
    ],
    "alerts": [
      {
        "platform": "twitter",
        "type": "negative_sentiment_spike",
        "severity": "low",
        "message": "3 tweets expressing frustration about portal access",
        "action_taken": "Social media team responding with helpful alternatives"
      }
    ],
    "media_inquiries": [
      {
        "source": "Local Health Reporter",
        "inquiry": "Request for statement on portal outage",
        "received_at": "2025-10-11T14:42:00Z",
        "assigned_to": "PR Team",
        "response_status": "draft_prepared"
      }
    ]
  },
  "communication_metrics": {
    "total_external_recipients": 564,
    "channels_used": 5,
    "messages_delivered": 562,
    "delivery_rate": "99.6%",
    "engagement_rate": "23%",
    "sentiment_score": 6.5,
    "negative_feedback_count": 9,
    "escalation_required": false
  },
  "crisis_communication_readiness": {
    "level": "standard",
    "media_statement_prepared": true,
    "spokesperson_briefed": true,
    "social_media_team_active": true,
    "escalation_criteria": [
      {
        "trigger": "Media coverage exceeds local scope",
        "action": "Activate full crisis communication plan"
      },
      {
        "trigger": "Negative sentiment >30%",
        "action": "PR Director engagement"
      },
      {
        "trigger": "Service outage >4 hours",
        "action": "Executive spokesperson statement"
      }
    ]
  },
  "regulatory_notifications": {
    "required": false,
    "reason": "Service disruption <4 hours, no patient safety impact, no data breach",
    "monitoring": "Will notify if outage exceeds 4 hours (regulatory threshold)"
  },
  "next_communication": {
    "scheduled_at": "2025-10-11T15:30:00Z",
    "type": "progress_update",
    "trigger": "Upon resolution or every 60 minutes",
    "channels": ["website", "social_media"],
    "content": "Status update: Resolution progress or service restoration announcement"
  }
}
```

**Message Templates** (AI-Generated, Tone-Adjusted):
```json
{
  "template_variations": {
    "empathetic_patient_focus": {
      "tone": "warm, understanding, solution-oriented",
      "example": "We understand how important it is for you to access your healthcare information easily. While we work to restore our online services, we've ensured you can still..."
    },
    "professional_partner_focus": {
      "tone": "business professional, factual, collaborative",
      "example": "We want to inform you of a temporary service disruption affecting our Patient Portal. We have implemented alternative processes to ensure continuity of patient care and partner operations..."
    },
    "transparent_media_statement": {
      "tone": "transparent, factual, confident",
      "example": "Metropolitan Hospital is addressing a temporary technical issue affecting our Patient Portal. Our IT team has identified the root cause and is implementing a fix. Patient care continuity is maintained through established backup processes..."
    }
  }
}
```

**Events Published**:
```yaml
- event: incident.external_communication.sent
  payload:
    incident_id: INC-2025-0234
    communication_id: comm_ext_2025_234_001
    channels: [website, email, social_media, sms]
    recipients: 564

- event: incident.media_inquiry.received
  payload:
    incident_id: INC-2025-0234
    source: Local Health Reporter
    inquiry_type: statement_request
    assigned_to: PR Team

- event: incident.negative_sentiment.detected
  payload:
    incident_id: INC-2025-0234
    platform: twitter
    sentiment_score: 3.2
    action_taken: social_media_team_response

- event: incident.regulatory_notification.required
  trigger: if_outage_exceeds_4_hours
  payload:
    incident_id: INC-2025-0234
    regulatory_body: State Health Department
    notification_type: service_disruption_report
```

**Components Used**:
- Response Service (communication orchestration)
- Communication Service (multi-channel publishing)
- Template Service (message generation, tone adjustment)
- Sentiment Analysis (social monitoring)
- Legal/PR Workflow (approval routing)
- Media Monitoring (reputation management)

**Success Criteria**:
- ✅ All affected customers notified within 30 minutes
- ✅ 99%+ message delivery rate
- ✅ Legal and PR approval obtained
- ✅ Sentiment score maintained >6/10
- ✅ Media inquiries managed proactively

**Business Value**:
- **Transparency**: Proactive customer communication
- **Reputation**: Professional crisis communication
- **Trust**: Consistent, accurate messaging
- **Compliance**: Regulatory notification readiness
- **Brand Protection**: Sentiment monitoring and response

---

## Part 1 of 2 - Scenarios 5.10-5.18 to be continued

**Next Document**: RESPONSE_SERVICE_SCENARIOS_DETAILED_PART2.md will cover:
- 5.10 Incident Resolution & Closure
- 5.11 Post-Incident Review (PIR)
- 5.12 Incident Escalation
- 5.13 Crisis Declaration
- 5.14 Crisis Management Team (CMT) Coordination
- 5.15 Situation Reporting (SitRep)
- 5.16 Media & Public Relations Management
- 5.17 Recovery Coordination (Post-Crisis)
- 5.18 Incident Analytics & Trending

---

## API Reference

### Core Endpoints

```yaml
# Incident Creation
POST /api/response/incidents/auto-create
POST /api/response/incidents/manual-create

# Incident Classification
POST /api/response/incidents/{incident_id}/classify
PUT /api/response/incidents/{incident_id}/reclassify

# Plan Activation
POST /api/response/incidents/{incident_id}/activate-plan
GET /api/response/incidents/{incident_id}/plan-status

# Team Mobilization
POST /api/response/incidents/{incident_id}/mobilize-team
GET /api/response/incidents/{incident_id}/team-status

# Dashboard & Tracking
GET /api/response/incidents/{incident_id}/dashboard
GET /api/response/incidents/{incident_id}/rto-tracking
WS /api/response/incidents/{incident_id}/updates

# Action Management
GET /api/response/incidents/{incident_id}/actions
POST /api/response/incidents/{incident_id}/actions/{action_id}/complete
PUT /api/response/incidents/{incident_id}/actions/{action_id}/progress

# Communications
POST /api/response/incidents/{incident_id}/communicate/internal
POST /api/response/incidents/{incident_id}/communicate/external
GET /api/response/incidents/{incident_id}/communications
```

---

## Event Flow Diagrams

### Incident Detection to Plan Activation Flow

```
Monitoring Alert
    ↓
[Response Service]
    ├─→ Query BIA Data (RTO/RPO)
    ├─→ Calculate Business Impact
    ├─→ Create Incident Record
    ├─→ Classify Severity (P1/P2/P3)
    └─→ Check Activation Criteria
         ↓
    [Planning Service]
         ├─→ Retrieve BC Plan
         ├─→ Generate Action Items
         └─→ Return Plan Details
              ↓
         [Response Service]
              ├─→ Create Plan Activation
              ├─→ Assign Actions to Team
              ├─→ Publish Events
              └─→ Mobilize Team
                   ↓
              [Notification Service]
                   ├─→ Multi-Channel Alerts
                   ├─→ Track Acknowledgments
                   └─→ Escalate if Needed
```

### Communication Workflow

```
Incident Update Required
    ↓
[Response Service]
    ├─→ Identify Stakeholders
    ├─→ Tailor Messages by Role
    └─→ Route for Approval
         ↓
    [Approval Workflow]
         ├─→ Communications Lead Review
         ├─→ Legal Review (if external)
         └─→ Executive Approval (if critical)
              ↓
         [Communication Service]
              ├─→ Format Messages
              ├─→ Multi-Channel Delivery
              ├─→ Track Delivery & Reads
              └─→ Monitor Sentiment (external)
```

---

**Document Status**: ✅ Part 1 Complete (Scenarios 5.1-5.9)
**Last Updated**: 2025-10-11
**Next**: Part 2 with scenarios 5.10-5.18
