# 🗺️ Где Находится unified-workflow?

**Последнее обновление:** 2025-10-05 21:10

---

## 📍 ТЕКУЩЕЕ МЕСТОПОЛОЖЕНИЕ

```
/Users/MD/AI-Platform-ISO/intelligent-core/platform-core/workflow/
```

**ДО (старое):**
```
❌ /Users/MD/AI-Platform-ISO/intelligent-core/unified-workflow/
   (БОЛЬШЕ НЕ СУЩЕСТВУЕТ - переименовано/перемещено)
```

**ПОСЛЕ (новое):**
```
✅ /Users/MD/AI-Platform-ISO/intelligent-core/platform-core/workflow/
   (ЭТО ТО ЖЕ САМОЕ, просто переместили)
```

---

## 🔄 Что Произошло?

### Шаг 1: Было
```
intelligent-core/
├── unified-workflow/           ← Было здесь
│   ├── bpmn/
│   ├── core/
│   ├── persistence/
│   └── ...
```

### Шаг 2: Создали platform-core
```
intelligent-core/
├── platform-core/              ← Создали новую папку
│   └── (пусто)
```

### Шаг 3: Переместили unified-workflow
```bash
# Команда:
mv intelligent-core/unified-workflow intelligent-core/platform-core/workflow
```

### Шаг 4: Стало
```
intelligent-core/
├── platform-core/              ← Новая структура
│   └── workflow/               ← unified-workflow переименован в workflow
│       ├── bpmn/
│       ├── core/
│       ├── persistence/
│       └── ...
│
└── unified-workflow/           ← БОЛЬШЕ НЕ СУЩЕСТВУЕТ
```

---

## 📂 Полная Структура Сейчас

```
/Users/MD/AI-Platform-ISO/intelligent-core/platform-core/workflow/
│
├── __init__.py                 # Exports (UnifiedWorkflowEngine, etc.)
├── README.md                   # Documentation
├── PHASE_2_COMPLETE.md         # Phase 2 docs
├── QUICK_START.md              # Quick start guide
├── requirements.txt            # Dependencies
│
├── bpmn/                       # BPMN Layer
│   ├── __init__.py
│   ├── models.py               # Pydantic models (280 lines)
│   ├── parser.py               # BPMN XML parser (240 lines)
│   ├── engine.py               # In-memory engine (400 lines)
│   └── engine_persistent.py   # PostgreSQL engine (600 lines) ⭐
│
├── core/                       # Integration Layer
│   ├── __init__.py
│   └── unified_engine.py       # Main UnifiedWorkflowEngine (830 lines) ⭐
│
├── persistence/                # Database Layer
│   ├── __init__.py
│   ├── database.py             # DatabaseManager (140 lines)
│   └── repositories/
│       ├── __init__.py
│       ├── process_repository.py    # Process CRUD (220 lines)
│       ├── instance_repository.py   # Instance CRUD (380 lines)
│       └── task_repository.py       # Task CRUD (420 lines)
│
├── examples/                   # Usage Examples
│   ├── basic_usage.py          # Simple example
│   └── production_usage.py     # Full production example
│
├── tests/                      # Tests
│   └── test_unified_engine.py
│
├── visualization/              # UI helpers
│   └── __init__.py
│
└── api/                        # API (future)
    └── __init__.py
```

---

## 🔍 Где Найти Ключевые Файлы?

### 1. Главный Engine (UnifiedWorkflowEngine)
**Путь:**
```
/Users/MD/AI-Platform-ISO/intelligent-core/platform-core/workflow/core/unified_engine.py
```
**Размер:** 28 KB (830 строк)
**Что делает:** Главный класс, объединяющий BPMN + AI

---

### 2. BPMN Persistent Engine
**Путь:**
```
/Users/MD/AI-Platform-ISO/intelligent-core/platform-core/workflow/bpmn/engine_persistent.py
```
**Размер:** 19 KB (600 строк)
**Что делает:** BPMN execution с PostgreSQL

---

### 3. Database Manager
**Путь:**
```
/Users/MD/AI-Platform-ISO/intelligent-core/platform-core/workflow/persistence/database.py
```
**Размер:** 140 строк
**Что делает:** PostgreSQL connection manager

---

### 4. Repositories
**Путь:**
```
/Users/MD/AI-Platform-ISO/intelligent-core/platform-core/workflow/persistence/repositories/
├── process_repository.py    (220 строк)
├── instance_repository.py   (380 строк)
└── task_repository.py       (420 строк)
```
**Что делают:** CRUD операции для BPMN entities

---

### 5. Models
**Путь:**
```
/Users/MD/AI-Platform-ISO/intelligent-core/platform-core/workflow/bpmn/models.py
```
**Размер:** 280 строк
**Что делает:** Pydantic модели (BPMNProcess, ProcessInstance, Task, etc.)

---

### 6. Examples
**Путь:**
```
/Users/MD/AI-Platform-ISO/intelligent-core/platform-core/workflow/examples/
├── basic_usage.py          # Простой пример
└── production_usage.py     # Production пример
```

---

## 📥 Как Импортировать?

### ❌ СТАРЫЙ способ (НЕ РАБОТАЕТ):
```python
from intelligent_core.unified_workflow import UnifiedWorkflowEngine
# ModuleNotFoundError: No module named 'intelligent_core.unified_workflow'
```

### ✅ НОВЫЙ способ (РАБОТАЕТ):

#### Вариант 1: Через platform_core
```python
from platform_core.workflow import UnifiedWorkflowEngine
```

#### Вариант 2: Через platform_core напрямую
```python
from platform_core import UnifiedWorkflowEngine
```

#### Вариант 3: Полный путь
```python
from platform_core.workflow.core.unified_engine import UnifiedWorkflowEngine
```

---

## 🗂️ Что НЕ Переместили?

### workflow_intelligence - ОСТАЛСЯ на месте
**Путь:**
```
/Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence/
```

**Почему НЕ переместили:**
- Это БИБЛИОТЕКА компонентов (не сервис)
- unified-workflow ИСПОЛЬЗУЕТ его (импортирует)
- Может использоваться отдельно другими модулями

**Импорт НЕ изменился:**
```python
from workflow_intelligence import ContextAdvisor, CaseLibrary
```

---

## 📊 До и После

### ДО миграции:
```
intelligent-core/
├── unified-workflow/              ← Было здесь
│   ├── bpmn/
│   ├── core/
│   │   └── unified_engine.py
│   └── persistence/
│
└── workflow_intelligence/         ← Было здесь
    ├── ai/
    ├── case_library/
    └── core/
```

### ПОСЛЕ миграции:
```
intelligent-core/
├── platform-core/                 ← НОВАЯ структура
│   └── workflow/                  ← unified-workflow переименован
│       ├── bpmn/
│       ├── core/
│       │   └── unified_engine.py
│       └── persistence/
│
└── workflow_intelligence/         ← БЕЗ ИЗМЕНЕНИЙ
    ├── ai/
    ├── case_library/
    └── core/
```

---

## 🎯 Почему Переместили?

### Причины:

1. **Архитектура слоев (Layer 1/2/3)**
   - Platform Core = Layer 1 (domain-agnostic)
   - unified-workflow = orchestration (подходит под Layer 1)

2. **Четкое разделение**
   - platform-core/ = системные функции
   - intelligent-core/ = AI компоненты

3. **Plugin architecture готовность**
   - Легче отделить BCM domain от platform
   - Готово для других доменов (HR, Finance, etc.)

4. **Переиспользование**
   - Ясно что workflow - это platform функция
   - Можно использовать в ЛЮБОМ домене

---

## ✅ Проверка

```bash
# Старая директория должна НЕ существовать
ls /Users/MD/AI-Platform-ISO/intelligent-core/unified-workflow
# Результат: No such file or directory ✅

# Новая директория существует
ls /Users/MD/AI-Platform-ISO/intelligent-core/platform-core/workflow
# Результат: (список файлов) ✅

# Главный файл на месте
ls /Users/MD/AI-Platform-ISO/intelligent-core/platform-core/workflow/core/unified_engine.py
# Результат: (файл существует) ✅
```

---

## 📚 Связанная Документация

- `/intelligent-core/platform-core/README.md` - Platform Core overview
- `/intelligent-core/platform-core/workflow/PHASE_2_COMPLETE.md` - Workflow docs
- `/PLATFORM_CORE_MIGRATION_COMPLETE.md` - Migration summary
- `/CURRENT_ARCHITECTURE_STATUS.md` - Current architecture
- `/BPMN_MODULES_COMPARISON.md` - Modules comparison

---

## 🚀 TL;DR

**Вопрос:** Где unified-workflow?

**Ответ:**
```
БЫЛО: intelligent-core/unified-workflow/
СТАЛО: intelligent-core/platform-core/workflow/
```

**Импорт:**
```python
# БЫЛО:
from intelligent_core.unified_workflow import UnifiedWorkflowEngine

# СТАЛО:
from platform_core.workflow import UnifiedWorkflowEngine
# ИЛИ
from platform_core import UnifiedWorkflowEngine
```

**Код:** Весь код БЕЗ изменений, только переместили папку!

---

**Дата создания:** 2025-10-05
**Автор:** Claude AI Assistant
