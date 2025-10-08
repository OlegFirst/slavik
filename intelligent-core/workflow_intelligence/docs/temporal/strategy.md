# Temporal Cloud - Стратегия Интеграции в AI-Powered BCM Platform

**Версия:** 1.0
**Дата:** 2025-10-06
**Статус:** ✅ Temporal Cloud настроен

---

## 📖 Что такое Temporal Cloud

**Temporal** - это платформа для оркестрации долгоживущих, надежных рабочих процессов (workflows).

### Ключевые возможности Temporal

#### 1. Надежность и устойчивость к сбоям
- **Автоматические retry** при сбоях (network, database, API failures)
- **Workflows выживают при крашах сервера** - состояние сохраняется в БД
- **Exactly-once execution semantics** - гарантия выполнения
- **Automatic recovery** - процессы продолжают работу после перезапуска

**Пример:**
```python
# Если activity упал - Temporal автоматически retry
@activity.defn(retry_policy=RetryPolicy(
    maximum_attempts=10,
    initial_interval=timedelta(seconds=1),
    maximum_interval=timedelta(minutes=5),
    backoff_coefficient=2.0
))
async def call_external_api():
    # Если API недоступен - будет 10 попыток с exponential backoff
    return await http_client.post("https://api.example.com")
```

#### 2. Долгоживущие процессы
- **Workflows выполняются дни, недели, месяцы**
- **Automatic timers и schedules** (cron-like)
- **Ожидание внешних событий** (human-in-the-loop, approvals)
- **Signals и queries** для взаимодействия с running workflows

**Пример:**
```python
@workflow.defn
class QuarterlyAuditWorkflow:
    """Workflow выполняется 3 месяца"""

    @workflow.run
    async def run(self):
        # Сбор данных за квартал за квартал
        for month in range(3):
            await workflow.sleep(timedelta(days=30))
            data = await workflow.execute_activity(collect_monthly_data)

        # Генерация отчета
        return await workflow.execute_activity(generate_report, data)
```

#### 3. Visibility и мониторинг
- **Web UI** для просмотра всех workflows в реальном времени
- **История выполнения** каждого шага (event history)
- **Метрики и аналитика** (latency, success rate, etc.)
- **Search и фильтрация** workflows по атрибутам

**Dashboard:** https://cloud.temporal.io
- Видно все running workflows
- История всех completed workflows
- Детали каждого activity
- Stack traces при ошибках

#### 4. Версионирование и обновления
- **Обновление workflow logic БЕЗ остановки** выполняющихся процессов
- **Rollback** к предыдущим версиям
- **Gradual rollout** новых версий

#### 5. Параллелизм и оркестрация
- **Параллельные activities** (fan-out/fan-in)
- **Child workflows** (композиция сложных процессов)
- **Sagas pattern** (distributed transactions с compensations)

**Пример:**
```python
# Параллельное выполнение 10 activities
results = await asyncio.gather(*[
    workflow.execute_activity(process_item, item)
    for item in items
])
```

#### 6. Testing и отладка
- **Replay тесты** - воспроизведение workflow execution
- **Time skipping** в тестах (не ждать реальное время)
- **Детерминистическое выполнение** (результаты предсказуемы)

---

## 🎯 Как мы будем использовать Temporal в проекте

### Temporal = МОЗГ платформы

Из `арх2.md`:
> "Workflow Intelligence Engine - это единственный компонент, который НЕЛЬЗЯ заменить позже. Определяет как работают ВСЕ остальные компоненты."

### Что НЕ идет через Temporal:
❌ Simple CRUD operations (создать документ, обновить пользователя)
❌ Синхронные API запросы
❌ Stateless operations

### Что ОБЯЗАТЕЛЬНО идет через Temporal:
✅ **Долгоживущие бизнес-процессы** (BIA, Risk Assessment, Planning)
✅ **Human-in-the-loop workflows** (approvals, reviews)
✅ **Процессы с внешними зависимостями** (ожидание данных, API calls)
✅ **Критичные операции** (incident response, disaster recovery)
✅ **Scheduled/recurring процессы** (compliance audits, testing)

---

## 🏗️ Архитектура интеграции

```
┌─────────────────────────────────────────────────────────────┐
│                    TEMPORAL CLOUD                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ BIA Workflow │  │ Risk         │  │ Compliance   │      │
│  │              │  │ Workflow     │  │ Workflow     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│         ▲ Event History (persistent)                        │
└─────────┼───────────────────────────────────────────────────┘
          │
          │ gRPC (europe-west3.gcp.api.temporal.io:7233)
          │ API Key Auth + TLS
          ▼
┌─────────────────────────────────────────────────────────────┐
│         WORKFLOW INTELLIGENCE ENGINE (наш код)              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Temporal Worker (Python)                            │  │
│  │  - Executes workflow code                            │  │
│  │  - Executes activities                               │  │
│  │  - Reports to Temporal Cloud                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Activities   │  │ Case Library │  │ Governance   │      │
│  │ (Actions)    │  │ (Learning)   │  │ (Rules)      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
          │
          │ Uses infrastructure
          ▼
┌─────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │PostgreSQL│  │  Redis   │  │  Qdrant  │  │ EventBus │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Последовательность интеграции: НЕ параллельно!

### ❌ НЕПРАВИЛЬНО:
```
Phase 1: Настроить всю инфраструктуру (БД, Redis, EventBus, etc.)
Phase 2: Добавить Temporal
Phase 3: Интегрировать workflows
```

### ✅ ПРАВИЛЬНО (Bottom-Up из арх2.md):

```
Phase 0 (2-3 часа): ✅ DONE
├─ Temporal Cloud setup
├─ API Key получен
└─ Connection tested

Phase 1 (4-6 часов): Basic Infrastructure
├─ Только PostgreSQL (для Case Library)
├─ Только Redis (для caching)
├─ Только Qdrant (для semantic search)
└─ Temporal Worker running

Phase 2 : Workflow Intelligence Engine ⭐ СНАЧАЛА ЭТО!
├─ Phase 2.1: Core Workflow Engine на Temporal
│   ├─ BIA Workflow definition
│   ├─ Activities implementation
│   └─ State machine logic
│
├─ Phase 2.2: Case Library
│   ├─ Auto-collect completed workflows
│   ├─ Store in PostgreSQL + Qdrant
│   ├─ AI analysis of patterns
│   └─ Semantic search
│
├─ Phase 2.3: Governance System
│   ├─ Rules Engine (checkpoints)
│   ├─ Creative Zones (AI autonomy)
│   └─ Integration with workflows
│
└─ Phase 2.4: First Production Workflow
    ├─ BIA Workflow fully tested
    ├─ Running in Temporal Cloud
    └─ Case Library collecting data

Phase 3 : Platform Services Integration
├─ BIA Service использует BIA Workflow
├─ Risk Service использует Risk Workflow
├─ Planning Service использует Planning Workflow
└─ All services publish to Case Library

Phase 4 : Infrastructure Services
├─ EventBus (для inter-service events)
├─ Notification Service
└─ Monitoring

Phase 5 : Human Interface
├─ API Gateway
├─ Web UI для workflows
└─ Integration с Temporal UI
```

### Почему такая последовательность?

**1. Workflow Intelligence ПЕРВЫЙ:**
- Определяет КАК работают все процессы
- Case Library учится на каждом выполнении
- Governance rules применяются с первого дня
- Невозможно заменить позже

**2. Platform Services ВТОРЫМИ:**
- Используют готовые workflows
- Не нужно придумывать логику с нуля
- AI уже имеет context из Case Library

**3. Infrastructure ТРЕТЬИМ:**
- Мы уже знаем что нужно
- EventBus публикует события workflows
- Monitoring знает что мониторить

---

## 🔄 Какие процессы интегрируем с Temporal

### 1. BIA (Business Impact Analysis) Workflow

**Продолжительность:** 
**Участники:** Stakeholders, AI Agents, Compliance Officers
**Почему Temporal:** Долгий процесс, human approvals, критичные данные

**Стадии:**
```python
@workflow.defn
class BIAWorkflow:
    """
    Temporal Workflow для BIA
    Выполняется 
    """

    @workflow.run
    async def run(self, org_id: str) -> BIAResult:
        # Stage 1: Kickoff Meeting 
        kickoff = await workflow.execute_activity(
            schedule_kickoff_meeting,
            org_id,
            start_to_close_timeout=timedelta(days=2)
        )

        # Ждем подтверждения от stakeholders
        await workflow.wait_condition(
            lambda: self.kickoff_confirmed
        )

        # Stage 2: Data Collection 
        # AI собирает данные + human input
        data = await workflow.execute_activity(
            ai_data_collection,
            org_id,
            start_to_close_timeout=timedelta(days=5)
        )

        # Stage 3: Dependency Analysis 
        # AI анализирует зависимости
        dependencies = await workflow.execute_activity(
            ai_dependency_analysis,
            data,
            start_to_close_timeout=timedelta(days=3)
        )

        # Stage 4: Impact Assessment (3-4 дня)
        # Governance checkpoint - нужно ли AI approval?
        governance_check = await workflow.execute_activity(
            governance_checkpoint,
            dependencies
        )

        if governance_check.requires_human:
            # Human review
            impact = await workflow.execute_activity(
                human_impact_assessment,
                dependencies,
                start_to_close_timeout=timedelta(days=4)
            )
        else:
            # Creative Zone - AI может решать
            impact = await workflow.execute_activity(
                ai_impact_assessment,
                dependencies
            )

        # Stage 5: RTO/RPO Definition 
        rto_rpo = await workflow.execute_activity(
            define_rto_rpo,
            impact,
            start_to_close_timeout=timedelta(days=2)
        )

        # Stage 6: Validation (2 дня)
        validation = await workflow.execute_activity(
            validate_bia_results,
            rto_rpo,
            start_to_close_timeout=timedelta(days=2)
        )

        # Stage 7: Final Approval (1-3 дня)
        # Ждем approval от compliance officer
        await workflow.wait_condition(
            lambda: self.compliance_approved
        )

        # Stage 8: Publish to Case Library
        await workflow.execute_activity(
            publish_to_case_library,
            validation
        )

        return BIAResult(
            organization_id=org_id,
            rto=rto_rpo.rto,
            rpo=rto_rpo.rpo,
            critical_processes=impact.critical_processes,
            completed_at=workflow.now()
        )
```

**Преимущества Temporal:**
- ✅ Процесс может длиться месяц - не проблема
- ✅ Крашнулся сервер? Продолжим с того же места
- ✅ Stakeholder не ответил? Ждем signal
- ✅ Вся история в Temporal UI

---

### 2. Risk Assessment Workflow

**Продолжительность:** 
**Участники:** Risk Managers, AI Agents
**Почему Temporal:** Сложные расчеты, external data, approvals

**Стадии:**
```python
@workflow.defn
class RiskAssessmentWorkflow:
    """
    Risk Assessment Workflow
    Интеграция с внешними источниками данных
    """

    @workflow.run
    async def run(self, scope: str) -> RiskReport:
        # Stage 1: Identify Risks (AI + Case Library)
        # Ищем похожие cases в Case Library
        similar_cases = await workflow.execute_activity(
            search_case_library,
            scope
        )

        # AI генерирует список рисков на основе similar cases
        risks = await workflow.execute_activity(
            ai_identify_risks,
            scope,
            similar_cases
        )

        # Stage 2: Assess Likelihood (parallel)
        # Параллельно оцениваем все риски
        assessments = await asyncio.gather(*[
            workflow.execute_activity(
                assess_risk_likelihood,
                risk,
                start_to_close_timeout=timedelta(hours=24)
            )
            for risk in risks
        ])

        # Stage 3: External Data Collection
        # Retry при сбоях API
        external_data = await workflow.execute_activity(
            fetch_external_threat_data,
            scope,
            retry_policy=RetryPolicy(
                maximum_attempts=5,
                backoff_coefficient=2.0
            )
        )

        # Stage 4: Calculate Risk Scores
        risk_scores = await workflow.execute_activity(
            calculate_risk_scores,
            assessments,
            external_data
        )

        # Stage 5: Prioritize Mitigation
        mitigation_plan = await workflow.execute_activity(
            ai_prioritize_mitigation,
            risk_scores
        )

        # Stage 6: Approval (if high-risk items found)
        if any(r.score > 8 for r in risk_scores):
            await workflow.wait_condition(
                lambda: self.high_risk_approved
            )

        # Stage 7: Publish to Case Library
        await workflow.execute_activity(
            publish_risk_case,
            risk_scores,
            mitigation_plan
        )

        return RiskReport(
            scope=scope,
            risks=risk_scores,
            mitigation_plan=mitigation_plan
        )
```

---

### 3. Incident Response Workflow

**Продолжительность:** От минут до длительных процессов
**Участники:** Response Team, AI Agents, Management
**Почему Temporal:** Критичность, real-time, escalations

**Стадии:**
```python
@workflow.defn
class IncidentResponseWorkflow:
    """
    Incident Response - критичный процесс
    Temporal гарантирует выполнение даже при сбоях
    """

    @workflow.run
    async def run(self, incident: Incident) -> Resolution:
        # Stage 0: Immediate Actions (секунды)
        if incident.severity == "CRITICAL":
            # Параллельно:
            # 1. Escalate to management
            # 2. Activate response team
            # 3. Send notifications
            await asyncio.gather(
                workflow.execute_activity(
                    escalate_to_management,
                    incident,
                    start_to_close_timeout=timedelta(seconds=30)
                ),
                workflow.execute_activity(
                    activate_response_team,
                    incident,
                    start_to_close_timeout=timedelta(minutes=1)
                ),
                workflow.execute_activity(
                    send_emergency_notifications,
                    incident,
                    start_to_close_timeout=timedelta(seconds=10)
                )
            )

        # Stage 1: Assess Impact (минуты)
        impact = await workflow.execute_activity(
            assess_incident_impact,
            incident,
            start_to_close_timeout=timedelta(minutes=5)
        )

        # Stage 2: Search Case Library (секунды)
        # Ищем похожие incidents
        similar_incidents = await workflow.execute_activity(
            search_similar_incidents,
            incident,
            impact
        )

        # Stage 3: AI Recommendation (секунды)
        # AI предлагает решение на основе similar cases
        ai_recommendation = await workflow.execute_activity(
            ai_recommend_solution,
            incident,
            similar_incidents
        )

        # Stage 4: Governance Check
        governance = await workflow.execute_activity(
            governance_checkpoint,
            incident,
            ai_recommendation
        )

        if governance.requires_human_approval:
            # Ждем human decision (минуты-часы)
            await workflow.wait_condition(
                lambda: self.human_decision_made,
                timeout=timedelta(hours=2)
            )
            solution = self.human_decision
        else:
            # Creative Zone - AI executes
            solution = ai_recommendation

        # Stage 5: Execute Response (минуты-часы)
        result = await workflow.execute_activity(
            execute_incident_response,
            solution,
            start_to_close_timeout=timedelta(hours=24)
        )

        # Stage 6: Verify Resolution
        verified = await workflow.execute_activity(
            verify_incident_resolved,
            result
        )

        if not verified:
            # Escalate to next level
            return await workflow.execute_child_workflow(
                EscalatedIncidentWorkflow,
                incident,
                result
            )

        # Stage 7: Post-Incident Report
        report = await workflow.execute_activity(
            generate_incident_report,
            incident,
            result
        )

        # Stage 8: Publish to Case Library
        await workflow.execute_activity(
            publish_incident_case,
            incident,
            solution,
            result,
            report
        )

        return Resolution(
            incident_id=incident.id,
            resolved=True,
            solution=solution,
            duration=workflow.now() - incident.created_at,
            report=report
        )
```

**Преимущества Temporal:**
- ✅ Гарантированное выполнение (incident НЕ потеряется)
- ✅ Вся история action в UI
- ✅ Timeout для human decisions
- ✅ Automatic escalation

---

### 4. Compliance Audit Workflow (Scheduled)

**Продолжительность:** Ежеквартально (recurring)
**Участники:** Auditors, AI Agents, Compliance Team
**Почему Temporal:** Cron schedule, long-running, approvals

**Стадии:**
```python
@workflow.defn
class ComplianceAuditWorkflow:
    """
    Quarterly Compliance Audit
    Runs automatically every quarter
    """

    @workflow.run
    async def run(self, quarter: str) -> AuditReport:
        # Stage 1: Document Collection 
        documents = await workflow.execute_activity(
            collect_compliance_documents,
            quarter,
            start_to_close_timeout=timedelta(days=7)
        )

        # Stage 2: AI Preliminary Check 
        ai_check = await workflow.execute_activity(
            ai_compliance_check,
            documents,
            start_to_close_timeout=timedelta(hours=24)
        )

        # Stage 3: Remediation (if issues found)
        if ai_check.issues:
            # Child workflow для каждого issue
            remediations = await asyncio.gather(*[
                workflow.execute_child_workflow(
                    RemediationWorkflow,
                    issue
                )
                for issue in ai_check.issues
            ])

        # Stage 4: Human Audit 
        human_audit = await workflow.execute_activity(
            human_compliance_audit,
            documents,
            ai_check,
            start_to_close_timeout=timedelta(days=5)
        )

        # Stage 5: Generate Report
        report = await workflow.execute_activity(
            generate_audit_report,
            human_audit
        )

        # Stage 6: Management Approval
        await workflow.wait_condition(
            lambda: self.management_approved
        )

        # Stage 7: Submit to Regulators
        submission = await workflow.execute_activity(
            submit_to_regulators,
            report,
            retry_policy=RetryPolicy(maximum_attempts=3)
        )

        # Stage 8: Publish to Case Library
        await workflow.execute_activity(
            publish_audit_case,
            report,
            submission
        )

        return report


# Schedule to run quarterly
@workflow.defn
class QuarterlyAuditSchedule:
    """
    Cron schedule для запуска audits
    """

    @workflow.run
    async def run(self):
        # Run every 3 months
        while True:
            quarter = get_current_quarter()

            # Start audit workflow
            await workflow.execute_child_workflow(
                ComplianceAuditWorkflow,
                quarter
            )

            # Sleep until next quarter
            await workflow.sleep(timedelta(days=90))
```

**Преимущества Temporal:**
- ✅ Cron-like scheduling
- ✅ Automatic execution
- ✅ Не забудем про audit
- ✅ История всех audits

---

### 5. DR Plan Testing Workflow (Scheduled)

**Продолжительность:** Ежемесячно/ежеквартально
**Участники:** DR Team, AI Agents
**Почему Temporal:** Scheduled, critical, long test duration

```python
@workflow.defn
class DRTestWorkflow:
    """
    Monthly DR Plan Testing
    Validates backup and recovery procedures
    """

    @workflow.run
    async def run(self, plan_id: str) -> TestResult:
        # Stage 1: Pre-Test Preparation
        prep = await workflow.execute_activity(
            prepare_dr_test,
            plan_id,
            start_to_close_timeout=timedelta(hours=4)
        )

        # Stage 2: Execute Tests (parallel)
        test_results = await asyncio.gather(*[
            workflow.execute_activity(
                test_backup_restore,
                system,
                start_to_close_timeout=timedelta(hours=8)
            )
            for system in prep.critical_systems
        ])

        # Stage 3: Verify RTO/RPO
        verification = await workflow.execute_activity(
            verify_rto_rpo_compliance,
            test_results
        )

        # Stage 4: AI Gap Analysis
        # Сравнить с previous tests из Case Library
        previous_tests = await workflow.execute_activity(
            get_previous_test_results,
            plan_id
        )

        gap_analysis = await workflow.execute_activity(
            ai_gap_analysis,
            test_results,
            previous_tests
        )

        # Stage 5: Remediation Plan
        if gap_analysis.gaps:
            remediation = await workflow.execute_activity(
                create_remediation_plan,
                gap_analysis.gaps
            )

            # Escalate to management
            await workflow.execute_activity(
                notify_management,
                remediation
            )

        # Stage 6: Update DR Plan
        updated_plan = await workflow.execute_activity(
            update_dr_plan,
            plan_id,
            test_results,
            gap_analysis
        )

        # Stage 7: Publish to Case Library
        await workflow.execute_activity(
            publish_dr_test_case,
            test_results,
            gap_analysis,
            updated_plan
        )

        return TestResult(
            plan_id=plan_id,
            passed=verification.compliant,
            gaps=gap_analysis.gaps,
            updated_plan=updated_plan
        )
```

---

## 🔄 Взаимодействие Workflows с Case Library

**Case Library = Самообучающаяся база знаний**

Каждый завершенный workflow автоматически публикуется в Case Library:

```python
@activity.defn
async def publish_to_case_library(workflow_result: dict):
    """
    Auto-publish completed workflow to Case Library

    Case включает:
    - Initial state
    - All transitions
    - Final outcome
    - Duration
    - Success/failure
    - Challenges encountered
    - Solutions applied
    """

    # 1. Extract workflow data
    case = WorkflowCase(
        id=workflow_result["workflow_id"],
        workflow_type=workflow_result["type"],
        organization_id=workflow_result["org_id"],
        industry=workflow_result["industry"],
        org_size=workflow_result["org_size"],

        initial_state=workflow_result["initial_state"],
        final_state=workflow_result["final_state"],
        transitions=workflow_result["transitions"],
        duration_days=workflow_result["duration"],

        success=workflow_result["success"],
        challenges=workflow_result["challenges"],
        solutions=workflow_result["solutions"],
    )

    # 2. Generate embedding для semantic search
    embedding = await ai_generate_embedding(case)
    case.embedding = embedding

    # 3. Save to PostgreSQL
    await db.save(case)

    # 4. Index in Qdrant (vector DB)
    await qdrant.index(
        collection="workflow_cases",
        id=case.id,
        vector=embedding,
        payload=case.to_dict()
    )

    # 5. AI learns patterns
    await ai_learn_from_case(case)
```

**Использование Case Library в новых workflows:**

```python
@activity.defn
async def ai_data_collection(org_id: str):
    """
    AI использует Case Library для генерации вопросов
    """

    # 1. Get organization context
    org = await db.get_organization(org_id)

    # 2. Search similar cases in Case Library
    similar_cases = await qdrant.search(
        collection="workflow_cases",
        query_vector=await ai_generate_embedding(org),
        limit=5,
        filter={
            "workflow_type": "bia",
            "industry": org.industry,
            "org_size": org.size
        }
    )

    # 3. AI learns from similar cases
    # - Какие вопросы задавали?
    # - Какие данные собирали?
    # - Какие challenges были?
    # - Как их решили?

    questions = await ai_generate_questions(
        organization=org,
        similar_cases=similar_cases
    )

    return questions
```

---

## 🎯 Резюме: Последовательность интеграции

### ✅ ШАГ 1 (DONE): Temporal Cloud Setup
- [x] Account created
- [x] Namespace: `ai-platform-iso-22301.r3gxp`
- [x] Connection tested
- [x] Sample workflow executed

### 🚀 ШАГ 2 (NEXT): Workflow Intelligence Engine 

**НЕ параллельно! Строго последовательно:**

**Phase 2.1: Core Workflow Engine**
1. Определить BIA Workflow на Temporal
2. Реализовать Activities
3. State machine logic
4. Integration с PostgreSQL

**Phase 2.2: Case Library**
1. Models для хранения cases
2. Auto-collector для workflows
3. PostgreSQL storage
4. Qdrant integration (semantic search)
5. AI learning patterns

**Phase 2.3: Governance System**
1. Rules Engine
2. Checkpoints (governance approval points)
3. Creative Zones (AI autonomy)
4. Integration с workflows

**Phase 2.4: Production BIA Workflow**
1. Full BIA workflow tested
2. Running in Temporal Cloud
3. Case Library collecting data
4. Governance rules applied

### ШАГ 3: Platform Services Integration
- BIA Service → uses BIA Workflow
- Risk Service → uses Risk Workflow
- Planning Service → uses Planning Workflow

### ШАГ 4: Infrastructure 
- EventBus
- Monitoring
- Notifications

### ШАГ 5: UI 
- Web interface
- Integration с Temporal UI

---

## 📚 Ресурсы

**Temporal Docs:**
- Python SDK: https://docs.temporal.io/dev-guide/python
- Best Practices: https://docs.temporal.io/dev-guide/python/foundations
- Workflow Patterns: https://docs.temporal.io/encyclopedia/workflow-patterns

**Наша документация:**
- [CORRECT_SETUP_WITH_TEMPORAL.md](../../doc-project/CORRECT_SETUP_WITH_TEMPORAL.md)
- [арх2.md](../../doc-project/м/арх2.md)
- [README.md](README.md)

**Temporal Cloud:**
- Dashboard: https://cloud.temporal.io
- Namespace: `ai-platform-iso-22301.r3gxp`

---

**Последнее обновление:** 2025-10-06
**Статус:** ✅ Ready to start Phase 2 - Workflow Intelligence Engine
