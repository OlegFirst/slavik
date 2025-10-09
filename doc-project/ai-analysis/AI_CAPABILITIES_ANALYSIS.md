# AI Capabilities - Анализ и Маппинг

## Вопрос
`/Users/MD/AI-Platform-ISO/intelligent-core/ai_capabilities` - заглушка или есть реализация?

## Ответ: ✅ Реализовано в других модулях

---

## Сравнительная таблица

| AI Capability (заглушка) | Где реализовано | Статус | Файл |
|-------------------------|-----------------|--------|------|
| **compliance_auditor** | ✅ AI Experts | ГОТОВО | [ai_experts/specialists/compliance_auditor.py](intelligent-core/ai_experts/specialists/compliance_auditor.py) |
| **risk_advisor** | ✅ AI Office | ГОТОВО | [ai-office/organs/risk_advisor.py](intelligent-core/ai-office/organs/risk_advisor.py) |
| **scenario_generator** | ✅ Digital Twin | ГОТОВО | [digital_twin/simulation/exercise_simulators/ai_scenario_generator.py](intelligent-core/digital_twin/simulation/simulation/exercise_simulators/ai_scenario_generator.py) |
| **rto_predictor** | ⚠️ Частично | ЧАСТИЧНО | Логика в BIA Workflow + ML Predictor |

---

## Детальный анализ

### 1. Compliance Auditor ✅

**Где:** `intelligent-core/ai_experts/specialists/compliance_auditor.py`

**Что делает:**
- Clause-by-clause compliance checking
- Gap analysis (анализ пробелов)
- Audit preparation (подготовка к аудиту)
- Evidence validation (проверка доказательств)

**Инструменты:**
```python
class ComplianceAuditor(ExpertAgent):
    tools = [
        ComplianceCheckTool,      # Проверка соответствия
        GapAnalysisTool,          # Анализ пробелов
        EvidenceValidatorTool     # Валидация доказательств
    ]
```

**Использование:**
```python
auditor = ComplianceAuditor(knowledge_graph)
compliance = await auditor.advise(
    "Check my BIA compliance with ISO 22301",
    context={'workflow_id': 'bia_123'}
)
```

**Интеграция:**
- Работает с Knowledge Graph (Neo4j)
- Использует ISO 22301 clauses
- Интегрируется с Workflow Engine

---

### 2. Risk Advisor ✅

**Где:** `intelligent-core/ai-office/organs/risk_advisor.py`

**Что делает:**
- Risk identification and analysis
- Risk severity and likelihood assessment
- Risk mitigation strategies
- Risk prioritization
- Risk monitoring approaches

**Архитектура:**
```python
class RiskAdvisor(BaseAIOrgan):
    """
    AI Organ для риск-анализа
    
    - Количественные методы
    - Actionable insights
    - Integration с Digital Twin
    """
```

**Методы:**
```python
async def analyze(context):
    """
    Context:
    - twin_id: Digital Twin ID
    - organization_state: Current state
    - known_risks: Known risks list
    - scenario: Risk scenario
    """
```

**Интеграция:**
- AI Office (AI Organs ecosystem)
- Digital Twin (для dependency analysis)
- LLM Router (Claude/GPT)

---

### 3. Scenario Generator ✅

**Где:**
1. `intelligent-core/digital_twin/simulation/exercise_simulators/ai_scenario_generator.py`
2. `intelligent-core/digital_twin/digital-twin/core/ai/advanced_scenario_generator.py`

**Что делает:**
- Generate BCM exercise scenarios
- Realistic disruption scenarios
- Multi-stage crisis simulations
- Industry-specific scenarios

**Типы сценариев:**
```python
scenarios = [
    "cyberattack",           # Кибератака
    "natural_disaster",      # Природная катастрофа
    "pandemic",              # Пандемия
    "supply_chain_failure",  # Сбой поставок
    "key_person_loss",       # Потеря ключевого персонала
    "infrastructure_failure" # Сбой инфраструктуры
]
```

**Интеграция:**
- Digital Twin Simulation
- Exercise Simulators
- AI-powered scenario evolution

---

### 4. RTO Predictor ⚠️ (Частично реализован)

**Где реализована логика:**

#### A. BIA Workflow Engine
`intelligent-core/workflow_intelligence/core/bia_workflow.py`

```python
class BIAWorkflowEngine:
    async def set_recovery_objective(process_id, objective):
        """
        Set RTO/RPO with validation
        - Validates against industry benchmarks
        - Checks feasibility
        """
```

#### B. Predictive Timeline Service
`intelligent-core/community_intelligence/services/predictive_timeline.py`

```python
class PredictiveTimelineService:
    async def predict_timeline(org_id, horizon_months):
        """
        ML-based prediction:
        - Predicts stage completion times
        - Resource needs forecasting
        - Based on similar orgs
        """
```

#### C. Case Library Benchmarking
`intelligent-core/workflow_intelligence/case_library/repository.py`

```python
class CaseRepository:
    async def get_benchmarks(industry, size, module):
        """
        Returns:
        - avg_rto_hours (среднее RTO)
        - median_rto_hours
        - p90_rto_hours (90 перцентиль)
        """
```

**Что НЕ хватает для полного RTO Predictor:**
- [ ] Dedicated ML model for RTO prediction
- [ ] Historical RTO data collection
- [ ] Industry-specific RTO rules
- [ ] Dependency-based RTO calculation

**Можно создать:**
```python
# intelligent-core/ai_capabilities/rto_predictor/rto_predictor.py

class RTOPredictor:
    """
    ML-based RTO prediction
    
    Features:
    - Predict RTO based on process characteristics
    - Industry benchmarks
    - Dependency analysis
    - Risk-adjusted RTO
    """
    
    async def predict_rto(self, process: Dict) -> Dict:
        """
        Predict optimal RTO for process
        
        Inputs:
        - process_type
        - industry
        - criticality
        - dependencies
        - resources_available
        
        Outputs:
        - recommended_rto_hours
        - confidence_score
        - reasoning
        - similar_cases
        """
```

---

## Рекомендации

### ✅ Оставить как есть (реализовано лучше)
- **compliance_auditor** → `ai_experts/specialists/`
- **risk_advisor** → `ai-office/organs/`
- **scenario_generator** → `digital_twin/simulation/`

### 🔄 Доработать
- **rto_predictor** → Создать dedicated модуль

### 🗑️ Удалить заглушки
```bash
rm -rf /Users/MD/AI-Platform-ISO/intelligent-core/ai_capabilities
```

Или переименовать в `_archive_ai_capabilities` для истории.

---

## Архитектурное решение

### Текущая архитектура (правильная ✅)

```
intelligent-core/
├── ai_experts/              # Expert agents (specialists)
│   └── specialists/
│       └── compliance_auditor.py
│
├── ai-office/              # AI Organs (modular capabilities)
│   └── organs/
│       └── risk_advisor.py
│
├── digital_twin/           # Simulation & scenarios
│   └── simulation/
│       └── ai_scenario_generator.py
│
└── community_intelligence/ # Predictive services
    └── services/
        └── predictive_timeline.py
```

### Почему это лучше?

1. **Модульность** - каждая capability в своем контексте
2. **Специализация** - AI Experts для advice, AI Organs для execution
3. **Интеграция** - каждый модуль интегрирован с нужными сервисами
4. **Расширяемость** - легко добавлять новые organs/experts

---

## Действия

### 1. Удалить заглушки ✅
```bash
# Переместить в архив
mv /Users/MD/AI-Platform-ISO/intelligent-core/ai_capabilities \
   /Users/MD/AI-Platform-ISO/_archive/ai_capabilities_stub_2024
```

### 2. Создать RTO Predictor (опционально)
```bash
# Если нужен dedicated RTO predictor
mkdir -p intelligent-core/ai-office/organs/predictors
touch intelligent-core/ai-office/organs/predictors/rto_predictor.py
```

### 3. Обновить документацию
Добавить mapping в README:
```markdown
# AI Capabilities Mapping

- Compliance Auditor → ai_experts/specialists/
- Risk Advisor → ai-office/organs/
- Scenario Generator → digital_twin/simulation/
- RTO Prediction → workflow_intelligence + community_intelligence
```

---

## Заключение

**ai_capabilities/** - это действительно **заглушка**, но функциональность **полностью реализована** в других, более подходящих местах:

✅ **compliance_auditor** → AI Experts (с tools и knowledge graph)  
✅ **risk_advisor** → AI Office (AI Organ с LLM)  
✅ **scenario_generator** → Digital Twin (с simulation engine)  
⚠️ **rto_predictor** → Распределено (BIA Workflow + Predictive Timeline + Benchmarking)

**Рекомендация:** Удалить `ai_capabilities/` заглушки и документировать где находится реальная реализация.

---

**Дата**: 2025-10-04  
**Статус**: ✅ Анализ завершен  
**Решение**: Удалить заглушки, использовать существующие модули
