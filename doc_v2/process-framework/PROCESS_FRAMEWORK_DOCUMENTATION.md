# Process Framework - Документация

**Date**: 2025-10-11
**Version**: 1.0
**Status**: ✅ Production Ready

---

## 📋 Оглавление

1. [Обзор](#обзор)
2. [Архитектура](#архитектура)
3. [Компоненты](#компоненты)
4. [Стандартные процессы](#стандартные-процессы)
5. [Автоматизация](#автоматизация)
6. [API Reference](#api-reference)
7. [Примеры использования](#примеры-использования)
8. [Integration](#integration)

---

## Обзор

Process Framework - это каркас для формализации и автоматизации бизнес-процессов в BCM системе.

### Основные возможности

✅ **Формализация процессов**:
- Структурированное описание бизнес-процессов
- Определение шагов с типами (Form, Analysis, Decision, Approval, etc.)
- Валидация переходов между шагами

✅ **Стандартизация взаимодействия**:
- Единый формат форм для пользователя
- Валидация входных данных
- Контроль ролей и прав доступа

✅ **Стандартизация документов**:
- Шаблоны документов (BIA Report, Risk Register, BC Plan)
- Автоматическая генерация по шаблонам
- ISO 22301 compliance

✅ **Автоматизация**:
- AI-агенты автоматически заполняют формы
- Система сама выполняет процессы
- Интеграция с AI Orchestrator

---

## Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                           │
│  (Формы, кнопки, валидация на клиенте)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              PROCESS FRAMEWORK API                          │
│  • start_process()                                          │
│  • get_current_step_form()                                  │
│  • execute_step()                                           │
│  • get_process_status()                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           PROCESS ORCHESTRATOR (AI Automation)              │
│  • execute_process_automatically()                          │
│  • _auto_fill_form() → AI заполняет форму                  │
│  • _auto_analyze() → Analytics Specialist                  │
│  • _auto_decide() → AI принимает решение                   │
│  • _auto_generate_document() → Document Generator          │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ AI           │  │ Document     │  │ EventBus     │
│ Orchestrator │  │ Templates    │  │ (Events)     │
│              │  │ Library      │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        │                │                │
        ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA STORAGE                             │
│  • Process Definitions (JSON files)                         │
│  • Process Instances (runtime state)                        │
│  • Generated Documents (PDF, DOCX, MD)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Компоненты

### 1. Process Framework (`process_framework.py`)

**Основные классы**:

#### ProcessDefinition
```python
@dataclass
class ProcessDefinition:
    id: str                          # bcm_bia_v1
    name: str                        # Business Impact Analysis
    version: str                     # 1.0
    steps: Dict[str, ProcessStep]   # Шаги процесса
    start_step_id: str              # Стартовый шаг
    end_step_ids: List[str]         # Конечные шаги
    iso_clause: Optional[str]       # ISO 22301 Clause
```

#### ProcessStep
```python
@dataclass
class ProcessStep:
    id: str                         # bia_initiation
    name: str                       # Инициация BIA
    step_type: StepType            # FORM_INPUT, ANALYSIS, etc.
    form_fields: List[FormField]   # Поля формы
    next_steps: List[str]          # Следующие шаги
    allowed_roles: List[str]       # Кто может выполнять
    ai_agent: Optional[str]        # AI агент для автоматизации
```

#### FormField
```python
@dataclass
class FormField:
    name: str                       # bia_scope
    label: str                      # "Область анализа"
    field_type: str                 # text, textarea, select, date
    required: bool                  # Обязательное поле?
    validations: List[FieldValidation]  # Правила валидации
    help_text: Optional[str]       # Подсказка для пользователя
```

#### StepType (Enum)
```python
class StepType(Enum):
    FORM_INPUT = "form_input"                  # Ввод данных пользователем
    APPROVAL = "approval"                      # Согласование/утверждение
    ANALYSIS = "analysis"                      # Анализ (AI/человек)
    DECISION = "decision"                      # Принятие решения
    DOCUMENT_GENERATION = "document_generation"  # Генерация документа
    NOTIFICATION = "notification"              # Уведомление
    VALIDATION = "validation"                  # Валидация данных
    EXECUTION = "execution"                    # Выполнение действия
```

---

### 2. BCM Processes (`bcm_processes.py`)

**Готовые процессы**:

#### Business Impact Analysis (BIA)
- **Process ID**: `bcm_bia_v1`
- **ISO Clause**: 8.2.2
- **Шаги**: 6
  1. Инициация BIA (Form Input)
  2. Идентификация критичных функций (Form Input)
  3. Анализ воздействия (Analysis) - AI
  4. Требования к ресурсам (Form Input)
  5. Генерация отчета (Document Generation) - AI
  6. Утверждение (Approval)

#### Risk Assessment
- **Process ID**: `bcm_risk_assessment_v1`
- **ISO Clause**: 8.2.3
- **Шаги**: 3
  1. Идентификация рисков
  2. Анализ рисков (AI)
  3. Обработка рисков (Decision)

#### BC Plan Development
- **Process ID**: `bcm_bc_plan_v1`
- **ISO Clause**: 8.4
- **Шаги**: 5
  1. Инициация плана
  2. Определение стратегии
  3. Роли и ответственности
  4. Генерация документа
  5. Утверждение

---

### 3. Document Templates (`document_templates.py`)

**Шаблоны документов**:

#### BIA Report Template
```python
template_id = "bia_report_v1"
sections = [
    "1. Executive Summary",
    "2. Scope and Objectives",
    "3. Critical Business Functions",
    "4. Impact Analysis",
    "5. Resource Requirements",
    "6. Recommendations",
    "7. Approval"
]
```

**Переменные** (автоматически заполняются из process data):
- `{{organization_name}}`
- `{{analysis_date}}`
- `{{critical_functions}}`
- `{{rto_summary}}`
- `{{financial_impact}}`
- etc.

#### Risk Register Template
```python
template_id = "risk_register_v1"
sections = [
    "1. Identified Risks",
    "2. Risk Treatment Plan"
]
```

#### BC Plan Template
```python
template_id = "bc_plan_v1"
sections = [
    "1. Introduction",
    "2. Scope",
    "3. Critical Business Functions",
    "4. Recovery Strategies",
    "5. Roles and Responsibilities",
    "6. Recovery Procedures",
    "7. Communication Plan",
    "8. Testing and Maintenance"
]
```

---

### 4. Process Orchestrator (`process_orchestration_api.py`)

**Автоматизация процессов**:

#### execute_process_automatically()
Автоматически выполняет весь процесс без участия человека.

**Как работает**:
1. Запускает процесс
2. Получает текущий шаг
3. Определяет тип шага
4. Вызывает соответствующий AI агент
5. AI заполняет форму/делает анализ
6. Переходит к следующему шагу
7. Повторяет до завершения

#### AI Automation по типам шагов

| Step Type | Метод | AI Agent | Что делает |
|-----------|-------|----------|------------|
| **FORM_INPUT** | `_auto_fill_form()` | Analytics Specialist | Анализирует контекст и заполняет форму |
| **ANALYSIS** | `_auto_analyze()` | Analytics Specialist | Проводит анализ (BIA, Risk) |
| **DECISION** | `_auto_decide()` | AI Orchestrator | Принимает решение на основе данных |
| **DOCUMENT_GENERATION** | `_auto_generate_document()` | Document Generator | Генерирует документ по шаблону |
| **APPROVAL** | `_auto_approve()` | AI System | Проверяет и утверждает (если auto_approve=True) |
| **VALIDATION** | `_auto_validate()` | Framework | Валидирует данные |

---

## Стандартные процессы

### Business Impact Analysis (BIA) - Полный workflow

```
┌─────────────────────────────────────────────────────────────┐
│ Шаг 1: Инициация BIA (FORM_INPUT)                         │
│                                                             │
│ Пользователь/AI заполняет:                                 │
│ • Область анализа (Scope)                                  │
│ • Цели BIA                                                 │
│ • Заинтересованные стороны                                 │
│ • Планируемый срок завершения                              │
│                                                             │
│ Валидация:                                                  │
│ • Scope >= 50 символов                                     │
│ • Все обязательные поля заполнены                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Шаг 2: Идентификация критичных функций (FORM_INPUT)       │
│                                                             │
│ Пользователь/AI перечисляет:                               │
│ • Бизнес-функции для анализа                               │
│ • Зависимости между функциями                              │
│                                                             │
│ Результат: Список из 5-10 критичных функций                │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Шаг 3: Анализ воздействия (ANALYSIS) - AI AGENT           │
│                                                             │
│ Analytics Specialist анализирует:                          │
│ • RTO (Recovery Time Objective) для каждой функции         │
│ • RPO (Recovery Point Objective)                           │
│ • Финансовое воздействие (Critical/High/Medium/Low)        │
│ • Репутационное воздействие                                │
│ • Регуляторное воздействие                                 │
│                                                             │
│ AI использует:                                             │
│ • Исторические данные                                      │
│ • Industry benchmarks                                      │
│ • Контекст организации                                     │
│                                                             │
│ Результат: Полная матрица воздействия                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Шаг 4: Требования к ресурсам (FORM_INPUT)                 │
│                                                             │
│ Определяются:                                               │
│ • Необходимый персонал                                     │
│ • Технологии/системы                                       │
│ • Помещения/локации                                        │
│ • Зависимости от третьих сторон                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Шаг 5: Генерация отчета (DOCUMENT_GENERATION) - AI        │
│                                                             │
│ Document Generator:                                         │
│ • Собирает все данные из шагов 1-4                         │
│ • Применяет шаблон BIA Report                              │
│ • AI обогащает данные:                                     │
│   - Executive Summary                                      │
│   - Key Findings                                           │
│   - Recommendations                                        │
│   - Priority Actions                                       │
│ • Генерирует PDF/DOCX/HTML                                 │
│                                                             │
│ Результат: Готовый BIA Report (30-50 страниц)              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Шаг 6: Утверждение (APPROVAL)                             │
│                                                             │
│ Если auto_approve=True:                                    │
│ • AI проверяет:                                            │
│   - Полноту данных                                         │
│   - ISO compliance                                         │
│   - Качество анализа                                       │
│ • Автоматически утверждает если OK                         │
│                                                             │
│ Если auto_approve=False:                                   │
│ • Отправляет уведомление Senior Management                 │
│ • Ждет утверждения человеком                               │
│                                                             │
│ Утверждающий вводит:                                       │
│ • Решение (Approved/Rejected)                              │
│ • Комментарии                                              │
│ • ФИО и должность                                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │  ЗАВЕРШЕНО    │
                  └───────────────┘
```

---

## Автоматизация

### Сценарий 1: Полностью автоматическое выполнение

```python
from process_orchestration_api import get_process_orchestrator

orchestrator = get_process_orchestrator()

# Запустить BIA автоматически
instance = await orchestrator.execute_process_automatically(
    process_id="bcm_bia_v1",
    initial_data={
        "organization": "Acme Corporation",
        "department": "IT"
    },
    user_email="admin@acme.com"
)

# Система сама:
# 1. Заполнит все формы (AI)
# 2. Проведет анализ (Analytics Specialist)
# 3. Сгенерирует документ (Document Generator)
# 4. Утвердит (если auto_approve=True)

print(f"Процесс завершен: {instance.status}")
print(f"Документ: {instance.data.get('document_path')}")
```

### Сценарий 2: Гибридное выполнение (человек + AI)

```python
framework = get_process_framework()

# Человек запускает процесс
instance = framework.start_process(
    process_id="bcm_bia_v1",
    started_by="john.doe@acme.com"
)

# Человек заполняет Шаг 1
form = framework.get_current_step_form(instance.id)
# UI показывает форму пользователю

# Пользователь вводит данные
user_data = {
    "bia_scope": "IT Infrastructure",
    "bia_objectives": "Determine RTO/RPO",
    # ...
}

framework.execute_step(instance.id, user_data, "john.doe")

# Шаг 2: AI автоматически анализирует
# (если step.ai_agent указан)
await orchestrator._auto_analyze(instance, current_step)

# Шаг 3: AI генерирует документ
# ...

# Шаг 4: Человек утверждает
# (если auto_approve=False)
```

### Сценарий 3: EventBus-driven execution

```python
# Процесс запускается по событию
@eventbus.subscribe("incident.detected")
async def on_incident(event):
    # Автоматически запустить BIA
    instance = await orchestrator.execute_process_automatically(
        process_id="bcm_bia_v1",
        initial_data={
            "trigger": "incident",
            "incident_id": event["incident_id"]
        },
        user_email="system@acme.com"
    )

    # Отправить уведомление по завершении
    await eventbus.publish("process.completed", {
        "process_id": instance.id,
        "document": instance.data.get("document_path")
    })
```

---

## API Reference

### ProcessFramework API

#### `start_process(process_id, started_by, initial_data) → ProcessInstance`
Запустить новый экземпляр процесса.

**Parameters**:
- `process_id` (str): ID процесса (e.g., "bcm_bia_v1")
- `started_by` (str): Email пользователя
- `initial_data` (dict): Начальные данные

**Returns**: ProcessInstance

#### `execute_step(instance_id, step_data, executed_by) → (success, error, next_step)`
Выполнить текущий шаг процесса.

**Parameters**:
- `instance_id` (str): ID экземпляра процесса
- `step_data` (dict): Данные формы
- `executed_by` (str): Кто выполняет

**Returns**: tuple (bool, Optional[str], Optional[str])

#### `get_current_step_form(instance_id) → dict`
Получить форму для текущего шага (для UI).

**Returns**:
```json
{
  "step_id": "bia_initiation",
  "step_name": "Инициация BIA",
  "description": "...",
  "fields": [
    {
      "name": "bia_scope",
      "label": "Область анализа",
      "type": "textarea",
      "required": true,
      "help_text": "..."
    }
  ]
}
```

#### `get_process_status(instance_id) → dict`
Получить статус процесса.

**Returns**:
```json
{
  "instance_id": "bcm_bia_v1-20251011120000",
  "process_name": "Business Impact Analysis",
  "status": "in_progress",
  "current_step_id": "impact_analysis",
  "current_step_name": "Анализ воздействия",
  "progress_percent": 50.0,
  "started_at": "2025-10-11T12:00:00",
  "completed_at": null
}
```

---

### ProcessOrchestrator API

#### `execute_process_automatically(process_id, initial_data, user_email) → ProcessInstance`
Автоматически выполнить весь процесс с помощью AI.

**How it works**:
1. Запускает процесс
2. Для каждого шага:
   - Определяет тип (Form, Analysis, Decision, etc.)
   - Вызывает соответствующий AI агент
   - AI заполняет данные
   - Переходит к следующему шагу
3. Генерирует документ
4. Утверждает (если auto_approve)
5. Возвращает завершенный instance

---

### DocumentTemplateLibrary API

#### `generate_document(template_id, variables) → str`
Сгенерировать документ по шаблону.

**Parameters**:
- `template_id` (str): ID шаблона (e.g., "bia_report_v1")
- `variables` (dict): Данные для подстановки

**Returns**: Markdown/HTML content

**Example**:
```python
library = get_document_library()

document = library.generate_document(
    template_id="bia_report_v1",
    variables={
        "organization_name": "Acme Corp",
        "analysis_date": "2025-10-11",
        "critical_functions": "...",
        # ... все переменные шаблона
    }
)

# Save to file
with open("BIA_Report.md", "w") as f:
    f.write(document)
```

---

## Примеры использования

### Пример 1: Регистрация процесса

```python
from process_framework import get_process_framework
from bcm_processes import register_all_bcm_processes

framework = get_process_framework()

# Зарегистрировать стандартные BCM процессы
register_all_bcm_processes(framework)

# Доступны процессы:
# - bcm_bia_v1
# - bcm_risk_assessment_v1
# - bcm_bc_plan_v1
```

### Пример 2: Ручное выполнение процесса

```python
# Запустить BIA
instance = framework.start_process(
    process_id="bcm_bia_v1",
    started_by="manager@company.com"
)

# Получить форму для пользователя
form = framework.get_current_step_form(instance.id)

# Пользователь заполняет форму в UI
# ...

# Отправить данные
success, error, next_step = framework.execute_step(
    instance_id=instance.id,
    step_data=user_input,
    executed_by="manager@company.com"
)

if success:
    print(f"Шаг выполнен, следующий: {next_step}")
else:
    print(f"Ошибка: {error}")
```

### Пример 3: Автоматическое выполнение

```python
from process_orchestration_api import get_process_orchestrator

orchestrator = get_process_orchestrator()

# Запустить процесс автоматически
instance = await orchestrator.execute_process_automatically(
    process_id="bcm_bia_v1",
    initial_data={
        "organization": "Acme Corp",
        "department": "IT"
    },
    user_email="system@acme.com"
)

# Процесс выполнен автоматически
print(f"Статус: {instance.status}")
print(f"Документ: {instance.data['document_path']}")
```

---

## Integration

### С AI Orchestrator

Process Orchestrator вызывает AI Orchestrator для:
- Делегирования задач AI агентам
- Заполнения форм
- Анализа данных
- Принятия решений

**Endpoint**: `POST /orchestrate`

```json
{
  "task_type": "form_auto_fill",
  "context": {
    "step_name": "Инициация BIA",
    "form_fields": [...],
    "existing_data": {...}
  },
  "preferred_agent": "analytics_specialist",
  "auto_execute": true
}
```

### С EventBus

Process Framework публикует события:
- `process.started` - Процесс запущен
- `process.step_completed` - Шаг завершен
- `process.completed` - Процесс завершен
- `process.suspended` - Процесс приостановлен
- `process.approval_required` - Требуется утверждение

**Subscribe**:
```python
@eventbus.subscribe("process.completed")
async def on_process_completed(event):
    print(f"Процесс {event['process_id']} завершен")
    # Отправить email
    # Создать задачу в Jira
    # etc.
```

### С System BCM Service

System BCM Service использует Process Framework для:
- Выполнения BCM цикла (Analyze → Plan → Do → Check → Act)
- Автоматизации BIA
- Генерации BC планов

**API**: `POST /bcm/process/start`

---

## Best Practices

### 1. Определение процессов

✅ **DO**:
- Определять четкие шаги с ясными целями
- Использовать валидацию для всех обязательных полей
- Указывать ISO clause для compliance
- Добавлять help_text для полей

❌ **DON'T**:
- Создавать слишком длинные процессы (>10 шагов)
- Пропускать валидацию
- Делать все поля обязательными

### 2. AI Automation

✅ **DO**:
- Использовать auto_approve осторожно
- Всегда логировать решения AI
- Предоставлять fallback для человека
- Тестировать AI на реальных данных

❌ **DON'T**:
- Полностью полагаться на AI без проверки
- Автоматически утверждать критичные решения
- Игнорировать ошибки AI

### 3. Документы

✅ **DO**:
- Использовать шаблоны для стандартизации
- Обогащать данные через AI
- Сохранять версии документов
- Генерировать в разных форматах (PDF, DOCX, HTML)

❌ **DON'T**:
- Генерировать документы без валидации данных
- Забывать про metadata (дата, автор, версия)

---

## Roadmap

### Phase 1: Foundation (✅ Complete)
- [x] Process Framework core
- [x] BCM standard processes
- [x] Document templates
- [x] Process Orchestrator with AI

### Phase 2: Enhancement (Q1 2026)
- [ ] UI Builder для визуального создания процессов
- [ ] BPMN 2.0 import/export
- [ ] Process analytics и reporting
- [ ] Advanced AI capabilities

### Phase 3: Enterprise (Q2 2026)
- [ ] Multi-tenant support
- [ ] Advanced workflow patterns (parallel, conditional)
- [ ] External system integrations (Jira, ServiceNow)
- [ ] Compliance automation (ISO, SOC2, GDPR)

---

## Summary

Process Framework обеспечивает:

✅ **Формализацию** бизнес-процессов с четкими шагами и валидацией
✅ **Стандартизацию** взаимодействия через единые формы
✅ **Стандартизацию** документов через шаблоны
✅ **Автоматизацию** через AI агентов
✅ **ISO 22301 compliance** из коробки

**Status**: ✅ Production Ready
**Version**: 1.0
**Date**: 2025-10-11
