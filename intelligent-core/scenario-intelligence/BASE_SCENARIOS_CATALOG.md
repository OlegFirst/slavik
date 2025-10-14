# Base Scenarios Catalog

**Created:** 2025-10-12
**Total Scenarios:** 14
**Status:** ✅ Complete

## Summary

Создана библиотека из 14 базовых сценариев, охватывающих все 4 уровня архитектуры:
- **Level 1 (Module):** 6 сценариев
- **Level 2 (Subsystem):** 3 сценария
- **Level 3 (Inter-system):** 2 сценария
- **Level 4 (User):** 3 сценария (включая существующий BIA workflow)

---

## Level 1: Module Scenarios (6)

Тестирование отдельных микросервисов и компонентов.

### 1. BIA Service - Create BIA
**File:** `level1-modules/bia-service/functional/create-bia.v1.0.0.yaml`
**ID:** `bia-service-create-bia`
**Domain:** Business Continuity
**Purpose:** Создание Business Impact Analysis с оценкой воздействия

**Key Features:**
- Валидация permissions и организации
- Создание BIA с RTO/RPO
- Публикация события `bia.created`
- ISO 22301 compliance (clause 8.2.2)
- Audit logging

---

### 2. Risk Service - Create Risk Assessment
**File:** `level1-modules/risk-service/functional/create-risk-assessment.v1.0.0.yaml`
**ID:** `risk-service-create-risk-assessment`
**Domain:** Risk Management
**Purpose:** Создание оценки риска с расчетом likelihood × impact

**Key Features:**
- Автоматический расчет risk score
- Валидация likelihood (1-5) и impact (1-5)
- Event subscription на `bia.created` для автоанализа
- ISO 22301 compliance (clauses 8.2.2, 8.2.3)
- Mitigation strategy документирование

---

### 3. Document Service - Store Document
**File:** `level1-modules/document-service/functional/store-document.v1.0.0.yaml`
**ID:** `document-service-store-document`
**Domain:** Document Management
**Purpose:** Хранение документов (BCM план, SOP, policy) с version control

**Key Features:**
- Virus scanning перед сохранением
- Object storage integration
- Metadata management
- Version control (1.0.0)
- ISO 22301 compliance (clauses 7.5.3, 8.4.1)

---

### 4. Audit Service - Create Audit Log
**File:** `level1-modules/audit-service/functional/create-audit-log.v1.0.0.yaml`
**ID:** `audit-service-create-audit-log`
**Domain:** Audit Logging
**Purpose:** Создание immutable audit log с cryptographic hash

**Key Features:**
- SHA-256 integrity hash
- Immutable storage
- Event subscriptions (bia.created, risk.identified, document.stored)
- High retry policy (5 retries)
- ISO 22301 compliance (clauses 7.5.3, 9.1.1)

---

### 5. Compliance Engine - Check Compliance
**File:** `level1-modules/compliance-engine/functional/check-compliance.v1.0.0.yaml`
**ID:** `compliance-engine-check-compliance`
**Domain:** Compliance Management
**Purpose:** Проверка ISO 22301 compliance для организации

**Key Features:**
- Multi-clause validation (4.1, 6.1, 8.2, 8.4)
- Compliance score calculation (0-100)
- Gap identification
- Recommendations generation
- Event на `compliance.gap.identified` если score < 80

---

### 6. Plans Service - Create BCM Plan
**File:** `level1-modules/plans-service/functional/create-bcm-plan.v1.0.0.yaml`
**ID:** `plans-service-create-bcm-plan`
**Domain:** Business Continuity Planning
**Purpose:** Создание BCM плана с recovery strategies

**Key Features:**
- Linkage to BIA
- RTO/RPO target definition
- Recovery procedures documentation
- Event subscription на `bia.created` для auto-suggest
- ISO 22301 compliance (clauses 8.4, 8.4.1, 8.4.2)

---

## Level 2: Subsystem Scenarios (3)

Интеграционное тестирование групп модулей.

### 7. Platform Services - BCM Subsystem Health
**File:** `level2-subsystems/platform-services/integration/bcm-subsystem-health.v1.0.0.yaml`
**ID:** `platform-services-bcm-subsystem-health`
**Domain:** Subsystem Health
**Purpose:** Проверка здоровья всех BCM сервисов

**Modules Tested:**
- BIA Service
- Risk Service
- Plans Service
- Document Service

**Key Features:**
- Health check всех сервисов
- Database connection verification
- EventBus connectivity test
- Cross-service integration test
- SLA: 99.9% availability

---

### 8. AI Office - Agent Coordination
**File:** `level2-subsystems/ai-office/integration/ai-office-coordination.v1.0.0.yaml`
**ID:** `ai-office-coordination`
**Domain:** AI Orchestration
**Purpose:** Тестирование координации между AI агентами

**Agents Tested:**
- AI Orchestrator
- Agent Router
- Analytics Specialist
- MIO Manager
- AI Event Manager

**Key Features:**
- Task submission and routing
- Agent-to-agent coordination
- MIO monitoring verification
- EventBus event tracking
- SLA: 5s response time, 95% success rate

---

### 9. Security Subsystem - Integration Test
**File:** `level2-subsystems/security/integration/security-subsystem-test.v1.0.0.yaml`
**ID:** `security-subsystem-test`
**Domain:** Security Integration
**Purpose:** E2E security flow: auth → secrets → audit

**Modules Tested:**
- Auth Service
- Vault
- Secrets Manager
- Audit Service

**Key Features:**
- Full authentication flow
- Secret store/retrieve with authorization
- Unauthorized access testing
- Audit log verification
- SLA: 99.99% availability (security critical)

---

## Level 3: Inter-System Scenarios (2)

Взаимодействие между подсистемами.

### 10. AI-Assisted BIA Creation
**File:** `level3-intersystem/ai-platform-integration/ai-assisted-bia.v1.0.0.yaml`
**ID:** `ai-assisted-bia-workflow`
**Domain:** AI-Platform Integration
**Purpose:** AI Office помогает Platform Services создавать BIA

**Systems Involved:**
- AI Office Infrastructure
- Platform Services

**Workflow:**
1. User creates BIA draft (Platform)
2. System triggers AI analysis (AI Office)
3. AI provides RTO/RPO recommendations
4. Platform updates BIA with AI suggestions
5. Cross-system audit trail

**Key Features:**
- Calls Level 2 scenarios (ai-office-coordination, bcm-subsystem-health)
- Calls Level 1 scenarios (bia-service-create-bia, audit-service-create-audit-log)
- AI confidence scoring
- SLA: 15s including AI analysis

---

### 11. Platform-Infrastructure Monitoring
**File:** `level3-intersystem/platform-infrastructure/monitoring-integration.v1.0.0.yaml`
**ID:** `platform-infrastructure-monitoring`
**Domain:** Monitoring Integration
**Purpose:** Platform metrics → Prometheus → Alerting

**Systems Involved:**
- Platform Services
- Infrastructure Observability
- EventBus

**Key Features:**
- Prometheus scraping verification
- Service Discovery integration
- Alert rules validation
- Cross-system latency measurement
- Dashboard verification
- SLA: <30s metric lag

---

## Level 4: User Scenarios (3)

Полные E2E пользовательские workflows.

### 12. BIA Complete Workflow (Existing)
**File:** `level4-user/workflows/bia-complete-workflow.v1.0.0.yaml`
**ID:** `bia-complete-workflow`
**Domain:** User Workflow
**Purpose:** Полный BIA workflow от создания до compliance

**User Personas:**
- Business Analyst
- BCM Coordinator

**Already exists** - not recreated.

---

### 13. Complete Risk Assessment Workflow
**File:** `level4-user/workflows/complete-risk-assessment-workflow.v1.0.0.yaml`
**ID:** `complete-risk-assessment-workflow`
**Domain:** User Workflow
**Purpose:** E2E risk assessment с AI помощью

**User Personas:**
- Risk Manager
- BCM Coordinator

**Workflow Phases:**
1. **Authentication & Context** - Login, organization setup
2. **Risk Identification with AI** - AI analyzes historical risks and benchmarks
3. **Risk Assessment Creation** - Create with AI recommendations
4. **Link to BIA** - Connect risk to business process
5. **Mitigation Plan Documentation** - Create mitigation document
6. **Compliance Evidence Generation** - ISO 22301 evidence
7. **Stakeholder Notification** - Notify risk committee
8. **Workflow Completion** - Mark complete

**Key Features:**
- Calls Level 3 scenario (ai-assisted-bia-workflow)
- Calls Level 2 scenario (platform-services-bcm-subsystem-health)
- Calls Level 1 scenarios (risk-service, document-service, audit-service)
- AI confidence scoring
- User experience: 10 minutes estimated
- SLA: 98% success rate

---

### 14. Incident Response Workflow
**File:** `level4-user/workflows/incident-response-workflow.v1.0.0.yaml`
**ID:** `incident-response-workflow`
**Domain:** Incident Management
**Purpose:** E2E incident response от detection до post-incident review

**User Personas:**
- Incident Manager
- BCM Coordinator
- Crisis Team Member

**Workflow Phases:**
1. **Incident Detection & Authentication** - Report incident
2. **AI-Powered Incident Assessment** - AI assesses severity and impact
3. **Update Incident with AI Assessment** - Incorporate AI recommendations
4. **Activate BCM Plan** - Find and activate relevant plan
5. **Notify Crisis Team** - Automatic notification to crisis team
6. **Execute Response Procedures** - Create and track response tasks
7. **Document Recovery Actions** - Log recovery activities
8. **Generate Post-Incident Report** - Full incident report
9. **Compliance Evidence** - ISO 22301 clause 8.5 evidence
10. **Workflow Completion** - Mark complete

**Key Features:**
- Calls Level 3 scenario (ai-assisted-bia-workflow for AI assessment)
- Calls Level 2 scenario (ai-office-coordination)
- Calls Level 1 scenario (audit-service-create-audit-log)
- Crisis team mobilization
- BCM plan activation tracking
- User experience: 15 minutes estimated, HIGH complexity, CRITICAL urgency
- SLA: 5min detection-to-response, 60s crisis team notification, 99% success rate

---

## Integration Map

Визуализация вызовов между уровнями:

```
Level 4 (User Workflows)
│
├─→ complete-risk-assessment-workflow
│   ├─→ [Level 3] ai-assisted-bia-workflow
│   ├─→ [Level 2] platform-services-bcm-subsystem-health
│   ├─→ [Level 1] risk-service-create-risk-assessment
│   ├─→ [Level 1] document-service-store-document
│   └─→ [Level 1] audit-service-create-audit-log
│
├─→ incident-response-workflow
│   ├─→ [Level 3] ai-assisted-bia-workflow
│   ├─→ [Level 2] ai-office-coordination
│   └─→ [Level 1] audit-service-create-audit-log
│
└─→ bia-complete-workflow
    └─→ [Level 3] (future integration)

Level 3 (Inter-System)
│
├─→ ai-assisted-bia-workflow
│   ├─→ [Level 2] ai-office-coordination
│   ├─→ [Level 2] platform-services-bcm-subsystem-health
│   ├─→ [Level 1] bia-service-create-bia
│   └─→ [Level 1] audit-service-create-audit-log
│
└─→ platform-infrastructure-monitoring
    └─→ [Level 2] platform-services-bcm-subsystem-health

Level 2 (Subsystems)
│
├─→ platform-services-bcm-subsystem-health
│   ├─→ [Level 1] bia-service-create-bia
│   └─→ [Level 1] risk-service-create-risk-assessment
│
├─→ ai-office-coordination
│   └─→ (AI agents coordination)
│
└─→ security-subsystem-test
    ├─→ [Level 1] vault-store-secret-encrypted
    └─→ [Level 1] audit-service-create-audit-log

Level 1 (Modules)
│
├─→ bia-service-create-bia
├─→ risk-service-create-risk-assessment
├─→ document-service-store-document
├─→ audit-service-create-audit-log
├─→ compliance-engine-check-compliance
└─→ plans-service-create-bcm-plan
```

---

## Event Flow Map

Асинхронные события между сценариями:

```
bia.created (BIA Service)
  ├─→ triggers: risk-service auto-analyze (if financial_impact > 100k)
  ├─→ triggers: plans-service suggest-from-bia
  └─→ triggers: audit-service log creation

risk.identified (Risk Service)
  └─→ triggers: audit-service log creation

document.stored (Document Service)
  └─→ triggers: audit-service log creation

compliance.gap.identified (Compliance Engine)
  └─→ triggers: notification to compliance team (if score < 80)

vault.secret.stored (Vault)
  └─→ triggers: audit-service log creation

service.health.changed (Service Discovery)
  └─→ triggers: update-monitoring-dashboard

alert.triggered (Prometheus)
  └─→ triggers: escalate-to-on-call
```

---

## Compliance Coverage

ISO 22301 clauses покрываемые сценариями:

| Clause | Title | Scenarios |
|--------|-------|-----------|
| 4.1 | Understanding the organization | compliance-engine-check-compliance |
| 6.1 | Actions to address risks | risk-service, compliance-engine |
| 7.5.3 | Control of documented information | bia-service, risk-service, document-service, audit-service, plans-service |
| 8.2.2 | BIA and risk assessment | bia-service, risk-service, compliance-engine |
| 8.2.3 | Risk assessment | risk-service, compliance-engine |
| 8.4 | BCM plans and procedures | plans-service, compliance-engine |
| 8.4.1 | General | plans-service, document-service |
| 8.4.2 | Incident response structure | plans-service |
| 8.5 | Incident response | incident-response-workflow |
| 9.1 | Monitoring and evaluation | audit-service, compliance-engine |
| 9.1.1 | Monitoring | audit-service |

---

## Metrics Coverage

Prometheus metrics определенные в сценариях:

### BIA Service
- `bia_creation_duration_seconds` (histogram)
- `bia_created_total` (counter)
- `bia_validation_failures_total` (counter)

### Risk Service
- `risk_assessment_creation_duration_seconds` (histogram)
- `risk_assessments_total` (counter)
- `risk_score_distribution` (histogram, buckets: 1,5,10,15,20,25)

### Document Service
- `document_upload_duration_seconds` (histogram)
- `documents_stored_total` (counter)
- `document_size_bytes` (histogram)
- `virus_scan_failures_total` (counter)

### Audit Service
- `audit_log_creation_duration_seconds` (histogram)
- `audit_logs_created_total` (counter)
- `audit_log_write_failures_total` (counter)

### Compliance Engine
- `compliance_check_duration_seconds` (histogram)
- `compliance_checks_total` (counter)
- `compliance_score` (gauge)
- `compliance_gaps_total` (counter)

### Plans Service
- `bcm_plan_creation_duration_seconds` (histogram)
- `bcm_plans_created_total` (counter)
- `bcm_plan_rto_target_hours` (histogram, buckets: 1,4,8,24,72)

### Subsystems
- `subsystem_health_check_duration_seconds` (histogram)
- `subsystem_health_status` (gauge)
- `ai_coordination_duration_seconds` (histogram)
- `security_auth_success_rate` (gauge)

### Workflows
- `risk_assessment_workflow_duration_seconds` (histogram)
- `incident_response_workflow_duration_seconds` (histogram)
- `cross_system_latency_seconds` (histogram)

---

## Next Steps

### Immediate (This Week)
1. ✅ **Create base scenarios** - COMPLETED (14 scenarios)
2. 🔄 **Add API authentication** - PENDING
3. 🔄 **Implement Qdrant RAG integration** - PENDING

### Short-term (2-4 Weeks)
4. **Load scenarios to database** - Use `database_integration.py`
5. **Load scenarios to Qdrant** - Use `rag_integration.py`
6. **Test all scenarios via API** - Execute via `/scenarios/execute`
7. **Create scenario visualization dashboard** - Show scenario graph

### Medium-term (1-2 Months)
8. **Add chaos scenarios** (Level 1) - Vault outage, DB failure, Network partition
9. **Add security scenarios** (Level 1) - SQL injection, XSS, CSRF tests
10. **Add performance scenarios** (Level 2) - Load testing, stress testing
11. **Expand Level 4** - Add more user workflows (compliance audit, training completion)

### Long-term (3-6 Months)
12. **Scenario versioning** - Support multiple versions of same scenario
13. **A/B testing** - Compare scenario variants
14. **Auto-generation** - AI generates new scenarios from templates
15. **Visual editor** - UI for scenario creation/editing
16. **Distributed execution** - Execute scenarios on multiple nodes

---

## Files Summary

```
intelligent-core/scenario-intelligence/scenarios/
│
├── level1-modules/
│   ├── bia-service/functional/create-bia.v1.0.0.yaml
│   ├── risk-service/functional/create-risk-assessment.v1.0.0.yaml
│   ├── document-service/functional/store-document.v1.0.0.yaml
│   ├── audit-service/functional/create-audit-log.v1.0.0.yaml
│   ├── compliance-engine/functional/check-compliance.v1.0.0.yaml
│   ├── plans-service/functional/create-bcm-plan.v1.0.0.yaml
│   └── vault/functional/store-secret.v1.0.0.yaml (existing)
│
├── level2-subsystems/
│   ├── platform-services/integration/bcm-subsystem-health.v1.0.0.yaml
│   ├── ai-office/integration/ai-office-coordination.v1.0.0.yaml
│   └── security/integration/security-subsystem-test.v1.0.0.yaml
│
├── level3-intersystem/
│   ├── ai-platform-integration/ai-assisted-bia.v1.0.0.yaml
│   └── platform-infrastructure/monitoring-integration.v1.0.0.yaml
│
└── level4-user/
    ├── workflows/bia-complete-workflow.v1.0.0.yaml (existing)
    ├── workflows/complete-risk-assessment-workflow.v1.0.0.yaml
    └── workflows/incident-response-workflow.v1.0.0.yaml
```

**Total:** 14 scenarios (12 new + 2 existing)

---

## Testing Strategy

### Unit Testing (Level 1)
```bash
# Test individual modules
python3 -m api.api &
curl -X POST http://localhost:8090/scenarios/execute \
  -H "Content-Type: application/json" \
  -d @scenarios/level1-modules/bia-service/functional/create-bia.v1.0.0.yaml
```

### Integration Testing (Level 2)
```bash
# Test subsystems
curl -X POST http://localhost:8090/scenarios/execute \
  -H "Content-Type: application/json" \
  -d @scenarios/level2-subsystems/platform-services/integration/bcm-subsystem-health.v1.0.0.yaml
```

### Inter-System Testing (Level 3)
```bash
# Test cross-system integration
curl -X POST http://localhost:8090/scenarios/execute \
  -H "Content-Type: application/json" \
  -d @scenarios/level3-intersystem/ai-platform-integration/ai-assisted-bia.v1.0.0.yaml
```

### E2E Testing (Level 4)
```bash
# Test full user workflows
curl -X POST http://localhost:8090/scenarios/execute \
  -H "Content-Type: application/json" \
  -d @scenarios/level4-user/workflows/complete-risk-assessment-workflow.v1.0.0.yaml
```

---

## Success Criteria

✅ **14 базовых сценариев созданы**
- Level 1: 6 сценариев ✅
- Level 2: 3 сценария ✅
- Level 3: 2 сценария ✅
- Level 4: 3 сценария ✅

✅ **Все сценарии следуют единому формату**
- Metadata (id, version, level, type)
- Ownership
- Description
- Behavior (Gherkin)
- Execution (steps with retry policy)
- Integration (calls, events)
- Compliance (ISO 22301)
- Observability (metrics, logs)
- SLA targets
- Changelog

✅ **Полное покрытие критических сервисов**
- BIA Service ✅
- Risk Service ✅
- Plans Service ✅
- Document Service ✅
- Audit Service ✅
- Compliance Engine ✅

✅ **Интеграционные сценарии**
- Platform Services subsystem ✅
- AI Office subsystem ✅
- Security subsystem ✅
- AI-Platform integration ✅
- Platform-Infrastructure monitoring ✅

✅ **Пользовательские workflows**
- Risk Assessment E2E ✅
- Incident Response E2E ✅
- BIA Complete Workflow (existing) ✅

---

## Заключение

Библиотека базовых сценариев готова! 🎉

- **14 scenarios** охватывают все 4 уровня архитектуры
- **ISO 22301 compliance** интегрирован во все сценарии
- **Event-driven architecture** с pub/sub через EventBus
- **AI integration** для enhanced workflows
- **Full observability** с Prometheus metrics
- **Audit trail** через Audit Service

Сценарии готовы к:
1. Загрузке в PostgreSQL
2. Индексации в Qdrant RAG
3. Выполнению через Scenario Intelligence API
4. Интеграции с существующими сервисами

**Next:** Реализовать API authentication и Qdrant RAG integration.
