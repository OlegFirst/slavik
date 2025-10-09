# Техническое Задание для Параллельной Работы

**Дата**: 2025-10-06
**Для**: Второй Claude (параллельная сессия)
**Проект**: AI-Powered BCM Platform
**Архитектура**: V7 Improved

---

## 📋 Контекст

Мы собираем платформу по архитектуре V7. Уже готово:

### ✅ Что Сделано (основная сессия):

1. **Layer 1: Infrastructure** ✅
   - Supabase (PostgreSQL) настроен
   - Redis (Upstash) настроен
   - Qdrant настроен

2. **Layer 2: Shared Libraries** ✅
   - `/shared/` полностью готов (auth, database, cache, eventbus, utils)

3. **Layer 3: ai-foundation** ✅ (только что создан)
   - `/intelligent-core/ai-foundation/` с RAG, ML, Learning, Context, LLM
   - Последний коммит: `699f3eb`

4. **Layer 3: workflow_intelligence** ⚠️ (в процессе)
   - Структура готова, нужна интеграция с ai-foundation

---

## 🎯 Твоя Задача: expertise-center

### Цель:
Реорганизовать и настроить `expertise-center/` по архитектуре V7.

### Текущее Состояние:

```
/intelligent-core/expertise-center/
├── ai-office/         # Старый код (нужно разобрать)
└── ai_experts/        # Старый код (нужно разобрать)
```

### Целевая Структура (из FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md):

```
/intelligent-core/expertise-center/
│
├── core/                      # Plugin Manager Core
│   ├── chief_executive.py     # Main orchestrator
│   ├── domain_loader.py       # Plugin loader
│   ├── expert_registry.py     # Expert registry
│   └── coordinator.py
│
├── shared/                    # Shared for Domain Plugins
│   ├── base/                  # Base Classes
│   │   ├── base_specialist.py # Strategic AI
│   │   ├── base_colleague.py  # Tactical AI
│   │   ├── base_analyzer.py   # Heavy AI
│   │   ├── base_tool.py
│   │   └── base_domain.py
│   │
│   └── tools/                 # Domain Tools (2,747 LOC)
│       ├── bia_tools.py
│       ├── compliance_tools.py
│       ├── strategic_tools.py
│       └── case_library_tool.py
│
└── domains/                   # 🔌 DOMAIN PLUGINS
    │
    └── bcm/                   # BCM Domain Plugin
        │
        ├── specialists/       # 🎯 Strategic Experts (3)
        │   ├── bcm_advisor.py
        │   ├── compliance_auditor.py
        │   └── strategic_planner.py
        │
        ├── colleagues/        # 💬 Tactical Assistants (7)
        │   ├── bia_specialist.py
        │   ├── risk_analyst.py
        │   ├── project_manager.py
        │   ├── incident_advisor.py
        │   ├── plan_generator.py
        │   ├── compliance_copilot.py
        │   └── exercise_designer.py
        │
        ├── analyzers/         # 🧠 Heavy AI Analyzers (10)
        │   ├── governance_analyzer.py
        │   ├── impact_analyzer.py
        │   ├── risk_analyzer.py
        │   ├── compliance_analyzer.py
        │   ├── emergency_analyzer.py
        │   ├── scenario_analyzer.py
        │   ├── performance_analyzer.py
        │   ├── learning_analyzer.py
        │   ├── plan_analyzer.py
        │   └── lifecycle_analyzer.py
        │
        ├── knowledge/         # BCM Knowledge
        │   ├── iso_22301/
        │   ├── bci_guidelines/
        │   └── best_practices/
        │
        └── services_config.py
```

---

## 📝 Пошаговый План:

### Шаг 1: Создать структуру директорий

```bash
mkdir -p intelligent-core/expertise-center/{core,shared,domains}
mkdir -p intelligent-core/expertise-center/shared/{base,tools}
mkdir -p intelligent-core/expertise-center/domains/bcm/{specialists,colleagues,analyzers,knowledge}
```

### Шаг 2: Разобрать ai_experts/

**Источник**: `/intelligent-core/expertise-center/ai_experts/`

**Куда переносить**:

1. **Base Classes** (`ai_experts/base/`) → `expertise-center/shared/base/`
   - Переименовать классы:
     - `BaseExpert` → `BaseSpecialist`
     - Создать `BaseColleague` (похож на BaseSpecialist, но tactical)
     - Создать `BaseAnalyzer` (похож на BaseSpecialist, но heavy AI)

2. **Tools** (`ai_experts/tools/`) → `expertise-center/shared/tools/`
   - Скопировать как есть

3. **Specialists** (`ai_experts/specialists/`) → `expertise-center/domains/bcm/specialists/`
   - 3 файла: bcm_advisor.py, compliance_auditor.py, strategic_planner.py

4. **Knowledge** (`ai_experts/knowledge/`) → `expertise-center/domains/bcm/knowledge/`
   - Скопировать как есть

### Шаг 3: Разобрать ai-office/

**Источник**: `/intelligent-core/expertise-center/ai-office/`

**Куда переносить**:

1. **ВСМ-colleagues/** → `expertise-center/domains/bcm/colleagues/`
   - 7 файлов colleagues

2. **organs/** → `expertise-center/domains/bcm/analyzers/`
   - 10 файлов analyzers
   - ⚠️ **Важно**: Переименовать все упоминания "organ" → "analyzer" в коде

### Шаг 4: Создать Core файлы

Создай базовые файлы (можно заглушки):

1. `core/chief_executive.py` - main orchestrator
2. `core/domain_loader.py` - plugin loader
3. `core/expert_registry.py` - expert registry
4. `core/coordinator.py` - coordination logic

### Шаг 5: Создать __init__.py

**expertise-center/__init__.py**:
```python
"""
Expertise Center - Domain Plugin Manager

Manages domain plugins with AI specialists, colleagues, and analyzers.
"""

from .core.chief_executive import ChiefExecutiveAI
from .core.domain_loader import DomainLoader
from .core.expert_registry import ExpertRegistry

from .shared.base import BaseSpecialist, BaseColleague, BaseAnalyzer

__all__ = [
    'ChiefExecutiveAI',
    'DomainLoader',
    'ExpertRegistry',
    'BaseSpecialist',
    'BaseColleague',
    'BaseAnalyzer',
]

__version__ = '1.0.0'
```

### Шаг 6: Обновить импорты

Во всех перенесённых файлах заменить:

```python
# Старое:
from ai_experts.base import BaseExpert
from ai_experts.rag import RAGPipeline

# Новое:
from expertise_center.shared.base import BaseSpecialist
from ai_foundation import RAGPipeline
```

### Шаг 7: Создать README.md

В `expertise-center/README.md` описать:
- Что это
- Структуру (3-tier hierarchy)
- Как использовать
- Примеры кода

---

## 🔗 Зависимости

expertise-center должен использовать:

1. **ai-foundation** (уже готов):
   ```python
   from ai_foundation import RAGPipeline, MLPredictor, LLMRouter
   ```

2. **shared** (уже готов):
   ```python
   from shared.database import get_db
   from shared.cache import cached
   from shared.auth import get_current_user
   ```

---

## ⚠️ Важные Правила:

1. **НЕ удалять старые папки** (`ai_experts`, `ai-office`)
   - После переноса переместить в `_archive/`

2. **Документация**:
   - Промежуточная → `/doc-project/`
   - Финальная → прямо в `expertise-center/`

3. **Не коммитить**:
   - `venv/`
   - `htmlcov/`
   - `__pycache__/`
   - `.DS_Store`

4. **Коммит после завершения**:
   ```bash
   git add intelligent-core/expertise-center/
   git commit -m "feat: reorganize expertise-center (V7 architecture)

   - Created plugin architecture (core, shared, domains)
   - 3-tier hierarchy: specialists (3), colleagues (7), analyzers (10)
   - Integrated with ai-foundation and shared/
   - Moved old code to _archive/

   🤖 Generated with Claude Code"
   ```

---

## 📚 Справочные Документы:

1. `/doc-project/FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md` - полная архитектура
2. `/intelligent-core/ai-foundation/README.md` - как использовать ai-foundation
3. `/shared/README.md` - как использовать shared/

---

## ✅ Критерии Готовности:

- [ ] Структура директорий создана
- [ ] ai_experts/ разобран и перенесён
- [ ] ai-office/ разобран и перенесён
- [ ] Core файлы созданы (минимум заглушки)
- [ ] __init__.py создан
- [ ] README.md создан
- [ ] Импорты обновлены (ai-foundation, shared)
- [ ] Старый код в _archive/
- [ ] Коммит сделан

---

## 🤝 Координация:

После завершения дай знать в чате:
- Что сделано
- Какие проблемы возникли
- Какие решения принял

Мы синхронизируемся и продолжим дальше вместе!

---

**Удачи!** 🚀

P.S. Если что-то непонятно - задавай вопросы в чате.
