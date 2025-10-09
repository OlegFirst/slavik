# ТЗ для Агента #1 (Терминал 1)

## Задача
Создать 5 Engines + Tools по шаблону RiskEngine

## Engines для создания
1. BIA Engine (bia_engine/)
2. Compliance Engine (compliance_engine/)
3. Governance Engine (governance_engine/)
4. Emergency Engine (emergency_engine/)
5. Planning Engine (planning_engine/)

## Шаблоны

### Используй как основу:
- `/Users/MD/AI-Platform-ISO/intelligent-core/bcm_ai/engines/base_engine.py` - базовый класс
- `/Users/MD/AI-Platform-ISO/intelligent-core/bcm_ai/engines/risk_engine/risk_engine.py` - пример Engine
- `/Users/MD/AI-Platform-ISO/intelligent-core/bcm_ai/engines/risk_engine/risk_tools.py` - пример Tools

### Полное ТЗ с деталями:
`/Users/MD/AI-Platform-ISO/TZ_AI_BCM_PLATFORM.md` - секция 6.3 (Engines)

## Структура для каждого Engine

```
/Users/MD/AI-Platform-ISO/intelligent-core/bcm_ai/engines/
├── bia_engine/
│   ├── __init__.py
│   ├── bia_engine.py       # Наследник BaseEngine
│   └── bia_tools.py        # DB операции
│
├── compliance_engine/
│   ├── __init__.py
│   ├── compliance_engine.py
│   └── compliance_tools.py
│
├── governance_engine/
│   ├── __init__.py
│   ├── governance_engine.py
│   └── governance_tools.py
│
├── emergency_engine/
│   ├── __init__.py
│   ├── emergency_engine.py
│   └── emergency_tools.py
│
└── planning_engine/
    ├── __init__.py
    ├── planning_engine.py
    └── planning_tools.py
```

## Детали по каждому Engine

### 1. BIA Engine
**Файл:** `bia_engine/bia_engine.py`

**Actions:**
- `analyze_process_impact` - анализ влияния процесса
- `calculate_rto_rpo` - расчет RTO/RPO
- `map_dependencies` - картирование зависимостей
- `assess_criticality` - оценка критичности

**Tools:** `bia_tools.py`
```python
async def get_process(process_id: str) -> dict
    # SELECT * FROM bia.processes WHERE id = ?

async def save_bia_analysis(analysis: dict) -> str
    # INSERT INTO bia.impact_analysis

async def update_rto_rpo(process_id: str, rto: int, rpo: int) -> bool
    # UPDATE bia.processes SET rto_hours=?, rpo_hours=?

async def get_dependencies(process_id: str) -> list
    # SELECT * FROM bia.dependencies WHERE process_id = ?

async def save_dependency(dependency: dict) -> str
    # INSERT INTO bia.dependencies
```

### 2. Compliance Engine
**Файл:** `compliance_engine/compliance_engine.py`

**Actions:**
- `check_compliance` - проверка соответствия
- `perform_gap_analysis` - gap анализ
- `validate_evidence` - валидация доказательств
- `generate_audit_report` - генерация отчета

**Tools:** `compliance_tools.py`
```python
async def get_compliance_status(org_id: str, standard: str) -> dict
    # SELECT * FROM governance.compliance_status WHERE org_id=? AND standard=?

async def save_gap_analysis(gaps: dict) -> str
    # INSERT INTO audit.gap_analysis

async def get_evidence(clause_id: str) -> list
    # SELECT * FROM documents.evidence WHERE clause_id=?

async def save_audit_finding(finding: dict) -> str
    # INSERT INTO audit.findings
```

### 3. Governance Engine
**Файл:** `governance_engine/governance_engine.py`

**Actions:**
- `analyze_governance` - анализ governance
- `assess_policies` - оценка политик
- `evaluate_strategic_alignment` - оценка стратегического выравнивания

**Tools:** `governance_tools.py`
```python
async def get_policies(org_id: str) -> list
    # SELECT * FROM governance.policies WHERE org_id=?

async def assess_strategic_alignment(org_id: str) -> dict
    # Complex query joining governance and bia tables

async def save_governance_assessment(assessment: dict) -> str
    # INSERT INTO governance.assessments
```

### 4. Emergency Engine
**Файл:** `emergency_engine/emergency_engine.py`

**Actions:**
- `assess_incident_severity` - оценка серьезности инцидента
- `recommend_response_actions` - рекомендации по реагированию
- `escalate_incident` - эскалация инцидента

**Tools:** `emergency_tools.py`
```python
async def get_incident(incident_id: str) -> dict
    # SELECT * FROM response.incidents WHERE id=?

async def save_incident_assessment(assessment: dict) -> str
    # INSERT INTO response.incident_assessments

async def get_response_procedures(incident_type: str) -> list
    # SELECT * FROM response.procedures WHERE type=?

async def create_incident_log(log_entry: dict) -> str
    # INSERT INTO response.incident_log
```

### 5. Planning Engine
**Файл:** `planning_engine/planning_engine.py`

**Actions:**
- `generate_plan` - генерация плана (BCP/DRP/IRP)
- `validate_plan` - валидация плана
- `update_plan_section` - обновление секции плана

**Tools:** `planning_tools.py`
```python
async def get_plan_template(plan_type: str) -> dict
    # SELECT * FROM planning.templates WHERE type=?

async def save_plan(plan_data: dict) -> str
    # INSERT INTO planning.plans

async def get_process_data_for_plan(process_ids: list) -> list
    # SELECT * FROM bia.processes WHERE id IN (?)

async def validate_plan_structure(plan_id: str) -> dict
    # Validation logic
```

## Важные правила

1. **Каждый Engine:**
   - Наследует от `BaseEngine`
   - Имеет метод `execute(action, params)`
   - Использует `self._use_tool()` для DB операций
   - Использует `self._analyze_with_analyzer()` для LLM
   - Использует `self._synthesize_result()` для итогового результата

2. **Каждый Tool:**
   - Принимает `db_session` в `__init__`
   - Все методы `async`
   - Обработка ошибок с try/except
   - Возвращает данные или None при ошибке

3. **Импорты:**
```python
from typing import Dict, List, Optional, Any
from datetime import datetime
from ..base_engine import BaseEngine
```

4. **Не создавай __init__.py с кодом** - только пустые файлы

## Начинай когда готов!

После завершения сообщи в терминале: "✅ Agent 1 completed: 5 Engines created"
