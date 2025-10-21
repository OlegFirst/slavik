# BCM Platform - Unified Workflows & Integrations

**Дата:** 2025-10-02
**Цель:** Полноценные end-to-end workflows через все 10 сервисов
**Архитектура:** Event-driven + REST API

---

## 🎯 Концепция Unified Workflows

**Не просто интеграции point-to-point, а полные бизнес-процессы!**

```
┌─────────────────────────────────────────────────────────────────────┐
│                   BCM Business Workflows                            │
│                                                                     │
│  BIA → Risk → Planning → Projects → Plans → Validation → Learning  │
│                              ↓                                      │
│                       Incidents ← Response                          │
│                              ↓                                      │
│                   Governance ← Documents                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📋 10 Ключевых Workflows

### Workflow 1: From Risk to Recovery (Full Cycle)

**Сценарий:** Обнаружен критический риск → полный цикл до validated recovery plan

**Участники:** Risk (8013) → BIA (8012) → Planning (8005) → Project Intelligence (8025) → Plans (8023) → Validation (8022) → Documents (8024)

**Шаги:**

#### 1. Risk Identification (Risk Service - 8013)
```python
# POST /api/v1/risks
{
  "id": "risk-001",
  "title": "Potential data center failure",
  "category": "infrastructure",
  "likelihood": 4,
  "impact": 5,
  "risk_score": 20,  # 4 * 5 = critical
  "requires_treatment": true
}
```

**Triggers:** Risk score > 15 → Auto-create BIA assessment

---

#### 2. BIA Assessment (BIA Service - 8012)
```python
# Webhook from Risk → BIA
POST /api/v1/webhooks/risk-detected
{
  "risk_id": "risk-001",
  "risk_score": 20,
  "affected_processes": ["data-center-ops"]
}

# BIA создает assessment
POST /api/v1/bia/processes
{
  "id": "bia-proc-001",
  "name": "Data Center Operations",
  "source_risk_id": "risk-001",
  "criticality": 5,
  "rto": 4,  # 4 hours
  "rpo": 1,  # 1 hour
  "mtpd": 24,  # 24 hours max
  "financial_impact_per_hour": 50000,
  "regulatory_requirements": ["SOC2", "ISO27001"]
}
```

**Triggers:** Criticality = 5 → Auto-create recovery strategy

---

#### 3. Recovery Strategy (Planning Service - 8005)
```python
# Webhook from BIA → Planning
POST /api/v1/webhooks/critical-process-identified
{
  "process_id": "bia-proc-001",
  "rto": 4,
  "rpo": 1,
  "criticality": 5
}

# Planning создает стратегию
POST /api/v1/strategies
{
  "id": "strategy-001",
  "name": "Data Center Failover Strategy",
  "process_id": "bia-proc-001",
  "risk_id": "risk-001",
  "strategy_type": "hot_site",
  "rto_target": 4,
  "rpo_target": 1,
  "estimated_cost": 250000,
  "implementation_steps": [
    {
      "order": 1,
      "name": "Setup secondary data center",
      "duration_days": 90,
      "required_skills": ["infrastructure", "cloud", "networking"],
      "dependencies": []
    },
    {
      "order": 2,
      "name": "Configure real-time replication",
      "duration_days": 30,
      "required_skills": ["database", "replication"],
      "dependencies": ["step-1"]
    },
    {
      "order": 3,
      "name": "Test failover procedures",
      "duration_days": 14,
      "required_skills": ["testing", "validation"],
      "dependencies": ["step-1", "step-2"]
    }
  ],
  "auto_create_project": true
}
```

**Triggers:** Strategy approved → Auto-create implementation project

---

#### 4. Project Intelligence (Project Intelligence - 8025)
```python
# Webhook from Planning → Project Intelligence
POST /api/v1/webhooks/strategy-approved
{
  "strategy_id": "strategy-001",
  "implementation_steps": [...],
  "rto_target": 4
}

# Project Intelligence создает проект
POST /api/v1/projects
{
  "id": "proj-001",
  "name": "Implement: Data Center Failover Strategy",
  "bcm_type": "recovery",
  "criticality_level": "critical",
  "source_strategy_id": "strategy-001",
  "source_risk_id": "risk-001",
  "source_process_id": "bia-proc-001",
  "recovery_objectives": {
    "rto_hours": 4,
    "rpo_hours": 1,
    "mtd_hours": 24
  },
  "tasks": [
    {
      "id": "task-001",
      "name": "Setup secondary data center",
      "priority": "urgent",
      "deadline": "2026-01-10",
      "required_skills": ["infrastructure", "cloud", "networking"],
      "complexity_score": 9
    },
    {
      "id": "task-002",
      "name": "Configure real-time replication",
      "priority": "high",
      "deadline": "2026-02-15",
      "required_skills": ["database", "replication"],
      "complexity_score": 7,
      "dependencies": ["task-001"]
    },
    {
      "id": "task-003",
      "name": "Test failover procedures",
      "priority": "high",
      "deadline": "2026-03-01",
      "required_skills": ["testing", "validation"],
      "complexity_score": 6,
      "dependencies": ["task-001", "task-002"]
    }
  ],
  "team_members": [],  # Will be populated from HR
  "auto_assign": true,
  "auto_escalate": true
}

# AI сразу анализирует и назначает
POST /api/v1/projects/proj-001/analyze
# Returns:
{
  "health_score": 100,
  "health_status": "healthy",
  "predicted_completion_date": "2026-03-05",
  "confidence": 0.75,
  "recommendations": [
    {
      "action": "assign",
      "title": "Assign infrastructure lead",
      "description": "Task-001 requires infrastructure expert",
      "priority": "high"
    }
  ]
}

# AI предлагает исполнителей
POST /api/v1/projects/proj-001/tasks/task-001/suggest-assignee
# Returns:
{
  "suggested_assignee_id": "user-john",
  "suggested_assignee_name": "John Infrastructure",
  "confidence": 0.89,
  "reasoning": "Skill match: 100%; Low workload; Excellent completion rate"
}
```

**Triggers:** Project created → Notify Planning with project_id

---

#### 5. Plan Activation (Plans Service - 8023)
```python
# После завершения проекта → создается активный план
# Webhook from Project Intelligence → Plans
POST /api/v1/webhooks/project-completed
{
  "project_id": "proj-001",
  "strategy_id": "strategy-001",
  "all_tasks_completed": true
}

# Plans создает executable plan
POST /api/v1/plans
{
  "id": "plan-001",
  "name": "Data Center Failover Plan",
  "plan_type": "recovery",
  "strategy_id": "strategy-001",
  "project_id": "proj-001",
  "process_id": "bia-proc-001",
  "status": "active",
  "activation_criteria": [
    "Data center primary site unavailable",
    "RTO threshold approaching (< 4 hours)"
  ],
  "execution_steps": [
    {
      "order": 1,
      "name": "Activate failover",
      "duration_minutes": 15,
      "responsible_role": "Infrastructure Lead",
      "procedure_document_id": "doc-001"
    },
    {
      "order": 2,
      "name": "Verify replication sync",
      "duration_minutes": 10,
      "responsible_role": "Database Admin",
      "procedure_document_id": "doc-002"
    },
    {
      "order": 3,
      "name": "Update DNS records",
      "duration_minutes": 5,
      "responsible_role": "Network Engineer",
      "procedure_document_id": "doc-003"
    },
    {
      "order": 4,
      "name": "Verify service restoration",
      "duration_minutes": 30,
      "responsible_role": "Service Manager",
      "procedure_document_id": "doc-004"
    }
  ],
  "auto_schedule_exercise": true
}
```

**Triggers:** Plan active → Auto-schedule validation exercise

---

#### 6. Exercise Planning (Validation Service - 8022)
```python
# Webhook from Plans → Validation
POST /api/v1/webhooks/plan-activated
{
  "plan_id": "plan-001",
  "plan_type": "recovery",
  "rto_target": 4
}

# Validation создает exercise
POST /api/v1/exercises
{
  "id": "exercise-001",
  "name": "Data Center Failover Exercise",
  "exercise_type": "simulation",
  "plan_id": "plan-001",
  "scheduled_date": "2026-04-15",
  "duration_hours": 4,
  "objectives": [
    "Test RTO compliance (< 4 hours)",
    "Validate failover procedures",
    "Assess team coordination",
    "Identify gaps in documentation"
  ],
  "participants": [
    {"role": "Infrastructure Lead", "user_id": "user-john"},
    {"role": "Database Admin", "user_id": "user-sarah"},
    {"role": "Network Engineer", "user_id": "user-mike"},
    {"role": "Service Manager", "user_id": "user-lisa"}
  ],
  "scenario": {
    "inject_1": {
      "time": "00:00",
      "event": "Primary data center fire alarm triggered"
    },
    "inject_2": {
      "time": "00:15",
      "event": "Confirm site evacuation required"
    },
    "inject_3": {
      "time": "01:00",
      "event": "Site confirmed offline indefinitely"
    }
  },
  "success_criteria": [
    {"metric": "failover_time", "target": "< 240 minutes"},
    {"metric": "data_loss", "target": "< 60 minutes"},
    {"metric": "service_availability", "target": "> 95%"}
  ],
  "auto_create_project": true
}

# Создается проект для планирования exercise
# → Project Intelligence (8025) создает proj-002
```

**Triggers:** Exercise scheduled → Notify participants (Learning module)

---

#### 7. Training Requirements (Learning Service - 8021)
```python
# Webhook from Validation → Learning
POST /api/v1/webhooks/exercise-scheduled
{
  "exercise_id": "exercise-001",
  "participants": [...],
  "required_skills": ["failover", "crisis_management", "technical_recovery"]
}

# Learning анализирует skill gaps
POST /api/v1/training/gap-analysis
{
  "exercise_id": "exercise-001",
  "participants": [
    {
      "user_id": "user-john",
      "current_skills": ["infrastructure", "cloud"],
      "required_skills": ["failover", "crisis_management"]
    }
  ]
}

# Returns:
{
  "gaps": [
    {
      "user_id": "user-john",
      "missing_skills": ["crisis_management"],
      "recommended_courses": [
        {
          "id": "course-101",
          "name": "Crisis Management for IT Leaders",
          "duration_hours": 8,
          "priority": "high"
        }
      ]
    }
  ],
  "auto_enroll": true
}

# Auto-enroll в курсы
POST /api/v1/enrollments
{
  "user_id": "user-john",
  "course_id": "course-101",
  "reason": "Required for exercise-001",
  "deadline": "2026-04-10"  # 5 days before exercise
}
```

**Triggers:** Training completed → Update exercise readiness

---

#### 8. Document Management (Documents Service - 8024)
```python
# Все процедуры из плана → документы
# Webhook from Plans → Documents
POST /api/v1/webhooks/plan-activated
{
  "plan_id": "plan-001",
  "procedures": [
    {"id": "proc-001", "name": "Activate failover"},
    {"id": "proc-002", "name": "Verify replication sync"}
  ]
}

# Documents создает/обновляет документацию
POST /api/v1/documents
{
  "id": "doc-001",
  "title": "Data Center Failover Procedure",
  "document_type": "procedure",
  "plan_id": "plan-001",
  "version": "1.0",
  "status": "active",
  "content": "...",
  "review_cycle_days": 180,
  "next_review_date": "2026-10-15",
  "approvers": [
    {"role": "Infrastructure Lead", "status": "approved"},
    {"role": "BCM Manager", "status": "approved"}
  ],
  "access_control": {
    "readers": ["all_staff"],
    "editors": ["bcm_team"],
    "approvers": ["bcm_manager"]
  }
}

# Все документы связываются с планом
# Доступны в Plans Service через API
```

**Triggers:** Documents approved → Plan fully documented

---

#### 9. Exercise Execution (Validation Service - 8022)
```python
# День exercise: 2026-04-15
POST /api/v1/exercises/exercise-001/start
{
  "actual_start_time": "2026-04-15T09:00:00Z"
}

# Real-time tracking
POST /api/v1/exercises/exercise-001/observations
{
  "time": "09:15",
  "observer": "facilitator-001",
  "observation": "Failover initiated successfully",
  "category": "success"
}

POST /api/v1/exercises/exercise-001/observations
{
  "time": "10:30",
  "observer": "facilitator-001",
  "observation": "DNS update delayed - procedure unclear",
  "category": "issue",
  "severity": "medium"
}

# После завершения
POST /api/v1/exercises/exercise-001/complete
{
  "actual_end_time": "2026-04-15T13:15:00Z",
  "results": {
    "failover_time": 195,  # minutes - под RTO (240)!
    "data_loss": 45,  # minutes - под RPO (60)!
    "service_availability": 97  # % - выше target (95%)!
  },
  "findings": [
    {
      "id": "finding-001",
      "type": "gap",
      "severity": "medium",
      "description": "DNS procedure step 3 unclear",
      "recommendation": "Update doc-003 with clearer instructions",
      "assign_to": "doc_team"
    }
  ],
  "overall_rating": "success"
}
```

**Triggers:** Exercise complete → Create CAPA for findings

---

#### 10. Continuous Improvement (Validation CAPA)
```python
# CAPA для finding-001
POST /api/v1/capa
{
  "id": "capa-001",
  "source_exercise_id": "exercise-001",
  "source_finding_id": "finding-001",
  "corrective_action": "Update DNS failover procedure",
  "preventive_action": "Add procedure review checklist",
  "responsible": "doc_team",
  "due_date": "2026-05-01",
  "auto_create_project": true
}

# → Project Intelligence создает improvement project
POST /api/v1/projects
{
  "id": "proj-003",
  "name": "Improve DNS Failover Documentation",
  "bcm_type": "improvement",
  "source_capa_id": "capa-001",
  "criticality_level": "medium",
  "tasks": [
    {
      "id": "task-001",
      "name": "Review DNS procedure feedback",
      "required_skills": ["technical_writing"]
    },
    {
      "id": "task-002",
      "name": "Update doc-003",
      "required_skills": ["technical_writing", "networking"]
    },
    {
      "id": "task-003",
      "name": "Review with SMEs",
      "required_skills": ["validation"]
    },
    {
      "id": "task-004",
      "name": "Publish updated procedure",
      "required_skills": ["document_control"]
    }
  ]
}
```

**Triggers:** CAPA completed → Update Documents → Notify Plans

---

### 🔄 Full Cycle Complete!

```
Risk (critical)
  → BIA (RTO/RPO defined)
    → Planning (strategy created)
      → Project Intelligence (implementation managed)
        → Plans (executable plan ready)
          → Validation (exercise conducted)
            → Learning (skills validated)
              → CAPA (improvements identified)
                → Documents (updated)
                  → Plans (improved)
                    → Next exercise cycle...
```

---

## 🔥 Workflow 2: Real-time Incident Response (Full Stack)

**Сценарий:** Инцидент происходит → полная response chain

**Участники:** Incidents (8007) → Plans (8023) → Project Intelligence (8025) → Documents (8024) → Validation (CAPA) → Risk (update)

### 1. Incident Detection (Response Service - 8007)
```python
# POST /api/v1/incidents
{
  "id": "inc-001",
  "title": "Data center primary site fire",
  "severity": "critical",
  "detected_at": "2026-06-20T14:30:00Z",
  "affected_systems": ["data_center_primary"],
  "affected_processes": ["bia-proc-001"],
  "auto_activate_plan": true
}

# Response Service → Plans Service
POST /api/v1/webhooks/incident-critical
{
  "incident_id": "inc-001",
  "affected_processes": ["bia-proc-001"]
}
```

### 2. Plan Activation (Plans Service - 8023)
```python
# Plans автоматически находит plan-001 для bia-proc-001
POST /api/v1/plans/plan-001/activate
{
  "incident_id": "inc-001",
  "activation_reason": "Critical incident: Data center fire",
  "activated_by": "system_auto",
  "activated_at": "2026-06-20T14:32:00Z"
}

# Создается execution instance
POST /api/v1/plan-executions
{
  "id": "execution-001",
  "plan_id": "plan-001",
  "incident_id": "inc-001",
  "status": "in_progress",
  "steps": [
    {
      "step_id": "step-001",
      "name": "Activate failover",
      "status": "pending",
      "assigned_to": "user-john",
      "eta": "2026-06-20T14:47:00Z"  # +15 min
    },
    # ... other steps
  ]
}

# → Project Intelligence для tracking
POST /api/v1/projects
{
  "id": "proj-inc-001",
  "name": "Incident Response: Data center fire",
  "bcm_type": "incident",
  "criticality_level": "critical",
  "source_incident_id": "inc-001",
  "tasks": [...execution steps as tasks...],
  "auto_assign": true
}
```

### 3. Real-time Execution Tracking
```python
# WebSocket connection for real-time updates
ws://localhost:8007/ws/incidents/inc-001

# Updates stream:
{
  "time": "14:35",
  "event": "step_started",
  "step": "Activate failover",
  "user": "user-john"
}

{
  "time": "14:45",
  "event": "step_completed",
  "step": "Activate failover",
  "duration_minutes": 10,
  "status": "success"
}

# Project Intelligence monitors health
GET /api/v1/projects/proj-inc-001/health
# Returns:
{
  "health_score": 85,
  "health_status": "warning",  # Some steps delayed
  "overdue_tasks": 1,
  "recommendations": [
    {
      "priority": "urgent",
      "action": "escalate",
      "description": "Step 3 (DNS update) delayed by 10 minutes"
    }
  ]
}

# Auto-escalation triggers
POST /api/v1/incidents/inc-001/escalate
{
  "reason": "RTO at risk - DNS step delayed",
  "escalate_to": "bcm_manager"
}
```

### 4. Incident Resolution
```python
# All steps completed
POST /api/v1/incidents/inc-001/resolve
{
  "resolved_at": "2026-06-20T17:45:00Z",
  "total_duration_minutes": 195,  # 3h 15min
  "rto_compliance": true,  # < 4 hours target!
  "data_loss_minutes": 30,  # < 1 hour RPO target!
  "lessons_learned": [
    "DNS step delayed due to unclear procedure",
    "Team coordination excellent",
    "Failover worked as expected"
  ]
}

# → Validation Service для post-incident review
POST /api/v1/post-incident-reviews
{
  "incident_id": "inc-001",
  "review_type": "hot_wash",
  "scheduled_date": "2026-06-21T10:00:00Z",
  "participants": [...incident response team...],
  "agenda": [
    "What went well?",
    "What needs improvement?",
    "Action items"
  ]
}

# → Risk Service для risk update
POST /api/v1/risks/risk-001/update
{
  "materialized": true,
  "materialized_incident_id": "inc-001",
  "actual_impact": 8,  # Was predicted 5
  "actual_likelihood": 1,  # Happened once
  "treatment_effectiveness": "high",  # Plan worked!
  "residual_risk_score": 5  # Lower after successful recovery
}
```

---

## 🎓 Workflow 3: Compliance & Governance (Continuous)

**Сценарий:** Audit cycle → compliance tracking → improvements

**Участники:** Governance (8020) → Documents (8024) → Validation (8022) → Project Intelligence (8025)

### 1. Audit Planning (Governance/Validation)
```python
POST /api/v1/audits
{
  "id": "audit-001",
  "audit_type": "internal",
  "standard": "ISO22301",
  "scope": "full_bcm_system",
  "scheduled_date": "2026-09-01",
  "auditor": "auditor-external",
  "checklist_items": 150,  # ISO 22301 requirements
  "auto_create_project": true
}

# → Project Intelligence
POST /api/v1/projects
{
  "id": "proj-audit-001",
  "name": "ISO 22301 Internal Audit Preparation",
  "bcm_type": "audit",
  "tasks": [
    {"name": "Review all BCM documentation"},
    {"name": "Update policies and procedures"},
    {"name": "Prepare evidence files"},
    {"name": "Schedule audit interviews"}
  ]
}
```

### 2. Audit Execution & Findings
```python
POST /api/v1/audits/audit-001/findings
{
  "findings": [
    {
      "id": "finding-001",
      "clause": "8.4.2",
      "requirement": "Exercise and testing",
      "finding_type": "minor_nc",
      "description": "Exercise frequency below standard (1/year vs required 2/year)",
      "evidence": "exercise-log-2025-2026.pdf",
      "recommendation": "Increase exercise frequency"
    },
    {
      "id": "finding-002",
      "clause": "7.5",
      "requirement": "Documented information",
      "finding_type": "observation",
      "description": "Some procedures lack review dates",
      "recommendation": "Implement document review schedule"
    }
  ]
}

# → Validation CAPA
POST /api/v1/capa
{
  "source_audit_id": "audit-001",
  "source_finding_id": "finding-001",
  "corrective_action": "Schedule 2 exercises per year",
  "root_cause": "Lack of exercise planning workflow",
  "preventive_action": "Implement auto-scheduling after plan activation"
}

# → Documents update
POST /api/v1/documents/batch-update
{
  "action": "add_review_schedule",
  "document_ids": [...],
  "review_frequency_days": 180
}
```

---

## 🔗 Event-Driven Architecture

### Event Bus Design

```python
# Central Event Bus (можно RabbitMQ/Kafka, но начнём с webhooks)

class EventBus:
    """Центральная шина событий для всех модулей"""

    EVENTS = {
        # Risk events
        "risk.created": ["bia", "planning"],
        "risk.critical": ["bia", "planning", "governance"],
        "risk.materialized": ["incidents", "validation"],

        # BIA events
        "bia.process.critical": ["planning", "risk"],
        "bia.rto_exceeded": ["incidents", "validation"],

        # Planning events
        "strategy.approved": ["project_intelligence", "plans"],
        "strategy.rejected": ["risk", "governance"],

        # Project events
        "project.created": ["planning", "learning"],
        "project.health.critical": ["governance", "planning"],
        "project.completed": ["plans", "documents", "validation"],

        # Plans events
        "plan.activated": ["incidents", "project_intelligence"],
        "plan.execution.started": ["documents", "learning"],
        "plan.execution.completed": ["validation", "risk"],

        # Incidents events
        "incident.critical": ["plans", "governance", "risk"],
        "incident.resolved": ["validation", "risk", "learning"],

        # Validation events
        "exercise.scheduled": ["learning", "project_intelligence"],
        "exercise.completed": ["plans", "documents", "learning"],
        "capa.created": ["project_intelligence", "documents"],

        # Learning events
        "training.completed": ["validation", "project_intelligence"],
        "skill_gap.identified": ["learning", "governance"],

        # Documents events
        "document.approved": ["plans", "governance"],
        "document.expired": ["governance", "validation"],

        # Governance events
        "audit.scheduled": ["validation", "project_intelligence"],
        "policy.updated": ["all_modules"],
    }

    @staticmethod
    async def publish(event_type: str, payload: dict):
        """Publish event to subscribers"""
        subscribers = EventBus.EVENTS.get(event_type, [])

        for subscriber in subscribers:
            webhook_url = SERVICE_URLS[subscriber] + f"/api/v1/webhooks/{event_type}"

            async with AsyncClient() as client:
                try:
                    await client.post(webhook_url, json=payload, timeout=5.0)
                except Exception as e:
                    logger.error(f"Failed to notify {subscriber}: {e}")

# Usage in any service:
await EventBus.publish("risk.critical", {
    "risk_id": "risk-001",
    "risk_score": 20,
    "affected_processes": ["proc-001"]
})
```

### Webhook Handlers (в каждом сервисе)

```python
# В каждом модуле (например, Planning Service):

@app.post("/api/v1/webhooks/risk.critical")
async def handle_critical_risk(payload: dict):
    """Handle critical risk event"""
    risk_id = payload["risk_id"]
    affected_processes = payload["affected_processes"]

    # Auto-create strategies for affected processes
    for process_id in affected_processes:
        # Get process details from BIA
        process = await bia_service.get_process(process_id)

        # Create strategy
        strategy = await create_strategy_from_risk(risk_id, process)

        # Publish event
        await EventBus.publish("strategy.approved", {
            "strategy_id": strategy.id,
            "risk_id": risk_id
        })

    return {"status": "processed"}


@app.post("/api/v1/webhooks/project.completed")
async def handle_project_completed(payload: dict):
    """Handle project completion"""
    project_id = payload["project_id"]
    strategy_id = payload.get("strategy_id")

    if strategy_id:
        # Update strategy status
        await update_strategy_status(strategy_id, "implemented")

        # Create executable plan
        plan = await create_plan_from_strategy(strategy_id, project_id)

        # Publish event
        await EventBus.publish("plan.activated", {
            "plan_id": plan.id,
            "strategy_id": strategy_id
        })

    return {"status": "processed"}
```

---

## 📊 Service Integration Matrix

| From ↓ / To → | BIA | Risk | Planning | Projects | Plans | Incidents | Validation | Learning | Documents | Governance |
|---------------|-----|------|----------|----------|-------|-----------|------------|----------|-----------|------------|
| **BIA** | - | ✅ Update risk | ✅ Create strategy | - | - | ✅ Notify critical | - | - | - | ✅ Report |
| **Risk** | ✅ Assess process | - | ✅ Create strategy | - | - | ✅ Materialized | - | - | - | ✅ Report |
| **Planning** | - | ✅ Link risk | - | ✅ Create project | ✅ Create plan | - | - | - | ✅ Create docs | - |
| **Projects** | - | - | ✅ Update status | - | ✅ Complete → plan | - | ✅ Schedule exercise | ✅ Skill gaps | ✅ Update docs | - |
| **Plans** | - | - | - | ✅ Track execution | - | ✅ Activate on incident | ✅ Schedule exercise | ✅ Required skills | ✅ Link procedures | - |
| **Incidents** | ✅ Update criticality | ✅ Update risk | - | ✅ Create response project | ✅ Activate plan | - | ✅ Post-incident review | - | ✅ Incident report | ✅ Notify |
| **Validation** | ✅ Exercise results | ✅ Update risk | ✅ Strategy feedback | ✅ Create improvement project | ✅ Update plan | - | - | ✅ Training required | ✅ CAPA docs | ✅ Audit findings |
| **Learning** | - | - | - | ✅ Update team skills | - | - | ✅ Exercise readiness | - | ✅ Training materials | - |
| **Documents** | - | - | ✅ Procedures available | - | ✅ Link to plan | ✅ Response procedures | ✅ Audit evidence | ✅ Training content | - | ✅ Policy docs |
| **Governance** | ✅ Context updates | ✅ Risk appetite | ✅ Policy constraints | - | - | ✅ Escalation | ✅ Compliance requirements | - | ✅ Approvals | - |

---

## 🚀 Implementation Roadmap

### Phase 1: Core Workflows (Weeks 1-4)
- [ ] Implement Event Bus (webhook-based)
- [ ] Workflow 1: Risk → BIA → Planning → Projects
- [ ] Workflow 2: Incidents → Plans → Projects
- [ ] Testing end-to-end

### Phase 2: Extended Workflows (Weeks 5-8)
- [ ] Workflow 3: Projects → Plans → Validation
- [ ] Workflow 4: Validation → CAPA → Improvement
- [ ] Learning integration (skill gaps)
- [ ] Documents integration (procedures)

### Phase 3: Governance & Compliance (Weeks 9-12)
- [ ] Governance workflows
- [ ] Audit workflows
- [ ] Compliance tracking
- [ ] Full cycle testing

### Phase 4: Optimization (Weeks 13-16)
- [ ] Performance tuning
- [ ] Advanced AI integration
- [ ] Real-time dashboards
- [ ] Analytics & reporting

---

## 📋 API Contracts

### Standard Webhook Payload
```typescript
interface WebhookPayload {
  event_type: string;
  timestamp: string;
  source_service: string;
  source_module: string;
  data: {
    entity_type: string;
    entity_id: string;
    action: string;
    metadata: Record<string, any>;
  };
  correlation_id?: string;  // For tracing full workflow
}
```

### Standard Response
```typescript
interface WebhookResponse {
  status: "processed" | "failed" | "deferred";
  message?: string;
  actions_taken?: string[];
  error?: string;
}
```

---

## 🎯 Success Metrics

### Workflow Efficiency
- **End-to-end time**: Risk → Validated Plan < 180 days
- **Automation rate**: 70%+ of workflows automated
- **Manual interventions**: < 5 per workflow

### Integration Health
- **Webhook success rate**: > 99%
- **Event processing time**: < 1 second average
- **Failed events**: < 0.1%

### Business Impact
- **RTO compliance**: 95%+ incidents meet RTO
- **Exercise frequency**: 2+ per plan per year
- **CAPA closure rate**: 90%+ within deadline
- **Audit findings**: < 3 major non-conformities

---

**Status:** 🟢 Ready to implement
**Next Step:** Start with Phase 1 - Core Workflows
**Priority:** Workflow 1 (Risk → Recovery) - highest business value
