# 🏢 AI Office - Полный Анализ Модулей

**Дата:** 5 октября 2025
**Цель:** Определить что оставить, что интегрировать, что архивировать

---

## 📊 Что Есть в ai-office/

### 1. **ВСМ-colleagues/** - 2,698 строк ✅ КАЧЕСТВЕННЫЙ КОД
**7 AI Digital Colleagues:**
- `bia_specialist` - BIA анализ, RTO/RPO
- `compliance_copilot` - ISO 22301 compliance
- `project_manager` - BCM проекты
- `risk_analyst` - Risk management
- `plan_generator` - BCM планирование
- `incident_advisor` - Crisis response
- `exercise_designer` - BCM exercises

**Архитектура:**
```python
BaseAIColleague (ABC)
  ├── PDCA Framework (Plan-Do-Check-Act)
  ├── RAG Pipeline integration
  ├── Conversation tracking
  ├── Next Best Action suggestions
  └── EventBus integration
```

**Отличие от ai_experts/specialists:**
- ✅ PDCA-aware (знают фазу пользователя)
- ✅ UI context-aware (знают где пользователь в интерфейсе)
- ✅ Conversational (диалоговые, с историей)
- ✅ Action suggestions (рекомендуют следующие шаги)

### 2. **core/** - 2,210 строк ✅ ИНФРАСТРУКТУРА

**Структура:**
```
core/
├── rag/                    # RAG Pipeline
│   ├── rag_pipeline.py    # Полный RAG workflow
│   ├── context_retriever.py # Retrieval из BCM модулей
│   └── __init__.py
├── intent/                 # Intent Analysis
│   ├── intent_analyzer.py # Определение намерений пользователя
│   └── __init__.py
├── adapters/               # LLM Adapters
│   ├── anthropic_adapter.py # Claude API
│   └── __init__.py
└── learning/               # Machine Learning
    ├── meta_learning_engine.py
    └── predictive_analytics.py
```

**Возможности:**
- RAG с retrieval из platform-services (BIA, Risk, Planning)
- Intent analysis для умных ответов
- Anthropic Claude adapter (production-ready)
- Meta-learning и predictive analytics

### 3. **organs/** - 11 файлов ✅ УЖЕ ПРОАНАЛИЗИРОВАНЫ
- AI-powered analyzers
- Интеграция с Digital Twin
- LLM-based insights

### 4. **pdca_assistant.py** - 552 строки ✅ УЖЕ ПРОАНАЛИЗИРОВАН
- PDCA Phase tracking
- UI context awareness
- Next Best Actions

### 5. **llm/** - LLM Router
```
llm/
└── llm_router.py  # Multi-provider routing (Anthropic, OpenAI, Ollama)
```

### 6. **Legacy/Duplicates:**
- `ai-consultant/` - Odoo legacy (6 файлов)
- `bcm_ai_consultant/` - Odoo legacy (6 файлов)
- `agent-router/` - дубликат (2 файла)
- `ai-devops/` - уже перенесен в infrastructure/
- `bcm_ai_control/` - устаревший контроль (16 файлов)
- `mio-manager/` - MIO Manager (24 файла) - нужно изучить
- `project-agent/` - Project Agent (20 файлов) - нужно изучить

---

## 🔍 Сравнение: ai_experts vs ВСМ-colleagues

| Характеристика | ai_experts/specialists | ВСМ-colleagues |
|----------------|------------------------|----------------|
| **Размер** | 8,103 строк (новый, 5 окт) | 2,698 строк (реальный код) |
| **Архитектура** | Tools-based (используют tools) | RAG-based (прямой RAG) |
| **PDCA** | ❌ Нет | ✅ Есть (Plan-Do-Check-Act) |
| **UI Context** | ❌ Нет | ✅ Есть (8 контекстов UI) |
| **Conversational** | ❌ Stateless | ✅ История диалога |
| **RAG** | ✅ Свой RAG pipeline | ✅ Общий core/rag |
| **Tools** | ✅ 9 специализированных | ❌ Нет |
| **ML Models** | ✅ Predictive models | ⚠️ Partial (core/learning) |
| **Self-Learning** | ✅ Pattern extraction | ❌ Нет |
| **Organs Integration** | 🔧 Планируется | ❌ Нет |

---

## 🎯 Рекомендация: ГИБРИДНАЯ АРХИТЕКТУРА

### Концепция: "Лучшее из обоих миров"

```
intelligent-core/
├── ai_experts/                    ← ГЛАВНЫЙ ИНТЕРФЕЙС
│   │
│   ├── colleagues/                ← ВСМ-colleagues (переименовать)
│   │   ├── base_colleague.py     (PDCA + RAG + Conversational)
│   │   ├── bia_specialist.py
│   │   ├── compliance_copilot.py
│   │   ├── project_manager.py
│   │   ├── risk_analyst.py
│   │   ├── plan_generator.py
│   │   ├── incident_advisor.py
│   │   └── exercise_designer.py
│   │
│   ├── tools/                     ← Специализированные инструменты
│   │   ├── bia_tools.py          (с хардкодом + AI)
│   │   ├── compliance_tools.py
│   │   ├── strategic_tools.py
│   │   └── organs/               ← AI-движки для tools
│   │       ├── compliance_guardian.py
│   │       ├── emergency_response.py
│   │       └── ...
│   │
│   ├── ml/                        ← ML Models (оставить)
│   │   ├── predictive_models.py
│   │   ├── anomaly_detection.py
│   │   └── training_pipeline.py
│   │
│   └── learning/                  ← Self-Learning (оставить)
│       ├── self_learning_engine.py
│       ├── pattern_extractor.py
│       └── rule_generator.py
│
└── shared/ai_core/                ← ОБЩАЯ ИНФРАСТРУКТУРА (из ai-office/core)
    ├── rag/
    │   ├── rag_pipeline.py       ← используется ВСЕМИ
    │   └── context_retriever.py
    ├── intent/
    │   └── intent_analyzer.py
    ├── adapters/
    │   └── anthropic_adapter.py
    ├── llm/
    │   └── llm_router.py         ← Multi-provider (Claude/GPT/Ollama)
    └── pdca/
        └── pdca_context.py       ← PDCA framework
```

---

## 💡 Ключевая Идея

### 2 Режима Работы AI:

#### 1. **Colleague Mode** (Интерактивный)
```python
# Пользователь общается с AI коллегой
colleague = BIASpecialistAI(rag_pipeline, config)

response = await colleague.chat(
    user_message="Помоги определить RTO для процесса закупок",
    pdca_phase="plan",
    ui_context="bia",
    conversation_history=[...]
)

# Получает:
# - Персонализированный ответ (знает контекст UI + PDCA)
# - Suggested next actions
# - Conversation продолжается
```

#### 2. **Tool Mode** (Программный)
```python
# Другой сервис вызывает tool
tool = BIAAnalysisTool()

result = await tool.execute(
    process_name="Закупки",
    industry="healthcare"
)

# Получает:
# - Структурированный результат
# - Готовые данные для обработки
# - Stateless вызов
```

---

## 🔧 План Интеграции

### Phase 1: Общая Инфраструктура
```bash
# ПЕРЕМЕСТИТЬ (не копировать!):
ai-office/core/        → shared/ai_core/
ai-office/llm/         → shared/ai_core/llm/
ai-office/pdca_assistant.py → shared/ai_core/pdca/pdca_context.py
```

**Результат:** Единый RAG, LLM Router, PDCA для всех

### Phase 2: Colleagues Integration
```bash
# ПЕРЕМЕСТИТЬ:
ai-office/ВСМ-colleagues/ → ai_experts/colleagues/
```

**Обновить импорты:**
```python
# Было:
from core import RAGPipeline

# Стало:
from shared.ai_core.rag import RAGPipeline
```

### Phase 3: Organs Integration
```bash
# УЖЕ ЗАПЛАНИРОВАНО:
ai-office/organs/ → ai_experts/tools/organs/
```

### Phase 4: Архивирование
```bash
# АРХИВИРОВАТЬ:
ai-office/ai-consultant/       → _archive/ai-office/
ai-office/bcm_ai_consultant/   → _archive/ai-office/
ai-office/agent-router/        → _archive/ai-office/
ai-office/ai-devops/           → _archive/ai-office/ (уже в infrastructure)
ai-office/bcm_ai_control/      → _archive/ai-office/

# ИЗУЧИТЬ ПОТОМ:
ai-office/mio-manager/         (24 файла - возможно нужен)
ai-office/project-agent/       (20 файлов - возможно нужен)
```

### Phase 5: Удалить Дубликаты в ai_experts
```bash
# АРХИВИРОВАТЬ (были заглушки):
ai_experts/rag/          → _archive/ai_experts/ (используем shared/ai_core/rag)
ai_experts/specialists/  → _archive/ai_experts/ (используем colleagues)
```

**Почему:** colleagues более зрелые, с PDCA + conversational

---

## ✅ Преимущества Гибридной Архитектуры

1. **Эффективность** - единая RAG/LLM инфраструктура
2. **Не дублируем** - RAG pipeline только в shared/
3. **2 режима** - Colleague (UI) + Tools (API)
4. **PDCA everywhere** - все AI знают фазу пользователя
5. **Conversational** - colleagues с историей диалога
6. **Structured** - tools для программных вызовов
7. **AI-enhanced tools** - tools используют organs как движки

---

## 📊 Итоговая Структура

```
AI Platform
│
├── ai_experts/                    # ИНТЕРФЕЙС для пользователей
│   ├── colleagues/ (7)           # Интерактивные AI коллеги
│   ├── tools/ (9)                # Программные инструменты
│   ├── ml/ (3)                   # ML модели
│   └── learning/ (3)             # Self-learning
│
├── shared/ai_core/                # ОБЩАЯ ИНФРАСТРУКТУРА
│   ├── rag/                      # RAG pipeline (один для всех)
│   ├── llm/                      # LLM router
│   ├── intent/                   # Intent analyzer
│   ├── adapters/                 # Claude/GPT/Ollama
│   └── pdca/                     # PDCA framework
│
└── _archive/ai-office/            # LEGACY код
```

**Метрики:**
- Colleagues: 2,698 строк
- Core infrastructure: 2,210 строк
- Tools: 3,285 строк
- ML + Learning: 2,282 строк
- **ИТОГО:** ~10,475 строк качественного кода

---

## ❓ Вопрос к тебе

**Одобряешь гибридную архитектуру?**

**Плюсы:**
- ✅ Используем весь качественный код
- ✅ Не дублируем инфраструктуру
- ✅ 2 режима работы (UI + API)
- ✅ PDCA + conversational для пользователей
- ✅ Structured tools для сервисов

**Что делать с:**
- `mio-manager/` (24 файла) - изучить или архивировать?
- `project-agent/` (20 файлов) - изучить или архивировать?

**Начинаем Phase 1 (общая инфраструктура)?**
