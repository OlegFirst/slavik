# 📝 PROJECT MEMORY

**Дата:** 5 октября 2025
**Проект:** AI-Platform-ISO

---

## ⚠️ КРИТИЧЕСКОЕ ПРАВИЛО

**НИКОГДА НЕ УДАЛЯТЬ КОД!**

> "и мы если чтто ничего и никогда не удаляем!!!!! только архив!"
> — MD, 4 октября 2025

**Всегда:**
- ✅ Перемещать в `_archive/` с сохранением структуры
- ✅ Добавлять дату архивирования в README
- ✅ Сохранять историю изменений

**Никогда:**
- ❌ `rm -rf` или удаление файлов
- ❌ Перезапись без сохранения оригинала
- ❌ Потеря legacy кода

---

## 🎯 Текущая Задача

**Интеграция AI модулей** - объединение ai_experts, organs, pdca_assistant в единую архитектуру

### Статус Анализа
✅ **ЗАВЕРШЕН** - создан файл [AI_MODULES_INTEGRATION_ANALYSIS.md](./AI_MODULES_INTEGRATION_ANALYSIS.md)

### Архитектурное Решение
**ИЕРАРХИЯ (рекомендуется):**
```
ai_experts/              # Высокоуровневые консультанты (для пользователей)
    ├── specialists/      # BCM Advisor, Compliance Auditor, Strategic Planner
    ├── tools/            # 9 инструментов (BIA, Compliance, Strategic)
    │   └── organs/       # ← СЮДА переносим AI Organs (движки для tools)
    └── context/          # ← СЮДА интегрируем PDCA (контекстный провайдер)
```

---

## 📊 Найденные Модули

### 1. ai_experts/ (НОВЫЙ - 5 октября)
- **Размер:** 36 файлов, 8,103 строк
- **Статус:** ✅ 100% готов (был 22%, дополнен до 100%)
- **Компоненты:**
  - 3 Expert Agents
  - 9 Specialized Tools (с хардкодом логики)
  - RAG Pipeline
  - ML Models
  - Self-Learning Engine
  - FastAPI endpoints

### 2. ai-office/organs/ (СУЩЕСТВУЮЩИЙ)
- **Размер:** 11 файлов Python
- **Статус:** ✅ Полностью реализованы с бизнес-логикой
- **Органы:**
  - `compliance_guardian.py` - анализ соответствия стандартам
  - `emergency_response.py` - кризисное реагирование
  - `governance_brain.py` - управление
  - `impact_oracle.py` - оценка воздействия
  - `learning_coach.py` - обучение
  - `lifecycle_monitor.py` - мониторинг жизненного цикла
  - `plan_generator.py` - генерация планов
  - `performance_analyst.py` - анализ производительности
  - `risk_advisor.py` - управление рисками
  - `scenario_creator.py` - создание сценариев
  - `base_organ.py` - базовый класс

**Архитектура Organs:**
- Наследуются от `BaseAIOrgan`
- Метод `analyze(context)` - главный интерфейс
- Используют LLM через `llm_router`
- Возвращают `{insights, recommendations, confidence}`
- Интегрируются с Digital Twin (получают состояние организации)
- Получают знания из Domain Intelligence

### 3. ai-office/pdca_assistant.py (СУЩЕСТВУЮЩИЙ)
- **Размер:** 552 строки
- **Статус:** ✅ Реализован
- **Возможности:**
  - PDCA Phase tracking (Plan-Do-Check-Act)
  - 8 контекстов (overview, events, orchestrator, documents, exercises, governance, training, admin)
  - Next Best Action suggestions
  - Scenario management
  - Conversation history tracking

---

## 🔧 План Интеграции

### Phase 1: Переместить Organs
```bash
# ИЗ:
intelligent-core/ai-office/organs/*.py

# В:
intelligent-core/ai_experts/tools/organs/
├── __init__.py
├── base_organ.py
├── compliance_guardian.py
├── emergency_response.py
├── governance_brain.py
├── impact_oracle.py
├── learning_coach.py
├── lifecycle_monitor.py
├── plan_generator.py
├── performance_analyst.py
├── risk_advisor.py
└── scenario_creator.py
```

**Использование в tools:**
```python
# В ai_experts/tools/compliance_tools.py

from .organs.compliance_guardian import ComplianceGuardian

class ComplianceCheckTool(BaseTool):
    def __init__(self):
        super().__init__(...)
        self.guardian = ComplianceGuardian()  # ← используем organ как движок

    async def execute(self, clause_number: str, evidence_provided: List, **kwargs):
        # Текущая логика: хардкод проверок
        # НОВАЯ логика: используем AI organ для анализа
        result = await self.guardian.analyze({
            'standards': ['ISO_22301'],
            'current_controls': evidence_provided,
            'audit_scope': f"Clause {clause_number}"
        })

        # Комбинируем: хардкод структуры + AI анализ
        return {
            'clause': clause_number,
            'requirements': self.clause_requirements[clause_number],
            'ai_analysis': result['insights'],
            'recommendations': result['recommendations'],
            'confidence': result['confidence']
        }
```

### Phase 2: Интегрировать PDCA
```bash
# Создать:
intelligent-core/ai_experts/context/pdca_context.py
```

**Реализация:**
```python
from ai_office.pdca_assistant import PDCAAssistant

class PDCAContextProvider:
    """Предоставляет PDCA контекст для экспертов"""

    def __init__(self, config):
        self.pdca = PDCAAssistant(config)

    async def enrich_query(self, user_query: str, base_context: Dict) -> Dict:
        """Обогащает запрос пользователя PDCA контекстом"""
        return {
            **base_context,
            'pdca_phase': self.pdca.current_phase,
            'pdca_context': self.pdca.current_context,
            'suggested_actions': await self.pdca.get_next_best_actions()
        }
```

**Использование в specialists:**
```python
# В ai_experts/specialists/bcm_advisor.py

from ..context.pdca_context import PDCAContextProvider

class BCMAdvisor:
    def __init__(self, ...):
        self.pdca_context = PDCAContextProvider(config)

    async def answer_query(self, query: str, context: Dict):
        # Обогащаем контекст PDCA информацией
        enriched_context = await self.pdca_context.enrich_query(query, context)

        # Теперь эксперт знает:
        # - В какой PDCA фазе пользователь (Plan/Do/Check/Act)
        # - В каком UI контексте (events/exercises/governance)
        # - Какие действия рекомендованы следующими

        # Адаптируем ответ под контекст
        response = await self._generate_response(query, enriched_context)
        return response
```

### Phase 3: Архивировать Legacy
```bash
# Архивировать:
intelligent-core/ai-office/bcm_ai_consultant/  → _archive/ai-office/
intelligent-core/ai-office/ai-consultant/      → _archive/ai-office/

# Оставить (переиспользуются):
intelligent-core/ai-office/pdca_assistant.py   ← используется через context/
intelligent-core/ai-office/organs/             → переносится в ai_experts/tools/organs/
```

### Phase 4: Обновить Импорты

**В ai_experts/__init__.py:**
```python
from .specialists import BCMAdvisor, ComplianceAuditor, StrategicPlanner
from .tools import *
from .tools.organs import *  # Экспортируем organs
from .context.pdca_context import PDCAContextProvider
```

**В платформенных сервисах:**
```python
# Было:
from ai_office.organs.compliance_guardian import ComplianceGuardian

# Стало:
from ai_experts.tools.organs import ComplianceGuardian
```

---

## ✅ Преимущества

1. **Единая точка входа** - ai_experts как главный AI модуль
2. **Чистая иерархия:**
   - Experts (для пользователей) → Tools (возможности) → Organs (движки)
3. **Нет дублирования** - каждый модуль имеет свою роль
4. **AI-усиление** - tools получают AI-анализ через organs
5. **Контекстная осведомленность** - все experts знают PDCA фазу
6. **Расширяемость** - легко добавить новые organs/tools/experts

---

## 📝 Следующие Шаги

**🔄 ОБНОВЛЕНИЕ (5 окт, после изучения ai-office/):**

Найдено много качественного кода в ai-office/:
- ВСМ-colleagues/ (2,698 строк) - 7 AI коллег с PDCA + RAG
- core/ (2,210 строк) - RAG pipeline, LLM router, Intent analyzer
- organs/ (11 файлов) - уже анализировали
- pdca_assistant.py (552 строки) - уже анализировали

**НОВАЯ РЕКОМЕНДАЦИЯ:** Гибридная архитектура (см. AI_OFFICE_ANALYSIS.md)

**Ожидание решения пользователя:**
1. ⏳ Прочитать [AI_OFFICE_ANALYSIS.md](./AI_OFFICE_ANALYSIS.md)
2. ⏳ Одобрить гибридную архитектуру (colleagues + tools + shared core)
3. ⏳ Решить что делать с mio-manager/ и project-agent/
4. ⏳ Дать команду на Phase 1 (общая инфраструктура в shared/)

**Оценка:** 2-3 дня работы

---

## 🔗 Связанные Файлы

**ГЛАВНОЕ:**
- **[AI_OFFICE_ANALYSIS.md](./AI_OFFICE_ANALYSIS.md)** ⭐ НОВЫЙ полный анализ - ЧИТАТЬ ПЕРВЫМ

**Дополнительно:**
- [AI_INTEGRATION_SUMMARY.md](./AI_INTEGRATION_SUMMARY.md) - устарела (была до изучения ai-office)
- [AI_MODULES_INTEGRATION_ANALYSIS.md](./AI_MODULES_INTEGRATION_ANALYSIS.md) - первичный анализ
- [intelligent-core/ai_experts/](./intelligent-core/ai_experts/) - новый модуль (8,103 строки)
- [intelligent-core/ai-office/](./intelligent-core/ai-office/) - 144 файла Python (изучено)

## 📌 Заметки о EventBus

**ВАЖНО:** В проекте 2 EventBus реализации:

1. **`/infrastructure/eventbus/`** (НОВАЯ - 4 октября)
   - Clean Architecture с интерфейсом IEventBus
   - Pluggable backends (InMemory, Redis Streams)
   - Рекомендуется для новых сервисов
   - 2,919 строк, production-ready

2. **`/shared/eventbus/`** (LEGACY)
   - RabbitMQ-based (aio_pika)
   - Используется в существующих сервисах
   - Может быть заменена на новую

**Рекомендация:** Новые интеграции (ai_experts, organs) используют `/infrastructure/eventbus/`
