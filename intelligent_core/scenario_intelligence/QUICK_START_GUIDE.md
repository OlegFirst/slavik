# Scenario Intelligence - Quick Start Guide

## 🚀 Что это в двух словах?

**Scenario Intelligence** = Система, которая **описывает**, **тестирует**, **оркестрирует** и **улучшает** вашу платформу через исполняемые сценарии (YAML).

---

## 📁 Структура директории

```
/Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence/
│
├── 📚 engines/                         # Движки исполнения
│   ├── scenario_engine.py             # Главный оркестратор
│   ├── call_engine.py                 # BPMN Call Activity
│   ├── event_engine.py                # Event Storming
│   ├── chaos_engine.py                # Chaos Engineering
│   └── compliance_engine.py           # ISO 22301
│
├── 💾 storage/                         # Хранилище
│   ├── registry.py                    # Мульти-индекс поиск (in-memory)
│   └── rag_storage.py                 # RAG с embeddings [TODO]
│
├── 🎓 learning/                        # Обучение
│   ├── scenario_learner.py            # Учится на выполнении
│   └── [pattern_detector, predictor, auto_generator - TODO]
│
├── 📋 scenarios/                       # 14+ YAML сценариев
│   ├── level1-modules/                # Модули (BIA, Risk, Vault, etc)
│   ├── level2-subsystems/             # Подсистемы (AI Office, Security)
│   ├── level3-intersystem/            # Интеграции (AI↔Platform)
│   └── level4-user/                   # E2E workflows
│
├── 🔌 integration/                     # Интеграции
│   ├── database_integration.py        # PostgreSQL ✅
│   ├── eventbus_integration.py        # EventBus ✅
│   └── rag_integration.py             # Qdrant [TODO]
│
├── 🌐 api/                             # REST API
│   └── api.py                         # FastAPI на :8090
│
├── 📖 Документация
│   ├── README.md                      # Главный README
│   ├── SCENARIO_INTELLIGENCE_ROLE.md  # Роль в платформе ⭐
│   ├── BASE_SCENARIOS_CATALOG.md      # Каталог 14 сценариев
│   └── QUICK_START_GUIDE.md           # Эта шпаргалка
│
└── 🧪 test_scenario_system.py          # Комплексный тест
```

---

## ⚡ Быстрый старт (3 команды)

### 1️⃣ Протестировать систему

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence
python3 test_scenario_system.py
```

**Ожидаемый результат:**
```
✅ ALL TESTS PASSED!
✅ Scenario Engine - OK
✅ Call Engine - OK
✅ Event Engine - OK
✅ Chaos Engine - OK
✅ Compliance Engine - OK
✅ Registry - OK
✅ Learner - OK
```

---

### 2️⃣ Запустить API

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence
python3 -m api.api
```

**API доступен на:** http://localhost:8090

---

### 3️⃣ Выполнить сценарий через API

```bash
# Выполнить BIA creation сценарий
curl -X POST http://localhost:8090/scenarios/execute \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_file": "scenarios/level1-modules/bia-service/functional/create-bia.v1.0.0.yaml",
    "context": {
      "user_id": "user-123",
      "organization_id": "org-456",
      "process_name": "Customer Orders",
      "rto": 4,
      "rpo": 1,
      "financial_impact": 100000
    }
  }'
```

---

## 🎯 Основные концепции

### 1. Четыре уровня сценариев

```
Level 1 - Module       → Тестирование отдельного модуля (BIA Service)
Level 2 - Subsystem    → Тестирование подсистемы (AI Office)
Level 3 - Inter-system → Тестирование интеграции (AI ↔ Platform)
Level 4 - User         → E2E пользовательский workflow
```

**Пример:**
- **Level 1:** `bia-service-create-bia` - создает BIA
- **Level 4:** `complete-risk-assessment-workflow` - вызывает 5+ Level 1 сценариев

---

### 2. Гибридная модель (6 frameworks)

Scenario Intelligence объединяет:

1. **BPMN 2.0** → Call Activity (синхронные вызовы)
2. **Event Storming** → Events (асинхронные события)
3. **ISO 22301** → Compliance (автопроверка)
4. **Google SRE** → Runbooks (шаги выполнения)
5. **Netflix Chaos** → Chaos experiments
6. **AWS Well-Architected** → 5 pillars (security, reliability, etc)

---

### 3. Формат сценария (YAML)

```yaml
scenario:
  meta:
    id: "unique-id"
    version: "1.0.0"
    level: 1              # 1-4
    type: "functional"    # functional, chaos, security, workflow

  behavior:               # Gherkin (Given/When/Then)
    given: ["precondition"]
    when: ["action"]
    then: ["result"]

  execution:              # SRE Runbook
    steps:
      - id: "step1"
        action: "service.method"
        expect: {...}

  integration:            # BPMN + Event Storming
    calls: [...]          # Синхронные вызовы
    events: [...]         # Асинхронные события

  compliance:             # ISO 22301
    iso_22301:
      clauses: ["8.2.2"]
      evidence_generated: [...]
```

---

## 📊 14 базовых сценариев

### Level 1 - Modules (6)
1. ✅ `bia-service-create-bia` - Создание BIA
2. ✅ `risk-service-create-risk-assessment` - Оценка риска
3. ✅ `document-service-store-document` - Хранение документа
4. ✅ `audit-service-create-audit-log` - Audit logging
5. ✅ `compliance-engine-check-compliance` - Проверка compliance
6. ✅ `plans-service-create-bcm-plan` - Создание BCM плана

### Level 2 - Subsystems (3)
7. ✅ `platform-services-bcm-subsystem-health` - Здоровье BCM подсистемы
8. ✅ `ai-office-coordination` - Координация AI агентов
9. ✅ `security-subsystem-test` - Тест security подсистемы

### Level 3 - Inter-system (2)
10. ✅ `ai-assisted-bia-workflow` - AI-assisted BIA
11. ✅ `platform-infrastructure-monitoring` - Monitoring интеграция

### Level 4 - User (3)
12. ✅ `bia-complete-workflow` - Полный BIA workflow
13. ✅ `complete-risk-assessment-workflow` - Полный Risk Assessment
14. ✅ `incident-response-workflow` - Реагирование на инциденты

**См. полный каталог:** [BASE_SCENARIOS_CATALOG.md](BASE_SCENARIOS_CATALOG.md)

---

## 🌐 API Endpoints

```bash
# Health check
GET http://localhost:8090/health

# Выполнить сценарий
POST http://localhost:8090/scenarios/execute
Body: {"scenario_file": "...", "context": {...}}

# Зарегистрировать сценарий
POST http://localhost:8090/scenarios/register
Body: {"scenario": {...}}

# Получить сценарий
GET http://localhost:8090/scenarios/{scenario_id}

# Поиск сценариев
GET http://localhost:8090/scenarios?level=1&type=functional

# Статистика всех сценариев
GET http://localhost:8090/scenarios/statistics

# Статистика конкретного сценария
GET http://localhost:8090/scenarios/{scenario_id}/statistics

# История выполнений
GET http://localhost:8090/scenarios/{scenario_id}/executions
```

---

## 🔧 Использование в коде

### Python

```python
from scenario_intelligence import ScenarioEngine, global_registry

# 1. Загрузить сценарий
scenario = await global_registry.load_from_file(
    "scenarios/level1-modules/bia-service/functional/create-bia.v1.0.0.yaml"
)

# 2. Выполнить
engine = ScenarioEngine()
result = await engine.execute_scenario(
    scenario,
    context={
        "user_id": "user-123",
        "organization_id": "org-456",
        "process_name": "Customer Orders"
    }
)

# 3. Проверить результат
print(f"Status: {result['status']}")
print(f"Duration: {result['duration_ms']}ms")

# 4. Получить статистику
from scenario_intelligence import global_learner
stats = await global_learner.get_statistics("bia-service-create-bia")
print(f"Success rate: {stats['success_rate']}")
```

---

## 🎓 Три роли Scenario Intelligence

### 1. Тестировщик
- Сценарии = живые тесты
- Покрывают все уровни (unit → integration → E2E)
- Встроенная проверка compliance

### 2. Оркестратор
- Композиция сценариев (Call Activity)
- Асинхронные события (Event Storming)
- Централизованная логика workflows

### 3. Обучающаяся система
- Собирает статистику каждого выполнения
- Находит паттерны использования
- Предсказывает следующие сценарии [TODO]
- Генерирует новые сценарии [TODO]

---

## 📈 Метрики

После выполнения сценария вы получаете:

```json
{
  "scenario_id": "bia-service-create-bia",
  "executions": 156,
  "success_rate": 0.97,
  "avg_duration_ms": 523,
  "p95_duration_ms": 810,
  "last_failure": "2025-10-10T15:23:00Z",
  "common_patterns": [
    "часто выполняется после user login",
    "обычно следует за organization creation"
  ]
}
```

---

## 🔗 Интеграции

### ✅ Готовые интеграции

**PostgreSQL:**
```python
from integration.database_integration import ScenarioDatabaseManager

db = ScenarioDatabaseManager()
db.save_scenario(scenario)
db.save_execution(result)
```

**EventBus:**
```python
from integration.eventbus_integration import ScenarioEventPublisher

publisher = ScenarioEventPublisher()
await publisher.publish_execution_completed(scenario_id, result)
```

### 🔄 В разработке

- **Qdrant RAG** - семантический поиск сценариев
- **API Authentication** - JWT токены
- **Real-time monitoring** - WebSocket для live updates

---

## 🛠️ Разработка новых сценариев

### Шаг 1: Создать YAML

```yaml
# scenarios/level1-modules/my-service/functional/my-scenario.v1.0.0.yaml
scenario:
  meta:
    id: "my-service-my-scenario"
    version: "1.0.0"
    level: 1
    type: "functional"

  description:
    title: "My scenario title"
    summary: "What it does"
    business_value: "Why it matters"

  behavior:
    given: ["Service is running"]
    when: ["User does X"]
    then: ["System responds Y"]

  execution:
    steps:
      - id: "step1"
        action: "http.post"
        params:
          url: "http://my-service:8001/api/endpoint"
          body: {...}
        expect:
          status: 201
```

### Шаг 2: Зарегистрировать

```bash
curl -X POST http://localhost:8090/scenarios/register \
  -H "Content-Type: application/json" \
  -d @scenarios/level1-modules/my-service/functional/my-scenario.v1.0.0.yaml
```

### Шаг 3: Выполнить

```bash
curl -X POST http://localhost:8090/scenarios/execute \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "my-service-my-scenario",
    "context": {...}
  }'
```

---

## 🐛 Troubleshooting

### Сценарий не выполняется?

1. **Проверить формат YAML:**
```bash
python3 -c "import yaml; yaml.safe_load(open('scenario.yaml'))"
```

2. **Проверить логи:**
```bash
# Логи Scenario Intelligence
tail -f /var/log/scenario-intelligence.log
```

3. **Проверить зависимости:**
```bash
# Убедиться что сервисы доступны
curl http://bia-service:8001/health
curl http://ai-orchestrator:8000/health
```

### API не отвечает?

```bash
# Проверить что API запущен
lsof -i :8090

# Перезапустить API
cd /Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence
python3 -m api.api
```

---

## 📚 Дополнительные ресурсы

1. **[README.md](README.md)** - Подробная документация
2. **[SCENARIO_INTELLIGENCE_ROLE.md](SCENARIO_INTELLIGENCE_ROLE.md)** - Роль в платформе ⭐⭐⭐
3. **[BASE_SCENARIOS_CATALOG.md](BASE_SCENARIOS_CATALOG.md)** - Каталог всех 14 сценариев
4. **[HYBRID_ARCHITECTURE_VISUALIZATION.md](HYBRID_ARCHITECTURE_VISUALIZATION.md)** - Архитектура

---

## ✅ Чек-лист "Я понял Scenario Intelligence"

- [ ] Понимаю 4 уровня (Module → Subsystem → Inter-system → User)
- [ ] Понимаю разницу между Call (синхр) и Event (асинхр)
- [ ] Могу запустить `test_scenario_system.py` ✅
- [ ] Могу запустить API на :8090 ✅
- [ ] Могу выполнить сценарий через API ✅
- [ ] Понимаю формат YAML сценария
- [ ] Знаю где найти 14 базовых сценариев
- [ ] Понимаю роль Scenario Intelligence в платформе

---

## 🎯 Next Steps

### Сейчас доступно:
- ✅ 14 базовых сценариев
- ✅ API на :8090
- ✅ PostgreSQL integration
- ✅ EventBus integration

### В разработке:
- 🔄 API authentication
- 🔄 Qdrant RAG integration
- 🔄 Загрузка сценариев в БД
- 🔄 Загрузка сценариев в Qdrant

### В планах:
- 📋 Visual dashboard
- 📋 Scenario editor UI
- 📋 Auto-generation AI
- 📋 A/B testing

---

**Вопросы? Смотри [SCENARIO_INTELLIGENCE_ROLE.md](SCENARIO_INTELLIGENCE_ROLE.md) для глубокого понимания! 🚀**
