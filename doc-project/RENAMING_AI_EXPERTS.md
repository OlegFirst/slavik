# 💡 Переименование: ai_experts → expertise_center

## Проблема

**Текущее название**: `ai_experts`
- Звучит как "эксперты" (люди/агенты)
- Путаница с specialists в модулях
- Неясно что это инфраструктура

**Путаница**:
```
ai_experts/specialists/  ← Звучит как "топовые эксперты"
vs
platform-services/*/colleague/  ← "Коллеги - менеджеры модулей"
```

## ✅ Решение

**Новое название**: `expertise_center` (Центр Экспертизы)

**Суть**:
- Центр = инфраструктура, не персона
- Экспертиза = знания, инструменты, правила
- Center = централизованный ресурс для всех

---

## 📋 Что Переименовать

### 1. Директория

```bash
# БЫЛО
/Users/MD/AI-Platform-ISO/intelligent-core/ai_experts/

# СТАНЕТ
/Users/MD/AI-Platform-ISO/intelligent-core/expertise_center/
```

### 2. Импорты

```python
# БЫЛО
from ai_experts.tools import BIAAnalysisTool
from ai_experts.rag import RAGPipeline
from ai_experts.ml import WorkflowPredictor
from ai_experts.learning import SelfLearningEngine

# СТАНЕТ
from expertise_center.tools import BIAAnalysisTool
from expertise_center.rag import RAGPipeline
from expertise_center.ml import WorkflowPredictor
from expertise_center.learning import SelfLearningEngine
```

### 3. Документация

Все упоминания `ai_experts` → `expertise_center`

---

## 🎯 Новая Структура

```
intelligent-core/
│
├── expertise_center/              # ЦЕНТР ЭКСПЕРТИЗЫ (инфраструктура)
│   ├── tools/                     # Общие инструменты
│   ├── rag/                       # Единая база знаний
│   ├── ml/                        # Общие предсказания
│   ├── learning/                  # Единое самообучение
│   └── coordinators/              # (вместо specialists)
│       ├── bcm_coordinator.py     # Координатор BIA/Risk/Planning
│       ├── compliance_coordinator.py
│       └── strategic_coordinator.py
│
├── workflow_intelligence/         # ИНФРАСТРУКТУРА workflow
│
└── ai_platform/                   # РОУТИНГ (ChiefExecutiveAI)
```

---

## 🔄 Обновлённая Терминология

### Было (путаница):
- ❌ ai_experts = "AI эксперты" (звучит как люди)
- ❌ specialists = "специалисты" (тоже звучит как люди)
- ❌ Unclear: кто главнее - experts или specialists?

### Стало (понятно):
- ✅ **expertise_center** = "Центр Экспертизы" (инфраструктура)
- ✅ **coordinators** = "Координаторы" (используют инфраструктуру)
- ✅ **colleagues** = "Коллеги" (менеджеры модулей)
- ✅ **organs** = "Органы" (LLM анализаторы)

---

## 📊 Роли (после переименования)

### 1. Expertise Center (Инфраструктура)
**Где**: `/intelligent-core/expertise_center/`

**Что**:
- Tools - общие инструменты
- RAG - база знаний (ISO + Cases)
- ML - предсказания
- Learning - самообучение

**Кто использует**: ВСЕ (colleagues, organs, coordinators)

---

### 2. Coordinators (опционально)
**Где**: `/expertise_center/coordinators/`

**Что**: Координируют использование инфраструктуры для сложных задач

**Примеры**:
- BCMCoordinator - координирует BIA + Risk + Planning
- ComplianceCoordinator - координирует Compliance + Governance
- StrategicCoordinator - координирует Planning + Maturity

**НЕ владельцы**, а **пользователи инфраструктуры**!

---

### 3. Colleagues (Менеджеры модулей)
**Где**: `/platform-services/{service}/colleague/`

**Что**: Диалог с пользователем, управление модулем

**Используют**: expertise_center (Tools, RAG, ML, Learning)

---

### 4. Organs (LLM анализаторы)
**Где**: `/platform-services/{service}/organs/`

**Что**: LLM анализ, поиск

**Используют**: expertise_center.rag

---

## 🔧 Команды для Переименования

```bash
# 1. Переименовать директорию
mv /Users/MD/AI-Platform-ISO/intelligent-core/ai_experts \
   /Users/MD/AI-Platform-ISO/intelligent-core/expertise_center

# 2. Переименовать specialists → coordinators
mv /Users/MD/AI-Platform-ISO/intelligent-core/expertise_center/specialists \
   /Users/MD/AI-Platform-ISO/intelligent-core/expertise_center/coordinators

# 3. Переименовать файлы координаторов
cd /Users/MD/AI-Platform-ISO/intelligent-core/expertise_center/coordinators
mv bcm_advisor.py bcm_coordinator.py
mv compliance_auditor.py compliance_coordinator.py
mv strategic_planner.py strategic_coordinator.py

# 4. Обновить импорты (grep + sed)
find /Users/MD/AI-Platform-ISO -type f -name "*.py" -exec sed -i '' 's/from ai_experts/from expertise_center/g' {} +
find /Users/MD/AI-Platform-ISO -type f -name "*.py" -exec sed -i '' 's/import ai_experts/import expertise_center/g' {} +
```

---

## 📚 Обновлённая Документация

### Было:
> "AI Experts - топовый AI слой с 3 специалистами для координации модулей"

### Стало:
> "Expertise Center - централизованная AI инфраструктура (Tools, RAG, ML, Learning) для всех модулей платформы"

---

## ✅ Преимущества Нового Названия

### 1. Понятность
- ✅ "Center" = инфраструктура, не персона
- ✅ "Expertise" = знания и инструменты
- ✅ Нет путаницы с "экспертами-людьми"

### 2. Правильная роль
- ✅ Центр = ресурс для всех
- ✅ Не "топовый уровень", а "общий ресурс"
- ✅ Ясно что это инфраструктура

### 3. Согласованность с другими названиями
- ✅ workflow_intelligence - инфраструктура ✓
- ✅ expertise_center - инфраструктура ✓
- ✅ platform-services - сервисы ✓
- ✅ ai_platform - роутинг ✓

---

## 🎯 Итоговая Архитектура (с новыми названиями)

```
┌─────────────────────────────────────────────────────────┐
│              INFRASTRUCTURE LAYER                       │
│                                                         │
│  ┌──────────────────┐  ┌──────────────────────────┐   │
│  │ workflow_        │  │ expertise_center         │   │
│  │ intelligence     │  │                          │   │
│  │                  │  │ - tools/                 │   │
│  │ - StateMachine   │  │ - rag/                   │   │
│  │ - CaseLibrary    │  │ - ml/                    │   │
│  │ - EventBus       │  │ - learning/              │   │
│  │                  │  │ - coordinators/ (opt)    │   │
│  └──────────────────┘  └──────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↑
                  Используют ВСЕ
                          ↓
┌─────────────────────────────────────────────────────────┐
│              ROUTING LAYER                              │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ ai_platform (ChiefExecutiveAI + Managers)        │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              SERVICE LAYER                              │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ risk-service │  │ bia-service  │  │ compliance-  │ │
│  │              │  │              │  │ service      │ │
│  │ colleague/   │  │ colleague/   │  │ colleague/   │ │
│  │ organs/      │  │ organs/      │  │ organs/      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 План Действий

### 1. Переименовать (5 минут)
```bash
mv ai_experts expertise_center
mv expertise_center/specialists expertise_center/coordinators
```

### 2. Обновить импорты (10 минут)
```bash
# Автоматическая замена во всех файлах
find . -type f -name "*.py" -exec sed -i '' 's/ai_experts/expertise_center/g' {} +
```

### 3. Обновить документацию (15 минут)
- Все MD файлы: ai_experts → expertise_center
- Концептуальные описания
- README файлы

### 4. Проверить (5 минут)
```bash
# Убедиться что нет старых импортов
grep -r "ai_experts" --include="*.py"
# Должно быть пусто
```

---

## ✅ Результат

**БЫЛО**: Путаница
```
ai_experts/specialists/  ← "Топовые эксперты?" 🤔
platform-services/*/colleague/  ← "Коллеги менеджеры?" 🤔
```

**СТАЛО**: Понятно
```
expertise_center/  ← "Центр инфраструктуры" ✅
    ├── tools/  ← "Общие инструменты" ✅
    ├── rag/  ← "База знаний" ✅
    ├── ml/  ← "Предсказания" ✅
    └── learning/  ← "Самообучение" ✅

platform-services/*/colleague/  ← "Менеджеры модулей" ✅
```

**Делаем переименование?** 🚀
