# АРХИТЕКТУРНОЕ РАСПРЕДЕЛЕНИЕ КОМПОНЕНТОВ

**Дата**: 2025-10-06
**Вопрос**: Где должны быть ai_experts, ai-office, platform-services в Variant 5?
**Статус**: Детальный план распределения

---

## 🎯 ТЕКУЩАЯ СИТУАЦИЯ

### Что у нас есть:

```
/intelligent-core/ai_experts/          # AI-инструменты (RAG, ML, Learning, Tools)
├─ rag/                                # 1,368 LOC
├─ ml/                                 # 1,127 LOC
├─ learning/                           # 619 LOC
├─ tools/                              # 2,747 LOC
├─ specialists/                        # 3 специалиста
│  ├─ bcm_advisor.py
│  ├─ compliance_auditor.py
│  └─ strategic_planner.py
└─ knowledge/                          # Знания

/intelligent-core/ai-office/           # BCM AI офис
├─ ВСМ-colleagues/                     # 10 colleagues (специалисты BCM)
│  ├─ bia_specialist/
│  ├─ risk_analyst/
│  ├─ project_manager/
│  ├─ incident_advisor/
│  ├─ plan_generator/
│  ├─ compliance_copilot/
│  ├─ exercise_designer/
│  └─ ...
├─ organs/                             # 10 organs (тяжелые AI анализаторы)
│  ├─ governance_brain.py
│  ├─ impact_oracle.py
│  ├─ risk_advisor.py
│  ├─ compliance_guardian.py
│  ├─ emergency_response.py
│  ├─ scenario_creator.py
│  ├─ performance_analyst.py
│  ├─ learning_coach.py
│  ├─ plan_generator.py
│  └─ lifecycle_monitor.py
└─ core/
   ├─ rag/                             # RAG (дубль!)
   └─ learning/                        # Learning (дубль!)

/platform-services/                    # Микросервисы (REST API)
├─ bia-service/                        # BIA REST API (FastAPI)
├─ risk-service/                       # Risk REST API
├─ governance-service/                 # Governance REST API
├─ planning_service/                   # Planning REST API
├─ plans_service/                      # Plans REST API
├─ response-service/                   # Response REST API
├─ compliance-service/                 # Compliance REST API
├─ documents-service/                  # Documents REST API
├─ validation-service/                 # Validation REST API
└─ learning-service/                   # Learning REST API
```

---

## 🧩 КОНЦЕПТУАЛЬНАЯ МОДЕЛЬ

### 3 разных типа компонентов:

**1. SPECIALISTS (Специалисты) - Легковесные AI агенты**
- Быстрая работа
- Конкретная экспертиза
- Используют инструменты (tools)
- Примеры: BIA Specialist, Risk Analyst, Compliance Auditor

**2. ORGANS (Органы) - Тяжелые AI анализаторы**
- Глубокий анализ (multiple LLM calls)
- Комплексное мышление
- Используют цепочки рассуждений
- Примеры: Impact Oracle, Governance Brain, Risk Advisor

**3. SERVICES (Сервисы) - REST API микросервисы**
- Бизнес-логика
- Database операции
- REST endpoints
- Независимое развертывание
- Примеры: BIA Service, Risk Service, Compliance Service

---

## 🎯 VARIANT 5 РАСПРЕДЕЛЕНИЕ

### АРХИТЕКТУРА:

```
intelligent-core/
│
├─ workflow_intelligence/              # 🧠 THE BRAIN + AI TOOLS
│  │
│  ├─ core/                           # Brain Core
│  │  ├─ engine.py
│  │  ├─ state_machine.py
│  │  └─ governance/
│  │
│  ├─ services/                       # AI TOOLS (унифицированные)
│  │  ├─ rag/                         # ← Из ai_experts/rag + ai-office/core/rag
│  │  ├─ ml/                          # ← Из ai_experts/ml
│  │  ├─ learning/                    # ← Из ai_experts/learning + ai-office/core/learning
│  │  ├─ context/
│  │  ├─ case_library/
│  │  ├─ journey/
│  │  └─ anomaly/
│  │
│  └─ workflows/
│
├─ expertise-center/                   # 🎓 AI EXPERTISE (Plugin система)
│  │
│  ├─ shared/                         # Shared AI infrastructure
│  │  ├─ base/                        # ← Из ai_experts/base + ai-office/base
│  │  │  ├─ base_specialist.py
│  │  │  ├─ base_organ.py
│  │  │  └─ base_tool.py
│  │  │
│  │  └─ tools/                       # ← Из ai_experts/tools
│  │     ├─ bia_tools.py
│  │     ├─ compliance_tools.py
│  │     ├─ strategic_tools.py
│  │     └─ case_library_tool.py
│  │
│  └─ domains/                        # Domain plugins
│     │
│     └─ bcm/                         # BCM Plugin
│        │
│        ├─ specialists/              # ← Из ai-office/ВСМ-colleagues + ai_experts/specialists
│        │  ├─ bia_specialist.py     # Из ai-office/ВСМ-colleagues/bia_specialist
│        │  ├─ risk_analyst.py       # Из ai-office/ВСМ-colleagues/risk_analyst
│        │  ├─ project_manager.py    # Из ai-office/ВСМ-colleagues/project_manager
│        │  ├─ incident_advisor.py   # Из ai-office/ВСМ-colleagues/incident_advisor
│        │  ├─ plan_generator.py     # Из ai-office/ВСМ-colleagues/plan_generator
│        │  ├─ compliance_copilot.py # Из ai-office/ВСМ-colleagues/compliance_copilot
│        │  ├─ exercise_designer.py  # Из ai-office/ВСМ-colleagues/exercise_designer
│        │  ├─ compliance_auditor.py # Из ai_experts/specialists/compliance_auditor
│        │  ├─ bcm_advisor.py        # Из ai_experts/specialists/bcm_advisor
│        │  └─ strategic_planner.py  # Из ai_experts/specialists/strategic_planner
│        │
│        ├─ organs/                   # ← Из ai-office/organs
│        │  ├─ governance_brain.py
│        │  ├─ impact_oracle.py
│        │  ├─ risk_advisor.py
│        │  ├─ compliance_guardian.py
│        │  ├─ emergency_response.py
│        │  ├─ scenario_creator.py
│        │  ├─ performance_analyst.py
│        │  ├─ learning_coach.py
│        │  ├─ plan_generator_organ.py
│        │  └─ lifecycle_monitor.py
│        │
│        ├─ knowledge/                # ← Из ai_experts/knowledge
│        │  ├─ iso_22301/
│        │  ├─ bci_guidelines/
│        │  └─ best_practices/
│        │
│        └─ services_config.py        # Metadata о platform-services
│
└─ orchestration/
   └─ ai-orchestration/

platform-services/                     # 💼 ОСТАЮТСЯ КАК ЕСТЬ!
├─ bia-service/                        # FastAPI микросервисы
├─ risk-service/
├─ governance-service/
├─ planning_service/
├─ plans_service/
├─ response-service/
├─ compliance-service/
├─ documents-service/
├─ validation-service/
└─ learning-service/
```

---

## 📊 ДЕТАЛЬНАЯ МИГРАЦИЯ

### 1. ai_experts/ → Куда перемещается?

| Компонент | Откуда | Куда | Причина |
|-----------|--------|------|---------|
| `rag/` | ai_experts/rag/ | workflow_intelligence/services/rag/ | AI tool для brain |
| `ml/` | ai_experts/ml/ | workflow_intelligence/services/ml/ | AI tool для brain |
| `learning/` | ai_experts/learning/ | workflow_intelligence/services/learning/ | AI tool для brain |
| `tools/` | ai_experts/tools/ | expertise-center/shared/tools/ | Shared tools для всех |
| `base/` | ai_experts/base/ | expertise-center/shared/base/ | Base classes |
| `specialists/` | ai_experts/specialists/ | expertise-center/domains/bcm/specialists/ | BCM domain |
| `knowledge/` | ai_experts/knowledge/ | expertise-center/domains/bcm/knowledge/ | BCM knowledge |

**ПОСЛЕ МИГРАЦИИ: ai_experts/ → _archive/ai_experts/**

---

### 2. ai-office/ → Куда перемещается?

| Компонент | Откуда | Куда | Причина |
|-----------|--------|------|---------|
| `ВСМ-colleagues/` | ai-office/ВСМ-colleagues/ | expertise-center/domains/bcm/specialists/ | BCM specialists |
| `organs/` | ai-office/organs/ | expertise-center/domains/bcm/organs/ | BCM organs |
| `core/rag/` | ai-office/core/rag/ | workflow_intelligence/services/rag/ | Merge с ai_experts/rag |
| `core/learning/` | ai-office/core/learning/ | workflow_intelligence/services/learning/ | Merge с ai_experts/learning |
| `core/intent/` | ai-office/core/intent/ | orchestration/ai-orchestration/intent/ | Orchestration logic |
| `coordinator/` | ai-office/coordinator/ | expertise-center/core/coordinator.py | Orchestration |
| `llm/` | ai-office/llm/ | expertise-center/shared/llm/ | Shared LLM clients |

**ПОСЛЕ МИГРАЦИИ: ai-office/ → _archive/ai-office/**

---

### 3. platform-services/ → Остаются как есть!

**✅ НЕ ТРОГАЕМ!**

```
platform-services/
├─ bia-service/              # ✅ ОСТАЕТСЯ
├─ risk-service/             # ✅ ОСТАЕТСЯ
├─ governance-service/       # ✅ ОСТАЕТСЯ
├─ planning_service/         # ✅ ОСТАЕТСЯ
├─ plans_service/            # ✅ ОСТАЕТСЯ
├─ response-service/         # ✅ ОСТАЕТСЯ
├─ compliance-service/       # ✅ ОСТАЕТСЯ
├─ documents-service/        # ✅ ОСТАЕТСЯ
├─ validation-service/       # ✅ ОСТАЕТСЯ
└─ learning-service/         # ✅ ОСТАЕТСЯ
```

**Причины:**
- Это микросервисы с REST API
- Независимое развертывание (Docker)
- Business logic + database
- НЕ AI логика - бизнес логика!

**Связь с AI:**
```
platform-services/bia-service/
├─ main.py
├─ api/routes.py
└─ integration/
   └─ ai_integration.py      # ← Вызывает expertise-center/domains/bcm/specialists/bia_specialist
```

---

## 🔗 КАК ОНИ ВЗАИМОДЕЙСТВУЮТ?

### Request Flow (пример BIA):

```
1. USER REQUEST
   ↓
   POST /api/v1/bcm/bia/analyze

2. API GATEWAY
   ↓
   Routes to platform-services/bia-service (port 8011)

3. BIA SERVICE (platform-services/bia-service)
   ↓
   async def analyze_bia(request):
       # Вызвать AI specialist
       specialist = await get_specialist("bcm", "bia_specialist")
       ai_analysis = await specialist.analyze(request.data)

       # Сохранить в DB
       await db.save(ai_analysis)

       return ai_analysis

4. EXPERTISE-CENTER (intelligent-core/expertise-center)
   ↓
   Get specialist: domains/bcm/specialists/bia_specialist.py

5. BIA SPECIALIST (expertise-center/domains/bcm/specialists/bia_specialist.py)
   ↓
   class BIASpecialist(BaseSpecialist):
       async def analyze(self, data):
           # 1. Check workflow rules (from brain)
           workflow = await self.brain.get_workflow("bia")

           # 2. Use RAG (from brain tools)
           similar_cases = await self.rag.search(data)

           # 3. Use ML (from brain tools)
           criticality = await self.ml.predict(data)

           # 4. Use Tools (from shared tools)
           bia_calc = await self.tools.bia_calculator.calculate(data)

           # 5. Delegate to Organ if needed (heavy analysis)
           if complex_analysis_needed:
               deep_analysis = await self.delegate_to_organ(
                   organ="impact_oracle",
                   data=data
               )

           return analysis

6. IMPACT ORACLE (expertise-center/domains/bcm/organs/impact_oracle.py)
   ↓
   class ImpactOracle(BaseOrgan):
       async def analyze(self, data):
           # Deep multi-step LLM analysis
           # Chain of thought reasoning
           # Multiple LLM calls
           return deep_insights

7. BRAIN TOOLS (workflow_intelligence/services/)
   ↓
   - RAG: Semantic search in case library
   - ML: Predict criticality
   - Learning: Learn from this case

8. RESULT
   ↓
   BIA Service saves to database
   Returns to user
```

---

## 🎯 КЛЮЧЕВЫЕ РАЗЛИЧИЯ

### Specialists vs Organs vs Services

**SPECIALISTS (Специалисты)**
```python
# expertise-center/domains/bcm/specialists/bia_specialist.py

class BIASpecialist(BaseSpecialist):
    """
    Легковесный AI агент
    - Быстрые ответы
    - Использует инструменты
    - Конкретная экспертиза
    """

    capabilities = ["bia_analysis", "criticality_assessment"]
    tools = ["bia_calculator", "dependency_mapper"]

    async def handle(self, query):
        # 1 LLM call обычно
        # Использует готовые инструменты
        result = await self.tools.bia_calculator.calculate(query)
        advice = await self.llm.generate_advice(result)
        return advice
```

**ORGANS (Органы)**
```python
# expertise-center/domains/bcm/organs/impact_oracle.py

class ImpactOracle(BaseOrgan):
    """
    Тяжелый AI анализатор
    - Глубокий анализ
    - Multiple LLM calls
    - Chain of thought
    """

    async def analyze(self, data):
        # Multiple LLM calls (5-10+)
        # Chain of thought reasoning

        # Step 1: Identify critical factors
        factors = await self.llm.identify_factors(data)

        # Step 2: Analyze each factor
        analyses = []
        for factor in factors:
            analysis = await self.llm.deep_analyze(factor)
            analyses.append(analysis)

        # Step 3: Synthesize
        synthesis = await self.llm.synthesize(analyses)

        # Step 4: Generate recommendations
        recommendations = await self.llm.recommend(synthesis)

        return {
            "analysis": synthesis,
            "recommendations": recommendations,
            "confidence": self._calculate_confidence(analyses)
        }
```

**SERVICES (Сервисы)**
```python
# platform-services/bia-service/api/routes.py

@router.post("/bia/analyze")
async def analyze_bia(
    request: BIARequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    REST API микросервис
    - Business logic
    - Database operations
    - Authentication
    - Вызывает AI specialists/organs при необходимости
    """

    # Business logic
    bia = await bia_service.create_bia(request.org_id, user.id)

    # AI analysis (optional)
    if request.use_ai:
        specialist = await get_specialist("bcm", "bia_specialist")
        ai_analysis = await specialist.analyze(request.data)
        bia.ai_insights = ai_analysis

    # Save to database
    await db.save(bia)

    # Publish event
    await eventbus.publish("bia.created", bia)

    return bia
```

---

## 📁 ИТОГОВАЯ СТРУКТУРА (после миграции)

```
AI-Platform-ISO/
│
├─ intelligent-core/
│  │
│  ├─ workflow_intelligence/           # 🧠 THE BRAIN + AI TOOLS
│  │  ├─ core/                        # Brain logic
│  │  ├─ services/                    # AI tools (RAG, ML, Learning, etc)
│  │  └─ workflows/
│  │
│  ├─ expertise-center/                # 🎓 AI EXPERTISE
│  │  ├─ core/                        # Orchestration logic
│  │  ├─ shared/                      # Shared AI infrastructure
│  │  │  ├─ base/                     # Base classes
│  │  │  ├─ tools/                    # Shared tools
│  │  │  └─ llm/                      # LLM clients
│  │  │
│  │  └─ domains/                     # Domain plugins
│  │     └─ bcm/                      # BCM Plugin
│  │        ├─ specialists/           # 10+ BCM specialists
│  │        ├─ organs/                # 10 BCM organs
│  │        ├─ knowledge/             # BCM knowledge
│  │        └─ services_config.py     # Service metadata
│  │
│  └─ orchestration/
│     ├─ ai-orchestration/
│     └─ coordination-center/
│
├─ platform-services/                  # 💼 BUSINESS SERVICES
│  ├─ bia-service/                    # FastAPI микросервисы
│  ├─ risk-service/
│  ├─ governance-service/
│  ├─ planning_service/
│  ├─ plans_service/
│  ├─ response-service/
│  ├─ compliance-service/
│  ├─ documents-service/
│  ├─ validation-service/
│  └─ learning-service/
│
├─ infrastructure/                     # ⚙️ INFRASTRUCTURE
│  ├─ database/
│  ├─ eventbus/
│  ├─ auth/
│  └─ monitoring/
│
└─ _archive/                          # 📦 ARCHIVED
   ├─ ai_experts/                     # ← Moved to workflow_intelligence + expertise-center
   └─ ai-office/                      # ← Moved to expertise-center
```

---

## 🔄 MIGRATION PLAN

### Phase 1: Создать новую структуру (НЕ ЛОМАЕТ!)

```bash
# 1. Создать expertise-center
mkdir -p intelligent-core/expertise-center/{core,shared,domains/bcm}
mkdir -p intelligent-core/expertise-center/shared/{base,tools,llm}
mkdir -p intelligent-core/expertise-center/domains/bcm/{specialists,organs,knowledge}

# 2. Расширить workflow_intelligence/services
mkdir -p intelligent-core/workflow_intelligence/services/{rag,ml,learning,context,case_library,journey,anomaly}
```

### Phase 2: Копировать (НЕ перемещать!) код

```bash
# AI tools → workflow_intelligence/services/
cp -r intelligent-core/ai_experts/rag/* intelligent-core/workflow_intelligence/services/rag/
cp -r intelligent-core/ai_experts/ml/* intelligent-core/workflow_intelligence/services/ml/
cp -r intelligent-core/ai_experts/learning/* intelligent-core/workflow_intelligence/services/learning/

# Specialists → expertise-center/domains/bcm/specialists/
cp -r intelligent-core/ai-office/ВСМ-colleagues/* intelligent-core/expertise-center/domains/bcm/specialists/
cp intelligent-core/ai_experts/specialists/* intelligent-core/expertise-center/domains/bcm/specialists/

# Organs → expertise-center/domains/bcm/organs/
cp intelligent-core/ai-office/organs/* intelligent-core/expertise-center/domains/bcm/organs/

# Base classes → expertise-center/shared/base/
cp intelligent-core/ai_experts/base/* intelligent-core/expertise-center/shared/base/
cp intelligent-core/ai-office/base/* intelligent-core/expertise-center/shared/base/

# Tools → expertise-center/shared/tools/
cp -r intelligent-core/ai_experts/tools/* intelligent-core/expertise-center/shared/tools/

# Knowledge → expertise-center/domains/bcm/knowledge/
cp -r intelligent-core/ai_experts/knowledge/* intelligent-core/expertise-center/domains/bcm/knowledge/
```

### Phase 3: Обновить импорты

```python
# До:
from ai_experts.rag import RAGPipeline
from ai_office.ВСМ_colleagues.bia_specialist import BIASpecialist

# После:
from workflow_intelligence.services.rag import RAGPipeline
from expertise_center.domains.bcm.specialists.bia_specialist import BIASpecialist
```

### Phase 4: Архивировать старый код

```bash
# После успешной миграции и тестов
mv intelligent-core/ai_experts _archive/ai_experts
mv intelligent-core/ai-office _archive/ai-office
```

---

## ✅ ПРЕИМУЩЕСТВА НОВОЙ СТРУКТУРЫ

### 1. Ясность архитектуры

**До:**
- ❌ ai_experts - это часть brain или нет?
- ❌ ai-office - это BCM domain или platform?
- ❌ Где искать BIA specialist? В ai-office или ai_experts?

**После:**
- ✅ workflow_intelligence = Brain + AI Tools (ясно!)
- ✅ expertise-center = AI Experts (ясно!)
- ✅ expertise-center/domains/bcm = BCM AI (ясно!)
- ✅ platform-services = Business logic (ясно!)

### 2. Убирает дублирование

**До:**
- RAG в 3 местах (ai_experts, ai-office, ai_platform)
- Learning в 2 местах (ai_experts, ai-office)
- Base classes в 2 местах

**После:**
- RAG в 1 месте (workflow_intelligence/services/rag)
- Learning в 1 месте (workflow_intelligence/services/learning)
- Base classes в 1 месте (expertise-center/shared/base)

### 3. Логичная группировка

**Specialists + Organs + Knowledge = BCM Domain**

Всё BCM AI в одном месте:
```
expertise-center/domains/bcm/
├─ specialists/    # Быстрые AI агенты
├─ organs/         # Глубокие AI анализаторы
├─ knowledge/      # Знания (ISO, BCI)
└─ services_config.py
```

### 4. Независимое развертывание

```python
# Можно развернуть только AI инструменты
from workflow_intelligence.services.rag import RAGPipeline

# Можно развернуть только BCM domain
from expertise_center.domains.bcm import BCMDomain

# Можно развернуть только services
docker-compose up bia-service
```

---

## 🎯 ФИНАЛЬНЫЙ ОТВЕТ

**Где должны быть компоненты в Variant 5:**

| Компонент | Текущее место | Новое место | Роль |
|-----------|---------------|-------------|------|
| **AI Tools (RAG, ML, Learning)** | ai_experts/ | workflow_intelligence/services/ | Инструменты мозга |
| **Specialists** | ai_experts/ + ai-office/ВСМ-colleagues/ | expertise-center/domains/bcm/specialists/ | BCM AI агенты |
| **Organs** | ai-office/organs/ | expertise-center/domains/bcm/organs/ | BCM AI анализаторы |
| **Base classes** | ai_experts/base + ai-office/base | expertise-center/shared/base/ | Shared базовые классы |
| **Tools** | ai_experts/tools/ | expertise-center/shared/tools/ | Shared инструменты |
| **Knowledge** | ai_experts/knowledge/ | expertise-center/domains/bcm/knowledge/ | BCM знания |
| **Services** | platform-services/ | platform-services/ | ✅ ОСТАЮТСЯ! |

**platform-services/ НЕ ТРОГАЕМ!** Это микросервисы с бизнес-логикой.

---

**Статус**: План распределения готов
**Следующий шаг**: Начать миграцию Phase 1?
