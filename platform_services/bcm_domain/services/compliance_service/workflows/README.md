# Compliance Workflows - Фиксированные сценарии

Этот модуль содержит **строго определенные воркфлоу** для управления соответствием стандартам.

## Философия

Воркфлоу фиксированы и монолитны в рамках модуля для:
1. **Предсказуемости** - AI не может "придумать" свой путь
2. **Аудируемости** - каждый шаг логируется и отслеживается
3. **Соответствия стандартам** - ISO 22301 требует документированных процессов
4. **Интеграции с EventBus** - каждый переход состояния = событие

## Структура воркфлоу

Каждый воркфлоу состоит из:
- **States** - Конечные состояния (enum)
- **Transitions** - Разрешенные переходы между состояниями
- **Actions** - Действия при переходе (валидация, события, побочные эффекты)
- **Guards** - Условия для разрешения перехода
- **Events** - События EventBus, публикуемые при переходах

## Воркфлоу в модуле

### 1. Evidence Workflow
Управление свидетельствами соответствия
- States: DRAFT → SUBMITTED → UNDER_REVIEW → VERIFIED / REJECTED → ARCHIVED
- Events: evidence.created, evidence.submitted, evidence.verified, etc.

### 2. Assessment Workflow
Проведение оценок соответствия
- States: PLANNED → IN_PROGRESS → REVIEW → COMPLETED / CANCELLED
- Events: assessment.planned, assessment.started, assessment.completed, etc.

### 3. Gap Workflow
Управление пробелами в соответствии
- States: IDENTIFIED → PLANNED → IN_PROGRESS → RESOLVED → VERIFIED / ACCEPTED_RISK
- Events: gap.identified, gap.planned, gap.resolved, etc.

### 4. Nonconformity Workflow
Управление несоответствиями (NC)
- States: OPEN → ROOT_CAUSE_ANALYSIS → CORRECTIVE_ACTION → VERIFICATION → CLOSED
- Events: nc.created, nc.rca_completed, nc.action_planned, nc.verified, nc.closed

### 5. Audit Workflow
Управление аудитами
- States: PLANNED → PREPARATION → IN_PROGRESS → FINDINGS_REVIEW → COMPLETED
- Events: audit.planned, audit.started, audit.findings_submitted, audit.completed

## Использование

```python
from workflows.evidence_workflow import EvidenceWorkflow, EvidenceState

# Создание воркфлоу
workflow = EvidenceWorkflow(eventbus_client)

# Инициализация свидетельства
evidence = await workflow.initialize(
    evidence_data=data,
    tenant_id=tenant_id
)

# Переход в новое состояние
success = await workflow.transition(
    evidence_id=evidence.id,
    from_state=EvidenceState.DRAFT,
    to_state=EvidenceState.SUBMITTED,
    actor_id=user_id,
    metadata={"comment": "Ready for review"}
)
```

## Интеграция с AI

AI используется для:
1. **Рекомендаций** - какие действия выполнить
2. **Автоанализа** - извлечение информации из документов
3. **Приоритизации** - какие пробелы важнее

AI **НЕ** принимает решений о переходах состояний - это делает код на основе правил.
