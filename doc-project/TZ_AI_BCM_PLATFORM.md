# ТЕХНИЧЕСКОЕ ЗАДАНИЕ
# Единая AI-система для платформы BCM

**Версия:** 1.0
**Дата:** 5 октября 2025
**Статус:** К реализации

---

## 📋 СОДЕРЖАНИЕ

1. [Введение](#введение)
2. [Текущее состояние](#текущее-состояние)
3. [Целевая архитектура](#целевая-архитектура)
4. [Унифицированная номенклатура](#унифицированная-номенклатура)
5. [Структура файлов](#структура-файлов)
6. [Компоненты системы](#компоненты-системы)
7. [Этапы реализации](#этапы-реализации)
8. [Требования к интеграции](#требования-к-интеграции)

---

## 1. ВВЕДЕНИЕ

### 1.1 Назначение документа

Техническое задание на разработку **единой AI-системы для платформы Business Continuity Management (BCM)**, которая объединяет существующие AI компоненты в консистентную архитектуру.

### 1.2 Цели проекта

**Основная цель:** Создать единое AI решение, которое:
- Устраняет дублирование функционала между AI Colleagues, AI Experts и AI Organs
- Обеспечивает консистентное взаимодействие с модулями БД (bia.*, risk.*, governance.*)
- Предоставляет единый интерфейс для диалоговой работы и программных вызовов
- Поддерживает самообучение через Case Library
- Интегрируется с Workflow Intelligence Engine

**Дополнительные цели:**
- Унификация номенклатуры компонентов
- Полное покрытие BCM функционала (BIA, Risk, Compliance, Planning, Incidents, Exercises)
- Расширяемая архитектура для добавления новых специализаций

### 1.3 Границы проекта

**В рамках проекта:**
- AI компоненты для BCM (ВСМ-colleagues, AI Experts, AI Organs)
- Интеграция с БД модулями платформы
- Tools для работы с данными
- Case Library для самообучения
- RAG Pipeline для работы с знаниями

**Вне рамок проекта:**
- Модули БД (bia.*, risk.*, governance.*) - уже реализованы
- EventBus - уже реализован
- Frontend UI - отдельный проект
- Workflow Intelligence Engine - отдельный модуль (интеграция предусмотрена)

---

## 2. ТЕКУЩЕЕ СОСТОЯНИЕ

### 2.1 Существующие компоненты

#### 2.1.1 AI Colleagues (ВСМ-colleagues)
**Расположение:** `/intelligent-core/ai-office/ВСМ-colleagues/`

| Colleague | Файлы | Статус | Функционал |
|-----------|-------|--------|------------|
| **risk_analyst** | risk_analyst.py | ✅ Работает | FAIR методология, риск-анализ, диалог |
| **bia_specialist** | bia_specialist.py | ✅ Работает | RTO/RPO, критичность процессов, диалог |
| **compliance_copilot** | compliance_copilot.py | ✅ Работает | ISO 22301, gap analysis, диалог |
| **project_manager** | project_manager.py | ✅ Работает | BCM проекты, таймлайны, диалог |
| **incident_advisor** | incident_advisor.py | ✅ Работает | Кризисное реагирование, диалог |
| **plan_generator** | plan_generator.py | ✅ Работает | Создание планов BCP/DRP, диалог |
| **exercise_designer** | exercise_designer.py | ✅ Работает | Дизайн учений, сценарии, диалог |

**Характеристики:**
- ✅ PDCA framework
- ✅ Conversation memory
- ✅ RAG Pipeline
- ❌ НЕТ Tools (не пишут в БД)
- ❌ НЕТ ML predictions
- ❌ НЕТ Case Library

#### 2.1.2 AI Experts
**Расположение:** `/intelligent-core/ai_experts/specialists/`

| Expert | Файлы | Статус | Функционал |
|--------|-------|--------|------------|
| **bcm_advisor** | bcm_advisor.py | ⚠️ Архитектура | BIA + планирование + стратегия |
| **compliance_auditor** | compliance_auditor.py | ⚠️ Архитектура | ISO 22301 аудит |
| **strategic_planner** | strategic_planner.py | ⚠️ Архитектура | Долгосрочное планирование |

**Характеристики:**
- ✅ Tools (архитектура есть)
- ✅ ML integration (архитектура есть)
- ✅ Case Library (архитектура есть)
- ❌ НЕТ диалога
- ❌ НЕТ PDCA
- ⚠️ Неполная реализация

#### 2.1.3 AI Organs
**Расположение:** `/intelligent-core/ai-orchestration/muscles/ai_organs/`

| Organ | Файлы | Статус | Функционал |
|-------|-------|--------|------------|
| **governance_brain** | governance_brain.py | ✅ Работает | Governance анализ |
| **risk_advisor** | risk_advisor.py | ✅ Работает | Риск-анализ (LLM) |
| **impact_oracle** | impact_oracle.py | ✅ Работает | Предсказание влияния |
| **compliance_guardian** | compliance_guardian.py | ✅ Работает | Compliance проверка |
| **emergency_response** | emergency_response.py | ✅ Работает | Кризис-менеджмент |
| **scenario_creator** | scenario_creator.py | ✅ Работает | Генерация сценариев |
| **performance_analyst** | performance_analyst.py | ✅ Работает | Анализ KPI |
| **learning_coach** | learning_coach.py | ✅ Работает | Обучение |
| **plan_generator** | plan_generator.py | ✅ Работает | Генерация планов |
| **lifecycle_monitor** | lifecycle_monitor.py | ✅ Работает | Мониторинг |

**Характеристики:**
- ✅ Stateless LLM анализ
- ✅ Structured output
- ❌ НЕТ БД интеграции
- ❌ НЕТ Tools
- ❌ НЕТ самообучения

**ДУБЛИКАТ:** `/intelligent-core/ai-office/organs/` - идентичные файлы

### 2.2 Проблемы текущей архитектуры

1. **Дублирование функционала:**
   - Risk Analyst (colleague) + Risk Advisor (expert) + Risk Advisor (organ) - делают ОДНО И ТО ЖЕ
   - План generator в 2 местах (colleague + organ)
   - Compliance в 3 местах (copilot + auditor + guardian)

2. **Отсутствие интеграции:**
   - Colleagues не используют Experts
   - Experts не используют Organs
   - Никто не пишет в БД
   - Нет Case Library для обучения

3. **Неконсистентная номенклатура:**
   - "Colleagues" vs "Experts" vs "Organs" - непонятно чем отличаются
   - Нет единого подхода к именованию

4. **Неполная реализация:**
   - Experts реализованы только архитектурно (~70 строк)
   - Tools не созданы
   - Case Library не подключена

---

## 3. ЦЕЛЕВАЯ АРХИТЕКТУРА

### 3.1 Трехуровневая архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│  УРОВЕНЬ 1: BCM AI SPECIALISTS (Conversational Layer)           │
│  Диалоговые специалисты для пользователей                       │
│                                                                  │
│  7 специалистов по функциям BCM:                                │
│  • Risk Specialist        • BIA Specialist                      │
│  • Compliance Specialist  • Project Specialist                  │
│  • Incident Specialist    • Planning Specialist                 │
│  • Exercise Specialist                                          │
│                                                                  │
│  Функции: Диалог, PDCA, RAG, Conversation Memory               │
│  Делегирование → BCM AI Engines                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  УРОВЕНЬ 2: BCM AI ENGINES (Business Logic Layer)               │
│  Движки бизнес-логики с инструментами                           │
│                                                                  │
│  10 движков по доменам:                                         │
│  • Risk Engine          • BIA Engine                            │
│  • Compliance Engine    • Governance Engine                     │
│  • Emergency Engine     • Planning Engine                       │
│  • Performance Engine   • Learning Engine                       │
│  • Scenario Engine      • Lifecycle Engine                      │
│                                                                  │
│  Функции: Tools (БД), ML, Case Library, RAG                    │
│  Использование → AI Analyzers                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  УРОВЕНЬ 3: AI ANALYZERS (Fast LLM Layer)                       │
│  Быстрые LLM анализаторы (stateless)                            │
│                                                                  │
│  10 анализаторов (соответствуют engines):                       │
│  Специализированные промпты для Claude/GPT                      │
│                                                                  │
│  Функции: analyze(context) → insights                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  БАЗА: PostgreSQL + Redis + Neo4j                               │
│  • bia.*  • risk.*  • governance.*  • cases.*                   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Принципы архитектуры

1. **Единая точка входа для каждой BCM функции**
   - Риски → Risk Specialist
   - BIA → BIA Specialist
   - Compliance → Compliance Specialist

2. **Делегирование ответственности**
   - Specialist (диалог) → Engine (логика) → Analyzer (LLM)

3. **Переиспользование компонентов**
   - Один Engine может использоваться несколькими Specialists
   - Один Analyzer может использоваться несколькими Engines

4. **Полная интеграция с БД**
   - Все Engines пишут в БД через Tools
   - Все действия логируются в audit.*
   - Case Library собирает паттерны

---

## 4. УНИФИЦИРОВАННАЯ НОМЕНКЛАТУРА

### 4.1 Проблема с текущими названиями

**Сейчас:**
- "AI Colleagues" - коллеги (7 шт)
- "AI Experts" - эксперты (3 шт)
- "AI Organs" - органы (10 шт)

**Проблема:** Непонятно чем отличаются, все они эксперты и все коллеги!

### 4.2 Новая номенклатура (функциональная)

#### **Уровень 1: BCM AI Specialists**
*"Специалисты по функциям BCM для диалога с пользователями"*

- **Risk Specialist** - специалист по рискам
- **BIA Specialist** - специалист по анализу влияния
- **Compliance Specialist** - специалист по соответствию
- **Project Specialist** - специалист по проектам
- **Incident Specialist** - специалист по инцидентам
- **Planning Specialist** - специалист по планированию
- **Exercise Specialist** - специалист по учениям

#### **Уровень 2: BCM AI Engines**
*"Движки бизнес-логики с инструментами"*

- **Risk Engine** - движок анализа рисков
- **BIA Engine** - движок BIA
- **Compliance Engine** - движок compliance
- **Governance Engine** - движок governance
- **Emergency Engine** - движок кризисного реагирования
- **Planning Engine** - движок планирования
- **Performance Engine** - движок анализа производительности
- **Learning Engine** - движок обучения
- **Scenario Engine** - движок сценариев
- **Lifecycle Engine** - движок мониторинга жизненного цикла

#### **Уровень 3: AI Analyzers**
*"Быстрые LLM анализаторы"*

- **RiskAnalyzer** - анализ рисков
- **ImpactAnalyzer** - анализ влияния
- **ComplianceAnalyzer** - анализ соответствия
- **GovernanceAnalyzer** - анализ governance
- **EmergencyAnalyzer** - анализ кризисов
- **PlanningAnalyzer** - анализ планирования
- **PerformanceAnalyzer** - анализ производительности
- **LearningAnalyzer** - анализ обучения
- **ScenarioAnalyzer** - генерация сценариев
- **LifecycleAnalyzer** - мониторинг жизненного цикла

### 4.3 Логика именования

**Specialist** = Диалоговый интерфейс для пользователя
**Engine** = Бизнес-логика + Tools + ML
**Analyzer** = LLM анализ (stateless)

**Преимущества:**
✅ Понятно из названия что делает компонент
✅ Функциональный подход (по доменам BCM)
✅ Нет путаницы между "коллегами" и "экспертами"

---

## 5. СТРУКТУРА ФАЙЛОВ

### 5.1 Целевая структура директорий

```
intelligent-core/
└── bcm_ai/                              # Единый модуль AI для BCM
    │
    ├── __init__.py
    ├── README.md
    ├── requirements.txt
    │
    ├── specialists/                     # Уровень 1: Диалоговые специалисты
    │   ├── __init__.py
    │   ├── base_specialist.py          # Базовый класс
    │   │
    │   ├── risk_specialist/
    │   │   ├── __init__.py
    │   │   ├── risk_specialist.py
    │   │   └── prompts.py
    │   │
    │   ├── bia_specialist/
    │   │   ├── __init__.py
    │   │   ├── bia_specialist.py
    │   │   └── prompts.py
    │   │
    │   ├── compliance_specialist/
    │   │   ├── __init__.py
    │   │   ├── compliance_specialist.py
    │   │   └── prompts.py
    │   │
    │   ├── project_specialist/
    │   │   ├── __init__.py
    │   │   ├── project_specialist.py
    │   │   └── prompts.py
    │   │
    │   ├── incident_specialist/
    │   │   ├── __init__.py
    │   │   ├── incident_specialist.py
    │   │   └── prompts.py
    │   │
    │   ├── planning_specialist/
    │   │   ├── __init__.py
    │   │   ├── planning_specialist.py
    │   │   └── prompts.py
    │   │
    │   └── exercise_specialist/
    │       ├── __init__.py
    │       ├── exercise_specialist.py
    │       └── prompts.py
    │
    ├── engines/                         # Уровень 2: Бизнес-логика
    │   ├── __init__.py
    │   ├── base_engine.py              # Базовый класс
    │   │
    │   ├── risk_engine/
    │   │   ├── __init__.py
    │   │   ├── risk_engine.py
    │   │   └── risk_tools.py           # Tools для работы с risk.*
    │   │
    │   ├── bia_engine/
    │   │   ├── __init__.py
    │   │   ├── bia_engine.py
    │   │   └── bia_tools.py            # Tools для работы с bia.*
    │   │
    │   ├── compliance_engine/
    │   │   ├── __init__.py
    │   │   ├── compliance_engine.py
    │   │   └── compliance_tools.py     # Tools для работы с governance.*
    │   │
    │   ├── governance_engine/
    │   │   ├── __init__.py
    │   │   ├── governance_engine.py
    │   │   └── governance_tools.py
    │   │
    │   ├── emergency_engine/
    │   │   ├── __init__.py
    │   │   ├── emergency_engine.py
    │   │   └── emergency_tools.py
    │   │
    │   ├── planning_engine/
    │   │   ├── __init__.py
    │   │   ├── planning_engine.py
    │   │   └── planning_tools.py
    │   │
    │   ├── performance_engine/
    │   │   ├── __init__.py
    │   │   ├── performance_engine.py
    │   │   └── performance_tools.py
    │   │
    │   ├── learning_engine/
    │   │   ├── __init__.py
    │   │   ├── learning_engine.py
    │   │   └── learning_tools.py
    │   │
    │   ├── scenario_engine/
    │   │   ├── __init__.py
    │   │   ├── scenario_engine.py
    │   │   └── scenario_tools.py
    │   │
    │   └── lifecycle_engine/
    │       ├── __init__.py
    │       ├── lifecycle_engine.py
    │       └── lifecycle_tools.py
    │
    ├── analyzers/                       # Уровень 3: LLM анализаторы
    │   ├── __init__.py
    │   ├── base_analyzer.py            # Базовый класс
    │   │
    │   ├── risk_analyzer.py
    │   ├── impact_analyzer.py
    │   ├── compliance_analyzer.py
    │   ├── governance_analyzer.py
    │   ├── emergency_analyzer.py
    │   ├── planning_analyzer.py
    │   ├── performance_analyzer.py
    │   ├── learning_analyzer.py
    │   ├── scenario_analyzer.py
    │   └── lifecycle_analyzer.py
    │
    ├── core/                            # Общая инфраструктура
    │   ├── __init__.py
    │   │
    │   ├── rag/                         # RAG Pipeline
    │   │   ├── __init__.py
    │   │   ├── pipeline.py
    │   │   ├── embeddings.py
    │   │   └── retrieval.py
    │   │
    │   ├── llm/                         # LLM Router
    │   │   ├── __init__.py
    │   │   ├── llm_router.py
    │   │   ├── anthropic_adapter.py
    │   │   └── openai_adapter.py
    │   │
    │   ├── pdca/                        # PDCA Framework
    │   │   ├── __init__.py
    │   │   ├── pdca_engine.py
    │   │   └── conversation_manager.py
    │   │
    │   └── case_library/                # Case Library
    │       ├── __init__.py
    │       ├── repository.py
    │       ├── collector.py
    │       └── search.py
    │
    ├── ml/                              # ML компоненты
    │   ├── __init__.py
    │   ├── predictive_models.py
    │   ├── pattern_extractor.py
    │   └── training_pipeline.py
    │
    ├── api/                             # API endpoints
    │   ├── __init__.py
    │   ├── specialist_routes.py        # /specialists/*
    │   ├── engine_routes.py            # /engines/*
    │   └── analyzer_routes.py          # /analyzers/*
    │
    ├── tests/                           # Тесты
    │   ├── __init__.py
    │   ├── test_specialists.py
    │   ├── test_engines.py
    │   ├── test_analyzers.py
    │   └── test_integration.py
    │
    └── examples/                        # Примеры использования
        ├── __init__.py
        ├── basic_usage.py
        └── integration_example.py
```

### 5.2 Миграция существующего кода

**Откуда → Куда:**

```
SPECIALISTS (было: AI Colleagues)
---------------------------------
/ai-office/ВСМ-colleagues/risk_analyst/
  → /bcm_ai/specialists/risk_specialist/

/ai-office/ВСМ-colleagues/bia_specialist/
  → /bcm_ai/specialists/bia_specialist/

/ai-office/ВСМ-colleagues/compliance_copilot/
  → /bcm_ai/specialists/compliance_specialist/

/ai-office/ВСМ-colleagues/project_manager/
  → /bcm_ai/specialists/project_specialist/

/ai-office/ВСМ-colleagues/incident_advisor/
  → /bcm_ai/specialists/incident_specialist/

/ai-office/ВСМ-colleagues/plan_generator/
  → /bcm_ai/specialists/planning_specialist/

/ai-office/ВСМ-colleagues/exercise_designer/
  → /bcm_ai/specialists/exercise_specialist/


ENGINES (новые + частично из AI Experts)
-----------------------------------------
НОВОЕ: /bcm_ai/engines/risk_engine/
НОВОЕ: /bcm_ai/engines/bia_engine/
НОВОЕ: /bcm_ai/engines/compliance_engine/
НОВОЕ: /bcm_ai/engines/governance_engine/
НОВОЕ: /bcm_ai/engines/emergency_engine/
НОВОЕ: /bcm_ai/engines/planning_engine/
НОВОЕ: /bcm_ai/engines/performance_engine/
НОВОЕ: /bcm_ai/engines/learning_engine/
НОВОЕ: /bcm_ai/engines/scenario_engine/
НОВОЕ: /bcm_ai/engines/lifecycle_engine/


ANALYZERS (было: AI Organs)
----------------------------
/ai-orchestration/muscles/ai_organs/risk_advisor.py
  → /bcm_ai/analyzers/risk_analyzer.py

/ai-orchestration/muscles/ai_organs/impact_oracle.py
  → /bcm_ai/analyzers/impact_analyzer.py

/ai-orchestration/muscles/ai_organs/compliance_guardian.py
  → /bcm_ai/analyzers/compliance_analyzer.py

/ai-orchestration/muscles/ai_organs/governance_brain.py
  → /bcm_ai/analyzers/governance_analyzer.py

/ai-orchestration/muscles/ai_organs/emergency_response.py
  → /bcm_ai/analyzers/emergency_analyzer.py

/ai-orchestration/muscles/ai_organs/plan_generator.py
  → /bcm_ai/analyzers/planning_analyzer.py

/ai-orchestration/muscles/ai_organs/performance_analyst.py
  → /bcm_ai/analyzers/performance_analyzer.py

/ai-orchestration/muscles/ai_organs/learning_coach.py
  → /bcm_ai/analyzers/learning_analyzer.py

/ai-orchestration/muscles/ai_organs/scenario_creator.py
  → /bcm_ai/analyzers/scenario_analyzer.py

/ai-orchestration/muscles/ai_organs/lifecycle_monitor.py
  → /bcm_ai/analyzers/lifecycle_analyzer.py


УДАЛИТЬ (дубликаты)
--------------------
/ai-office/organs/ - полный дубликат ai-orchestration/muscles/ai_organs/
/ai_experts/ - заменяется на engines
```

---

## 6. КОМПОНЕНТЫ СИСТЕМЫ

### 6.1 Базовые классы

#### 6.1.1 BaseSpecialist

**Файл:** `/bcm_ai/specialists/base_specialist.py`

**Назначение:** Базовый класс для всех Specialists (диалоговый слой)

**Функционал:**
- PDCA framework (Plan-Do-Check-Act)
- Conversation memory management
- Intent detection
- Делегирование Engine
- Форматирование ответов для UI

**Ключевые методы:**
```python
async def chat(message: str, context: dict, history: list) -> dict
async def _delegate_to_engine(intent: str, context: dict) -> dict
def _format_response(engine_result: dict) -> dict
def _detect_intent(message: str) -> str
def _manage_pdca_stage(intent: str) -> str
```

#### 6.1.2 BaseEngine

**Файл:** `/bcm_ai/engines/base_engine.py`

**Назначение:** Базовый класс для всех Engines (бизнес-логика)

**Функционал:**
- Tools management (БД операции)
- Analyzer invocation
- Case Library integration
- ML predictions
- Result synthesis

**Ключевые методы:**
```python
async def execute(action: str, params: dict) -> dict
async def _use_tool(tool_name: str, params: dict) -> dict
async def _analyze_with_analyzer(context: dict) -> dict
async def _find_similar_cases(context: dict) -> list
async def _record_to_case_library(result: dict) -> None
```

#### 6.1.3 BaseAnalyzer

**Файл:** `/bcm_ai/analyzers/base_analyzer.py`

**Назначение:** Базовый класс для всех Analyzers (LLM слой)

**Функционал:**
- LLM prompt building
- Claude/GPT invocation
- Structured output parsing

**Ключевые методы:**
```python
async def analyze(context: dict) -> dict
def _build_system_prompt() -> str
def _build_user_prompt(context: dict) -> str
async def _query_llm(system: str, user: str) -> str
def _parse_response(llm_response: str) -> dict
```

### 6.2 Специалисты (Specialists)

#### 6.2.1 Risk Specialist

**Файл:** `/bcm_ai/specialists/risk_specialist/risk_specialist.py`

**Назначение:** Диалоговый специалист по управлению рисками

**Функционал:**
- FAIR методология (TEF × LM = ALE)
- ISO 27005 risk assessment
- Threat modeling
- Risk treatment recommendations
- Интеграция с BIA для risk-impact correlation

**Делегирование:**
- Engine: `RiskEngine`
- Analyzer: `RiskAnalyzer`

**Intent detection:**
- "analyze_risk" → анализ рисков процесса
- "calculate_fair" → FAIR расчет
- "suggest_mitigation" → предложения по снижению
- "risk_treatment" → план лечения риска

**PDCA stages:**
- Plan: Идентификация рисков
- Do: Анализ рисков (FAIR)
- Check: Оценка treatments
- Act: Реализация treatments

**Пример диалога:**
```
User: "Какие риски у процесса Emergency Department?"
Specialist: Делегирует RiskEngine
Engine: Использует RiskAnalyzer + Tools (БД bia.*, risk.*)
Response:
  "🔴 Критические риски (Severity: 4/5):
   • EMR система - единая точка отказа
   • Нет резервирования для клинической документации

   💡 Рекомендации FAIR:
   1. Внедрить redundancy для EMR (Priority: High)
   2. Обучить персонал работе на бумаге (Priority: Medium)

   📊 На основе 3 похожих случаев из healthcare

   Действия:
   [Создать план снижения] [Рассчитать FAIR] [Детали зависимостей]"
```

#### 6.2.2 BIA Specialist

**Файл:** `/bcm_ai/specialists/bia_specialist/bia_specialist.py`

**Назначение:** Специалист по Business Impact Analysis

**Функционал:**
- RTO/RPO determination
- MTD/MBCO calculation
- Critical process identification
- Dependency mapping
- Impact assessment (financial, operational, reputational)

**Делегирование:**
- Engine: `BIAEngine`
- Analyzer: `ImpactAnalyzer`

**Intent detection:**
- "analyze_impact" → анализ влияния
- "calculate_rto" → определение RTO/RPO
- "map_dependencies" → картирование зависимостей
- "assess_criticality" → оценка критичности

**PDCA stages:**
- Plan: Идентификация процессов
- Do: BIA анализ (RTO/RPO)
- Check: Валидация результатов
- Act: Утверждение критичности

#### 6.2.3 Compliance Specialist

**Файл:** `/bcm_ai/specialists/compliance_specialist/compliance_specialist.py`

**Назначение:** Специалист по соответствию ISO 22301

**Функционал:**
- Clause-by-clause compliance check
- Gap analysis
- Audit preparation
- Evidence validation
- Remediation planning

**Делегирование:**
- Engine: `ComplianceEngine`
- Analyzer: `ComplianceAnalyzer`

**Intent detection:**
- "check_compliance" → проверка соответствия
- "gap_analysis" → gap analysis
- "audit_prep" → подготовка к аудиту
- "validate_evidence" → валидация доказательств

#### 6.2.4 Project Specialist

**Файл:** `/bcm_ai/specialists/project_specialist/project_specialist.py`

**Назначение:** Специалист по BCM проектам

**Функционал:**
- Timeline planning
- Resource allocation
- Milestone tracking
- Risk management для проектов
- Status reporting

**Делегирование:**
- Engine: `PlanningEngine` + `PerformanceEngine`
- Analyzer: `PlanningAnalyzer`

#### 6.2.5 Incident Specialist

**Файл:** `/bcm_ai/specialists/incident_specialist/incident_specialist.py`

**Назначение:** Специалист по кризисному реагированию

**Функционал:**
- Incident severity assessment
- Response procedure guidance
- Escalation recommendations
- Communication planning
- Post-incident review

**Делегирование:**
- Engine: `EmergencyEngine`
- Analyzer: `EmergencyAnalyzer`

#### 6.2.6 Planning Specialist

**Файл:** `/bcm_ai/specialists/planning_specialist/planning_specialist.py`

**Назначение:** Специалист по созданию планов BCM

**Функционал:**
- BCP/DRP/IRP generation
- Template selection
- Plan structure design
- Content generation
- Plan validation

**Делегирование:**
- Engine: `PlanningEngine`
- Analyzer: `PlanningAnalyzer`

#### 6.2.7 Exercise Specialist

**Файл:** `/bcm_ai/specialists/exercise_specialist/exercise_specialist.py`

**Назначение:** Специалист по учениям и тренировкам

**Функционал:**
- Tabletop scenario design
- Exercise planning
- Evaluation criteria
- Performance assessment
- Improvement recommendations

**Делегирование:**
- Engine: `ScenarioEngine` + `LearningEngine`
- Analyzer: `ScenarioAnalyzer`, `LearningAnalyzer`

---

### 6.3 Движки (Engines)

#### 6.3.1 Risk Engine

**Файл:** `/bcm_ai/engines/risk_engine/risk_engine.py`

**Назначение:** Бизнес-логика управления рисками

**Tools:** (файл: `risk_tools.py`)
- `get_process_details(process_id)` → SELECT FROM bia.processes
- `get_process_dependencies(process_id)` → SELECT FROM bia.dependencies
- `get_existing_risks(process_id)` → SELECT FROM risk.risk_register
- `save_risk_analysis(analysis)` → INSERT INTO risk.analyses
- `create_risk_treatment(treatment)` → INSERT INTO risk.treatments

**Analyzers:**
- `RiskAnalyzer` - для риск-анализа
- `ImpactAnalyzer` - для impact assessment

**Case Library:**
- Поиск похожих cases по: industry, process_tier, risk_type
- Запись новых паттернов после анализа

**ML (опционально):**
- `predict_risk_severity()` - Random Forest
- `predict_treatment_effectiveness()` - Gradient Boosting

**Основные методы:**
```python
async def analyze_process_risks(process_id, context) -> dict
async def calculate_fair(process_id, threat_data) -> dict
async def suggest_mitigations(risk_id) -> dict
async def create_treatment_plan(risk_id, treatment_type) -> str
```

#### 6.3.2 BIA Engine

**Файл:** `/bcm_ai/engines/bia_engine/bia_engine.py`

**Tools:** (файл: `bia_tools.py`)
- `get_process(process_id)` → SELECT FROM bia.processes
- `save_bia_analysis(analysis)` → INSERT INTO bia.impact_analysis
- `update_rto_rpo(process_id, rto, rpo)` → UPDATE bia.processes
- `get_dependencies(process_id)` → SELECT FROM bia.dependencies
- `save_dependency(dependency)` → INSERT INTO bia.dependencies

**Основные методы:**
```python
async def analyze_process_impact(process_id, context) -> dict
async def calculate_rto_rpo(process_id, impact_data) -> dict
async def map_dependencies(process_id) -> dict
async def assess_criticality(process_id) -> str
```

#### 6.3.3 Compliance Engine

**Файл:** `/bcm_ai/engines/compliance_engine/compliance_engine.py`

**Tools:** (файл: `compliance_tools.py`)
- `get_compliance_status(org_id, standard)` → SELECT FROM governance.compliance_status
- `save_gap_analysis(gaps)` → INSERT INTO audit.gap_analysis
- `get_evidence(clause_id)` → SELECT FROM documents.evidence
- `save_audit_finding(finding)` → INSERT INTO audit.findings

**Основные методы:**
```python
async def check_compliance(org_id, standard) -> dict
async def perform_gap_analysis(org_id, clauses) -> list
async def validate_evidence(clause_id, evidence_ids) -> dict
async def generate_audit_report(org_id) -> dict
```

#### 6.3.4 Governance Engine

**Файл:** `/bcm_ai/engines/governance_engine/governance_engine.py`

**Tools:** (файл: `governance_tools.py`)
- `get_policies(org_id)` → SELECT FROM governance.policies
- `assess_strategic_alignment(org_id)` → complex query
- `save_governance_assessment(assessment)` → INSERT

**Основные методы:**
```python
async def analyze_governance(org_id, context) -> dict
async def assess_policies(org_id) -> dict
async def evaluate_strategic_alignment(org_id) -> dict
```

#### 6.3.5 Emergency Engine

**Файл:** `/bcm_ai/engines/emergency_engine/emergency_engine.py`

**Tools:** (файл: `emergency_tools.py`)
- `get_incident(incident_id)` → SELECT FROM response.incidents
- `save_incident_assessment(assessment)` → INSERT
- `get_response_procedures(incident_type)` → SELECT FROM response.procedures
- `create_incident_log(log_entry)` → INSERT INTO response.incident_log

**Основные методы:**
```python
async def assess_incident_severity(incident_id, context) -> dict
async def recommend_response_actions(incident_id) -> list
async def escalate_incident(incident_id, level) -> dict
```

#### 6.3.6 Planning Engine

**Файл:** `/bcm_ai/engines/planning_engine/planning_engine.py`

**Tools:** (файл: `planning_tools.py`)
- `get_plan_template(plan_type)` → SELECT FROM planning.templates
- `save_plan(plan_data)` → INSERT INTO planning.plans
- `get_process_data_for_plan(process_ids)` → SELECT FROM bia.*
- `validate_plan_structure(plan_id)` → validation logic

**Основные методы:**
```python
async def generate_plan(plan_type, process_ids, context) -> dict
async def validate_plan(plan_id) -> dict
async def update_plan_section(plan_id, section, content) -> None
```

#### 6.3.7 Performance Engine

**Файл:** `/bcm_ai/engines/performance_engine/performance_engine.py`

**Tools:** (файл: `performance_tools.py`)
- `get_kpis(org_id, period)` → SELECT FROM monitoring.kpis
- `calculate_metrics(kpi_data)` → analytics logic
- `save_performance_report(report)` → INSERT

**Основные методы:**
```python
async def analyze_kpis(org_id, period) -> dict
async def identify_trends(kpi_data) -> list
async def recommend_improvements(kpi_id) -> list
```

#### 6.3.8 Learning Engine

**Файл:** `/bcm_ai/engines/learning_engine/learning_engine.py`

**Tools:** (файл: `learning_tools.py`)
- `get_training_history(org_id)` → SELECT FROM learning.training_sessions
- `assess_competency_gaps(org_id)` → complex analysis
- `save_learning_plan(plan)` → INSERT

**Основные методы:**
```python
async def assess_training_needs(org_id, role) -> dict
async def recommend_training(competency_gaps) -> list
async def track_learning_progress(user_id) -> dict
```

#### 6.3.9 Scenario Engine

**Файл:** `/bcm_ai/engines/scenario_engine/scenario_engine.py`

**Tools:** (файл: `scenario_tools.py`)
- `get_historical_scenarios(org_id)` → SELECT FROM exercises.scenarios
- `save_scenario(scenario_data)` → INSERT
- `get_threat_intelligence(threat_type)` → external API or DB

**Основные методы:**
```python
async def generate_scenario(scenario_type, complexity, context) -> dict
async def adapt_scenario_to_org(scenario_id, org_id) -> dict
async def evaluate_scenario_realism(scenario_id) -> dict
```

#### 6.3.10 Lifecycle Engine

**Файл:** `/bcm_ai/engines/lifecycle_engine/lifecycle_engine.py`

**Tools:** (файл: `lifecycle_tools.py`)
- `get_lifecycle_status(org_id)` → SELECT FROM monitoring.lifecycle_status
- `get_activity_log(org_id, period)` → SELECT FROM audit.activity_log
- `save_health_check(health_data)` → INSERT

**Основные методы:**
```python
async def monitor_lifecycle_health(org_id) -> dict
async def identify_stagnation(org_id) -> list
async def recommend_next_actions(org_id, current_stage) -> list
```

---

### 6.4 Анализаторы (Analyzers)

#### Общие характеристики

Все Analyzers имеют:
- Stateless архитектуру (нет памяти между вызовами)
- Метод `analyze(context: dict) -> dict`
- Специализированные LLM промпты
- Structured output (insights, recommendations, confidence)

#### Список Analyzers

1. **RiskAnalyzer** - анализ рисков (FAIR, severity, vulnerabilities)
2. **ImpactAnalyzer** - анализ влияния (RTO/RPO, impact curves)
3. **ComplianceAnalyzer** - проверка соответствия (gaps, compliance score)
4. **GovernanceAnalyzer** - governance анализ (policies, strategic alignment)
5. **EmergencyAnalyzer** - кризисный анализ (severity, response actions)
6. **PlanningAnalyzer** - анализ планирования (structure, completeness)
7. **PerformanceAnalyzer** - анализ производительности (KPIs, trends)
8. **LearningAnalyzer** - анализ обучения (competency gaps, training needs)
9. **ScenarioAnalyzer** - генерация сценариев (realism, complexity)
10. **LifecycleAnalyzer** - мониторинг жизненного цикла (health, stagnation)

**Файлы:**
```
/bcm_ai/analyzers/risk_analyzer.py
/bcm_ai/analyzers/impact_analyzer.py
/bcm_ai/analyzers/compliance_analyzer.py
/bcm_ai/analyzers/governance_analyzer.py
/bcm_ai/analyzers/emergency_analyzer.py
/bcm_ai/analyzers/planning_analyzer.py
/bcm_ai/analyzers/performance_analyzer.py
/bcm_ai/analyzers/learning_analyzer.py
/bcm_ai/analyzers/scenario_analyzer.py
/bcm_ai/analyzers/lifecycle_analyzer.py
```

---

### 6.5 Общая инфраструктура (Core)

#### 6.5.1 RAG Pipeline

**Расположение:** `/bcm_ai/core/rag/`

**Компоненты:**
- `pipeline.py` - главный RAG pipeline
- `embeddings.py` - генерация embeddings (OpenAI/local)
- `retrieval.py` - hybrid search (vector + keyword)

**Источники знаний:**
- PostgreSQL: `documents.knowledge_base` (ISO 22301, BCI GPG, etc.)
- Neo4j: Knowledge Graph (relationships между clauses)
- Case Library: `cases.*` (похожие кейсы)

**Методы:**
```python
async def retrieve(query: str, context: dict, top_k: int = 5) -> list
async def embed_query(query: str) -> list[float]
async def hybrid_search(query_embedding, query_text, filters) -> list
async def rerank_results(results, query, context) -> list
```

#### 6.5.2 LLM Router

**Расположение:** `/bcm_ai/core/llm/`

**Компоненты:**
- `llm_router.py` - роутинг запросов к LLM провайдерам
- `anthropic_adapter.py` - Anthropic Claude adapter
- `openai_adapter.py` - OpenAI GPT adapter

**Provider priority:**
1. Anthropic Claude (claude-3-5-sonnet-20241022)
2. OpenAI GPT (gpt-4-turbo-preview)
3. Fallback: Ollama (local)

**Методы:**
```python
async def generate(system: str, user: str, temperature: float = 0.7) -> str
async def generate_with_tools(messages, tools, temperature) -> dict
def get_available_providers() -> list
async def health_check() -> dict
```

#### 6.5.3 PDCA Framework

**Расположение:** `/bcm_ai/core/pdca/`

**Компоненты:**
- `pdca_engine.py` - PDCA state management
- `conversation_manager.py` - управление историей диалога

**PDCA Stages:**
- Plan - планирование (что будем делать)
- Do - выполнение (делаем)
- Check - проверка (проверяем результат)
- Act - действие (утверждаем/корректируем)

**Методы:**
```python
def get_current_stage(conversation_id: str) -> str
def advance_to_next_stage(conversation_id: str) -> str
def suggest_next_actions(current_stage: str, context: dict) -> list
def track_stage_progress(conversation_id: str) -> dict
```

#### 6.5.4 Case Library

**Расположение:** `/bcm_ai/core/case_library/`

**Компоненты:**
- `repository.py` - БД операции с cases
- `collector.py` - автоматический сбор паттернов
- `search.py` - semantic search по cases

**БД Schema:**
```sql
-- Уже существует в платформе
cases.workflow_cases
cases.action_patterns
cases.success_metrics
```

**Методы:**
```python
async def search(industry, module, action_type, limit=5) -> list
async def record_case(case_data: dict) -> str
async def extract_patterns(case_id: str) -> list
async def calculate_benchmarks(filters: dict) -> dict
```

---

### 6.6 ML компоненты

**Расположение:** `/bcm_ai/ml/`

#### Файлы:
- `predictive_models.py` - Workflow Predictor (Random Forest + Gradient Boosting)
- `pattern_extractor.py` - ML извлечение паттернов из cases
- `training_pipeline.py` - обучение моделей

#### Модели:

**1. Workflow Duration Predictor**
- Модель: Random Forest Regressor
- Предсказывает: длительность выполнения workflow
- Features: org context, current stage, historical data
- Target: R² > 0.7

**2. Stuck Probability Classifier**
- Модель: Gradient Boosting Classifier
- Предсказывает: вероятность застревания workflow
- Features: time in stage, complexity, resource availability
- Target: Accuracy > 0.75

**3. Expert Help Predictor**
- Модель: Gradient Boosting Classifier
- Предсказывает: нужна ли помощь эксперта
- Features: workflow type, org maturity, AI usage history
- Target: Accuracy > 0.75

**Методы:**
```python
async def predict_journey(org_context, current_state, progress) -> dict
async def train_models(historical_cases: list) -> dict
async def evaluate_model_performance() -> dict
async def retrain_if_needed() -> bool
```

---

## 7. ЭТАПЫ РЕАЛИЗАЦИИ

### ЭТАП 1: Подготовка инфраструктуры

**Цель:** Создать базовые классы и общую инфраструктуру

**Задачи:**
1. Создать структуру директорий `/bcm_ai/`
2. Реализовать `BaseSpecialist`
3. Реализовать `BaseEngine`
4. Реализовать `BaseAnalyzer`
5. Настроить LLM Router (Anthropic + OpenAI)
6. Настроить RAG Pipeline
7. Настроить PDCA Framework
8. Настроить Case Library Repository

**Результат:**
- ✅ Все базовые классы работают
- ✅ LLM Router работает с Claude
- ✅ RAG Pipeline может получать знания из БД
- ✅ Case Library может записывать/искать cases

**Критерии готовности:**
- Unit тесты для базовых классов проходят
- LLM Router может сгенерировать текст через Claude
- RAG Pipeline может найти релевантный документ по запросу

---

### ЭТАП 2: Реализация Analyzers

**Цель:** Мигрировать существующие AI Organs в Analyzers

**Задачи:**
1. Переименовать файлы:
   - `risk_advisor.py` → `risk_analyzer.py`
   - `impact_oracle.py` → `impact_analyzer.py`
   - и т.д.

2. Привести к единому интерфейсу (наследование от `BaseAnalyzer`)
3. Убрать дублирование кода (использовать базовый класс)
4. Добавить structured output parsing
5. Оптимизировать промпты

**Результат:**
- ✅ Все 10 Analyzers реализованы
- ✅ Работают через единый интерфейс
- ✅ Дубликат (`/ai-office/organs/`) удален

**Критерии готовности:**
- Каждый Analyzer может вызвать `analyze(context)` и вернуть результат
- Output имеет структуру: `{insights, recommendations, confidence}`
- Промпты оптимизированы (temperature настроен)

---

### ЭТАП 3: Реализация Engines с Tools

**Цель:** Создать бизнес-логику с интеграцией БД

**Задачи для каждого Engine:**

**3.1 Risk Engine**
1. Создать `RiskEngine` класс (наследник `BaseEngine`)
2. Создать `RiskTools`:
   - `get_process_details()` - SQL к bia.processes
   - `get_dependencies()` - SQL к bia.dependencies
   - `save_risk_analysis()` - INSERT в risk.analyses
   - `create_risk_treatment()` - INSERT в risk.treatments
3. Интегрировать `RiskAnalyzer`
4. Интегрировать Case Library search
5. Реализовать методы:
   - `analyze_process_risks()`
   - `calculate_fair()`
   - `suggest_mitigations()`
   - `create_treatment_plan()`

**3.2 BIA Engine**
1. Создать `BIAEngine` класс
2. Создать `BIATools`:
   - `get_process()` - SELECT FROM bia.processes
   - `save_bia_analysis()` - INSERT INTO bia.impact_analysis
   - `update_rto_rpo()` - UPDATE bia.processes
   - `save_dependency()` - INSERT INTO bia.dependencies
3. Интегрировать `ImpactAnalyzer`
4. Реализовать методы:
   - `analyze_process_impact()`
   - `calculate_rto_rpo()`
   - `map_dependencies()`
   - `assess_criticality()`

**Аналогично для остальных 8 Engines**

**Результат:**
- ✅ Все 10 Engines реализованы
- ✅ Tools пишут в БД
- ✅ Analyzers интегрированы
- ✅ Case Library записывает паттерны

**Критерии готовности:**
- Каждый Engine может выполнить свои основные операции
- Tools успешно пишут/читают БД
- Case Library получает записи после каждой операции
- Integration тесты проходят

---

### ЭТАП 4: Реализация Specialists

**Цель:** Мигрировать Colleagues в Specialists с делегированием Engines

**Задачи для каждого Specialist:**

**4.1 Risk Specialist**
1. Мигрировать код из `/ai-office/ВСМ-colleagues/risk_analyst/`
2. Привести к `BaseSpecialist`
3. Добавить inject `RiskEngine` в `__init__`
4. Модифицировать методы для делегирования:
   - `_handle_risk_analysis()` → `await self.engine.analyze_process_risks()`
   - `_handle_fair_calculation()` → `await self.engine.calculate_fair()`
   - `_handle_mitigation()` → `await self.engine.suggest_mitigations()`
5. Сохранить диалоговую логику (intent detection, PDCA, formatting)

**Аналогично для остальных 6 Specialists**

**Результат:**
- ✅ Все 7 Specialists реализованы
- ✅ Делегируют работу Engines
- ✅ Сохранена диалоговая логика
- ✅ PDCA работает

**Критерии готовности:**
- Каждый Specialist может вести диалог
- Делегирование Engine работает
- Результаты форматируются для UI
- Conversation memory сохраняется

---

### ЭТАП 5: API Endpoints

**Цель:** Создать HTTP API для доступа к системе

**Задачи:**
1. Создать FastAPI endpoints:
   - `/specialists/{specialist_name}/chat` - POST (диалог)
   - `/engines/{engine_name}/execute` - POST (программный вызов)
   - `/analyzers/{analyzer_name}/analyze` - POST (быстрый анализ)

2. Настроить dependency injection (БД сессия, Case Library)
3. Добавить валидацию входных данных (Pydantic models)
4. Добавить error handling
5. Добавить logging

**Результат:**
- ✅ API endpoints работают
- ✅ Валидация входных данных
- ✅ Error handling

**Критерии готовности:**
- Можно вызвать Specialist через HTTP POST
- Можно вызвать Engine напрямую
- Можно вызвать Analyzer напрямую
- API документация (Swagger) доступна

---

### ЭТАП 6: ML Integration (опциональный)

**Цель:** Добавить ML predictions для улучшения точности

**Задачи:**
1. Собрать исторические данные из Case Library (минимум 50 cases)
2. Обучить Workflow Duration Predictor
3. Обучить Stuck Probability Classifier
4. Обучить Expert Help Predictor
5. Интегрировать в Engines (опциональный параметр)
6. Настроить автоматический retrain (еженедельно)

**Результат:**
- ✅ ML модели обучены
- ✅ Интегрированы в Engines
- ✅ Автоматический retrain настроен

**Критерии готовности:**
- Workflow Duration R² > 0.7
- Stuck Probability Accuracy > 0.75
- Expert Help Accuracy > 0.75
- Predictions доступны через Engines

---

### ЭТАП 7: Testing & Documentation

**Цель:** Полное покрытие тестами и документация

**Задачи:**
1. Unit тесты для всех классов
2. Integration тесты для Specialists → Engines → Analyzers
3. End-to-End тесты для полных сценариев
4. Performance тесты (latency, throughput)
5. Документация API (Swagger)
6. Примеры использования
7. Руководство по интеграции

**Результат:**
- ✅ Test coverage > 80%
- ✅ Вся функциональность протестирована
- ✅ Документация полная

---

### ЭТАП 8: Migration & Cleanup

**Цель:** Финальная миграция и удаление старого кода

**Задачи:**
1. Обновить все импорты в других модулях платформы
2. Удалить старые директории:
   - `/ai-office/ВСМ-colleagues/` → мигрировано
   - `/ai-office/organs/` → дубликат
   - `/ai_experts/` → заменено на engines
   - `/ai-orchestration/muscles/ai_organs/` → мигрировано
3. Обновить README во всех модулях
4. Создать migration guide для разработчиков

**Результат:**
- ✅ Старый код удален
- ✅ Все модули обновлены
- ✅ Migration guide готов

---

## 8. ТРЕБОВАНИЯ К ИНТЕГРАЦИИ

### 8.1 Интеграция с модулями БД

**Требуемые БД таблицы** (уже существуют):

**Schema: bia**
- `bia.processes` - бизнес-процессы
- `bia.dependencies` - зависимости процессов
- `bia.impacts` - анализ влияния
- `bia.templates` - BIA шаблоны

**Schema: risk**
- `risk.risk_register` - реестр рисков
- `risk.assessments` - оценки рисков
- `risk.treatments` - меры по снижению
- `risk.scenarios` - риск-сценарии

**Schema: governance**
- `governance.policies` - политики
- `governance.standards` - стандарты
- `governance.compliance_status` - статус соответствия

**Schema: audit**
- `audit.gap_analysis` - gap анализ
- `audit.findings` - находки аудита
- `audit.activity_log` - логи действий

**Schema: response**
- `response.incidents` - инциденты
- `response.procedures` - процедуры реагирования
- `response.incident_log` - логи инцидентов

**Schema: planning**
- `planning.plans` - планы (BCP/DRP/IRP)
- `planning.templates` - шаблоны планов

**Schema: monitoring**
- `monitoring.kpis` - KPI метрики
- `monitoring.lifecycle_status` - статус жизненного цикла

**Schema: learning**
- `learning.training_sessions` - тренинги
- `learning.competency_matrix` - матрица компетенций

**Schema: exercises**
- `exercises.scenarios` - сценарии учений
- `exercises.results` - результаты учений

**Schema: cases** (Case Library)
- `cases.workflow_cases` - кейсы workflow
- `cases.action_patterns` - паттерны действий
- `cases.success_metrics` - метрики успеха

**Schema: documents**
- `documents.knowledge_base` - база знаний (ISO, BCI GPG)
- `documents.evidence` - доказательства для аудита

### 8.2 Интеграция с EventBus

**События для публикации:**

```python
# После риск-анализа
eventbus.publish('risk.analysis.completed', {
    'process_id': 'proc_123',
    'severity': 4,
    'analyzer': 'risk_specialist'
})

# После создания treatment
eventbus.publish('risk.treatment.created', {
    'risk_id': 'risk_456',
    'treatment_type': 'reduce'
})

# После BIA анализа
eventbus.publish('bia.analysis.completed', {
    'process_id': 'proc_123',
    'rto_hours': 4,
    'tier': 'tier_1'
})

# После gap analysis
eventbus.publish('compliance.gap_found', {
    'standard': 'ISO_22301',
    'clause': '8.4',
    'severity': 'critical'
})
```

**Подписки на события:**

```python
# Case Library собирает все события
@eventbus.subscribe('*.*.completed')
async def collect_case(event):
    await case_library.record_case(event.data)

# ML Training Pipeline
@eventbus.subscribe('cases.threshold_reached')
async def trigger_retraining(event):
    if event.data['new_cases'] >= 10:
        await ml_pipeline.retrain_models()
```

### 8.3 Интеграция с Workflow Intelligence Engine

**Контекст от Workflow для AI:**

```python
# Workflow предоставляет контекст
workflow_context = workflow_engine.get_context()

# AI Specialist использует контекст
specialist = RiskSpecialist()
response = await specialist.chat(
    message="Analyze risks",
    context=workflow_context  # включает: current_stage, data, progress
)
```

**AI предлагает следующие шаги для Workflow:**

```python
# AI возвращает действия
response = {
    'actions': [
        {
            'type': 'workflow_transition',
            'target_stage': 'assess_impact',
            'reason': 'Risk analysis complete'
        }
    ]
}

# Workflow использует
if action['type'] == 'workflow_transition':
    await workflow_engine.transition_to(action['target_stage'])
```

### 8.4 Интеграция с Frontend

**API Contracts:**

**POST /specialists/{specialist_name}/chat**

Request:
```json
{
  "message": "Analyze risks for Emergency Department",
  "context": {
    "process_id": "proc_001",
    "industry": "healthcare",
    "size": "medium"
  },
  "conversation_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

Response:
```json
{
  "response": "🔴 Критические риски...",
  "actions": [
    {
      "type": "create_treatment_plan",
      "label": "📋 Создать план снижения риска",
      "data": {"process_id": "proc_001"}
    }
  ],
  "pdca_stage": "check",
  "analysis_data": {
    "severity": 4,
    "vulnerabilities": [...],
    "recommendations": [...]
  },
  "metadata": {
    "analyzed_at": "2025-10-05T10:30:00Z",
    "confidence": 0.87
  }
}
```

---

## 9. КРИТЕРИИ ПРИЕМКИ

### 9.1 Функциональные требования

**FR-1: Диалоговый интерфейс**
- ✅ Каждый Specialist может вести диалог
- ✅ Conversation memory работает
- ✅ PDCA stages отслеживаются
- ✅ Intent detection работает корректно

**FR-2: Бизнес-логика**
- ✅ Каждый Engine может выполнить свои основные операции
- ✅ Tools пишут в БД корректно
- ✅ Case Library получает записи
- ✅ ML predictions работают (если включены)

**FR-3: LLM Анализ**
- ✅ Каждый Analyzer возвращает structured output
- ✅ Confidence score рассчитывается
- ✅ Промпты оптимизированы

**FR-4: Интеграция**
- ✅ Specialist → Engine → Analyzer цепочка работает
- ✅ БД транзакции корректны
- ✅ EventBus получает события
- ✅ Workflow Engine может использовать AI

### 9.2 Нефункциональные требования

**NFR-1: Performance**
- Response latency < 3 секунды (simple queries)
- Response latency < 10 секунд (complex queries с Tools)
- RAG retrieval < 200ms
- Throughput > 10 requests/second

**NFR-2: Reliability**
- Uptime > 99.5%
- Error rate < 1%
- Graceful degradation (если LLM недоступен → fallback)

**NFR-3: Maintainability**
- Code coverage > 80%
- Документация полная
- Logging на всех уровнях
- Clear error messages

**NFR-4: Scalability**
- Может обработать 100+ concurrent users
- БД queries оптимизированы (indexes)
- Case Library может хранить 10000+ cases

---

## 10. ЗАКЛЮЧЕНИЕ

### 10.1 Итоговая система

**Единое AI решение для BCM платформы** состоит из:

- **7 AI Specialists** - диалоговые специалисты для пользователей
- **10 AI Engines** - бизнес-логика с Tools и ML
- **10 AI Analyzers** - быстрые LLM анализаторы
- **Общая инфраструктура** - RAG, LLM Router, PDCA, Case Library
- **Полная интеграция** - с БД, EventBus, Workflow Engine

### 10.2 Преимущества решения

✅ **Единая архитектура** - нет дублирования
✅ **Консистентная номенклатура** - понятно из названия
✅ **Полная интеграция с БД** - все пишут в БД
✅ **Самообучение** - через Case Library
✅ **Расширяемость** - легко добавить новый Specialist/Engine
✅ **Переиспользование** - один Engine для многих Specialists

### 10.3 Следующие шаги

1. Утверждение ТЗ
2. Начало реализации с Этапа 1
3. Поэтапная разработка согласно плану
4. Тестирование на каждом этапе
5. Финальная миграция и cleanup

---

**Конец технического задания**
