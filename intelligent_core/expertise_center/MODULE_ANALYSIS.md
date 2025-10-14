# Expertise Center - Module Analysis

## Назначение

Expertise Center - это Domain Plugin Manager для AI экспертов:
- **Specialists** (3) - стратегический уровень (глубокий анализ, стратегические рекомендации)
- **Tactical Assistants** (12) - операционный уровень (конкретные задачи, быстрые ответы)
- **Analyzers** (10) - тяжелые AI анализаторы (машинное обучение, предсказания)

## Архитектурная Роль

```
┌─────────────────────────────────────────────────────────┐
│             EXPERTISE CENTER                            │
│                                                          │
│  ┌────────────────┐                                     │
│  │     Chief      │  (Orchestrator)                     │
│  │   Executive    │                                     │
│  └────────┬───────┘                                     │
│           │                                              │
│           ▼                                              │
│  ┌────────────────┐        ┌──────────────┐            │
│  │    Expert      │───────▶│   Domain     │            │
│  │   Registry     │        │   Loader     │            │
│  └────────────────┘        └──────────────┘            │
│           │                                              │
│           ▼                                              │
│  ┌───────────────────────────────────────┐             │
│  │         Domain: BCM                    │             │
│  │  ┌───────────┐  ┌────────────────┐   │             │
│  │  │Specialists│  │Tactical Assist.│   │             │
│  │  │   (3)     │  │     (12)       │   │             │
│  │  └───────────┘  └────────────────┘   │             │
│  │  ┌───────────┐                        │             │
│  │  │ Analyzers │                        │             │
│  │  │   (10)    │                        │             │
│  │  └───────────┘                        │             │
│  └───────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────┘
                      ▲
                      │
           Uses: ai-foundation (RAG, LLM, ML)
```

**Design Pattern**: Plugin Architecture с domain-based organization

## Структура файлов

```
expertise-center/
├── __init__.py                         # Main exports
│
├── core/                              # Core Orchestration
│   ├── __init__.py
│   ├── chief_executive.py             # ChiefExecutive (main orchestrator)
│   ├── expert_registry.py             # ExpertRegistry (plugin registry)
│   ├── domain_loader.py               # DomainLoader (dynamic loading)
│   └── organism_coordinator.py        # OrganismCoordinator (multi-agent)
│
├── shared/                            # Shared Base Classes
│   ├── base/
│   │   ├── __init__.py
│   │   ├── base_specialist.py         # BaseSpecialist (strategic)
│   │   ├── base_tactical_assistant.py # BaseTacticalAssistant (tactical)
│   │   ├── base_analyzer.py           # BaseAnalyzer (heavy AI)
│   │   └── base_colleague.py          # BaseColleague (deprecated alias)
│   └── learning_knowledge_adapter.py  # Learning Knowledge integration
│
├── domains/                           # Domain Plugins
│   └── bcm/                          # BCM Domain
│       ├── __init__.py
│       │
│       ├── specialists/              # Strategic Experts (3)
│       │   ├── __init__.py
│       │   ├── bcm_advisor.py        # BCMAdvisor - strategic BCM guidance
│       │   ├── compliance_auditor.py # ComplianceAuditor - compliance analysis
│       │   └── strategic_planner.py  # StrategicPlanner - strategic planning
│       │
│       ├── tactical_assistants/      # Operational Experts (12)
│       │   ├── __init__.py
│       │   ├── bia_specialist.py     # BIA tasks
│       │   ├── risk_analyst.py       # Risk analysis
│       │   ├── compliance_copilot.py # Compliance support
│       │   ├── incident_advisor.py   # Incident response
│       │   ├── plan_generator.py     # Plan generation
│       │   ├── project_manager.py    # Project management
│       │   ├── exercise_designer.py  # Exercise design
│       │   ├── documents_specialist.py    # Documentation
│       │   ├── community_specialist.py    # Community support
│       │   ├── governance_specialist.py   # Governance
│       │   ├── validation_specialist.py   # Validation
│       │   └── learning_specialist.py     # Learning support
│       │
│       └── analyzers/                # Heavy AI (10)
│           ├── __init__.py
│           ├── compliance_analyzer.py    # Compliance analysis
│           ├── risk_analyzer.py          # Risk analysis
│           ├── impact_analyzer.py        # Impact analysis
│           ├── emergency_analyzer.py     # Emergency analysis
│           ├── learning_analyzer.py      # Learning analysis
│           ├── lifecycle_analyzer.py     # Lifecycle analysis
│           ├── scenario_analyzer.py      # Scenario analysis
│           ├── governance_analyzer.py    # Governance analysis
│           ├── performance_analyzer.py   # Performance analysis
│           └── plan_analyzer.py          # Plan analysis
│
├── update_specialists.py              # Migration script
└── update_assistants.py               # Migration script
```

## Основные компоненты

### 1. ChiefExecutive (core/)

**Главный оркестратор всех экспертов**

```python
class ChiefExecutive:
    """
    Responsibilities:
    - Load and manage domain plugins
    - Coordinate specialists, colleagues, analyzers
    - Route queries to appropriate experts
    - Integrate with ai-foundation (RAG, LLM, ML)
    """
```

**Методы:**
- `initialize(domains)` - инициализация с доменами
- `load_domain(domain_name)` - загрузка домена
- `query_specialist(specialist_id, context, query)` - запрос к специалисту
- `ask_colleague(colleague_id, task, context)` - запрос к помощнику
- `run_analyzer(analyzer_id, data, params)` - запуск анализатора

### 2. ExpertRegistry (core/)

**Реестр всех AI экспертов**

Хранит:
- Specialists по ID
- Tactical Assistants по ID
- Analyzers по ID
- Metadata о каждом эксперте

### 3. DomainLoader (core/)

**Динамическая загрузка доменов**

Загружает:
- Domain configuration
- Specialists
- Tactical Assistants
- Analyzers

### 4. Base Classes (shared/base/)

#### BaseSpecialist
**Стратегический уровень**

Интеграции:
- `self.rag` - RAGPipeline для поиска знаний
- `self.llm` - LLMRouter для стратегического анализа
- `self.context_builder` - ContextBuilder для обогащения контекста
- `self.knowledge` - LearningKnowledgeAdapter для domain knowledge

Методы:
- `analyze(context, query)` - стратегический анализ
- `recommend(analysis)` - стратегические рекомендации

#### BaseTacticalAssistant
**Операционный уровень**

Интеграции: те же что у BaseSpecialist

Методы:
- `assist(task, context)` - помощь в выполнении задачи
- `validate(data)` - валидация данных
- `suggest(context)` - предложения

#### BaseAnalyzer
**Тяжелые AI анализаторы**

Интеграции:
- `self.rag` - RAGPipeline
- `self.llm` - LLMRouter
- `self.ml` - ML models из ai-foundation

Методы:
- `analyze(data, params)` - глубокий анализ
- `predict(data)` - предсказания
- `score(data)` - оценка

## BCM Domain Experts

### Specialists (Strategic - 3)

1. **BCMAdvisor**
   - Strategic BCM guidance
   - High-level recommendations
   - Roadmap planning

2. **ComplianceAuditor**
   - ISO 22301 compliance analysis
   - Gap analysis
   - Audit reports

3. **StrategicPlanner**
   - Strategic planning
   - Long-term roadmaps
   - Resource allocation

### Tactical Assistants (Operational - 12)

1. **BIASpecialist** - BIA workflow support
2. **RiskAnalyst** - Risk assessment support
3. **ComplianceCopilot** - Daily compliance tasks
4. **IncidentAdvisor** - Incident response guidance
5. **PlanGenerator** - Plan generation support
6. **ProjectManager** - Project management support
7. **ExerciseDesigner** - Exercise scenario design
8. **DocumentsSpecialist** - Documentation support
9. **CommunitySpecialist** - Community interaction
10. **GovernanceSpecialist** - Governance support
11. **ValidationSpecialist** - Validation support
12. **LearningSpecialist** - Learning support

### Analyzers (Heavy AI - 10)

1. **ComplianceAnalyzer** - Deep compliance analysis
2. **RiskAnalyzer** - Advanced risk analysis
3. **ImpactAnalyzer** - Impact assessment
4. **EmergencyAnalyzer** - Emergency scenario analysis
5. **LearningAnalyzer** - Learning pattern analysis
6. **LifecycleAnalyzer** - BCM lifecycle analysis
7. **ScenarioAnalyzer** - Scenario analysis
8. **GovernanceAnalyzer** - Governance analysis
9. **PerformanceAnalyzer** - Performance analysis
10. **PlanAnalyzer** - Plan quality analysis

## Зависимости

### Внешние (pip пакеты)

Наследует зависимости от ai-foundation:
- anthropic, openai - LLM providers
- qdrant-client - vector DB
- scikit-learn - ML models

### Внутренние зависимости

**FROM expertise-center:**
- `ai-foundation` → все AI компоненты (RAG, LLM, ML)
- `ai-foundation/learning-knowledge` → domain knowledge

**TO expertise-center:**
- `platform-services/*` → используют экспертов для AI-powered функций
- `workflow_intelligence` → используют ContextAdvisor
- `community_intelligence` → используют CommunitySpecialist

## API контракты

### Initialization

```python
from expertise_center import ChiefExecutive

# Initialize
chief = ChiefExecutive()
await chief.initialize(domains=['bcm'])
```

### Query Specialist (Strategic)

```python
# Strategic analysis
result = await chief.query_specialist(
    specialist_id="bcm_advisor",
    context={
        "organization_id": "org_123",
        "current_maturity": "level_2"
    },
    query="What should be our BCM roadmap for next year?"
)

# result = {
#     "analysis": "...",
#     "recommendations": [...],
#     "timeline": {...}
# }
```

### Ask Tactical Assistant

```python
# Operational task
result = await chief.ask_colleague(
    colleague_id="bia_specialist",
    task="Help me identify critical processes",
    context={
        "industry": "healthcare",
        "org_size": "500-1000"
    }
)

# result = {
#     "suggestions": [...],
#     "best_practices": [...],
#     "examples": [...]
# }
```

### Run Analyzer

```python
# Heavy AI analysis
result = await chief.run_analyzer(
    analyzer_id="risk_analyzer",
    data={
        "processes": [...],
        "threats": [...],
        "controls": [...]
    },
    params={
        "model": "advanced",
        "confidence_threshold": 0.8
    }
)

# result = {
#     "risk_score": 7.5,
#     "predictions": [...],
#     "recommendations": [...]
# }
```

## Точки интеграции

### 1. Platform Services Integration

```python
# В BIA service
from expertise_center import ChiefExecutive

chief = ChiefExecutive()
await chief.initialize()

# Get AI assistance
hint = await chief.ask_colleague(
    "bia_specialist",
    "Suggest RTO for customer support process"
)
```

### 2. Workflow Intelligence Integration

```python
# В ContextAdvisor
from expertise_center import ChiefExecutive

# Use specialists for strategic advice
advice = await chief.query_specialist(
    "bcm_advisor",
    context=workflow_context,
    query="Is this BIA on track?"
)
```

### 3. Community Intelligence Integration

```python
# Community contributions
from expertise_center import ChiefExecutive

# Validate contribution
validation = await chief.ask_colleague(
    "community_specialist",
    "Validate this case study contribution"
)
```

## Конфигурация

### Domain Configuration

```python
# domains/bcm/__init__.py
DOMAIN_CONFIG = {
    "id": "bcm",
    "name": "Business Continuity Management",
    "specialists": [
        "bcm_advisor",
        "compliance_auditor",
        "strategic_planner"
    ],
    "tactical_assistants": [
        "bia_specialist",
        "risk_analyst",
        # ... 10 more
    ],
    "analyzers": [
        "compliance_analyzer",
        "risk_analyzer",
        # ... 8 more
    ]
}
```

### Environment Variables

```bash
# AI Foundation credentials (inherited)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Vector DB (inherited)
QDRANT_URL=http://localhost:6333
```

## Проблемы/TODO

### Критичные (P0)
- [ ] **Complete Analyzer Implementation** - некоторые analyzers пустые
- [ ] **Domain Loading** - автоматическая загрузка domain plugins
- [ ] **Error Handling** - обработка ошибок при вызове экспертов

### Важные (P1)
- [ ] **Expert Routing** - умный выбор эксперта по запросу
- [ ] **Multi-Expert Coordination** - координация нескольких экспертов
- [ ] **Caching** - кэширование результатов анализа
- [ ] **Monitoring** - метрики использования экспертов

### Улучшения (P2)
- [ ] **New Domains** - добавить домены (ISMS, Quality, etc)
- [ ] **Expert Training** - обучение экспертов на feedback
- [ ] **Expert Benchmarking** - оценка качества работы экспертов
- [ ] **Expert Personalization** - адаптация под организацию

### Документация (P2)
- [ ] **Expert Catalog** - каталог всех экспертов с описаниями
- [ ] **Domain Development Guide** - как создавать новые домены
- [ ] **Best Practices** - best practices использования экспертов

## Метрики и Мониторинг

### Рекомендуемые метрики
- Expert query latency по типам
- Expert success rate
- Token usage per expert
- Cache hit rate
- Expert utilization (какие эксперты популярны)
- User satisfaction scores

## Тестирование

### Необходимые тесты
- [ ] Unit tests для каждого эксперта
- [ ] Integration tests с ai-foundation
- [ ] Performance tests (latency, throughput)
- [ ] Quality tests (expert output quality)

## Deployment Notes

### Требования
- Python 3.11+
- ai-foundation (все зависимости)
- ~2GB RAM (для ML models)

### Scaling
- Experts stateless - horizontal scaling
- Можно кэшировать результаты анализа
- Rate limiting на уровне LLM calls

## Ключевые Решения

### Почему Plugin Architecture?
- Легко добавлять новые домены
- Изоляция доменной логики
- Независимое версионирование доменов
- Lazy loading (загрузка только нужных доменов)

### Почему 3 уровня (Specialist/Tactical/Analyzer)?
- **Specialists** - стратегия, редкие сложные запросы (дорого)
- **Tactical** - ежедневные задачи (быстро, дешево)
- **Analyzers** - тяжелые вычисления (ML, долго)

### Почему ai-foundation integration в base classes?
- DRY - одна точка интеграции
- Все эксперты получают AI capabilities
- Легко обновлять AI компоненты

### Почему Learning Knowledge Adapter?
- Доступ к domain knowledge (ISO standards, case library)
- Унифицированный интерфейс для знаний
- Можно расширять источники знаний

## Migration Notes

### Recent Changes
- ✅ Integrated ai-foundation into base classes
- ✅ Added LearningKnowledgeAdapter
- ✅ Removed duplicate initializations from concrete classes
- ✅ Standardized naming (Colleague → TacticalAssistant)

### Migration Scripts
- `update_specialists.py` - migrate specialists
- `update_assistants.py` - migrate tactical assistants

## Следующие Шаги

1. **Complete Implementation** (P0)
   - Finish analyzer implementations
   - Add error handling
   - Test all experts

2. **Expert Routing** (P1)
   - Smart expert selection
   - Multi-expert coordination
   - Result aggregation

3. **Observability** (P1)
   - Usage metrics
   - Quality metrics
   - Cost tracking

4. **New Domains** (P2)
   - ISMS domain
   - Quality Management domain
   - HR domain

---

**Версия**: 1.0.0
**Последнее обновление**: 2025-10-07
**Статус**: ✅ Production-ready (base architecture)
**Note**: Individual experts need completion
