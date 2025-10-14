# 🔗 Living PDCA System - Integration Plan

**Date**: 2025-10-09
**Status**: Ready to Execute

---

## 🎯 Цель

**НЕ создавать новые модули**, а **связать существующие** в единую саморазвивающуюся систему через PDCA циклы.

---

## ✅ ЧТО УЖЕ ЕСТЬ (Existing Modules)

### 1. **PDCA Infrastructure** ✅
**Location**: `intelligent-core/orchestration/pdca_assistant.py`

**Что есть**:
- ✅ PDCAPhase enum (PLAN, DO, CHECK, ACT)
- ✅ PDCAScenario (scenarios по контекстам)
- ✅ NextBestAction (рекомендации действий)
- ✅ Phase progress tracking
- ✅ EventBus integration

**Что используем**:
```python
from intelligent_core.orchestration.pdca_assistant import (
    PDCAAssistant,
    PDCAPhase,
    PDCAScenario,
    NextBestAction
)
```

### 2. **Case Library** ✅
**Locations**:
- `intelligent-core/collective/services/case_library.py` - Коллективная библиотека
- `intelligent-core/community_intelligence/services/case_library_bridge.py` - Community bridge
- `intelligent-core/workflow_intelligence/` - Workflow cases

**Что есть**:
- ✅ Case storage & retrieval
- ✅ k-anonymity (min 5 orgs)
- ✅ Success pattern extraction
- ✅ Case similarity search
- ✅ Quality scoring

**Что используем**:
```python
from intelligent_core.collective.services.case_library import CaseLibrary
from intelligent_core.workflow_intelligence.case_library import WorkflowCaseCollector
```

### 3. **Learning & Knowledge System** ✅
**Location**: `intelligent-core/ai-foundation/learning-knowledge/`

**Что есть**:
- ✅ Pattern detection
- ✅ Lesson extraction
- ✅ Knowledge base (standards, cases, lessons)
- ✅ Vector search (Qdrant)
- ✅ ML self-learning
- ✅ Competency tracking

**Что используем**:
```python
from intelligent_core.ai_foundation.learning_knowledge import (
    PatternDetector,
    LessonExtractor,
    KnowledgeBase
)
```

### 4. **Workflow Intelligence** ✅
**Location**: `intelligent-core/workflow_intelligence/`

**Что есть**:
- ✅ Temporal workflows
- ✅ State machine
- ✅ Case collector
- ✅ Benchmarking
- ✅ Cross-module learning
- ✅ ML predictions

**Что используем**:
```python
from intelligent_core.workflow_intelligence import (
    WorkflowEngine,
    CaseCollector,
    CrossModuleLearning
)
```

### 5. **AI Experts** ✅
**Location**: `intelligent-core/expertise-center/ai_experts/`

**Что есть**:
- ✅ Self-learning engine
- ✅ Pattern extractor
- ✅ Rule generator
- ✅ Case library tool
- ✅ Meta-learning engine

**Что используем**:
```python
from intelligent_core.expertise_center.ai_experts.learning import (
    SelfLearningEngine,
    PatternExtractor
)
```

---

## 🔄 ЧТО ДОБАВЛЯЕМ (Integration Layer)

### NEW: PDCA Lifecycle Coordinator

**Что делает**: Связывает все существующие модули в PDCA циклы

**Location**: `intelligent-core/pdca-lifecycle/`

**Структура**:
```python
pdca-lifecycle/
├── coordinator.py          # Главный координатор (НОВОЕ)
├── integrations/
│   ├── pdca_adapter.py     # Использует pdca_assistant.py
│   ├── case_adapter.py     # Использует case_library.py
│   ├── learning_adapter.py # Использует learning-knowledge/
│   ├── workflow_adapter.py # Использует workflow_intelligence/
│   └── expert_adapter.py   # Использует ai_experts/
├── api/
│   └── routes.py           # REST API
└── main.py                 # Service entry
```

---

## 🔗 INTEGRATION ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│             PDCA LIFECYCLE COORDINATOR (NEW)                    │
│  Единая точка входа для всех PDCA циклов                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
┌───────────────┐   ┌────────────────┐   ┌─────────────────┐
│ PDCA Assistant│   │  Case Library  │   │ Learning System │
│   (EXISTS)    │   │   (EXISTS)     │   │    (EXISTS)     │
│               │   │                │   │                 │
│ • Phases      │   │ • Cases        │   │ • Patterns      │
│ • Scenarios   │   │ • k-anonymity  │   │ • Lessons       │
│ • Actions     │   │ • Search       │   │ • Knowledge     │
└───────────────┘   └────────────────┘   └─────────────────┘
        ↓                     ↓                     ↓
┌─────────────────────────────────────────────────────────────────┐
│           Workflow Intelligence (EXISTS)                         │
│  • Temporal workflows • State machine • Benchmarking            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              AI Experts Learning (EXISTS)                        │
│  • Self-learning • Pattern extraction • Meta-learning           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 IMPLEMENTATION CODE

### 1. PDCA Lifecycle Coordinator (NEW)

```python
# intelligent-core/pdca-lifecycle/coordinator.py

from intelligent_core.orchestration.pdca_assistant import (
    PDCAAssistant, PDCAPhase, NextBestAction
)
from intelligent_core.collective.services.case_library import CaseLibrary
from intelligent_core.ai_foundation.learning_knowledge import (
    PatternDetector, LessonExtractor, KnowledgeBase
)
from intelligent_core.workflow_intelligence import (
    WorkflowEngine, CaseCollector
)
from intelligent_core.expertise_center.ai_experts.learning import (
    SelfLearningEngine
)

class PDCALifecycleCoordinator:
    """
    Координирует PDCA циклы используя СУЩЕСТВУЮЩИЕ модули

    НЕ дублирует функциональность - только связывает!
    """

    def __init__(self):
        # Используем существующие модули
        self.pdca_assistant = PDCAAssistant(config)
        self.case_library = CaseLibrary(db)
        self.pattern_detector = PatternDetector()
        self.lesson_extractor = LessonExtractor()
        self.knowledge_base = KnowledgeBase()
        self.workflow_engine = WorkflowEngine()
        self.self_learning = SelfLearningEngine()

    async def track_action(
        self,
        action_name: str,
        action_data: dict,
        user_context: dict
    ) -> dict:
        """
        Track любое действие как PDCA цикл

        Использует существующие модули!
        """

        # 1. PLAN - используем PDCA Assistant
        plan = await self.pdca_assistant.get_next_best_actions(
            context=user_context["context"]
        )

        # 2. DO - выполняет пользователь (или workflow)
        # action_data содержит результат

        # 3. CHECK - используем Pattern Detector
        patterns = await self.pattern_detector.detect_patterns(
            action_result=action_data
        )

        # Используем Case Library для сравнения
        similar_cases = await self.case_library.find_cases(
            problem_type=action_name,
            exclude_org_id=user_context["org_id"]
        )

        # 4. ACT - используем Lesson Extractor
        lessons = await self.lesson_extractor.extract(
            action_data=action_data,
            patterns=patterns,
            similar_cases=similar_cases
        )

        # Сохраняем в Knowledge Base
        await self.knowledge_base.save_lesson(lessons)

        # Обновляем ML models через Self-Learning
        if lessons.success:
            await self.self_learning.add_training_example(
                action_name=action_name,
                action_data=action_data,
                outcome=lessons
            )

        return {
            "cycle_complete": True,
            "patterns_detected": len(patterns),
            "lessons_learned": len(lessons),
            "similar_cases_found": len(similar_cases),
            "knowledge_updated": True
        }
```

### 2. Decorator для Tracking (NEW)

```python
# intelligent-core/pdca-lifecycle/decorators.py

from functools import wraps
from .coordinator import PDCALifecycleCoordinator

coordinator = PDCALifecycleCoordinator()

def pdca_tracked(action_name: str, level: str = "micro"):
    """
    Decorator для автоматического PDCA tracking

    Использует существующие модули через coordinator!
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Выполняем оригинальную функцию
            result = await func(*args, **kwargs)

            # Трекаем как PDCA цикл (в фоне)
            context = kwargs.get("context", {})

            await coordinator.track_action(
                action_name=action_name,
                action_data=result,
                user_context=context
            )

            return result
        return wrapper
    return decorator
```

### 3. Использование в существующем коде

```python
# platform-services/bia-service/api.py (СУЩЕСТВУЮЩИЙ КОД)

from pdca_lifecycle.decorators import pdca_tracked

# Просто добавляем decorator!
@pdca_tracked(action_name="bia_completion", level="micro")
async def complete_bia(bia_id: str, user_id: str):
    """
    Существующая функция БЕЗ изменений
    Только добавили decorator
    """
    result = await bia_service.complete(bia_id)
    return result

# PDCA цикл происходит автоматически:
# - Case сохраняется в Case Library
# - Patterns детектятся через Pattern Detector
# - Lessons извлекаются через Lesson Extractor
# - Knowledge обновляется в Knowledge Base
# - ML models обучаются через Self-Learning Engine
```

### 4. Workflow Integration

```python
# intelligent-core/workflow_intelligence/core/workflow_engine.py

from pdca_lifecycle.coordinator import PDCALifecycleCoordinator

class WorkflowEngine:
    """СУЩЕСТВУЮЩИЙ класс - минимальные изменения"""

    def __init__(self):
        # Существующая инициализация
        # ...

        # ДОБАВЛЯЕМ только coordinator
        self.pdca_coordinator = PDCALifecycleCoordinator()

    async def complete_workflow(self, workflow_id: str):
        """СУЩЕСТВУЮЩИЙ метод - добавляем PDCA tracking"""

        # Существующая логика
        result = await self._execute_workflow(workflow_id)

        # ДОБАВЛЯЕМ только одну строку!
        await self.pdca_coordinator.track_action(
            action_name="workflow_completion",
            action_data=result,
            user_context={"workflow_id": workflow_id}
        )

        return result
```

---

## 📋 IMPLEMENTATION PHASES

### Phase 1: Core Integration (Week 1)

**Goal**: Связать существующие модули

**Tasks**:
1. ✅ Create PDCA Lifecycle Coordinator
2. ✅ Create adapters для существующих модулей
3. ✅ Create @pdca_tracked decorator
4. ✅ Write integration tests

**Files to create**:
- `intelligent-core/pdca-lifecycle/coordinator.py` (200 lines)
- `intelligent-core/pdca-lifecycle/decorators.py` (50 lines)
- `intelligent-core/pdca-lifecycle/integrations/*.py` (5 files × 100 lines)

**Files to modify**:
- NONE! (только добавляем decorators при использовании)

### Phase 2: Micro PDCA (Week 2)

**Goal**: Каждое действие = PDCA цикл

**Tasks**:
1. Add @pdca_tracked to BIA service
2. Add @pdca_tracked to Risk service
3. Add @pdca_tracked to BCP service
4. Monitor & verify cycles working

**Modifications**:
```python
# platform-services/bia-service/api.py
# Добавить только import + decorator

from pdca_lifecycle.decorators import pdca_tracked

@pdca_tracked("bia_completion")
async def complete_bia(...):
    # Existing code unchanged
```

**Impact**: Minimal (1 line per action)

### Phase 3: Workflow PDCA (Week 3)

**Goal**: Workflows = PDCA циклы

**Tasks**:
1. Integrate coordinator into Workflow Intelligence
2. Track workflow completions
3. Extract workflow-level lessons

**Modifications**:
```python
# intelligent-core/workflow_intelligence/core/workflow_engine.py
# Add coordinator initialization + 1 line on completion

self.pdca_coordinator = PDCALifecycleCoordinator()

# On workflow complete:
await self.pdca_coordinator.track_action(...)
```

**Impact**: Minimal (2-3 lines)

### Phase 4: Continuous Evolution (Week 4+)

**Goal**: Система эволюционирует автоматически

**Tasks**:
1. Monitor accumulated patterns
2. Verify ML models improving
3. Check knowledge growth
4. Measure platform intelligence

**Modifications**: NONE (all automatic!)

---

## 🎯 KEY BENEFITS

### ✅ Минимальные изменения существующего кода
- Только добавляем decorators
- Существующие модули работают как есть
- Не нужно переписывать логику

### ✅ Максимальное переиспользование
- PDCA Assistant (уже есть)
- Case Library (уже есть)
- Learning System (уже есть)
- Workflow Intelligence (уже есть)
- AI Experts (уже есть)

### ✅ Прозрачная интеграция
- Coordinat

or связывает модули
- Каждый модуль делает свою работу
- Никакого дублирования кода

### ✅ Автоматическое накопление знаний
- Cases → Case Library
- Patterns → Pattern Detector
- Lessons → Knowledge Base
- ML training → Self-Learning Engine

---

## 📊 METRICS TO TRACK

```python
# Metrics автоматически собираются из существующих модулей

metrics = {
    # From Case Library
    "total_cases": await case_library.count_cases(),

    # From Pattern Detector
    "patterns_detected": await pattern_detector.count_patterns(),

    # From Knowledge Base
    "lessons_stored": await knowledge_base.count_lessons(),

    # From Self-Learning
    "ml_accuracy": await self_learning.get_accuracy(),

    # From Workflow Intelligence
    "workflows_completed": await workflow_engine.count_completions(),

    # From PDCA Coordinator (new)
    "pdca_cycles_total": coordinator.cycles_count,
    "pdca_cycles_active": coordinator.active_cycles,
    "knowledge_reuse_rate": coordinator.knowledge_reuse_rate
}
```

---

## 🚀 READY TO START?

**Estimated Time**: 4 weeks
**Code to Write**: ~1,500 lines (coordinator + adapters)
**Code to Modify**: Minimal (decorators only)
**Risk**: Low (не трогаем существующую логику)

**Next Step**: Создать `pdca-lifecycle/coordinator.py`?

---

✅ **План готов!** Используем ВСЕ существующие модули - просто связываем их в единую систему через PDCA циклы!
