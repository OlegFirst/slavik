# V7 MIGRATION PLAN - БЕЗ УДАЛЕНИЯ!

**Дата**: 2025-10-06
**Принцип**: КОПИРУЕМ, НЕ ПЕРЕМЕЩАЕМ! Старый код остается как reference.

---

## 📊 ТЕКУЩЕЕ СОСТОЯНИЕ

### Что у нас есть (НЕ ТРОГАЕМ!):

```
intelligent-core/
│
├─ ai_experts/                    # ✅ ОСТАВЛЯЕМ (source для ai-foundation)
│  ├─ rag/ (1,368 LOC)
│  ├─ ml/ (1,127 LOC)
│  ├─ learning/ (619 LOC)
│  ├─ tools/ (2,747 LOC)
│  ├─ specialists/ (3 специалиста)
│  └─ knowledge/
│
├─ ai-office/                     # ✅ ОСТАВЛЯЕМ (source для expertise-center)
│  ├─ ВСМ-colleagues/ (7 colleagues)
│  ├─ organs/ (10 organs)
│  ├─ core/rag/
│  ├─ core/learning/
│  └─ llm/
│
├─ expertise-center/              # ⚠️ ПРОБНАЯ ВЕРСИЯ (19 файлов)
│  ├─ core/
│  ├─ shared/
│  └─ domains/
│
├─ bcm_offices/                   # ⚠️ ПРОБНАЯ ВЕРСИЯ (7 файлов)
│  └─ risk/
│
├─ ai_platform/                   # ⚠️ ПРОБНАЯ ВЕРСИЯ (12 файлов)
│  ├─ chief/
│  ├─ experts/
│  ├─ managers/
│  ├─ organs/
│  ├─ shared/
│  └─ tools/
│
└─ coordination-center/           # ✅ ИСПОЛЬЗУЕМ (14 файлов)
   ├─ intent_parser.py
   ├─ api_executor.py
   └─ security_layer.py
```

---

## 🎯 ПЛАН V7 МИГРАЦИИ

### ПРАВИЛО: Копируем код, старые папки НЕ трогаем!

---

## PHASE 1: Создать ai-foundation (4-6 часов)

### Шаг 1.1: Создать структуру

```bash
mkdir -p intelligent-core/ai-foundation/{rag,ml,learning,context,llm,tests}
```

### Шаг 1.2: Копировать RAG

```bash
# Копируем (НЕ перемещаем!) из ai_experts
cp -r intelligent-core/ai_experts/rag/* intelligent-core/ai-foundation/rag/

# Merge с ai-office/core/rag (если есть уникальный код)
# Вручную смотрим что добавить из ai-office/core/rag/
```

### Шаг 1.3: Копировать ML

```bash
# Копируем из ai_experts
cp -r intelligent-core/ai_experts/ml/* intelligent-core/ai-foundation/ml/

# Добавляем community predictor из community_intelligence
cp intelligent-core/community_intelligence/services/ml_predictor.py \
  intelligent-core/ai-foundation/ml/community_predictor.py
```

### Шаг 1.4: Копировать Learning

```bash
# Копируем из ai_experts
cp -r intelligent-core/ai_experts/learning/* intelligent-core/ai-foundation/learning/

# Merge с ai-office/core/learning (если есть уникальный код)
```

### Шаг 1.5: Копировать LLM

```bash
# Копируем из ai-office
cp -r intelligent-core/ai-office/llm/* intelligent-core/ai-foundation/llm/
```

### Шаг 1.6: Создать Context

```bash
# Копируем из community_intelligence
cp intelligent-core/community_intelligence/services/unified_ai_context.py \
  intelligent-core/ai-foundation/context/context_builder.py

cp intelligent-core/community_intelligence/services/unified_ai_context.py \
  intelligent-core/ai-foundation/context/context_aggregator.py
```

### Шаг 1.7: Создать __init__.py

```bash
# intelligent-core/ai-foundation/__init__.py
cat > intelligent-core/ai-foundation/__init__.py << 'EOF'
"""
AI Foundation - Core AI Infrastructure

Provides RAG, ML, Learning, Context, LLM for entire platform.
"""

from .rag import RAGPipeline
from .ml import MLPredictor
from .learning import SelfLearningEngine
from .context import ContextBuilder
from .llm import LLMClient

__all__ = [
    'RAGPipeline',
    'MLPredictor',
    'SelfLearningEngine',
    'ContextBuilder',
    'LLMClient',
]

__version__ = '1.0.0'
EOF
```

**РЕЗУЛЬТАТ PHASE 1**:
- ✅ ai-foundation создан
- ✅ Старый код в ai_experts и ai-office НЕ ТРОНУТ

---

## PHASE 2: Обновить workflow_intelligence (2-3 часа)

### Шаг 2.1: Создать services (только workflow-specific)

```bash
mkdir -p intelligent-core/workflow_intelligence/services/{case_library,journey,anomaly}
```

### Шаг 2.2: Копировать case_library

```bash
# Копируем существующий case_library
cp -r intelligent-core/workflow_intelligence/case_library/* \
  intelligent-core/workflow_intelligence/services/case_library/
```

### Шаг 2.3: Копировать journey

```bash
# Копируем из predictive
cp intelligent-core/predictive/services/journey_predictor.py \
  intelligent-core/workflow_intelligence/services/journey/journey_predictor.py

cp intelligent-core/predictive/services/journey_predictor.py \
  intelligent-core/workflow_intelligence/services/journey/timeline_engine.py
```

### Шаг 2.4: Копировать anomaly

```bash
# Копируем из collective
cp intelligent-core/collective/services/stuck_detector_service.py \
  intelligent-core/workflow_intelligence/services/anomaly/stuck_detector.py
```

### Шаг 2.5: Обновить __init__.py

```bash
# intelligent-core/workflow_intelligence/__init__.py
cat > intelligent-core/workflow_intelligence/__init__.py << 'EOF'
"""
Workflow Intelligence - THE BRAIN

Workflow engine with managed autonomy.
"""

# Core
from .core.engine import WorkflowEngine
from .core.state_machine import StateMachine
from .core.governance import Governance

# Workflow-specific services
from .services.case_library import CaseRepository
from .services.journey import JourneyPredictor
from .services.anomaly import StuckDetector

__all__ = [
    'WorkflowEngine',
    'StateMachine',
    'Governance',
    'CaseRepository',
    'JourneyPredictor',
    'StuckDetector',
]

__version__ = '5.0.0'
EOF
```

**РЕЗУЛЬТАТ PHASE 2**:
- ✅ workflow_intelligence обновлен
- ✅ Только workflow-specific services
- ✅ Старый код НЕ ТРОНУТ

---

## PHASE 3: Создать expertise-center (4-6 часов)

### Шаг 3.1: Создать структуру

```bash
# Удаляем пробную версию expertise-center
rm -rf intelligent-core/expertise-center

# Создаем заново
mkdir -p intelligent-core/expertise-center/{core,shared,domains}
mkdir -p intelligent-core/expertise-center/shared/{base,tools}
mkdir -p intelligent-core/expertise-center/domains/bcm/{specialists,colleagues,analyzers,knowledge}
```

### Шаг 3.2: Копировать Base classes

```bash
# Из ai_experts
cp intelligent-core/ai_experts/base/* \
  intelligent-core/expertise-center/shared/base/

# Merge с ai-office/base (если есть)
# Вручную проверяем ai-office/base/ и добавляем уникальное
```

### Шаг 3.3: Копировать Tools

```bash
# Из ai_experts
cp -r intelligent-core/ai_experts/tools/* \
  intelligent-core/expertise-center/shared/tools/
```

### Шаг 3.4: Копировать Specialists (3)

```bash
# Из ai_experts/specialists
cp intelligent-core/ai_experts/specialists/bcm_advisor.py \
  intelligent-core/expertise-center/domains/bcm/specialists/

cp intelligent-core/ai_experts/specialists/compliance_auditor.py \
  intelligent-core/expertise-center/domains/bcm/specialists/

cp intelligent-core/ai_experts/specialists/strategic_planner.py \
  intelligent-core/expertise-center/domains/bcm/specialists/
```

### Шаг 3.5: Копировать Colleagues (7)

```bash
# Из ai-office/ВСМ-colleagues
cp -r intelligent-core/ai-office/ВСМ-colleagues/bia_specialist \
  intelligent-core/expertise-center/domains/bcm/colleagues/bia_specialist

cp -r intelligent-core/ai-office/ВСМ-colleagues/risk_analyst \
  intelligent-core/expertise-center/domains/bcm/colleagues/risk_analyst

cp -r intelligent-core/ai-office/ВСМ-colleagues/project_manager \
  intelligent-core/expertise-center/domains/bcm/colleagues/project_manager

cp -r intelligent-core/ai-office/ВСМ-colleagues/incident_advisor \
  intelligent-core/expertise-center/domains/bcm/colleagues/incident_advisor

cp -r intelligent-core/ai-office/ВСМ-colleagues/plan_generator \
  intelligent-core/expertise-center/domains/bcm/colleagues/plan_generator

cp -r intelligent-core/ai-office/ВСМ-colleagues/compliance_copilot \
  intelligent-core/expertise-center/domains/bcm/colleagues/compliance_copilot

cp -r intelligent-core/ai-office/ВСМ-colleagues/exercise_designer \
  intelligent-core/expertise-center/domains/bcm/colleagues/exercise_designer
```

### Шаг 3.6: Копировать Analyzers (10) - переименовываем!

```bash
# Из ai-office/organs → analyzers
cp intelligent-core/ai-office/organs/governance_brain.py \
  intelligent-core/expertise-center/domains/bcm/analyzers/governance_analyzer.py

cp intelligent-core/ai-office/organs/impact_oracle.py \
  intelligent-core/expertise-center/domains/bcm/analyzers/impact_analyzer.py

cp intelligent-core/ai-office/organs/risk_advisor.py \
  intelligent-core/expertise-center/domains/bcm/analyzers/risk_analyzer.py

cp intelligent-core/ai-office/organs/compliance_guardian.py \
  intelligent-core/expertise-center/domains/bcm/analyzers/compliance_analyzer.py

cp intelligent-core/ai-office/organs/emergency_response.py \
  intelligent-core/expertise-center/domains/bcm/analyzers/emergency_analyzer.py

cp intelligent-core/ai-office/organs/scenario_creator.py \
  intelligent-core/expertise-center/domains/bcm/analyzers/scenario_analyzer.py

cp intelligent-core/ai-office/organs/performance_analyst.py \
  intelligent-core/expertise-center/domains/bcm/analyzers/performance_analyzer.py

cp intelligent-core/ai-office/organs/learning_coach.py \
  intelligent-core/expertise-center/domains/bcm/analyzers/learning_analyzer.py

cp intelligent-core/ai-office/organs/plan_generator.py \
  intelligent-core/expertise-center/domains/bcm/analyzers/plan_analyzer.py

cp intelligent-core/ai-office/organs/lifecycle_monitor.py \
  intelligent-core/expertise-center/domains/bcm/analyzers/lifecycle_analyzer.py
```

### Шаг 3.7: Копировать Knowledge

```bash
# Из ai_experts
cp -r intelligent-core/ai_experts/knowledge/* \
  intelligent-core/expertise-center/domains/bcm/knowledge/
```

**РЕЗУЛЬТАТ PHASE 3**:
- ✅ expertise-center создан с нуля (пробная версия удалена)
- ✅ Все AI агенты скопированы
- ✅ Organs → Analyzers (переименовано)
- ✅ Старый код в ai_experts и ai-office НЕ ТРОНУТ

---

## PHASE 4: Обновить импорты (3-4 часа)

### Файлы для обновления:

**1. bcm_offices/risk/ai/expert.py**
```python
# ДО:
from workflow_intelligence.integration.ai_context_builder import AIContextBuilder
from workflow_intelligence.core.case_library.repository import CaseLibraryRepository

# ПОСЛЕ:
from ai_foundation.context import ContextBuilder
from workflow_intelligence.services.case_library import CaseRepository
```

**2. predictive/integration/dependencies.py**
```python
# ДО:
from workflow_intelligence.case_library.repository import CaseRepository

# ПОСЛЕ:
from workflow_intelligence.services.case_library import CaseRepository
```

**3. Все Specialists/Colleagues/Analyzers**
```python
# ДО:
from ai_experts.base import BaseExpert
from ai_experts.rag import RAGPipeline
from ai_experts.ml import WorkflowPredictor

# ПОСЛЕ:
from expertise_center.shared.base import BaseSpecialist  # или BaseColleague, BaseAnalyzer
from ai_foundation.rag import RAGPipeline
from ai_foundation.ml import MLPredictor
```

---

## PHASE 5: Тестирование (2-3 часа)

```bash
# Test ai-foundation
python3 -m pytest intelligent-core/ai-foundation/tests/ -v

# Test workflow_intelligence
python3 -m pytest intelligent-core/workflow_intelligence/tests/ -v

# Test expertise-center
python3 -m pytest intelligent-core/expertise-center/tests/ -v

# Integration tests
python3 -m pytest tests/integration/ -v
```

---

## PHASE 6: Документация (1 час)

Создать:
- ai-foundation/README.md
- workflow_intelligence/README.md (обновить)
- expertise-center/README.md

---

## 📦 ЧТО НЕ ТРОГАЕМ (Reference Code)

### Оставляем КАК ЕСТЬ:

```
intelligent-core/
├─ ai_experts/              # ✅ REFERENCE - оставляем
├─ ai-office/               # ✅ REFERENCE - оставляем
├─ ai_platform/             # ✅ REFERENCE - оставляем (пробная версия)
├─ bcm_offices/             # ✅ REFERENCE - оставляем (пробная версия)
├─ coordination-center/     # ✅ ИСПОЛЬЗУЕМ - не трогаем
├─ predictive/              # ✅ REFERENCE - оставляем
├─ collective/              # ✅ REFERENCE - оставляем
└─ community_intelligence/  # ✅ REFERENCE - оставляем
```

**Почему оставляем:**
- Reference для разработчиков
- Backup на случай проблем
- История развития
- Можно сравнивать код

**Когда архивировать:**
- ТОЛЬКО после 1-2 месяцев успешной работы V7
- ТОЛЬКО когда уверены что всё работает
- ТОЛЬКО с полным тестированием

---

## 📊 ИТОГОВАЯ СТРУКТУРА (после миграции)

```
intelligent-core/
│
├─ ai-foundation/                   # ✅ НОВОЕ (V7)
│  ├─ rag/
│  ├─ ml/
│  ├─ learning/
│  ├─ context/
│  └─ llm/
│
├─ workflow_intelligence/           # ✅ ОБНОВЛЕНО (V7)
│  ├─ core/
│  └─ services/
│     ├─ case_library/
│     ├─ journey/
│     └─ anomaly/
│
├─ expertise-center/                # ✅ НОВОЕ (V7)
│  ├─ core/
│  ├─ shared/
│  └─ domains/bcm/
│     ├─ specialists/
│     ├─ colleagues/
│     └─ analyzers/
│
├─ coordination-center/             # ✅ БЕЗ ИЗМЕНЕНИЙ
│
├─ ai_experts/                      # 📦 REFERENCE (не трогаем)
├─ ai-office/                       # 📦 REFERENCE (не трогаем)
├─ ai_platform/                     # 📦 REFERENCE (не трогаем)
├─ bcm_offices/                     # 📦 REFERENCE (не трогаем)
├─ predictive/                      # 📦 REFERENCE (не трогаем)
├─ collective/                      # 📦 REFERENCE (не трогаем)
└─ community_intelligence/          # 📦 REFERENCE (не трогаем)
```

---

## ⏱️ TIMELINE

**TOTAL: 16-23 часа (~2-3 рабочих дня)**

| Phase | Задача | Время |
|-------|--------|-------|
| 1 | ai-foundation | 4-6 часов |
| 2 | workflow_intelligence | 2-3 часа |
| 3 | expertise-center | 4-6 часов |
| 4 | Обновить импорты | 3-4 часа |
| 5 | Тестирование | 2-3 часа |
| 6 | Документация | 1 час |

---

## ✅ CHECKLIST

### Перед стартом:
- [ ] Сделать git commit всего текущего кода
- [ ] Создать ветку `feature/v7-architecture`
- [ ] Backup базы данных (если есть данные)

### После миграции:
- [ ] Все тесты проходят
- [ ] Импорты обновлены
- [ ] Документация создана
- [ ] Code review
- [ ] Merge в main

### Через 1-2 месяца:
- [ ] V7 стабильно работает
- [ ] Нет регрессий
- [ ] Можно архивировать старый код

---

## 🚀 ГОТОВЫ НАЧАТЬ?

**Следующий шаг**:
```bash
# 1. Commit текущий код
git add .
git commit -m "Before V7 migration"

# 2. Создать ветку
git checkout -b feature/v7-architecture

# 3. Начать Phase 1
mkdir -p intelligent-core/ai-foundation/{rag,ml,learning,context,llm,tests}
```

**Начинаем?**
