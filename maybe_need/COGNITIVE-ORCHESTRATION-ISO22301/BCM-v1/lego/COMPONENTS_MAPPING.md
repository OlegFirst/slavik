# 🗺️ КАРТА РАСПРЕДЕЛЕНИЯ КОМПОНЕНТОВ ПО 5 ФУНКЦИЯМ

## НАШИ КОМПОНЕНТЫ → 5 ФУНКЦИЙ СИСТЕМЫ:

### 1️⃣ **ORCHESTRATION** (Координирует модули)
```
✅ ЕСТЬ:
- platform-orchestrator       → главный координатор
- scenario_orchestrator       → координатор сценариев
- unified_control_center      → центр управления
- cognitive-orchestrator      → когнитивный координатор (из lego/orchestrators/)
- ai_orchestrator            → AI координатор

❌ НУЖНО СОЗДАТЬ:
- service-registry           → реестр модулей
- module-loader             → загрузчик модулей
- dependency-resolver       → разрешение зависимостей
```

### 2️⃣ **EVENTS** (Передает события)
```
✅ ЕСТЬ:
- event-bus                  → шина событий (+ вложенные)
- realtime_websocket         → real-time события
- notification_service       → уведомления
- notifications             → дублирует notification_service

❌ НУЖНО СОЗДАТЬ:
- message-queue             → очередь сообщений (RabbitMQ wrapper)
- event-store              → хранение истории событий
```

### 3️⃣ **PROCESSING** (Исполняет процессы)
```
✅ ЕСТЬ:
- workflow                   → workflow engine (+ вложенные BPMN)
- ai_workflow_optimizer      → оптимизатор процессов
- deployer                   → развертывание (можно отнести сюда)

❌ НУЖНО СОЗДАТЬ:
- task-scheduler            → планировщик задач
- batch-processor          → пакетная обработка
- rules-engine            → движок правил
- state-machine          → конечные автоматы
```

### 4️⃣ **STORAGE** (Хранит данные)
```
✅ ЕСТЬ:
- unified_database_gateway   → единый доступ к данным ✅
- database                   → адаптер БД
- databases                  → множественные БД
- supabase                   → real-time БД
- digital-twin              → виртуальная копия данных

❌ НУЖНО СОЗДАТЬ:
- cache-layer              → кэширование (Redis wrapper)
- file-storage            → файловое хранилище (S3/MinIO wrapper)
- search-index           → поисковый индекс (Elasticsearch wrapper)
```

### 5️⃣ **INTELLIGENCE** (Предсказывает и учится)
```
✅ ЕСТЬ:
- ai                         → базовый AI
- ai-consultant              → AI консультант
- ai-services               → набор AI сервисов (7 вложенных)
- ai_control_center         → центр управления AI
- ai_workflow_optimizer     → AI оптимизация
- process_mining_service    → анализ процессов
- docker-ai                 → AI в Docker
- docker-ai-poc            → AI прототип

❌ НУЖНО СОЗДАТЬ:
- prediction-engine        → движок предсказаний
- pattern-detector        → детектор паттернов
- learning-loop          → цикл обучения
- knowledge-graph       → граф знаний
```

### 🔧 **SUPPORT** (Вспомогательные)
```
✅ ЕСТЬ:
- gateway/gateways           → API gateway
- unified_api_gateway        → унифицированный gateway
- auth                       → аутентификация
- monitoring                 → мониторинг
- monitoring_service         → сервис мониторинга
- nginx                      → балансировщик
- tools                      → инструменты
- github_app                → GitHub интеграция
- vscode-extension          → VSCode расширение
- mcp-server                → MCP сервер

ЭТО НЕ ОСНОВНЫЕ ФУНКЦИИ, НО НУЖНЫ ДЛЯ РАБОТЫ
```

## 📊 СТАТИСТИКА:

| Функция | Есть | Нужно создать | Готовность |
|---------|------|---------------|------------|
| ORCHESTRATION | 5 | 3 | 62% |
| EVENTS | 4 | 2 | 66% |
| PROCESSING | 3 | 4 | 43% |
| STORAGE | 5 | 3 | 62% |
| INTELLIGENCE | 8 | 4 | 66% |
| **ИТОГО** | **25** | **16** | **60%** |

## 🎯 ПРИОРИТЕТЫ:

### КРИТИЧНО (без этого не заработает):
1. **service-registry** - без него orchestrator не знает о модулях
2. **message-queue** - без нее события теряются
3. **task-scheduler** - без него нет автоматизации
4. **cache-layer** - без него медленно
5. **prediction-engine** - без него нет интеллекта

### ВАЖНО (улучшает работу):
- rules-engine
- event-store
- search-index
- pattern-detector
- knowledge-graph

### МОЖНО ОТЛОЖИТЬ:
- batch-processor
- state-machine
- file-storage
- learning-loop
- dependency-resolver

## 📁 ПРАВИЛЬНАЯ СТРУКТУРА:

```
SYSTEM_COMPONENTS/
├── 1_ORCHESTRATION/
│   ├── platform-orchestrator/
│   ├── scenario_orchestrator/
│   ├── unified_control_center/
│   ├── cognitive-orchestrator/
│   └── ai_orchestrator/
│
├── 2_EVENTS/
│   ├── event-bus/
│   ├── realtime_websocket/
│   ├── notification_service/
│   └── notifications/
│
├── 3_PROCESSING/
│   ├── workflow/
│   ├── ai_workflow_optimizer/
│   └── deployer/
│
├── 4_STORAGE/
│   ├── unified_database_gateway/  ← ВОТ ТУТ!
│   ├── database/
│   ├── databases/
│   ├── supabase/
│   └── digital-twin/
│
├── 5_INTELLIGENCE/
│   ├── ai/
│   ├── ai-consultant/
│   ├── ai-services/
│   ├── ai_control_center/
│   ├── process_mining_service/
│   ├── docker-ai/
│   └── docker-ai-poc/
│
└── SUPPORT/
    ├── gateway/
    ├── unified_api_gateway/
    ├── auth/
    ├── monitoring/
    ├── nginx/
    └── tools/
```

Вот теперь понятно куда что относится!