# Planning Service - Detailed Scenarios with Examples
## Journey Planning & BC Plan Development - Complete Usage Scenarios (Part 1)

**Service**: Planning Service (Port 8014)
**ISO Clause**: Multiple (4.1 Understanding organization context, 8.4 BC procedures, 9.1 Monitoring)
**Total Scenarios**: 28 (This document covers 3.1-3.7)
**Status**: ✅ Ready for Implementation

---

## Table of Contents

1. [Journey Planning Scenarios (3.1-3.7)](#journey-planning-scenarios)
2. [API Reference](#api-reference)
3. [Event Flow Diagrams](#event-flow-diagrams)

---

## Journey Planning Scenarios

### 3.1 Create ISO 22301 Certification Journey

**Business Context**: Organization wants to achieve ISO 22301 certification and needs an intelligent journey plan that adapts to their maturity level, resources, and timeline

**Inputs**:
```json
{
  "tenant_id": "org_healthcare_001",
  "organization_profile": {
    "name": "City General Hospital",
    "industry": "healthcare",
    "size": "500_employees",
    "locations": 3,
    "revenue": "50M_USD",
    "existing_certifications": ["ISO 9001:2015"],
    "has_bcm_program": false
  },
  "target_certification_date": "2026-06-30",
  "existing_maturity": {
    "level": 1,
    "description": "Ad-hoc processes, no formal BCM",
    "assessment_date": "2025-10-01"
  },
  "available_resources": {
    "dedicated_bcm_manager": true,
    "budget_usd": 75000,
    "internal_team_hours_per_week": 20,
    "external_consultant": false
  },
  "constraints": {
    "must_complete_bia_by": "2025-12-31",
    "limited_it_resources": true,
    "peak_business_seasons": ["June", "December"]
  }
}
```

**API Endpoint**: `POST /api/planning/journey/create`

**Process Flow**:
```
User → Planning Service → Orchestrator → Predictive Engine → AI Foundation
  ↓
  1. Analyze current maturity vs target (Level 1 → Level 5)
  2. Identify gaps (10 ISO clauses fully missing, 5 partial)
  3. Predict realistic timeline using ML (historical data: 350+ journeys)
  4. Generate milestone breakdown (gap analysis → BIA → RA → Plans → Exercises)
  5. Optimize schedule around constraints (avoid June/December)
  6. Assign resources and estimate costs
  7. Create tracking dashboards
  ↓
Return: journey_id, timeline, milestones, confidence_score
```

**AI Analysis Process**:
```
1. Gap Analysis (AI-Powered)
   ├─ Current State: Maturity Level 1
   ├─ Target State: ISO 22301 Certified (Level 5)
   ├─ RAG Query: "ISO 22301 implementation healthcare 500 employees"
   └─ Output: 47 tasks across 10 ISO clauses

2. Timeline Prediction (ML Model)
   ├─ Input Features: [org_size=500, industry=healthcare, maturity=1,
   │                   resources=medium, budget=75k, has_consultant=false]
   ├─ Model: Gradient Boosting (trained on 350+ journeys)
   ├─ Predicted Timeline: 48 weeks ± 6 weeks
   └─ Confidence: 87%

3. Collective Intelligence
   ├─ Query: Similar healthcare orgs (k=5 anonymity)
   ├─ Found: 12 cases, average duration 52 weeks
   └─ Success Pattern: "Start with BIA, parallel risk assessment,
                        avoid big-bang exercises"

4. Constraint Optimization
   ├─ Avoid: June 2026 (peak season)
   ├─ Avoid: December 2025 (peak + BIA deadline)
   ├─ Critical Path: BIA → Risk → BC Plans → Exercises → Audit
   └─ Optimized Schedule: Start Oct 2025, Cert audit May 2026
```

**Response**:
```json
{
  "journey_id": "journey_iso22301_2025_001",
  "status": "planned",
  "overview": {
    "start_date": "2025-10-15",
    "target_certification_date": "2026-06-30",
    "predicted_certification_date": "2026-05-25",
    "total_duration_weeks": 48,
    "confidence_score": 0.87,
    "confidence_rationale": "Based on 12 similar healthcare organizations (k=5 anonymized). Success rate: 83%. Main risk: Limited IT resources may delay digital twin setup."
  },
  "milestones": [
    {
      "milestone_id": "m1",
      "name": "Gap Analysis & Foundation",
      "start_week": 1,
      "end_week": 4,
      "duration_weeks": 4,
      "status": "pending",
      "description": "Conduct ISO 22301 gap analysis, establish BCM policy, define scope",
      "key_deliverables": [
        "Gap analysis report",
        "BCM policy document",
        "BCMS scope statement",
        "BCM organizational structure"
      ],
      "iso_clauses": ["4.1", "4.2", "4.3", "5.2", "5.3"],
      "estimated_effort_hours": 80,
      "assigned_resources": ["BCM Manager", "Executive Sponsor"]
    },
    {
      "milestone_id": "m2",
      "name": "Business Impact Analysis (BIA)",
      "start_week": 5,
      "end_week": 14,
      "duration_weeks": 10,
      "status": "pending",
      "description": "Complete BIA for all critical processes, establish RTO/RPO",
      "key_deliverables": [
        "BIA methodology document",
        "Completed BIA for 25+ processes",
        "Dependency maps",
        "RTO/RPO matrix",
        "BIA report (ISO 8.2.2 compliant)"
      ],
      "iso_clauses": ["8.2.2"],
      "estimated_effort_hours": 160,
      "must_complete_by": "2025-12-31",
      "assigned_resources": ["BCM Manager", "Department Heads"],
      "ai_assistance": [
        "AI-generated interview questions",
        "Real-time interview support",
        "Automated dependency analysis",
        "ML-powered RTO/RPO recommendations"
      ]
    },
    {
      "milestone_id": "m3",
      "name": "Risk Assessment",
      "start_week": 10,
      "end_week": 18,
      "duration_weeks": 9,
      "status": "pending",
      "description": "Identify risks, assess likelihood/impact, develop treatment plans",
      "key_deliverables": [
        "Risk assessment methodology",
        "Risk register (50+ risks)",
        "Risk matrix (5x5)",
        "Risk treatment plans",
        "Residual risk analysis"
      ],
      "iso_clauses": ["8.2.3"],
      "estimated_effort_hours": 120,
      "parallel_with": "m2",
      "assigned_resources": ["BCM Manager", "Risk Manager"],
      "ai_assistance": [
        "ML-powered likelihood prediction",
        "Impact analysis using BIA dependencies",
        "Treatment recommendations from collective intelligence"
      ]
    },
    {
      "milestone_id": "m4",
      "name": "BC Strategy & Plans Development",
      "start_week": 15,
      "end_week": 28,
      "duration_weeks": 14,
      "status": "pending",
      "description": "Define BC strategy, create BC plans for critical processes",
      "key_deliverables": [
        "BC strategy document",
        "Incident response plan",
        "Crisis management plan",
        "IT disaster recovery plan",
        "Departmental BC plans (8+)",
        "Communication plan"
      ],
      "iso_clauses": ["8.3", "8.4"],
      "estimated_effort_hours": 200,
      "assigned_resources": ["BCM Manager", "IT Manager", "Department Heads"],
      "ai_assistance": [
        "AI-generated plans from templates",
        "Auto-filled sections using BIA/RA data",
        "Living documents (auto-update)"
      ]
    },
    {
      "milestone_id": "m5",
      "name": "Training & Awareness",
      "start_week": 20,
      "end_week": 35,
      "duration_weeks": 16,
      "status": "pending",
      "description": "Train BCM team, conduct organization-wide awareness",
      "key_deliverables": [
        "Training program",
        "BCM awareness materials",
        "Training records",
        "Competency assessments"
      ],
      "iso_clauses": ["7.2", "7.3"],
      "estimated_effort_hours": 80,
      "parallel_with": "m4",
      "assigned_resources": ["BCM Manager", "HR"]
    },
    {
      "milestone_id": "m6",
      "name": "Testing & Exercises",
      "start_week": 29,
      "end_week": 40,
      "duration_weeks": 12,
      "status": "pending",
      "description": "Conduct BC plan tests, tabletop exercises, full-scale exercise",
      "key_deliverables": [
        "Exercise program",
        "Tabletop exercise (TTX) x3",
        "Full-scale exercise x1",
        "After-action reports",
        "Plan updates based on lessons"
      ],
      "iso_clauses": ["8.5"],
      "estimated_effort_hours": 120,
      "assigned_resources": ["BCM Manager", "Exercise Coordinator"],
      "ai_assistance": [
        "AI-generated exercise scenarios",
        "Digital twin simulation",
        "Real-time exercise tracking",
        "AI-generated after-action reports"
      ]
    },
    {
      "milestone_id": "m7",
      "name": "Documentation & Evidence Collection",
      "start_week": 30,
      "end_week": 42,
      "duration_weeks": 13,
      "status": "pending",
      "description": "Finalize all documentation, collect audit evidence",
      "key_deliverables": [
        "Document control system",
        "Complete BCMS documentation",
        "Audit evidence package",
        "Management review records"
      ],
      "iso_clauses": ["7.5", "9.3"],
      "estimated_effort_hours": 100,
      "parallel_with": "m6",
      "assigned_resources": ["BCM Manager", "Quality Manager"]
    },
    {
      "milestone_id": "m8",
      "name": "Internal Audit & Management Review",
      "start_week": 41,
      "end_week": 44,
      "duration_weeks": 4,
      "status": "pending",
      "description": "Conduct internal audit, hold management review",
      "key_deliverables": [
        "Internal audit plan",
        "Internal audit report",
        "Corrective actions closed",
        "Management review minutes"
      ],
      "iso_clauses": ["9.2", "9.3"],
      "estimated_effort_hours": 60,
      "assigned_resources": ["Internal Auditor", "Executive Sponsor"]
    },
    {
      "milestone_id": "m9",
      "name": "Certification Audit Preparation",
      "start_week": 44,
      "end_week": 47,
      "duration_weeks": 4,
      "status": "pending",
      "description": "Final readiness check, mock audit, evidence preparation",
      "key_deliverables": [
        "Audit readiness checklist (47 tasks)",
        "Mock audit completed",
        "Evidence package organized",
        "Site prepared for auditors"
      ],
      "iso_clauses": ["All"],
      "estimated_effort_hours": 80,
      "assigned_resources": ["BCM Manager", "All Department Heads"]
    },
    {
      "milestone_id": "m10",
      "name": "Certification Audit (Stage 1 & 2)",
      "start_week": 47,
      "end_week": 50,
      "duration_weeks": 4,
      "status": "pending",
      "description": "Stage 1 documentation review, Stage 2 on-site audit",
      "key_deliverables": [
        "Stage 1 completion",
        "Stage 2 completion",
        "Non-conformities closed",
        "ISO 22301 certificate"
      ],
      "iso_clauses": ["All"],
      "estimated_effort_hours": 120,
      "target_completion": "2026-05-25",
      "assigned_resources": ["BCM Manager", "All Teams"],
      "note": "Buffer: 5 weeks before target date (2026-06-30)"
    }
  ],
  "resource_plan": {
    "total_effort_hours": 1120,
    "weekly_effort_average": 23.3,
    "within_budget": true,
    "budget_breakdown": {
      "consulting_hours": 0,
      "training": 15000,
      "software": 12000,
      "certification_fees": 8000,
      "exercises": 5000,
      "contingency": 10000,
      "total": 50000,
      "remaining_budget": 25000
    }
  },
  "risk_assessment": {
    "overall_risk": "medium",
    "key_risks": [
      {
        "risk": "Limited IT resources may delay digital twin setup",
        "impact": "medium",
        "likelihood": "medium",
        "mitigation": "Use simpler exercise methods (TTX instead of full digital twin)"
      },
      {
        "risk": "BIA deadline (Dec 31) coincides with peak season",
        "impact": "high",
        "likelihood": "low",
        "mitigation": "Start BIA early (Week 5), complete by Week 14"
      },
      {
        "risk": "First-time certification (no prior BCM experience)",
        "impact": "medium",
        "likelihood": "medium",
        "mitigation": "Heavy AI assistance, collective intelligence patterns"
      }
    ]
  },
  "success_factors": {
    "based_on_collective_intelligence": true,
    "similar_orgs_analyzed": 12,
    "top_success_patterns": [
      "Start with comprehensive BIA (don't rush)",
      "Conduct risk assessment in parallel with BIA",
      "Use AI-generated plans to save 60% time",
      "Do 3+ exercises before certification audit",
      "Leave 4-week buffer before target date"
    ]
  },
  "monitoring": {
    "progress_tracking_url": "/api/planning/journey/journey_iso22301_2025_001/progress",
    "dashboard_url": "/dashboard/journey/journey_iso22301_2025_001",
    "weekly_reports": true,
    "at_risk_detection": "enabled"
  }
}
```

**Events Published**:
```yaml
- event: journey.created
  payload:
    journey_id: journey_iso22301_2025_001
    tenant_id: org_healthcare_001
    type: iso_22301_certification
    milestones_count: 10
    total_duration_weeks: 48
    target_date: 2026-06-30
  subscribers:
    - orchestrator (track journey progress)
    - compliance-service (monitor ISO clauses)
    - notification-service (weekly progress emails)
    - dashboard-service (create journey dashboard)
```

**Components Used**:
- Planning Service (main)
- Orchestrator (journey tracking)
- Predictive Engine (timeline ML model)
- AI Foundation (gap analysis, recommendations)
- Collective Intelligence (similar orgs k=5)
- Compliance Service (ISO clause mapping)
- Task Queue (milestone task creation)

**Success Criteria**:
- ✅ Journey created with realistic timeline (confidence >80%)
- ✅ All 10 milestones defined with clear deliverables
- ✅ Resources allocated within budget
- ✅ Constraints respected (peak seasons avoided)
- ✅ Dashboard ready for tracking

**Error Handling**:
```json
{
  "error": "InsufficientResourcesError",
  "message": "Target certification date (2026-06-30) not achievable with current resources",
  "analysis": {
    "minimum_duration_weeks": 48,
    "requested_duration_weeks": 32,
    "required_weekly_hours": 35,
    "available_weekly_hours": 20
  },
  "recommendations": [
    "Extend target date to 2026-10-31 (feasible)",
    "Increase weekly hours to 35 (hire temp resource)",
    "Engage external consultant (reduce duration to 40 weeks)"
  ]
}
```

---

### 3.2 Journey Timeline Prediction (ML-based)

**Business Context**: After creating journey, system continuously predicts actual completion date using ML models trained on 350+ historical journeys, updating predictions as journey progresses

**Inputs**:
```json
{
  "journey_id": "journey_iso22301_2025_001",
  "current_week": 15,
  "actual_progress": {
    "milestones_completed": 2,
    "milestones_total": 10,
    "tasks_completed": 87,
    "tasks_total": 245,
    "completion_percentage": 35.5
  },
  "performance_metrics": {
    "average_task_completion_time_days": 3.2,
    "planned_average_days": 2.8,
    "overdue_tasks": 5,
    "team_engagement_score": 0.78,
    "quality_score": 0.85
  },
  "resource_actuals": {
    "hours_spent_to_date": 420,
    "hours_planned_to_date": 380,
    "budget_spent": 22000,
    "budget_planned": 18000
  }
}
```

**API Endpoint**: `GET /api/planning/journey/{journey_id}/timeline-prediction`

**ML Prediction Process**:
```
1. Feature Engineering
   ├─ Progress Features: completion_%, milestone_velocity, task_velocity
   ├─ Performance Features: time_variance, overdue_rate, engagement, quality
   ├─ Resource Features: hour_variance, budget_variance, team_size
   ├─ Context Features: industry, org_size, maturity_level, has_consultant
   └─ Total Features: 23

2. ML Model (Gradient Boosting Regressor)
   ├─ Training Data: 350+ journeys (50% healthcare, 30% financial, 20% other)
   ├─ Target Variable: actual_completion_week - planned_completion_week
   ├─ Model Performance: MAE=2.3 weeks, R²=0.82
   └─ Feature Importance: [milestone_velocity: 28%, overdue_rate: 22%,
                           hour_variance: 18%, engagement: 15%, ...]

3. Prediction
   ├─ Input: Current journey state (23 features)
   ├─ Output: Predicted delay = +3.2 weeks
   ├─ Confidence Interval: [+1.8 weeks, +4.6 weeks] (80% CI)
   └─ Confidence Score: 84%

4. Contributing Factors Analysis
   ├─ Positive: High quality score (0.85), good engagement (0.78)
   ├─ Negative: Slower task completion (3.2 vs 2.8 days), 5 overdue tasks
   ├─ Main Risk: Hour variance +10.5% (team spending more time than planned)
   └─ Recommendation: Review task complexity estimates, add resources to BIA
```

**Response**:
```json
{
  "journey_id": "journey_iso22301_2025_001",
  "current_status": {
    "current_week": 15,
    "weeks_remaining_planned": 33,
    "completion_percentage": 35.5,
    "on_track": false
  },
  "timeline_prediction": {
    "predicted_completion_week": 51,
    "original_planned_week": 48,
    "predicted_delay_weeks": 3.2,
    "confidence_score": 0.84,
    "confidence_interval_80": {
      "best_case_delay": 1.8,
      "worst_case_delay": 4.6
    },
    "predicted_certification_date": "2026-06-15",
    "original_target_date": "2026-05-25",
    "target_still_achievable": true,
    "buffer_remaining_weeks": 2.8
  },
  "contributing_factors": {
    "positive": [
      {
        "factor": "High quality work",
        "metric": "quality_score",
        "value": 0.85,
        "impact": "+0.8 weeks saved",
        "description": "Deliverables meeting standards on first review"
      },
      {
        "factor": "Good team engagement",
        "metric": "team_engagement_score",
        "value": 0.78,
        "impact": "+0.5 weeks saved",
        "description": "Team actively participating, few blockers"
      }
    ],
    "negative": [
      {
        "factor": "Slower task completion",
        "metric": "avg_task_completion_time",
        "value": 3.2,
        "planned": 2.8,
        "variance": "+14.3%",
        "impact": "+2.1 weeks delay",
        "description": "Tasks taking longer than estimated, especially BIA interviews"
      },
      {
        "factor": "Overdue tasks accumulating",
        "metric": "overdue_tasks",
        "value": 5,
        "impact": "+1.2 weeks delay",
        "description": "5 tasks overdue (average 6 days late)"
      },
      {
        "factor": "Hour variance",
        "metric": "hours_spent_vs_planned",
        "variance": "+10.5%",
        "impact": "+0.9 weeks delay",
        "description": "Team spending more time than planned, may indicate scope creep or complexity underestimation"
      }
    ]
  },
  "recommendations": {
    "immediate_actions": [
      {
        "priority": "high",
        "action": "Review BIA task estimates",
        "rationale": "BIA interviews taking 25% longer than planned. Either complexity underestimated or interviewees unprepared.",
        "suggested_fix": "Increase BIA interview time estimates from 2h to 2.5h, send prep materials to interviewees 48h in advance"
      },
      {
        "priority": "high",
        "action": "Address 5 overdue tasks",
        "rationale": "Overdue tasks create domino effect on dependent tasks",
        "suggested_fix": "Assign BCM Manager to clear overdue backlog this week, escalate 2 critical tasks"
      },
      {
        "priority": "medium",
        "action": "Optimize resource allocation",
        "rationale": "Hour variance +10.5% suggests inefficiencies or scope creep",
        "suggested_fix": "Review task scope, eliminate non-essential work, consider automation (AI-generated content)"
      }
    ],
    "strategic_options": [
      {
        "option": "Accept 3-week delay",
        "pros": "Still achieves target date (5-week buffer), maintains quality",
        "cons": "Reduces buffer from 5 weeks to 2 weeks",
        "recommendation": "Recommended if quality is priority"
      },
      {
        "option": "Accelerate with additional resources",
        "pros": "Get back on track, maintain full buffer",
        "cons": "Budget increase +$5K (0.5 FTE for 8 weeks)",
        "recommendation": "Consider if budget available"
      },
      {
        "option": "Simplify exercise scope",
        "pros": "Save 2 weeks on Exercise milestone",
        "cons": "Reduce from 1 full-scale to 3 TTX only",
        "recommendation": "Not recommended (exercises critical for certification)"
      }
    ]
  },
  "comparison_to_peers": {
    "based_on_collective_intelligence": true,
    "similar_orgs": 12,
    "your_performance_percentile": 62,
    "interpretation": "Performing better than 62% of similar organizations at Week 15",
    "peer_average_delay": 4.8,
    "your_predicted_delay": 3.2,
    "insight": "You're ahead of average. Most delays occur in Exercise milestone (Weeks 29-40)."
  },
  "next_update": "2025-11-22T00:00:00Z",
  "update_frequency": "weekly"
}
```

**Events Published**:
```yaml
- event: journey.timeline.predicted
  payload:
    journey_id: journey_iso22301_2025_001
    predicted_delay_weeks: 3.2
    confidence: 0.84
    on_track: false
    requires_attention: true
  subscribers:
    - orchestrator (track at-risk journeys)
    - notification-service (alert BCM Manager)
    - dashboard-service (update journey dashboard)
```

**Components Used**:
- Planning Service (main)
- Predictive Engine (ML model: Gradient Boosting)
- Analytics Engine (calculate metrics)
- Collective Intelligence (peer comparison k=5)
- Orchestrator (intervention triggers)

**Success Criteria**:
- ✅ Prediction accurate within ±2 weeks (80% confidence)
- ✅ Contributing factors identified
- ✅ Actionable recommendations provided
- ✅ Peer comparison available

---

### 3.3 Journey Milestone Tracking

**Business Context**: Real-time tracking of journey milestones, automatic status updates, and milestone completion workflows with approval processes

**Inputs**:
```json
{
  "journey_id": "journey_iso22301_2025_001",
  "milestone_id": "m2",
  "update_type": "complete",
  "completion_data": {
    "completed_by": "sarah.johnson@hospital.com",
    "completed_date": "2025-12-20",
    "deliverables_submitted": [
      {
        "deliverable": "BIA methodology document",
        "document_id": "doc_bia_method_001",
        "status": "approved",
        "url": "/documents/doc_bia_method_001"
      },
      {
        "deliverable": "Completed BIA for 28 processes",
        "document_id": "doc_bia_results_001",
        "status": "approved",
        "process_count": 28,
        "url": "/documents/doc_bia_results_001"
      },
      {
        "deliverable": "Dependency maps",
        "document_id": "doc_bia_dependencies_001",
        "status": "approved",
        "dependencies_mapped": 142,
        "url": "/documents/doc_bia_dependencies_001"
      },
      {
        "deliverable": "RTO/RPO matrix",
        "document_id": "doc_bia_rto_matrix_001",
        "status": "approved",
        "url": "/documents/doc_bia_rto_matrix_001"
      },
      {
        "deliverable": "BIA report (ISO 8.2.2 compliant)",
        "document_id": "doc_bia_report_001",
        "status": "approved",
        "compliance_score": 0.95,
        "url": "/documents/doc_bia_report_001"
      }
    ],
    "actual_effort_hours": 172,
    "planned_effort_hours": 160,
    "actual_duration_weeks": 11,
    "planned_duration_weeks": 10,
    "notes": "Completed 1 week late due to holiday schedule, but covered 28 processes instead of planned 25. Quality score: 95%."
  }
}
```

**API Endpoint**: `POST /api/planning/journey/{journey_id}/milestone/{milestone_id}/complete`

**Milestone Completion Workflow**:
```
1. Validation
   ├─ Check all deliverables submitted ✅
   ├─ Check deliverables approved ✅
   ├─ Check ISO compliance requirements met ✅
   └─ Check dependencies satisfied ✅

2. Quality Check (AI-Powered)
   ├─ BIA Report Compliance Check (ISO 8.2.2)
   │  ├─ Required sections present: 100%
   │  ├─ RTO/RPO defined for all critical processes: 100%
   │  ├─ Dependencies documented: 100%
   │  ├─ Financial impact calculated: 100%
   │  └─ Compliance Score: 95%
   └─ AI Recommendation: "Excellent quality. Minor improvement: Add regulatory impact analysis for HIPAA-related processes."

3. Update Journey State
   ├─ Mark milestone M2 as "completed"
   ├─ Update journey completion: 35.5% → 43.8%
   ├─ Trigger dependent milestones (M4: BC Plans can now start)
   └─ Update timeline prediction

4. Notifications
   ├─ Notify: BCM Manager (milestone completed)
   ├─ Notify: Risk Manager (M3 can now proceed with BIA data)
   ├─ Notify: Executive Sponsor (progress update)
   └─ Update: Journey dashboard (real-time)

5. Learning
   ├─ Record: Actual vs planned performance
   ├─ Extract: Lessons learned (28 processes vs 25 planned = +12%)
   ├─ Update: ML model training data
   └─ Share: Anonymized success case to Collective Intelligence (k=5)
```

**Response**:
```json
{
  "journey_id": "journey_iso22301_2025_001",
  "milestone_id": "m2",
  "milestone_name": "Business Impact Analysis (BIA)",
  "status": "completed",
  "completion_summary": {
    "completed_date": "2025-12-20",
    "planned_completion_date": "2025-12-13",
    "delay_days": 7,
    "delay_reason": "Holiday schedule (Thanksgiving week)",
    "actual_effort_hours": 172,
    "planned_effort_hours": 160,
    "effort_variance": "+7.5%",
    "deliverables_count": 5,
    "deliverables_approved": 5,
    "quality_score": 0.95
  },
  "deliverables": [
    {
      "deliverable": "BIA methodology document",
      "status": "approved",
      "approved_by": "executive.sponsor@hospital.com",
      "approved_date": "2025-12-18",
      "compliance_check": "passed",
      "url": "/documents/doc_bia_method_001"
    },
    {
      "deliverable": "Completed BIA for 28 processes",
      "status": "approved",
      "processes_analyzed": 28,
      "planned_processes": 25,
      "overdelivery": "+12%",
      "critical_processes": 15,
      "high_priority_processes": 8,
      "medium_priority_processes": 5,
      "url": "/documents/doc_bia_results_001"
    },
    {
      "deliverable": "Dependency maps",
      "status": "approved",
      "dependencies_mapped": 142,
      "process_to_process": 67,
      "process_to_system": 45,
      "process_to_vendor": 30,
      "url": "/documents/doc_bia_dependencies_001"
    },
    {
      "deliverable": "RTO/RPO matrix",
      "status": "approved",
      "processes_with_rto": 28,
      "processes_with_rpo": 22,
      "rto_range": "0-72 hours",
      "ml_recommendations_used": 18,
      "url": "/documents/doc_bia_rto_matrix_001"
    },
    {
      "deliverable": "BIA report (ISO 8.2.2 compliant)",
      "status": "approved",
      "pages": 47,
      "compliance_score": 0.95,
      "iso_clause": "8.2.2",
      "ai_generated_sections": 12,
      "human_reviewed": true,
      "url": "/documents/doc_bia_report_001"
    }
  ],
  "quality_assessment": {
    "overall_score": 0.95,
    "iso_compliance": 0.95,
    "completeness": 1.0,
    "accuracy": 0.92,
    "ai_feedback": "Excellent quality BIA. All ISO 8.2.2 requirements met. Minor improvement: Add regulatory impact analysis for HIPAA-related processes (ED, Surgery, Labs).",
    "recommendations": [
      "Consider adding regulatory impact section to BIA report (HIPAA, state health dept requirements)",
      "Document cyber risk dependencies (ransomware impact on patient data systems)",
      "Excellent overdelivery: 28 processes vs 25 planned shows thoroughness"
    ]
  },
  "journey_impact": {
    "journey_completion_before": 35.5,
    "journey_completion_after": 43.8,
    "journey_progress": "+8.3%",
    "milestones_completed": 3,
    "milestones_remaining": 7,
    "dependent_milestones_unlocked": [
      {
        "milestone_id": "m4",
        "milestone_name": "BC Strategy & Plans Development",
        "can_start_now": true,
        "rationale": "BIA data available for BC plan development"
      }
    ],
    "timeline_impact": {
      "delay_absorbed": "1 week delay absorbed by starting M4 immediately (was planned parallel)",
      "predicted_completion_date": "2026-05-25",
      "still_on_track": true
    }
  },
  "lessons_learned": {
    "what_went_well": [
      "AI-generated interview questions saved 12 hours",
      "Real-time AI support during interviews improved quality",
      "ML-powered RTO recommendations accepted for 18/28 processes (64%)",
      "Automated dependency analysis saved 20 hours"
    ],
    "challenges": [
      "Holiday scheduling (Thanksgiving) caused 1-week delay",
      "Some interviewees unprepared (required follow-up sessions)",
      "IT systems documentation incomplete (slowed dependency mapping)"
    ],
    "improvements_for_next_time": [
      "Block major holidays in journey schedule",
      "Send interview prep materials 1 week in advance (vs 48h)",
      "Pre-populate IT systems inventory before BIA starts"
    ],
    "shared_to_collective_intelligence": true,
    "anonymization_level": "k=5"
  },
  "next_steps": [
    {
      "action": "Start Milestone M4 (BC Strategy & Plans Development)",
      "assigned_to": "BCM Manager",
      "due_date": "2025-12-27",
      "url": "/api/planning/journey/journey_iso22301_2025_001/milestone/m4/start"
    },
    {
      "action": "Continue Milestone M3 (Risk Assessment) using BIA data",
      "assigned_to": "Risk Manager",
      "due_date": "ongoing",
      "note": "Use BIA dependencies for risk impact analysis"
    },
    {
      "action": "Add regulatory impact section to BIA report",
      "assigned_to": "BCM Manager",
      "due_date": "2026-01-10",
      "priority": "low",
      "note": "Nice-to-have improvement suggested by AI"
    }
  ],
  "notifications_sent": [
    "BCM Manager: Milestone M2 completed (email + dashboard)",
    "Executive Sponsor: BIA milestone completed, journey 43.8% complete (email)",
    "Risk Manager: BIA data available for risk assessment (email)",
    "All stakeholders: Progress update posted to dashboard"
  ]
}
```

**Events Published**:
```yaml
- event: journey.milestone.completed
  payload:
    journey_id: journey_iso22301_2025_001
    milestone_id: m2
    milestone_name: Business Impact Analysis (BIA)
    completed_date: 2025-12-20
    quality_score: 0.95
    deliverables: 5
    journey_completion: 43.8
  subscribers:
    - orchestrator (update journey tracking)
    - compliance-service (ISO 8.2.2 evidence collected)
    - planning-service (unlock dependent milestones)
    - notification-service (notify stakeholders)
    - learning-service (record lessons learned)
    - collective-intelligence (share success case k=5)
```

**Components Used**:
- Planning Service (main)
- Compliance Service (ISO 8.2.2 compliance check)
- Documents Service (deliverable validation)
- AI Foundation (quality assessment, recommendations)
- Orchestrator (journey state management)
- Collective Intelligence (share lessons k=5)
- Notification Service (stakeholder alerts)

**Success Criteria**:
- ✅ All deliverables submitted and approved
- ✅ ISO compliance requirements met (95%+)
- ✅ Journey state updated accurately
- ✅ Dependent milestones unlocked
- ✅ Lessons learned captured and shared

---

### 3.4 Journey At-Risk Detection

**Business Context**: Proactive detection of journeys at risk of missing target dates using 6 signals + ML prediction, with automatic intervention recommendations

**Monitoring Signals** (6 types):
```yaml
1. No Activity Signal
   - Trigger: No tasks completed in last 7 days
   - Severity: medium → high (if >14 days)

2. No Progress Signal
   - Trigger: Completion % unchanged in last 14 days
   - Severity: high

3. Low Engagement Signal
   - Trigger: Team engagement score <0.6
   - Calculation: task_completion_rate × communication_frequency × quality_score
   - Severity: medium

4. Deadline Overrun Signal
   - Trigger: Milestone past due date
   - Severity: critical (if >7 days overdue)

5. Resource Variance Signal
   - Trigger: Hour/budget variance >20%
   - Severity: medium → high (if >30%)

6. ML Prediction Signal
   - Trigger: Predicted delay >4 weeks
   - Severity: high (if confidence >80%)
```

**Inputs** (Automatic monitoring, no manual input):
```json
{
  "journey_id": "journey_iso22301_2025_001",
  "current_week": 22,
  "monitoring_data": {
    "last_task_completed": "2025-03-01",
    "days_since_last_activity": 18,
    "completion_percentage": 48.2,
    "completion_percentage_2_weeks_ago": 47.8,
    "current_milestone": "m4",
    "milestone_due_date": "2025-03-10",
    "milestone_current_date": "2025-03-19",
    "milestone_overdue_days": 9,
    "team_engagement_score": 0.54,
    "hour_variance": 28.5,
    "budget_variance": 22.3,
    "ml_predicted_delay_weeks": 6.2,
    "ml_confidence": 0.87
  }
}
```

**API Endpoint**: `GET /api/planning/journey/{journey_id}/at-risk-detection`

**At-Risk Detection Process**:
```
1. Signal Analysis (6 signals)
   ├─ Signal 1: No Activity = 18 days ❌ TRIGGERED (severity: high)
   ├─ Signal 2: No Progress = 0.4% in 14 days ❌ TRIGGERED (severity: high)
   ├─ Signal 3: Low Engagement = 0.54 ❌ TRIGGERED (severity: medium)
   ├─ Signal 4: Deadline Overrun = M4 overdue 9 days ❌ TRIGGERED (severity: critical)
   ├─ Signal 5: Resource Variance = 28.5% hours ❌ TRIGGERED (severity: high)
   └─ Signal 6: ML Prediction = 6.2 weeks delay ❌ TRIGGERED (severity: high)

2. Overall Risk Assessment
   ├─ Signals Triggered: 6/6 (100%)
   ├─ Critical Signals: 1 (Deadline Overrun)
   ├─ High Signals: 4
   ├─ Medium Signals: 1
   └─ Overall Risk: CRITICAL

3. Root Cause Analysis (AI-Powered)
   ├─ Primary Issue: BCM Manager on unexpected medical leave (2 weeks)
   ├─ Secondary Issue: No backup resource assigned
   ├─ Impact: BC Plans development stalled (Milestone M4)
   └─ Cascading Effect: Dependent milestones (M5, M6) at risk

4. Collective Intelligence Search
   ├─ Query: "BCM journey key person absence recovery" (k=5)
   ├─ Found: 8 similar cases
   ├─ Success Pattern: "Assign temp resource + simplify plans + extend 3 weeks"
   ├─ Success Rate: 75% (6/8 recovered, 2 abandoned)
   └─ Average Recovery Time: 4 weeks

5. Intervention Recommendations (Ranked by ML)
   ├─ Option 1: Assign backup resource (success prob: 85%, cost: $8K)
   ├─ Option 2: Simplify BC plans scope (success prob: 70%, cost: $0)
   ├─ Option 3: Extend timeline 6 weeks (success prob: 60%, cost: $0)
   └─ Option 4: Engage external consultant (success prob: 90%, cost: $15K)
```

**Response**:
```json
{
  "journey_id": "journey_iso22301_2025_001",
  "at_risk_status": {
    "is_at_risk": true,
    "risk_level": "critical",
    "risk_score": 0.92,
    "detected_date": "2025-03-19",
    "requires_immediate_action": true
  },
  "signals_triggered": {
    "count": 6,
    "total": 6,
    "details": [
      {
        "signal": "no_activity",
        "triggered": true,
        "severity": "high",
        "value": 18,
        "threshold": 14,
        "description": "No tasks completed in 18 days (threshold: 14 days)"
      },
      {
        "signal": "no_progress",
        "triggered": true,
        "severity": "high",
        "value": 0.4,
        "threshold": 2.0,
        "description": "Journey progress only 0.4% in last 14 days (expected: 2%/week)"
      },
      {
        "signal": "low_engagement",
        "triggered": true,
        "severity": "medium",
        "value": 0.54,
        "threshold": 0.6,
        "description": "Team engagement score 0.54 (threshold: 0.6)"
      },
      {
        "signal": "deadline_overrun",
        "triggered": true,
        "severity": "critical",
        "milestone": "m4",
        "milestone_name": "BC Strategy & Plans Development",
        "due_date": "2025-03-10",
        "days_overdue": 9,
        "description": "Milestone M4 overdue by 9 days"
      },
      {
        "signal": "resource_variance",
        "triggered": true,
        "severity": "high",
        "hour_variance": 28.5,
        "budget_variance": 22.3,
        "threshold": 20,
        "description": "Hour variance 28.5% (threshold: 20%)"
      },
      {
        "signal": "ml_prediction",
        "triggered": true,
        "severity": "high",
        "predicted_delay_weeks": 6.2,
        "confidence": 0.87,
        "threshold_delay": 4,
        "description": "ML model predicts 6.2 weeks delay (confidence 87%)"
      }
    ]
  },
  "root_cause_analysis": {
    "primary_cause": "Key person absence",
    "details": "BCM Manager on unexpected medical leave (started 2025-03-01, expected return 2025-03-22)",
    "impact": "Milestone M4 (BC Plans) development completely stalled",
    "no_backup_resource": true,
    "knowledge_transfer_incomplete": true,
    "cascading_risks": [
      "M5 (Training) delayed (depends on M4 plans)",
      "M6 (Exercises) delayed (depends on M4 plans)",
      "M9 (Audit prep) at risk if delays cascade"
    ],
    "confidence": 0.91
  },
  "collective_intelligence_insights": {
    "similar_cases_found": 8,
    "anonymization_level": "k=5",
    "success_pattern": "Assign temporary backup resource + simplify plan scope + extend timeline moderately",
    "success_rate": 0.75,
    "average_recovery_time_weeks": 4,
    "key_lessons": [
      "Don't wait for key person return - assign backup immediately",
      "Simplify BC plan scope (use AI-generated templates, fewer custom plans)",
      "Extend timeline realistically (3-4 weeks better than optimistic 1 week)",
      "Maintain momentum with quick wins (complete easy tasks first)"
    ]
  },
  "intervention_recommendations": [
    {
      "rank": 1,
      "intervention": "Assign backup resource + AI assistance",
      "description": "Assign senior team member as temp BCM lead, leverage AI-generated BC plans heavily",
      "success_probability": 0.85,
      "recovery_time_weeks": 3,
      "cost_usd": 8000,
      "pros": [
        "Fastest recovery",
        "Maintains quality",
        "Team learns BCM (knowledge distribution)",
        "AI-generated plans save 60% time"
      ],
      "cons": [
        "Cost increase $8K",
        "Backup resource has other duties (prioritization needed)"
      ],
      "action_plan": [
        "Assign John Smith (IT Manager) as temp BCM lead this week",
        "1-day knowledge transfer session with BCM Manager (phone/video)",
        "Use AI to generate all 8 BC plans from templates",
        "BCM Manager reviews plans remotely (final approval)",
        "Resume normal operations when BCM Manager returns Week 25"
      ],
      "estimated_new_completion_date": "2026-06-10",
      "still_meets_target": true
    },
    {
      "rank": 2,
      "intervention": "Simplify BC plan scope",
      "description": "Reduce from 8 detailed plans to 4 critical plans + 4 lightweight plans",
      "success_probability": 0.70,
      "recovery_time_weeks": 4,
      "cost_usd": 0,
      "pros": [
        "No additional cost",
        "Still meets ISO 22301 minimum requirements",
        "Faster completion"
      ],
      "cons": [
        "Lower quality plans (may need rework post-certification)",
        "Some departments not covered in detail",
        "Longer recovery time than Option 1"
      ],
      "action_plan": [
        "Identify 4 critical processes (ED, Surgery, IT, Labs)",
        "Develop detailed BC plans for critical 4 only",
        "Use AI-generated lightweight plans for remaining 4",
        "Schedule post-certification plan enhancement"
      ],
      "estimated_new_completion_date": "2026-06-20",
      "still_meets_target": true
    },
    {
      "rank": 3,
      "intervention": "Extend timeline 6 weeks",
      "description": "Extend certification target from 2026-05-25 to 2026-07-06 (still within goal 2026-06-30)",
      "success_probability": 0.60,
      "recovery_time_weeks": 6,
      "cost_usd": 0,
      "pros": [
        "No additional cost",
        "No scope reduction",
        "Less pressure on team"
      ],
      "cons": [
        "Uses entire buffer (no safety margin)",
        "Risk of missing 2026-06-30 goal if further delays",
        "Team momentum may decline with extended timeline"
      ],
      "not_recommended": true,
      "recommendation_note": "Only use if Options 1 & 2 not feasible. Risky - no buffer remaining."
    },
    {
      "rank": 4,
      "intervention": "Engage external BCM consultant",
      "description": "Hire external consultant for 6 weeks to complete BC plans",
      "success_probability": 0.90,
      "recovery_time_weeks": 2,
      "cost_usd": 15000,
      "pros": [
        "Fastest recovery (2 weeks)",
        "Highest success rate (90%)",
        "Expert quality plans",
        "No internal resource impact"
      ],
      "cons": [
        "High cost ($15K)",
        "Exceeds remaining budget ($25K - $22K spent = $3K)",
        "Requires budget approval",
        "Less knowledge transfer to internal team"
      ],
      "requires_approval": "Executive Sponsor (budget increase)",
      "action_plan": [
        "Get executive approval for $12K budget increase",
        "Engage consultant (pre-qualified vendor, 5 days to start)",
        "Consultant develops 8 BC plans in 2 weeks",
        "Internal team reviews and approves",
        "Resume normal journey Week 24"
      ],
      "estimated_new_completion_date": "2026-05-28",
      "still_meets_target": true
    }
  ],
  "recommended_action": {
    "recommendation": "Option 1: Assign backup resource + AI assistance",
    "rationale": "Best balance of speed, cost, and quality. Moderate cost ($8K within budget tolerance), high success rate (85%), reasonable recovery time (3 weeks). Builds internal capability. AI assistance reduces effort by 60%.",
    "urgency": "Immediate (start this week)",
    "requires_approval": "Executive Sponsor (notify, no budget approval needed)",
    "executive_summary": "Journey at critical risk due to BCM Manager medical leave. Recommend assigning IT Manager as temp BCM lead + heavy AI assistance. Cost: $8K, Recovery: 3 weeks, Success rate: 85%. Still meets 2026-06-30 target."
  },
  "orchestrator_actions": {
    "notification_sent": true,
    "escalation_level": "executive",
    "recipients": [
      "BCM Manager (sarah.johnson@hospital.com)",
      "Executive Sponsor (ceo@hospital.com)",
      "IT Manager - proposed backup (john.smith@hospital.com)"
    ],
    "intervention_workflow_created": true,
    "intervention_id": "intervention_2025_001",
    "auto_actions_taken": [
      "Created intervention workflow",
      "Notified executive sponsor",
      "Prepared Option 1 action plan template",
      "Scheduled AI assistance session for backup resource",
      "Generated 8 BC plan templates (AI) ready for review"
    ]
  },
  "monitoring": {
    "recheck_date": "2025-03-26",
    "recheck_frequency": "every_3_days",
    "success_criteria": [
      "Backup resource assigned and started",
      "At least 2 BC plans drafted by Week 23",
      "Milestone M4 completion by Week 25",
      "Journey back on track (risk_level < medium) by Week 26"
    ]
  }
}
```

**Events Published**:
```yaml
- event: journey.at_risk.detected
  payload:
    journey_id: journey_iso22301_2025_001
    risk_level: critical
    risk_score: 0.92
    signals_triggered: 6
    primary_cause: key_person_absence
    recommended_intervention: assign_backup_resource
    requires_executive_approval: false
    estimated_recovery_weeks: 3
  subscribers:
    - orchestrator (create intervention workflow)
    - notification-service (escalate to executive)
    - planning-service (prepare intervention options)
    - ai-foundation (generate BC plan templates)
```

**Components Used**:
- Planning Service (main)
- Orchestrator (at-risk monitoring, intervention workflows)
- Predictive Engine (ML delay prediction)
- AI Foundation (root cause analysis, recommendations)
- Collective Intelligence (similar cases k=5)
- Notification Service (executive escalation)

**Success Criteria**:
- ✅ At-risk detected within 3 days of trigger
- ✅ Root cause identified with >80% confidence
- ✅ 4+ intervention options provided
- ✅ Recommended action ranked by ML
- ✅ Executive notified immediately

---

### 3.5 Journey Recovery Plan Generation

**Business Context**: When journey is at risk, system generates detailed recovery plan using AI + Collective Intelligence + ML, with specific actions, timelines, and resource allocation

**Inputs**:
```json
{
  "journey_id": "journey_iso22301_2025_001",
  "at_risk_detection_id": "risk_2025_001",
  "selected_intervention": "assign_backup_resource_ai",
  "intervention_parameters": {
    "backup_resource": {
      "name": "John Smith",
      "role": "IT Manager",
      "email": "john.smith@hospital.com",
      "availability_hours_per_week": 20,
      "bcm_experience": "basic",
      "start_date": "2025-03-22"
    },
    "ai_assistance_level": "heavy",
    "budget_approved": 8000,
    "target_recovery_weeks": 3,
    "maintain_quality": true
  }
}
```

**API Endpoint**: `POST /api/planning/journey/{journey_id}/recovery-plan/generate`

**Recovery Plan Generation Process**:
```
1. Analyze Current Situation
   ├─ Journey Status: 48.2% complete, Week 22/48, at risk
   ├─ Blocked Milestone: M4 (BC Plans), 9 days overdue
   ├─ Root Cause: BCM Manager medical leave
   ├─ Cascading Impact: M5, M6 at risk
   └─ Target: Recover by Week 25, back on track by Week 26

2. AI Foundation (Claude Opus) - Recovery Strategy
   ├─ Input: Journey state + intervention params + collective intelligence
   ├─ Generate: Step-by-step recovery plan
   ├─ Optimize: Resource allocation, timeline, risk mitigation
   └─ Output: 23-action recovery plan

3. ML Model - Success Probability Prediction
   ├─ Input: Recovery plan features (actions, timeline, resources)
   ├─ Model: Random Forest (trained on 150+ interventions)
   ├─ Output: Success probability 85%, confidence 82%
   └─ Risk Factors: [backup_bcm_experience: basic (-5%),
                     tight_timeline: 3_weeks (-8%),
                     heavy_ai: +15%,
                     budget_adequate: +10%]

4. Collective Intelligence - Validate Strategy
   ├─ Query: "BCM journey backup resource AI assistance recovery" (k=5)
   ├─ Found: 6 similar recoveries
   ├─ Validation: Strategy matches 5/6 successful cases
   └─ Confidence: High

5. Generate Detailed Action Plan
   ├─ Week 22: Knowledge transfer, AI plan generation
   ├─ Week 23-24: Plan review, quality check, approval
   ├─ Week 25: Milestone M4 completion
   └─ Week 26: Resume normal operations

6. Create Tracking & Monitoring
   ├─ Daily check-ins (first week)
   ├─ Recovery metrics dashboard
   ├─ Success criteria checklist
   └─ Early warning signals
```

**Response**:
```json
{
  "journey_id": "journey_iso22301_2025_001",
  "recovery_plan_id": "recovery_2025_001",
  "intervention_type": "assign_backup_resource_ai",
  "created_date": "2025-03-19",
  "status": "ready_to_execute",
  "overview": {
    "current_situation": "Journey at critical risk due to BCM Manager medical leave. Milestone M4 (BC Plans) 9 days overdue.",
    "recovery_strategy": "Assign IT Manager as temp BCM lead with heavy AI assistance to complete BC Plans",
    "recovery_timeline_weeks": 3,
    "target_back_on_track": "Week 26",
    "success_probability": 0.85,
    "confidence": 0.82,
    "estimated_cost": 8000,
    "budget_approved": true
  },
  "recovery_actions": {
    "total_actions": 23,
    "critical_path_actions": 8,
    "actions_by_week": {
      "week_22": {
        "week_name": "Week 22: Emergency Response & Knowledge Transfer",
        "dates": "2025-03-19 to 2025-03-25",
        "actions": [
          {
            "action_id": "r1",
            "priority": "critical",
            "action": "Notify Executive Sponsor and get approval",
            "assigned_to": "Planning Service (automated)",
            "due_date": "2025-03-19",
            "duration_hours": 1,
            "status": "completed",
            "dependencies": []
          },
          {
            "action_id": "r2",
            "priority": "critical",
            "action": "Contact John Smith (IT Manager) and confirm availability",
            "assigned_to": "Executive Sponsor",
            "due_date": "2025-03-20",
            "duration_hours": 2,
            "status": "pending",
            "dependencies": ["r1"]
          },
          {
            "action_id": "r3",
            "priority": "critical",
            "action": "Schedule knowledge transfer session with BCM Manager (remote)",
            "assigned_to": "Executive Sponsor",
            "due_date": "2025-03-21",
            "duration_hours": 1,
            "status": "pending",
            "dependencies": ["r2"],
            "details": "Video call, 2 hours, cover: BC plan structure, templates, approval workflow, key contacts"
          },
          {
            "action_id": "r4",
            "priority": "critical",
            "action": "Conduct knowledge transfer session",
            "assigned_to": "BCM Manager (remote) + John Smith",
            "due_date": "2025-03-22",
            "duration_hours": 2,
            "status": "pending",
            "dependencies": ["r3"],
            "details": "Cover: BC plan requirements, ISO 8.4 compliance, department priorities, approval process"
          },
          {
            "action_id": "r5",
            "priority": "high",
            "action": "AI generates 8 BC plans from templates",
            "assigned_to": "AI Foundation (automated)",
            "due_date": "2025-03-22",
            "duration_hours": 0.5,
            "status": "pending",
            "dependencies": ["r3"],
            "details": "AI uses: BIA data (28 processes), risk assessment data, ISO 8.4 templates, industry best practices (healthcare)"
          },
          {
            "action_id": "r6",
            "priority": "high",
            "action": "John Smith reviews AI-generated BC plans (initial pass)",
            "assigned_to": "John Smith",
            "due_date": "2025-03-24",
            "duration_hours": 8,
            "status": "pending",
            "dependencies": ["r4", "r5"],
            "details": "Review all 8 plans, flag issues/gaps, identify plans needing customization"
          },
          {
            "action_id": "r7",
            "priority": "medium",
            "action": "Send recovery plan to stakeholders",
            "assigned_to": "Planning Service (automated)",
            "due_date": "2025-03-22",
            "duration_hours": 0.5,
            "status": "pending",
            "dependencies": ["r2"],
            "details": "Notify: Executive Sponsor, Department Heads, BCM Manager. Include: recovery timeline, new point of contact (John), expectations"
          }
        ]
      },
      "week_23": {
        "week_name": "Week 23: BC Plan Review & Customization",
        "dates": "2025-03-26 to 2025-04-01",
        "actions": [
          {
            "action_id": "r8",
            "priority": "critical",
            "action": "Prioritize 4 critical BC plans for detailed review",
            "assigned_to": "John Smith",
            "due_date": "2025-03-26",
            "duration_hours": 2,
            "status": "pending",
            "dependencies": ["r6"],
            "details": "Critical plans: 1) Emergency Department, 2) Surgery/OR, 3) IT Systems, 4) Laboratory"
          },
          {
            "action_id": "r9",
            "priority": "critical",
            "action": "Customize BC Plan #1: Emergency Department",
            "assigned_to": "John Smith + ED Manager",
            "due_date": "2025-03-27",
            "duration_hours": 4,
            "status": "pending",
            "dependencies": ["r8"],
            "details": "Review AI draft, add department-specific details, validate RTOs, review dependencies, add contact lists"
          },
          {
            "action_id": "r10",
            "priority": "critical",
            "action": "Customize BC Plan #2: Surgery/OR",
            "assigned_to": "John Smith + Surgery Manager",
            "due_date": "2025-03-28",
            "duration_hours": 4,
            "status": "pending",
            "dependencies": ["r8"],
            "details": "Review AI draft, surgical protocols during disruption, patient transfer procedures"
          },
          {
            "action_id": "r11",
            "priority": "critical",
            "action": "Customize BC Plan #3: IT Systems",
            "assigned_to": "John Smith (owner)",
            "due_date": "2025-03-29",
            "duration_hours": 4,
            "status": "pending",
            "dependencies": ["r8"],
            "details": "John's expertise area - detailed IT DR plan, system recovery sequences, data backup verification"
          },
          {
            "action_id": "r12",
            "priority": "critical",
            "action": "Customize BC Plan #4: Laboratory",
            "assigned_to": "John Smith + Lab Manager",
            "due_date": "2025-03-30",
            "duration_hours": 4,
            "status": "pending",
            "dependencies": ["r8"],
            "details": "Lab-specific continuity, external lab partnerships, test prioritization"
          },
          {
            "action_id": "r13",
            "priority": "medium",
            "action": "Light review of remaining 4 BC plans",
            "assigned_to": "John Smith",
            "due_date": "2025-04-01",
            "duration_hours": 4,
            "status": "pending",
            "dependencies": ["r6"],
            "details": "Plans: Pharmacy, Radiology, Admin, Finance. AI drafts sufficient, light customization only"
          },
          {
            "action_id": "r14",
            "priority": "high",
            "action": "AI Quality Check: All 8 BC plans",
            "assigned_to": "AI Foundation (automated)",
            "due_date": "2025-04-01",
            "duration_hours": 0.5,
            "status": "pending",
            "dependencies": ["r12", "r13"],
            "details": "Check: ISO 8.4 compliance, completeness, consistency, missing sections, quality score"
          }
        ]
      },
      "week_24": {
        "week_name": "Week 24: Approval & Finalization",
        "dates": "2025-04-02 to 2025-04-08",
        "actions": [
          {
            "action_id": "r15",
            "priority": "high",
            "action": "Address AI quality check findings",
            "assigned_to": "John Smith",
            "due_date": "2025-04-03",
            "duration_hours": 4,
            "status": "pending",
            "dependencies": ["r14"],
            "details": "Fix gaps, add missing sections, improve quality scores to >90%"
          },
          {
            "action_id": "r16",
            "priority": "critical",
            "action": "BCM Manager final review (remote)",
            "assigned_to": "BCM Manager (Sarah Johnson)",
            "due_date": "2025-04-05",
            "duration_hours": 6,
            "status": "pending",
            "dependencies": ["r15"],
            "details": "Review all 8 plans, final approval authority, request changes if needed"
          },
          {
            "action_id": "r17",
            "priority": "high",
            "action": "Implement BCM Manager feedback",
            "assigned_to": "John Smith",
            "due_date": "2025-04-06",
            "duration_hours": 3,
            "status": "pending",
            "dependencies": ["r16"],
            "details": "Make final revisions based on BCM Manager comments"
          },
          {
            "action_id": "r18",
            "priority": "critical",
            "action": "Executive Sponsor approval",
            "assigned_to": "Executive Sponsor",
            "due_date": "2025-04-07",
            "duration_hours": 2,
            "status": "pending",
            "dependencies": ["r17"],
            "details": "Final sign-off on all 8 BC plans"
          },
          {
            "action_id": "r19",
            "priority": "high",
            "action": "Publish approved BC plans to document repository",
            "assigned_to": "John Smith",
            "due_date": "2025-04-08",
            "duration_hours": 1,
            "status": "pending",
            "dependencies": ["r18"],
            "details": "Upload to document control system, set version 1.0, assign access controls"
          },
          {
            "action_id": "r20",
            "priority": "critical",
            "action": "Mark Milestone M4 as COMPLETED",
            "assigned_to": "Planning Service (automated)",
            "due_date": "2025-04-08",
            "duration_hours": 0.5,
            "status": "pending",
            "dependencies": ["r19"],
            "details": "Update journey status, trigger M5 & M6 start"
          }
        ]
      },
      "week_25_26": {
        "week_name": "Week 25-26: Handoff & Resume Normal Operations",
        "dates": "2025-04-09 to 2025-04-22",
        "actions": [
          {
            "action_id": "r21",
            "priority": "high",
            "action": "BCM Manager returns to work",
            "assigned_to": "BCM Manager",
            "due_date": "2025-04-09",
            "duration_hours": 0,
            "status": "pending",
            "dependencies": [],
            "details": "Expected return date"
          },
          {
            "action_id": "r22",
            "priority": "high",
            "action": "Handoff meeting: John → Sarah",
            "assigned_to": "John Smith + BCM Manager",
            "due_date": "2025-04-10",
            "duration_hours": 2,
            "status": "pending",
            "dependencies": ["r21"],
            "details": "Transfer knowledge, review recovery process, document lessons learned, thank John for stepping up"
          },
          {
            "action_id": "r23",
            "priority": "medium",
            "action": "Recovery retrospective & lessons learned",
            "assigned_to": "Planning Service + Orchestrator",
            "due_date": "2025-04-15",
            "duration_hours": 1,
            "status": "pending",
            "dependencies": ["r22"],
            "details": "Document: What worked (AI assistance!), what didn't, improvements. Share to Collective Intelligence (k=5)"
          }
        ]
      }
    }
  },
  "critical_path": [
    "r1 → r2 → r3 → r4 → r5 → r6 → r8 → r9,r10,r11,r12 → r14 → r15 → r16 → r17 → r18 → r19 → r20 → r21 → r22"
  ],
  "resource_allocation": {
    "john_smith_hours": {
      "week_22": 10,
      "week_23": 20,
      "week_24": 12,
      "total": 42,
      "rate_per_hour": 190,
      "cost": 7980
    },
    "bcm_manager_remote_hours": {
      "week_22": 2,
      "week_24": 6,
      "week_25": 2,
      "total": 10,
      "note": "Remote support while on medical leave (approved)"
    },
    "department_heads_hours": {
      "total": 16,
      "note": "Plan review meetings"
    },
    "ai_foundation_usage": {
      "plan_generation": "8 BC plans",
      "quality_checks": "3 iterations",
      "estimated_human_hours_saved": 60,
      "note": "AI reduced effort by 58% (60h saved from typical 103h)"
    }
  },
  "success_metrics": {
    "primary_kpis": [
      {
        "kpi": "Milestone M4 completed",
        "target_date": "2025-04-08",
        "status": "pending"
      },
      {
        "kpi": "Journey back on track (risk_level < medium)",
        "target_date": "2025-04-15",
        "status": "pending"
      },
      {
        "kpi": "All 8 BC plans approved with quality >90%",
        "target": 8,
        "status": "pending"
      },
      {
        "kpi": "Recovery completed within budget",
        "budget": 8000,
        "estimated_cost": 7980,
        "status": "within_budget"
      }
    ],
    "secondary_kpis": [
      {
        "kpi": "Knowledge transfer successful",
        "measure": "John Smith comfortable leading BCM (if needed again)"
      },
      {
        "kpi": "Lessons learned documented",
        "target": "Shared to Collective Intelligence (k=5)"
      }
    ]
  },
  "risk_mitigation": {
    "risks_identified": [
      {
        "risk": "John Smith (backup) overwhelmed with dual role",
        "likelihood": "medium",
        "impact": "high",
        "mitigation": "Heavy AI assistance (58% effort reduction), BCM Manager remote support, prioritize critical 4 plans only"
      },
      {
        "risk": "AI-generated plans lack quality",
        "likelihood": "low",
        "impact": "medium",
        "mitigation": "AI quality check, BCM Manager final review, human customization for critical plans"
      },
      {
        "risk": "BCM Manager unable to return Week 25",
        "likelihood": "low",
        "impact": "high",
        "mitigation": "John continues until return, extend timeline if needed (buffer available)"
      }
    ]
  },
  "collective_intelligence_validation": {
    "similar_recoveries": 6,
    "matching_strategy": 5,
    "success_rate_peers": 0.83,
    "confidence": "high",
    "key_insight": "AI assistance is game-changer for backup resource success (success rate: 85% with AI vs 60% without)"
  },
  "monitoring_plan": {
    "check_in_frequency": {
      "week_22": "daily",
      "week_23_24": "every_2_days",
      "week_25_26": "weekly"
    },
    "dashboard_url": "/dashboard/journey/journey_iso22301_2025_001/recovery",
    "automated_tracking": [
      "Action completion status",
      "Critical path adherence",
      "Quality scores",
      "Budget tracking",
      "Early warning signals"
    ],
    "escalation_triggers": [
      "2+ critical actions missed",
      "Quality score <85%",
      "John Smith requests help",
      "BCM Manager return delayed >1 week"
    ]
  },
  "communication_plan": {
    "stakeholder_updates": {
      "executive_sponsor": "End of Week 22, 24, 26",
      "department_heads": "Weekly (Fridays)",
      "john_smith": "Daily check-ins Week 22, then as needed",
      "bcm_manager": "Weekly updates on recovery progress"
    },
    "format": "Email summary + dashboard link"
  }
}
```

**Events Published**:
```yaml
- event: journey.recovery_plan.generated
  payload:
    journey_id: journey_iso22301_2025_001
    recovery_plan_id: recovery_2025_001
    intervention_type: assign_backup_resource_ai
    total_actions: 23
    recovery_weeks: 3
    success_probability: 0.85
    estimated_cost: 7980
  subscribers:
    - orchestrator (execute recovery workflow)
    - notification-service (notify stakeholders)
    - task-queue (create 23 recovery tasks)
    - monitoring-service (track recovery progress)
```

**Components Used**:
- Planning Service (main)
- AI Foundation (Claude Opus - recovery strategy)
- Predictive Engine (ML - success probability)
- Collective Intelligence (validate strategy k=5)
- Orchestrator (execute recovery workflow)
- Task Queue (create & track 23 actions)
- Notification Service (stakeholder updates)

**Success Criteria**:
- ✅ Recovery plan generated within 2 hours
- ✅ 20+ specific actions with clear owners
- ✅ Success probability >80%
- ✅ Budget within approved amount
- ✅ Validated against peer cases (k=5)

---

### 3.6 Journey Progress Dashboard

**Business Context**: Real-time visual dashboard showing journey progress, milestones, tasks, timeline, risks, and AI insights

**Inputs** (Dashboard URL access):
```
GET /api/planning/journey/{journey_id}/progress-dashboard
```

**API Endpoint**: `GET /api/planning/journey/{journey_id}/progress-dashboard`

**Dashboard Data Structure**:
```json
{
  "journey_id": "journey_iso22301_2025_001",
  "dashboard_generated": "2025-03-19T14:30:00Z",
  "refresh_interval_seconds": 300,
  "organization": {
    "tenant_id": "org_healthcare_001",
    "name": "City General Hospital",
    "industry": "healthcare"
  },
  "overview": {
    "journey_name": "ISO 22301 Certification Journey",
    "status": "at_risk",
    "status_color": "red",
    "start_date": "2025-10-15",
    "current_date": "2025-03-19",
    "target_completion_date": "2026-05-25",
    "predicted_completion_date": "2026-06-15",
    "weeks_elapsed": 22,
    "weeks_remaining": 26,
    "total_weeks": 48,
    "completion_percentage": 48.2,
    "on_track": false,
    "risk_level": "critical"
  },
  "progress_chart": {
    "type": "line_chart",
    "data": {
      "weeks": [0, 4, 8, 12, 16, 20, 22],
      "planned_completion": [0, 8, 16, 25, 35, 45, 48],
      "actual_completion": [0, 9, 18, 28, 42, 48, 48.2],
      "predicted_trajectory": [48.2, 50, 55, 62, 70, 80, 90, 100]
    },
    "annotations": [
      {
        "week": 22,
        "label": "At Risk Detected",
        "color": "red"
      },
      {
        "week": 25,
        "label": "Expected Recovery",
        "color": "orange"
      }
    ]
  },
  "milestones": {
    "total": 10,
    "completed": 3,
    "in_progress": 1,
    "pending": 6,
    "overdue": 1,
    "milestones_list": [
      {
        "milestone_id": "m1",
        "name": "Gap Analysis & Foundation",
        "status": "completed",
        "completion_date": "2025-11-10",
        "planned_date": "2025-11-12",
        "ahead_by_days": 2,
        "quality_score": 0.88,
        "visual_indicator": "✅"
      },
      {
        "milestone_id": "m2",
        "name": "Business Impact Analysis (BIA)",
        "status": "completed",
        "completion_date": "2025-12-20",
        "planned_date": "2025-12-13",
        "delay_days": 7,
        "quality_score": 0.95,
        "visual_indicator": "✅"
      },
      {
        "milestone_id": "m3",
        "name": "Risk Assessment",
        "status": "completed",
        "completion_date": "2026-02-12",
        "planned_date": "2026-02-15",
        "ahead_by_days": 3,
        "quality_score": 0.91,
        "visual_indicator": "✅"
      },
      {
        "milestone_id": "m4",
        "name": "BC Strategy & Plans Development",
        "status": "in_progress",
        "progress_percentage": 65,
        "planned_completion_date": "2025-03-10",
        "current_date": "2025-03-19",
        "overdue_days": 9,
        "risk_level": "critical",
        "visual_indicator": "🔴",
        "issue": "BCM Manager medical leave - recovery plan active"
      },
      {
        "milestone_id": "m5",
        "name": "Training & Awareness",
        "status": "pending",
        "planned_start_date": "2025-02-25",
        "planned_completion_date": "2025-04-15",
        "blocked_by": ["m4"],
        "visual_indicator": "⏸️"
      },
      {
        "milestone_id": "m6",
        "name": "Testing & Exercises",
        "status": "pending",
        "planned_start_date": "2025-03-10",
        "planned_completion_date": "2025-05-15",
        "blocked_by": ["m4"],
        "visual_indicator": "⏸️"
      },
      {
        "milestone_id": "m7",
        "name": "Documentation & Evidence Collection",
        "status": "pending",
        "planned_start_date": "2025-03-17",
        "planned_completion_date": "2025-05-22",
        "visual_indicator": "⏳"
      },
      {
        "milestone_id": "m8",
        "name": "Internal Audit & Management Review",
        "status": "pending",
        "planned_start_date": "2025-05-12",
        "planned_completion_date": "2025-06-09",
        "visual_indicator": "⏳"
      },
      {
        "milestone_id": "m9",
        "name": "Certification Audit Preparation",
        "status": "pending",
        "planned_start_date": "2025-05-30",
        "planned_completion_date": "2025-06-27",
        "visual_indicator": "⏳"
      },
      {
        "milestone_id": "m10",
        "name": "Certification Audit (Stage 1 & 2)",
        "status": "pending",
        "planned_start_date": "2025-06-20",
        "planned_completion_date": "2026-05-25",
        "visual_indicator": "🎯"
      }
    ]
  },
  "tasks": {
    "total": 245,
    "completed": 122,
    "in_progress": 15,
    "pending": 103,
    "overdue": 5,
    "completion_percentage": 49.8,
    "tasks_this_week": [
      {
        "task_id": "t_087",
        "title": "Notify Executive Sponsor of at-risk status",
        "priority": "critical",
        "due_date": "2025-03-19",
        "status": "completed",
        "assigned_to": "Planning Service (automated)"
      },
      {
        "task_id": "t_088",
        "title": "Contact John Smith (IT Manager) for backup role",
        "priority": "critical",
        "due_date": "2025-03-20",
        "status": "in_progress",
        "assigned_to": "Executive Sponsor"
      },
      {
        "task_id": "t_089",
        "title": "Schedule knowledge transfer with BCM Manager",
        "priority": "critical",
        "due_date": "2025-03-21",
        "status": "pending",
        "assigned_to": "Executive Sponsor"
      }
    ],
    "overdue_tasks": [
      {
        "task_id": "t_072",
        "title": "BC Plan: Emergency Department - Draft",
        "due_date": "2025-03-05",
        "days_overdue": 14,
        "assigned_to": "BCM Manager",
        "note": "On hold - recovery plan addresses"
      },
      {
        "task_id": "t_073",
        "title": "BC Plan: Surgery/OR - Draft",
        "due_date": "2025-03-08",
        "days_overdue": 11,
        "assigned_to": "BCM Manager",
        "note": "On hold - recovery plan addresses"
      }
    ]
  },
  "timeline": {
    "gantt_chart_url": "/api/planning/journey/journey_iso22301_2025_001/gantt",
    "critical_path": ["m1", "m2", "m3", "m4", "m6", "m8", "m9", "m10"],
    "current_phase": "BC Plans Development (M4)",
    "next_phase": "Training & Awareness (M5), Exercises (M6)",
    "time_buffer": {
      "original_buffer_weeks": 5,
      "consumed_buffer_weeks": 3,
      "remaining_buffer_weeks": 2,
      "buffer_status": "low"
    }
  },
  "risks": {
    "current_risk_level": "critical",
    "at_risk_since": "2025-03-19",
    "signals_triggered": 6,
    "recovery_plan_active": true,
    "recovery_plan_id": "recovery_2025_001",
    "top_risks": [
      {
        "risk": "BCM Manager medical leave",
        "impact": "high",
        "likelihood": "occurred",
        "status": "mitigating",
        "mitigation": "Recovery plan: Assign backup resource (John Smith) + AI assistance"
      },
      {
        "risk": "Milestone M4 overdue (9 days)",
        "impact": "high",
        "likelihood": "occurred",
        "status": "mitigating",
        "mitigation": "Recovery plan: Complete by Week 25 (April 8)"
      },
      {
        "risk": "Buffer consumed (3/5 weeks)",
        "impact": "medium",
        "likelihood": "high",
        "status": "monitoring",
        "mitigation": "Close monitoring, no further delays acceptable"
      }
    ]
  },
  "ai_insights": {
    "ml_prediction": {
      "predicted_completion_date": "2026-06-15",
      "confidence": 0.84,
      "delay_weeks": 3.2,
      "still_achieves_target": true,
      "insight": "After recovery, 2-week buffer remains. High confidence in achieving 2026-06-30 goal."
    },
    "collective_intelligence": {
      "your_performance_percentile": 62,
      "peer_comparison": "Performing better than 62% of similar organizations at Week 22",
      "insight": "Recovery strategy matches 5/6 successful peer cases. Expected success rate: 85%."
    },
    "recommendations": [
      {
        "priority": "critical",
        "recommendation": "Execute recovery plan immediately",
        "action": "Assign John Smith as backup BCM lead this week"
      },
      {
        "priority": "high",
        "recommendation": "Leverage AI assistance heavily",
        "action": "Use AI-generated BC plans (saves 60% effort)"
      },
      {
        "priority": "medium",
        "recommendation": "Maintain quality focus",
        "action": "BCM Manager remote final review ensures quality remains >90%"
      }
    ]
  },
  "resources": {
    "budget": {
      "total_budget": 75000,
      "spent_to_date": 22000,
      "committed": 7980,
      "remaining": 45020,
      "budget_health": "good"
    },
    "effort": {
      "total_effort_hours": 1120,
      "spent_to_date": 420,
      "remaining": 700,
      "weekly_average_planned": 23,
      "weekly_average_actual": 19,
      "effort_health": "good"
    }
  },
  "compliance": {
    "iso_clauses_completed": [
      "4.1 Understanding organization context ✅",
      "4.2 Understanding stakeholder needs ✅",
      "4.3 BCMS scope ✅",
      "5.2 Policy ✅",
      "5.3 Roles & responsibilities ✅",
      "8.2.2 Business Impact Analysis ✅",
      "8.2.3 Risk Assessment ✅"
    ],
    "iso_clauses_in_progress": [
      "8.3 BC Strategy (65%)",
      "8.4 BC Plans (65%)"
    ],
    "iso_clauses_pending": [
      "7.2 Competence",
      "7.3 Awareness",
      "8.5 Exercise and testing",
      "9.2 Internal audit",
      "9.3 Management review"
    ],
    "overall_compliance": 47
  },
  "team": {
    "bcm_manager": {
      "name": "Sarah Johnson",
      "status": "medical_leave",
      "expected_return": "2025-04-09",
      "remote_availability": "limited (reviews only)"
    },
    "backup_lead": {
      "name": "John Smith",
      "role": "IT Manager (temp BCM lead)",
      "start_date": "2025-03-22",
      "availability": "20 hours/week"
    },
    "executive_sponsor": {
      "name": "CEO",
      "engagement_level": "high",
      "last_update": "2025-03-19"
    },
    "team_engagement_score": 0.54
  },
  "recent_activity": [
    {
      "date": "2025-03-19",
      "activity": "At-risk detected (critical level)",
      "user": "System"
    },
    {
      "date": "2025-03-19",
      "activity": "Recovery plan generated (assign_backup_resource_ai)",
      "user": "Planning Service"
    },
    {
      "date": "2025-03-19",
      "activity": "Executive Sponsor notified",
      "user": "Notification Service"
    },
    {
      "date": "2025-02-12",
      "activity": "Milestone M3 (Risk Assessment) completed",
      "user": "Sarah Johnson"
    },
    {
      "date": "2025-12-20",
      "activity": "Milestone M2 (BIA) completed",
      "user": "Sarah Johnson"
    }
  ],
  "dashboard_widgets": [
    {
      "widget_type": "completion_gauge",
      "title": "Overall Progress",
      "value": 48.2,
      "target": 100,
      "color": "orange"
    },
    {
      "widget_type": "milestone_status",
      "title": "Milestones",
      "completed": 3,
      "total": 10,
      "overdue": 1
    },
    {
      "widget_type": "risk_indicator",
      "title": "Risk Level",
      "value": "CRITICAL",
      "color": "red",
      "action_required": true
    },
    {
      "widget_type": "timeline_chart",
      "title": "Timeline vs Actual",
      "status": "behind_schedule"
    },
    {
      "widget_type": "budget_gauge",
      "title": "Budget",
      "spent": 22000,
      "total": 75000,
      "health": "good"
    },
    {
      "widget_type": "compliance_chart",
      "title": "ISO 22301 Compliance",
      "percentage": 47,
      "clauses_complete": 7,
      "clauses_total": 15
    }
  ],
  "actions": {
    "available_actions": [
      {
        "action": "View Recovery Plan",
        "url": "/api/planning/journey/journey_iso22301_2025_001/recovery/recovery_2025_001"
      },
      {
        "action": "View Gantt Chart",
        "url": "/api/planning/journey/journey_iso22301_2025_001/gantt"
      },
      {
        "action": "Download Progress Report (PDF)",
        "url": "/api/planning/journey/journey_iso22301_2025_001/report/pdf"
      },
      {
        "action": "View Detailed Tasks",
        "url": "/api/planning/journey/journey_iso22301_2025_001/tasks"
      },
      {
        "action": "Message Team",
        "url": "/api/planning/journey/journey_iso22301_2025_001/message"
      }
    ]
  }
}
```

**Dashboard Features**:

1. **Real-Time Updates**: WebSocket connection for live progress
2. **Visual Charts**: Progress line chart, Gantt chart, milestone timeline
3. **Risk Alerts**: Prominent display of at-risk status + recovery plan
4. **AI Insights**: ML predictions, peer comparisons, recommendations
5. **Task Management**: This week's tasks, overdue tasks, quick actions
6. **Resource Tracking**: Budget, effort, team availability
7. **Compliance View**: ISO clause completion status
8. **Mobile Responsive**: Works on desktop, tablet, mobile

**Events Published**:
```yaml
- event: journey.dashboard.viewed
  payload:
    journey_id: journey_iso22301_2025_001
    user: sarah.johnson@hospital.com
    timestamp: 2025-03-19T14:30:00Z
  subscribers:
    - analytics-service (track dashboard usage)
```

**Components Used**:
- Planning Service (data provider)
- Dashboard Service (visualization)
- Analytics Engine (charts, metrics)
- AI Foundation (insights)
- WebSocket (real-time updates)

**Success Criteria**:
- ✅ Dashboard loads <2 seconds
- ✅ Real-time updates (<5s latency)
- ✅ All key metrics visible
- ✅ Mobile responsive
- ✅ Export to PDF available

---

### 3.7 Create BC Plan from Template

**Business Context**: After BIA and Risk Assessment completed, organization needs to develop Business Continuity Plans. System provides intelligent templates that auto-fill with BIA/RA data and adapt to industry/organization type.

**Inputs**:
```json
{
  "tenant_id": "org_healthcare_001",
  "plan_type": "departmental_bc_plan",
  "department": "Emergency Department",
  "bia_id": "bia_2025_001",
  "risk_assessment_id": "ra_2025_001",
  "template_preferences": {
    "industry": "healthcare",
    "standard": "iso_22301",
    "include_who_guidelines": true,
    "detail_level": "comprehensive",
    "language": "english"
  },
  "auto_fill": true,
  "ai_assistance_level": "high"
}
```

**API Endpoint**: `POST /api/planning/bc-plan/create-from-template`

**BC Plan Creation Process**:
```
1. Template Selection (AI-Powered)
   ├─ Query RAG: "healthcare emergency department BC plan ISO 22301 WHO"
   ├─ Collections: [bcm_business_flows, WHO_healthcare_flows, ISO_templates]
   ├─ Found: 8 templates (ranked by relevance)
   └─ Selected: "Healthcare Departmental BC Plan (ISO 22301 + WHO Emergency Guidelines)"

2. Data Extraction (from BIA & RA)
   ├─ BIA Data:
   │  ├─ Emergency Department processes (15 identified)
   │  ├─ RTOs: 0-4 hours (critical), 4-24 hours (high)
   │  ├─ Dependencies: 45 mapped (IT systems, supplies, staff, facilities)
   │  └─ Impact analysis: Patient safety, regulatory compliance, revenue
   ├─ Risk Assessment Data:
   │  ├─ ED-related risks (12 identified)
   │  ├─ Top risks: Pandemic, power outage, cyber attack, natural disaster
   │  └─ Treatment plans: 8 applicable to ED
   └─ Organization Data: Policies, contacts, locations

3. AI-Powered Auto-Fill (Claude Sonnet)
   ├─ Input: Template + BIA data + RA data + Organization data
   ├─ Generate: Customized BC plan (auto-fill 70% of content)
   ├─ Smart Sections:
   │  ├─ Executive Summary (AI-generated)
   │  ├─ Critical Processes (from BIA)
   │  ├─ Recovery Strategies (from RA + WHO guidelines)
   │  ├─ Roles & Responsibilities (from org chart)
   │  ├─ Communication Plan (from stakeholder list)
   │  └─ Resources (from BIA dependencies)
   └─ Quality: 85% complete, 15% requires human input

4. Template Customization
   ├─ Healthcare-Specific: WHO emergency response protocols
   ├─ Regulatory: HIPAA, EMTALA compliance sections
   ├─ Local: Hospital-specific procedures, local emergency services
   └─ ISO 22301: Clause 8.4 compliance checkpoints

5. Quality Check (AI)
   ├─ Completeness: 85% (15 sections need human input)
   ├─ Compliance: ISO 8.4 requirements 95% met
   ├─ WHO Guidelines: Emergency care continuity 100% addressed
   └─ Recommendations: Add specific equipment lists, update phone tree
```

**Response**:
```json
{
  "plan_id": "bc_plan_ed_001",
  "plan_type": "departmental_bc_plan",
  "department": "Emergency Department",
  "status": "draft",
  "created_date": "2025-03-20",
  "template_used": {
    "template_id": "tpl_healthcare_dept_bc_iso_who",
    "template_name": "Healthcare Departmental BC Plan (ISO 22301 + WHO)",
    "template_version": "2.1",
    "template_source": "ISO + WHO Knowledge Base"
  },
  "auto_fill_summary": {
    "total_sections": 20,
    "auto_filled_sections": 17,
    "requires_human_input": 3,
    "completion_percentage": 85,
    "ai_generated_content_percentage": 70,
    "data_sources": {
      "bia_data": "bia_2025_001 (15 ED processes)",
      "risk_assessment": "ra_2025_001 (12 ED risks)",
      "organization_data": "Org policies, contacts, locations",
      "knowledge_base": "ISO 22301 templates, WHO emergency guidelines"
    }
  },
  "plan_structure": {
    "sections": [
      {
        "section": "1. Executive Summary",
        "status": "auto_filled",
        "completion": 100,
        "content_preview": "This Business Continuity Plan ensures City General Hospital Emergency Department can continue delivering critical emergency care during disruptions. The ED treats 50,000+ patients annually with RTOs of 0-4 hours for life-saving care...",
        "ai_generated": true,
        "requires_review": true
      },
      {
        "section": "2. Plan Scope and Objectives",
        "status": "auto_filled",
        "completion": 100,
        "content": {
          "scope": "Emergency Department operations, including triage, resuscitation, trauma care, emergency procedures",
          "objectives": [
            "Maintain emergency care capacity >80% during disruptions",
            "Achieve RTO 0-4 hours for critical care",
            "Ensure patient safety and regulatory compliance",
            "Coordinate with hospital-wide BC plans"
          ]
        },
        "data_source": "BIA + Organization policies"
      },
      {
        "section": "3. Critical Processes and RTOs",
        "status": "auto_filled",
        "completion": 100,
        "content": {
          "processes": [
            {
              "process": "Patient Triage",
              "criticality": "critical",
              "rto": "0 hours (immediate)",
              "rpo": "0 hours",
              "rationale": "Life-saving decisions require immediate capability"
            },
            {
              "process": "Resuscitation Services",
              "criticality": "critical",
              "rto": "0 hours (immediate)",
              "rpo": "0 hours",
              "rationale": "Life support cannot be interrupted"
            },
            {
              "process": "Trauma Care",
              "criticality": "critical",
              "rto": "1 hour",
              "rpo": "1 hour",
              "rationale": "Critical trauma requires rapid response"
            },
            {
              "process": "Emergency Surgery Coordination",
              "criticality": "high",
              "rto": "2 hours",
              "rpo": "4 hours",
              "rationale": "Coordination with OR for emergency cases"
            },
            {
              "process": "Emergency Lab Orders",
              "criticality": "high",
              "rto": "4 hours",
              "rpo": "8 hours",
              "rationale": "Lab results needed for treatment decisions"
            }
          ],
          "total_processes": 15
        },
        "data_source": "BIA (bia_2025_001)"
      },
      {
        "section": "4. Risk Assessment Summary",
        "status": "auto_filled",
        "completion": 100,
        "content": {
          "top_risks": [
            {
              "risk": "Pandemic / Mass Casualty",
              "likelihood": "medium",
              "impact": "critical",
              "rto_impact": "ED capacity overwhelmed, 0-hour RTO at risk",
              "mitigation": "Surge capacity plan, PPE stockpile, staff cross-training"
            },
            {
              "risk": "Power Outage",
              "likelihood": "medium",
              "impact": "high",
              "rto_impact": "Medical equipment failure, lighting, HVAC",
              "mitigation": "Generator backup (4-hour), UPS for critical equipment"
            },
            {
              "risk": "IT System Failure / Cyber Attack",
              "likelihood": "medium",
              "impact": "high",
              "rto_impact": "EMR unavailable, order entry down",
              "mitigation": "Paper-based downtime procedures, EMR backup"
            }
          ],
          "total_risks": 12
        },
        "data_source": "Risk Assessment (ra_2025_001)"
      },
      {
        "section": "5. Recovery Strategies",
        "status": "auto_filled",
        "completion": 90,
        "content": {
          "strategies": [
            {
              "strategy": "Alternate Care Site",
              "description": "Establish temporary ED in hospital lobby or parking lot tent",
              "triggers": ["Building damage", "Hazmat contamination", "Facility evacuation"],
              "resources_required": ["Portable medical equipment", "Triage tents", "Emergency lighting"],
              "estimated_setup_time": "2 hours",
              "capacity": "60% of normal ED capacity",
              "who_guideline_reference": "WHO Emergency Care Systems Framework - Alternate Sites"
            },
            {
              "strategy": "Surge Capacity Activation",
              "description": "Expand ED capacity by 200% during mass casualty or pandemic",
              "triggers": ["Pandemic", "Mass casualty event", "Natural disaster"],
              "resources_required": ["Additional staff (call-in)", "Convertible spaces (waiting room, hallways)", "Supply cache activation"],
              "estimated_activation_time": "1 hour",
              "who_guideline_reference": "WHO Pandemic Preparedness - Surge Capacity"
            },
            {
              "strategy": "Paper-Based Downtime Procedures",
              "description": "Manual charting, paper orders when EMR unavailable",
              "triggers": ["IT system failure", "Cyber attack", "Power outage >4 hours"],
              "resources_required": ["Pre-printed forms", "Manual medication administration records", "Backup patient identification system"],
              "estimated_activation_time": "15 minutes",
              "duration": "Up to 24 hours"
            }
          ],
          "total_strategies": 8
        },
        "data_source": "AI + WHO Guidelines",
        "requires_review": true,
        "review_note": "Verify alternate care site location and resources with ED Manager"
      },
      {
        "section": "6. Roles and Responsibilities",
        "status": "auto_filled",
        "completion": 95,
        "content": {
          "bc_team": [
            {
              "role": "ED BC Coordinator",
              "primary": "Dr. Michael Chen (ED Director)",
              "backup": "Sarah Williams (ED Nurse Manager)",
              "responsibilities": [
                "Activate ED BC Plan",
                "Coordinate recovery activities",
                "Liaise with Hospital Incident Commander",
                "Authorize alternate care site"
              ],
              "contact": {
                "phone": "+1-555-0101",
                "mobile": "+1-555-0102",
                "email": "michael.chen@hospital.com"
              }
            },
            {
              "role": "Triage Coordinator",
              "primary": "Sarah Williams (ED Nurse Manager)",
              "backup": "John Davis (Senior ED RN)",
              "responsibilities": [
                "Manage triage operations during disruption",
                "Implement surge capacity protocols",
                "Coordinate patient flow"
              ]
            }
          ],
          "total_roles": 12
        },
        "data_source": "Organization chart + BIA stakeholders"
      },
      {
        "section": "7. Communication Plan",
        "status": "auto_filled",
        "completion": 85,
        "content": {
          "internal_communication": {
            "ed_staff": "Overhead PA, mobile phones, WhatsApp group",
            "hospital_administration": "Incident command calls, email alerts",
            "other_departments": "Hospital-wide alert system"
          },
          "external_communication": {
            "ems_ambulance": "Direct radio/phone, EMS coordinator",
            "patients_families": "ED waiting room updates, website, patient portal",
            "media": "Hospital PR department (centralized)"
          },
          "communication_tree": "auto_generated_phone_tree.pdf"
        },
        "data_source": "Organization contacts + ISO 8.4 requirements",
        "requires_input": true,
        "missing": "Specific EMS radio frequencies, WhatsApp group invite links"
      },
      {
        "section": "8. Resource Requirements",
        "status": "auto_filled",
        "completion": 80,
        "content": {
          "critical_resources": [
            {
              "resource": "Medical Equipment",
              "items": ["Defibrillators (10)", "Ventilators (5)", "Portable monitors (15)", "Trauma carts (3)"],
              "backup_location": "Central equipment storage, Floor 2",
              "supplier": "Medical Equipment Services",
              "replacement_time": "24 hours"
            },
            {
              "resource": "Medications",
              "critical_drugs": ["Epinephrine", "Atropine", "Naloxone", "Antibiotics", "Pain management"],
              "cache_location": "ED medication room + Pharmacy backup cache",
              "supplier": "Cardinal Health",
              "emergency_reorder": "6-hour delivery contract"
            },
            {
              "resource": "Staff",
              "minimum_staff": "10 RNs, 3 MDs, 5 support staff per shift",
              "call_in_list": "ED_call_in_roster.xlsx",
              "backup_staffing_agency": "Healthcare Staffing Solutions"
            }
          ]
        },
        "data_source": "BIA dependencies + ED Manager input needed",
        "requires_input": true,
        "missing": "Specific equipment serial numbers, medication quantities, complete call-in roster"
      },
      {
        "section": "9. Activation and Escalation",
        "status": "auto_filled",
        "completion": 100,
        "content": {
          "activation_triggers": [
            "Automatic: Fire alarm, facility evacuation order, hospital-wide incident declared",
            "Manual: ED Director determines disruption will exceed 4-hour RTO"
          ],
          "escalation_levels": [
            {
              "level": 1,
              "description": "Minor disruption, ED handles internally",
              "authority": "ED Charge Nurse",
              "notification": "ED Director"
            },
            {
              "level": 2,
              "description": "Moderate disruption, requires hospital support",
              "authority": "ED Director",
              "notification": "Hospital Incident Commander, Facilities, IT"
            },
            {
              "level": 3,
              "description": "Major disruption, hospital-wide incident",
              "authority": "Hospital Incident Commander",
              "notification": "Executive team, external agencies (EMS, public health)"
            }
          ]
        },
        "data_source": "ISO 8.4 + Hospital incident response plan"
      },
      {
        "section": "10. Procedures",
        "status": "partially_filled",
        "completion": 60,
        "subsections": [
          {
            "procedure": "10.1 Alternate Care Site Setup",
            "status": "auto_filled",
            "content": "Step-by-step guide to establish temporary ED in hospital lobby...",
            "requires_review": true
          },
          {
            "procedure": "10.2 Paper Downtime Procedures",
            "status": "auto_filled",
            "content": "When EMR unavailable: 1) Use pre-printed forms, 2) Manual charting...",
            "requires_review": true
          },
          {
            "procedure": "10.3 Surge Capacity Activation",
            "status": "requires_input",
            "content": "INCOMPLETE - Needs ED Manager to define specific spaces and protocols"
          }
        ]
      },
      {
        "section": "11-20. Additional Sections",
        "status": "auto_filled / partially_filled",
        "sections": [
          "11. Dependencies and Interfaces (auto-filled from BIA)",
          "12. Testing and Exercises (template provided)",
          "13. Training Requirements (auto-filled)",
          "14. Plan Maintenance (ISO template)",
          "15. Document Control (template)",
          "16. Regulatory Compliance (HIPAA, EMTALA sections included)",
          "17. WHO Guidelines Alignment (auto-filled)",
          "18. Appendices (templates for forms, checklists)",
          "19. Contact Lists (auto-filled, needs update)",
          "20. Version History (initialized)"
        ]
      }
    ]
  },
  "compliance_check": {
    "iso_22301_clause_8_4": {
      "requirements_met": 19,
      "requirements_total": 20,
      "compliance_percentage": 95,
      "missing": ["8.4.2(e) - Specific resource quantities need human verification"]
    },
    "who_guidelines": {
      "emergency_care_continuity": "100% addressed",
      "surge_capacity": "included",
      "alternate_care_sites": "included",
      "compliance": "excellent"
    }
  },
  "quality_assessment": {
    "overall_quality": 0.85,
    "ai_confidence": 0.88,
    "completeness": 0.85,
    "ready_for_review": true,
    "estimated_human_effort_remaining": "6-8 hours",
    "ai_time_saved": "18 hours (75% effort reduction vs manual creation)"
  },
  "next_steps": [
    {
      "step": 1,
      "action": "ED Manager reviews and fills missing sections",
      "sections": ["7. Communication Plan", "8. Resource Requirements", "10.3 Surge Procedures"],
      "estimated_time": "4 hours",
      "assigned_to": "Dr. Michael Chen (ED Director)"
    },
    {
      "step": 2,
      "action": "BCM Manager quality review",
      "estimated_time": "2 hours",
      "assigned_to": "Sarah Johnson (BCM Manager)"
    },
    {
      "step": 3,
      "action": "Executive approval",
      "assigned_to": "Executive Sponsor"
    },
    {
      "step": 4,
      "action": "Publish to document repository",
      "assigned_to": "BCM Manager"
    }
  ],
  "document": {
    "format": "living_document",
    "auto_updates": "enabled",
    "update_triggers": ["bia.updated", "risk.updated", "org_structure.changed"],
    "version": "1.0 (draft)",
    "word_count": 12500,
    "pages": 45,
    "export_formats": ["PDF", "DOCX", "HTML"],
    "document_url": "/api/documents/bc_plan_ed_001"
  }
}
```

**Events Published**:
```yaml
- event: plan.draft_created
  payload:
    plan_id: bc_plan_ed_001
    plan_type: departmental_bc_plan
    department: Emergency Department
    tenant_id: org_healthcare_001
    template_used: tpl_healthcare_dept_bc_iso_who
    completion_percentage: 85
    requires_human_input: true
    ai_generated_content: 70
  subscribers:
    - planning-service (track plan in journey)
    - documents-service (store and version control)
    - notification-service (notify ED Director)
    - compliance-service (ISO 8.4 evidence)
```

**Components Used**:
- Planning Service (main)
- AI Foundation (Claude Sonnet - plan generation)
- RAG (template retrieval)
- BIA Service (data extraction)
- Risk Service (risk data)
- Documents Service (storage, living docs)
- Compliance Service (ISO 8.4 check)

**Success Criteria**:
- ✅ Plan created with 80%+ auto-fill
- ✅ ISO 22301 Clause 8.4 compliance >90%
- ✅ WHO guidelines incorporated (healthcare)
- ✅ BIA/RA data integrated seamlessly
- ✅ Clear next steps for human completion

---

## API Reference

### Journey Management

- `POST /api/planning/journey/create` - Create new ISO 22301 journey
- `GET /api/planning/journey/{journey_id}` - Get journey details
- `GET /api/planning/journey/{journey_id}/timeline-prediction` - ML timeline prediction
- `GET /api/planning/journey/{journey_id}/progress-dashboard` - Progress dashboard data
- `GET /api/planning/journey/{journey_id}/at-risk-detection` - Check at-risk status
- `POST /api/planning/journey/{journey_id}/recovery-plan/generate` - Generate recovery plan
- `POST /api/planning/journey/{journey_id}/milestone/{milestone_id}/complete` - Complete milestone

### BC Plan Management

- `POST /api/planning/bc-plan/create-from-template` - Create BC plan from template
- `GET /api/planning/bc-plan/templates` - List available templates
- `GET /api/planning/bc-plan/{plan_id}` - Get plan details
- `PUT /api/planning/bc-plan/{plan_id}` - Update plan
- `POST /api/planning/bc-plan/{plan_id}/approve` - Approve plan

---

## Event Flow Diagrams

### Journey Creation Flow
```
User Request
    ↓
Planning Service
    ↓
[Analyze current maturity]
    ↓
[Gap analysis (AI)]
    ↓
[Timeline prediction (ML)]
    ↓
[Collective Intelligence (k=5)]
    ↓
[Generate 10 milestones]
    ↓
Event: journey.created
    ↓
[Orchestrator tracks]
[Compliance monitors]
[Dashboard created]
    ↓
Response to User
```

### At-Risk Detection Flow
```
Orchestrator (continuous monitoring)
    ↓
[Check 6 signals every 24h]
    ↓
Signal triggered?
    ↓ Yes
Planning Service: at-risk detection
    ↓
[ML prediction]
[Root cause analysis (AI)]
[Collective Intelligence search]
    ↓
Event: journey.at_risk.detected
    ↓
[Generate intervention recommendations]
    ↓
[Notify Executive Sponsor]
    ↓
[Create intervention workflow]
```

---

## Part 1 of 4 - Scenarios 3.8-3.28 to be continued

**Status**: ✅ Part 1 Complete (Scenarios 3.1-3.7 - Journey Planning)

**Next Parts**:
- Part 2: Scenarios 3.8-3.15 (BC Plan Development)
- Part 3: Scenarios 3.16-3.19 (Exercise Planning)
- Part 4: Scenarios 3.20-3.28 (Strategy & Roadmap)

**Total Scenarios**: 28 across 4 categories

---

**Created**: 2025-03-20
**Last Updated**: 2025-03-20
**Version**: 1.0
