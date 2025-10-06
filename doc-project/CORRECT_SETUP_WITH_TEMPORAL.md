# 🚀 ПРАВИЛЬНЫЙ Алгоритм Настройки (с Temporal + Workflow Intelligence)

**Version:** 2.0 CORRECTED
**Date:** 2025-10-06
**Основано на:** `арх2.md` + Temporal Cloud

---

## ⚠️ ВАЖНОЕ ИСПРАВЛЕНИЕ

**Ошибка в предыдущем алгоритме:**
- ❌ Не учел главную концепцию из `арх2.md`: **Workflow Intelligence Engine + Case Library** - это ФУНДАМЕНТ
- ❌ Проигнорировал использование **Temporal Cloud** для workflow orchestration
- ❌ Начал с infrastructure, вместо того чтобы начать с **мозга платформы**

**Правильный подход (из `арх2.md`):**
> "Workflow Intelligence Engine - это мозг всей платформы. Без state machine и case library:
> - AI workers будут галлюцинировать
> - Нет контекстного понимания
> - Невозможно самообучение
> - Единственный компонент, который НЕЛЬЗЯ заменить позже"

---

## 🎯 ПРАВИЛЬНАЯ Архитектура (Dependency Order)

```
                   ┌─────────────────────────────────┐
                   │  Workflow Intelligence Engine   │ ← START HERE!
                   │  + Case Library                 │ ← FOUNDATION
                   │  (powered by Temporal Cloud)    │
                   └───────────────┬─────────────────┘
                                   │ provides context to
                   ┌───────────────▼─────────────────┐
                   │  Platform Services              │
                   │  (BIA, Risk, Planning, etc.)    │
                   └───────────────┬─────────────────┘
                                   │ use
                   ┌───────────────▼─────────────────┐
                   │  Infrastructure                 │
                   │  (Database, EventBus, etc.)     │
                   └─────────────────────────────────┘
```

**Правило:** Сначала строим МОЗГ (Workflow Intelligence), потом всё остальное!

---

## 📋 ИСПРАВЛЕННЫЙ Алгоритм

### Phase 0: Prerequisites (2-3 часа) ✅

**То же что и раньше, ПЛЮС:**

```bash
# Setup Temporal Cloud
# 1. Create account at https://cloud.temporal.io/get-started/profile/platform
# 2. Get credentials:
#    - Namespace
#    - Namespace ID
#    - Account ID
#    - gRPC Endpoint

# Add to .env
echo "TEMPORAL_NAMESPACE=your-namespace.xxxxx" >> .env
echo "TEMPORAL_NAMESPACE_ID=xxxxx" >> .env
echo "TEMPORAL_ACCOUNT_ID=xxxxx" >> .env
echo "TEMPORAL_GRPC_ENDPOINT=your-namespace.xxxxx.tmprl.cloud:7233" >> .env
echo "TEMPORAL_CLIENT_CERT_PATH=/path/to/client.pem" >> .env
echo "TEMPORAL_CLIENT_KEY_PATH=/path/to/client.key" >> .env
```

**Критерии успеха:**
- ✅ Temporal Cloud account создан
- ✅ Credentials получены
- ✅ `.env` настроен с Temporal credentials

---

### Phase 1: Foundation - Temporal + Basic Infrastructure (4-6 часов) ✅

**Цель:** Подключить Temporal Cloud и запустить минимальную инфраструктуру

#### 1.1 Setup Temporal Cloud Connection

```bash
cd intelligent-core/workflow_intelligence

# Install Temporal SDK
pip install temporalio

# Create Temporal client config
cat > temporal_config.py << 'EOF'
from temporalio.client import Client, TLSConfig
import os

async def get_temporal_client():
    """Connect to Temporal Cloud"""
    return await Client.connect(
        target_host=os.getenv("TEMPORAL_GRPC_ENDPOINT"),
        namespace=os.getenv("TEMPORAL_NAMESPACE"),
        tls=TLSConfig(
            client_cert=open(os.getenv("TEMPORAL_CLIENT_CERT_PATH"), "rb").read(),
            client_private_key=open(os.getenv("TEMPORAL_CLIENT_KEY_PATH"), "rb").read(),
        ),
    )

# Test connection
async def test_connection():
    client = await get_temporal_client()
    print(f"✅ Connected to Temporal: {client.identity}")
    return client
EOF

# Test connection
python -c "
import asyncio
from temporal_config import test_connection

asyncio.run(test_connection())
"
```

**Критерии успеха:**
- ✅ Temporal Cloud connection работает
- ✅ Client подключается к namespace

#### 1.2 Start Minimal Infrastructure

```bash
# Only what's absolutely necessary for Workflow Intelligence:

# 1. PostgreSQL (для Case Library)
docker-compose up -d postgres

# 2. Redis (для caching)
docker-compose up -d redis

# 3. Qdrant (для semantic search в Case Library)
cd infrastructure/vector-db
python test_connection.py
python qdrant/init_collections.py

# 4. Apply ONLY case library migrations
cd infrastructure/database
psql $DATABASE_URL -f migrations_source/case_library_schema.sql
```

**Критерии успеха:**
- ✅ PostgreSQL running
- ✅ Redis running
- ✅ Qdrant connected
- ✅ Case Library schema created

---

### Phase 2: CORE - Workflow Intelligence Engine (Week 1-2, 8-12 дней) ✅

**Цель:** Реализовать полноценный Workflow Intelligence Engine с Temporal

**Из `арх2.md`:**
> "Полная реализация включает:
> 1. Core Workflow Engine (3-4 дня)
> 2. Case Library (3-4 дня)
> 3. Governance System (2-3 дня)
> 4. BIA Workflow Definition (2-3 дня)"

#### 2.1 Core Workflow Engine на Temporal (3-4 дня)

```bash
cd intelligent-core/workflow_intelligence

# Create structure
mkdir -p core/{workflows,activities,state_machine}
mkdir -p case_library/{models,collector,repository,search}
mkdir -p governance/{rules,checkpoints,creative_zones}
mkdir -p definitions/{bia,risk,planning}
```

**Реализовать (согласно `арх2.md`):**

**Day 1-2: State Machine + Temporal Workflows**
```python
# core/workflows/bia_workflow.py
from temporalio import workflow
from datetime import timedelta

@workflow.defn
class BIAWorkflow:
    """
    BIA Workflow на Temporal Cloud

    Стадии (из арх2.md):
    1. Kickoff Meeting
    2. Data Collection
    3. Dependency Analysis
    4. Impact Assessment
    5. RTO/RPO Definition
    6. Validation
    7. Approval
    """

    @workflow.run
    async def run(self, organization_id: str) -> dict:
        # State machine для BIA процесса
        state = await workflow.execute_activity(
            initialize_bia_state,
            organization_id,
            start_to_close_timeout=timedelta(minutes=5)
        )

        # Kickoff Meeting
        state = await workflow.execute_activity(
            kickoff_meeting,
            state,
            start_to_close_timeout=timedelta(hours=2)
        )

        # Data Collection (AI-powered)
        state = await workflow.execute_activity(
            collect_data_with_ai,
            state,
            start_to_close_timeout=timedelta(days=7)
        )

        # ... остальные стадии

        # Publish case to Case Library
        await workflow.execute_activity(
            publish_to_case_library,
            state,
            start_to_close_timeout=timedelta(minutes=5)
        )

        return state
```

**Day 3-4: Activities + Validators**
```python
# core/activities/bia_activities.py
from temporalio import activity

@activity.defn
async def initialize_bia_state(organization_id: str) -> dict:
    """Initialize BIA state machine"""
    return {
        "organization_id": organization_id,
        "state": "initialized",
        "data": {},
        "validation_errors": [],
        "completed_actions": []
    }

@activity.defn
async def kickoff_meeting(state: dict) -> dict:
    """Kickoff meeting activity"""
    # Validation
    if not await validate_stakeholders(state):
        raise ValueError("Missing stakeholders")

    # Execute
    state["state"] = "kickoff_completed"
    state["data"]["meeting_minutes"] = await conduct_meeting(state)

    # Publish event
    await publish_event("bia.kickoff.completed", state)

    return state

@activity.defn
async def collect_data_with_ai(state: dict) -> dict:
    """AI-powered data collection"""
    # Get context from Case Library
    similar_cases = await search_case_library(state)

    # AI generates questions based on similar cases
    questions = await ai_generate_questions(state, similar_cases)

    # Collect responses
    responses = await collect_responses(questions)

    state["data"]["collected_data"] = responses
    state["state"] = "data_collected"

    return state
```

**Критерии успеха (Day 1-4):**
- ✅ BIA Workflow работает в Temporal Cloud
- ✅ Все стадии реализованы как Activities
- ✅ State transitions работают
- ✅ Validators проверяют данные
- ✅ Events публикуются на каждом шаге

---

#### 2.2 Case Library (3-4 дня)

**Day 5-6: Case Collection + Storage**
```python
# case_library/models.py
from sqlalchemy import Column, String, JSON, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class WorkflowCase(Base):
    """
    Хранение completed workflow cases для обучения

    Из арх2.md:
    - Auto-collect cases
    - PostgreSQL + Vector DB
    - AI анализ patterns
    - Semantic search
    """
    __tablename__ = "workflow_cases"

    id = Column(String, primary_key=True)
    workflow_type = Column(String)  # "bia", "risk", "planning"
    organization_id = Column(String)
    industry = Column(String)
    org_size = Column(String)

    # Workflow data
    initial_state = Column(JSON)
    final_state = Column(JSON)
    transitions = Column(JSON)  # All state transitions
    duration_days = Column(Integer)

    # Outcomes
    success = Column(Boolean)
    rto_achieved = Column(Boolean)
    rpo_achieved = Column(Boolean)

    # Learning data
    challenges = Column(JSON)  # What was difficult
    solutions = Column(JSON)   # How it was solved
    best_practices = Column(JSON)

    # Embedding for semantic search
    embedding = Column(JSON)  # 1536-dim vector

    created_at = Column(DateTime)


# case_library/collector.py
from temporalio import workflow

class CaseCollector:
    """
    Auto-collect cases from completed workflows

    Subscribes to:
    - workflow.completed events
    - workflow.failed events (to learn from failures!)
    """

    async def collect_from_workflow(self, workflow_run_id: str):
        # Get workflow history from Temporal
        history = await temporal_client.get_workflow_history(workflow_run_id)

        # Extract case data
        case = await self._extract_case_data(history)

        # AI analysis
        case.challenges = await ai_analyze_challenges(case)
        case.solutions = await ai_extract_solutions(case)
        case.best_practices = await ai_find_patterns(case)

        # Generate embedding
        case.embedding = await generate_embedding(case)

        # Store in PostgreSQL
        await db.save(case)

        # Store embedding in Qdrant
        await qdrant.upsert(
            collection="workflow_cases",
            vectors=[case.embedding],
            payloads=[case.to_dict()]
        )
```

**Day 7-8: Semantic Search + AI Analysis**
```python
# case_library/search.py
class CaseLibrarySearch:
    """
    Semantic search в Case Library

    Используется для:
    - AI context building (найти похожие cases)
    - Benchmarking (сравнить с индустрией)
    - Best practices recommendations
    """

    async def find_similar_cases(
        self,
        current_state: dict,
        filters: dict = None,
        limit: int = 5
    ) -> List[WorkflowCase]:
        """
        Найти похожие cases для AI context

        Filters:
        - industry
        - org_size
        - workflow_type
        - success=True (only successful cases)
        """
        # Generate embedding для текущего состояния
        query_embedding = await generate_embedding(current_state)

        # Search in Qdrant
        results = await qdrant.search(
            collection="workflow_cases",
            query_vector=query_embedding,
            limit=limit,
            filters=filters
        )

        # Load full cases from PostgreSQL
        cases = []
        for hit in results:
            case = await db.get(hit.payload["id"])
            case.similarity_score = hit.score
            cases.append(case)

        return cases

    async def get_benchmark_data(
        self,
        industry: str,
        org_size: str,
        workflow_type: str
    ) -> dict:
        """
        Get industry benchmarks

        Returns:
        - Average duration
        - Success rate
        - Common challenges
        - Best practices
        """
        cases = await db.query(
            workflow_type=workflow_type,
            industry=industry,
            org_size=org_size,
            success=True
        )

        return {
            "avg_duration_days": mean([c.duration_days for c in cases]),
            "success_rate": len([c for c in cases if c.success]) / len(cases),
            "common_challenges": ai_aggregate_challenges(cases),
            "best_practices": ai_aggregate_best_practices(cases)
        }
```

**Критерии успеха (Day 5-8):**
- ✅ Cases автоматически собираются после завершения workflow
- ✅ PostgreSQL schema для cases создана
- ✅ Qdrant используется для semantic search
- ✅ AI анализирует patterns из cases
- ✅ Benchmark calculator работает

---

#### 2.3 Governance System (2-3 дня)

**Day 9-10: Rules Engine + Checkpoints**
```python
# governance/rules_engine.py
class GovernanceRulesEngine:
    """
    Managed Autonomy для AI

    Из арх2.md:
    - Rules engine с YAML definitions
    - Checkpoints для критичных точек
    - Creative zones для AI свободы
    - Escalation logic
    """

    def __init__(self):
        self.rules = self._load_rules_from_yaml()
        self.checkpoints = self._load_checkpoints()
        self.creative_zones = self._load_creative_zones()

    async def validate_action(
        self,
        action: str,
        context: dict,
        state: str
    ) -> tuple[bool, str]:
        """
        Validate if AI can perform action

        Returns: (allowed, reason)
        """
        # Check if in creative zone
        if self._is_creative_zone(state, action):
            return (True, "Creative zone - AI has freedom")

        # Check rules
        for rule in self.rules.get(state, []):
            if not await rule.evaluate(context):
                return (False, f"Rule violation: {rule.description}")

        # Check checkpoint
        if self._is_checkpoint(state):
            if not await self._checkpoint_passed(context):
                return (False, "Checkpoint not passed - human review required")

        return (True, "Validated")

    async def escalate_to_human(
        self,
        issue: str,
        context: dict,
        urgency: str = "normal"
    ):
        """Escalate decision to human"""
        await notification_service.send(
            to=context["stakeholders"],
            subject=f"Decision required: {issue}",
            body=self._format_escalation(issue, context),
            urgency=urgency
        )

        # Pause workflow until human responds
        decision = await workflow.wait_for_signal("human_decision")
        return decision


# governance/bia_rules.yaml
bia_rules:
  kickoff_meeting:
    required_stakeholders:
      - Business Owner
      - IT Lead
      - BCM Coordinator

    checkpoints:
      - name: "Executive Approval"
        required: true
        escalate_if_fail: true

    creative_zones:
      - action: "suggest_additional_stakeholders"
        ai_freedom: true

  data_collection:
    required_data:
      - critical_functions
      - dependencies
      - peak_periods

    checkpoints:
      - name: "Data Completeness Check"
        required: true
        min_functions: 3

    creative_zones:
      - action: "generate_questions"
        ai_freedom: true
        constraints:
          - "Must be relevant to ISO 22301"
          - "Must not ask PII"

      - action: "suggest_dependencies"
        ai_freedom: true
        validation: "human_review"
```

**Day 11: Integration**
```python
# integration/ai_context_builder.py
class AIContextBuilder:
    """
    Build rich context для AI from Case Library

    Из арх2.md:
    - Построение контекста для AI
    - Reference real cases
    - Industry benchmarks
    - Best practices
    """

    async def build_context(
        self,
        current_state: dict,
        workflow_type: str
    ) -> dict:
        """
        Build AI context для текущего состояния workflow
        """
        # Find similar cases
        similar_cases = await case_library.find_similar_cases(
            current_state,
            filters={"workflow_type": workflow_type, "success": True},
            limit=5
        )

        # Get benchmarks
        benchmarks = await case_library.get_benchmark_data(
            industry=current_state["industry"],
            org_size=current_state["org_size"],
            workflow_type=workflow_type
        )

        # Get governance rules
        rules = governance.get_rules_for_state(current_state["state"])
        creative_zones = governance.get_creative_zones(current_state["state"])

        return {
            "current_state": current_state,
            "similar_cases": [
                {
                    "id": case.id,
                    "similarity": case.similarity_score,
                    "challenges": case.challenges,
                    "solutions": case.solutions,
                    "best_practices": case.best_practices
                }
                for case in similar_cases
            ],
            "benchmarks": benchmarks,
            "governance": {
                "rules": rules,
                "creative_zones": creative_zones,
                "checkpoints": governance.get_checkpoints(current_state["state"])
            },
            "recommendations": await ai_generate_recommendations(
                current_state,
                similar_cases,
                benchmarks
            )
        }
```

**Критерии успеха (Day 9-11):**
- ✅ Rules engine работает с YAML definitions
- ✅ Checkpoints блокируют workflow при необходимости
- ✅ Creative zones позволяют AI свободу
- ✅ Escalation logic уведомляет людей
- ✅ AI Context Builder предоставляет rich context

---

#### 2.4 BIA Workflow Definition (2-3 дня)

**Day 12-14: Complete YAML Definitions + Testing**

```yaml
# definitions/bia/bia_workflow.yaml
workflow:
  name: "Business Impact Analysis"
  type: "bia"
  version: "1.0"

  states:
    - id: "initialized"
      name: "Initialized"
      entry_actions:
        - create_workspace
        - notify_stakeholders

    - id: "kickoff_meeting"
      name: "Kickoff Meeting"
      required_data:
        - business_owner
        - it_lead
        - bcm_coordinator
      checkpoints:
        - executive_approval
      creative_zones:
        - suggest_additional_stakeholders
        - recommend_meeting_agenda

    - id: "data_collection"
      name: "Data Collection"
      ai_powered: true
      activities:
        - generate_questionnaire  # AI generates questions based on Case Library
        - collect_responses
        - validate_completeness
      validators:
        - min_critical_functions: 3
        - all_questions_answered: true
      creative_zones:
        - generate_questions
        - suggest_dependencies
        - identify_gaps

    - id: "dependency_analysis"
      name: "Dependency Analysis"
      ai_powered: true
      activities:
        - map_dependencies       # AI maps based on collected data + Case Library
        - identify_single_points_of_failure
        - calculate_impact
      checkpoints:
        - dependency_map_review  # Human reviews AI-generated map
      creative_zones:
        - suggest_dependencies
        - recommend_redundancy

    - id: "impact_assessment"
      name: "Impact Assessment"
      ai_powered: true
      activities:
        - assess_financial_impact
        - assess_operational_impact
        - assess_reputational_impact
      validators:
        - all_impacts_assessed: true
        - impact_values_reasonable: true

    - id: "rto_rpo_definition"
      name: "RTO/RPO Definition"
      ai_powered: true
      activities:
        - recommend_rto_rpo      # AI recommends based on benchmarks
        - validate_feasibility
        - get_stakeholder_approval
      checkpoints:
        - rto_rpo_approval      # Executive must approve

    - id: "validation"
      name: "Validation"
      activities:
        - validate_completeness
        - validate_consistency
        - validate_against_iso22301
      validators:
        - iso22301_compliant: true

    - id: "approval"
      name: "Approval"
      checkpoints:
        - executive_sign_off
      required_data:
        - approver_signature
        - approval_date

    - id: "completed"
      name: "Completed"
      exit_actions:
        - publish_to_case_library
        - generate_report
        - notify_stakeholders

  transitions:
    - from: "initialized"
      to: "kickoff_meeting"
      condition: "stakeholders_available"

    - from: "kickoff_meeting"
      to: "data_collection"
      condition: "executive_approval_received"

    - from: "data_collection"
      to: "dependency_analysis"
      condition: "data_complete"

    - from: "dependency_analysis"
      to: "impact_assessment"
      condition: "dependencies_mapped"

    - from: "impact_assessment"
      to: "rto_rpo_definition"
      condition: "impacts_assessed"

    - from: "rto_rpo_definition"
      to: "validation"
      condition: "rto_rpo_approved"

    - from: "validation"
      to: "approval"
      condition: "validation_passed"

    - from: "approval"
      to: "completed"
      condition: "executive_signed_off"

  governance:
    rules_file: "bia_rules.yaml"
    checkpoint_manager: "CheckpointManager"
    escalation_policy: "standard"
```

**Testing (Day 14):**
```bash
# Test complete BIA workflow
cd intelligent-core/workflow_intelligence

# Start Temporal worker
python -m workers.bia_worker

# Run test workflow
python tests/test_bia_workflow.py

# Expected:
# ✅ Workflow starts in Temporal Cloud
# ✅ All states transition correctly
# ✅ AI activities execute
# ✅ Checkpoints pause for human input
# ✅ Case collected at the end
# ✅ Semantic search works
```

**Критерии успеха (Day 12-14):**
- ✅ Complete BIA workflow definition (YAML)
- ✅ All states, transitions, validators defined
- ✅ Checkpoints and creative zones configured
- ✅ Integration with Temporal Cloud works
- ✅ End-to-end test passes
- ✅ Case automatically added to Case Library

---

### Phase 3: Platform Services Integration (Week 3, 5-7 дней) ✅

**Цель:** Интегрировать существующие platform services с Workflow Intelligence

#### 3.1 BIA Service Adapter (2 дня)

```python
# platform-services/bia-service/workflow_adapter.py
class BIAWorkflowAdapter:
    """
    Adapter между BIA Service и Workflow Intelligence

    Из арх2.md:
    - Использовать workflow engine
    - Публиковать события
    - Собирать cases
    - Предоставлять контекст AI
    """

    def __init__(self):
        self.temporal_client = get_temporal_client()
        self.workflow_intelligence = WorkflowIntelligenceClient()

    async def start_bia(self, organization_id: str) -> str:
        """Start BIA через Temporal Workflow"""
        # Start workflow in Temporal Cloud
        handle = await self.temporal_client.start_workflow(
            BIAWorkflow.run,
            organization_id,
            id=f"bia-{organization_id}-{uuid.uuid4()}",
            task_queue="bia-workflows"
        )

        return handle.id

    async def get_ai_context(self, workflow_id: str, state: str) -> dict:
        """Get AI context для текущего состояния"""
        # Get workflow state
        state_data = await self.get_workflow_state(workflow_id)

        # Build AI context from Case Library
        context = await self.workflow_intelligence.build_ai_context(
            state_data,
            workflow_type="bia"
        )

        return context

    async def signal_workflow(self, workflow_id: str, signal: str, data: dict):
        """Send signal to running workflow (e.g., human decision)"""
        handle = self.temporal_client.get_workflow_handle(workflow_id)
        await handle.signal(signal, data)


# Update existing BIA endpoints to use Workflow Intelligence
@router.post("/bia/start")
async def start_bia(organization_id: str):
    """Start BIA using Workflow Intelligence"""
    adapter = BIAWorkflowAdapter()
    workflow_id = await adapter.start_bia(organization_id)

    return {"workflow_id": workflow_id, "status": "started"}

@router.get("/bia/{workflow_id}/context")
async def get_context(workflow_id: str):
    """Get AI context для workflow"""
    adapter = BIAWorkflowAdapter()
    context = await adapter.get_ai_context(workflow_id, "current")

    return context
```

#### 3.2 Risk & Planning Service Adapters (3 дня)

**Аналогично BIA, создать:**
- Risk Assessment Workflow (YAML definition)
- Planning Workflow (YAML definition)
- Adapters для существующих services

#### 3.3 EventBus Integration (2 дня)

```python
# Publish workflow events to EventBus
@activity.defn
async def publish_event(event_type: str, data: dict):
    """Publish workflow event to EventBus"""
    await eventbus.publish(
        topic=event_type,
        data={
            "timestamp": datetime.utcnow().isoformat(),
            "workflow_id": data.get("workflow_id"),
            "state": data.get("state"),
            "organization_id": data.get("organization_id"),
            "data": data
        }
    )

# Subscribe to platform service events for Case Collection
class PlatformEventCollector:
    """Collect events from platform services для Case Library"""

    async def start(self):
        await eventbus.subscribe("bia.*", self.handle_bia_event)
        await eventbus.subscribe("risk.*", self.handle_risk_event)
        await eventbus.subscribe("planning.*", self.handle_planning_event)

    async def handle_bia_event(self, event):
        # Update Case Library with real-time data
        if event["type"] == "bia.completed":
            await case_library.collect_case(event["data"]["workflow_id"])
```

**Критерии успеха (Phase 3):**
- ✅ BIA Service использует Workflow Intelligence
- ✅ Risk & Planning services адаптированы
- ✅ EventBus integration работает
- ✅ Cases собираются автоматически
- ✅ AI context доступен для всех services

---

### Phase 4: Infrastructure Services (Week 4, 3-5 дней) ✅

**Теперь, когда МОЗГ работает, добавляем остальную infrastructure:**

```bash
# 1. Start EventBus
cd infrastructure/eventbus
python -m eventbus.main

# 2. Start API Gateway
cd infrastructure/security/api-gateway
uvicorn main:app --port 3001

# 3. Start Monitoring
cd infrastructure/monitoring
docker-compose up -d

# 4. Start remaining services
./infrastructure/scripts/start_platform_services.sh
```

**Критерии успеха:**
- ✅ Все infrastructure services работают
- ✅ Platform services подключены к Workflow Intelligence
- ✅ Monitoring собирает метрики
- ✅ Health checks green

---

### Phase 5: Human Interface (Week 5, 4-6 дней) ✅

```bash
# Web App с Temporal Cloud integration
cd human-interface/web-app

# Add Temporal workflow UI
npm install @temporalio/ui

# Configure
# .env.local
NEXT_PUBLIC_TEMPORAL_WEB_URL=https://cloud.temporal.io

# Start
npm run dev
```

**Features:**
- Workflow visualization (Temporal UI)
- Case Library browser
- AI context viewer
- Governance dashboard

**Критерии успеха:**
- ✅ Web App показывает running workflows
- ✅ Case Library доступна через UI
- ✅ AI recommendations видны
- ✅ Governance rules управляемы

---

## ⏱️ CORRECTED Timeline

| Phase | Task | Time | Cumulative |
|-------|------|------|------------|
| **Phase 0** | Prerequisites + Temporal Setup | 2-3h | 2-3h |
| **Phase 1** | Temporal Connection + Basic Infra | 4-6h | 6-9h |
| **Phase 2** | **Workflow Intelligence Engine** | **8-12 дней** | **8-12 дней** |
|  | - Core Workflow Engine | 3-4 дня | |
|  | - Case Library | 3-4 дня | |
|  | - Governance System | 2-3 дня | |
|  | - BIA Workflow Definition | 2-3 дня | |
| **Phase 3** | Platform Services Integration | 5-7 дней | 13-19 дней |
| **Phase 4** | Infrastructure Services | 3-5 дней | 16-24 дней |
| **Phase 5** | Human Interface | 4-6 дней | 20-30 дней |
| **TOTAL** | | **20-30 дней** | **4-6 недель** |

---

## 🎯 Почему этот порядок ПРАВИЛЬНЫЙ

**Из `арх2.md`:**

> "Workflow Intelligence Engine - это мозг всей платформы. Определяет как работают ВСЕ остальные компоненты:
> - BIA service → использует workflow engine
> - Risk service → использует workflow engine
> - AI advisors → используют case library
> - ML predictor → тренируется на cases
>
> Единственный компонент, который НЕЛЬЗЯ заменить позже."

**Что получаем:**
- ✅ AI не галлюцинирует - знает контекст из Case Library
- ✅ Платформа учится - каждый case → знания
- ✅ Managed autonomy - творчество в рамках governance
- ✅ Масштабируемо - тот же engine для всех modules
- ✅ Production-ready - Temporal Cloud + governance + audit trail
- ✅ Уникальное преимущество - нет аналогов на рынке

---

## 📚 Дополнительные ресурсы

**Temporal Cloud:**
- Dashboard: https://cloud.temporal.io
- Docs: https://docs.temporal.io
- SDK: https://github.com/temporalio/sdk-python

**Архитектура:**
- `арх2.md` - Оригинальная концепция
- `FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md` - Полная спецификация

---

## ✅ Success Criteria

**Workflow Intelligence работает если:**
1. ✅ BIA workflow запускается в Temporal Cloud
2. ✅ AI получает context из Case Library
3. ✅ Governance rules контролируют AI
4. ✅ Cases автоматически собираются
5. ✅ Semantic search находит похожие cases
6. ✅ Benchmarks показывают industry data
7. ✅ Platform services используют Workflow Intelligence

---

**Last Updated:** 2025-10-06
**Version:** 2.0 CORRECTED
**Основано на:** `арх2.md` + Temporal Cloud ✅
