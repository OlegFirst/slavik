# Module Scan Report: expertise-center

**Дата сканирования:** 2025-10-08 14:33
**Путь:** `intelligent-core/expertise-center`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 11846 |
| **Python файлов** | 63 |
| **Классов** | 58 |
| **Функций** | 27 |
| **API Endpoints** | 28 |
| **Зависимостей** | 57 |

---

## 🔗 Зависимости (57)


### abc
- `abc`

### ai_foundation
- `ai_foundation`
- `ai_foundation/expertise_center`
- `ai_foundation/intelligent_core`

### aiohttp
- `aiohttp`

### argparse
- `argparse`

### asyncio
- `asyncio`

### base_analyzer
- `base_analyzer`

### base_organ
- `base_organ`

### base_specialist
- `base_specialist`

### base_tactical_assistant
- `base_tactical_assistant`

### bia_specialist
- `bia_specialist`

### chief_executive
- `chief_executive`

### community_specialist
- `community_specialist`

### compliance_copilot
- `compliance_copilot`

### contextlib
- `contextlib`

### core
- `core`

### dataclasses
- `dataclasses`

### datetime
- `datetime`

### documents_specialist
- `documents_specialist`

### domain_loader
- `domain_loader`

### enum
- `enum`

### exercise_designer
- `exercise_designer`

### expert_registry
- `expert_registry`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### functools
- `functools`

### governance_specialist
- `governance_specialist`

### httpx
- `httpx`

### importlib
- `importlib`

### incident_advisor
- `incident_advisor`

### json
- `json`

### learning_specialist
- `learning_specialist`

### logging
- `logging`

### metrics
- `metrics`

### os
- `os`

### pathlib
- `pathlib`

### plan_generator
- `plan_generator`

### project_manager
- `project_manager`

### prometheus_client
- `prometheus_client`

### pydantic
- `pydantic`

### pytest
- `pytest`

### re
- `re`

### risk_analyst
- `risk_analyst`

### service
- `service`

### service.api.analyzers
- `service.api.analyzers`

### service.api.routes
- `service.api.routes`

### service.api.tactical
- `service.api.tactical`

### shared
- `shared/base`

### sys
- `sys`

### tactical
- `tactical`

### time
- `time`

### typing
- `typing`

### uvicorn
- `uvicorn`

### validation_specialist
- `validation_specialist`

### werkzeug.middleware.dispatcher
- `werkzeug.middleware.dispatcher`

### werkzeug.serving
- `werkzeug.serving`

---

## 🌐 API Endpoints (28)

- **GET** `/health` (файл: `standalone_main.py`)
- **GET** `/metrics` (файл: `standalone_main.py`)
- **GET** `/info` (файл: `standalone_main.py`)
- **POST** `/query` (файл: `standalone_main.py`)
- **GET** `/` (файл: `standalone_main.py`)
- **POST** `/compliance/analyze` (файл: `analyzers.py`)
- **POST** `/risk/analyze` (файл: `analyzers.py`)
- **POST** `/governance/analyze` (файл: `analyzers.py`)
- **POST** `/lifecycle/analyze` (файл: `analyzers.py`)
- **POST** `/learning/analyze` (файл: `analyzers.py`)

---

## 💻 Классы (58)

- **LearningCoach** (10 методов) - `learning_analyzer.py`
- **OrganismCoordinator** (10 методов) - `organism_coordinator.py`
- **ExpertRegistry** (9 методов) - `expert_registry.py`
- **PlanGenerator** (8 методов) - `plan_analyzer.py`
- **ComplianceGuardian** (8 методов) - `compliance_analyzer.py`
- **LifecycleMonitor** (7 методов) - `lifecycle_analyzer.py`
- **PerformanceAnalyst** (7 методов) - `performance_analyzer.py`
- **ScenarioCreator** (7 методов) - `scenario_analyzer.py`
- **GovernanceBrain** (7 методов) - `governance_analyzer.py`
- **EmergencyResponse** (6 методов) - `emergency_analyzer.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 1246 символов (67 строк)

**Превью:**
```
# expertise-center

> Доменные эксперты и тактические ассистенты

## 📊 Обзор

| Метрика | Значение |
|---------|----------|
| **Строк кода** | 7,932 |
| **Python файлов** | 45 |
| **Классов** | 47 |
| **Функций** | 8 |
| **API Endpoints** | 0 |
| **Зависимостей** | 36 |

**Тип модуля:** 📚 Library
**Последнее обновление:** 2025-10-07

---

## 🏗️ Архитектура

### Ключевые классы

- **LearningCoach** (10 методов) - `learning_analyzer.py`
- **OrganismCoordinator** (10 методов) - `organism_coordinator.py`
- **ExpertRegistry** (9 методов) - `expert_registry.py`
- **ComplianceGuardian** (8 методов) - `compliance_analyzer.py`
- **LifecycleMonitor** (7 методов) - `lifecycle_analyzer.py`

### Функции

Всего публичных функций: 8

---

## 🔗 Зависимости

### Внутренние
- `ai_foundation`
- `ai_foundation/expertise_center`
- `shared/base`

---

## 💻 Использование

### Импорт

```python
from expertise_center import ...
```

---


---

## 📚 Дополнительные материалы

- [Архитектура платформы](../../doc-
```

---

## 📂 Структура

**Всего файлов:** 90
**Директорий:** 15
