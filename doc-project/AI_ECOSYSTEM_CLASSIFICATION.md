# AI ECOSYSTEM - КЛАССИФИКАЦИЯ КОМПОНЕНТОВ

**Дата:** 2025-10-05
**Цель:** Определить КТО КУДА относится в архитектуре AI экосистемы

---

## АРХИТЕКТУРНЫЕ СЛОИ (Functional Roles)

Напомню 6 функциональных ролей из нашей архитектурной дискуссии:

1. **Orchestrators** (Decision Makers) - Принимают решения на уровне платформы
2. **Workers** (Task Executors) - Выполняют конкретные задачи
3. **LLM Integrations** (Embedded Intelligence) - Встроенный интеллект
4. **Domain Specialists** (BCM Experts) - Специалисты домена
5. **Interface AI** (User-Facing) - Взаимодействие с пользователем
6. **System AI** (Platform Maintainers) - Обслуживание платформы

---

## КЛАССИФИКАЦИЯ AI OFFICE КОМПОНЕНТОВ

### КАТЕГОРИЯ 1: DOMAIN SPECIALISTS (AI Colleagues)

**Локация:** `/intelligent-core/ai-office/ВСМ-colleagues/`

**Роль в экосистеме:** User-facing AI консультанты по BCM домену

**Компоненты:**

| Colleague | Строк | Статус | Functional Role |
|-----------|-------|--------|-----------------|
| **Compliance Copilot** | 275 | ⭐⭐⭐⭐⭐ Production | Domain Specialist (ISO 22301) |
| **BIA Specialist** | 377 | ⭐⭐⭐⭐⭐ Production | Domain Specialist (BIA) |
| **Risk Analyst** | 320 | ⭐⭐⭐⭐⭐ Production | Domain Specialist (Risk/FAIR) |
| **Project Manager** | 423 | ⭐⭐⭐⭐⭐ Production | Domain Specialist (Projects) |
| **Plan Generator** | 53 | ⭐⭐⭐ Minimal | Domain Specialist (Plans) - НУЖНО РАСШИРИТЬ |
| **Incident Advisor** | 53 | ⭐⭐⭐ Minimal | Domain Specialist (Incidents) - НУЖНО РАСШИРИТЬ |
| **Exercise Designer** | 53 | ⭐⭐⭐ Minimal | Domain Specialist (Exercises) - НУЖНО РАСШИРИТЬ |

**Характеристики:**
- Наследуют `BaseAIColleague`
- Используют RAG Pipeline для консультаций
- User-facing (через Chat/Web UI)
- Дают qualitative insights
- НЕ выполняют тяжелые вычисления сами

**Куда относятся:**
```
Layer 2: INTELLIGENT AGENTS (Domain Specialists)
└─ ВСМ-colleagues/ - AI Consultants
   ├─ Compliance Copilot
   ├─ BIA Specialist
   ├─ Risk Analyst
   ├─ Project Manager AI
   ├─ Plan Generator AI
   ├─ Incident Advisor AI
   └─ Exercise Designer AI
```

---

### КАТЕГОРИЯ 2: WORKERS (AI Organs)

**Локация:** `/intelligent-core/ai-office/organs/`

**Роль в экосистеме:** Execution workers (выполняют конкретные задачи)

**Компоненты:**

| Organ | Строк | Роль | Functional Role |
|-------|-------|------|-----------------|
| **Compliance Guardian** | ~250 | Compliance checks executor | Worker (Compliance) |
| **Emergency Response** | ~230 | Emergency response executor | Worker (Incidents) |
| **Governance Brain** | ~155 | Governance decisions | Worker (Governance) |
| **Impact Oracle** | ~190 | Impact calculations | Worker (BIA) |
| **Learning Coach** | ~295 | Learning optimization | Worker (Learning) |
| **Lifecycle Monitor** | ~320 | Lifecycle tracking | Worker (Monitoring) |
| **Performance Analyst** | ~280 | Performance analysis | Worker (Analytics) |
| **Plan Generator** | ~310 | Plan document generation | Worker (Plans) - ⚠️ ДУБЛЬ! |
| **Risk Advisor** | ~165 | Risk treatment advice | Worker (Risk) |
| **Scenario Creator** | ~255 | Scenario generation | Worker (Exercises) |

**Характеристики:**
- Наследуют `BaseOrgan` (предположительно)
- Выполняют конкретные задачи (calculations, generation, analysis)
- НЕ user-facing
- Используются Colleagues как tools

**Куда относятся:**
```
Layer 3: WORKERS (Execution Engines)
└─ organs/ - AI Organs (Task Executors)
   ├─ Compliance Guardian (compliance checks)
   ├─ Emergency Response (incident handling)
   ├─ Governance Brain (governance decisions)
   ├─ Impact Oracle (BIA calculations)
   ├─ Learning Coach (learning optimization)
   ├─ Lifecycle Monitor (tracking)
   ├─ Performance Analyst (analytics)
   ├─ Plan Generator (document generation) ⚠️ ДУБЛЬ
   ├─ Risk Advisor (risk treatment)
   └─ Scenario Creator (exercise scenarios)
```

**⚠️ ПРОБЛЕМА: Дубль Plan Generator**
- Colleague: Plan Generator AI (53 строки, minimal)
- Organ: Plan Generator (310 строк, rich)

**Решение:**
- **Colleague** → переименовать в "Plan Strategy AI" (консультирует ЧТО планировать)
- **Organ** → оставить "Plan Document Generator" (ГЕНЕРИРУЕТ actual documents)
- Colleague использует Organ как tool

---

### КАТЕГОРИЯ 3: SYSTEM COMPONENTS (Core Infrastructure)

**Локация:** `/intelligent-core/ai-office/core/`

**Роль в экосистеме:** Core system services (infrastructure)

**Компоненты:**

| Component | Локация | Роль | Functional Role |
|-----------|---------|------|-----------------|
| **RAG Pipeline** | `core/rag/rag_pipeline.py` | Query → Context → LLM → Answer | LLM Integration |
| **Intent Analyzer** | `core/intent/intent_analyzer.py` | Intent detection & routing | System AI |
| **Context Retriever** | `core/rag/context_retriever.py` | BCM module context fetch | System AI |
| **Anthropic Adapter** | `core/adapters/anthropic_adapter.py` | Claude API integration | LLM Integration |
| **Meta Learning Engine** | `core/learning/meta_learning_engine.py` | Platform learning | System AI |
| **Predictive Analytics** | `core/learning/predictive_analytics.py` | Analytics & predictions | System AI |

**Куда относятся:**
```
Layer 1: INTELLIGENCE INFRASTRUCTURE (Core Systems)
└─ core/ - System Components
   ├─ RAG Pipeline (LLM Integration)
   ├─ Intent Analyzer (System AI)
   ├─ Context Retriever (System AI)
   ├─ Anthropic Adapter (LLM Integration)
   ├─ Meta Learning Engine (System AI)
   └─ Predictive Analytics (System AI)
```

---

### КАТЕГОРИЯ 4: COORDINATION (Orchestrators)

**Локация:** `/intelligent-core/ai-office/coordinator/`

**Роль в экосистеме:** Routing & orchestration

**Компоненты:**

| Component | Роль | Functional Role |
|-----------|------|-----------------|
| **Colleague Coordinator** | Routes queries to appropriate AI Colleague | Orchestrator |

**Куда относится:**
```
Layer 2: COORDINATION & ROUTING
└─ coordinator/ - Orchestration
   └─ Colleague Coordinator (routes user queries)
```

---

### КАТЕГОРИЯ 5: BACKEND SERVICES (Execution Engines)

**Локация:** `/intelligent-core/ai-office/ВСМ-colleagues/project-intelligence/`

**Роль в экосистеме:** Specialized backend microservices

**Компоненты:**

| Service | Port | Роль | Functional Role |
|---------|------|------|-----------------|
| **Project Intelligence Service** | 8025 | BCM project management engine | Worker (specialized) |

**Характеристики:**
- FastAPI микросервис (standalone)
- Quantitative analysis (health score, assignment, prediction)
- Learning from patterns
- REST API
- НЕ user-facing напрямую
- Используется Project Manager AI Colleague

**Куда относится:**
```
Layer 3: SPECIALIZED WORKERS (Backend Engines)
└─ Backend Services
   └─ Project Intelligence Service
      - Health monitoring
      - Smart assignment
      - Deadline prediction
      - Pattern learning
```

**Integration Pattern:**
```
User → Project Manager AI (Colleague)
         ├→ Project Intelligence Service (quantitative)
         └→ RAG Pipeline (qualitative)
```

---

### КАТЕГОРИЯ 6: SUPPORT SERVICES (Infrastructure)

**Локация:** `/intelligent-core/ai-office/mio-manager/`

**Роль в экосистеме:** MIO (Monitoring, Improvement, Oversight) management

**Компоненты:**

| Service | Роль | Functional Role |
|---------|------|-----------------|
| **MIO Manager** | MIO workflow management | Worker (specialized) ИЛИ Orchestrator? |

**Статус:** ❓ Требуется детальный анализ

**Предполагаемая роль:**
- Workflow management для MIO процессов
- Scheduler для continuous monitoring
- Integration points с другими модулями

**Куда относится (предварительно):**
```
Layer 3: SPECIALIZED WORKERS OR Layer 2: ORCHESTRATORS
└─ Support Services
   └─ MIO Manager (нужен анализ)
```

---

### КАТЕГОРИЯ 7: LEGACY / ODOO MODULES

**Локация:** `/intelligent-core/ai-office/`

**Статус:** ⚠️ Unclear - deprecate, migrate, или integrate?

**Компоненты:**

| Component | Тип | Размер | Решение |
|-----------|-----|--------|---------|
| **ai-consultant/** | Odoo module | ~2000 строк | **ARCHIVE** (заменен Compliance Copilot) |
| **bcm_ai_consultant/** | Odoo module | ~2000 строк | **ARCHIVE** (заменен Compliance Copilot) |
| **bcm_ai_control/** | Odoo mega-module | ~4000 строк | **ANALYZE** (может содержать Organs coordinator) |
| **EXTRACTED_FROM_ODOO/** | Patterns & references | Mixed | **REFERENCE** → потом archive |

**Куда относятся:**
```
_archive/odoo_modules/ (после анализа bcm_ai_control/)
├─ ai-consultant/
├─ bcm_ai_consultant/
└─ EXTRACTED_FROM_ODOO/ (reference materials)

KEEP (если нужно):
bcm_ai_control/models/ai_organ_coordinator.py → извлечь в core/
```

---

### КАТЕГОРИЯ 8: TOOLS (NOT Part of AI Ecosystem)

**Локация:** `/intelligent-core/ai-office/project-agent/`

**Роль:** Universal CLI tool для code analysis

**Характеристики:**
- НЕ относится к BCM project management
- Generic code analysis (security, testing, quality)
- Supports BCM через ISO 22301 compliance module
- Completely separate от AI Office экосистемы

**Куда относится:**
```
/tools/code-agent/ (переместить из ai-office/)
ИЛИ
/intelligent-core/ai-office/project-agent/ (но документировать как separate tool)
```

**НЕ входит в AI экосистему!**

---

## ФИНАЛЬНАЯ АРХИТЕКТУРА AI OFFICE

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 4: USER INTERFACE                                        │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│ │ Web UI       │  │ Chat Bot     │  │ Mobile App   │          │
│ └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└────────┼──────────────────┼──────────────────┼─────────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 3: COORDINATION & ROUTING (Orchestrators)                │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ Colleague Coordinator                                         ││
│ │ - Auto-routes queries to appropriate AI Colleague            ││
│ │ - Cross-colleague workflows                                   ││
│ └──────────────────────┬───────────────────────────────────────┘│
└────────────────────────┼─────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: DOMAIN SPECIALISTS (AI Colleagues)                    │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│ │Compliance │ │    BIA     │ │   Risk     │ │  Project   │   │
│ │ Copilot   │ │ Specialist │ │  Analyst   │ │  Manager   │   │
│ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘   │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐                   │
│ │   Plan     │ │  Incident  │ │ Exercise   │                   │
│ │ Strategy   │ │  Advisor   │ │ Designer   │                   │
│ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘                   │
└───────┼──────────────┼──────────────┼───────────────────────────┘
        │              │              │
        │ Use RAG      │ Use Organs   │ Use Services
        ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: INTELLIGENCE INFRASTRUCTURE (Core Systems)            │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ RAG Pipeline (LLM Integration)                                ││
│ │ ├─ Intent Analyzer                                           ││
│ │ ├─ Context Retriever                                         ││
│ │ ├─ Anthropic Adapter                                         ││
│ │ └─ Response Builder                                          ││
│ └──────────────────────────────────────────────────────────────┘│
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ Learning & Analytics                                          ││
│ │ ├─ Meta Learning Engine                                      ││
│ │ └─ Predictive Analytics                                       ││
│ └──────────────────────────────────────────────────────────────┘│
└────────────────────────┬──────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 0: WORKERS & SERVICES (Execution Engines)                │
│                                                                   │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ AI ORGANS (Workers)                                          │ │
│ │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │ │
│ │ │Complian│ │Emergency│ │Governan│ │Impact  │           │ │
│ │ │ce Guard│ │Response │ │ce Brain│ │Oracle  │           │ │
│ │ └─────────┘ └─────────┘ └─────────┘ └─────────┘           │ │
│ │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │ │
│ │ │Learning│ │Lifecycl│ │Performa│ │Plan Doc│           │ │
│ │ │Coach   │ │e Monit.│ │nce Anal│ │Generat.│           │ │
│ │ └─────────┘ └─────────┘ └─────────┘ └─────────┘           │ │
│ │ ┌─────────┐ ┌─────────┐                                    │ │
│ │ │Risk    │ │Scenario│                                    │ │
│ │ │Advisor │ │Creator │                                    │ │
│ │ └─────────┘ └─────────┘                                    │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ BACKEND SERVICES (Specialized Workers)                       │ │
│ │ ┌──────────────────────────────────────────────────────────┐│ │
│ │ │ Project Intelligence Service (Port 8025)                  ││ │
│ │ │ - Health monitoring                                       ││ │
│ │ │ - Smart assignment                                        ││ │
│ │ │ - Deadline prediction                                     ││ │
│ │ └──────────────────────────────────────────────────────────┘│ │
│ │ ┌──────────────────────────────────────────────────────────┐│ │
│ │ │ MIO Manager (TBD - needs analysis)                        ││ │
│ │ └──────────────────────────────────────────────────────────┘│ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## INTEGRATION PATTERNS

### Pattern 1: Colleague → Organ (Direct)

```python
class BIASpecialistAI(BaseAIColleague):
    def __init__(self, rag_pipeline, impact_oracle: ImpactOracle):
        self.rag = rag_pipeline
        self.impact_oracle = impact_oracle  # AI Organ as tool

    async def calculate_impact_over_time(self, process_data):
        # 1. RAG для high-level strategy
        strategy = await self.rag.process_query(
            "What impact assessment approach for this process?"
        )

        # 2. Organ для execution (calculations)
        impact_curve = await self.impact_oracle.calculate(process_data)

        # 3. Synthesize
        return {
            "strategy": strategy.content,
            "calculations": impact_curve,
            "recommendations": strategy.actions
        }
```

---

### Pattern 2: Colleague → Service → Organ (Layered)

```python
class ProjectManagerAI(BaseAIColleague):
    def __init__(self, rag_pipeline, project_intelligence_url):
        self.rag = rag_pipeline
        self.project_service = ProjectIntelligenceClient(project_intelligence_url)

    async def analyze_project_health(self, project_data, tenant_id):
        # 1. Service для quantitative analysis
        metrics = await self.project_service.analyze_project(project_data)
        # Service internally может использовать Organs

        # 2. RAG для qualitative insights
        rag_result = await self.rag.process_query(
            f"Project metrics: {metrics}. Provide insights."
        )

        # 3. Combine
        return {
            "metrics": metrics,  # From service
            "insights": rag_result.content,  # From RAG
            "recommendations": rag_result.actions
        }
```

---

### Pattern 3: Coordinator → Colleague (Routing)

```python
class ColleagueCoordinator:
    def __init__(self, colleagues: Dict[str, BaseAIColleague]):
        self.colleagues = colleagues
        self.intent_analyzer = IntentAnalyzer()

    async def route_query(self, user_query, context):
        # 1. Analyze intent
        intent = self.intent_analyzer.analyze(user_query)

        # 2. Route to appropriate colleague
        if intent.intent_type == "analyze_risk":
            colleague = self.colleagues["risk_analyst"]
        elif intent.intent_type == "analyze_bia":
            colleague = self.colleagues["bia_specialist"]
        elif intent.intent_type == "query_compliance":
            colleague = self.colleagues["compliance_copilot"]
        # ...

        # 3. Process through colleague
        return await colleague.process_message(user_query, context)
```

---

## ДЕЙСТВИЯ ПО КОМПОНЕНТАМ

### НЕМЕДЛЕННО (Critical Path)

#### 1. Clarify AI Organs Integration ⚠️ CRITICAL
**Проблема:** Organs существуют, но unclear как используются

**Действия:**
1. Read `bcm_ai_control/models/ai_organ_coordinator.py` (может быть ключ)
2. Read `organs/base_organ.py` (понять interface)
3. Определить pattern: Direct (Colleague → Organ) или Layered (Colleague → Service → Organ)
4. Document integration в каждом Colleague

**Effort:** 4-6 часов
**Приоритет:** 🔥 КРИТИЧНО

---

#### 2. Resolve Plan Generator Дубль ⚠️ URGENT
**Проблема:** Plan Generator в 2 местах (Colleague 53 строки vs Organ 310 строк)

**Действия:**
1. Rename Colleague: `Plan Generator AI` → `Plan Strategy AI`
2. Keep Organ: `Plan Generator` → `Plan Document Generator`
3. Implement integration:
   ```python
   class PlanStrategyAI(BaseAIColleague):
       def __init__(self, rag, plan_generator_organ):
           self.plan_doc_generator = plan_generator_organ

       async def generate_plan(self, strategy_data):
           # RAG: ЧТО планировать (strategy)
           strategy = await self.rag.process_query(...)

           # Organ: КАК генерировать (execution)
           document = await self.plan_doc_generator.generate(strategy)

           return {"strategy": strategy, "document": document}
   ```

**Effort:** 2-3 часа
**Приоритет:** 🔥 URGENT

---

#### 3. Implement Project Manager ↔ Project Intelligence Integration
**Проблема:** Упоминается integration, но не реализовано

**Действия:**
1. Create `ProjectIntelligenceClient` (HTTP client)
2. Inject в `ProjectManagerAI.__init__()`
3. Update методы для combined analysis (quantitative + qualitative)

**Effort:** 1-2 дня
**Приоритет:** 🔥 HIGH

---

#### 4. Archive Odoo Modules (после анализа bcm_ai_control)
**Действия:**
1. Read `bcm_ai_control/models/ai_organ_coordinator.py`
2. Если полезно → extract в `core/organ_coordinator.py`
3. Archive остальное:
   ```bash
   mkdir -p _archive/odoo_modules
   mv ai-consultant/ _archive/odoo_modules/
   mv bcm_ai_consultant/ _archive/odoo_modules/
   mv bcm_ai_control/ _archive/odoo_modules/  # После extraction
   mv EXTRACTED_FROM_ODOO/ _archive/reference_materials/
   ```

**Effort:** 4-6 часов
**Приоритет:** MEDIUM

---

#### 5. Move/Rename Project Agent
**Действия:**
Опция A (рекомендуется):
```bash
mv intelligent-core/ai-office/project-agent/ tools/code-analysis-agent/
```

Опция B:
```bash
# Keep location, но добавить README:
echo "⚠️ NOT part of BCM AI ecosystem. Universal code analysis CLI." > project-agent/README_WARNING.md
```

**Effort:** 1 час
**Приоритет:** LOW (но важно для clarity)

---

### КРАТКОСРОЧНО (1-2 недели)

#### 6. Expand Minimal Colleagues
**Компоненты:** Plan Strategy AI, Incident Advisor, Exercise Designer

**Действия:** Довести до уровня Compliance/BIA/Risk (300+ строк, unique методы)

**Effort:** 1-2 дня на каждого = 3-6 дней
**Приоритет:** MEDIUM

---

#### 7. Implement EventBus Integration
**Для:** Colleagues, Organs, Services

**Действия:**
1. BaseAIColleague: publish events (`colleague_consulted`, `action_suggested`)
2. BaseOrgan: publish events (`task_executed`, `result_computed`)
3. Services: publish events (`project_analyzed`, `assignment_suggested`)

**Effort:** 2-3 дня
**Приоритет:** HIGH (для Experiment Lab)

---

#### 8. Analyze MIO Manager
**Действия:**
1. Read MIO Manager code
2. Determine role: Orchestrator или Worker?
3. Document integration points
4. Classify в architecture

**Effort:** 1 день
**Приоритет:** MEDIUM

---

## ИТОГОВАЯ ТАБЛИЦА КЛАССИФИКАЦИИ

| Компонент | Категория | Layer | Functional Role | Действие |
|-----------|-----------|-------|-----------------|----------|
| **Compliance Copilot** | Domain Specialist | 2 | Interface AI | ✅ Keep as is |
| **BIA Specialist** | Domain Specialist | 2 | Interface AI | ✅ Keep as is |
| **Risk Analyst** | Domain Specialist | 2 | Interface AI | ✅ Keep as is |
| **Project Manager AI** | Domain Specialist | 2 | Interface AI | ⚠️ Add service integration |
| **Plan Generator AI** | Domain Specialist | 2 | Interface AI | ⚠️ Rename to "Plan Strategy AI" |
| **Incident Advisor** | Domain Specialist | 2 | Interface AI | ⚠️ Expand (minimal) |
| **Exercise Designer** | Domain Specialist | 2 | Interface AI | ⚠️ Expand (minimal) |
| **10 AI Organs** | Workers | 0 | Workers | ⚠️ Clarify integration pattern |
| **Project Intelligence** | Backend Service | 0 | Worker (specialized) | ⚠️ Add DB, EventBus |
| **MIO Manager** | ? | ? | ? | ❓ Needs analysis |
| **RAG Pipeline** | Core System | 1 | LLM Integration | ✅ Keep as is |
| **Intent Analyzer** | Core System | 1 | System AI | ✅ Keep as is |
| **Colleague Coordinator** | Orchestrator | 3 | Orchestrator | ✅ Keep as is |
| **ai-consultant** | Legacy | Archive | - | 🗑️ Archive |
| **bcm_ai_consultant** | Legacy | Archive | - | 🗑️ Archive |
| **bcm_ai_control** | Legacy | Archive | - | ⚠️ Extract organ_coordinator first |
| **Project Agent** | Tool | Outside | - | 📦 Move to tools/ |

---

## ПРИОРИТИЗИРОВАННЫЙ ПЛАН ДЕЙСТВИЙ

### ФАЗА 1: КРИТИЧНЫЕ ПРОБЛЕМЫ (1 неделя)
1. ✅ Read AI Organs + organ_coordinator (понять integration) - 6 часов
2. ✅ Resolve Plan Generator дубль (rename + integrate) - 3 часа
3. ✅ Implement Project Manager ↔ Service integration - 2 дня
4. ✅ Archive Odoo modules (после extraction) - 6 часов

### ФАЗА 2: УЛУЧШЕНИЯ (2 недели)
5. ✅ Expand minimal colleagues (Plan/Incident/Exercise) - 6 дней
6. ✅ Implement EventBus integration - 3 дня
7. ✅ Analyze MIO Manager - 1 день
8. ✅ Move Project Agent to tools/ - 1 час

### ФАЗА 3: ОПТИМИЗАЦИЯ (1 месяц)
9. Add PostgreSQL to Project Intelligence
10. Add testing suite
11. Performance optimization
12. Documentation

---

**Итого:** ВСЕ компоненты классифицированы, план действий готов! 🎯
