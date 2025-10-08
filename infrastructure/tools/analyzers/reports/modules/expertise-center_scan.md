# Module Scan Report: expertise-center

**Дата сканирования:** 2025-10-06 21:10
**Путь:** `intelligent-core/expertise-center`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 7932 |
| **Python файлов** | 45 |
| **Классов** | 47 |
| **Функций** | 8 |
| **API Endpoints** | 0 |
| **Зависимостей** | 36 |

---

## 🔗 Зависимости (36)


### abc
- `abc`

### ai_foundation
- `ai_foundation`
- `ai_foundation/expertise_center`

### aiohttp
- `aiohttp`

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

### pathlib
- `pathlib`

### plan_generator
- `plan_generator`

### project_manager
- `project_manager`

### re
- `re`

### risk_analyst
- `risk_analyst`

### shared
- `shared/base`

### sys
- `sys`

### typing
- `typing`

### validation_specialist
- `validation_specialist`

---

## 💻 Классы (47)

- **LearningCoach** (10 методов) - `learning_analyzer.py`
- **OrganismCoordinator** (10 методов) - `organism_coordinator.py`
- **ExpertRegistry** (9 методов) - `expert_registry.py`
- **ComplianceGuardian** (8 методов) - `compliance_analyzer.py`
- **LifecycleMonitor** (7 методов) - `lifecycle_analyzer.py`
- **PerformanceAnalyst** (7 методов) - `performance_analyzer.py`
- **ScenarioCreator** (7 методов) - `scenario_analyzer.py`
- **GovernanceBrain** (7 методов) - `governance_analyzer.py`
- **EmergencyResponse** (6 методов) - `emergency_analyzer.py`
- **ExpertRegistry** (6 методов) - `organism_coordinator.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 5533 символов (211 строк)

**Превью:**
```
# Expertise Center

Domain Plugin Manager for AI-Powered BCM Platform

## Overview

Expertise Center manages domain-specific AI experts:
- **Specialists** - Strategic experts (deep analysis, strategic recommendations)
- **Tactical Assistants** - Tactical assistants (specific tasks, quick answers)
- **Analyzers** - Heavy AI (deep data analysis, pattern recognition)

## Architecture

```
expertise-center/
├── core/                    # Plugin Manager Core
│   ├── chief_executive.py   # Main orchestrator
│   ├── domain_loader.py     # Plugin loader
│   └── expert_registry.py   # Expert registry
│
├── shared/                  # Shared for Domain Plugins
│   ├── base/               # Base Classes
│   │   ├── base_specialist.py
│   │   ├── base_tactical_assistant.py
│   │   └── base_analyzer.py
│   └── tools/              # Domain Tools
│
└── domains/                # Domain Plugins
    └── bcm/               # BCM Domain
        ├── specialists/   # 3 Strategic Experts
        ├── tactical_
```

---

## 📂 Структура

**Всего файлов:** 56
**Директорий:** 9
