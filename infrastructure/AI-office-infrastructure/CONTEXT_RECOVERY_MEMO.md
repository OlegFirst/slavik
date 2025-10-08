# 🚀 ПАМЯТКА БЫСТРОГО ВОССТАНОВЛЕНИЯ КОНТЕКСТА

**Дата создания:** 2025-10-08
**Статус инфраструктуры:** 85.7% функциональная
**Компонентов всего:** 35+ | **Сервисов:** 11 (1 работает)

---

## ⚡ КРИТИЧЕСКАЯ ИНФОРМАЦИЯ

### Что Работает Прямо Сейчас
- ✅ **Workflow Intelligence** (порт 8020) - THE BRAIN
- ✅ **Infrastructure Orchestrator** (85.7% тестов проходит)
- ✅ **AI Event Manager** с continuous monitoring (5 мин)
- ✅ **EventBus** (memory backend)
- ✅ **DevOps Agent** (код готов, не запущен)

### Что НЕ Работает
- ❌ **10 сервисов остановлены** (см. список портов ниже)
- ❌ **Конфликты портов:** 8001 (Auth/GitHub), 8050 (DB/WebSocket)
- ❌ **43% компонентов не интегрированы**

---

## 📍 КЛЮЧЕВЫЕ ДИРЕКТОРИИ

```
/Users/MD/AI-Platform-ISO/
│
├── infrastructure/
│   ├── AI-office-infrastructure/          ← ГЛАВНАЯ ДИРЕКТОРИЯ AI ОФИСА
│   │   ├── ai-event-manager/              ← EVENT MANAGER (НОВЫЙ)
│   │   │   ├── integrations/              ← 7 интеграционных файлов
│   │   │   ├── config.yaml                ← Конфигурация всех интеграций
│   │   │   ├── docker-compose.yml         ← Docker setup
│   │   │   └── start.sh                   ← Запуск системы
│   │   ├── devops-agent/                  ← DEVOPS AI COLLEAGUE
│   │   │   ├── agent.py                   ← Главный файл (порт 8060)
│   │   │   ├── api/main.py                ← REST API
│   │   │   └── reports-generated/         ← Отчеты анализаторов
│   │   ├── orchestrator/                  ← INFRASTRUCTURE ORCHESTRATOR
│   │   │   ├── unified_orchestrator.py    ← Главный оркестратор (FIXED)
│   │   │   ├── test_orchestrator.py       ← Тесты (12/14 pass)
│   │   │   └── requirements.txt           ← Зависимости
│   │   └── mio-manager/                   ← MASTER INTELLIGENCE ORCHESTRATOR
│   │       └── integrations/
│   │           └── devops_agent_client.py ← Клиент для DevOps Agent
│   │
│   ├── eventbus/                          ← EVENT-DRIVEN ARCHITECTURE
│   │   ├── core/events.py                 ← Event, EventPriority
│   │   ├── backends/                      ← memory, redis backends
│   │   └── factory.py                     ← create_eventbus()
│   │
│   ├── tools/analyzers/                   ← АНАЛИЗАТОРЫ (7 файлов)
│   │   ├── discover_services.py           ← ServiceDiscovery
│   │   ├── dependency_validator.py        ← Валидация зависимостей
│   │   └── ...                            ← Остальные анализаторы
│   │
│   └── observability/                     ← МОНИТОРИНГ
│       ├── config/prometheus/
│       └── docker-compose.monitoring.yml
│
└── intelligent-core/                      ← INTELLIGENT CORE
    ├── ai-foundation/                     ← RAG + LLM TOOLKIT
    ├── workflow_intelligence/             ← THE BRAIN (порт 8020)
    ├── orchestration/
    │   ├── ai-orchestration/              ← AI Orchestrator
    │   └── coordination-center/           ← Coordination Center
    └── expertise-center/
        └── domains/bcm/tactical_assistants/ ← 7 AI КОЛЛЕГ
```

---

## 🔌 КАРТА ПОРТОВ

| Порт | Сервис | Статус | Путь |
|------|--------|--------|------|
| **8020** | Workflow Intelligence | ✅ РАБОТАЕТ | intelligent-core/workflow_intelligence |
| **8030** | AI Orchestrator | ❌ Остановлен | orchestration/ai-orchestration |
| **8035** | Coordination Center | ❌ Остановлен | orchestration/coordination-center |
| **8040** | Expertise Center | ❌ Остановлен | expertise-center |
| **8045** | Collective | ❌ Остановлен | collective |
| **8046** | Community Intelligence | ❌ Остановлен | community_intelligence |
| **8047** | Predictive Service | ❌ Остановлен | predictive |
| **8001** | Auth / GitHub | ⚠️ КОНФЛИКТ | infrastructure/auth, github-integration |
| **8050** | DB Intelligence / WebSocket | ⚠️ КОНФЛИКТ | db-intelligence-service, realtime-websocket |
| **8060** | DevOps Agent | 🆕 ГОТОВ | AI-office-infrastructure/devops-agent |
| **8039** | Event Intelligence | ❓ Проверить | event-intelligence |

---

## 🚀 БЫСТРЫЙ СТАРТ

### 1. Запуск AI Event Manager (НОВЫЙ)
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/ai-event-manager
chmod +x start.sh
./start.sh

# Или через Docker
docker-compose up -d
```

**Что запустится:**
- IntegrationManager (все интеграции)
- Continuous Monitor (сканирование каждые 5 мин)
- EventBus integration
- DevOps Agent integration
- GitHub automation

### 2. Запуск Infrastructure Orchestrator
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/orchestrator
python3 unified_orchestrator.py

# Или тесты
pytest test_orchestrator.py -v
```

### 3. Запуск DevOps Agent
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/devops-agent
python3 api/main.py

# Проверка
curl http://localhost:8060/health
```

### 4. Запуск Всех Сервисов (intelligent-core)
```bash
cd /Users/MD/AI-Platform-ISO
./start_all_services.sh
```

### 5. Проверка Статуса
```bash
# Все сервисы
python3 infrastructure/tools/analyzers/discover_services.py

# Workflow Intelligence
curl http://localhost:8020/health

# DevOps Agent
curl http://localhost:8060/status
```

---

## 🔧 ТИПИЧНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ

### Проблема: ImportError: No module named 'eventbus'
**Решение:**
```python
import sys
from pathlib import Path
project_root = Path(__file__).parents[N]  # N зависит от глубины
sys.path.insert(0, str(project_root / "infrastructure"))
from eventbus import create_eventbus
```

### Проблема: ServiceDiscovery not found
**Решение:**
```python
sys.path.insert(0, str(PROJECT_ROOT / 'infrastructure' / 'tools' / 'analyzers'))
from discover_services import ServiceDiscovery
```

### Проблема: Port already in use (8001, 8050)
**Решение:**
```bash
# Найти процесс
lsof -i :8001
lsof -i :8050

# Убить процесс
kill -9 <PID>

# Или изменить порт в конфиге
```

### Проблема: Continuous monitor не работает
**Проверка:**
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/ai-event-manager
python3 -c "from integrations.continuous_monitor import ContinuousMonitor; print('OK')"
```

### Проблема: EventBus connection failed
**Решение:**
```bash
# Проверить Redis (если используется)
redis-cli ping

# Или использовать memory backend
eventbus = create_eventbus('memory')
```

---

## 📊 АРХИТЕКТУРНЫЕ ПАТТЕРНЫ

### Event-Driven Architecture
```python
from infrastructure.eventbus import create_eventbus, Event, EventPriority

bus = create_eventbus('memory')

# Публикация
event = Event.create(
    event_type='infrastructure.service_down',
    data={'service': 'auth-service', 'port': 8001},
    source='devops-agent',
    priority=EventPriority.HIGH
)
await bus.publish(event)

# Подписка
async def handle(event: Event):
    print(f"Event: {event.type}")

await bus.subscribe('infrastructure.*', handle)
```

### AI Event Manager Integration
```python
from integrations import IntegrationManager

manager = IntegrationManager()
await manager.initialize_all()

# Полный цикл анализа
result = await manager.full_analysis_cycle()

# Continuous monitoring
await manager.start_continuous_monitoring(interval=300)
```

### DevOps Agent Usage
```python
from infrastructure.AI_office_infrastructure.devops_agent.agent import DevOpsAgent

agent = DevOpsAgent("/Users/MD/AI-Platform-ISO")
await agent.initialize()
result = await agent.run_full_cycle()
```

---

## 🎯 WORKFLOW СЦЕНАРИИ

### Сценарий 1: Обнаружение Проблемы Сервиса
```
1. Continuous Monitor сканирует (каждые 5 мин)
2. Обнаруживает service_down
3. Публикует событие в EventBus
4. DevOps Agent получает событие
5. Анализирует логи через RAG
6. Предлагает решение через LLM
7. MIO Manager координирует fix
8. GitHub Action создает issue (опционально)
```

### Сценарий 2: Запуск Нового Сервиса
```
1. Infrastructure Orchestrator получает команду
2. Проверяет зависимости (ServiceDiscovery)
3. Проверяет конфликты портов
4. Запускает Docker container
5. Регистрирует в Service Registry
6. Публикует событие service_started
7. AI Event Manager обновляет статус
```

### Сценарий 3: Автоматический Fix
```
1. Event Intelligence обнаруживает аномалию
2. Публикует событие в EventBus (priority=HIGH)
3. DevOps Agent анализирует через RAG
4. LLM генерирует fix
5. MIO Manager координирует применение
6. Workflow Intelligence отслеживает результат
7. Отчет сохраняется в reports-generated/
```

---

## 📈 СТАТУС ИНТЕГРАЦИЙ

### Полностью Интегрированы (57%)
- ✅ EventBus (100%)
- ✅ Workflow Intelligence (100%)
- ✅ AI Event Manager (100%)
- ✅ DevOps Agent (100%)
- ✅ Infrastructure Orchestrator (85.7%)
- ✅ MIO Manager (95%)

### Частично Интегрированы (30%)
- ⚠️ GitHub Integration (API готов, automation pending)
- ⚠️ Event Intelligence (код готов, не запущен)
- ⚠️ Monitoring (Prometheus setup, нет full integration)

### Не Интегрированы (13%)
- ❌ Auth Service (конфликт порта 8001)
- ❌ WebSocket Service (конфликт порта 8050)
- ❌ Deployment Service (не интегрирован)
- ❌ Process Mining (не интегрирован)

---

## 🔍 ДИАГНОСТИЧЕСКИЕ КОМАНДЫ

### Проверка Всех Компонентов
```bash
# Service Discovery
python3 infrastructure/tools/analyzers/discover_services.py

# Dependency Validation
python3 infrastructure/tools/analyzers/dependency_validator.py

# Orchestrator Tests
pytest infrastructure/AI-office-infrastructure/orchestrator/test_orchestrator.py -v
```

### Проверка AI Event Manager
```bash
cd infrastructure/AI-office-infrastructure/ai-event-manager

# Проверка интеграций
python3 -c "
from integrations import IntegrationManager
import asyncio
async def test():
    mgr = IntegrationManager()
    await mgr.initialize_all()
    print('✅ All integrations OK')
asyncio.run(test())
"
```

### Проверка EventBus
```bash
python3 -c "
from infrastructure.eventbus import create_eventbus
bus = create_eventbus('memory')
print('✅ EventBus OK')
"
```

### Проверка Портов
```bash
# Проверить все порты
lsof -i :8020 :8030 :8035 :8040 :8045 :8046 :8047 :8060 :8001 :8050 :8039

# Или через netstat
netstat -an | grep -E ':(8020|8030|8035|8040|8045|8046|8047|8060)'
```

---

## 📝 ПОСЛЕДНИЕ ИЗМЕНЕНИЯ (2025-10-08)

### Выполнено
1. ✅ DevOps Agent перенесен в AI Office Infrastructure
2. ✅ Исправлены все импорты (EventBus, project_root)
3. ✅ Reports перенесены в devops-agent/reports-generated/
4. ✅ Infrastructure Orchestrator починен (85.7% тестов)
5. ✅ AI Event Manager создан с полной интеграцией
6. ✅ Continuous Monitor настроен (5-минутный цикл)
7. ✅ Полный каталог компонентов создан (35+ компонентов)

### В Процессе
- ⏳ GitHub Actions automation (конфиг готов, не протестирован)
- ⏳ Запуск остановленных сервисов (10 сервисов)
- ⏳ Разрешение конфликтов портов (8001, 8050)

### Следующие Шаги
1. Запустить все остановленные сервисы
2. Разрешить конфликты портов
3. Протестировать GitHub automation
4. Интегрировать оставшиеся 13% компонентов
5. Setup Redis backend для EventBus (production)

---

## 🆘 КРИТИЧЕСКИЕ ФАЙЛЫ (НЕ ТРОГАТЬ БЕЗ BACKUP)

- `/infrastructure/eventbus/` - Core event system
- `/intelligent-core/workflow_intelligence/` - THE BRAIN
- `/infrastructure/AI-office-infrastructure/ai-event-manager/integrations/` - Integration layer
- `/infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py` - Main orchestrator
- `/infrastructure/database/` - Database schemas

---

## 📚 ДОКУМЕНТАЦИЯ

- **Полный каталог:** `/infrastructure/FULL_COMPONENT_CATALOG.md`
- **EventBus:** `/infrastructure/eventbus/README.md`
- **AI Event Manager:** `/infrastructure/AI-office-infrastructure/ai-event-manager/README.md`
- **DevOps Agent:** `/infrastructure/AI-office-infrastructure/devops-agent/README.md`
- **Orchestrator Tests:** `/infrastructure/AI-office-infrastructure/orchestrator/test_orchestrator.py`

---

## ⚙️ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ

```bash
# Temporal (если используется)
export TEMPORAL_NAMESPACE='quickstart-maxdemch-73cb5509.r3gxp'
export TEMPORAL_ADDRESS='europe-west3.gcp.api.temporal.io:7233'

# Qdrant (если используется)
export QDRANT_URL='https://fa9f6acd-aef9-4ebe-a3f5-f89c62bce378.eu-west-1-0.aws.cloud.qdrant.io'
export QDRANT_API_KEY='<ключ в config>'

# Supabase (если используется)
export SUPABASE_URL='<url>'
export SUPABASE_KEY='<key>'

# Python Path
export PYTHONPATH=/Users/MD/AI-Platform-ISO:$PYTHONPATH
```

---

## 🎯 БЫСТРАЯ ДИАГНОСТИКА (30 сек)

```bash
# 1. Проверить Workflow Intelligence
curl -s http://localhost:8020/health | python3 -m json.tool

# 2. Проверить все порты
lsof -i :8020,:8030,:8035,:8040,:8045,:8046,:8047,:8060 | wc -l

# 3. Проверить EventBus
python3 -c "from infrastructure.eventbus import create_eventbus; print('✅')"

# 4. Проверить DevOps Agent
python3 infrastructure/AI-office-infrastructure/devops-agent/agent.py --version 2>&1 | head -1

# 5. Проверить Orchestrator
pytest infrastructure/AI-office-infrastructure/orchestrator/test_orchestrator.py -q
```

**Ожидаемый результат:**
- Workflow Intelligence: `{"status": "healthy"}`
- Порты: 1-2 активных процесса
- EventBus: ✅
- DevOps Agent: версия или импорт OK
- Orchestrator: 12/14 passed

---

## 💡 КОНТАКТЫ И РЕСУРСЫ

- **Project Root:** `/Users/MD/AI-Platform-ISO`
- **Git Branch:** `main`
- **Python:** 3.x
- **OS:** macOS (Darwin 23.6.0)

---

**Последнее обновление:** 2025-10-08
**Статус:** Infrastructure Orchestrator 85.7% functional, AI Event Manager ready, 1/11 services running
**Приоритет:** Запуск остановленных сервисов, разрешение конфликтов портов
