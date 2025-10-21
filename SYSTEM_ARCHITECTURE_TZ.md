# ТЕХНИЧЕСКОЕ ЗАДАНИЕ - Системная Архитектура Платформы

**Дата:** 21 октября 2025, 04:35
**Приоритет:** КРИТИЧЕСКИЙ
**Статус:** В РАБОТЕ

---

## ЦЕЛЬ ПРОЕКТА

**Главная задача:**
Провести полный анализ и редизайн архитектуры AI-Platform-ISO для создания устойчивой системной основы, пронизывающей всю платформу.

**Философия:**
> "ai_foundation = формирование интеллекта через разные подходы"
> "Нужна устойчивая основа, пронизывающая всю платформу"
> "В каждом сервисе реализовать эту подсистему, но с разными функциями"

---

## КОНТЕКСТ ПРОБЛЕМЫ

### Выявленные критические проблемы:

#### 1. Дублирование AI-подсистем (КРИТИЧНО!)

```
ai_foundation/ml/           ← Оригинал
workflow_intelligence/ml/   ← ДУБЛИКАТ #1
expertise_center/.../ml/    ← ДУБЛИКАТ #2

ai_foundation/rag/          ← Оригинал
expertise_center/.../rag/   ← ДУБЛИКАТ

ai_foundation/learning/     ← Оригинал
learning_knowledge/learning/← ДУБЛИКАТ
```

**Проблема:** Код дублируется, несогласованные версии, сложность поддержки.

#### 2. Memory в неправильном месте

```
ai_foundation/memory/  ← Используется ВОВНЕ ai_foundation
```

**Используется в:**
- `system_bcm_service/instincts/survival.py`
- `orchestration/gameloop/operational_loop.py`

**Решение:** Переместить в `shared/memory/`

#### 3. Путаница в именовании

```
ai_foundation/
├── learning/              ← Базовое
└── learning_knowledge/    ← Полное
    └── learning/          ← ЕЩЕ ОДНО!
```

**Решение:** Переименовать для ясности

---

## ЗАДАЧИ ПРОЕКТА

### ФАЗА 1: ПОЛНЫЙ АНАЛИЗ (Priority #1)

#### 1.1 Анализ catalogs/

**Цель:** Понять структуру каталогов, шаблонов, сценариев

**Что анализировать:**
- `/Users/MD/AI-Platform-ISO/catalogs/`
  - Структура директорий
  - Типы файлов (JSON, YAML, MD)
  - Назначение каталогов (simulation-templates, theory-of-change, etc.)
  - Связи между каталогами
  - Используемые стандарты (ISO 22301, etc.)

**Выходные данные:**
- Карта всех каталогов
- Классификация по типам (templates, scenarios, standards)
- Зависимости между каталогами

#### 1.2 Анализ DOC/

**Цель:** Понять документационную структуру и архитектуру

**Что анализировать:**
- `/Users/MD/AI-Platform-ISO/DOC/`
  - Структура документации
  - Покрытие модулей
  - API документация
  - Архитектурные решения
  - Бизнес-логика
  - Интеграции

**Выходные данные:**
- Карта документации
- Недокументированные модули
- Архитектурные паттерны
- Интеграционные точки

#### 1.3 Анализ README.md

**Цель:** Понять общее видение и структуру платформы

**Что анализировать:**
- `/Users/MD/AI-Platform-ISO/README.md`
  - Общая архитектура
  - Модули и компоненты
  - Технологический стек
  - Deployment стратегия
  - Видение платформы

**Выходные данные:**
- Высокоуровневая архитектура
- Ключевые компоненты
- Технические решения

#### 1.4 Анализ intelligent_core/

**Цель:** Глубокий анализ интеллектуального ядра

**Что анализировать:**
- Все модули в `intelligent_core/`
- Зависимости между модулями
- Дублирование кода
- Архитектурные паттерны
- Подсистемы (ml, rag, llm, learning, memory)

**Выходные данные:**
- Карта зависимостей
- Список дубликатов
- Рекомендации по консолидации

#### 1.5 Анализ platform_services/

**Цель:** Понять сервисную архитектуру

**Что анализировать:**
- Все сервисы в `platform_services/`
- API endpoints
- Межсервисные коммуникации
- Общие компоненты
- Дублирование функционала

**Выходные данные:**
- Карта сервисов
- API gateway архитектура
- Общие паттерны

#### 1.6 Анализ infrastructure/

**Цель:** Понять инфраструктурные решения

**Что анализировать:**
- Kubernetes манифесты
- Docker конфигурации
- Deployment стратегии
- Monitoring/Logging
- Security (Vault, secrets)

**Выходные данные:**
- Инфраструктурная карта
- Deployment паттерны
- Security архитектура

---

### ФАЗА 2: ПРОЕКТИРОВАНИЕ ПОД СИСТЕМЫ (Priority #2)

#### 2.1 Определение системных слоев

**Цель:** Создать четкую слоистую архитектуру

**Слои (предварительно):**

```
Layer 1: AI Foundation (Единое ядро интеллекта)
  ├── core/              # Базовые AI-возможности
  │   ├── ml/            # Machine Learning
  │   ├── llm/           # Language Models
  │   ├── rag/           # Retrieval-Augmented Generation
  │   └── learning/      # Pattern Learning
  │
  ├── domain_adapters/   # Специализация для доменов
  │   ├── workflow_ml/   # ML для workflow
  │   ├── expert_ml/     # ML для экспертов
  │   └── orchestration_ml/
  │
  └── shared/
      ├── memory/        # ГЛОБАЛЬНАЯ память
      ├── context/       # Context building
      └── balancer/      # Decision balancing

Layer 2: Intelligent Core (Бизнес-логика)
  ├── orchestration/         # Оркестрация
  ├── workflow_intelligence/ # Workflow логика
  ├── expertise_center/      # AI эксперты
  └── ... другие модули

Layer 3: Platform Services (Сервисы)
  ├── bia_service/
  ├── compliance_service/
  ├── digital_twin/
  └── ... другие

Layer 4: Infrastructure (Инфраструктура)
  ├── kubernetes/
  ├── security/
  └── monitoring/

Layer 5: Interface (Интерфейсы)
  ├── admin/
  └── ... другие
```

#### 2.2 Определение системных паттернов

**Паттерны для внедрения:**

1. **Domain Adapter Pattern**
   ```python
   # ai_foundation/domain_adapters/workflow_ml.py
   from ai_foundation.core.ml import MLEngine

   class WorkflowMLAdapter:
       def __init__(self):
           self.ml_engine = MLEngine()

       def predict_workflow_duration(self, workflow_data):
           # Специфичная логика для workflow
           pass
   ```

2. **Shared Memory Pattern**
   ```python
   # shared/memory/memory_system.py
   class GlobalMemorySystem:
       # Используется всеми модулями
       pass
   ```

3. **Event-Driven Architecture**
   ```python
   # shared/event_bus/
   # Единая шина событий для всей платформы
   ```

#### 2.3 Определение интеграционных точек

**Где модули интегрируются:**
- Event Bus (события)
- Shared Memory (память)
- AI Foundation (интеллект)
- Platform Client (межсервисное взаимодействие)

---

### ФАЗА 3: ПОИСК СУЩЕСТВУЮЩИХ ЭЛЕМЕНТОВ (Priority #3)

#### 3.1 Инвентаризация компонентов

**Что искать:**

1. **AI компоненты:**
   - Все ML модели
   - Все RAG pipeline
   - Все LLM интеграции
   - Все learning engines

2. **Общие утилиты:**
   - Database connectors
   - API clients
   - Event handlers
   - Validators

3. **Конфигурации:**
   - ENV переменные
   - Kubernetes configs
   - Docker compose
   - Settings файлы

4. **Документация:**
   - API docs
   - Architecture docs
   - Deployment guides
   - User guides

#### 3.2 Классификация элементов

**Категории:**

```
CATEGORY 1: CANONICAL (Единственный источник правды)
  - ai_foundation/ml/
  - ai_foundation/rag/
  - ai_foundation/llm/
  - shared/event_bus/

CATEGORY 2: DUPLICATES (Должны быть удалены)
  - workflow_intelligence/ml/
  - expertise_center/.../ml/
  - expertise_center/.../rag/

CATEGORY 3: DOMAIN-SPECIFIC (Остаются, но рефакторинг)
  - workflow_intelligence/workflow_analyzer.py
  - expertise_center/ai_experts/specialist_matcher.py

CATEGORY 4: MISPLACED (Неправильное размещение)
  - ai_foundation/memory/ → shared/memory/

CATEGORY 5: NAMING ISSUES (Путаница в названиях)
  - learning/ vs learning_knowledge/
```

#### 3.3 Создание карты миграции

**Формат:**

```yaml
migration_map:
  - source: ai_foundation/memory/
    destination: shared/memory/
    reason: "Used globally, not AI-specific"
    affected_imports:
      - system_bcm_service/instincts/survival.py
      - orchestration/gameloop/operational_loop.py
    risk: LOW
    estimated_time: 10min

  - source: workflow_intelligence/ml/
    destination: DELETE
    replace_with: ai_foundation/domain_adapters/workflow_ml/
    reason: "Duplicate of ai_foundation/ml/"
    risk: MEDIUM
    estimated_time: 2 hours
```

---

### ФАЗА 4: СБОРКА (Priority #4)

#### 4.1 Поэтапная миграция

**День 1-2: Подготовка**
- Создать ветку `feature/system-architecture-refactor`
- Создать все необходимые domain_adapters
- Написать тесты для критических компонентов

**День 3: Memory migration**
- Переместить ai_foundation/memory/ → shared/memory/
- Обновить импорты (2 файла)
- Тестирование

**День 4-5: Learning refactoring**
- Переименовать learning/ → pattern_learning/
- Переименовать learning_knowledge/ → knowledge_platform/
- Обновить импорты
- Тестирование

**День 6-7: ML/RAG consolidation**
- Создать domain_adapters для всех доменов
- Удалить дубликаты
- Обновить все импорты
- Полное тестирование

#### 4.2 Документация

**Создать:**
1. `ARCHITECTURE.md` - Полная архитектура платформы
2. `MIGRATION_GUIDE.md` - Гид по миграции для разработчиков
3. `DOMAIN_ADAPTERS.md` - Как использовать domain adapters
4. `SYSTEM_LAYERS.md` - Описание всех слоев системы

#### 4.3 Валидация

**Чеклист:**
- [ ] Все тесты проходят
- [ ] Нет дублирования кода
- [ ] Четкие границы между слоями
- [ ] Документация обновлена
- [ ] Deployment не сломан
- [ ] Performance не ухудшился

---

## ВЫХОДНЫЕ ДОКУМЕНТЫ

### Аналитические документы:

1. **PLATFORM_ANALYSIS_COMPLETE.md**
   - Полный анализ всей платформы
   - Все найденные компоненты
   - Карта зависимостей
   - Выявленные проблемы

2. **SYSTEM_ARCHITECTURE_DESIGN.md**
   - Финальная архитектура
   - Слои и их ответственности
   - Паттерны и практики
   - Интеграционные точки

3. **MIGRATION_ROADMAP.md**
   - Пошаговый план миграции
   - Карта всех изменений
   - Риски и митигации
   - Timeline и ресурсы

4. **ASSEMBLY_COMPLETE.md**
   - Отчет о сборке
   - Что изменилось
   - Метрики (до/после)
   - Next steps

### Диаграммы:

1. **platform-architecture.mmd** - Общая архитектура
2. **dependency-graph.mmd** - Граф зависимостей
3. **migration-flow.mmd** - Поток миграции
4. **layer-diagram.mmd** - Слоистая архитектура

---

## МЕТРИКИ УСПЕХА

### Технические метрики:

```
Дублирование кода:
  До:  3 копии ML, 2 копии RAG, 2 копии Learning
  После: 1 источник + domain adapters
  Улучшение: 66-100% reduction

Четкость архитектуры:
  До:  65/100 (путаница, неправильное размещение)
  После: 95/100 (четкие слои, правильные границы)

Maintainability:
  До:  Сложно (изменения в 3 местах)
  После: Просто (изменения в 1 месте)

Документация:
  До:  40/100 (фрагментарная)
  После: 90/100 (полная, актуальная)
```

### Бизнес-метрики:

```
Time to market для новых AI features:
  До:  3-5 дней (нужно обновить 3 копии)
  После: 1 день (одно место)

Onboarding новых разработчиков:
  До:  2 недели (путаница в архитектуре)
  После: 3 дня (четкая документация)

Production incidents:
  До:  Риск рассинхронизации версий
  После: Единый источник правды
```

---

## РИСКИ И МИТИГАЦИИ

### Риск 1: Breaking changes

**Вероятность:** ВЫСОКАЯ
**Влияние:** КРИТИЧНОЕ

**Митигация:**
- Полное тестирование перед миграцией
- Поэтапное внедрение
- Возможность rollback
- Синхронизация с командой

### Риск 2: Performance degradation

**Вероятность:** СРЕДНЯЯ
**Влияние:** ВЫСОКОЕ

**Митигация:**
- Benchmarking до и после
- Profiling критических путей
- Оптимизация domain adapters
- Monitoring в production

### Риск 3: Недокументированные зависимости

**Вероятность:** СРЕДНЯЯ
**Влияние:** СРЕДНЕЕ

**Митигация:**
- Глубокий анализ imports
- Grep по всему кодбейсу
- Тестирование всех модулей
- Gradual rollout

---

## TIMELINE

### Неделя 1: Анализ
- День 1-2: catalogs/, DOC/, README.md
- День 3-4: intelligent_core/, platform_services/
- День 5: infrastructure/, interface/
- День 6-7: Создание карт и документов

### Неделя 2: Проектирование
- День 1-2: Слоистая архитектура
- День 3-4: Domain adapters дизайн
- День 5: Интеграционные точки
- День 6-7: Финализация дизайна

### Неделя 3: Реализация
- День 1-2: Memory migration + Learning rename
- День 3-5: ML/RAG consolidation
- День 6-7: Тестирование и багфиксы

### Неделя 4: Валидация и Deploy
- День 1-2: Финальное тестирование
- День 3-4: Документация
- День 5: Code review
- День 6-7: Production deployment

---

## КОМАНДА И РОЛИ

### Роли (для Claude Code Agents):

1. **Analyzer Agent** - Анализ catalogs/, DOC/, README.md
2. **Architect Agent** - Проектирование системной архитектуры
3. **Search Agent** - Поиск существующих элементов
4. **Migration Agent** - Выполнение миграции
5. **Testing Agent** - Валидация и тестирование
6. **Documentation Agent** - Создание документации

---

## СЛЕДУЮЩИЕ ШАГИ (НЕМЕДЛЕННО)

### Шаг 1: Запустить Analyzer Agent

**Задача:**
```
Проанализировать:
1. /Users/MD/AI-Platform-ISO/catalogs/
2. /Users/MD/AI-Platform-ISO/DOC/
3. /Users/MD/AI-Platform-ISO/README.md

Создать:
- CATALOGS_ANALYSIS.md
- DOC_ANALYSIS.md
- README_VISION.md
```

### Шаг 2: Запустить Search Agent (параллельно)

**Задача:**
```
Найти все дубликаты:
- ML implementations
- RAG implementations
- Learning implementations

Создать:
- DUPLICATION_INVENTORY.md
```

### Шаг 3: Начать проектирование

**После завершения анализа:**
```
Создать SYSTEM_ARCHITECTURE_DESIGN.md
```

---

## КРИТЕРИИ ПРИЕМКИ

### Для Фазы 1 (Анализ):

- [ ] Все каталоги проанализированы
- [ ] Вся документация проанализирована
- [ ] README видение понятно
- [ ] Все дубликаты найдены
- [ ] Карты созданы

### Для Фазы 2 (Проектирование):

- [ ] Слоистая архитектура определена
- [ ] Domain adapters спроектированы
- [ ] Интеграционные точки определены
- [ ] Паттерны документированы

### Для Фазы 3 (Поиск):

- [ ] Все компоненты классифицированы
- [ ] Карта миграции создана
- [ ] Риски оценены

### Для Фазы 4 (Сборка):

- [ ] Все миграции выполнены
- [ ] Все тесты проходят
- [ ] Документация обновлена
- [ ] Production готов к deploy

---

## КОНТАКТЫ И РЕСУРСЫ

### Ключевые документы:

```
/CONTEXT_MEMO.md                    # Контекст восстановления
/NEXT_STEPS_GUIDE.md                # Инструкции
/intelligent_core/AI_FOUNDATION_PHILOSOPHY.md  # Философия
/intelligent_core/SYSTEM_CONSOLIDATION_PLAN.md # План консолидации
```

### Инструменты:

```
/scripts/safe-cleanup.sh            # Cleanup
/scripts/analyze-codebase.py       # Анализ
/infrastructure/security/vault_client.py  # Vault
```

---

## СТАТУС

**Текущий этап:** ФАЗА 1 - АНАЛИЗ (в работе)

**Следующее действие:** Запуск Analyzer Agent для catalogs/, DOC/, README.md

**Дата начала:** 21 октября 2025, 04:35

**Предполагаемое завершение:** 18 ноября 2025 (4 недели)

---

**ПРИОРИТЕТ: КРИТИЧЕСКИЙ**

**ЗАПУСКАЕМ! 🚀**

---

END OF TECHNICAL SPECIFICATION
