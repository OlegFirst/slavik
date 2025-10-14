# Ответы на Ваши Вопросы

**Дата**: 2025-10-12
**Вопросы от пользователя:**
1. Почему всего 5 сценариев для шаблонов?
2. Где размещать генераторы и куда складываться сценарии?
3. Есть ли прямая интеграция в RAG и всю систему знаний?

---

## 1️⃣ Почему Всего 5 Шаблонов? (Обновлено!)

### Исходный Ответ
Изначально было **5 базовых шаблонов**, потому что:
- L1 разделён на 2: platform services vs user applications (разные типы тестов)
- L2, L3, L4 - по одному шаблону каждый

### 🆕 НО ТЕПЕРЬ У НАС 16 ШАБЛОНОВ!

```
БАЗОВЫЕ ШАБЛОНЫ (5):
├── golden_standard_l1.yaml                  ← 46 platform services
├── golden_standard_l1_application.yaml      ← 16 user applications
├── golden_standard_l2.yaml                  ← 12 subsystems
├── golden_standard_l3.yaml                  ← 19 systems (general fallback)
└── golden_standard_l4.yaml                  ← AI-generated workflows

СПЕЦИАЛИЗИРОВАННЫЕ L3 ШАБЛОНЫ (11):
├── l3_infrastructure_system.yaml            ✅ СОЗДАН
├── l3_reliability_system.yaml               🔄 TODO
├── l3_security_system.yaml                  🔄 TODO
├── l3_operations_system.yaml                🔄 TODO
├── l3_intelligence_system.yaml              🔄 TODO
├── l3_ai_system.yaml                        🔄 TODO
├── l3_business_system.yaml                  🔄 TODO
├── l3_orchestration_system.yaml             🔄 TODO
├── l3_quality_system.yaml                   🔄 TODO
├── l3_frontend_system.yaml                  🔄 TODO
└── l3_infrastructure_management_system.yaml 🔄 TODO

ИТОГО: 16 шаблонов (5 базовых + 11 специализированных)
```

### Зачем Специализированные Шаблоны?

**Проблема с generic template:**
```yaml
# Общий L3 template для ВСЕХ систем:
test_scenarios:
  - "End-to-End Functional Flow"       # Слишком общий!
  - "Business Process Validation"      # Не подходит для infrastructure!
  - "User Experience Validation"       # Не подходит для AI systems!
```

**Решение - специализация:**
```yaml
# Infrastructure template:
test_scenarios:
  - "Platform Startup Orchestration"   # Специфично!
  - "Service Dependency Resolution"
  - "Resource Provisioning"
  - "Disaster Recovery"

# Security template:
test_scenarios:
  - "Penetration Testing"              # Специфично!
  - "Threat Detection"
  - "Compliance Validation"
  - "Security Incident Simulation"

# AI template:
test_scenarios:
  - "AI Agent Coordination"            # Специфично!
  - "Decision Quality Validation"
  - "Hallucination Detection"
  - "AI Safety Controls"
```

### Логика Выбора Шаблона

```python
def select_template(system):
    """Smart template selection."""

    if system.level == 1:
        if system.type == "platform_service":
            return "golden_standard_l1.yaml"
        else:
            return "golden_standard_l1_application.yaml"

    elif system.level == 2:
        return "golden_standard_l2.yaml"

    elif system.level == 3:
        # ВАЖНО: Выбираем специализированный если есть!
        if system.category in SPECIALIZED_TEMPLATES:
            return f"l3_specialized/l3_{system.category}_system.yaml"
        else:
            return "golden_standard_l3.yaml"  # Fallback

    elif system.level == 4:
        return "golden_standard_l4.yaml"  # AI-generated
```

### Статистика

| Шаблоны | Количество | Сценариев/шаблон | Итого |
|---------|-----------|------------------|-------|
| L1 Base | 2 | 6-8 | 404 scenarios |
| L2 Base | 1 | 8 | 96 scenarios |
| L3 Base | 1 | 8 | Fallback |
| **L3 Specialized** | **11** | **8-10** | **152-190 scenarios** |
| L4 Base | 1 | 8 | Variable |
| **ИТОГО** | **16** | - | **652-690** |

---

## 2️⃣ Где Размещать Генераторы и Куда Складываться Сценарии?

### A. Генераторы (Service Code)

```
📍 LOCATION: /intelligent-core/scenario-intelligence/scenario-manager/

scenario-manager/
├── main.py                          ← FastAPI app, port 8050
│
├── generators/                      ← 🎯 ВОТ ГЕНЕРАТОРЫ
│   ├── __init__.py
│   ├── base_generator.py            ← Базовый класс
│   ├── l1_platform_generator.py     ← Генератор L1 services
│   ├── l1_application_generator.py  ← Генератор L1 apps
│   ├── l2_subsystem_generator.py    ← Генератор L2
│   ├── l3_system_generator.py       ← Генератор L3 (+ specialized)
│   └── l4_workflow_generator.py     ← Генератор L4 (AI-powered)
│
├── executor/
│   └── scenario_executor.py         ← Выполнение сценариев
│
├── rag/
│   └── embeddings.py                ← RAG интеграция
│
└── ...
```

**Почему здесь?**
- ✅ Вместе с Scenario Manager service
- ✅ Легко деплоить как единый Docker image
- ✅ Прямой доступ к templates/
- ✅ Прямой доступ к generated/

### B. Сгенерированные Сценарии (3 места!)

#### 🗄️ Место 1: PostgreSQL (Primary Storage)

```sql
-- ГЛАВНОЕ хранилище
scenario_intelligence.scenarios
├── id: UUID
├── level: 1|2|3|4
├── category: "infrastructure", "security", etc.
├── name: "l1-service-mio-manager"
├── content: JSONB  ← Полный YAML как JSON!
├── version: "1.0.0"
├── status: "active"
└── metadata: JSONB

-- Быстрые запросы:
SELECT * FROM scenario_intelligence.scenarios WHERE level = 1;
SELECT * FROM scenario_intelligence.scenarios WHERE category = 'security';
SELECT * FROM scenario_intelligence.scenarios WHERE status = 'active';
```

**Зачем:** CRUD операции, транзакции, версионирование

#### 📁 Место 2: File System (Human-Readable)

```
📍 LOCATION: /intelligent-core/scenario-intelligence/generated/

generated/
├── l1/
│   ├── services/
│   │   ├── mio-manager.yaml               ← Human-readable YAML!
│   │   ├── analytics-specialist.yaml
│   │   ├── project-agent.yaml
│   │   └── ... (46 files)
│   │
│   └── applications/
│       ├── bcm-portal.yaml
│       ├── simulation-platform.yaml
│       └── ... (16 files)
│
├── l2/
│   └── subsystems/
│       ├── database-infrastructure.yaml
│       ├── runtime-services.yaml
│       └── ... (12 files)
│
├── l3/
│   └── systems/
│       ├── startup-orchestration.yaml
│       ├── resilience-system.yaml
│       └── ... (19 files)
│
└── l4/
    └── workflows/
        ├── bcm-manager-onboarding.yaml
        ├── bia-creation-workflow.yaml
        └── ... (variable)
```

**Зачем:**
- ✅ Люди могут читать и редактировать
- ✅ Git version control
- ✅ Code review возможен
- ✅ Backup простой (просто файлы)

#### 🔍 Место 3: Qdrant (Semantic Search)

```python
# Vector embeddings для RAG
Qdrant Collection: "scenario_intelligence_scenarios"
├── Vector size: 1536 (OpenAI embeddings)
├── Distance: Cosine similarity
└── Records: 652+ scenarios

# Каждый scenario = vector + payload
{
    "id": "l1-service-mio-manager",
    "vector": [0.123, 0.456, ...],  # 1536 floats
    "payload": {
        "level": 1,
        "category": "service",
        "name": "MIO Manager Service Test",
        "systems": ["ai_office", "observatory"],
        "compliance": ["ISO 22301"],
        "created_at": "2025-10-12"
    }
}
```

**Зачем:** Semantic search, RAG queries, AI recommendations

### C. Workflow Генерации и Хранения

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Generator Creates Scenario                                │
│    - Reads template (YAML)                                   │
│    - Reads catalog (service/app/subsystem/system)            │
│    - Fills placeholders                                      │
│    - Validates structure                                     │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Save to File System (YAML)                                │
│    Path: generated/{level}/{category}/{name}.yaml            │
│    Format: Pretty-printed YAML with comments                 │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Save to PostgreSQL (JSON)                                 │
│    INSERT INTO scenario_intelligence.scenarios (...)         │
│    content = YAML converted to JSONB                         │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Create Embedding (OpenAI)                                 │
│    text = prepare_text(scenario)                             │
│    embedding = openai.create_embedding(text)                 │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Store in Qdrant (Vector)                                  │
│    qdrant.upsert(                                            │
│        collection="scenario_intelligence_scenarios",          │
│        points=[{id, vector, payload}]                        │
│    )                                                         │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Publish Event                                             │
│    eventbus.publish(                                         │
│        "scenario.{level}.generated",                         │
│        {scenario_id, name, ...}                              │
│    )                                                         │
└─────────────────────────────────────────────────────────────┘
```

### D. Пример Кода

```python
class L1ServiceGenerator:
    """Generate L1 scenarios for platform services."""

    def __init__(self):
        self.template = load_yaml("templates/golden_standard_l1.yaml")
        self.db = DatabaseClient()
        self.qdrant = QdrantClient()
        self.eventbus = EventBusClient()

    async def generate_all(self):
        """Generate scenarios for all 46 services."""

        # Read service catalog
        catalog = load_yaml("catalogs/SERVICE_CATALOG_DETAILED.yaml")

        for service in catalog["services"]:
            scenario = await self.generate_one(service)

            # 1. Save to file system
            filepath = f"generated/l1/services/{service['name']}.yaml"
            save_yaml(filepath, scenario)

            # 2. Save to PostgreSQL
            await self.db.insert("scenario_intelligence.scenarios", {
                "id": scenario["meta"]["id"],
                "level": 1,
                "category": "service",
                "name": scenario["meta"]["name"],
                "content": scenario,  # JSONB
                "version": scenario["meta"]["version"],
                "status": "active"
            })

            # 3. Create embedding
            text = self._prepare_text(scenario)
            embedding = await openai.create_embedding(text)

            # 4. Store in Qdrant
            await self.qdrant.upsert(
                collection_name="scenario_intelligence_scenarios",
                points=[{
                    "id": scenario["meta"]["id"],
                    "vector": embedding,
                    "payload": {
                        "level": 1,
                        "category": "service",
                        "name": service["name"],
                        "subsystem": service["subsystem"],
                        "criticality": service["criticality"]
                    }
                }]
            )

            # 5. Publish event
            await self.eventbus.publish("scenario.l1.generated", {
                "scenario_id": scenario["meta"]["id"],
                "name": scenario["meta"]["name"],
                "service": service["name"]
            })

    async def generate_one(self, service):
        """Generate scenario for one service."""

        scenario = deepcopy(self.template)

        # Fill placeholders
        scenario = self._fill_placeholders(scenario, {
            "service_name": service["name"],
            "port": service["port"],
            "criticality": service["criticality"],
            "subsystem_name": service["subsystem"],
            "internal_dependencies": service["dependencies"]["internal"],
            "external_dependencies": service["dependencies"]["external"]
        })

        return scenario
```

---

## 3️⃣ Есть Ли Прямая Интеграция в RAG и Систему Знаний?

### ДА! Полная Интеграция! 🎯

### A. RAG Integration (Qdrant)

```python
# 1. Scenarios AS Knowledge Base
class ScenarioRAG:
    """Scenarios as RAG knowledge base."""

    def search_similar(self, query: str):
        """Find similar scenarios."""
        embedding = openai.create_embedding(query)

        return qdrant.search(
            collection_name="scenario_intelligence_scenarios",
            query_vector=embedding,
            limit=10
        )

    def recommend_for_new_service(self, service_info):
        """Recommend scenarios for new service."""
        query = f"""
        {service_info.type} service
        Dependencies: {service_info.dependencies}
        Criticality: {service_info.criticality}
        """

        similar = self.search_similar(query)
        return [s.payload for s in similar]

    def learn_from_failures(self, failed_scenario):
        """Find similar failures and recommend fixes."""
        query = f"""
        Failure: {failed_scenario.error}
        System: {failed_scenario.system}
        """

        similar_failures = qdrant.search(
            collection_name="scenario_intelligence_executions",
            query_vector=openai.create_embedding(query),
            query_filter={"status": "failed"},
            limit=10
        )

        # Analyze patterns
        pattern = detect_pattern(similar_failures)
        recommendation = generate_recommendation(pattern)

        return recommendation
```

### B. Knowledge System Integration

```python
# Integration with /intelligent-core/ai-foundation/learning-knowledge/
from learning_knowledge import LearningKnowledgeAdapter

class ScenarioKnowledgeIntegration:
    """Integrate scenarios with platform knowledge system."""

    def __init__(self):
        self.learning = LearningKnowledgeAdapter()

    async def sync_to_knowledge_system(self, scenario):
        """Send scenario to learning system."""

        knowledge_item = {
            "type": "scenario",
            "id": scenario.id,
            "content": scenario,
            "category": "testing",
            "subcategory": f"level_{scenario.level}",
            "tags": [
                scenario.category,
                f"level-{scenario.level}",
                *scenario.systems_involved
            ],
            "metadata": {
                "quality_score": scenario.quality_score,
                "execution_count": scenario.execution_count,
                "success_rate": scenario.success_rate
            }
        }

        # Store in learning system
        await self.learning.store_knowledge(knowledge_item)

    async def get_knowledge_context(self, scenario_type):
        """Get knowledge context for scenario generation."""

        # Query learning system for relevant knowledge
        context = await self.learning.query_knowledge({
            "type": "scenario",
            "category": scenario_type,
            "include_related": True
        })

        return context
```

### C. Workflow Intelligence Integration

```python
# Integration with /intelligent-core/workflow_intelligence/
from temporalio import workflow

@workflow.defn
class ScenarioExecutionWorkflow:
    """Every scenario execution is a Temporal workflow."""

    @workflow.run
    async def run(self, scenario_id: str):
        """Execute scenario as workflow."""

        # 1. Load scenario (from knowledge base)
        scenario = await get_scenario_from_knowledge_base(scenario_id)

        # 2. Execute with workflow context
        result = await execute_scenario(scenario)

        # 3. Store result in knowledge base
        await store_execution_in_knowledge_base(result)

        # 4. If failed, trigger learning
        if result.status == "failed":
            await workflow.execute_child_workflow(
                LearningWorkflow,
                args=[result]
            )

        return result

# Fundamental scenarios auto-execute via workflows
FUNDAMENTAL_SCENARIOS = {
    "startup": {
        "scenario_id": "l3-startup-orchestration",
        "workflow": ScenarioExecutionWorkflow,
        "trigger": "platform_start",
        "knowledge_integration": True  # ← Stores in knowledge base
    },
    "resilience": {
        "scenario_id": "l3-resilience-self-healing",
        "workflow": ScenarioExecutionWorkflow,
        "trigger": "service_failure",
        "knowledge_integration": True
    }
}
```

### D. Knowledge Graph Integration

```python
# Optional: Neo4j knowledge graph
class ScenarioKnowledgeGraph:
    """Build knowledge graph of scenarios."""

    def build_graph(self):
        """Create nodes and relationships."""

        # Nodes
        - Scenario nodes (652+)
        - Service nodes (62)
        - System nodes (19)
        - Requirement nodes (ISO 22301 clauses)
        - Failure pattern nodes

        # Relationships
        - (Scenario)-[:TESTS]->(Service)
        - (Scenario)-[:DEPENDS_ON]->(Scenario)
        - (Scenario)-[:COVERS]->(Requirement)
        - (Scenario)-[:PART_OF]->(System)
        - (FailurePattern)-[:APPEARS_IN]->(Scenario)
        - (Service)-[:DEPENDS_ON]->(Service)

    def query_coverage(self, requirement):
        """Query which scenarios cover ISO requirement."""
        return cypher("""
            MATCH (s:Scenario)-[:COVERS]->(r:Requirement {name: $req})
            RETURN s
        """, req=requirement)

    def find_critical_path(self):
        """Find critical test path through scenarios."""
        return cypher("""
            MATCH path = (s1:Scenario)-[:DEPENDS_ON*]->(s2:Scenario)
            WHERE s1.level = 1 AND s2.level = 4
            RETURN path
            ORDER BY length(path) DESC
            LIMIT 1
        """)
```

### E. Full Integration Diagram

```
┌──────────────────────────────────────────────────────────┐
│                 SCENARIO INTELLIGENCE                     │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Scenarios (652+)                                    │  │
│  └────────────────────────────────────────────────────┘  │
│                         │                                 │
│         ┌───────────────┼───────────────┐                │
│         │               │               │                │
│         ▼               ▼               ▼                │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐            │
│  │PostgreSQL│   │Qdrant    │   │FileSystem│            │
│  │(CRUD)    │   │(RAG)     │   │(Human)   │            │
│  └──────────┘   └──────────┘   └──────────┘            │
└──────────────────────────────────────────────────────────┘
         │               │               │
         │               │               │
         ▼               ▼               ▼
┌──────────────────────────────────────────────────────────┐
│              KNOWLEDGE INTEGRATION LAYER                  │
│                                                           │
│  ┌─────────────────┐  ┌─────────────────┐               │
│  │ Learning System │  │ Workflow Intel  │               │
│  │ - Store results │  │ - Execute as    │               │
│  │ - Extract       │  │   workflows     │               │
│  │   patterns      │  │ - Temporal      │               │
│  └─────────────────┘  └─────────────────┘               │
│                                                           │
│  ┌─────────────────┐  ┌─────────────────┐               │
│  │ Knowledge Graph │  │ AI Foundation   │               │
│  │ - Relationships │  │ - RAG context   │               │
│  │ - Coverage map  │  │ - Embeddings    │               │
│  └─────────────────┘  └─────────────────┘               │
└──────────────────────────────────────────────────────────┘
         │               │               │
         │               │               │
         ▼               ▼               ▼
┌──────────────────────────────────────────────────────────┐
│                      CONSUMERS                            │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ AI Office    │  │ Simulation   │  │ New Services │  │
│  │ - MIO Manager│  │ - BCM        │  │ - Auto       │  │
│  │ - Analytics  │  │   exercises  │  │   recommend  │  │
│  │ - Predictive │  │ - Training   │  │   scenarios  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## 🎯 Итоговые Ответы

### Вопрос 1: Почему 5 шаблонов?
**Ответ:** Теперь **16 шаблонов**! (5 базовых + 11 специализированных L3)

### Вопрос 2: Где генераторы и куда складываться?
**Ответ:**
- **Генераторы**: `/scenario-manager/generators/` (5 generator классов)
- **Сценарии**: 3 места - PostgreSQL (primary), FileSystem (human), Qdrant (RAG)

### Вопрос 3: RAG и знания?
**Ответ:** **ДА!** Полная интеграция:
- ✅ Qdrant для semantic search
- ✅ Learning System для накопления знаний
- ✅ Workflow Intelligence для выполнения
- ✅ Knowledge Graph (опционально)
- ✅ AI Foundation для RAG context

---

## 📊 Summary Stats

| Аспект | Значение |
|--------|----------|
| **Шаблонов** | 16 (5 base + 11 specialized) |
| **Сценариев** | 652-690 (L1-L3) |
| **Хранилищ** | 3 (PostgreSQL, Qdrant, FileSystem) |
| **Интеграций** | 6 (RAG, Learning, Workflow, Graph, AI Office, Simulation) |
| **Генераторов** | 5 (L1×2, L2, L3, L4) |

---

**Статус**: ✅ Все вопросы отвечены с деталями и примерами кода!

