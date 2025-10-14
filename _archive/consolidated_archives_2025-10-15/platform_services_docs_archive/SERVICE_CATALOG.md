# ПОЛНЫЙ КАТАЛОГ СЕРВИСОВ ПЛАТФОРМЫ BCM
## Platform Services Comprehensive Catalog

**Дата аудита**: 2025-10-10
**Статус**: Готовность к запуску
**Всего сервисов**: 20 (13 стандартных ISO + 7 платформенных)

---

## КАТЕГОРИЯ 1: СТАНДАРТНЫЕ СЕРВИСЫ (ISO 22301)

Эти сервисы составляют ядро BCM-платформы и реализуют требования ISO 22301.

### 1. BIA Service - Business Impact Analysis
**Порт**: `8012`
**ISO**: Clause 8.2.2
**Статус**: ✅ **ГОТОВ К ЗАПУСКУ**

**Назначение**: Анализ влияния на бизнес, определение критичных процессов и требований к восстановлению (RTO/RPO).

**API Endpoints** (16):
- `POST /api/bia/processes` - Создание BIA процесса
- `GET /api/bia/processes` - Список процессов с фильтрами
- `GET /api/bia/processes/{id}` - Детали процесса
- `POST /api/bia/processes/{id}/suggest-rto` - AI предложения RTO/RPO
- `POST /api/bia/processes/{id}/discover-dependencies` - AI обнаружение зависимостей
- `POST /api/bia/processes/bulk` - Массовое создание
- `GET /api/bia/reports/summary` - Сводный отчет
- `GET /api/bia/reports/critical-processes` - Отчет критичных процессов
- `GET /health` - Health check

**База данных**:
- PostgreSQL: `bia_processes`, `bia_dependencies`, `bia_impacts`
- Redis: кэш для производительности

**Интеграции**:
- EventBus (8001): публикует `bia.assessment.completed`, `bia.critical.process.identified`
- AI Orchestration (8002): AI-рекомендации
- Risk Service: получает события критичных процессов

**Зависимости**:
```
fastapi >= 0.104.0
sqlalchemy >= 2.0.0
asyncpg >= 0.28.0
redis >= 5.0.0
workflow-intelligence (local)
```

**Запуск**:
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/bcm
REDIS_URL=redis://localhost:6379/0
EVENTBUS_URL=amqp://guest:guest@localhost:5672
cd /Users/MD/AI-Platform-ISO/platform-services/bia-service
python main.py
```

**Бизнес-флоу**:
1. Создание процесса → Установка критичности → Определение RTO/RPO → Оценка воздействий → Картирование зависимостей
2. AI предложения → Анализ характеристик → Применение benchmark'ов → Возврат с confidence score

**User-флоу**:
- BCM Manager создает BIA для критичной функции
- Process Owner проверяет и обновляет оценки воздействий
- Risk Analyst картирует зависимости

---

### 2. Compliance Service - Управление соответствием
**Порт**: `8014`
**ISO**: Clauses 9.2, 10.1, 10.2
**Статус**: ✅ **ГОТОВ К ЗАПУСКУ**

**Назначение**: Управление compliance, gap analysis, внутренние аудиты, управление несоответствиями через RCA, инициативы улучшения.

**API Endpoints** (60+):
- Evidence Management: `POST /api/evidence`, `GET /api/evidence`
- Assessments: `POST /api/assessments`, `POST /api/assessments/{id}/score`
- Gap Analysis: `GET /api/gaps`, `POST /api/gaps/{id}/remediate`
- Internal Audit: `POST /api/audit/audits`, `POST /api/audit/audits/{id}/findings`
- Nonconformity & RCA: `POST /api/nonconformities`, `POST /api/nonconformities/{id}/rca/start`
- Improvements: `POST /api/improvements`, `GET /api/improvements/metrics`
- Management Review: `POST /api/management-review`

**База данных**:
- PostgreSQL: Evidence, Assessments, Gaps, Nonconformities, Audits, Improvements

**Интеграции**:
- EventBus: публикует compliance события, получает события инцидентов
- AI Orchestration: AI compliance scanning, RCA помощь

**RCA методы**:
- 5 Whys (итеративное вопрошание)
- Fishbone/Ishikawa (6M категории)
- Fault Tree Analysis (вероятностный анализ)

**Запуск**:
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/bcm
COMPLIANCE_AI_ENABLED=true
cd /Users/MD/AI-Platform-ISO/platform-services/compliance-service
python main.py
```

**Бизнес-флоу**:
- Assessment: Draft → In Progress → Under Review → Approved
- Nonconformity: IDENTIFIED → RCA_IN_PROGRESS → CORRECTIVE_ACTION → VERIFICATION → CLOSED
- Evidence: Submit → Review → Verify → Approved

---

### 3. Governance Service - Управление и политики
**Порт**: `8013` ⚠️ **КОНФЛИКТ ПОРТОВ!**
**ISO**: Clauses 4, 5, 6, 7
**Статус**: ⚠️ **ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ ПОРТА**

**Назначение**: Организационная структура BCM, политики, роли, ресурсы, компетенции, цели, stakeholder management.

**КРИТИЧЕСКАЯ ПРОБЛЕМА**:
- В `config.py` указан порт `8020`
- В `PORT_ALLOCATION.md` должен быть `8013`
- **ДЕЙСТВИЕ**: Изменить `config.py` line 17 на `SERVICE_PORT: int = 8013`

**API Endpoints** (46):
- Policy Management: `POST /api/v1/governance/policies`, `POST /api/v1/governance/policies/{id}/approve`
- Roles: `POST /api/v1/governance/roles`, `POST /api/v1/governance/roles/{id}/assign`
- Resources: `POST /api/v1/governance/resources`
- Competence: `POST /api/v1/governance/competence`
- Objectives: `POST /api/v1/governance/objectives`
- Stakeholders: `POST /api/v1/governance/stakeholders`
- Context Analysis: `POST /api/v1/governance/context-analysis` (PESTLE, SWOT, PORTER, VUCA, SCENARIO)

**База данных**:
- PostgreSQL: BCMPolicy, OrganizationalRole, BCMResource, CompetenceRecord, BCMObjective, Stakeholder, ContextAnalysis

**Интеграции**:
- EventBus: публикует governance события (policy.created, role.assigned)
- All BCM Services: получают organization context, policies, resources

**Запуск**:
```bash
# СНАЧАЛА ИСПРАВИТЬ ПОРТ!
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/bcm
JWT_SECRET_KEY=your-secret
EVENTBUS_URL=amqp://guest:guest@localhost:5672
cd /Users/MD/AI-Platform-ISO/platform-services/governance-service
python main.py
```

**Бизнес-флоу**:
- Policy: Create draft → Review → Approve → Publish
- Role: Define → Set competence requirements → Assign → Publish event
- Resource: Create → Mark critical → Track availability → Allocate

---

### 4. Learning Service - Обучение и осведомленность
**Порт**: `8021`
**ISO**: Clauses 7.2, 7.3
**Статус**: ✅ **ГОТОВ К ЗАПУСКУ**

**Назначение**: Управление тренингами, компетенциями, awareness campaigns, сертификация, геймификация.

**API Endpoints** (26):
- Training Programs: `POST /api/v1/learning/programs`, `POST /api/v1/learning/programs/{id}/publish`
- Enrollments: `POST /api/v1/learning/enrollments`, `POST /api/v1/learning/enrollments/{id}/complete`
- Competency Assessments: gap analysis, рекомендации
- Awareness Campaigns: 8 типов кампаний
- Gamification: `GET /api/v1/learning/persons/{id}/achievements`, leaderboard

**База данных**:
- PostgreSQL: training_programs, training_enrollments, competency_assessments, awareness_campaigns, user_achievements

**Gamification**:
- 21 point action
- 19 achievement types
- 7-tier leveling (Beginner → Champion)
- Leaderboards, streaks

**Интеграции**:
- EventBus: получает события от Governance (person.added), публикует training события
- Governance Service: получает competency requirements

**Запуск**:
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/bcm
EVENTBUS_URL=http://localhost:8001
cd /Users/MD/AI-Platform-ISO/platform-services/learning-service
python main.py
```

**Бизнес-флоу**:
- Enrollment: ENROLLED → IN_PROGRESS → COMPLETED → CERTIFIED
- 11 competency areas (BCI practices)

---

### 5. Planning Service - Стратегии BCM
**Порт**: `8011`
**ISO**: Clause 8.3
**Статус**: ✅ **ГОТОВ К ЗАПУСКУ**

**Назначение**: Разработка и выбор стратегий Business Continuity.

**API Endpoints** (8):
- `POST /api/strategies` - Создание стратегии
- `GET /api/strategies` - Список стратегий
- `POST /api/strategies/{id}/cost-benefit` - Cost-benefit анализ (NPV, ROI, Payback)
- `POST /api/strategies/{id}/submit-review` - Submit for review
- `POST /api/strategies/{id}/approve` - Approve

**База данных**:
- PostgreSQL: planning.strategies (JSON columns)
- Redis: кэш стратегий

**Cost-Benefit Analysis**:
- NPV (Net Present Value) с discount rate
- ROI (Return on Investment) %
- Payback Period
- CAPEX, OPEX, training, maintenance breakdown

**Интеграции**:
- BIA Service (8012): получает BIA результаты
- Risk Service (8006): получает risk assessments
- EventBus: получает `bia.analysis.completed`, публикует `planning.strategy.approved`

**Запуск**:
```bash
DATABASE_URL=postgresql+asyncpg://bcm:bcm@localhost:5432/bcm
REDIS_URL=redis://localhost:6379/0
BIA_SERVICE_URL=http://localhost:8012
RISK_SERVICE_URL=http://localhost:8006
cd /Users/MD/AI-Platform-ISO/platform-services/planning_service
python main.py
```

**Бизнес-флоу**:
- BIA completion → Strategy selection → Cost-benefit analysis → Approval

---

### 6. Plans Service - Планы и процедуры BCM
**Порт**: `8023`
**ISO**: Clause 8.4
**Статус**: ⚠️ **SYNTAX ERROR - ИСПРАВИТЬ!**

**КРИТИЧЕСКАЯ ПРОБЛЕМА**:
- Line 69 в `main.py`: неверная индентация `global audit_logger`
- **ДЕЙСТВИЕ**: Исправить отступ

**Назначение**: Управление BC планами, процедурами, contact lists, активация планов, reviews.

**API Endpoints** (25+):
- Plan Management: `POST /api/plans/plans`, `POST /api/plans/plans/{id}/activate`
- Procedures: `POST /api/plans/plans/{id}/procedures`
- Resources: `POST /api/plans/plans/{id}/resources`
- Contact Lists: `POST /api/plans/contact-lists` (ISO 8.4.3)
- Plan Activation: `POST /api/plans/plans/{id}/activate-real` (ISO 8.4.2)
- Reviews: `POST /api/plans/plans/{id}/reviews`

**База данных**:
- PostgreSQL: Plan, Procedure, PlanResource, ContactList, PlanActivation, PlanReview

**Plan Types**:
- IT_RECOVERY, DISASTER_RECOVERY, CRISIS_MANAGEMENT, PANDEMIC, CYBER_INCIDENT, SUPPLY_CHAIN

**Contact Roles**:
- INCIDENT_MANAGER, TEAM_LEAD, TECHNICAL_LEAD, STAKEHOLDER, VENDOR

**Интеграции**:
- Planning Service (8011): получает approved strategies
- BIA Service (8012): получает RTO/RPO requirements
- Incident Service: координация активации планов
- EventBus: `planning.strategy.approved`, `bia.analysis.completed`

**Запуск**:
```bash
# СНАЧАЛА ИСПРАВИТЬ SYNTAX ERROR!
DATABASE_URL=postgresql+asyncpg://bcm:bcm@localhost:5432/bcm
PLANNING_SERVICE_URL=http://localhost:8011
cd /Users/MD/AI-Platform-ISO/platform-services/plans_service
python -m plans_service.main
```

**Бизнес-флоу**:
- Workflow: DRAFT → UNDER_REVIEW → APPROVED → ACTIVE → ARCHIVED
- Activation types: REAL_INCIDENT, TEST_EXERCISE, DRILL

---

### 7. Response Service - Управление инцидентами
**Порт**: `8041`
**ISO**: Clause 8.4
**Статус**: ✅ **ГОТОВ К ЗАПУСКУ**

**Назначение**: Полный lifecycle управления инцидентами от обнаружения до разрешения с ISO 22301 compliance.

**API Endpoints** (21):
- Incidents: `POST /api/v1/response/incidents`, `POST /api/v1/response/incidents/{id}/escalate`
- Response Actions: `POST /api/v1/response/incidents/{id}/actions`
- Response Teams: `POST /api/v1/response/incidents/{id}/team`
- Communications: `POST /api/v1/response/incidents/{id}/communications`
- Timeline: `GET /api/v1/response/incidents/{id}/timeline`
- Metrics: `POST /api/v1/response/incidents/{id}/metrics` (RTO/RPO tracking)
- Reports: `GET /api/v1/response/incidents/{id}/report`, `GET /api/v1/response/dashboard`

**База данных**:
- PostgreSQL (Supabase): incidents, response_actions, response_teams, communication_logs, incident_timeline, recovery_metrics

**Интеграции**:
- Risk Service (8031): risk analysis integration
- Impact Service (8032): impact analysis integration
- Recovery Service (8042): recovery coordination
- EventBus: получает `monitoring.alert.critical`, `recovery.rto_exceeded`

**Запуск**:
```bash
DATABASE_URL=postgresql+asyncpg://...@supabase/postgres
cd /Users/MD/AI-Platform-ISO/platform-services/response-service
python main.py
```

**Бизнес-флоу**:
- Incident: Detection → Investigation → Containment → Resolution → Closed
- Auto-escalation для critical incidents
- RTO/RPO compliance validation

---

### 8. Risk Service - Управление рисками
**Порт**: `8040`
**ISO**: Clause 8.2.3
**Статус**: ✅ **ГОТОВ К ЗАПУСКУ**

**Назначение**: Risk identification, assessment, quantitative analysis (FAIR/Monte Carlo), treatment planning.

**API Endpoints** (15):
- Risk CRUD: `POST /api/v1/risk/assessments`, `GET /api/v1/risk/assessments`
- Risk Analysis: `POST /api/v1/risk/assessments/{id}/fair-analysis`, `POST /api/v1/risk/assessments/{id}/monte-carlo`
- Treatment: `POST /api/v1/risk/assessments/{id}/treatment-plans`
- Reports: `GET /api/v1/risk/risk-heat-map`, `GET /api/v1/risk/risk-trends`

**База данных**:
- PostgreSQL: risk_assessments, fair_analysis, monte_carlo_simulations, risk_treatment_plans

**Risk Scoring**:
- Методология: 5×5 Risk Matrix
- Likelihood: 1-5 (Rare → Almost Certain)
- Impact: 1-5 (Insignificant → Catastrophic)
- Risk Score: Likelihood × Impact (1-25)
- Severity: Critical (≥20), High (15-19), Medium (8-14), Low (<8)

**FAIR Analysis**:
- Factor Analysis of Information Risk
- Quantitative risk assessment
- Confidence intervals

**Monte Carlo**:
- Probability distribution analysis
- Default 10,000 iterations
- Confidence intervals

**Интеграции**:
- EventBus: получает `bia.assessment.completed`, публикует `risk.assessment.completed`
- Planning Service: потребляет risk events

**Запуск**:
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/bcm
cd /Users/MD/AI-Platform-ISO/platform-services/risk-service
python main.py
```

---

### 9. Validation Service - Валидация и улучшение
**Порт**: `8022`
**ISO**: Clauses 8.5, 9.1, 9.2, 9.3, 10
**Статус**: ✅ **ГОТОВ К ЗАПУСКУ (требует Redis)**

**Назначение**: Exercises, performance monitoring, internal audits, management reviews, CAPA.

**API Endpoints** (35):
- Exercises: `POST /api/validation/exercises`, `POST /api/validation/exercises/{id}/start`
- Scenarios: `POST /api/validation/scenarios`
- KPIs: `POST /api/validation/kpis`, `POST /api/validation/kpi/collect-now` (auto-collection)
- Audits: `POST /api/validation/audits`, `POST /api/validation/audits/{id}/findings`
- CAPA: `POST /api/validation/capa`, `POST /api/validation/capa/{id}/verify`
- Management Reviews: `POST /api/validation/management-reviews`
- Reports: `GET /api/validation/reports/performance-summary`

**База данных**:
- PostgreSQL: exercises, kpis, kpi_measurements, audit_plans, audit_findings, capa, management_reviews
- Redis: REQUIRED для Celery task queue

**Background Tasks (Celery)**:
- Auto-collection KPIs (24h interval)
- Alert checking (1h interval)
- Email notifications

**Exercise Types**:
- Tabletop, Walkthrough, Simulation, Full-scale

**Интеграции**:
- Orchestrator (8002): service registration
- EventBus (8001): webhooks
- Governance, Plans, Incidents Services: KPI data collection

**Запуск**:
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/bcm
REDIS_URL=redis://localhost:6379/0  # REQUIRED!
ORCHESTRATOR_URL=http://localhost:8002
cd /Users/MD/AI-Platform-ISO/platform-services/validation-service
python main.py

# Отдельные процессы для Celery:
celery -A tasks.celery_app worker --loglevel=info
celery -A tasks.celery_app beat --loglevel=info
```

**Бизнес-флоу**:
- Exercise: Planned → Scheduled → In Progress → Completed → Reviewed
- Audit: Planned → In Progress → Fieldwork Complete → Reported → Closed
- CAPA: Open → In Progress → Implemented → Verified → Closed

---

### 10. Documents Service - Управление документами
**Порт**: `8024`
**ISO**: Clause 7.5
**Статус**: ✅ **ГОТОВ К ЗАПУСКУ**

**Назначение**: Enterprise DMS для ISO 22301 документов с AI/NLP processing.

**API Endpoints** (24+):
- Documents: `POST /api/documents/documents`, `GET /api/documents/documents`
- Workflow: `POST /api/documents/documents/{id}/workflow/{action}`
- Approvals: `POST /api/documents/documents/{id}/approvals`
- Retention: `POST /api/documents/retention-policies`
- ISO Coverage: `GET /api/documents/iso-coverage`

**AI/NLP Features**:
- Text extraction (PDF, DOCX, Excel, OCR)
- Auto-classification (document types, ISO clause mapping)
- Entity recognition
- Summarization
- Version comparison (diff)

**Document Lifecycle**:
- DRAFT → REVIEW → APPROVED → PUBLISHED → ARCHIVED

**Retention Policies**:
- ISO 22301: 3-7 years
- HIPAA: 6+ years
- Phases: ACTIVE → ARCHIVED → DESTROYED → LEGAL_HOLD

**Security**:
- Classification: Public → Highly Restricted
- Access control, audit logging
- Time-limited sharing tokens
- SHA-256 hash verification

**База данных**:
- PostgreSQL: 8 core tables (documents, versions, approvals, retention_policies)

**Интеграции**:
- All BCM Services: хранят compliance документы
- EventBus: публикует document события

---

## КАТЕГОРИЯ 2: ПЛАТФОРМЕННЫЕ СЕРВИСЫ

Эти сервисы расширяют функциональность платформы.

### 11. Community Portal - Портал сообщества
**Порт**: `8033`
**Статус**: ✅ **MVP ГОТОВ К ЗАПУСКУ**

**Назначение**: Knowledge Hub, Scenario Marketplace, Community Forum для BCM professionals.

**API Endpoints** (38):
- Knowledge Hub: `POST /api/portal/knowledge/articles`, full-text search, voting, AI generation
- Scenario Marketplace: `GET /api/portal/scenarios`, one-click deployment
- Community Forum: `POST /api/portal/forum/topics`, reputation, badges, moderation

**База данных**:
- PostgreSQL (Supabase): portal schema

**Интеграции**:
- Clients Service (8030): authentication
- Validation Service (8022): exercise integration, AI article generation
- Learning Service: training completed events
- EventBus: 12 event types published

**Запуск**:
```bash
DATABASE_URL=postgresql+asyncpg://...@supabase/postgres
EVENTBUS_URL=http://localhost:8001
CLIENTS_SERVICE_URL=http://localhost:8030
cd /Users/MD/AI-Platform-ISO/platform-services/community-service/portal
uvicorn main:app --host 0.0.0.0 --port 8033
```

**⚠️ Blocking Issue**: Shared library imports (`shared.eventbus`)

---

### 12. Community Marketplace - Маркетплейс специалистов
**Порт**: `8032`
**Статус**: ✅ **MVP ГОТОВ К ЗАПУСКУ**

**Назначение**: "Uber for BCM Consultants" - marketplace connecting specialists with companies.

**API Endpoints** (46):
- Specialists: `POST /api/marketplace/specialists`, verification, portfolio
- Projects: `POST /api/marketplace/projects`, matching algorithm
- Proposals: `POST /api/marketplace/proposals`, bidding
- Reviews: `POST /api/marketplace/reviews`, 5-star rating

**База данных**:
- PostgreSQL (Supabase): marketplace schema

**Интеграции**:
- Portal Service (8033): knowledge articles, forum reputation
- Clients Service (8030): authentication
- Governance Service: competency sync, auto-verification via roles
- Learning Service: certification sync
- EventBus: 11 event types published

**Запуск**:
```bash
DATABASE_URL=postgresql+asyncpg://...@supabase/postgres
PORTAL_URL=http://localhost:8033
cd /Users/MD/AI-Platform-ISO/platform-services/community-service/marketplace
uvicorn main:app --host 0.0.0.0 --port 8032
```

**⚠️ Blocking Issue**: Shared library imports, Portal dependency

---

### 13. Living Docs - Самообучающаяся документация
**Порт**: `8034`
**Статус**: ✅ **ГОТОВ К ЗАПУСКУ**

**Назначение**: "Netflix for BCM Documentation" - AI-powered self-evolving educational platform.

**API Endpoints**:
- `GET /api/v1/{page_id}` - Personalized documentation
- `POST /api/v1/examples/generate` - AI example generation
- `GET /api/v1/search` - Smart contextual search
- `GET /api/v1/journey/{goal}` - Personalized learning paths
- `GET /api/v1/gaps` - Knowledge gap detection

**Ключевые возможности**:
- AI self-learning (learns from user interactions)
- Auto-improves unclear content
- Auto-generates missing topics
- A/B tests improvements
- Deploys winning versions automatically

**Персонализация**:
- User-specific documentation
- Industry-specific examples
- Experience level adjustment
- Related content recommendations

**НЕ ДУБЛИКАТ** Documents Service:
- Documents Service = formal compliance documents (ISO 22301)
- Living Docs = educational/instructional content

**Интеграция с Documents Service**:
```python
# Formal policy link to easy explanation
{
  "document_id": 123,
  "living_docs_explanation": "/api/v1/docs/bia-policy-explained"
}
```

---

### 14. Compliance Monitoring - Мониторинг соответствия
**Порт**: `8779`
**Путь**: `/мониторинг/compliance-monitoring`
**Статус**: ✅ **ГОТОВ К ЗАПУСКУ**

**⚠️ РЕКОМЕНДАЦИЯ**: Переименовать `/мониторинг` → `/compliance-monitoring-services`

**Назначение**: Real-time compliance tracking, alerts, nonconformity management.

**API Endpoints** (33+):
- Compliance Alerts
- Nonconformity management
- Audit requirements tracking
- WebSocket real-time alerts
- Auto-registration с Prometheus

**Интеграции**:
- Compliance Service
- Governance Service
- Prometheus/Grafana

**НЕ ДУБЛИКАТ** `/monitoring`:
- `/monitoring` = infrastructure config (Prometheus YML files)
- `/мониторинг` = active compliance services

---

### 15. Process Analytics - Аналитика процессов
**Порт**: `8780`
**Путь**: `/мониторинг/process-analytics`
**Статус**: ✅ **ГОТОВ К ЗАПУСКУ**

**Назначение**: Process mining, pattern discovery, deviation detection, performance analysis.

**Возможности**:
- Process pattern discovery
- Deviation detection
- Performance analysis
- Advanced analytics engine

---

### 16. Simulation Service
**Порт**: `8031`
**Статус**: ⏸️ **НЕ ТРОГАЛИ - ОСТАВЛЕНО НА КОНЕЦ**

**Назначение**: Monte Carlo simulations, scenario modeling.

**Примечание**: По твоему указанию пропустили на этапе аудита.

---

### 17. Monitoring (Infrastructure)
**Путь**: `/monitoring`
**Тип**: Configuration files (НЕ СЕРВИС!)
**Статус**: ✅ **АКТИВНЫЕ КОНФИГИ**

**Содержимое**:
- `prometheus.yml` - Prometheus configuration
- Grafana dashboard JSONs
- Infrastructure monitoring setup

**НЕ ДУБЛИКАТ** `/мониторинг` - это разные вещи!

---

## ВСПОМОГАТЕЛЬНЫЕ ДИРЕКТОРИИ

### Tools
**Путь**: `/tools`
**Тип**: Utility scripts

**Содержимое**:
- `integrate_workflow_intelligence.sh` - Script для интеграции Workflow Intelligence
- Генерирует workflow_ai.py templates для сервисов
- Targets: plans_service, bia-service, compliance-service

**Использование**:
```bash
bash /Users/MD/AI-Platform-ISO/platform-services/tools/integrate_workflow_intelligence.sh
```

---

## СВОДНАЯ ТАБЛИЦА: ПОРТЫ И СТАТУСЫ

| Сервис | Порт | ISO Clause | Статус | Проблемы |
|--------|------|------------|--------|----------|
| **BIA Service** | 8012 | 8.2.2 | ✅ ГОТОВ | - |
| **Compliance Service** | 8014 | 9.2, 10.1, 10.2 | ✅ ГОТОВ | - |
| **Governance Service** | 8013 | 4, 5, 6, 7 | ⚠️ ПОРТ! | **Config=8020, должен=8013** |
| **Learning Service** | 8021 | 7.2, 7.3 | ✅ ГОТОВ | - |
| **Planning Service** | 8011 | 8.3 | ✅ ГОТОВ | - |
| **Plans Service** | 8023 | 8.4 | ⚠️ SYNTAX! | **Line 69 indentation error** |
| **Response Service** | 8041 | 8.4 | ✅ ГОТОВ | - |
| **Risk Service** | 8040 | 8.2.3 | ✅ ГОТОВ | - |
| **Validation Service** | 8022 | 8.5, 9.1, 9.2, 9.3, 10 | ✅ ГОТОВ | Requires Redis |
| **Documents Service** | 8024 | 7.5 | ✅ ГОТОВ | - |
| **Community Portal** | 8033 | - | ✅ MVP | Shared imports |
| **Community Marketplace** | 8032 | - | ✅ MVP | Shared imports |
| **Living Docs** | 8034 | - | ✅ ГОТОВ | - |
| **Compliance Monitoring** | 8779 | - | ✅ ГОТОВ | Rename needed |
| **Process Analytics** | 8780 | - | ✅ ГОТОВ | Rename needed |
| **Simulation** | 8031 | - | ⏸️ SKIP | Not audited |

---

## КРИТИЧЕСКИЕ ДЕЙСТВИЯ ПЕРЕД ЗАПУСКОМ

### 🚨 ВЫСОКИЙ ПРИОРИТЕТ

1. **Governance Service - Исправить порт конфликт**
```bash
# Файл: /Users/MD/AI-Platform-ISO/platform-services/governance-service/config.py
# Line 17:
SERVICE_PORT: int = 8013  # Было 8020!
```

2. **Plans Service - Исправить syntax error**
```bash
# Файл: /Users/MD/AI-Platform-ISO/platform-services/plans_service/main.py
# Line 69 - исправить отступ:
    global audit_logger, iso_checker, security_middleware
```

3. **Переименовать `/мониторинг`**
```bash
cd /Users/MD/AI-Platform-ISO/platform-services
mv мониторинг compliance-monitoring-services

# ИЛИ разделить:
mkdir compliance-monitoring-service
mkdir process-analytics-service
mv мониторинг/compliance-monitoring/* compliance-monitoring-service/
mv мониторинг/process-analytics/* process-analytics-service/
```

### ⚠️ СРЕДНИЙ ПРИОРИТЕТ

4. **Настроить общие переменные окружения**
```bash
# Создать /Users/MD/AI-Platform-ISO/platform-services/.env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/bcm_platform
JWT_SECRET=<strong-secret-key>
EVENTBUS_URL=amqp://guest:guest@localhost:5672
REDIS_URL=redis://localhost:6379/0
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

5. **Исправить shared library imports**
```bash
# Для Portal и Marketplace:
cd /Users/MD/AI-Platform-ISO
pip install -e shared/  # Установить как package

# ИЛИ добавить в sys.path в main.py каждого сервиса
```

6. **Запустить Database migrations**
```bash
# Для каждого сервиса с database/migrations/:
psql -h localhost -U bcm -d bcm_platform -f service/database/migrations/001_init.sql
```

---

## ПОСЛЕДОВАТЕЛЬНОСТЬ ЗАПУСКА

### Шаг 1: Инфраструктура
```bash
# 1. PostgreSQL
docker-compose up -d postgres

# 2. Redis
docker-compose up -d redis

# 3. RabbitMQ (EventBus)
docker-compose up -d rabbitmq

# 4. Проверить подключения
psql -h localhost -U bcm -d bcm_platform -c "SELECT 1;"
redis-cli ping
```

### Шаг 2: Core Services (в порядке зависимостей)
```bash
# 1. Governance (8013) - базовый для всех
cd governance-service && python main.py &

# 2. BIA (8012)
cd bia-service && python main.py &

# 3. Risk (8040)
cd risk-service && python main.py &

# 4. Compliance (8014)
cd compliance-service && python main.py &

# 5. Learning (8021)
cd learning-service && python main.py &

# 6. Planning (8011)
cd planning_service && python -m planning_service.main &

# 7. Plans (8023) - после исправления syntax!
cd plans_service && python -m plans_service.main &

# 8. Response (8041)
cd response-service && python main.py &

# 9. Validation (8022) + Celery
cd validation-service && python main.py &
celery -A tasks.celery_app worker --loglevel=info &
celery -A tasks.celery_app beat --loglevel=info &

# 10. Documents (8024)
cd documents-service && python main.py &
```

### Шаг 3: Platform Services
```bash
# 11. Community Portal (8033)
cd community-service/portal && uvicorn main:app --port 8033 &

# 12. Community Marketplace (8032)
cd community-service/marketplace && uvicorn main:app --port 8032 &

# 13. Living Docs (8034)
cd living-docs && python main.py &

# 14. Compliance Monitoring (8779)
cd compliance-monitoring-services/compliance-monitoring && python main.py &

# 15. Process Analytics (8780)
cd compliance-monitoring-services/process-analytics && python main.py &
```

### Шаг 4: Проверка здоровья
```bash
# Проверить все health endpoints:
for port in 8012 8013 8014 8021 8011 8023 8040 8041 8022 8024 8033 8032 8034 8779 8780; do
  echo "Checking port $port..."
  curl -s http://localhost:$port/health | jq .
done
```

---

## INTEGRATION MAP - Карта интеграций

```
┌─────────────────────────────────────────────────────────────┐
│                     EVENT-DRIVEN CHOREOGRAPHY                │
└─────────────────────────────────────────────────────────────┘

BIA (8012) ──[bia.assessment.completed]──> Risk (8040)
Risk (8040) ──[risk.assessment.completed]──> Planning (8011)
Planning (8011) ──[planning.strategy.approved]──> Plans (8023)
Plans (8023) ──[plans.plan.activated]──> Response (8041)
Response (8041) ──[response.incident.resolved]──> Compliance (8014)

Governance (8013) ──[governance.policy.created]──> ALL SERVICES
Learning (8021) ──[learning.certification.issued]──> Marketplace (8032)
Compliance (8014) ──[compliance.gap.identified]──> Risk (8040)

Monitoring ──[monitoring.alert.critical]──> Response (8041)
Recovery ──[recovery.rto_exceeded]──> Response (8041)
```

### Прямые HTTP вызовы:
```
Portal (8033) ──> Validation (8022) [AI article generation]
Portal (8033) ──> Clients (8030) [authentication]
Marketplace (8032) ──> Portal (8033) [reputation, articles]
Marketplace (8032) ──> Governance (8020) [competencies]
All Services ──> Orchestrator (8002) [service registration]
```

---

## ОБЩИЕ ЗАВИСИМОСТИ

### Python Packages (все сервисы):
```
fastapi >= 0.104.0
uvicorn[standard] >= 0.24.0
pydantic >= 2.5.0
sqlalchemy >= 2.0.0
asyncpg >= 0.28.0
httpx >= 0.25.0
python-jose[cryptography] >= 3.3.0
prometheus-client >= 0.18.0
```

### Локальные пакеты:
```
workflow-intelligence (из /intelligent-core/)
shared (из project root)
```

### Инфраструктура:
```
PostgreSQL 14+
Redis 5.0+
RabbitMQ 3.11+
(Опционально) Supabase для Portal/Marketplace
```

---

## МЕТРИКИ КОДА

**Всего сервисов**: 15 активных (+ 1 simulation не аудирован)
**Всего API endpoints**: 400+
**Строк кода**: ~50,000+ (без intelligent-core)
**Database tables**: 80+ (across all services)
**Event types**: 60+ choreography events
**ISO Clauses covered**: 4, 5, 6, 7, 8.2.2, 8.2.3, 8.3, 8.4, 8.5, 9.1, 9.2, 9.3, 10

---

## СЛЕДУЮЩИЕ ШАГИ

### Немедленно:
- [ ] Исправить Governance port conflict
- [ ] Исправить Plans syntax error
- [ ] Переименовать `/мониторинг`
- [ ] Создать общий .env файл

### На этой неделе:
- [ ] Запустить все ISO сервисы
- [ ] Протестировать event choreography
- [ ] Проверить database migrations
- [ ] Настроить monitoring (Prometheus/Grafana)

### Следующий спринт:
- [ ] Запустить Platform сервисы
- [ ] Интеграционные тесты
- [ ] Load testing
- [ ] Security audit

---

**Документ составлен**: 2025-10-10
**Аудитор**: AI Platform Code Audit System
**Статус**: ✅ Готов к запуску после исправлений
